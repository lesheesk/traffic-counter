#!/bin/bash

# Скрипт для быстрого развертывания на VPS сервере
# Использование: ./deploy.sh

set -e

echo "🚀 Развертывание Traffic Counter на VPS"
echo "========================================"

# Проверка наличия Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите: sudo apt-get install git"
    exit 1
fi

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Выйдите и войдите снова, чтобы применить изменения группы."
    exit 0
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "📦 Установка Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
fi

# Создание директории проекта
PROJECT_DIR="$HOME/traffic-counter"

if [ -d "$PROJECT_DIR" ]; then
    echo "📂 Обновление существующего проекта..."
    cd "$PROJECT_DIR"
    git pull || echo "⚠️  Не удалось обновить через git. Продолжаем..."
else
    echo "📂 Клонирование проекта..."
    read -p "Введите URL вашего GitHub репозитория (или нажмите Enter для пропуска): " REPO_URL
    if [ -n "$REPO_URL" ]; then
        git clone "$REPO_URL" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    else
        echo "⚠️  Пропуск клонирования. Убедитесь, что проект находится в $PROJECT_DIR"
        exit 1
    fi
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "📝 Создание файла .env..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Создан .env из примера. Отредактируйте его: nano .env"
    else
        cat > .env << 'EOF'
RTSP_URL=rtsp://admin:banana38@45.152.169.105:55555//Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
LINE_THICKNESS=5
COUNTING_DIRECTION=down
SHOW_VIDEO=false
SAVE_VIDEO=false
OUTPUT_VIDEO_PATH=/app/output.avi
LOG_LEVEL=INFO
EOF
        echo "✅ Создан .env файл. Отредактируйте его: nano .env"
    fi
    read -p "Нажмите Enter после редактирования .env файла..."
else
    echo "✅ Файл .env уже существует"
fi

# Создание директории для вывода
mkdir -p output

# Запуск через Docker Compose
echo "🐳 Запуск через Docker Compose..."
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "📊 Полезные команды:"
echo "  Просмотр логов:    docker compose logs -f"
echo "  Остановка:         docker compose down"
echo "  Перезапуск:        docker compose restart"
echo "  Статус:            docker compose ps"
echo ""
echo "📝 Не забудьте отредактировать .env файл с вашими настройками RTSP!"



