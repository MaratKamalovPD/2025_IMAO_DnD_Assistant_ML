import os
from PIL import Image

# 📂 Папки для входа и выхода
INPUT_FOLDER = "images/input_png_images"
OUTPUT_FOLDER = "images/output_webp_images"

# 📐 Целевой размер для карточек товаров
OUTPUT_SIZE = (300, 400)  # Соотношение 3:4
QUALITY = 90  # Качество WebP (0-100)

def resize_and_crop(image, target_size):
    img_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]

    # Центрированная обрезка по высоте или ширине
    if img_ratio < target_ratio:
        new_height = int(image.width / target_ratio)
        offset = (image.height - new_height) // 2
        image = image.crop((0, offset, image.width, offset + new_height))
    elif img_ratio > target_ratio:
        new_width = int(image.height * target_ratio)
        offset = (image.width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, image.height))

    return image.resize(target_size, Image.LANCZOS)

def process_images(input_folder, output_folder, output_size=(300, 400), quality=80):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.lower().endswith('.png'):
            input_path = os.path.join(input_folder, file)
            output_file = os.path.splitext(file)[0] + ".webp"
            output_path = os.path.join(output_folder, output_file)

            with Image.open(input_path) as img:
                img = img.convert("RGB")
                img = resize_and_crop(img, output_size)
                img.save(output_path, "WEBP", quality=quality, method=6)
                print(f"[✔] {file} → {output_path} ({output_size[0]}x{output_size[1]}, q={quality})")

if __name__ == "__main__":
    if os.path.isdir(INPUT_FOLDER):
        process_images(INPUT_FOLDER, OUTPUT_FOLDER, OUTPUT_SIZE, QUALITY)
    else:
        print(f"❌ Папка '{INPUT_FOLDER}' не найдена.")
