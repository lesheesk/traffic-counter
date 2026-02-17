#!/bin/bash
# Скрипт запуска приложения на Ubuntu/Linux

set -e

echo "Traffic Counting System"
echo "======================"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не найден. Установите: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Создание виртуального окружения при необходимости
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения и установка зависимостей
source venv/bin/activate

if [ ! -f "venv/.dependencies_installed" ]; then
    echo "Установка зависимостей..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.dependencies_installed
fi

# Создание ONNX-модели из .pt, если файла нет (однократно)
MODEL="${YOLO_MODEL:-yolov8s.onnx}"
if [[ "$MODEL" == *.onnx ]] && [ ! -f "$MODEL" ]; then
    BASE="${MODEL%.onnx}"
    echo "Модель $MODEL не найдена. Создание из $BASE.pt (однократная загрузка)..."
    pip install torch --quiet
    python -c "
from ultralytics import YOLO
m = YOLO('$BASE.pt')
m.export(format='onnx')
"
    echo "Готово: $MODEL"
fi

# Предупреждение о RTSP_URL
if [ -z "${RTSP_URL}" ]; then
    echo "Предупреждение: RTSP_URL не задан!"
    echo "  Задайте переменную окружения:"
    echo "  export RTSP_URL=rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101"
    echo ""
fi

echo "Запуск приложения..."
exec python main.py
