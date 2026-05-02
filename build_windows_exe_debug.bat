@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv" (
    py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --console ^
  --name CodexPetCompanion_Debug ^
  --icon "app_icon.ico" ^
  --add-data "spritesheet.webp;." ^
  --add-data "pet.json;." ^
  --add-data "builtin_pets;builtin_pets" ^
  --add-data "README.md;." ^
  codex_pet_companion\main.py

echo.
echo Done.
echo EXE: dist\CodexPetCompanion_Debug.exe
pause
