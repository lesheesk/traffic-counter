@echo off
setlocal
cd /d "%~dp0"

echo Building traffic-counter.exe
echo ===========================

where python >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Creating venv...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo Installing build dependencies...
pip install --upgrade pip -q
pip install pyinstaller opencv-python onnxruntime numpy scipy ultralytics -q
if errorlevel 1 (
    echo Error: pip install failed
    pause
    exit /b 1
)

echo Cleaning old build...
if exist "build" rd /s /q build
if exist "dist" rd /s /q dist

echo Running PyInstaller...
pyinstaller --noconfirm --clean --onedir ^
  --name traffic-counter ^
  --hidden-import=cv2 ^
  --hidden-import=ultralytics ^
  --hidden-import=ultralytics.models ^
  --hidden-import=ultralytics.models.yolo ^
  --hidden-import=ultralytics.nn ^
  --collect-all ultralytics ^
  main.py

if errorlevel 1 (
    echo Error: PyInstaller failed.
    pause
    exit /b 1
)

echo.
echo Done. EXE and files: dist\traffic-counter\
echo Copy the whole folder to the other PC. Put yolov8m.onnx in the same folder.
pause
