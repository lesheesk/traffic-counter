# Traffic Counting System based on RTSP and YOLOv8

Подсчёт проезжающего транспорта по RTSP-потоку камеры Hikvision с детекцией YOLOv8.

**Платформа:** только Windows 10/11.

## Features

- 📹 Connect to RTSP stream from Hikvision camera
- 🚗 Vehicle detection using YOLOv8 (ONNX Runtime)
- 📊 Line crossing counting
- 🎥 Optional processed video recording
- 📦 Build executable .exe file for Windows (~50-80 MB)

## Project Structure

```
traffic-counter/
├── main.py              # Main application code
├── config.py            # Configuration file
├── requirements.txt     # Python dependencies
├── run.bat              # Windows startup script
├── run.sh               # (опционально) Linux
├── build.bat            # .exe build script
├── BUILD.md             # Build instructions
└── README.md            # Documentation
```

## Requirements

- **Windows 10 или 11**
- Python 3.10+ (для разработки и сборки .exe)
- Камера Hikvision с доступом по RTSP

## Installation and Running

### Option 1: Using .exe file (перенос на другой ПК)

1. **Сборка:**
   ```batch
   build.bat
   ```
   Требуется Python и зависимости; сборка может занять несколько минут.

2. **Результат:** папка `dist\traffic-counter\` с файлом `traffic-counter.exe` и библиотеками.

3. **Перенос на другой компьютер:**
   - Скопируйте **всю папку** `dist\traffic-counter\` на целевой ПК (Python на нём не нужен).
   - Положите в эту же папку файл модели, например `yolov8m.onnx` (или задайте переменную окружения `YOLO_MODEL`).
   - При необходимости положите туда же `config.py` для своих настроек RTSP и т.д.
   - Запустите `traffic-counter.exe`.

### Option 2: Using Python script

1. **Install Python 3.10+** (if not already installed):
   - Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Run script:**
   ```batch
   run.bat
   ```
   
   Script will automatically:
   - Create virtual environment (if needed)
   - Install dependencies
   - Run application

3. **Or manually:**
   ```batch
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

### Option 3 (опционально): Ubuntu / Linux

Ниже — инструкции для запуска на Linux (основная платформа — Windows 10/11). Установка и обновления выполняются из командной строки через GitHub.

**Требования к ПК:** AMD Ryzen 5700G, 16 GB ОЗУ, 512 GB SSD (или аналог). По умолчанию — модель **yolov8n.onnx** (минимальная нагрузка на CPU); при запасе по ресурсам можно задать `YOLO_MODEL=yolov8s.onnx` или `yolov8m.onnx`.

#### Первичная установка

1. Установите зависимости системы (если ещё не установлены):
   ```bash
   sudo apt update
   sudo apt install -y git python3 python3-venv python3-pip
   ```

2. Клонируйте репозиторий с GitHub:
   ```bash
   git clone https://github.com/YOUR_USERNAME/traffic-counter.git
   cd traffic-counter
   ```
   Замените `YOUR_USERNAME` на ваш логин или организацию в GitHub.

3. Сделайте скрипт запуска исполняемым и запустите приложение:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   При первом запуске скрипт создаст виртуальное окружение, установит зависимости и при отсутствии файла модели (по умолчанию `yolov8n.onnx`) — однократно загрузит соответствующий .pt и создаст ONNX (нужен интернет).

4. (Опционально) Задайте URL камеры перед запуском:
   ```bash
   export RTSP_URL="rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101"
   ./run.sh
   ```

#### Обновление приложения из GitHub

Чтобы получить последние изменения и перезапустить приложение:

```bash
cd traffic-counter
git pull origin main
./run.sh
```

Если в репозитории изменился `requirements.txt`, зависимости переустановятся при следующем запуске только после удаления маркера установки. Чтобы принудительно переустановить зависимости:

```bash
rm -f venv/.dependencies_installed
./run.sh
```

