import cv2
from ultralytics import YOLO

DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 540
TARGET_CLASSES = ['car', 'motorcycle', 'truck']

def line_intersects_box(p1, p2, box):
    x1, y1, x2, y2 = box
    rect_lines = [
        ((x1, y1), (x2, y1)),  # top
        ((x2, y1), (x2, y2)),  # right
        ((x2, y2), (x1, y2)),  # bottom
        ((x1, y2), (x1, y1))   # left
    ]
    for r1, r2 in rect_lines:
        if check_line_intersection(p1, p2, r1, r2):
            return True
    return False

def check_line_intersection(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

def get_line_points(cap):
    points = []
    SCALE_W, SCALE_H = DISPLAY_WIDTH, DISPLAY_HEIGHT

    ret, first_frame = cap.read()
    if not ret:
        print("[ERROR] Не удалось получить первый кадр.")
        return None

    orig_height, orig_width = first_frame.shape[:2]
    display_frame = cv2.resize(first_frame, (SCALE_W, SCALE_H))

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
            real_x = int(x * orig_width / SCALE_W)
            real_y = int(y * orig_height / SCALE_H)
            points.append((real_x, real_y))

    cv2.namedWindow("Setup", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Setup", mouse_callback)

    while len(points) < 2:
        temp = display_frame.copy()
        for pt in points:
            draw_x = int(pt[0] * SCALE_W / orig_width)
            draw_y = int(pt[1] * SCALE_H / orig_height)
            cv2.circle(temp, (draw_x, draw_y), 5, (0, 0, 255), -1)
        if len(points) == 2:
            pt1 = (int(points[0][0] * SCALE_W / orig_width), int(points[0][1] * SCALE_H / orig_height))
            pt2 = (int(points[1][0] * SCALE_W / orig_width), int(points[1][1] * SCALE_H / orig_height))
            cv2.line(temp, pt1, pt2, (0, 255, 255), 2)

        cv2.imshow("Setup", temp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyWindow("Setup")
    if len(points) < 2:
        return None

    return points[0], points[1]

def main(video_path):
    model = YOLO("yolov8s.pt")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[ERROR] Не удалось открыть видео: {video_path}")
        return

    print("[INFO] Задайте линию интереса (2 клика мышью).")
    line = get_line_points(cap)
    if line is None:
        return

    print("[INFO] Обработка началась. Нажмите 'q' для выхода.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] Видео окончено.")
            break

        results = model.track(frame, persist=False, conf=0.3, iou=0.5, verbose=False)[0]
        annotated = frame.copy()
        l1_p1, l1_p2 = line

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            if label not in TARGET_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if line_intersects_box(l1_p1, l1_p2, (x1, y1, x2, y2)):
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Нарисовать линию интереса
        cv2.line(annotated, l1_p1, l1_p2, (0, 255, 255), 2)

        resized = cv2.resize(annotated, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        cv2.imshow("Трекинг", resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Завершение.")
            break

    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    video_path = r"D:\Python_projects\TestCV\cvtest.avi"
    main(video_path)
