# 🪟 Быстрый старт для Windows 10

Пошаговая инструкция для пользователей Windows 10.

## 📋 Что вам понадобится

1. ✅ Git для Windows (или GitHub Desktop)
2. ✅ SSH клиент (встроен в Windows 10)
3. ✅ Текстовый редактор (Блокнот, VS Code, или любой другой)

## Шаг 1: Установка Git

### Вариант A: Git для Windows (для командной строки)

1. Скачайте: https://git-scm.com/download/win
2. Запустите установщик
3. Оставьте все настройки по умолчанию
4. После установки у вас будет:
   - **Git Bash** - терминал с Linux-подобными командами
   - **Git CMD** - командная строка Windows
   - **Git GUI** - графический интерфейс

### Вариант B: GitHub Desktop (проще)

1. Скачайте: https://desktop.github.com/
2. Установите и войдите в GitHub
3. Проще работать через интерфейс

## Шаг 2: Создание репозитория на GitHub

1. Откройте https://github.com и войдите
2. Нажмите **"+"** → **"New repository"**
3. Название: `traffic-counter`
4. **НЕ** ставьте галочки на README, .gitignore, license
5. Нажмите **"Create repository"**

## Шаг 3: Загрузка проекта на GitHub

### Способ 1: Git Bash (рекомендуется)

1. **Откройте Git Bash в папке проекта:**
   - Правый клик на папке `traffic-counter` → **"Git Bash Here"**
   - Или откройте Git Bash и выполните: `cd /d/traffic-counter`

2. **Выполните команды:**

```bash
# Инициализация
git init

# Добавление файлов
git add .

# Первый коммит
git commit -m "Initial commit: Traffic counter with YOLOv8"

# Добавление удаленного репозитория (замените YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/traffic-counter.git

# Отправка на GitHub
git branch -M main
git push -u origin main
```

3. **При первом push** Git попросит ввести логин и пароль GitHub
   - Логин: ваш GitHub username
   - Пароль: используйте **Personal Access Token** (см. ниже)

### Способ 2: PowerShell

1. **Откройте PowerShell в папке проекта:**
   - Shift + Правый клик на папке → **"Открыть окно PowerShell здесь"**

2. **Выполните те же команды:**

```powershell
git init
git add .
git commit -m "Initial commit: Traffic counter with YOLOv8"
git remote add origin https://github.com/YOUR_USERNAME/traffic-counter.git
git branch -M main
git push -u origin main
```

### Способ 3: GitHub Desktop

1. Откройте GitHub Desktop
2. **File** → **"Add Local Repository"**
3. Выберите папку `D:\traffic-counter`
4. Нажмите **"Publish repository"**
5. Выберите созданный репозиторий
6. Нажмите **"Publish repository"**

## 🔑 Создание Personal Access Token (для Git)

GitHub больше не принимает обычные пароли. Нужен токен:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Нажмите **"Generate new token (classic)"**
3. Название: `traffic-counter`
4. Выберите срок действия (например, 90 дней)
5. Отметьте **`repo`** (полный доступ к репозиториям)
6. Нажмите **"Generate token"**
7. **Скопируйте токен** (он показывается только один раз!)
8. Используйте этот токен вместо пароля при `git push`

## 📝 Создание файла .env (для локальной разработки)

**Важно:** Этот файл не попадет в Git (он в .gitignore)

### Способ 1: Через Блокнот

1. Откройте Блокнот
2. Вставьте:

```
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
LINE_THICKNESS=5
COUNTING_DIRECTION=down
SHOW_VIDEO=true
SAVE_VIDEO=false
OUTPUT_VIDEO_PATH=output.avi
LOG_LEVEL=INFO
```

3. **Сохраните как** → выберите "Все файлы" → имя: `.env` (с точкой в начале!)
4. Сохраните в папку `D:\traffic-counter`

### Способ 2: Через PowerShell

```powershell
cd D:\traffic-counter
@"
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
LINE_THICKNESS=5
COUNTING_DIRECTION=down
SHOW_VIDEO=true
SAVE_VIDEO=false
OUTPUT_VIDEO_PATH=output.avi
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
```

### Способ 3: Через Git Bash

```bash
cd /d/traffic-counter
cat > .env << 'EOF'
RTSP_URL=rtsp://admin:Banana38@45.152.169.105:55555/Streaming/Channels/101
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
LINE_POSITION=400
LINE_THICKNESS=5
COUNTING_DIRECTION=down
SHOW_VIDEO=true
SAVE_VIDEO=false
OUTPUT_VIDEO_PATH=output.avi
LOG_LEVEL=INFO
EOF
```

## Шаг 4: Подключение к VPS

### Встроенный SSH в Windows 10

1. Откройте **PowerShell** или **CMD**
2. Выполните:

```powershell
ssh username@your-vps-ip
```

**Пример:**
```powershell
ssh root@45.152.169.105
```

### Если SSH не работает

1. **Включите OpenSSH:**
   - Settings → Apps → Optional Features
   - "Add a feature" → "OpenSSH Client" → Install

2. **Или используйте PuTTY:**
   - Скачайте: https://www.putty.org/
   - Установите и используйте для подключения

## Шаг 5: Развертывание на VPS

После подключения к VPS выполните:

```bash
# Клонирование проекта
git clone https://github.com/YOUR_USERNAME/traffic-counter.git
cd traffic-counter

# Запуск скрипта развертывания
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически установит Docker и запустит приложение.

## Шаг 6: Настройка на VPS

После развертывания настройте `.env` на сервере:

```bash
nano .env
```

Укажите ваш RTSP URL и сохраните (Ctrl+O, Enter, Ctrl+X).

Перезапустите:
```bash
docker compose restart
```

## 🔄 Обновление проекта

### На Windows (после изменений):

**Git Bash или PowerShell:**
```bash
git add .
git commit -m "Описание изменений"
git push
```

**GitHub Desktop:**
1. Внесите изменения
2. Напишите комментарий
3. "Commit to main"
4. "Push origin"

### На VPS:

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

## 🧪 Локальное тестирование на Windows

Если хотите протестировать на Windows перед отправкой на VPS:

1. **Установите Python 3.10+**: https://www.python.org/downloads/
2. **Откройте PowerShell в папке проекта:**
```powershell
cd D:\traffic-counter
```

3. **Создайте виртуальное окружение:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

4. **Установите зависимости:**
```powershell
pip install -r requirements.txt
```

5. **Запустите:**
```powershell
python main.py
```

Или используйте готовый скрипт:
```powershell
.\run.bat
```

## ❓ Частые проблемы

### Проблема: "git: command not found"

**Решение:** Установите Git для Windows (см. Шаг 1)

### Проблема: "Permission denied" при push

**Решение:** Используйте Personal Access Token вместо пароля

### Проблема: Не видно файл .env в проводнике

**Решение:** Это нормально - файлы с точкой скрыты. Используйте PowerShell или Git Bash для создания

### Проблема: SSH не работает

**Решение:** Включите OpenSSH Client в Optional Features или используйте PuTTY

## 📚 Полезные ссылки

- Git для Windows: https://git-scm.com/download/win
- GitHub Desktop: https://desktop.github.com/
- PuTTY: https://www.putty.org/
- Python для Windows: https://www.python.org/downloads/



