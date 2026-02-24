"""
Система подсчета транспорта на основе RTSP потока и YOLOv8.
Целевая платформа: Windows 10/11.
"""
import os
import sys
import cv2
import numpy as np

# Трекер Ultralytics использует lap; на Windows lap часто не собирается — подменяем на scipy
import scipy.optimize
_linear_sum_assignment = scipy.optimize.linear_sum_assignment

class _LapJv:
    @staticmethod
    def lapjv(cost_matrix, extend_cost=False, cost_limit=None):
        r_ind, c_ind = _linear_sum_assignment(cost_matrix)
        n = cost_matrix.shape[0]
        x = np.full(n, -1, dtype=np.int64)
        y = np.full(cost_matrix.shape[1] if cost_matrix.ndim == 2 else n, -1, dtype=np.int64)
        for i, j in zip(r_ind, c_ind):
            if cost_limit is None or cost_matrix[i, j] <= cost_limit:
                x[i], y[j] = j, i
        return np.zeros(1), x, y

lap = type(sys)("lap")
lap.lapjv = _LapJv.lapjv
sys.modules["lap"] = lap

try:
    from ultralytics import YOLO
except ImportError:
    from ultralytics.models.yolo.model import YOLO
import logging
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

import requests

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
    STATS_OUTPUT_DIR,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Режим работы: 7:00–20:00
HOUR_START, HOUR_END = 7, 20


class DailyStats:
    """
    Почасовой учёт машин (7:00–20:00), сохранение отчёта за день в файл и отправка в Telegram.
    """
    def __init__(self):
        self._hourly = defaultdict(int)  # hour -> count
        self._current_date = date.today()
        self._finalized_dates = set()  # даты, по которым уже сохранён и отправлен отчёт
        self._output_dir = Path(STATS_OUTPUT_DIR)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def add(self, hour: int, count: int):
        if HOUR_START <= hour < HOUR_END:
            self._hourly[hour] += count

    def finalize_day(self):
        """Записать отчёт за текущий день в файл и отправить в Telegram (если настроен)."""
        today = date.today()
        if self._current_date != today:
            self._current_date = today
        if self._current_date in self._finalized_dates:
            return
        self._write_and_send(self._current_date, dict(self._hourly))
        self._finalized_dates.add(self._current_date)
        self._hourly = defaultdict(int)

    def _write_and_send(self, day: date, hourly: dict):
        total = sum(hourly.values())
        lines = [f"Дата: {day}", ""]
        for h in range(HOUR_START, HOUR_END):
            lines.append(f"{h:02d}:00-{h+1:02d}:00: {hourly.get(h, 0)}")
        lines.append("")
        lines.append(f"Итого за день: {total}")
        text = "\n".join(lines)
        path = self._output_dir / f"traffic_{day}.txt"
        path.write_text(text, encoding="utf-8")
        logger.info("Отчёт за день сохранён: %s", path)
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            self._send_telegram(path, day, total)
        else:
            logger.debug("Telegram не настроен (TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID пусты)")

    def _send_telegram(self, file_path: Path, day: date, total: int):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        try:
            with open(file_path, "rb") as f:
                r = requests.post(
                    url,
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"Подсчёт за {day}. Итого: {total}"},
                    files={"document": (file_path.name, f, "text/plain")},
                    timeout=30,
                )
            if not r.ok:
                logger.warning("Telegram sendDocument: %s %s", r.status_code, r.text)
            else:
                logger.info("Отчёт отправлен в Telegram (chat_id=%s)", TELEGRAM_CHAT_ID)
        except Exception as e:
            logger.warning("Ошибка отправки в Telegram: %s", e)


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


# Список моделей для переключения по клавише W
MODEL_OPTIONS = ["yolov8n.onnx", "yolov8s.onnx", "yolov8m.onnx"]


