import os
import boto3
from dotenv import load_dotenv

# 🔐 Загрузка переменных окружения
load_dotenv()

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

# 📁 Локальная папка с изображениями
LOCAL_FOLDER = "images/output_webp_maps"
S3_BUCKET = "map-images"
S3_PREFIX = "plug-maps"

def upload_images_to_s3():
    if not all([S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY]):
        print("❌ Не заданы все переменные окружения для подключения к S3.")
        return

    # Инициализация клиента S3
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )

    # Загрузка файлов в S3
    for filename in os.listdir(LOCAL_FOLDER):
        if filename.lower().endswith('.webp'):
            local_path = os.path.join(LOCAL_FOLDER, filename)
            s3_key = f"{S3_PREFIX}/{filename}"

            try:
                s3.upload_file(local_path, S3_BUCKET, s3_key, ExtraArgs={'ContentType': 'image/webp'})
                print(f"[✔] {filename} → s3://{S3_BUCKET}/{s3_key}")
            except Exception as e:
                print(f"[❌] Ошибка при загрузке {filename}: {e}")

if __name__ == "__main__":
    if os.path.isdir(LOCAL_FOLDER):
        upload_images_to_s3()
    else:
        print(f"❌ Папка '{LOCAL_FOLDER}' не найдена.")
