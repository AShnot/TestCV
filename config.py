"""
Конфигурационный файл для настроек трекинга трафика
"""

# Классы, которые отслеживаем
TARGET_CLASSES = ['car', 'motorcycle', 'truck']

# Размер окна отображения
DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 540

# Настройки модели YOLO
YOLO_MODEL_PATH = "yolov8s.pt"
YOLO_CONFIDENCE = 0.3
YOLO_IOU = 0.5

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_DIR = "logs"
LOG_FILE = "traffic_tracker.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Настройки отображения
STATUS_UPDATE_INTERVAL = 30  # кадров 