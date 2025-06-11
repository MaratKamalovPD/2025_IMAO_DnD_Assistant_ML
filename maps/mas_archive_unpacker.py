import os
import py7zr
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

source_dir = os.getenv("SOURCE_DIR")
dest_dir = os.getenv("DEST_DIR")

if not source_dir or not dest_dir:
    print("❌ Не заданы пути в .env")
    exit(1)

# Получаем список .7z файлов
archives = sorted([f for f in os.listdir(source_dir) if f.lower().endswith('.7z')])

for i, archive in enumerate(archives, 1):
    archive_path = os.path.join(source_dir, archive)
    folder_name = os.path.splitext(archive)[0]
    output_path = os.path.join(dest_dir, folder_name)
    os.makedirs(output_path, exist_ok=True)

    print(f"[{i}/{len(archives)}] Распаковка: {archive} → {output_path}")
    try:
        with py7zr.SevenZipFile(archive_path, mode='r') as z:
            z.extractall(path=output_path)
    except Exception as e:
        print(f"❌ Ошибка при распаковке {archive}: {e}")
