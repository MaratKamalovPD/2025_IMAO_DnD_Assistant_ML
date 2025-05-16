import os
import json
from PIL import Image
from io import BytesIO
import boto3
from dotenv import load_dotenv

# Загрузка переменных
load_dotenv()

# Пути и параметры
INPUT_FOLDER = "images/input_png_images"
STATUS_FILE = os.path.join(INPUT_FOLDER, "status.json")
OUTPUT_SIZE = (300, 400)
QUALITY = 90
FORCE = False  # Изменить на True для принудительной обработки всех

# MinIO/S3
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = "creature-images"
S3_FOLDER = "processed"

# Клиент S3
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

def resize_and_crop(image, target_size):
    img_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]

    if img_ratio < target_ratio:
        new_height = int(image.width / target_ratio)
        offset = (image.height - new_height) // 2
        image = image.crop((0, offset, image.width, offset + new_height))
    elif img_ratio > target_ratio:
        new_width = int(image.height * target_ratio)
        offset = (image.width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, image.height))

    return image.resize(target_size, Image.LANCZOS)

def process_and_upload_images(input_folder, bucket_name, s3_folder, output_size, quality, force=False):
    status = load_status()
    changed = False

    for file in os.listdir(input_folder):
        if not file.lower().endswith('.png'):
            continue

        if file in status and not force:
            prev = status[file]
            if prev.get("processed") and prev.get("size") == f"{output_size[0]}x{output_size[1]}" and prev.get("quality") == quality:
                print(f"[⏩] Пропущено: {file} — уже обработан")
                continue

        input_path = os.path.join(input_folder, file)
        output_filename = os.path.splitext(file)[0] + ".webp"
        s3_key = f"{s3_folder}/{output_filename}"

        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img = resize_and_crop(img, output_size)

            buffer = BytesIO()
            img.save(buffer, "WEBP", quality=quality, method=6)
            buffer.seek(0)

            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=buffer,
                ContentType="image/webp"
            )

            print(f"[☁] Загружено: {file} → s3://{bucket_name}/{s3_key}")
            status[file] = {
                "processed": True,
                "size": f"{output_size[0]}x{output_size[1]}",
                "quality": quality
            }
            changed = True

    if changed:
        save_status(status)
        print("✅ Файл статуса обновлён.")

if __name__ == "__main__":
    if os.path.isdir(INPUT_FOLDER):
        process_and_upload_images(INPUT_FOLDER, S3_BUCKET, S3_FOLDER, OUTPUT_SIZE, QUALITY, force=FORCE)
    else:
        print(f"❌ Папка '{INPUT_FOLDER}' не найдена.")
