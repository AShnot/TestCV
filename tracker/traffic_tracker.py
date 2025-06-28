"""
Модуль для трекинга трафика
"""

import cv2
import threading
import time
from ultralytics import YOLO

from utils.geometry import line_intersects_box
from utils.logger import setup_logger
from config import (
    TARGET_CLASSES, DISPLAY_WIDTH, DISPLAY_HEIGHT,
    YOLO_MODEL_PATH, YOLO_CONFIDENCE, YOLO_IOU,
    STATUS_UPDATE_INTERVAL
)

logger = setup_logger(__name__)


class TrafficTracker:
    def __init__(self, video_path):
        """
        Инициализация трекера трафика
        
        Args:
            video_path: путь к видеофайлу
        """
        self.video_path = video_path
        self.model = None
        self.cap = None
        self.line = None
        self.object_on_line = False
        self.is_running = False
        self.lock = threading.Lock()  # Для потокобезопасного доступа к object_on_line
        
        logger.info(f"TrafficTracker инициализирован для видео: {video_path}")

    def get_line_points(self):
        """
        Получает точки линии интереса от пользователя через GUI
        
        Returns:
            tuple: (p1, p2) или None если пользователь отменил
        """
        line_points = []
        SCALE_W, SCALE_H = DISPLAY_WIDTH, DISPLAY_HEIGHT

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and len(line_points) < 2:
                real_x = int(x * orig_width / SCALE_W)
                real_y = int(y * orig_height / SCALE_H)
                line_points.append((real_x, real_y))
                logger.debug(f"Добавлена точка линии: ({real_x}, {real_y})")

        ret, first_frame = self.cap.read()
        if not ret:
            logger.error("Не удалось получить первый кадр для настройки линии")
            return None

        global orig_width, orig_height
        orig_height, orig_width = first_frame.shape[:2]
        display_frame = cv2.resize(first_frame, (SCALE_W, SCALE_H))

        cv2.namedWindow("Setup", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Setup", mouse_callback)

        logger.info("Задайте линию интереса (2 клика мышью). Нажмите 'q' для отмены.")

        while len(line_points) < 2:
            temp = display_frame.copy()
            for i, pt in enumerate(line_points):
                draw_x = int(pt[0] * SCALE_W / orig_width)
                draw_y = int(pt[1] * SCALE_H / orig_height)
                cv2.circle(temp, (draw_x, draw_y), 5, (0, 0, 255), -1)
                if i == 1:
                    prev = (int(line_points[0][0] * SCALE_W / orig_width),
                            int(line_points[0][1] * SCALE_H / orig_height))
                    cv2.line(temp, prev, (draw_x, draw_y), (255, 0, 0), 2)

            cv2.imshow("Setup", temp)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                logger.info("Пользователь отменил настройку линии")
                cv2.destroyWindow("Setup")
                return None

        cv2.destroyWindow("Setup")
        logger.info(f"Линия интереса установлена: {line_points[0]} -> {line_points[1]}")
        return line_points[0], line_points[1]

    def get_object_on_line_status(self):
        """
        Возвращает текущий статус наличия объекта на линии
        
        Returns:
            bool: True если объект находится на линии, False иначе
        """
        with self.lock:
            return self.object_on_line

    def run(self):
        """
        Основной метод запуска трекинга
        """
        try:
            logger.info("Загрузка модели YOLO...")
            self.model = YOLO(YOLO_MODEL_PATH)
            logger.info("Модель YOLO успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            return

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            logger.error(f"Не удалось открыть видео: {self.video_path}")
            return

        logger.info("Получение линии интереса...")
        self.line = self.get_line_points()
        if self.line is None:
            logger.error("Линия интереса не задана. Завершение работы.")
            self.cap.release()
            return

        self.is_running = True
        logger.info("Обработка началась. Нажмите 'q' для выхода.")

        frame_count = 0
        start_time = time.time()

        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    logger.info("Видео окончено или кадр повреждён.")
                    break

                frame_count += 1
                
                # Обработка кадра с YOLO
                results = self.model.track(frame, persist=False, conf=YOLO_CONFIDENCE, 
                                         iou=YOLO_IOU, verbose=False)[0]

                if not hasattr(results, 'boxes') or results.boxes is None:
                    continue

                annotated = frame.copy()
                l1_p1, l1_p2 = self.line

                # Сброс флага в начале кадра
                with self.lock:
                    self.object_on_line = False

                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    if label not in TARGET_CLASSES:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Показываем только объекты, которые пересекают линию
                    if line_intersects_box(l1_p1, l1_p2, (x1, y1, x2, y2)):
                        with self.lock:
                            self.object_on_line = True
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(annotated, label, (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        logger.debug(f"Объект {label} обнаружен на линии")

                # Нарисовать линию интереса
                cv2.line(annotated, l1_p1, l1_p2, (0, 255, 255), 2)

                resized = cv2.resize(annotated, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
                cv2.imshow("Tracking", resized)

                # Логирование статистики каждые STATUS_UPDATE_INTERVAL кадров
                if frame_count % STATUS_UPDATE_INTERVAL == 0:
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                    logger.info(f"Кадр {frame_count}, FPS: {fps:.2f}")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Пользователь запросил завершение")
                    break

            except Exception as e:
                logger.error(f"Ошибка во время обработки кадра: {e}")
                continue

        self.is_running = False
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Трекинг завершен")

    def stop(self):
        """
        Останавливает трекинг
        """
        logger.info("Запрос на остановку трекинга")
        self.is_running = False 