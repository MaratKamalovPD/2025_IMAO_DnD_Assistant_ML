import requests
import itertools
import re
from config import api_keys_with_proxies, llm_models
from utils import mongo_utils
from prompts import attack_parsing
import json
import asyncio
from bson.objectid import ObjectId

api_keys_cycle = itertools.cycle(api_keys_with_proxies)

async def get_parsed_action_json(prompt):
   
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
            print(response)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к модели {model}: {e}")
            continue

    return None

async def process_character(character_id, index):
    """
    Обрабатывает одного персонажа, извлекая данные и вызывая асинхронную функцию.
    """
    first_character = mongo_utils.get_character_by_id(character_id)
    character_name = mongo_utils.get_character_url_by_id(character_id)
    if first_character:
        actions = first_character.get('actions', [])
        prompt = attack_parsing.parse_action_json_prompt(actions)
        recieved_json_str = await get_parsed_action_json(prompt)
        # Извлекаем JSON из строки
        recieved_json_str = recieved_json_str.replace("`json", "").replace("`", "").replace("\n", "").strip()
        recieved_json = json.loads(recieved_json_str)

        if not recieved_json:  # Проверка на пустой результат
            with open("empty_results.txt", "a") as f:
                f.write(f"{character_id}\n")
            print(f"Character {character_id} (index {index}): empty result, ID written to file.")
            return  # Выход из функции

        # Запись в MongoDB
        try:
            result = mongo_utils.mongo_collection.update_one(
                {"_id": ObjectId(character_id)},
                {"$set": {"llm_parsed_attack": recieved_json}}
            )

            if result.modified_count > 0:
                print(f"Character {character_id}:{character_name} (index {index}): updated with llm_parsed_attack")
            else:
                with open("update_errors.txt", "a") as f:
                    f.write(f"{character_id}:{character_name}\n")
                print(f"Character {character_id} (index {index}): update failed or no changes needed, ID written to file.")
        except Exception as e:
            with open("update_errors.txt", "a") as f:
                f.write(f"{character_id} - {str(e)}\n")
            print(f"Character {character_id} (index {index}): update error: {e}, ID written to file.")

    else:
        print(f"Character {character_id} (index {index}) not found.")

async def process_batch(batch):
    """
    Обрабатывает один батч персонажей асинхронно.
    """
    tasks = [process_character(char_id, index) for index, char_id in enumerate(batch)]
    await asyncio.gather(*tasks)

def process_single_batch_from_json(json_file, batch_index):
    """
    Извлекает указанный батч из JSON и обрабатывает его асинхронно в 2 потока.
    """
    with open(json_file, 'r') as f:
        batches = json.load(f)

    print("batches count = ", len(batches))   

    if batch_index < 0 or batch_index >= len(batches):
        print(f"Invalid batch index: {batch_index}")
        return

    selected_batch = batches[batch_index]

    async def main():
        await process_batch(selected_batch)

    asyncio.run(main())

# Пример использования
if __name__ == "__main__":
    process_single_batch_from_json('character_ids_batches.json', 0) # Обработка батча с индексом 1