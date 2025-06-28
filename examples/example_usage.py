"""
Пример использования TrafficTracker
"""

import threading
import time
from tracker.traffic_tracker import TrafficTracker
from utils.logger import setup_logger

logger = setup_logger(__name__)


def example_basic_usage():
    """
    Базовый пример использования трекера
    """
    logger.info("Запуск базового примера")
    
    video_path = r"D:\Python_projects\TestCV\cvtest.avi"
    tracker = TrafficTracker(video_path)
    
    try:
        tracker.run()
    except KeyboardInterrupt:
        logger.info("Пример прерван пользователем")
    finally:
        tracker.stop()


def example_multithreaded_usage():
    """
    Пример использования трекера в многопоточном режиме
    """
    logger.info("Запуск многопоточного примера")
    
    video_path = r"D:\Python_projects\TestCV\cvtest.avi"
    tracker = TrafficTracker(video_path)
    
    # Запуск трекера в отдельном потоке
    tracker_thread = threading.Thread(target=tracker.run)
    tracker_thread.start()
    
    try:
        # Мониторинг статуса в основном потоке
        while tracker_thread.is_alive():
            status = tracker.get_object_on_line_status()
            logger.info(f"Статус линии: {'ОБЪЕКТ НА ЛИНИИ!' if status else 'Линия свободна'}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Пример прерван пользователем")
    finally:
        tracker.stop()
        tracker_thread.join(timeout=5)


def example_custom_config():
    """
    Пример с кастомной конфигурацией
    """
    logger.info("Запуск примера с кастомной конфигурацией")
    
    # Здесь можно импортировать и изменить config.py
    # или передать параметры напрямую в класс
    
    video_path = r"D:\Python_projects\TestCV\cvtest.avi"
    tracker = TrafficTracker(video_path)
    
    try:
        tracker.run()
    except KeyboardInterrupt:
        logger.info("Пример прерван пользователем")
    finally:
        tracker.stop()


if __name__ == "__main__":
    print("Выберите пример:")
    print("1. Базовое использование")
    print("2. Многопоточное использование")
    print("3. Кастомная конфигурация")
    
    choice = input("Введите номер (1-3): ").strip()
    
    if choice == "1":
        example_basic_usage()
    elif choice == "2":
        example_multithreaded_usage()
    elif choice == "3":
        example_custom_config()
    else:
        print("Неверный выбор. Запускаем базовый пример.")
        example_basic_usage() 