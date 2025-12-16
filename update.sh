#!/bin/bash

# Скрипт для обновления проекта на VPS
# Использование: ./update.sh

set -e

PROJECT_DIR="$HOME/traffic-counter"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Проект не найден в $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo "🔄 Обновление проекта..."
git pull

echo "🐳 Пересборка и перезапуск контейнера..."
if docker compose version &> /dev/null; then
    docker compose up -d --build
    docker compose logs -f --tail=50
else
    docker-compose up -d --build
    docker-compose logs -f --tail=50
fi

echo "✅ Обновление завершено!"

