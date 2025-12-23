# 🚀 Быстрое решение проблемы с паролем на VPS

Если при клонировании публичного репозитория Git все равно запрашивает пароль, выполните на VPS:

## ✅ Решение (скопируйте и выполните на VPS):

```bash
# 1. Очистите сохраненные учетные данные Git
git config --global --unset credential.helper
rm ~/.git-credentials 2>/dev/null

# 2. Клонируйте репозиторий БЕЗ username в URL
cd ~
git clone https://github.com/lesheesk/traffic-counter.git
cd traffic-counter

# 3. Запустите развертывание
chmod +x deploy.sh
./deploy.sh
```

## ⚠️ Важно:

- **НЕ используйте** URL с username: `https://lesheesk@github.com/...`
- **Используйте** URL без username: `https://github.com/lesheesk/...`

Если Git все равно запрашивает пароль после очистки кэша, проверьте:
1. Репозиторий действительно публичный (Settings → Change visibility → Make public)
2. URL правильный (без username перед `@`)

## 📝 Если уже клонировали с неправильным URL:

```bash
cd ~/traffic-counter
git remote set-url origin https://github.com/lesheesk/traffic-counter.git
git pull
```