class TrafficCounter:
    """Основной класс для подсчета транспорта"""
    
    def __init__(self):
        logger.info("Инициализация модели YOLOv8...")
        self._rtsp_url = RTSP_URL
        self._model_list = [m for m in MODEL_OPTIONS if os.path.isfile(m)]
        if not self._model_list:
            self._model_list = MODEL_OPTIONS.copy()
        self._model_index = 0
        if YOLO_MODEL in self._model_list:
            self._model_index = self._model_list.index(YOLO_MODEL)
        self._current_model = self._model_list[self._model_index]
        if self._current_model.endswith('.onnx') and not os.path.isfile(self._current_model):
            raise FileNotFoundError(
                f"Файл модели '{self._current_model}' не найден. "
                "Запустите run.bat (Windows) или ./run.sh (Ubuntu) — при первом запуске модель будет создана."
            )
        self.model = YOLO(self._current_model, task="detect")
        logger.info(f"Модель {self._current_model} загружена")
        self.tracker = VehicleTracker()
        self._daily_stats = DailyStats()
        self._last_count = 0
        self._last_hour = datetime.now().hour
        self.cap = None
        self.video_writer = None

    def _get_stream_channel(self):
        """Возвращает '101' или '102' из текущего RTSP URL"""
        if "/Channels/101" in self._rtsp_url:
            return "101"
        if "/Channels/102" in self._rtsp_url:
            return "102"
        last = self._rtsp_url.rstrip("/").split("/")[-1]
        return last if last in ("101", "102") else "?"

    def _switch_model(self):
        """Переключение на следующую модель по клавише W"""
        self._model_index = (self._model_index + 1) % len(self._model_list)
        new_model = self._model_list[self._model_index]
        if new_model.endswith('.onnx') and not os.path.isfile(new_model):
            logger.warning(f"Модель {new_model} не найдена, пропуск")
            return
        self._current_model = new_model
        self.model = YOLO(self._current_model, task="detect")
        self.tracker = VehicleTracker()
        self._last_count = 0
        logger.info(f"Модель переключена на {self._current_model}")

    def _switch_stream(self):
        """Переключение поток 101 <-> 102 по клавише E"""
        old_url = self._rtsp_url
        if "/Channels/101" in self._rtsp_url:
            self._rtsp_url = self._rtsp_url.replace("/Channels/101", "/Channels/102")
        elif "/Channels/102" in self._rtsp_url:
            self._rtsp_url = self._rtsp_url.replace("/Channels/102", "/Channels/101")
        else:
            parts = self._rtsp_url.rstrip("/").split("/")
            if parts[-1] == "101":
                parts[-1] = "102"
            else:
                parts[-1] = "101"
            self._rtsp_url = "/".join(parts)
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
            logger.info(f"Переключение на поток: {self._get_stream_channel()}")
            self.connect_rtsp()
        except Exception as e:
            logger.warning(f"Не удалось переключить поток: {e}. Возврат к предыдущему URL.")
            self._rtsp_url = old_url
            if self.cap is None and old_url:
                try:
                    self.connect_rtsp()
                except Exception:
                    pass
        
    def connect_rtsp(self):
        """Подключение к RTSP потоку"""
        logger.info(f"Подключение к RTSP потоку: {self._rtsp_url}")
        self.cap = cv2.VideoCapture(self._rtsp_url)
        
        if not self.cap.isOpened():
            raise ConnectionError(f"Не удалось подключиться к RTSP потоку: {self._rtsp_url}")
        
        # Настройка буфера
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        logger.info("Подключение к RTSP потоку установлено")
        # Размеры из характеристик потока; при смене канала разрешение меняется — линию всегда пересчитываем
        stream_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        stream_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.tracker.line_position = stream_width // 3
        logger.info(
            f"Параметры потока: модель={self._current_model}, канал={self._get_stream_channel()}, "
            f"ширина={stream_width} px, высота={stream_height} px, "
            f"линия X={self.tracker.line_position} (1/3 от ширины)"
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
        # Почасовой учёт (7:00–20:00) для сохранения в файл и Telegram
        new_count = self.tracker.vehicle_count
        if new_count > self._last_count:
            hour = datetime.now().hour
            if HOUR_START <= hour < HOUR_END:
                self._daily_stats.add(hour, new_count - self._last_count)
        self._last_count = new_count
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
        # Текущая модель и поток, подсказки по клавишам W / E
        cv2.putText(
            frame, f"Model: {self._current_model} [W]",
            (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
        cv2.putText(
            frame, f"Stream: {self._get_stream_channel()} [E]",
            (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
        return frame
    
    def run(self):
        """Основной цикл обработки"""
        try:
            self.connect_rtsp()
            
            frame_count = 0
            while True:
                if self.cap is None:
                    self.connect_rtsp()
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
                
                # Отображение окна и обработка клавиш W / E / Q (Windows 10/11)
                if SHOW_VIDEO:
                    cv2.imshow('Traffic Counter', processed_frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        logger.info("Остановка по запросу пользователя")
                        break
                    if key == ord('w'):
                        self._switch_model()
                    if key == ord('e'):
                        self._switch_stream()
                
                frame_count += 1
                if frame_count % 100 == 0:
                    logger.info(f"Обработано кадров: {frame_count}, Всего автомобилей: {self.tracker.vehicle_count}")
                # В 20:00 — сохранить отчёт за день и отправить в Telegram
                now_hour = datetime.now().hour
                if now_hour >= HOUR_END and self._last_hour < HOUR_END:
                    self._daily_stats.finalize_day()
                self._last_hour = now_hour
        
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
        cv2.destroyAllWindows()
        self._daily_stats.finalize_day()
        logger.info(f"Итоговое количество автомобилей: {self.tracker.vehicle_count}")


def main():
    """Точка входа"""
    logger.info("Запуск системы подсчета транспорта")
    counter = TrafficCounter()
    counter.run()


if __name__ == "__main__":
    main()



