"""
Модуль для настройки логирования
"""

import logging
import os
from config import LOG_LEVEL, LOG_DIR, LOG_FILE, LOG_FORMAT


def setup_logger(name=__name__):
    """
    Настраивает и возвращает логгер
    
    Args:
        name: имя логгера
        
    Returns:
        logging.Logger: настроенный логгер
    """
    # Создаем папку для логов, если она не существует
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Создана папка для логов: {LOG_DIR}")
    
    # Полный путь к файлу лога
    log_file_path = os.path.join(LOG_DIR, LOG_FILE)
    
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(name) 