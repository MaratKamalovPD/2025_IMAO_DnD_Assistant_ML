from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Параметры подключения к MongoDB
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = "localhost"
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = "bestiary_db"

# URI подключения
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
collection = db["creatures"]

# Получаем первые N документа из коллекции
documents = collection.find().limit(1887)

updated_count = 0

for doc in documents:
    images = doc.get("images", [])
    
    if len(images) == 2 and "tokens" in images[0]:
        # Строим третий URL
        processed_url = images[0].replace("/tokens/", "/processed/")
        images.append(processed_url)

        # Обновляем документ
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"images": images}}
        )
        updated_count += 1

print(f"Обновлено документов: {updated_count}")
