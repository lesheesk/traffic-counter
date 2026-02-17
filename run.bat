@echo off
REM Script for quick project startup on Windows

echo Traffic Counting System
echo =======================

REM Check virtual environment
if not exist "venv" (
    echo Creating virtual environment...
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

REM Install dependencies (only if needed)
if not exist "venv\.dependencies_installed" (
    echo Installing dependencies...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo. > venv\.dependencies_installed
)

REM Create ONNX model from .pt if missing (like run.sh on Ubuntu)
if not defined YOLO_MODEL set "YOLO_MODEL=yolov8m.onnx"
echo %YOLO_MODEL% | findstr /E /L /C:".onnx" >nul
if %errorlevel% equ 0 (
    if not exist "%YOLO_MODEL%" (
        for %%A in ("%YOLO_MODEL%") do set "BASE=%%~nA"
        echo Model %YOLO_MODEL% not found. Creating from %BASE%.pt (one-time download)...
        venv\Scripts\python.exe -m pip install torch --quiet
        venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('%BASE%.pt').export(format='onnx')"
        echo Done: %YOLO_MODEL%
    )
)

REM Check environment variables
if "%RTSP_URL%"=="" (
    echo Warning: RTSP_URL is not set!
    echo    Set environment variable:
    echo    set RTSP_URL=rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101
    echo.
)

REM Run application
echo Starting application...
venv\Scripts\python.exe main.py

pause
