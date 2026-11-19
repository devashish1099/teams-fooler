@echo off
REM Builds dist\KeepActive.exe (run on Windows with Python installed)
python -m pip install --upgrade pyinstaller
python -m PyInstaller --onefile --windowed --name KeepActive keep_active.py
echo.
echo Done: dist\KeepActive.exe
