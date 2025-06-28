"""
Модуль для геометрических вычислений
"""


def line_intersects_box(p1, p2, box):
    """
    Проверяет, пересекает ли линия (p1-p2) прямоугольник box=(x1,y1,x2,y2)
    
    Args:
        p1: первая точка линии (x, y)
        p2: вторая точка линии (x, y)
        box: прямоугольник (x1, y1, x2, y2)
    
    Returns:
        bool: True если линия пересекает прямоугольник
    """
    x1, y1, x2, y2 = box

    # Функция проверки пересечения отрезков
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def intersect(A, B, C, D):
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    rect_points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

    # Проверяем линию с каждой стороной прямоугольника
    for i in range(4):
        A = rect_points[i]
        B = rect_points[(i + 1) % 4]
        if intersect(p1, p2, A, B):
            return True

    # Также проверим, если линия целиком внутри коробки (оба конца внутри)
    if (x1 <= p1[0] <= x2 and y1 <= p1[1] <= y2) or (x1 <= p2[0] <= x2 and y1 <= p2[1] <= y2):
        return True

    return False 