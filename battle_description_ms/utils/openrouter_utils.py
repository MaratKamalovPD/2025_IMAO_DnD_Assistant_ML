import requests
import itertools
import re
from config import api_keys_with_proxies, llm_models

api_keys_cycle = itertools.cycle(api_keys_with_proxies)

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