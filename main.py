"""
Система подсчета транспорта на основе RTSP потока и YOLOv8 (ONNX Runtime)
"""
import cv2
import numpy as np
import onnxruntime as ort
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
    LOG_LEVEL
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VehicleTracker:
    """Класс для отслеживания и подсчета транспортных средств"""
    
    def __init__(self):
        self.vehicle_count = 0
        self.tracked_vehicles = {}  # ID -> {'center': (x, y), 'crossed': bool}
        self.next_id = 0
        self.line_position = VERTICAL_LINE_POSITION
        
    def update(self, detections):
        """
        Обновляет состояние отслеживаемых объектов
        
        Args:
            detections: список детекций в формате [(x1, y1, x2, y2, conf, class_id), ...]
        """
        current_centers = {}
        
        for detection in detections:
            x1, y1, x2, y2, conf, class_id = detection
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Находим ближайший существующий трек или создаем новый
            vehicle_id = self._assign_or_create_track(center_x, center_y)
            current_centers[vehicle_id] = (center_x, center_y)
            
            # Проверяем пересечение вертикальной линии (слева направо)
            if vehicle_id in self.tracked_vehicles:
                prev_x = self.tracked_vehicles[vehicle_id]['center'][0]
                prev_crossed = self.tracked_vehicles[vehicle_id]['crossed']
                
                if not prev_crossed:
                    if COUNTING_DIRECTION == "left_to_right":
                        # Движение слева направо: пересечение линии справа
                        if prev_x < self.line_position and center_x >= self.line_position:
                            self.vehicle_count += 1
                            self.tracked_vehicles[vehicle_id]['crossed'] = True
                            logger.info(f"Автомобиль #{vehicle_id} пересек линию слева направо. Всего: {self.vehicle_count}")
                    else:  # right_to_left
                        # Движение справа налево: пересечение линии слева
                        if prev_x > self.line_position and center_x <= self.line_position:
                            self.vehicle_count += 1
                            self.tracked_vehicles[vehicle_id]['crossed'] = True
                            logger.info(f"Автомобиль #{vehicle_id} пересек линию справа налево. Всего: {self.vehicle_count}")
            
            # Обновляем позицию
            self.tracked_vehicles[vehicle_id] = {
                'center': (center_x, center_y),
                'crossed': self.tracked_vehicles.get(vehicle_id, {}).get('crossed', False)
            }
        
        # Удаляем старые треки (которые не были обнаружены в текущем кадре)
        active_ids = set(current_centers.keys())
        self.tracked_vehicles = {
            vid: data for vid, data in self.tracked_vehicles.items()
            if vid in active_ids
        }
    
    def _assign_or_create_track(self, center_x, center_y):
        """Назначает существующий трек или создает новый"""
        min_distance = float('inf')
        assigned_id = None
        
        for vid, data in self.tracked_vehicles.items():
            if data['crossed']:
                continue
            prev_center = data['center']
            distance = np.sqrt(
                (center_x - prev_center[0])**2 + 
                (center_y - prev_center[1])**2
            )
            if distance < min_distance and distance < 100:  # Максимальное расстояние для связи
                min_distance = distance
                assigned_id = vid
        
        if assigned_id is None:
            assigned_id = self.next_id
            self.next_id += 1
        
        return assigned_id