#### Просмотр видеопотока на экране (Ubuntu с монитором)

По умолчанию используется `opencv-python-headless` (без GUI), поэтому окно с видео не открывается. Чтобы видеть поток на экране:

**Вариант 1 — скрипт (рекомендуется):**
```bash
chmod +x setup-display.sh
./setup-display.sh
./run.sh
```

**Вариант 2 — вручную:**

1. Установите системные пакеты для GUI OpenCV:
   ```bash
   sudo apt update
   sudo apt install -y libgtk2.0-dev pkg-config libgl1 libglx-mesa0
   ```

2. В каталоге проекта в виртуальном окружении замените headless на полный OpenCV:
   ```bash
   source venv/bin/activate
   pip uninstall opencv-python-headless -y
   pip install opencv-python>=4.8.0
   ```

3. Запустите приложение (отображение по умолчанию включено):
   ```bash
   ./run.sh
   ```

Окно «Traffic Counter» появится на экране; выход по клавише **q**. Для работы без монитора снова установите headless: `pip uninstall opencv-python -y && pip install opencv-python-headless`.

#### Запуск в фоне (опционально)

```bash
nohup ./run.sh > traffic-counter.log 2>&1 &
```

Остановка: найдите процесс `python main.py` и завершите его (например, `pkill -f "python main.py"` или по PID).

## RTSP URL Configuration for Hikvision

Hikvision camera RTSP URL format:
```
rtsp://username:password@IP_ADDRESS:PORT/Streaming/Channels/CHANNEL
```

Examples:
- Main stream: `rtsp://admin:password123@192.168.1.64:554/Streaming/Channels/101`
- Sub stream: `rtsp://admin:password123@192.168.1.64:554/Streaming/Channels/102`

Where:
- `101` - main stream (high resolution)
- `102` - sub stream (low resolution)

## Configuration

### Environment Variables

| Variable | Description | Default |
|------------|----------|--------------|
| `RTSP_URL` | RTSP stream URL | (see config.py) |
| `YOLO_MODEL` | YOLOv8 model (n/s/m/l/x) | `yolov8n.onnx` |
| `CONFIDENCE_THRESHOLD` | Detection confidence threshold | `0.5` |
| `VERTICAL_LINE_POSITION` | X coordinate of vertical counting line | `480` |
| `LINE_THICKNESS` | Line thickness | `1` |
| `COUNTING_DIRECTION` | Counting direction (left_to_right/right_to_left) | `left_to_right` |
| `SHOW_VIDEO` | Show video window | `true` |
| `SAVE_VIDEO` | Save video | `false` |
| `OUTPUT_VIDEO_PATH` | Output video path | `output.avi` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `STATS_OUTPUT_DIR` | Каталог для отчётов за день | `stats` |
| `TELEGRAM_BOT_TOKEN` | Токен бота для отправки отчёта в Telegram | (пусто) |
| `TELEGRAM_CHAT_ID` | ID чата получателя (например для @leshee) | (пусто) |

### Сохранение подсчёта за день и Telegram

