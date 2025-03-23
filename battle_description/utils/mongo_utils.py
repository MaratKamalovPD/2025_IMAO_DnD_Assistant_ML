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