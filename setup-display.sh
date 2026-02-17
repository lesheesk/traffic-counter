#!/bin/bash
# Переключение на режим с отображением видеопотока на экране (Ubuntu).
# После выполнения ./run.sh будет показывать окно с видео.

set -e

echo "Настройка отображения видео на экране"
echo "======================================"

# Системные пакеты (запрос sudo). libgl1-mesa-glx устарел в Ubuntu 22.04+, используем libgl1 и libglx-mesa0
echo "Установка системных пакетов (GTK, OpenGL)..."
sudo apt update
sudo apt install -y libgtk2.0-dev pkg-config libgl1 libglx-mesa0

# Виртуальное окружение
if [ ! -d "venv" ]; then
    echo "Сначала запустите ./run.sh один раз (создастся venv), затем снова выполните этот скрипт."
    exit 1
fi

source venv/bin/activate
echo "Замена opencv-python-headless на opencv-python..."
pip uninstall opencv-python-headless -y 2>/dev/null || true
pip install "opencv-python>=4.8.0"

echo ""
echo "Готово. Запускайте: export SHOW_VIDEO=true; ./run.sh"
echo "Окно с видео откроется; выход по клавише q."
