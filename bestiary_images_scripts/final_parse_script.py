import os
import json
import requests
import boto3
from pymongo import MongoClient
from dotenv import load_dotenv
import multiprocessing
from tqdm import tqdm

# Загружаем переменные из .env
load_dotenv()

# Настройки API
BASE_URL = "https://ttg.club/api/v1"

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
S3_FOLDER_SOURCES = "sources"
S3_FOLDER_TOKENS = "tokens"

# Подключение к MongoDB
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
#client = MongoClient(mongo_uri)
#db = client[MONGO_DB]
#collection = db["creatures"]

def init_mongo():
    """Создаёт новое подключение к MongoDB в каждом процессе"""
    client = MongoClient(mongo_uri)
    db = client[MONGO_DB]

    return db["creatures"]  # Возвращаем объект БД

# Подключение к MinIO (S3)
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def fetch_creature_data(api_url):
    """ Делает POST-запрос и получает JSON с API """
    response = requests.post(api_url)
    response.raise_for_status()
    return response.json()

def upload_to_s3(image_url, s3_filename, folder_name):
    """ Загружает изображение в MinIO (S3) и возвращает новый URL """
    img_data = requests.get(image_url).content
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=f"{folder_name}/{s3_filename}",
        Body=img_data,
        ContentType="image/webp",
    )
    return f"{S3_ENDPOINT}/{S3_BUCKET}/{folder_name}/{s3_filename}"

def process_and_save_to_mongo(creature_base, collection):
    """ Обрабатывает существо, загружает изображение в S3, обновляет JSON и сохраняет в MongoDB """
    creature_url = creature_base["url"]
    api_url = f"{BASE_URL}{creature_url}"
    
    print(f"Обрабатываем: {api_url}")
    
    creature = fetch_creature_data(api_url)
    
    # Проверяем и заменяем изображение
    if "images" in creature and len(creature["images"]) >= 2:
        token_image_url = creature["images"][0]
        original_image_url = creature["images"][1]

        s3_filename_token = token_image_url.split("/")[-1]
        s3_filename_original = original_image_url.split("/")[-1]

        new_token_image_url = upload_to_s3(token_image_url, s3_filename_token, S3_FOLDER_TOKENS)
        new_original_image_url = upload_to_s3(original_image_url, s3_filename_original, S3_FOLDER_SOURCES)
        creature["images"] = [new_token_image_url, new_original_image_url]
    else:
        if "images" not in creature:
            print(f"Ошибка: нет раздела {creature['name']['rus']}")
        elif len(creature["images"]) < 2:    
            print(f"Ошибка: нет второго изображения для {creature['name']['rus']}")

        return
    
    # Сохраняем в MongoDB
    collection.insert_one(creature)
    print(f"Сохранено в MongoDB: {creature['name']['rus']}")

def worker(creature, queue):
    """Функция-обработчик для каждого существа"""
    db = init_mongo()  # Создаём новое подключение
    process_and_save_to_mongo(creature, db)  # Передаём объект БД
    queue.put(1)  # Уведомляем очередь о завершении задачи
    print(f"[PID {multiprocessing.current_process().pid}] Обработано: {creature['name']['rus']}")

def main():
    """Загружаем creatures из JSON и запускаем обработку в параллельных процессах"""
    with open("bestiary_data.json", "r", encoding="utf-8") as f:
        creatures_list = json.load(f)

    num_workers = min(8, multiprocessing.cpu_count())  # Ограничиваем до 8 процессов
    manager = multiprocessing.Manager()
    queue = manager.Queue()  # Очередь для отслеживания прогресса

    with multiprocessing.Pool(num_workers) as pool:
        # Запускаем worker'ы
        results = [pool.apply_async(worker, (creature, queue)) for creature in creatures_list]

        # Прогресс-бар
        with tqdm(total=len(creatures_list), desc="Обработка существ") as pbar:
            for _ in range(len(creatures_list)):
                queue.get()  # Ожидаем завершения одной задачи
                pbar.update(1)  # Обновляем прогресс-бар

        # Дожидаемся завершения всех процессов
        for r in results:
            r.wait()

if __name__ == "__main__":
    main()


# В КАКОЙ-ТО МОМЕНТ СКРИПТ ПЕРЕСТАЁТ ВЫПОЛНЯТЬСЯ + DEADLOCK НА МОНГЕ 