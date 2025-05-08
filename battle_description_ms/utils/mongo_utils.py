import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

def get_character_by_id(character_id):
    character = mongo_collection.find_one({"_id": ObjectId(character_id)})
    if character:
        character.pop("_id")
    return character

def get_character_url_by_id(character_id):
    character = mongo_collection.find_one({"_id": ObjectId(character_id)})
    if character and "url" in character:
        url = character["url"]
        return url.split("/")[-1]  # Обрезаем строку до последнего элемента после "/"
    return None

def get_character_ids_in_batches(batch_size=80):
    """
    Извлекает все _id из коллекции, формирует батчи и записывает в JSON.

    Args:
        batch_size (int): Размер батча.
    """
    all_ids = []
    for character in mongo_collection.find({}, {"_id": 1}):
        all_ids.append(str(character["_id"]))

    batches = [all_ids[i:i + batch_size] for i in range(0, len(all_ids), batch_size)]

    with open("character_ids_batches.json", "w") as f:
        json.dump(batches, f, indent=4)

    return batches