# Traffic Counting System based on RTSP and YOLOv8

Project for counting passing vehicles through RTSP stream from Hikvision camera using YOLOv8 for object detection.

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
├── run.sh               # Ubuntu/Linux startup script
├── setup-display.sh     # Включение отображения видео на экране (Ubuntu)
├── build.bat            # .exe build script
├── BUILD.md             # Build instructions
└── README.md            # Documentation
```

## Requirements

- Python 3.10+ (for development)
- Windows 10+ (for using .exe file) or Ubuntu/Linux (см. ниже)
- Hikvision camera with RTSP access

## Installation and Running

### Option 1: Using .exe file (recommended)

1. **Build .exe file:**
   ```batch
   build.bat
   ```
   
2. **Executable file will be in:** `dist\traffic-counter.exe`

3. **Run:**
   - Copy `traffic-counter.exe` to convenient location
   - (Optional) Create `config.py` file next to exe to override settings
   - Or configure environment variables
   - Run `traffic-counter.exe`

For details see [BUILD.md](BUILD.md)

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

### Option 3: Ubuntu — установка и обновление через GitHub

Приложение предназначено для запуска на Ubuntu. Установка и обновления выполняются из командной строки через GitHub.

**Требования к ПК:** AMD Ryzen 5700G, 16 GB ОЗУ, 512 GB SSD (или аналог). Рекомендуется модель YOLOv8: `yolov8s.onnx` или `yolov8m.onnx`.

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
   При первом запуске скрипт создаст виртуальное окружение, установит зависимости и при отсутствии файла `yolov8s.onnx` — однократно загрузит `yolov8s.pt` и создаст из него ONNX-модель (нужен интернет).

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
| `YOLO_MODEL` | YOLOv8 model (n/s/m/l/x) | `yolov8s.onnx` |
| `CONFIDENCE_THRESHOLD` | Detection confidence threshold | `0.5` |
| `VERTICAL_LINE_POSITION` | X coordinate of vertical counting line | `480` |
| `LINE_THICKNESS` | Line thickness | `1` |
| `COUNTING_DIRECTION` | Counting direction (left_to_right/right_to_left) | `left_to_right` |
| `SHOW_VIDEO` | Show video window | `true` |
| `SAVE_VIDEO` | Save video | `false` |
| `OUTPUT_VIDEO_PATH` | Output video path | `output.avi` |
| `LOG_LEVEL` | Logging level | `INFO` |

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

## YOLOv8 Models

The project uses ONNX Runtime to work with YOLOv8 models.

**Model format:** `.onnx` (not `.pt`)

Available models (from fastest to most accurate):
- `yolov8n.onnx` - Nano (fastest, lower accuracy)
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

To create .exe file that can be run on any Windows computer without installing Python:

1. Run: `build.bat`
2. Executable file will be in: `dist\traffic-counter.exe`

Detailed instructions: [BUILD.md](BUILD.md)

## Troubleshooting

### Problem: ImportError or crash when importing cv2 on Ubuntu (headless/server)

**Solution:** The project uses `opencv-python-headless` (no GUI libraries required). If you still have the old environment, reinstall dependencies:
```bash
rm -f venv/.dependencies_installed
./run.sh
```
Or manually: `pip install opencv-python-headless>=4.8.0`. On a server without a display, set `SHOW_VIDEO=false` so the app does not try to open a window.

### Problem: Cannot connect to RTSP stream

**Solution:**
- Check URL, username and password correctness
- Ensure camera is accessible on network
- Check RTSP settings on camera
- Try connecting via VLC to verify

### Problem: Low performance

**Solution:**
- Use lighter YOLOv8 model (yolov8n.onnx)
- Reduce frame resolution in camera settings
- Use sub stream (channel 102) instead of main stream

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
