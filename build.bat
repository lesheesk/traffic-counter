@echo off
REM Скрипт для сборки исполняемого файла .exe

echo 📦 Сборка исполняемого файла traffic-counter.exe
echo ==================================================

REM Проверка виртуального окружения
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка при создании виртуального окружения
        pause
        exit /b 1
    )
)

REM Проверка Python в виртуальном окружении
if not exist "venv\Scripts\python.exe" (
    echo ❌ Ошибка: Python не найден в виртуальном окружении
    pause
    exit /b 1
)

REM Установка зависимостей
echo 📥 Установка зависимостей...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -m pip install pyinstaller

if errorlevel 1 (
    echo ❌ Ошибка при установке зависимостей
    pause
    exit /b 1
)

REM Очистка предыдущей сборки
if exist "dist" (
    echo 🗑️  Очистка предыдущей сборки...
    rmdir /s /q dist
)
if exist "build" (
    rmdir /s /q build
)

REM Сборка exe файла
echo 🔨 Сборка исполняемого файла...
echo Это может занять несколько минут...

venv\Scripts\python.exe -m PyInstaller ^
    --name=traffic-counter ^
    --onefile ^
    --console ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=onnxruntime ^
    --hidden-import=config ^
    --hidden-import=logging ^
    --hidden-import=collections ^
    main.py

if errorlevel 1 (
    echo ❌ Ошибка при сборке
    pause
    exit /b 1
)

echo.
echo ✅ Сборка завершена успешно!
echo.
echo 📁 Исполняемый файл находится в папке: dist\traffic-counter.exe
echo.
echo ⚠️  Важно:
echo    1. Файл traffic-counter.exe можно запускать на любом Windows компьютере
echo    2. config.py встроен в exe (можно создать внешний для переопределения настроек)
echo    3. Модели YOLO (*.onnx) должны находиться рядом с exe файлом
echo    4. Для настройки используйте переменные окружения или внешний config.py
echo.
pause

