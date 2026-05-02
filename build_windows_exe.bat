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
  --add-data "spritesheet.webp;." ^
  --add-data "pet.json;." ^
  --add-data "builtin_pets;builtin_pets" ^
  --add-data "README.md;." ^
  codex_pet_companion\main.py

echo.
echo Done.
echo EXE: dist\CodexPetCompanion.exe
pause
