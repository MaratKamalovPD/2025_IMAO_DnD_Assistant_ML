import requests
from PIL import Image
import io
import os

from dotenv import load_dotenv
load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')

def send_image_to_ocr(image: Image.Image, server_ip=SERVER_IP):
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)

    response = requests.post(
        f"http://{server_ip}:7000/ocr",
        files={"file": ("screenshot.png", buf, "image/png")}
    )

    return response.json()
