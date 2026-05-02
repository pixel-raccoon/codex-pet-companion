from __future__ import annotations

import sys
import traceback
from pathlib import Path

def crash_log_path() -> Path:
    return Path(__file__).resolve().parents[1] / "companion_crash.log"

def main() -> None:
    try:
        from codex_pet_companion.ui_qt.app import run_app
        run_app()
    except Exception:
        path = crash_log_path()
        path.write_text(traceback.format_exc(), encoding="utf-8")
        print("Codex Pet Companion crashed.")
        print(f"Crash log: {path}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
