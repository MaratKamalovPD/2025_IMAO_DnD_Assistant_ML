import clr
from PIL import Image
import io

# Подключаем .NET сборки
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

import System
from System import IO
from System.Drawing import Bitmap, Graphics
from System.Windows.Forms import Clipboard

def set_image_to_clipboard(pil_image: Image.Image):
    # Сохраняем PIL.Image в PNG в поток
    stream = io.BytesIO()
    pil_image.save(stream, format="PNG")
    stream.seek(0)

    # Конвертируем в .NET MemoryStream
    mem_stream = IO.MemoryStream(stream.read())

    # Загружаем как Bitmap (именно PNG с прозрачностью)
    bitmap = Bitmap(mem_stream)

    # Создаём новый Bitmap для хранения изображения с альфа-каналом
    # Используем PixelFormat.Format32bppArgb для сохранения альфа-канала
    new_bitmap = Bitmap(bitmap.Width, bitmap.Height, System.Drawing.Imaging.PixelFormat.Format32bppArgb)
    
    # Рисуем изображение на новый Bitmap
    graphics = Graphics.FromImage(new_bitmap)
    graphics.DrawImage(bitmap, 0, 0)

    # Устанавливаем в буфер обмена
    Clipboard.SetImage(new_bitmap)
    print("[Clipboard] Изображение с прозрачностью скопировано в буфер.")

