@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install pyinstaller PySide6 pillow
py -3 -m PyInstaller --noconsole --name CodexPetCompanionQt ^
  --add-data "spritesheet.webp;." ^
  --add-data "pet.json;." ^
  --add-data "config.example.json;." ^
  --hidden-import PySide6.QtSvg ^
  -m codex_pet_companion.main
echo Built dist\CodexPetCompanionQt\CodexPetCompanionQt.exe
pause
