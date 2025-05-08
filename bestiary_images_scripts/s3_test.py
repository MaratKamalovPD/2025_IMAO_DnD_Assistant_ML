import os
import json
import requests
import boto3
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Настройки API
API_URL = "https://ttg.club/api/v1/bestiary/copper_stormforge"

# Настройки MinIO
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://95.31.164.69:9100")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = "creature-images"
S3_FOLDER = "sources"

# Подключение к MinIO (S3)
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def fetch_creature_data():
    """ Получаем JSON с API """
    response = requests.post(API_URL)
    response.raise_for_status()  # Ошибка, если запрос не удался
    return response.json()

def upload_to_s3(image_url, s3_filename):
    """ Загружаем изображение в MinIO (S3) """
    img_data = requests.get(image_url).content
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=f"{S3_FOLDER}/{s3_filename}",
        Body=img_data,
        ContentType="image/webp",
    )
    return f"{S3_ENDPOINT}/{S3_BUCKET}/{S3_FOLDER}/{s3_filename}"

def process_and_save_data():
    """ Основной процесс парсинга, загрузки в S3 и сохранения JSON """
    creature = fetch_creature_data()
    
    # Берем второе изображение
    if "images" in creature and len(creature["images"]) >= 2:
        original_image_url = creature["images"][1]
        s3_filename = original_image_url.split("/")[-1]  # Имя файла
        new_image_url = upload_to_s3(original_image_url, s3_filename)
    else:
        print("Ошибка: нет второго изображения.")
        return
    
    # Модифицируем JSON (оставляем только новое изображение)
    creature["images"] = [new_image_url]

    # Сохраняем новый JSON
    with open(f"{s3_filename}.json", "w", encoding="utf-8") as f:
        json.dump(creature, f, ensure_ascii=False, indent=4)

    print(f"Обработано и сохранено: {s3_filename}.json")

if __name__ == "__main__":
    process_and_save_data()
