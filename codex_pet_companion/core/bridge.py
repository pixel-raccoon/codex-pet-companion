from __future__ import annotations

import glob
import json
import re
import threading
import time
from pathlib import Path
from queue import Queue
from typing import Any


class CodexBridge(threading.Thread):
    def __init__(self, codex_home: Path | None, config: dict[str, Any], event_queue: Queue):
        super().__init__(daemon=True)
        self.codex_home = codex_home
        self.config = config
        self.event_queue = event_queue
        self.stop_event = threading.Event()
        self.offsets: dict[str, int] = {}
        self.last_events: dict[str, float] = {}
        self.active_session_file = ""
        self.started_at = time.time()
        self.last_activity_at = 0.0
        self.inactive_sent = False
        self.current_task_title = ""

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        if self.codex_home is None:
            return
        poll = max(0.5, float(self.config.get("pollSeconds", 1) or 1))
        while not self.stop_event.is_set():
            try:
                latest = self.find_latest_session()
                if latest is not None:
                    self.process_file(latest)
                self.maybe_emit_inactive()
            except Exception as exc:
                self.debug(f"bridge loop exception: {type(exc).__name__}: {exc}")
            self.stop_event.wait(poll)

    def debug(self, message: str) -> None:
        if bool(self.config.get("debugBridge", False)):
            self.event_queue.put({"action": "__bridge_debug__", "note": message, "session_file": self.active_session_file})

    def find_latest_session(self) -> Path | None:
        if self.codex_home is None:
            return None
        pattern = str(self.codex_home / str(self.config.get("sessionGlob", "sessions/*/*/*/rollout-*.jsonl")))
        existing = [Path(p) for p in glob.glob(pattern) if Path(p).is_file()]
        latest = max(existing, key=lambda p: p.stat().st_mtime) if existing else None
        if latest is not None and str(latest) != self.active_session_file:
            stat = latest.stat()
            self.debug(f"session selected: {latest} mtime={stat.st_mtime:.3f} size={stat.st_size}")
        return latest

    def read_new_lines(self, path: Path) -> list[str]:
        key = str(path.resolve())
        stat = path.stat()
        size = stat.st_size

        if key not in self.offsets and bool(self.config.get("bridgeStartFresh", True)):
            fresh_slack = float(self.config.get("bridgeFreshFileSlackSeconds", 3) or 3)
            created_after_bridge = float(getattr(stat, "st_ctime", 0.0) or 0.0) >= self.started_at - fresh_slack
            if not created_after_bridge:
                tail_bytes = max(0, int(self.config.get("bridgeInitialTailBytes", 65536) or 0))
                self.offsets[key] = self.tail_start_offset(path, max(0, size - tail_bytes))
                self.debug(f"existing session tail: offset={self.offsets[key]} size={size} ctime={stat.st_ctime:.3f} mtime={stat.st_mtime:.3f}")
            else:
                self.offsets[key] = 0
                self.debug(f"new session from start: offset=0 size={size} ctime={stat.st_ctime:.3f} mtime={stat.st_mtime:.3f}")

        offset = int(self.offsets.get(key, 0) or 0)
        if offset > size:
            offset = 0
            self.debug(f"offset reset after truncate: size={size}")

        before = offset
        with path.open("rb") as f:
            f.seek(offset)
            data = f.read()
            self.offsets[key] = f.tell()

        lines = [line for line in data.decode("utf-8", errors="ignore").splitlines() if line.strip()]
        if data or bool(self.config.get("debugBridgeVerbose", False)):
            self.debug(f"read session: before={before} after={self.offsets[key]} size={size} lines={len(lines)}")
        return lines

    @staticmethod
    def tail_start_offset(path: Path, wanted: int) -> int:
        if wanted <= 0:
            return 0
        try:
            with path.open("rb") as f:
                f.seek(wanted)
                f.readline()
                return f.tell()
        except Exception:
            return wanted

    def emit(self, action: str, note: str, session_file: str, kind: str = "") -> None:
        debounce = self.config.get("debounceSeconds", {"codex_running": 4, "review_ready": 3, "error": 2})
        if not isinstance(debounce, dict):
            debounce = {}
        delay = float(debounce.get(action, 3) or 3)
        current = time.time()
        last = float(self.last_events.get(action, 0) or 0)
        if current - last < delay:
            self.debug(f"debounced event: {action} type={kind or action}")
            return

        title, subtitle = self.notification_text(action, note, kind)
        self.last_events[action] = current
        self.last_activity_at = current
        self.inactive_sent = False
        self.debug(f"queue event: {action} type={kind or action} title={title} subtitle={subtitle}")
        self.event_queue.put({
            "action": action,
            "note": note,
            "session_file": session_file,
            "event_type": kind or action,
            "task_title": self.current_task_title,
            "notification_title": title,
            "notification_subtitle": subtitle,
        })

    def notification_text(self, action: str, note: str, kind: str) -> tuple[str, str]:
        task_title = self.current_task_title.strip()
        if action == "error":
            return (task_title or "Codex reported an error", "Error")
        if action == "review_ready":
            return (task_title or "Codex is ready to review", "Ready to review")
        if kind in {"function_call", "exec_command_end", "patch_apply"}:
            return (task_title or "Codex is running a command", "Running...")
        if task_title:
            return (task_title, "Thinking...")
        if note and not note.lower().startswith("codex "):
            return (self.short_title(note), "Thinking...")
        return ("Codex started a task", "Thinking...")

    def maybe_emit_inactive(self) -> None:
        if self.inactive_sent or not self.last_activity_at:
            return
        ttl = float(self.config.get("bridgeInactiveSeconds", 45) or 45)
        if ttl > 0 and time.time() - self.last_activity_at >= ttl:
            self.inactive_sent = True
            self.debug("queue event: codex_inactive")
            self.event_queue.put({"action": "codex_inactive", "note": "", "session_file": self.active_session_file})

    def process_file(self, path: Path) -> None:
        max_age = float(self.config.get("bridgeMaxEventAgeSeconds", 900) or 900)
        if path.stat().st_mtime < self.started_at - max_age:
            self.debug(f"skip stale session: {path}")
            return
        self.active_session_file = str(path)
        if not self.current_task_title:
            title = self.session_index_title(path)
            if title:
                self.current_task_title = title
                self.debug(f"task title from session_index: {title}")
        for line in self.read_new_lines(path):
            try:
                obj = json.loads(line)
            except Exception:
                self.debug("skip malformed jsonl line")
                continue
            age = self.event_age_seconds(obj)
            max_live_age = float(self.config.get("bridgeLiveEventAgeSeconds", 60) or 60)
            if age is not None and age > max_live_age:
                self.debug(f"skip old event: age={age:.1f}s max={max_live_age}")
                continue
            event = self.event_from_json(obj)
            if event:
                action, note, kind = event
                self.debug(f"recognized payload.type={kind} action={action} note={self.short_title(note)}")
                self.emit(action, note, str(path), kind)

    def event_from_json(self, obj: dict[str, Any]) -> tuple[str, str, str] | None:
        payload = self.extract_payload(obj)
        ptype = str(payload.get("type") or obj.get("type") or "")

        if ptype == "user_message":
            title = self.short_title(payload.get("message") or payload.get("text") or payload.get("text_elements"))
            if title:
                self.current_task_title = title
                self.debug(f"task title: {title}")
            return ("codex_running", title or "Codex is thinking...", "user_message")
        if ptype == "task_started":
            return ("codex_running", "Codex started a task", "task_started")
        if ptype == "agent_message":
            phase = str(payload.get("phase") or "")
            if phase == "final_answer":
                return ("review_ready", "Codex is ready to review", "final_answer")
            if phase == "commentary":
                return ("codex_running", "Codex is thinking...", "reasoning")
        if ptype == "message" and str(payload.get("phase") or "") == "final_answer":
            return ("review_ready", "Codex is ready to review", "final_answer")
        if ptype == "task_complete":
            return ("review_ready", "Codex is ready to review", "final_answer")
        if ptype == "exec_command_end":
            status = str(payload.get("status") or "").lower()
            exit_code = payload.get("exit_code")
            if status == "failed" or (isinstance(exit_code, int) and exit_code != 0):
                return ("error", f"Codex reported an error: status={status or '?'} exit_code={exit_code}", "error")
            return ("codex_running", "Codex finished a command", "exec_command_end")
        if ptype == "patch_apply_end":
            status = str(payload.get("status") or "").lower()
            success = payload.get("success")
            if status == "failed" or success is False:
                return ("error", "Codex reported an error while applying a patch", "error")
            return ("codex_running", "Codex applied changes", "patch_apply")

        for item in self.iter_dicts(obj):
            itype = str(item.get("type") or "")
            if itype in {"function_call", "custom_tool_call"}:
                name = str(item.get("name") or "").strip()
                if name in {"shell_command", "exec_command"}:
                    return ("codex_running", "Codex is running a command", "function_call")
                if name == "apply_patch":
                    return ("codex_running", "Codex is applying changes", "patch_apply")
                return ("codex_running", "Codex is running a tool", "function_call")
            if itype == "reasoning":
                return ("codex_running", "Codex is thinking...", "reasoning")
            if itype == "agent_message" and str(item.get("phase") or "") == "final_answer":
                return ("review_ready", "Codex is ready to review", "final_answer")
            if itype == "message" and str(item.get("phase") or "") == "final_answer":
                return ("review_ready", "Codex is ready to review", "final_answer")
            if itype == "task_complete":
                return ("review_ready", "Codex is ready to review", "final_answer")

        text = json.dumps(obj, ensure_ascii=False).lower()
        if "traceback" in text or '"status": "failed"' in text or '"level": "error"' in text:
            return ("error", "Codex reported an error", "error")
        return None

    @staticmethod
    def extract_payload(obj: dict[str, Any]) -> dict[str, Any]:
        for key in ("payload", "body", "data"):
            value = obj.get(key)
            if isinstance(value, dict):
                return value
        return obj

    @staticmethod
    def event_age_seconds(obj: dict[str, Any]) -> float | None:
        raw = obj.get("timestamp")
        if not isinstance(raw, str) or not raw:
            return None
        try:
            from datetime import datetime

            stamp = raw.replace("Z", "+00:00")
            return max(0.0, time.time() - datetime.fromisoformat(stamp).timestamp())
        except Exception:
            return None

    def session_index_title(self, path: Path) -> str:
        if self.codex_home is None:
            return ""
        match = re.search(r"([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})$", path.stem, re.IGNORECASE)
        thread_id = match.group(1) if match else ""
        if not thread_id:
            return ""
        index_path = self.codex_home / "session_index.jsonl"
        if not index_path.is_file():
            return ""
        try:
            with index_path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    if str(item.get("id") or "") == thread_id:
                        return self.short_title(item.get("thread_name") or "")
        except Exception:
            return ""
        return ""

    @classmethod
    def iter_dicts(cls, obj: Any):
        if isinstance(obj, dict):
            yield obj
            for value in obj.values():
                yield from cls.iter_dicts(value)
        elif isinstance(obj, list):
            for item in obj:
                yield from cls.iter_dicts(item)

    @staticmethod
    def short_text(value: Any) -> str:
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
            value = " ".join(parts)
        text = " ".join(str(value or "").split())
        if not text:
            return ""
        return text[:64].rstrip() + ("..." if len(text) > 64 else "")

    @classmethod
    def short_title(cls, value: Any, limit: int = 40) -> str:
        text = cls.short_text(value)
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)].rstrip() + "..."
