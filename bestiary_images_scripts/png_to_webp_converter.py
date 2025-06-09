import os
from PIL import Image

# 📂 Папки для входа и выхода
INPUT_FOLDER = "images/input_jpeg_maps"
OUTPUT_FOLDER = "images/output_webp_maps"

# 🔧 Качество WebP (0-100)
QUALITY = 95

def convert_to_webp(input_folder, output_folder, quality=90):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.lower().endswith(('.jpeg', '.jpg')):
            input_path = os.path.join(input_folder, file)
            output_file = os.path.splitext(file)[0] + ".webp"
            output_path = os.path.join(output_folder, output_file)

            with Image.open(input_path) as img:
                img = img.convert("RGB")
                img.save(output_path, "WEBP", quality=quality, method=6)
                print(f"[✔] {file} → {output_path} (q={quality})")

if __name__ == "__main__":
    if os.path.isdir(INPUT_FOLDER):
        convert_to_webp(INPUT_FOLDER, OUTPUT_FOLDER, QUALITY)
    else:
        print(f"❌ Папка '{INPUT_FOLDER}' не найдена.")
