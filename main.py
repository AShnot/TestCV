"""
Главный модуль приложения трекинга трафика
"""

from tracker.traffic_tracker import TrafficTracker
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Главная функция приложения
    """
    logger.info("Запуск приложения трекинга трафика")
    
    video_path = r"D:\Python_projects\TestCV\cvtest.avi"
    
    try:
        tracker = TrafficTracker(video_path)
        tracker.run()
    except KeyboardInterrupt:
        logger.info("Приложение прервано пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Приложение завершено")


if __name__ == "__main__":
    main()
