# 🔧 Решение ошибки: E: Package 'libgl1-mesa-glx' has no installation candidate

Эта ошибка возникает в Ubuntu 22.04+ и новых версиях Debian, где пакет `libgl1-mesa-glx` был заменен на `libgl1`.

## ✅ Быстрое решение

Выполните на VPS сервере:

```bash
# Обновите список пакетов
sudo apt-get update

# Установите правильный пакет (автоматически выберет нужный)
sudo apt-get install -y libglib2.0-0
sudo apt-get install -y libgl1 2>/dev/null || sudo apt-get install -y libgl1-mesa-glx
```

## 📋 Для разных версий Ubuntu

**Ubuntu 22.04+ (новые версии):**
```bash
sudo apt-get install -y libgl1 libglib2.0-0
```

**Ubuntu 20.04 и ниже (старые версии):**
```bash
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

## 🔍 Проверка версии Ubuntu

Чтобы узнать версию Ubuntu:
```bash
lsb_release -a
# или
cat /etc/os-release
```

## 🐳 Для Docker

Если используете Docker, обновите проект:
```bash
cd ~/traffic-counter
git pull
docker compose up -d --build
```

Dockerfile уже обновлен и использует правильный пакет.

## 📝 Полная установка зависимостей

После исправления ошибки, установите все зависимости:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git libglib2.0-0
sudo apt-get install -y libgl1 2>/dev/null || sudo apt-get install -y libgl1-mesa-glx
```

Затем продолжайте установку проекта как обычно.

