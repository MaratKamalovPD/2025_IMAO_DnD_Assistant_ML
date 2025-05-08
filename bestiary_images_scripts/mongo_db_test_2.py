from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Подключаемся к MongoDB
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = "localhost"
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = "bestiary_db"

mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
collection = db["creatures"]

# Проверяем, сколько документов в коллекции
count = collection.count_documents({})
print(f"Всего документов в коллекции: {count}")

# Выводим 5 первых документов
for creature in collection.find().limit(5):
    print(creature)
