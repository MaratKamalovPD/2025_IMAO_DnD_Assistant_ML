from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import easyocr
import numpy as np
from PIL import Image
import io
import time
import torch

app = FastAPI()

# Проверка CUDA при запуске
cuda_available = torch.cuda.is_available()
device_name = torch.cuda.get_device_name(0) if cuda_available else "CUDA not available"
print(f"[INIT] CUDA Available: {cuda_available}, Device: {device_name}")

# Инициализация easyocr
reader = easyocr.Reader(['en'], gpu=cuda_available)

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:
        start_time = time.time()

        # Чтение и преобразование изображения
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(image)

        # Распознавание текста
        results = reader.readtext(img_np)
        elapsed = round(time.time() - start_time, 3)

        # Обработка результатов
        processed_results = [
            {
                "text": text,
                "box": [[int(coord[0]), int(coord[1])] for coord in box],
                "conf": float(conf)
            }
            for box, text, conf in results
        ]

        response_data = {
            "results": processed_results,
            "time": elapsed
        }

        # Возврат безопасного JSON
        return JSONResponse(content=jsonable_encoder(response_data))

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": str(e)
        })
