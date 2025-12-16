# ✅ Чеклист для Windows 10

Быстрая памятка для развертывания проекта на VPS с Windows 10.

## 📦 Подготовка (один раз)

- [ ] Установлен Git для Windows: https://git-scm.com/download/win
- [ ] Создан аккаунт на GitHub
- [ ] Создан Personal Access Token на GitHub (Settings → Developer settings → Personal access tokens)

## 🚀 Загрузка на GitHub

- [ ] Создан репозиторий на GitHub (без README, .gitignore, license)
- [ ] Открыт Git Bash в папке проекта (правый клик → "Git Bash Here")
- [ ] Выполнены команды:
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git remote add origin https://github.com/YOUR_USERNAME/traffic-counter.git
  git push -u origin main
  ```
- [ ] Проект успешно загружен на GitHub

## 🔐 Безопасность

- [ ] Создан файл `.env` с паролями (НЕ коммитится в Git)
- [ ] Проверено, что `.env` в `.gitignore`
- [ ] Пароли удалены из `config.py` и `docker-compose.yml`

## 🖥️ Подключение к VPS

- [ ] Включен OpenSSH Client в Windows (Settings → Apps → Optional Features)
- [ ] Проверено подключение: `ssh user@vps-ip`
- [ ] Или установлен PuTTY: https://www.putty.org/

## 🐳 Развертывание на VPS

- [ ] Подключились к VPS через SSH
- [ ] Выполнено клонирование: `git clone https://github.com/YOUR_USERNAME/traffic-counter.git`
- [ ] Запущен скрипт развертывания: `./deploy.sh`
- [ ] Настроен `.env` файл на VPS с правильным RTSP_URL
- [ ] Приложение запущено и работает

## 🔄 Обновление проекта

**На Windows:**
- [ ] Внесены изменения в код
- [ ] Выполнено: `git add .`, `git commit -m "..."`, `git push`

**На VPS:**
- [ ] Выполнено: `cd ~/traffic-counter && ./update.sh`
- [ ] Или вручную: `git pull && docker compose up -d --build`

## 📝 Полезные команды

### На Windows (Git Bash):
```bash
# Проверка статуса
git status

# Добавление изменений
git add .

# Коммит
git commit -m "Описание"

# Отправка на GitHub
git push
```

### На VPS:
```bash
# Просмотр логов
docker compose logs -f

# Перезапуск
docker compose restart

# Остановка
docker compose stop

# Обновление
cd ~/traffic-counter && ./update.sh
```

## ❓ Проблемы?

- **Git не работает:** Установите Git для Windows
- **SSH не работает:** Включите OpenSSH Client или используйте PuTTY
- **Не могу push:** Используйте Personal Access Token вместо пароля
- **Не вижу .env:** Это нормально, файлы с точкой скрыты. Используйте PowerShell или Git Bash

## 📚 Документация

- **Подробная инструкция для Windows:** [QUICK_START_WINDOWS.md](QUICK_START_WINDOWS.md)
- **Быстрый старт:** [QUICK_START.md](QUICK_START.md)
- **Подробное развертывание:** [DEPLOY.md](DEPLOY.md)

