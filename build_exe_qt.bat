@echo off
setlocal
cd /d "%~dp0"

echo Creating virtual environment...
if not exist ".venv" (
    py -3 -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Building CodexPetCompanion.exe...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name CodexPetCompanion ^
  --icon "app_icon.ico" ^
  --add-data "builtin_pets;builtin_pets" ^
  --add-data "README.md;." ^
  codex_pet_companion\main.py

echo Building updater.exe...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --console ^
  --name updater ^
  tools\updater.py

echo Creating release folder...
set "RELEASE_DIR=dist\Codex Pet Companion"
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"
copy /y "dist\CodexPetCompanion.exe" "%RELEASE_DIR%\CodexPetCompanion.exe" >nul
copy /y "dist\updater.exe" "%RELEASE_DIR%\updater.exe" >nul
copy /y "README.md" "%RELEASE_DIR%\README.md" >nul
copy /y "LICENSE.txt" "%RELEASE_DIR%\LICENSE.txt" >nul
copy /y "app_icon.ico" "%RELEASE_DIR%\app_icon.ico" >nul

echo Creating release zip...
if exist "dist\Codex-Pet-Companion-windows-x64.zip" del "dist\Codex-Pet-Companion-windows-x64.zip"
powershell -NoProfile -Command "Compress-Archive -Force -Path 'dist\Codex Pet Companion' -DestinationPath 'dist\Codex-Pet-Companion-windows-x64.zip'"

echo.
echo Done.
echo Folder: dist\Codex Pet Companion
echo Release ZIP: dist\Codex-Pet-Companion-windows-x64.zip
pause
