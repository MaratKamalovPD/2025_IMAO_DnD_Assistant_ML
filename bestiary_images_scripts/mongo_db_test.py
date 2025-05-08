import os
from pymongo import MongoClient
import json
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = "localhost"
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = "bestiary_db"

mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

client = MongoClient(mongo_uri)
db = client[MONGO_DB]
collection = db["creatures"]

def insert_data_from_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

    print(f"Загружено {len(data)} записей в MongoDB")

def find_creature_by_name(name):
    result = collection.find_one({"name.rus": name})
    return result

if __name__ == "__main__":
    #insert_data_from_json("bestiary_data.json")
    
    creature = find_creature_by_name("Рой многоножек")
    if creature:
        print("Найдено:", creature)
    else:
        print("Существо не найдено")
