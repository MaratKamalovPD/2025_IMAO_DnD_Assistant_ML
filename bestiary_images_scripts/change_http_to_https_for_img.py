from pymongo import MongoClient
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

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

def update_image_urls(collection):
    """Заменяет старый URL на новый в поле images"""
    # Находим все документы, где поле images существует и является массивом
    documents = collection.find({"images": {"$exists": True, "$type": "array"}})
    
    old_domain = "http://95.31.164.69:9100"
    new_domain = "https://encounterium.ru"
    
    for doc in documents:
        images = doc.get("images", [])
        updated_images = []
        changed = False
        
        for img_url in images:
            if old_domain in img_url:
                # Заменяем старый домен на новый
                new_url = img_url.replace(old_domain, new_domain)
                updated_images.append(new_url)
                changed = True
            else:
                updated_images.append(img_url)
        
        if changed:
            # Обновляем документ в коллекции
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"images": updated_images}}
            )
            print(f"Обновлён документ с _id: {doc['_id']}")
            print(f"Старые URL: {images}")
            print(f"Новые URL: {updated_images}")
            print("---")

if __name__ == "__main__":
    collection = init_mongo()
    update_image_urls(collection)
    print("Все URL изображений успешно обновлены!")