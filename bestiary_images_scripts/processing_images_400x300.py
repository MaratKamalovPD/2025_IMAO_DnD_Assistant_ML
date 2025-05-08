import cv2
import numpy as np
import boto3
import os
from io import BytesIO
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image

# Загружаем переменные из .env
load_dotenv()

# Настройки MongoDB
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = "localhost"
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = "bestiary_db"

# Настройки MinIO (S3)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://95.31.164.69:9100")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = "creature-images"
S3_FOLDER_PROCESSED = "processed"

# Подключение к MongoDB
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

def init_mongo():
    """Создаёт новое подключение к MongoDB в каждом процессе"""
    client = MongoClient(mongo_uri)
    db = client[MONGO_DB]
    return db["creatures"]  # Возвращаем объект коллекции

# Подключение к MinIO (S3)
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def process_and_save_s3(bucket_name, image1, image2, output_dir, scale_factor=0.95, output_size=(300, 400)):

    img1_key = image1.split("/", 4)[-1]
    img2_key = image2.split("/", 4)[-1]

    # Загрузка изображений из S3
    img1_obj = s3_client.get_object(Bucket=bucket_name, Key=img1_key)
    img2_obj = s3_client.get_object(Bucket=bucket_name, Key=img2_key)
    
    img1_data = img1_obj['Body'].read()
    img2_data = img2_obj['Body'].read()

    img1 = cv2.imdecode(np.frombuffer(img1_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imdecode(np.frombuffer(img2_data , np.uint8), cv2.IMREAD_GRAYSCALE)
    try:
        # Декодируем изображение с альфа-каналом
        img2_alpha = cv2.imdecode(np.frombuffer(img2_data, np.uint8), cv2.IMREAD_UNCHANGED)
        
        # Проверяем, есть ли альфа-канал
        if img2_alpha is not None:
            has_alpha = img2_alpha.shape[2] == 4 if len(img2_alpha.shape) == 3 else False
        else:
            # Если img2_alpha равен None, записываем ошибку в файл
            has_alpha = False
            with open("error_log.txt", "a") as file:
                file.write("Ошибка: не удалось декодировать img2_data для img2_alpha\n")
                file.write(f"img1_key = {img1_key}\n")
                file.write(f"img2_key = {img2_key}\n")
                file.write("-" * 40 + "\n")
    except Exception as e:
        # Ловим любые другие исключения и записываем их в файл
        with open("error_log.txt", "a") as file:
            file.write(f"Ошибка при обработке img2_alpha: {e}\n")
            file.write(f"img1_key = {img1_key}\n")
            file.write(f"img2_key = {img2_key}\n")
            file.write("-" * 40 + "\n")
        has_alpha = False

    # Создаем детектор SIFT
    sift = cv2.SIFT_create()
    
    try:
        # Находим ключевые точки и дескрипторы
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)
    except cv2.error as e:
        # В случае ошибки записываем информацию в файл и возвращаем None
        with open("error_log.txt", "a") as file:  # Открываем файл в режиме добавления ('a')
            file.write(f"Ошибка при обработке изображений: {e}\n")
            file.write(f"img1_key = {img1_key}\n")
            file.write(f"img2_key = {img2_key}\n")
            file.write("-" * 40 + "\n")  # Добавляем разделитель для удобства чтения
        return None
    
    # BFMatcher с KNN
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    # Фильтрация по Лоу (лучшие совпадения)
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
    
    print(f"Найдено {len(good_matches)} хороших совпадений")
    
    if len(good_matches) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Вычисляем матрицу преобразования
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if M is not None:
            h, w = img1.shape
            aspect_ratio = 3 / 4
            
            while True:
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

                # Получаем координаты выделенной области
                x_min, y_min = np.int32(dst.min(axis=0).ravel())
                x_max, y_max = np.int32(dst.max(axis=0).ravel())

                # Обрезаем изображение
                cropped = img2_alpha[y_min:y_max, x_min:x_max]

                # Проверяем, что обрезанное изображение корректное
                if cropped.shape[0] > 100 and cropped.shape[1] > 100:
                    break  # Если всё ок — выходим из цикла

                # Уменьшаем aspect_ratio на 0.01 и повторяем
                scale_factor -= 0.01

                print(f"reducing scale_factor, now it's {scale_factor}")

                # Безопасность: не даём aspect_ratio уйти в ноль или отрицательные значения
                if scale_factor <= 0.1:
                    print("Ошибка: scale_factor уменьшился слишком сильно, но cropped остаётся пустым.")
                    return None

            print(f"Размер cropped: {cropped.shape if cropped is not None else 'None'}")

            # Изменяем размер до 300x400 с качественным алгоритмом Lanczos4
            resized = cv2.resize(cropped, output_size, interpolation=cv2.INTER_LANCZOS4)

            if has_alpha:
                resized_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA))
            else:
                resized_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
            
            # Определяем имя выходного файла
            output_filename = os.path.join(output_dir, os.path.basename(img1_key).lower())
            
            # Сохраняем в BytesIO
            buffer = BytesIO()
            resized_pil.save(buffer, format="WEBP", quality=95, lossless=True)
            buffer.seek(0)
            
            # Загружаем обработанное изображение в S3
            s3_client.put_object(
                Bucket=bucket_name, 
                Key=output_filename, 
                Body=buffer, 
                ContentType='image/webp')
            
            print(f"Фрагмент успешно сохранен в S3: {output_filename}")
            return f"{bucket_name}/{output_filename}"
        else:
            print("Гомография не найдена.")
    else:
        print("Недостаточно совпадений для определения местоположения.")
    return None

def update_mongo_with_processed_images():
    collection = init_mongo()

    print("mongo init")
    
    for document in collection.find():
        images = document.get("images", [])

        

        if len(images) >= 2:
            image1 = images[0]
            image2 = images[1]
            
            processed_image_key = process_and_save_s3(S3_BUCKET, image1, image2, S3_FOLDER_PROCESSED)

            if processed_image_key:
                processed_image_url = f"{S3_ENDPOINT}/{processed_image_key}"
                collection.update_one({"_id": document["_id"]}, {"$push": {"images": processed_image_url}})
                print(f"Документ {document['_id']} обновлён: {processed_image_url}")

        print("iteration ends")  

    print("aboba")


if __name__ == "__main__":
    update_mongo_with_processed_images()              
