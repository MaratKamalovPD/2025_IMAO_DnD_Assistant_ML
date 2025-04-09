from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
import json
import os

# Загрузка переменных окружения
load_dotenv()

# Установка прокси-глобально для текущего процесса
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:10808'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:10808'

# Проверка прокси-соединения
import requests
try:
    test_response = requests.get("https://httpbin.org/ip")
    print("Прокси работает:", test_response.text)
except Exception as e:
    print("Ошибка подключения через прокси:", str(e))

# Настройка Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
MODEL_ID = "gemini-2.0-flash"

app = Flask(__name__)


def load_example(structure_path="creature_generator/dnd_card_template.json"):
    with open(structure_path, "r", encoding="utf-8") as f:
        return json.load(f)


json_example = load_example()


def create_prompt_for_img_input():
    json_ex = json.dumps(json_example, ensure_ascii=False, indent=2)
    prompt = f"""
    На изображении — карточка персонажа из DnD.
    Проанализируй её и распарси содержимое в JSON, как в примере:

    {json_ex}

    Если чего-то нет на карточке — не добавляй это поле вовсе. Поля eng должны быть заполнены (сделай перевод сам).
    Ответ строго в формате JSON:
    """
    return prompt


def create_prompt_for_text_input(description):
    json_ex = json.dumps(json_example, ensure_ascii=False, indent=2)
    prompt = f"""
    Ты опытный мастер DnD. На основе описания существа создай его полную игровую карточку.
    Описание существа: {description}

    Пример структуры карточки: {json_ex}

    Заполняй те поля, которые считаешь необходимыми для данного персонажа. Остальные просто не добавляй.
    Поля eng должны быть заполнены (сделай перевод сам).
    В целом проявляй креативность и фантазию.

    Ответ строго в формате JSON:
    """
    return prompt


@app.route('/parse_card_from_img/', methods=['POST'])
def parse_card_from_img():
    """
    Обрабатывает изображение карточки DnD и возвращает JSON
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        prompt = create_prompt_for_img_input()

        # Создаём модель (прокси уже глобально задан)
        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content([prompt, image])

        cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_response)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Ошибка обработки: {str(e)}"}), 500


@app.route('/create_struct_from_desc/', methods=['POST'])
def create_struct_from_desc():
    """
    Генерирует структуру существа DnD на основе текстового описания
    """
    data = request.get_json()
    if not data or 'desc' not in data:
        return jsonify({"error": "Description is required"}), 400

    try:
        prompt = create_prompt_for_text_input(data["desc"])
        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content(prompt)

        cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_response)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Ошибка обработки: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
