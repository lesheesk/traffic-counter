"""
Скрипт для конвертации YOLOv8 модели из .pt в .onnx формат
Использование: python convert_to_onnx.py
"""
import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ Ошибка: ultralytics не установлен")
    print("Установите: pip install ultralytics")
    sys.exit(1)

def convert_model(input_model: str, output_model: str = None):
    """
    Конвертирует YOLOv8 модель из .pt в .onnx
    
    Args:
        input_model: путь к исходной .pt модели
        output_model: путь к выходной .onnx модели (опционально)
    """
    if not Path(input_model).exists():
        print(f"❌ Файл {input_model} не найден")
        return False
    
    if output_model is None:
        output_model = str(Path(input_model).with_suffix('.onnx'))
    
    print(f"🔄 Конвертация {input_model} → {output_model}")
    
    try:
        # Загружаем модель
        model = YOLO(input_model)
        
        # Экспортируем в ONNX
        model.export(
            format='onnx',
            imgsz=640,  # Размер входного изображения (стандартный для YOLOv8)
            simplify=True,  # Упростить модель
            opset=12,  # Версия ONNX opset
        )
        
        # Получаем путь к экспортированной модели
        exported_path = Path(input_model).with_suffix('.onnx')
        
        # Если нужно переименовать
        if exported_path.name != Path(output_model).name:
            exported_path.rename(output_model)
        
        print(f"✅ Модель успешно конвертирована: {output_model}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        return False

if __name__ == "__main__":
    # Модели для конвертации
    models_to_convert = [
        "yolov8n.pt",
        "yolov8s.pt",
        "yolov8m.pt",
    ]
    
    print("📦 Конвертация YOLOv8 моделей в ONNX формат")
    print("=" * 50)
    
    converted = 0
    for model_name in models_to_convert:
        if Path(model_name).exists():
            if convert_model(model_name):
                converted += 1
            print()
        else:
            print(f"⚠️  Файл {model_name} не найден, пропускаем")
    
    print(f"✅ Конвертировано моделей: {converted}/{len(models_to_convert)}")
    print("\n💡 Теперь можно использовать .onnx модели в приложении")

