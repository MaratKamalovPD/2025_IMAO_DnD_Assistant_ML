import cv2
import numpy as np

img1_path = "test_folder/amphisbaena.webp"
img2_path = "test_folder/Amphisbaena.webp"

# Загружаем изображения
img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)  # Вставка
img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)  # Исходное

# Создаем детектор SIFT
sift = cv2.SIFT_create()

# Находим ключевые точки и дескрипторы
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# BFMatcher с KNN
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# Фильтрация по Лоу (лучшие совпадения)
good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

print(f"Найдено {len(good_matches)} хороших совпадений")

if len(good_matches) > 10:  # Достаточно совпадений для гомографии
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Вычисляем матрицу преобразования
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if M is not None:
        h, w = img1.shape
        
        # Соотношение сторон 4:3
        aspect_ratio = 3 / 4
        
        # Коэффициент масштабирования (уменьшаем область выделения)
        scale_factor = 0.70  # Например, 70% от исходного размера
        
        # Вычисляем размеры прямоугольника
        rect_width = int(w * scale_factor)
        rect_height = int(rect_width / aspect_ratio)
        
        # Центрируем прямоугольник на изображении
        x_start = (w - rect_width) // 2
        y_start = (h - rect_height) // 2
        
        # Координаты прямоугольника
        pts = np.float32([
            [x_start, y_start],
            [x_start + rect_width, y_start],
            [x_start + rect_width, y_start + rect_height],
            [x_start, y_start + rect_height]
        ]).reshape(-1, 1, 2)
        
        # Применяем перспективное преобразование
        dst = cv2.perspectiveTransform(pts, M)

        # Рисуем найденную область на изображении
        img2_color = cv2.imread(img2_path)  # Загружаем цветное изображение
        img2_color = cv2.polylines(img2_color, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)

        cv2.imshow("Result", img2_color)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Гомография не найдена.")
else:
    print("Недостаточно совпадений для определения местоположения.")