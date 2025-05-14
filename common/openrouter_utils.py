import requests
import itertools
import re
import json
import time
from config import api_keys_with_proxies, llm_models


class DnDBattleGenerator:
    MAX_RETRIES = 5
    RETRY_DELAY = 5  # в секундах

    def __init__(self):
        self.api_keys_cycle = itertools.cycle(api_keys_with_proxies)
        self.models = llm_models

    def _get_default_battle_description(self):
        return """
        Заглушка
        """

    def _create_battle_prompt(self, json1, json2):
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

    def get_battle_description(self, json1, json2):
        prompt = self._create_battle_prompt(json1, json2)

        for model in self.models:
            try:
                current_api = next(self.api_keys_cycle)
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
                    proxies={"http": proxy, "https": proxy} if proxy else None,
                )

                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе к модели {model}: {e}")
                continue

        return self._get_default_battle_description()

    def get_parsed_action_json(self, prompt, retry_count=0):
        for model in self.models:
            try:
                current_api = next(self.api_keys_cycle)
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
                    proxies={"http": proxy, "https": proxy} if proxy else None,
                )

                response.raise_for_status()
                response_data = response.json()

                if "error" in response_data:
                    error_msg = response_data["error"].get("message", "")
                    metadata = response_data["error"].get("metadata", {})
                    provider_error = metadata.get("raw", "{}")

                    try:
                        provider_error = json.loads(provider_error)
                        if provider_error.get("error", {}).get("message", "") == "User location is not supported for the API use.":
                            if retry_count < self.MAX_RETRIES:
                                print(f"Ошибка локации, пробуем снова (попытка {retry_count + 1}/{self.MAX_RETRIES})...")
                                time.sleep(self.RETRY_DELAY)
                                return self.get_parsed_action_json(prompt, retry_count + 1)
                            else:
                                print("Достигнуто максимальное количество попыток для этой модели.")
                                continue
                    except json.JSONDecodeError:
                        pass

                    print(f"Ошибка от API: {error_msg}")
                    continue

                if "choices" not in response_data or not response_data["choices"]:
                    print(f"Unexpected response structure from model {model}. Response: {response_data}")
                    continue

                if "message" not in response_data["choices"][0] or "content" not in response_data["choices"][0]["message"]:
                    print(f"Missing message or content in response from model {model}. Response: {response_data}")
                    continue

                return response_data["choices"][0]["message"]["content"]

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе к модели {model}: {e}")
                if retry_count < self.MAX_RETRIES and isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                    print(f"Пробуем снова (попытка {retry_count + 1}/{self.MAX_RETRIES})...")
                    time.sleep(self.RETRY_DELAY)
                    return self.get_parsed_action_json(prompt, retry_count + 1)
                continue
            except json.JSONDecodeError as e:
                print(f"Ошибка декодирования JSON от модели {model}: {e}")
                continue
            except Exception as e:
                print(f"Неожиданная ошибка при обработке ответа от модели {model}: {e}")
                continue

        return None
