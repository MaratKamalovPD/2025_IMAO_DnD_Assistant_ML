import grpc
from concurrent import futures
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import sys
import json
import requests
import itertools
import re

sys.path.append(os.path.join(os.path.dirname(__file__), "protobuf"))

import battle_description_pb2
import battle_description_pb2_grpc

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

with open("battle_description/secrets.json", "r") as f:
    secrets = json.load(f)

api_keys_with_proxies = secrets["api_keys_with_proxies"]
api_keys_cycle = itertools.cycle(api_keys_with_proxies)

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

llm_models = ["google/gemini-2.0-flash-exp:free", "google/gemini-2.0-flash-lite-preview-02-05:free"]

def get_character_by_id(character_id):
    character = mongo_collection.find_one({"_id": ObjectId(character_id)})
    if character:
        character.pop("_id")
    return character

def get_default_battle_description():
    return """
    Заглушка
    """

def create_dnd_battle_prompt(json1, json2):
    prompt = f"""
    Придумай мне описание для сражения в DnD.
    Я пришлю тебе описание 2 персонажей:
    1) {json1}
    2) {json2}
    Опиши:
    - Как первый персонаж атакует второго, попадает по нему. Расскажи про сам удар и его эффект.
    - Как первый персонаж добивает второго, когда его ХП падают до нуля.
    Оформи результат в виде текста с абзацами.
    В выводе должно быть ТОЛЬКО описание без всяких вводных слов.
    """
    return prompt.strip()

def get_dnd_battle_description(json1, json2):
    prompt = create_dnd_battle_prompt(json1, json2)

    for model in llm_models:
        try:
            current_api = next(api_keys_cycle)
            proxy = current_api["proxy"]
            proxy_ip = re.search(r"@(.+):", proxy).group(1) if proxy else "No proxy"
            print(f"Используется прокси: {proxy_ip}")

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {current_api['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
                },
                proxies={"http": proxy, "https": proxy},
            )

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к модели {model}: {e}")
            continue

    return get_default_battle_description()

class DescriptionService(battle_description_pb2_grpc.DescriptionServiceServicer):
    def GenerateDescription(self, request, context):
        print("aboba")
        first_char_id = request.first_char_id
        second_char_id = request.second_char_id

        first_character = get_character_by_id(first_char_id)
        second_character = get_character_by_id(second_char_id)

        if not first_character or not second_character:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Один или оба персонажа не найдены")
            return battle_description_pb2.DescriptionResponse()

        battle_description = get_dnd_battle_description(first_character, second_character)
        return battle_description_pb2.DescriptionResponse(battle_description=battle_description)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    battle_description_pb2_grpc.add_DescriptionServiceServicer_to_server(DescriptionService(), server)
    server.add_insecure_port("[::]:50051")
    print("Сервер запущен на порту 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()