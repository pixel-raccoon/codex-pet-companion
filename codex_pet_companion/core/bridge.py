from __future__ import annotations

import glob
import json
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Any

from codex_pet_companion.core.config import DEFAULT_SESSION_GLOB, detect_codex_home_candidates


@dataclass(frozen=True)
class SessionSource:
    codex_home: Path
    session_file: Path
    mtime: float
    size: int


class CodexBridge(threading.Thread):
    def __init__(self, codex_home: Path | None, config: dict[str, Any], event_queue: Queue):
        super().__init__(daemon=True)
        self.codex_home = codex_home
        self.codex_homes = self.detect_codex_homes(codex_home, config, include_slow=False)
        self.active_codex_home: Path | None = None
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
        self._last_debug_selection: tuple[str, str, int, str] | None = None
        self._last_source_snapshot: tuple[str, str, int, str] | None = None
        self._last_candidate_scan_at = 0.0
        self.seen_session_files: set[str] = set()

    @classmethod
    def task_title_from_user_message(cls, value: Any, limit: int = 40) -> str:
        text = cls.long_text(value)
        if not text:
            return ""

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        request_match = re.search(
            r"(?ims)^##\s*(?:my\s+)?request(?:\s+for\s+codex)?\s*:?\s*(.*)$",
            normalized,
        )
        if request_match:
            normalized = request_match.group(1).strip()
        else:
            context_match = re.search(
                r"(?ims)^##\s*context\s+from\s+my\s+ide\s+setup\b",
                normalized,
            )
            if context_match:
                normalized = normalized[: context_match.start()].strip()

        normalized = re.sub(
            r"(?ims)^##\s*context\s+from\s+my\s+ide\s+setup\b.*?(?=^##\s*|\Z)",
            "",
            normalized,
        ).strip()
        normalized = re.sub(r"(?m)^##+\s*", "", normalized).strip()
        if not normalized:
            return ""
        return cls.short_title(normalized, limit)

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        poll = max(0.5, float(self.config.get("pollSeconds", 1) or 1))
        while not self.stop_event.is_set():
            try:
                self.refresh_codex_homes()
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

    @staticmethod
    def detect_codex_homes(codex_home: Path | None, config: dict[str, Any], include_slow: bool = True) -> list[Path]:
        paths: list[Path] = []
        for path in detect_codex_home_candidates(config, include_slow=include_slow):
            key = path if path.is_absolute() else path.absolute()
            if not any(existing == key for existing in paths):
                paths.append(key)
        if codex_home is not None and not any(existing == codex_home for existing in paths):
            paths.insert(0, codex_home)
        return paths

    def refresh_codex_homes(self, force: bool = False) -> None:
        current = time.time()
        interval = max(5.0, float(self.config.get("bridgeCandidateRefreshSeconds", 30) or 30))
        if not force and current - self._last_candidate_scan_at < interval:
            return
        self.codex_homes = self.detect_codex_homes(self.codex_home, self.config)
        self._last_candidate_scan_at = current

    def find_latest_session(self) -> Path | None:
        session_glob = str(self.config.get("sessionGlob", DEFAULT_SESSION_GLOB) or DEFAULT_SESSION_GLOB)
        sources: list[SessionSource] = []
        patterns: list[str] = []
        for codex_home in self.codex_homes:
            pattern = str(codex_home / session_glob)
            patterns.append(pattern)
            try:
                matches = glob.glob(pattern, recursive=True)
            except OSError:
                continue
            for raw in matches:
                path = Path(raw)
                try:
                    if not path.is_file():
                        continue
                    stat = path.stat()
                except OSError:
                    continue
                sources.append(SessionSource(codex_home, path, stat.st_mtime, stat.st_size))

        latest_source = max(sources, key=lambda source: source.mtime) if sources else None
        nearby_count = self.nearby_session_count(sources)

        if latest_source is not None:
            latest = latest_source.session_file
            self.active_codex_home = latest_source.codex_home
            self.codex_home = latest_source.codex_home
            latest_key = str(latest_source.session_file)
            self.active_session_file = latest_key
        else:
            latest = None
            self.active_codex_home = None
            latest_key = ""
            self.active_session_file = ""

        self.emit_source_snapshot(nearby_count)

        selection = (
            str(self.active_codex_home or ""),
            latest_key,
            nearby_count,
            "; ".join(patterns),
        )
        if selection != self._last_debug_selection:
            self._last_debug_selection = selection
            if latest_source is not None:
                self.debug(
                    f"codex candidates={len(self.codex_homes)} active={self.active_codex_home} "
                    f"session={latest_source.session_file} nearby_sessions={nearby_count} "
                    f"pattern={session_glob} mtime={latest_source.mtime:.3f} size={latest_source.size}"
                )
            else:
                self.debug(f"codex candidates={len(self.codex_homes)} active=not found session=not found pattern={session_glob}")
        return latest

    def nearby_session_count(self, sources: list[SessionSource]) -> int:
        if not sources:
            return 0
        window = max(1.0, float(self.config.get("bridgeNearbySessionSeconds", 180) or 180))
        cutoff = time.time() - window
        return sum(1 for source in sources if source.mtime >= cutoff)

    def source_snapshot(self, nearby_count: int) -> dict[str, Any]:
        label, kind = self.source_label(self.active_codex_home)
        found_labels = self.found_source_labels()
        return {
            "action": "__bridge_source__",
            "codex_detection_status": "ready" if self.active_codex_home is not None else "not_found",
            "codex_active_source_label": label,
            "codex_active_session_file": self.active_session_file,
            "codex_active_session_count": int(nearby_count),
            "codex_active_source_kind": kind,
            "codex_active_codex_home": str(self.active_codex_home or ""),
            "codex_found_source_labels": found_labels,
        }

    def emit_source_snapshot(self, nearby_count: int) -> None:
        snapshot = self.source_snapshot(nearby_count)
        key = (
            str(snapshot["codex_active_codex_home"]),
            str(snapshot["codex_active_session_file"]),
            int(snapshot["codex_active_session_count"]),
            str(snapshot["codex_active_source_kind"]),
            ", ".join(str(label) for label in snapshot.get("codex_found_source_labels", [])),
        )
        if key == self._last_source_snapshot:
            return
        self._last_source_snapshot = key
        self.event_queue.put(snapshot)

    @staticmethod
    def source_label(path: Path | None) -> tuple[str, str]:
        if path is None:
            return ("not found", "none")
        text = str(path)
        normalized = text.replace("/", "\\")
        lowered = normalized.lower()
        for prefix in ("\\\\wsl.localhost\\", "\\\\wsl$\\"):
            if lowered.startswith(prefix.lower()):
                rest = normalized[len(prefix):].split("\\")
                distro = rest[0] if rest and rest[0] else "WSL"
                return (f"WSL {distro}", "wsl")
        if sys.platform == "linux" and os.environ.get("WSL_DISTRO_NAME"):
            try:
                if path == Path.home() / ".codex":
                    return (f"WSL {os.environ.get('WSL_DISTRO_NAME') or 'local'}", "wsl")
            except Exception:
                pass
            if text.startswith("/mnt/c/Users/") or text.startswith("/mnt/c/users/"):
                return ("Windows .codex", "windows")
        try:
            if sys.platform == "win32" and path == Path.home() / ".codex":
                return ("Windows .codex", "windows")
        except Exception:
            pass
        return (str(path), "custom")

    def found_source_labels(self) -> list[str]:
        labels: list[str] = []
        for codex_home in self.codex_homes:
            try:
                if not codex_home.is_dir():
                    continue
            except OSError:
                continue
            label, _kind = self.source_label(codex_home)
            if label != "not found" and label not in labels:
                labels.append(label)
        return labels

    def read_new_lines(self, path: Path) -> list[str]:
        key = str(path.resolve())
        stat = path.stat()
        size = stat.st_size

        if key not in self.offsets and bool(self.config.get("bridgeStartFresh", True)):
            fresh_slack = float(self.config.get("bridgeFreshFileSlackSeconds", 3) or 3)
            created_after_bridge = float(getattr(stat, "st_ctime", 0.0) or 0.0) >= self.started_at - fresh_slack
            ignore_existing_tail = bool(self.config.get("bridgeIgnoreExistingSessionTail", True))
            if not created_after_bridge and ignore_existing_tail:
                self.offsets[key] = size
                self.debug(f"existing session ignored until new writes: offset={size} size={size} ctime={stat.st_ctime:.3f} mtime={stat.st_mtime:.3f}")
            elif not created_after_bridge:
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
        label, source_kind = self.source_label(self.active_codex_home)
        self.event_queue.put({
            "action": action,
            "note": note,
            "session_file": session_file,
            "event_type": kind or action,
            "task_title": self.current_task_title,
            "notification_title": title,
            "notification_subtitle": subtitle,
            "codex_active_source_label": label,
            "codex_active_session_file": self.active_session_file,
            "codex_active_source_kind": source_kind,
            "codex_active_codex_home": str(self.active_codex_home or ""),
            "codex_found_source_labels": self.found_source_labels(),
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
            label, source_kind = self.source_label(self.active_codex_home)
            self.event_queue.put({
                "action": "codex_inactive",
                "note": "",
                "session_file": self.active_session_file,
                "codex_active_source_label": label,
                "codex_active_session_file": self.active_session_file,
                "codex_active_source_kind": source_kind,
                "codex_active_codex_home": str(self.active_codex_home or ""),
                "codex_found_source_labels": self.found_source_labels(),
            })

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
            raw_message = payload.get("message") or payload.get("text") or payload.get("text_elements")
            title = self.task_title_from_user_message(raw_message)
            if not title and self.is_ide_context_message(raw_message):
                self.debug("skip IDE context user_message")
                return None
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
            failed = status == "failed" or (isinstance(exit_code, int) and exit_code != 0)
            if failed and bool(self.config.get("bridgeSuppressUntitledCommandErrors", True)) and not self.current_task_title.strip():
                self.debug(f"skip untitled command error: status={status or '?'} exit_code={exit_code}")
                return None
            if failed:
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
        codex_home = self.active_codex_home or self.codex_home
        if codex_home is None:
            return ""
        match = re.search(r"([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})$", path.stem, re.IGNORECASE)
        thread_id = match.group(1) if match else ""
        if not thread_id:
            return ""
        index_path = codex_home / "session_index.jsonl"
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
                        return self.task_title_from_user_message(item.get("thread_name") or "")
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
    def long_text(value: Any) -> str:
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
            value = "\n".join(parts)
        return str(value or "").strip()

    @classmethod
    def is_ide_context_message(cls, value: Any) -> bool:
        text = cls.long_text(value)
        return bool(re.search(r"(?ims)^##\s*context\s+from\s+my\s+ide\s+setup\b", text))

    @classmethod
    def short_text(cls, value: Any) -> str:
        text = " ".join(cls.long_text(value).split())
        if not text:
            return ""
        return text[:64].rstrip() + ("..." if len(text) > 64 else "")

    @classmethod
    def short_title(cls, value: Any, limit: int = 40) -> str:
        text = cls.short_text(value)
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)].rstrip() + "..."
