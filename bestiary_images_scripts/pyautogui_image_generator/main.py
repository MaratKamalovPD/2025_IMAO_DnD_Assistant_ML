import pyautogui
import keyboard
import pyperclip
import time
import threading
from PIL import Image
import io
import requests
import tempfile
import os
from dotenv import load_dotenv

from bestiary_images_scripts.pyautogui_image_generator.set_image_to_clipboard import set_image_to_clipboard
from google.sheet_session import SheetSession  # Импортируй сюда свою реализацию

# ===== Настройки Google Sheets =====
load_dotenv()

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE = 'CreatureImages!A2:D1887'  # A — чекбокс, C — URL картинки

sheet = SheetSession(spreadsheet_id=SPREADSHEET_ID, default_range=RANGE)
row_pointer = {'index': 0}  # Используем словарь, чтобы сохранять между вызовами

# ===== Вставка текста =====
def task_paste_text():
    text_to_paste = "Add a background that matches the lore, habitat, and mood of the Dungeons & Dragons creature shown in the input image. Preserve the creature’s pose, proportions, colors, and key visual features as closely as possible. The background should enhance the narrative and setting of the creature without altering the character's design. Make it look like the creature is naturally part of its world. Keep lighting and shadows consistent with the added environment."
    pyperclip.copy(text_to_paste)
    time.sleep(0.2)
    keyboard.press_and_release('ctrl+v')
    print("[F1] Текст вставлен.")

# ===== Найти следующую неотмеченную строку =====
def get_next_unprocessed_image():
    data = sheet.get()
    for i in range(row_pointer['index'], len(data)):
        row = data[i]
        checkbox = row[0].strip().upper() if len(row) > 0 else ""
        image_url = row[2] if len(row) > 2 else None

        if checkbox != "TRUE" and image_url:
            row_pointer['index'] = i + 1  # Сохраняем индекс для следующего запуска
            return image_url, i  # Возвращаем ссылку и индекс строки

    print("[F2] Нет необработанных строк с изображением.")
    return None, None

# ===== Скачивание и вставка изображения =====
def task_paste_image():
    image_url, row_idx = get_next_unprocessed_image()
    if not image_url:
        return

    try:
        # Скачиваем изображение из интернета
        response = requests.get(image_url)
        response.raise_for_status()

        # Загружаем картинку как изображение с альфой (RGBA)
        image = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Кладем изображение с прозрачностью в буфер через .NET Clipboard API
        set_image_to_clipboard(image)

        # Вставляем через эмуляцию Ctrl+V
        keyboard.press_and_release('ctrl+v')
        print(f"[F2] Вставлено изображение из строки {row_idx + 2} с прозрачностью.")

        # Отмечаем строку как обработанную в таблице
        sheet.queue_write(f'CreatureImages!A{row_idx + 2}', [['TRUE']])

    except Exception as e:
        print(f"[F2] Ошибка вставки изображения: {e}")

# ===== Слушатель горячих клавиш =====
def hotkey_listener():
    print("Готово. Ctrl+F1 — вставить текст, Ctrl+F2 — вставить изображение, Ctrl+Q — выход.")
    while True:
        if keyboard.is_pressed('ctrl+f1'):
            threading.Thread(target=task_paste_text).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl+f2'):
            threading.Thread(target=task_paste_image).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('f3'):  # Новая горячая клавиша для получения координат
            x, y = pyautogui.position()
            print(f"[F3] Координаты мыши: ({x}, {y})")
            time.sleep(1)   

        if keyboard.is_pressed('ctrl+q'):
            print("Скрипт остановлен пользователем.")
            break

        time.sleep(0.1)

if __name__ == "__main__":
    hotkey_listener()
