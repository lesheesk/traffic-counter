@echo off
REM Скрипт для быстрого запуска проекта на Windows

echo 🚗 Система подсчета транспорта
echo ================================

REM Проверка виртуального окружения
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
)

REM Активация виртуального окружения
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo 📥 Установка зависимостей...
pip install -r requirements.txt

REM Проверка переменных окружения
if "%RTSP_URL%"=="" (
    echo ⚠️  Внимание: RTSP_URL не установлен!
    echo    Установите переменную окружения:
    echo    set RTSP_URL=rtsp://username:password@192.168.1.64:554/Streaming/Channels/101
    echo.
)

REM Запуск приложения
echo ▶️  Запуск приложения...
python main.py

pause

