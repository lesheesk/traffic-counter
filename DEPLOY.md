# Инструкция по развертыванию на VPS сервере

## Подготовка проекта для GitHub

### 1. Создание репозитория на GitHub

1. Перейдите на [GitHub](https://github.com) и создайте новый репозиторий
2. Назовите его, например, `traffic-counter`
3. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть)

### 2. Настройка локального репозитория

**Для Windows 10:**

Откройте **Git Bash** или **PowerShell** в папке проекта:

```bash
# Инициализация Git (если еще не сделано)
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Traffic counter with YOLOv8"

# Добавление удаленного репозитория (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/traffic-counter.git

# Отправка на GitHub
git branch -M main
git push -u origin main
```

**Примечание:** При первом `git push` GitHub попросит ввести логин и пароль. Используйте **Personal Access Token** вместо пароля (см. инструкцию ниже).

### 3. Важно: Безопасность

**НЕ коммитьте пароли и чувствительные данные!**

Используйте файл `.env` для хранения секретов (он уже в `.gitignore`):

**Для Windows 10:**

**Способ 1: Через PowerShell**
```powershell
cd D:\traffic-counter
@"
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
SHOW_VIDEO=false
SAVE_VIDEO=false
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
```

**Способ 2: Через Git Bash**
```bash
cd /d/traffic-counter
cat > .env << 'EOF'
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
SHOW_VIDEO=false
SAVE_VIDEO=false
LOG_LEVEL=INFO
EOF
```

**Способ 3: Через Блокнот**
1. Откройте Блокнот
2. Вставьте содержимое выше
3. Сохраните как `.env` (с точкой в начале!) в папку проекта

## Развертывание на VPS сервере

### Вариант 1: Через Docker (Рекомендуется)

#### Шаг 1: Подключение к VPS

```bash
ssh user@your-vps-ip
```

#### Шаг 2: Установка необходимого ПО

```bash
# Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt-get install -y docker-compose-plugin

# Добавление пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER
newgrp docker
```

#### Шаг 3: Клонирование репозитория

```bash
# Переход в домашнюю директорию
cd ~

# Клонирование проекта
git clone https://github.com/YOUR_USERNAME/traffic-counter.git
cd traffic-counter
```

#### Шаг 4: Настройка конфигурации

```bash
# Создание файла .env с вашими настройками
nano .env
```

Содержимое `.env`:
```env
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
LINE_THICKNESS=5
COUNTING_DIRECTION=down
SHOW_VIDEO=false
SAVE_VIDEO=false
OUTPUT_VIDEO_PATH=/app/output.avi
LOG_LEVEL=INFO
```

Или отредактируйте `docker-compose.yml` напрямую.

#### Шаг 5: Запуск приложения

```bash
# Сборка и запуск в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart
```

#### Шаг 6: Автозапуск при перезагрузке сервера

Docker Compose с `restart: unless-stopped` уже настроен на автозапуск.

### Вариант 2: Прямая установка (без Docker)

#### Шаг 1: Подключение и установка зависимостей

```bash
ssh user@your-vps-ip

# Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# Установка Python и зависимостей
sudo apt-get install -y python3 python3-pip python3-venv git libgl1-mesa-glx libglib2.0-0
```

#### Шаг 2: Клонирование проекта

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/traffic-counter.git
cd traffic-counter
```

#### Шаг 3: Настройка виртуального окружения

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### Шаг 4: Настройка конфигурации

```bash
# Создание .env файла
nano .env
```

Или отредактируйте `config.py`.

#### Шаг 5: Запуск через systemd (для автозапуска)

Создайте сервис:

```bash
sudo nano /etc/systemd/system/traffic-counter.service
```

Содержимое:
```ini
[Unit]
Description=Traffic Counter Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/traffic-counter
Environment="PATH=/home/your-username/traffic-counter/venv/bin"
ExecStart=/home/your-username/traffic-counter/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable traffic-counter

# Запуск сервиса
sudo systemctl start traffic-counter

# Проверка статуса
sudo systemctl status traffic-counter

# Просмотр логов
sudo journalctl -u traffic-counter -f
```

## Обновление проекта на VPS

### Через Docker:

```bash
cd ~/traffic-counter
git pull
docker-compose up -d --build
```

### Прямая установка:

```bash
cd ~/traffic-counter
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart traffic-counter
```

## Мониторинг и логи

### Docker:

```bash
# Просмотр логов в реальном времени
docker-compose logs -f

# Просмотр последних 100 строк
docker-compose logs --tail=100

# Статистика использования ресурсов
docker stats traffic-counter
```

### Systemd:

```bash
# Логи сервиса
sudo journalctl -u traffic-counter -f

# Последние 100 строк
sudo journalctl -u traffic-counter -n 100
```

## Полезные команды

### Docker:

```bash
# Остановка контейнера
docker-compose stop

# Запуск контейнера
docker-compose start

# Перезапуск
docker-compose restart

# Удаление контейнера и образов
docker-compose down --rmi all

# Просмотр запущенных контейнеров
docker ps
```

### Проверка подключения к RTSP:

```bash
# Установка ffmpeg (если еще не установлен)
sudo apt-get install -y ffmpeg

# Тест подключения к RTSP потоку
ffplay rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
```

## Устранение проблем

### Проблема: Не удается подключиться к RTSP

1. Проверьте доступность камеры:
```bash
ping 45.152.169.105
```

2. Проверьте порт:
```bash
telnet 45.152.169.105 55555
```

3. Проверьте RTSP URL через VLC или ffplay

### Проблема: Контейнер не запускается

```bash
# Просмотр логов
docker-compose logs

# Проверка конфигурации
docker-compose config
```

### Проблема: Недостаточно памяти

YOLOv8 может потреблять много памяти. Используйте более легкую модель:
```bash
# В .env или docker-compose.yml
YOLO_MODEL=yolov8n.pt  # вместо yolov8m.pt или больше
```

## Рекомендации по безопасности

1. **Не храните пароли в коде** - используйте `.env` файл
2. **Ограничьте доступ к VPS** - настройте firewall
3. **Используйте SSH ключи** вместо паролей
4. **Регулярно обновляйте систему**:
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

5. **Мониторьте использование ресурсов**:
```bash
htop
df -h
free -h
```

