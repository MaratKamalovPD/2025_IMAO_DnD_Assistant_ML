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
import random
import numpy as np
from PIL import ImageGrab

from bestiary_images_scripts.pyautogui_image_generator.set_image_to_clipboard import set_image_to_clipboard
from bestiary_images_scripts.pyautogui_image_generator.send_img_to_ocr import send_image_to_ocr
from google.sheet_session import SheetSession  # Импортируй сюда свою реализацию

# ===== Настройки Google Sheets =====
load_dotenv()

EXTRA_TEXT_GLOBAL = ""

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE = 'CreatureImages!A2:E1887'  # A — чекбокс, C — URL картинки

sheet = SheetSession(spreadsheet_id=SPREADSHEET_ID, default_range=RANGE)
row_pointer = {'index': 0}  # Используем словарь, чтобы сохранять между вызовами

stop_requested = threading.Event()

template_path = r"bestiary_images_scripts/pyautogui_image_generator/img_templated/Generation_BG.bmp"

# Область поиска по координатам мыши
search_region = (485, 473, 1111 - 485, 853 - 473)

def random_sleep(base_delay=0.25, mean=0.3, sigma=0.4, max_delay=2.0):
    """
    Имитирует случайную человеческую задержку между действиями.
    
    - base_delay: минимальная задержка (в секундах), например 250 мс.
    - mean: логарифмическое среднее логнормального распределения.
    - sigma: стандартное отклонение.
    - max_delay: максимальная задержка (в секундах).
    """
    # Генерируем дополнительную задержку на основе логнормального распределения
    additional_delay = np.random.lognormal(mean=mean, sigma=sigma)
    
    # Ограничиваем итоговую задержку в разумных пределах
    total_delay = min(base_delay + additional_delay, max_delay)

    time.sleep(total_delay)

def is_background_present(region, expected_color=(26, 26, 26), tolerance=3, samples=10):
    screenshot = ImageGrab.grab(bbox=region).convert("RGB")
    width, height = screenshot.size
    pixels = screenshot.load()

    for _ in range(samples):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b = pixels[x, y]
        if not (
            abs(r - expected_color[0]) <= tolerance and
            abs(g - expected_color[1]) <= tolerance and
            abs(b - expected_color[2]) <= tolerance
        ):
            return False  # Фон не однотонный — считаем, что он исчез
    return True  # Все точки соответствуют — фон ещё отображается

def search_image():
    print("[F7] Запуск поиска изображения...")
    try:
        location = pyautogui.locateOnScreen(template_path, region=search_region, confidence=0.99)
        if location:
            print(f"[F7] Найдено изображение по координатам: {location}")
        else:
            print("[F7] Изображение не найдено.")
    except Exception as e:
        print(f"[F7] Ошибка при поиске: {e}")

def continuous_image_search():
    print("[F7] Поток поиска изображения запущен. Нажмите Ctrl+F6 для остановки.")
    while not stop_requested.is_set():
        search_image()
        time.sleep(1)
    print("[F7] Поток поиска остановлен.")

def random_offset(x, y, radius=10):
    """Возвращает координаты с небольшим случайным отклонением."""
    return (
        x + random.randint(-radius, radius),
        y + random.randint(-radius, radius)
    )

