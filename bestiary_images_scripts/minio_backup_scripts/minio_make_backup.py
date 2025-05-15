import os
import boto3
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Настройки MinIO
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
BACKUP_DIR = os.getenv("S3_BACKUP_DIR", "./s3_backup")

# Список бакетов через запятую: creature-images,another-bucket,...
S3_BUCKETS = os.getenv("S3_BUCKETS", "").split(",")

# Создаём подключение к MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def backup_bucket(bucket_name: str):
    print(f"Начинаем backup бакета: {bucket_name}")
    target_dir = os.path.join(BACKUP_DIR, bucket_name)
    os.makedirs(target_dir, exist_ok=True)

    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            local_path = os.path.join(target_dir, key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            print(f" -> Скачиваем: {key}")
            s3_client.download_file(bucket_name, key, local_path)

def main():
    if not S3_BUCKETS or S3_BUCKETS == [""]:
        print("❌ Не указан ни один бакет в переменной S3_BUCKETS")
        return
    
    for bucket in S3_BUCKETS:
        backup_bucket(bucket.strip())

    print("✅ Backup завершён.")

if __name__ == "__main__":
    main()
