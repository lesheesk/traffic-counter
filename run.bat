@echo off
REM Скрипт для быстрого запуска проекта на Windows

echo 🚗 Система подсчета транспорта
echo ================================

REM Проверка виртуального окружения
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка при создании виртуального окружения
        pause
        exit /b 1
    )
)

REM Проверка Python в виртуальном окружении
if not exist "venv\Scripts\python.exe" (
    echo ❌ Ошибка: Python не найден в виртуальном окружении
    pause
    exit /b 1
)

REM Установка зависимостей (только при необходимости)
if not exist "venv\.dependencies_installed" (
    echo 📥 Установка зависимостей...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка при установке зависимостей
        pause
        exit /b 1
    )
    echo. > venv\.dependencies_installed
)

REM Проверка переменных окружения
if "%RTSP_URL%"=="" (
    echo ⚠️  Внимание: RTSP_URL не установлен!
    echo    Установите переменную окружения:
    echo    set RTSP_URL=rtsp://admin:banana38@45.152.169.105:55555/Streaming/Channels/101
    echo.
)

REM Запуск приложения
echo ▶️  Запуск приложения...
venv\Scripts\python.exe main.py

pause



