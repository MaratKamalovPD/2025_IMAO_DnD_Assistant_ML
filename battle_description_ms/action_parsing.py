import requests
import itertools
import re
import time
from config import api_keys_with_proxies, llm_models
from utils import mongo_utils
from prompts import attack_parsing
import json
from bson.objectid import ObjectId

api_keys_cycle = itertools.cycle(api_keys_with_proxies)
MAX_RETRIES = 5  # Максимальное количество попыток для одного запроса
RETRY_DELAY = 5  # Задержка между попытками в секундах

def get_parsed_action_json(prompt, retry_count=0):
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
            #print(f"Response status: {response.status_code}")
            #print(f"Response content: {response.text}")
            
            response.raise_for_status()
            
            response_data = response.json()
            
            # Проверяем наличие ошибки локации
            if "error" in response_data:
                error_msg = response_data["error"].get("message", "")
                metadata = response_data["error"].get("metadata", {})
                provider_error = metadata.get("raw", "{}")
                
                try:
                    provider_error = json.loads(provider_error)
                    if provider_error.get("error", {}).get("message", "") == "User location is not supported for the API use.":
                        if retry_count < MAX_RETRIES:
                            print(f"Ошибка локации, пробуем снова (попытка {retry_count + 1}/{MAX_RETRIES})...")
                            time.sleep(RETRY_DELAY)
                            return get_parsed_action_json(prompt, retry_count + 1)
                        else:
                            print("Достигнуто максимальное количество попыток для этой модели.")
                            continue
                except json.JSONDecodeError:
                    pass
                
                print(f"Ошибка от API: {error_msg}")
                continue
            
            # Проверяем наличие ожидаемых ключей в ответе
            if "choices" not in response_data or not response_data["choices"]:
                print(f"Unexpected response structure from model {model}. Response: {response_data}")
                continue
                
            if "message" not in response_data["choices"][0] or "content" not in response_data["choices"][0]["message"]:
                print(f"Missing message or content in response from model {model}. Response: {response_data}")
                continue
                
            return response_data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к модели {model}: {e}")
            if retry_count < MAX_RETRIES and isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                print(f"Пробуем снова (попытка {retry_count + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                return get_parsed_action_json(prompt, retry_count + 1)
            continue
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON от модели {model}: {e}")
            continue
        except Exception as e:
            print(f"Неожиданная ошибка при обработке ответа от модели {model}: {e}")
            continue

    return None

def process_character(character_id, index):
    """
    Обрабатывает одного персонажа, извлекая данные и вызывая функцию.
    """
    first_character = mongo_utils.get_character_by_id(character_id)
    character_name = mongo_utils.get_character_url_by_id(character_id)
    if first_character:
        actions = first_character.get('actions', [])
        
        # Если actions пустой, сразу записываем [] в базу и пропускаем запрос к API
        if not actions:
            try:
                result = mongo_utils.mongo_collection.update_one(
                    {"_id": ObjectId(character_id)},
                    {"$set": {"llm_parsed_attack": []}}
                )
                if result.modified_count > 0:
                    print(f"Character {character_id}:{character_name} (index {index}): empty actions, set empty array in DB")
                else:
                    print(f"Character {character_id}:{character_name} (index {index}): no changes needed for empty actions")
                return
            except Exception as e:
                print(f"Error updating empty actions for character {character_id}: {e}")
                return
        
        prompt = attack_parsing.parse_action_json_prompt(actions)
        recieved_json_str = get_parsed_action_json(prompt)
        
        if not recieved_json_str:  # Проверка на пустой результат
            with open("empty_results.txt", "a") as f:
                f.write(f"{character_id}\n")
            print(f"Character {character_id} (index {index}): empty result, ID written to file.")
            return
            
        try:
            # Извлекаем JSON из строки
            recieved_json_str = recieved_json_str.replace("`json", "").replace("`", "").replace("\n", "").strip()
            recieved_json = json.loads(recieved_json_str)
        except json.JSONDecodeError as e:
            print(f"Character {character_id} (index {index}): failed to parse JSON: {e}")
            with open("json_parse_errors.txt", "a") as f:
                f.write(f"{character_id} - {str(e)}\n")
            return

        if not recieved_json:  # Проверка на пустой результат
            with open("empty_results.txt", "a") as f:
                f.write(f"{character_id}\n")
            print(f"Character {character_id} (index {index}): empty result, ID written to file.")
            return

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

def process_batch(batch):
    """
    Обрабатывает один батч персонажей.
    """
    for index, char_id in enumerate(batch):
        process_character(char_id, index)

def process_single_batch_from_json(json_file, batch_index):
    """
    Извлекает указанный батч из JSON и обрабатывает его.
    """
    with open(json_file, 'r') as f:
        batches = json.load(f)

    print("batches count = ", len(batches))   

    if batch_index < 0 or batch_index >= len(batches):
        print(f"Invalid batch index: {batch_index}")
        return

    selected_batch = batches[batch_index]
    process_batch(selected_batch)

if __name__ == "__main__":
    process_single_batch_from_json('character_ids_batches.json', 23)
    process_single_batch_from_json('character_ids_batches.json', 24)