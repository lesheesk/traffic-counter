# 🚀 Быстрый старт: Загрузка на GitHub и развертывание на VPS

> **Для Windows 10** - эта инструкция адаптирована специально для вас!

## Шаг 1: Загрузка проекта на GitHub

### 1.1 Установка Git (если еще не установлен)

**Вариант A: Git для Windows (рекомендуется)**
1. Скачайте с https://git-scm.com/download/win
2. Установите с настройками по умолчанию
3. После установки будет доступен **Git Bash** и **Git CMD**

**Вариант B: GitHub Desktop (проще для начинающих)**
1. Скачайте с https://desktop.github.com/
2. Установите и войдите в свой аккаунт GitHub

### 1.2 Создайте репозиторий на GitHub

1. Перейдите на https://github.com
2. Нажмите "New repository" (или "+" → "New repository")
3. Назовите репозиторий (например, `traffic-counter`)
4. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть в проекте)
5. Нажмите "Create repository"

### 1.3 Загрузите код на GitHub

**Способ 1: Через Git Bash (рекомендуется)**

1. Откройте **Git Bash** в папке проекта:
   - Правый клик на папке `traffic-counter` → "Git Bash Here"
   - Или откройте Git Bash и перейдите в папку: `cd /d/traffic-counter`

2. Выполните команды:

```bash
# Инициализация Git (если еще не сделано)
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Traffic counter with YOLOv8"

# Добавление удаленного репозитория (замените YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/traffic-counter.git

# Отправка на GitHub
git branch -M main
git push -u origin main
```

**Способ 2: Через PowerShell**

1. Откройте **PowerShell** в папке проекта:
   - Shift + Правый клик на папке → "Открыть окно PowerShell здесь"
   - Или откройте PowerShell и перейдите: `cd D:\traffic-counter`

2. Выполните те же команды (Git должен быть установлен):

```powershell
git init
git add .
git commit -m "Initial commit: Traffic counter with YOLOv8"
git remote add origin https://github.com/YOUR_USERNAME/traffic-counter.git
git branch -M main
git push -u origin main
```

**Способ 3: Через GitHub Desktop**

1. Откройте GitHub Desktop
2. File → "Add Local Repository"
3. Выберите папку `traffic-counter`
4. Нажмите "Publish repository"
5. Выберите созданный репозиторий на GitHub

**✅ Готово!** Проект теперь на GitHub.

## Шаг 2: Развертывание на VPS сервере

### 2.1 Подключитесь к VPS

**В Windows 10 есть встроенный SSH клиент:**

1. Откройте **PowerShell** или **CMD**
2. Выполните:

```powershell
ssh user@your-vps-ip
```

**Если SSH не работает:**
- Установите OpenSSH: Settings → Apps → Optional Features → Add a feature → OpenSSH Client
- Или используйте **PuTTY**: https://www.putty.org/

### 2.2 Автоматическое развертывание (рекомендуется)

```bash
# Клонирование проекта
git clone https://github.com/YOUR_USERNAME/traffic-counter.git
cd traffic-counter

# Запуск скрипта развертывания
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- ✅ Установит Docker (если нужно)
- ✅ Создаст файл `.env`
- ✅ Соберет и запустит контейнер

### 2.3 Настройка конфигурации

После запуска `deploy.sh` отредактируйте `.env` файл:

```bash
nano .env
```

Укажите ваш RTSP URL:
```env
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
```

Сохраните (Ctrl+O, Enter, Ctrl+X) и перезапустите:

```bash
docker compose restart
```

### 2.4 Проверка работы

```bash
# Просмотр логов
docker compose logs -f

# Проверка статуса
docker compose ps
```

## Шаг 3: Обновление проекта

Когда вы внесете изменения в код:

### На локальной машине (Windows):

**Через Git Bash или PowerShell:**

```bash
git add .
git commit -m "Описание изменений"
git push
```

**Или через GitHub Desktop:**
1. Внесите изменения в файлы
2. В GitHub Desktop увидите изменения
3. Напишите комментарий к коммиту
4. Нажмите "Commit to main"
5. Нажмите "Push origin"

### На VPS сервере:

```bash
cd ~/traffic-counter
./update.sh
```

Или вручную:
```bash
cd ~/traffic-counter
git pull
docker compose up -d --build
```

## 🔒 Безопасность

**⚠️ ВАЖНО:** Пароли и секретные данные НЕ должны попадать в GitHub!

- ✅ Файл `.env` уже в `.gitignore` - он не будет закоммичен
- ✅ Используйте `.env` для хранения паролей
- ✅ Не коммитьте файлы с паролями в `config.py` или `docker-compose.yml`

Если случайно закоммитили пароль:
1. Удалите его из истории Git (используйте `git filter-branch` или GitHub Secret Scanning)
2. Измените пароль на камере
3. Обновите `.env` на VPS

## 📋 Полезные команды

### На VPS:

```bash
# Просмотр логов в реальном времени
docker compose logs -f

# Остановка
docker compose stop

# Запуск
docker compose start

# Перезапуск
docker compose restart

# Полная остановка и удаление
docker compose down

# Статистика использования ресурсов
docker stats traffic-counter
```

### Обновление проекта:

```bash
# Автоматическое обновление
./update.sh

# Или вручную
git pull
docker compose up -d --build
```

## ❓ Проблемы?

См. подробную инструкцию в [DEPLOY.md](DEPLOY.md)