def automation_loop():
    print("[F1] Автоматический цикл запущен.")
    while not stop_requested.is_set():
        # Клик в первую точку
        x1, y1 = random_offset(1146, 1824)
        pyautogui.click(x=x1, y=y1)
        print(f"[F1] Клик в начальную точку: ({x1}, {y1})")
        time.sleep(1)

        # Вставка изображения
        extra_text = task_paste_image()

        # Ждём 1–2 секунды на подгрузку + немного случайной задержки
        time.sleep(random.randint(1, 2))
        random_sleep()

        # Вставка текста
        task_paste_text(extra_text)
        time.sleep(1)
        random_sleep()

        # ⏳ Ожидание появления изображения (до 3 минут)
        print("[F1] Ожидание появления изображения (до 3 минут)...")
        image_found = False
        start_time = time.time()
        while time.time() - start_time < 180:
            try:
                location = pyautogui.locateOnScreen(
                    r"bestiary_images_scripts\pyautogui_image_generator\img_templated\Remix.bmp",
                    region=(2416, 1877, 2552 - 2416, 1964 - 1877),
                    confidence=0.9
                )
                if location:
                    print(f"[F1] Изображение найдено по координатам: {location}")
                    image_found = True
                    break
            except Exception as e:
                print(f"[F1] Ошибка при поиске изображения: {e}")

            if stop_requested.is_set():
                print("[F2] Остановка по запросу во время ожидания изображения.")
                return

            time.sleep(1)

        if not image_found:
            print("[F1] Ошибка: изображение не найдено в течение 3 минут. Завершаем цикл.")
            break

        # Клик во вторую точку
        x2, y2 = random_offset(2477, 1916)
        pyautogui.click(x=x2, y=y2)
        print(f"[F1] Клик в завершающую точку: ({x2}, {y2})")

        # Подождать 15 секунд для появления фонового окна
        time.sleep(15)

        # Проверка наличия фонового изображения
        bg_region = (485, 473, 1111, 853)  # Формат для ImageGrab: (left, top, right, bottom)

        print("[F1] Ожидание завершения генерации (фон должен исчезнуть)...")
        while True:
            try:
                if is_background_present(bg_region):
                    print("[F1] Фон генерации всё ещё отображается. Ожидание...")
                else:
                    print("[F1] Фон исчез. Продолжаем.")
                    break
            except Exception as e:
                print(f"[F1] Ошибка при проверке фонового цвета: {e}")

            if stop_requested.is_set():
                print("[F2] Остановка по запросу во время ожидания завершения генерации.")
                return

            time.sleep(1)

        screenshot_region = (444, 397, 1129 - 444, 1444 - 397)
        screenshot = pyautogui.screenshot(region=screenshot_region)
        print("[F1] Скриншот области отправляется на OCR-сервер...")

        try:
            ocr_result = send_image_to_ocr(screenshot)
            print(f"[F1] Результат OCR: {ocr_result}")
        except Exception as e:
            print(f"[F1] Ошибка при отправке изображения на OCR-сервер: {e}")
            break  # Лучше прервать цикл, чем продолжать с недостоверным распознаванием

        # Проверка на ключевые слова
        trigger_words = {"pick", "improve", "images", "best", "help"}
        found_words = []

        for item in ocr_result.get("results", []):
            text = item.get("text", "").lower()
            for word in trigger_words:
                if word in text:
                    found_words.append(word)

        if found_words:
            print(f"[F1] Обнаружены ключевые слова {found_words} — завершаем цикл.")
            return
        else:
            print("[F1] Ничего подозрительного не найдено в OCR. Продолжаем.")

    print("[F1] Цикл остановлен.")


# ===== Вставка текста =====
def task_paste_text(extra_text=""):
    base_text  = "Add a background that matches the lore, habitat, and mood of the Dungeons & Dragons creature shown in the input image. Preserve the creature’s pose, proportions, colors, and key visual features as closely as possible. The background should enhance the narrative and setting of the creature without altering the character's design. Make it look like the creature is naturally part of its world. Keep lighting and shadows consistent with the added environment."
    # Добавим пробел и доп. текст, если он не пустой
    if extra_text.strip():
        full_text = f"{base_text} {extra_text.strip()}"
    else:
        full_text = base_text

    pyperclip.copy(full_text)
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
        extra_text = row[4] if len(row) > 4 else ""

        if checkbox != "TRUE" and image_url:
            row_pointer['index'] = i + 1
            return image_url, extra_text, i  # Возвращаем ссылку, доп. текст и индекс

    print("[F2] Нет необработанных строк с изображением.")
    return None, None, None


# ===== Скачивание и вставка изображения =====
def task_paste_image():
    image_url, extra_text, row_idx = get_next_unprocessed_image()
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

    return extra_text

# ===== Слушатель горячих клавиш =====
def hotkey_listener():
    print("Готово. Ctrl+F1 — автозапуск, Ctrl+F2 — стоп, Ctrl+F8 — вставить текст, Ctrl+F9 — вставить изображение, Ctrl+F3 — координаты, Ctrl+Q — выход.")
    while True:
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('f1'):
            stop_requested.clear()
            threading.Thread(target=automation_loop).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('f2'):
            stop_requested.set()
            print("[F2] Остановка запрошена.")
            time.sleep(1)

        if keyboard.is_pressed('ctrl+f8'):
            threading.Thread(target=task_paste_text).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl+f9'):
            threading.Thread(target=task_paste_image).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('f3'):
            x, y = pyautogui.position()
            print(f"[F3] Координаты мыши: ({x}, {y})")
            time.sleep(1)

        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('f7'):
            stop_requested.clear()
            threading.Thread(target=continuous_image_search).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('f6'):
            stop_requested.set()
            print("[F6] Остановка поиска изображения.")
            time.sleep(1)

        if keyboard.is_pressed('ctrl+q'):
            print("Скрипт остановлен пользователем.")
            break

        time.sleep(0.1)

if __name__ == "__main__":
    hotkey_listener()
