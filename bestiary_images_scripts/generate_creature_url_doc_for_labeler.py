from pymongo import MongoClient
import os
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

# Загружаем переменные из .env
load_dotenv()

# Параметры подключения к MongoDB
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = "localhost"
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = "bestiary_db"

# Формируем URI и подключаемся
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
collection = db["creatures"]

# Извлекаем все документы
documents = collection.find()

# Собираем второй элемент массива images
url_list = []
for doc in documents:
    images = doc.get("images", [])
    if len(images) >= 2:
        url_list.append(images[1])

# Создаём Excel-файл
wb = Workbook()
ws = wb.active
ws.title = "Creature Images"

# Заголовки
ws.append(["✓", "Image URL"])

# Добавляем Data Validation для чекбоксов (TRUE/FALSE)
dv = DataValidation(type="list", formula1='"TRUE,FALSE"', allow_blank=True)
ws.add_data_validation(dv)

# Заполняем данными
for i, url in enumerate(url_list, start=2):  # начинаем с 2-й строки
    cell_check = f"A{i}"
    cell_url = f"B{i}"
    ws[cell_check] = "FALSE"
    ws[cell_url] = url
    dv.add(ws[cell_check])

# Сохраняем файл
output_filename = "creature_images.xlsx"
wb.save(output_filename)
print(f"Файл сохранён как {output_filename}")
