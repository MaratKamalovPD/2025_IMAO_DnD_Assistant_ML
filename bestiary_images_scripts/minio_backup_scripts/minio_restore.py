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
S3_BUCKETS = os.getenv("S3_BUCKETS", "").split(",")

# Создаём подключение к MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def restore_bucket(bucket_name: str):
    source_dir = os.path.join(BACKUP_DIR, bucket_name)
    if not os.path.exists(source_dir):
        print(f"⚠️  Папка {source_dir} не найдена, пропускаем {bucket_name}.")
        return

    print(f"🔁 Восстанавливаем бакет: {bucket_name}")
    for root, _, files in os.walk(source_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_path, source_dir).replace("\\", "/")
            print(f" -> Загружаем: {s3_key}")
            s3_client.upload_file(local_path, bucket_name, s3_key)

def main():
    if not S3_BUCKETS or S3_BUCKETS == [""]:
        print("❌ Не указан ни один бакет в переменной S3_BUCKETS")
        return

    for bucket in S3_BUCKETS:
        restore_bucket(bucket.strip())

    print("✅ Восстановление завершено.")

if __name__ == "__main__":
    main()
