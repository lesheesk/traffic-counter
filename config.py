"""
Конфигурационный файл для проекта подсчета транспорта
"""
import os

# Настройки RTSP потока
RTSP_URL = os.getenv(
    "RTSP_URL",
    "rtsp://admin:Banana38@45.152.169.105:55556/Streaming/Channels/102"
)

# Настройки детекции
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8m.onnx")  # n=легче/быстрее, s, m, l, x=точнее/медленнее
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
VEHICLE_CLASSES = [2,7]  # COCO: 2=car, 3=motorcycle, 5=bus, 7=truck

# Настройки подсчета
VERTICAL_LINE_POSITION = int(os.getenv("VERTICAL_LINE_POSITION", "160"))  # X-координата вертикальной линии подсчета (слева направо)
LINE_THICKNESS = int(os.getenv("LINE_THICKNESS", "1"))
COUNTING_DIRECTION = os.getenv("COUNTING_DIRECTION", "left_to_right")  # "left_to_right" или "right_to_left"

# Настройки видео
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "1920"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "1080"))
FPS = int(os.getenv("FPS", "25"))

# Настройки отображения
SHOW_VIDEO = os.getenv("SHOW_VIDEO", "true").lower() == "true"
SAVE_VIDEO = os.getenv("SAVE_VIDEO", "false").lower() == "true"
OUTPUT_VIDEO_PATH = os.getenv("OUTPUT_VIDEO_PATH", "output.avi")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

