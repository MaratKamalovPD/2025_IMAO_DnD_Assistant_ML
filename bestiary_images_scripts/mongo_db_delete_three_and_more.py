from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Настройки MongoDB
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = "localhost"
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = "bestiary_db"

# Подключение к MongoDB
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

def init_mongo():
    """Создаёт новое подключение к MongoDB в каждом процессе"""
    client = MongoClient(mongo_uri)
    db = client[MONGO_DB]
    return db["creatures"]  # Возвращаем объект коллекции

def truncate_images(collection):
    """Оставляет только первые два элемента в массиве images для каждого документа"""
    # Находим все документы, где поле images существует и является массивом
    documents = collection.find({"images": {"$exists": True, "$type": "array"}})
    
    for doc in documents:
        images = doc.get("images", [])
        if len(images) > 2:
            # Оставляем только первые два элемента
            new_images = images[:2]
            # Обновляем документ в коллекции
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"images": new_images}}
            )
            print(f"Обновлён документ с _id: {doc['_id']}, оставлено {len(new_images)} изображений.")
        else:
            print(f"Документ с _id: {doc['_id']} уже содержит 2 или меньше изображений.")

if __name__ == "__main__":
    collection = init_mongo()
    truncate_images(collection)