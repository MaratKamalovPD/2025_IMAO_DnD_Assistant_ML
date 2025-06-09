import os
import json
from PIL import Image
from io import BytesIO
import boto3
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Параметры
STATUS_FILE = "images/status_tokens.json"
QUALITY = 90
FORCE = False  # Принудительно обрабатывать все файлы
OUTPUT_SIZE = None  # Без изменения размера

# Настройки S3/MinIO
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
SOURCE_BUCKET = "cropped-imgs"
DEST_BUCKET = "creature-images"
DEST_FOLDER = "tokens"

# Инициализация клиента S3
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=4, ensure_ascii=False)

def list_all_objects(bucket):
    continuation_token = None
    while True:
        if continuation_token:
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                ContinuationToken=continuation_token
            )
        else:
            response = s3_client.list_objects_v2(Bucket=bucket)

        for obj in response.get("Contents", []):
            yield obj

        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break

def convert_and_upload_objects():
    status = load_status()
    changed = False

    for obj in list_all_objects(SOURCE_BUCKET):
        key = obj["Key"]
        if not key.lower().endswith(".png"):
            continue

        if key in status and not FORCE:
            prev = status[key]
            if prev.get("processed") and prev.get("quality") == QUALITY:
                print(f"[⏩] Пропущено: {key} — уже обработан")
                continue

        try:
            # Загрузка изображения
            png_obj = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=key)
            png_data = png_obj["Body"].read()
            img = Image.open(BytesIO(png_data)).convert("RGB")

            if OUTPUT_SIZE:
                img = img.resize(OUTPUT_SIZE, Image.LANCZOS)

            # Конвертация в WebP
            buffer = BytesIO()
            img.save(buffer, "WEBP", quality=QUALITY, method=6)
            buffer.seek(0)

            filename_wo_ext = os.path.splitext(os.path.basename(key))[0]
            dest_key = f"{DEST_FOLDER}/{filename_wo_ext}.webp"

            # Загрузка в целевой бакет
            s3_client.put_object(
                Bucket=DEST_BUCKET,
                Key=dest_key,
                Body=buffer,
                ContentType="image/webp"
            )

            print(f"[☁] Загружено: {key} → s3://{DEST_BUCKET}/{dest_key}")
            status[key] = {
                "processed": True,
                "quality": QUALITY
            }
            changed = True

        except Exception as e:
            print(f"[⚠️] Ошибка при обработке {key}: {e}")

    if changed:
        save_status(status)
        print("✅ Файл статуса обновлён.")

if __name__ == "__main__":
    convert_and_upload_objects()

