import pyautogui
import keyboard
import pyperclip
import time
import threading
from PIL import Image
import win32clipboard
import io

# ===== Task 1: Вставка текста =====
def task_paste_text():
    text_to_paste = "Привет! Это тестовое сообщение из буфера обмена."
    pyperclip.copy(text_to_paste)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    print("[F1] Текст вставлен.")

# ===== Task 2: Вставка изображения =====
def task_paste_image():
    image_path = "bestiary_images_scripts\pyautogui_image_generator\img_templated\shadowHeart.jpg"  # Путь к картинке

    try:
        image = Image.open(image_path)

        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # обрезаем заголовок BMP
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        print("[F2] Изображение вставлено.")
    except Exception as e:
        print(f"[F2] Ошибка вставки изображения: {e}")

# ===== Привязка тасков к хоткеям =====
def hotkey_listener():
    print("Готово. Нажми Ctrl+F1 для текста или Ctrl+F2 для изображения. Ctrl+Q — выход.")
    while True:
        if keyboard.is_pressed('ctrl+f1'):
            threading.Thread(target=task_paste_text).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl+f2'):
            threading.Thread(target=task_paste_image).start()
            time.sleep(1)

        if keyboard.is_pressed('ctrl+q'):
            print("Скрипт остановлен пользователем.")
            break

        time.sleep(0.1)

if __name__ == "__main__":
    hotkey_listener()