Программа ведёт почасовой учёт (7:00–20:00). В файл `STATS_OUTPUT_DIR/traffic_YYYY-MM-DD.txt` записываются количество машин по каждому часу и итог за день. В 20:00 и при завершении работы отчёт сохраняется и при указанных `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` отправляется в Telegram (файл + подпись с итогом). Чтобы отправлять отчёт пользователю @leshee: создайте бота через [@BotFather](https://t.me/BotFather), укажите `TELEGRAM_BOT_TOKEN`; пользователь @leshee должен один раз написать боту, после чего его `chat_id` можно узнать через [getUpdates](https://core.telegram.org/bots/api#getupdates) и задать `TELEGRAM_CHAT_ID`.

### Configuration via config.py

Edit `config.py` file to change default settings.

### Vehicle Classes

By default, the following COCO classes are tracked:
- `2` - Car
- `3` - Motorcycle
- `5` - Bus
- `7` - Truck

Configuration in `config.py`: `VEHICLE_CLASSES = [2, 7]`

## Usage

1. **Run application** (see "Installation and Running" section)

2. **Configure counting line:**
   - Change `VERTICAL_LINE_POSITION` in configuration to set X coordinate of line
   - Line is displayed in green on video

3. **Observe counting:**
   - Detected objects are displayed with bounding boxes
   - Object center is marked with a dot
   - Counter updates when line is crossed

4. **Stop:**
   - Press `q` in video window (if `SHOW_VIDEO=true`)
   - Or `Ctrl+C` in terminal

5. **Горячие клавиши в окне видео:**
   - **Q** — выход
   - **W** — смена модели YOLO (nano → small → medium → …)
   - **E** — смена видеопотока (канал 101 ↔ 102). Текущая модель и канал отображаются на экране.

## YOLOv8 Models

The project uses ONNX Runtime to work with YOLOv8 models.

**Model format:** `.onnx` (not `.pt`)

Available models (from fastest to most accurate):
- `yolov8n.onnx` - Nano (по умолчанию; быстрее всего, меньше нагрузка на CPU)
- `yolov8s.onnx` - Small
- `yolov8m.onnx` - Medium
- `yolov8l.onnx` - Large
- `yolov8x.onnx` - XLarge (most accurate, slower)

### Converting models from .pt to .onnx

If you have models in `.pt` format, you need to convert them:

1. **Temporarily install ultralytics:**
   ```batch
   pip install ultralytics
   ```

2. **Run conversion script:**
   ```batch
   python convert_to_onnx.py
   ```

3. **After conversion you can remove ultralytics:**
   ```batch
   pip uninstall ultralytics torch torchvision -y
   ```

For details see [MIGRATION_TO_ONNX.md](MIGRATION_TO_ONNX.md)

## Building Executable File

Создание переносимого .exe для запуска на любом Windows без установки Python:

1. Запустите `build.bat` (нужны Python и интернет для установки зависимостей).
2. В папке `dist\traffic-counter\` появятся `traffic-counter.exe` и все нужные библиотеки.
3. Перенесите папку целиком на другой ПК, добавьте в неё файл модели (например `yolov8m.onnx`) и при необходимости `config.py`.

## Troubleshooting

### Problem: ImportError or crash when importing cv2

**Solution:** На Windows используйте `opencv-python` (не headless): `pip install opencv-python>=4.8.0`. Переустановите зависимости из `requirements.txt`.

### Problem: Cannot connect to RTSP stream

**Solution:**
- Check URL, username and password correctness
- Ensure camera is accessible on network
- Check RTSP settings on camera
- Try connecting via VLC to verify

### Problem: Low performance / CPU >100% / выпадают кадры

**Solution:**
- По умолчанию используется **yolov8n.onnx** (nano) — минимальная нагрузка на CPU. Если переключили на m/l/x и сервер не успевает, верните nano: `export YOLO_MODEL=yolov8n.onnx` (или в config.py).
- Уменьшите разрешение потока в настройках камеры или используйте субпоток (канал 102 вместо 101).
- При необходимости смените модель вручную: `YOLO_MODEL=yolov8s.onnx` или `yolov8m.onnx` при достаточном запасе по CPU.

### Problem: Inaccurate counting

**Solution:**
- Configure `VERTICAL_LINE_POSITION` for optimal placement
- Increase `CONFIDENCE_THRESHOLD` to filter false positives
- Use more accurate YOLOv8 model (yolov8m.onnx or higher)

## Logging

Logs are output to console with information about:
- RTSP stream connection
- Line crossings by vehicles
- Total number of processed frames
- Errors and warnings

## License

This project is provided "as is" for educational purposes.

## Support

If problems occur, check:
1. Application logs
2. RTSP camera settings
3. Network connection
4. Dependency versions
