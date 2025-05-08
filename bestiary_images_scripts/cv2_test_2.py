import cv2
import numpy as np
from PIL import Image

img1_path = "test_folder/amphisbaena.webp"
img2_path = "test_folder/Amphisbaena.webp"

# Загружаем изображения
img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)  # Вставка
img2= cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)  # Исходное
img2_alpha = cv2.imread(img2_path, cv2.IMREAD_UNCHANGED)  # Исходное

# Проверяем, есть ли альфа-канал
has_alpha = img2_alpha.shape[2] == 4 if len(img2_alpha.shape) == 3 else False
print(f"Альфа-канал {'есть' if has_alpha else 'отсутствует'}")

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
        scale_factor = 0.7  # Например, 70% от исходного размера
        
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

        for i in range(len(dst)):
            for j in range(len(dst[i])):
                for k in range(len(dst[i][j])):
                    if dst[i][j][k] < 0:
                        dst[i][j][k] = 0

        print(dst)

        # Получаем координаты выделенной области
        x_min, y_min = np.int32(dst.min(axis=0).ravel())
        x_max, y_max = np.int32(dst.max(axis=0).ravel())
        
        # Обрезаем изображение
        cropped = img2_alpha[y_min:y_max, x_min:x_max]

        print(f"Размер cropped: {cropped.shape if cropped is not None else 'None'}")

        # Изменяем размер до 300x400 с качественным алгоритмом Lanczos4
        resized = cv2.resize(cropped, (300, 400), interpolation=cv2.INTER_LANCZOS4)
        
        # Сохраняем изображение
        #cv2.imwrite("test_folder/extracted_fragment.webp", resized, [cv2.IMWRITE_WEBP_QUALITY, 100])

        if has_alpha:
            resized_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA))
        else:
            resized_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

        save_path = "test_folder/extracted_fragment.webp"
        resized_pil.save(save_path, "WEBP", quality=95, lossless=True)
        
        print("Фрагмент успешно сохранен как test_folder/extracted_fragment.webp")
    else:
        print("Гомография не найдена.")
else:
    print("Недостаточно совпадений для определения местоположения.")
