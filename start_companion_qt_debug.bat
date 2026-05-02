@echo off
setlocal
cd /d "%~dp0"
echo Starting Codex Pet Companion v11.8.0 DEBUG...
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -m pip show PySide6 >nul 2>nul || py -3 -m pip install PySide6 pillow
  py -3 -m codex_pet_companion.main
) else (
  python -m pip show PySide6 >nul 2>nul || python -m pip install PySide6 pillow
  python -m codex_pet_companion.main
)
echo.
echo Exit code: %ERRORLEVEL%
if exist companion_crash.log (
  echo.
  echo Crash log:
  type companion_crash.log
)
pause
