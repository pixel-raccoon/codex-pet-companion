@echo off
setlocal
cd /d "%~dp0"
where pyw >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" pyw -3 -m codex_pet_companion.main
) else (
  start "" pythonw -m codex_pet_companion.main
)
exit /b