class YOLOv8ONNX:
    """Класс для работы с YOLOv8 моделью через ONNX Runtime"""
    
    def __init__(self, model_path, conf_threshold=0.5):
        """
        Инициализация ONNX модели
        
        Args:
            model_path: путь к .onnx файлу модели
            conf_threshold: порог уверенности детекции
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.input_size = 640  # YOLOv8 использует размер 640x640
        
        # Создаем сессию ONNX Runtime
        providers = ['CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)
        
        # Получаем информацию о входе и выходе модели
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        logger.info(f"ONNX модель {model_path} загружена")
    
    def preprocess(self, image):
        """
        Предобработка изображения для модели
        
        Args:
            image: входное изображение (BGR формат от OpenCV)
        
        Returns:
            preprocessed: предобработанное изображение (1, 3, 640, 640)
            scale: масштаб для преобразования координат обратно
            pad: отступы для преобразования координат
        """
        # Получаем размеры исходного изображения
        h, w = image.shape[:2]
        
        # Вычисляем масштаб и размеры для сохранения пропорций
        scale = min(self.input_size / h, self.input_size / w)
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Изменяем размер изображения с сохранением пропорций
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Создаем квадратное изображение с нулевыми отступами
        padded = np.full((self.input_size, self.input_size, 3), 114, dtype=np.uint8)
        pad_h = (self.input_size - new_h) // 2
        pad_w = (self.input_size - new_w) // 2
        padded[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized
        
        # Преобразуем в формат модели: BGR -> RGB, нормализация, транспонирование
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        transposed = np.transpose(normalized, (2, 0, 1))
        batched = np.expand_dims(transposed, axis=0)
        
        return batched, scale, (pad_w, pad_h)
    
    def postprocess(self, output, scale, pad, original_shape):
        """
        Постобработка вывода модели
        
        Args:
            output: вывод модели (numpy array) - формат [1, 84, num_detections]
            scale: масштаб предобработки
            pad: отступы (pad_w, pad_h)
            original_shape: исходный размер изображения (h, w)
        
        Returns:
            detections: список детекций в формате [(x1, y1, x2, y2, conf, class_id), ...]
        """
        # YOLOv8 выдает тензор формы [1, 84, num_detections]
        # Где 84 = 4 (координаты xywh) + 80 (классы COCO)
        # Транспонируем в [num_detections, 84]
        predictions = np.squeeze(output, axis=0).transpose((1, 0))
        
        detections = []
        original_h, original_w = original_shape[:2]
        pad_w, pad_h = pad
        
        for pred in predictions:
            # Координаты центра и размеры (в пикселях на изображении 640x640)
            x_center, y_center, width, height = pred[:4]
            
            # Преобразуем обратно в исходное разрешение
            x_center = (x_center - pad_w) / scale
            y_center = (y_center - pad_h) / scale
            width = width / scale
            height = height / scale
            
            # Преобразуем в формат (x1, y1, x2, y2)
            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)
            
            # Ограничиваем координаты рамкой изображения
            x1 = max(0, min(x1, original_w))
            y1 = max(0, min(y1, original_h))
            x2 = max(0, min(x2, original_w))
            y2 = max(0, min(y2, original_h))
            
            # Пропускаем если размеры некорректны
            if x2 <= x1 or y2 <= y1:
                continue
            
            # Находим класс с максимальной вероятностью
            scores = pred[4:]
            class_id = np.argmax(scores)
            confidence = float(scores[class_id])
            
            # Фильтруем по порогу уверенности и нужным классам
            if confidence >= self.conf_threshold and class_id in VEHICLE_CLASSES:
                detections.append((x1, y1, x2, y2, confidence, class_id))
        
        return detections
    
    def predict(self, image):
        """
        Предсказание на изображении
        
        Args:
            image: входное изображение (BGR формат от OpenCV)
        
        Returns:
            detections: список детекций в формате [(x1, y1, x2, y2, conf, class_id), ...]
        """
        # Предобработка
        preprocessed, scale, pad = self.preprocess(image)
        
        # Инференс
        outputs = self.session.run([self.output_name], {self.input_name: preprocessed})
        
        # Постобработка
        detections = self.postprocess(outputs[0], scale, pad, image.shape)
        
        return detections


class TrafficCounter:
    """Основной класс для подсчета транспорта"""
    
    def __init__(self):
        logger.info("Инициализация модели YOLOv8 (ONNX Runtime)...")
        self.model = YOLOv8ONNX(YOLO_MODEL, CONFIDENCE_THRESHOLD)
        logger.info(f"Модель {YOLO_MODEL} загружена")
        
        self.tracker = VehicleTracker()
        self.cap = None
        self.video_writer = None
        
    def connect_rtsp(self):
        """Подключение к RTSP потоку"""
        logger.info(f"Подключение к RTSP потоку: {RTSP_URL}")
        self.cap = cv2.VideoCapture(RTSP_URL)
        
        if not self.cap.isOpened():
            raise ConnectionError(f"Не удалось подключиться к RTSP потоку: {RTSP_URL}")
        
        # Настройка буфера
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        logger.info("Подключение к RTSP потоку установлено")
        
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
        """Обработка одного кадра"""
        # Детекция объектов через ONNX модель
        detections = self.model.predict(frame)
        
        # Обновление трекера
        self.tracker.update(detections)
        
        # Отрисовка результатов
        annotated_frame = self._draw_results(frame, detections)
        
        return annotated_frame
    
    def _draw_results(self, frame, detections):
        """Отрисовка результатов детекции и линии подсчета"""
        # Рисуем вертикальную линию подсчета
        cv2.line(
            frame,
            (self.tracker.line_position, 0),
            (self.tracker.line_position, frame.shape[0]),
            (0, 255, 0),
            LINE_THICKNESS
        )
        
        # Рисуем детекции
        class_names = {2: 'Car', 3: 'Motorcycle', 5: 'Bus', 7: 'Truck'}
        colors = {2: (255, 0, 0), 3: (0, 255, 0), 5: (0, 0, 255), 7: (255, 255, 0)}
        
        for x1, y1, x2, y2, conf, class_id in detections:
            color = colors.get(class_id, (255, 255, 255))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Центр объекта
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(frame, (center_x, center_y), 5, color, -1)
            
            # Метка
            label = f"{class_names.get(class_id, 'Vehicle')} {conf:.2f}"
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        # Отображаем счетчик
        cv2.putText(
            frame,
            f"Vehicles: {self.tracker.vehicle_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
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
                
                # Отображение
                if SHOW_VIDEO:
                    cv2.imshow('Traffic Counter', processed_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Остановка по запросу пользователя")
                        break
                
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
        cv2.destroyAllWindows()
        logger.info(f"Итоговое количество автомобилей: {self.tracker.vehicle_count}")


def main():
    """Точка входа"""
    logger.info("Запуск системы подсчета транспорта")
    counter = TrafficCounter()
    counter.run()


if __name__ == "__main__":
    main()



