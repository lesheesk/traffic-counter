"""
Система подсчета транспорта на основе RTSP потока и YOLOv8
"""
import os
import cv2

# opencv-python-headless может не иметь GUI и части констант — добавляем заглушки для ultralytics
if not hasattr(cv2, "imshow"):
    cv2.imshow = lambda name, img: None
if not hasattr(cv2, "waitKey"):
    cv2.waitKey = lambda delay=0: -1
if not hasattr(cv2, "destroyAllWindows"):
    cv2.destroyAllWindows = lambda: None
# Константы для imread/imwrite (ultralytics patches.py)
if not hasattr(cv2, "IMREAD_COLOR"):
    cv2.IMREAD_COLOR = 1
if not hasattr(cv2, "IMREAD_GRAYSCALE"):
    cv2.IMREAD_GRAYSCALE = 0
if not hasattr(cv2, "IMREAD_UNCHANGED"):
    cv2.IMREAD_UNCHANGED = -1
if not hasattr(cv2, "IMWRITE_JPEG_QUALITY"):
    cv2.IMWRITE_JPEG_QUALITY = 1
if not hasattr(cv2, "setNumThreads"):
    cv2.setNumThreads = lambda n: None

import numpy as np
try:
    from ultralytics import YOLO
except ImportError:
    from ultralytics.models.yolo.model import YOLO
