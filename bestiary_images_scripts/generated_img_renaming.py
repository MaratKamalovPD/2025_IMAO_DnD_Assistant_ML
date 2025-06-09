import os
import shutil
from pathlib import Path

# === НАСТРОЙКИ ===
INPUT_DIR = Path("images/raw_generated_images")  # Папка с исходными PNG
OUTPUT_DIR = Path("images/processed_generated_images")  # Папка для сохранения новых файлов
NAMES_FILE = Path("images/names.txt")  # Файл с именами

# === ПРОВЕРКИ ===
if INPUT_DIR.resolve() == OUTPUT_DIR.resolve():
    raise ValueError("Исходная и целевая директории должны быть разными!")

# Получаем все PNG-файлы в папке
png_files = [f for f in INPUT_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".png"]

# Сортировка по времени создания (ctime)
png_files.sort(key=lambda f: f.stat().st_ctime)

# Чтение новых имен из файла
with open(NAMES_FILE, "r", encoding="utf-8") as f:
    names = [line.strip() for line in f if line.strip()]

# Проверка на совпадение количества
if len(names) != len(png_files):
    raise ValueError(f"Несовпадение количества файлов: {len(png_files)} PNG-файлов, {len(names)} имён в names.txt")

# Создание выходной папки, если нет
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Копирование с переименованием
for src_file, new_name in zip(png_files, names):
    dst_file = OUTPUT_DIR / f"{new_name}.png"
    shutil.copy2(src_file, dst_file)

print(f"✅ Успешно обработано {len(png_files)} файлов.")
