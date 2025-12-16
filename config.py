"""
Конфигурационный файл для проекта подсчета транспорта
"""
import os

# Настройки RTSP потока
RTSP_URL = os.getenv(
    "RTSP_URL",
    "rtsp://username:password@192.168.1.64:554/Streaming/Channels/101"
)

# Настройки детекции
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")  # yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
VEHICLE_CLASSES = [2, 3, 5, 7]  # COCO: 2=car, 3=motorcycle, 5=bus, 7=truck

# Настройки подсчета
LINE_POSITION = int(os.getenv("LINE_POSITION", "400"))  # Y-координата линии подсчета
LINE_THICKNESS = int(os.getenv("LINE_THICKNESS", "5"))
COUNTING_DIRECTION = os.getenv("COUNTING_DIRECTION", "down")  # "up" или "down"

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