import logging
from collections import defaultdict
from config import (
    RTSP_URL,
    YOLO_MODEL,
    CONFIDENCE_THRESHOLD,
    VEHICLE_CLASSES,
    VERTICAL_LINE_POSITION,
    LINE_THICKNESS,
    COUNTING_DIRECTION,
    SHOW_VIDEO,
    SAVE_VIDEO,
    OUTPUT_VIDEO_PATH,
    LOG_LEVEL,
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VehicleTracker:
    """
    Подсчёт пересечений линии по стабильным ID из трекера Ultralytics (ByteTrack/BoT-SORT).
    Один физический объект сохраняет один ID на протяжении всего проезда.
    """
    
    def __init__(self):
        self.vehicle_count = 0
        self.tracked_vehicles = {}  # track_id -> {'center': (x, y), 'crossed': bool}
        self.line_position = VERTICAL_LINE_POSITION
        
    def update(self, detections):
        """
        Обновляет состояние по детекциям с ID трекера.
        
        Args:
            detections: список кортежей (x1, y1, x2, y2, conf, class_id, track_id).
                        track_id может быть None — такие детекции не участвуют в подсчёте.
        """
        for detection in detections:
            x1, y1, x2, y2, conf, class_id, track_id = detection
            if track_id is None:
                continue
            track_id = int(track_id)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            prev = self.tracked_vehicles.get(track_id)
            prev_x = prev['center'][0] if prev else None
            prev_crossed = prev['crossed'] if prev else False
            
            if not prev_crossed and prev_x is not None:
                if COUNTING_DIRECTION == "left_to_right":
                    if prev_x < self.line_position and center_x >= self.line_position:
                        self.vehicle_count += 1
                        prev_crossed = True
                        logger.info(f"Автомобиль #{track_id} пересек линию слева направо. Всего: {self.vehicle_count}")
                else:
                    if prev_x > self.line_position and center_x <= self.line_position:
                        self.vehicle_count += 1
                        prev_crossed = True
                        logger.info(f"Автомобиль #{track_id} пересек линию справа налево. Всего: {self.vehicle_count}")
            
            self.tracked_vehicles[track_id] = {
                'center': (center_x, center_y),
                'crossed': prev_crossed
            }


class TrafficCounter:
    """Основной класс для подсчета транспорта"""
    
    def __init__(self):
        logger.info("Инициализация модели YOLOv8...")
        if YOLO_MODEL.endswith('.onnx') and not os.path.isfile(YOLO_MODEL):
            raise FileNotFoundError(
                f"Файл модели '{YOLO_MODEL}' не найден. "
                "Запустите run.bat (Windows) или ./run.sh (Ubuntu) — при первом запуске модель будет создана. "
                "Либо задайте YOLO_MODEL=yolov8n.pt для автоматической загрузки."
            )
        self.model = YOLO(YOLO_MODEL)
        logger.info(f"Модель {YOLO_MODEL} загружена")
        self.tracker = VehicleTracker()
        self.cap = None
        self.video_writer = None
        self._window_available = None  # None=не проверяли, True/False после первой попытки
        
    def connect_rtsp(self):
        """Подключение к RTSP потоку"""
        logger.info(f"Подключение к RTSP потоку: {RTSP_URL}")
        self.cap = cv2.VideoCapture(RTSP_URL)
        
        if not self.cap.isOpened():
            raise ConnectionError(f"Не удалось подключиться к RTSP потоку: {RTSP_URL}")
        
        # Настройка буфера
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        logger.info("Подключение к RTSP потоку установлено")
        # Размеры из характеристик потока; линия пересечения — первая четверть кадра
        stream_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        stream_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.tracker.line_position = stream_width // 4
        logger.info(
            f"Параметры потока: модель={YOLO_MODEL}, "
            f"ширина кадра по горизонтали={stream_width} px, высота={stream_height} px, "
            f"линия пересечения X={self.tracker.line_position} (25% от ширины, первая четверть)"
        )

    def setup_video_writer(self, frame_width, frame_height, fps):
        """Настройка записи видео"""
        if SAVE_VIDEO:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                OUTPUT_VIDEO_PATH,
                fourcc,
                fps,
                (frame_width, frame_height)
            )
            logger.info(f"Запись видео в файл: {OUTPUT_VIDEO_PATH}")
    
    def process_frame(self, frame):
        """Обработка одного кадра: трекинг с сохранением ID (persist=True) и подсчёт пересечений"""
        results = self.model.track(
            frame,
            persist=True,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            ids = boxes.id  # тензор (N,) или None
            for i, box in enumerate(boxes):
                class_id = int(box.cls[0])
                if class_id in VEHICLE_CLASSES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    if ids is not None and i < len(ids):
                        try:
                            track_id = int(ids[i].item() if hasattr(ids[i], 'item') else ids[i])
                        except (ValueError, TypeError):
                            track_id = None
                    else:
                        track_id = None
                    detections.append((x1, y1, x2, y2, conf, class_id, track_id))
        
        self.tracker.update(detections)
        annotated_frame = self._draw_results(frame, detections)
        return annotated_frame
    
    def _draw_results(self, frame, detections):
        """Отрисовка результатов детекции, ID трека и линии подсчета"""
        cv2.line(
            frame,
            (self.tracker.line_position, 0),
            (self.tracker.line_position, frame.shape[0]),
            (0, 255, 0),
            LINE_THICKNESS
        )
        
        class_names = {2: 'Car', 3: 'Motorcycle', 5: 'Bus', 7: 'Truck'}
        colors = {2: (255, 0, 0), 3: (0, 255, 0), 5: (0, 0, 255), 7: (255, 255, 0)}
        
        for det in detections:
            x1, y1, x2, y2, conf, class_id, track_id = det
            color = colors.get(class_id, (255, 255, 255))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(frame, (center_x, center_y), 5, color, -1)
            id_str = f"#{track_id}" if track_id is not None else "?"
            label = f"{class_names.get(class_id, 'Vehicle')} {id_str} {conf:.2f}"
            cv2.putText(
                frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )
        
        cv2.putText(
            frame, f"Vehicles: {self.tracker.vehicle_count}",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        return frame
    
    def run(self):
        """Основной цикл обработки"""
        try:
            self.connect_rtsp()
            
            frame_count = 0
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Не удалось получить кадр. Попытка переподключения...")
                    self.cap.release()
                    self.connect_rtsp()
                    continue
                
                # Обработка кадра
                processed_frame = self.process_frame(frame)
                
                # Запись видео
                if self.video_writer:
                    self.video_writer.write(processed_frame)
                
                # Отображение окна (opencv-python-headless не поддерживает GUI — пропускаем при ошибке)
                if SHOW_VIDEO:
                    if self._window_available is False:
                        pass  # уже выяснили, что окно недоступно
                    elif self._window_available is True:
                        cv2.imshow('Traffic Counter', processed_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            logger.info("Остановка по запросу пользователя")
                            break
                    else:
                        try:
                            cv2.imshow('Traffic Counter', processed_frame)
                            self._window_available = True
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                logger.info("Остановка по запросу пользователя")
                                break
                        except cv2.error:
                            self._window_available = False
                            if frame_count == 0:
                                logger.info("Окно видео недоступно (headless/без GUI), работаем без отображения")
                
                frame_count += 1
                if frame_count % 100 == 0:
                    logger.info(f"Обработано кадров: {frame_count}, Всего автомобилей: {self.tracker.vehicle_count}")
        
        except KeyboardInterrupt:
            logger.info("Остановка по сигналу прерывания")
        except Exception as e:
            logger.error(f"Ошибка: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        logger.info("Освобождение ресурсов...")
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass
        logger.info(f"Итоговое количество автомобилей: {self.tracker.vehicle_count}")


def main():
    """Точка входа"""
    logger.info("Запуск системы подсчета транспорта")
    counter = TrafficCounter()
    counter.run()


if __name__ == "__main__":
    main()



