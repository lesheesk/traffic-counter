#!/bin/bash

# Скрипт для быстрого запуска проекта

echo "🚗 Система подсчета транспорта"
echo "================================"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Проверка переменных окружения
if [ -z "$RTSP_URL" ]; then
    echo "⚠️  Внимание: RTSP_URL не установлен!"
    echo "   Установите переменную окружения:"
    echo "   export RTSP_URL='rtsp://username:password@192.168.1.64:554/Streaming/Channels/101'"
    echo ""
fi

# Запуск приложения
echo "▶️  Запуск приложения..."
python main.py



