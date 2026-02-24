@echo off
setlocal enabledelayedexpansion
REM Change to script directory (required when started from Explorer/shortcut)
cd /d "%~dp0"

echo Traffic Counting System
echo =======================

where python >nul 2>&1
if errorlevel 1 goto no_python

REM Check virtual environment
if not exist "venv" (
    echo Creating virtual environment
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Check Python in virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Error: Python not found in virtual environment
    pause
    exit /b 1
)

REM Install or upgrade dependencies
if not exist "venv\.dependencies_installed" (
    echo Installing dependencies
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo. > venv\.dependencies_installed
)
REM Ensure ultralytics is present (e.g. after requirements.txt was updated)
venv\Scripts\python.exe -c "import ultralytics" 2>nul
if errorlevel 1 (
    echo Installing missing dependencies
    venv\Scripts\python.exe -m pip install -r requirements.txt
    echo. > venv\.dependencies_installed
)

REM Create ONNX model from .pt if missing (like run.sh on Ubuntu)
if not defined YOLO_MODEL set "YOLO_MODEL=yolov8m.onnx"
echo %YOLO_MODEL% | findstr /E /L /C:".onnx" >nul
if %errorlevel% equ 0 (
    if not exist "%YOLO_MODEL%" (
        for %%A in ("%YOLO_MODEL%") do set "BASE=%%~nA"
        echo Model %YOLO_MODEL% not found. Creating from !BASE!.pt - one-time download
        venv\Scripts\python.exe -m pip install torch --quiet
        venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('!BASE!.pt').export(format='onnx')"
        echo Done: %YOLO_MODEL%
    )
)

REM On Windows: one OpenCV with GUI and VideoCapture - remove both variants then install full
echo Installing OpenCV with video support
venv\Scripts\pip.exe uninstall opencv-python-headless opencv-python -y >nul 2>&1
venv\Scripts\pip.exe install opencv-python
if errorlevel 1 (
    echo Error: opencv-python install failed. Check internet and run run.bat again.
    pause
    exit /b 1
)
echo OpenCV ready.

REM Check environment variables
if "%RTSP_URL%"=="" (
    echo Warning: RTSP_URL is not set!
    echo.
)

REM Run application
echo Starting application
venv\Scripts\python.exe main.py
goto end

:no_python
echo Error: Python not found. Install Python and add to PATH.
pause
exit /b 1

:end
pause
