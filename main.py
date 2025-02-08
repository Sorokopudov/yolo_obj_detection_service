import os
import base64
from io import BytesIO
import torch
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from PIL import Image
from ultralytics import YOLO
from dotenv import load_dotenv
import uvicorn


# Загрузка переменных окружения
load_dotenv()

# Конфигурация
MODEL_PATH = os.getenv("MODEL_PATH", "./models/yolov8_1280_car_06_02_25.pt")
DEVICE = os.getenv("DEVICE", "cpu")  # По умолчанию CPU
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Проверяем, доступна ли CUDA
if DEVICE.startswith("cuda") and not torch.cuda.is_available():
    print("CUDA недоступна, переключаюсь на CPU")
    DEVICE = "cpu"

# Загрузка модели YOLO
model = YOLO(MODEL_PATH)

app = FastAPI()


# Модель данных для API
class ImageRequest(BaseModel):
    image_base64: str  # Base64-строка изображения


@app.get("/", response_class=HTMLResponse)
async def render_form():
    return """
    <html>
        <head><title>YOLO Object Detection</title></head>
        <body>
            <h1>Загрузите изображение</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file"/>
                <button type="submit">Обработать</button>
            </form>
        </body>
    </html>
    """


import cv2

@app.post("/upload", response_class=HTMLResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Эндпоинт для загрузки изображения через веб-интерфейс.
    """
    try:
        # Считываем изображение
        image = Image.open(file.file)

        # Выполняем инференс модели
        results = model.predict(image, device=DEVICE, save=False, save_txt=False)

        # Process results list
        for result in results:
            boxes = result.boxes.xyxy.tolist()  # Преобразуем bounding boxes в список координат

        # Накладываем маску на изображение
        image_with_boxes = result.plot()  # Возвращает numpy.ndarray (в BGR формате)

        # Конвертируем цветовое пространство из BGR в RGB
        image_with_boxes = cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)

        # Конвертируем numpy.ndarray в PIL.Image
        image_with_boxes = Image.fromarray(image_with_boxes)

        # Конвертируем изображение с bbox в base64
        buffer = BytesIO()
        image_with_boxes.save(buffer, format="JPEG")
        mask_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Возвращаем HTML с изображением
        return f"""
        <html>
            <head><title>Результат обработки</title></head>
            <body>
                <h1>Обработанное изображение</h1>
                <img src="data:image/jpeg;base64,{mask_base64}" alt="Processed Image" />
                <h2>Bounding Boxes:</h2>
                <pre>{boxes}</pre>
                <a href="/">Вернуться назад</a>
            </body>
        </html>
        """

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки изображения: {str(e)}")




@app.post("/process_image")
async def process_image(request: ImageRequest):
    """
    Эндпоинт для обработки изображения в формате base64.
    Возвращает наложенную маску (в base64) и массив bounding boxes.
    """
    try:
        # Декодируем base64-строку в изображение
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(BytesIO(image_data))

        # Выполняем инференс модели
        results = model.predict(image, device=DEVICE, save=False, save_txt=False)

        # Process results list
        for result in results:
            boxes = result.boxes.xyxy.tolist()  # Преобразуем bounding boxes в список координат

        # Накладываем маску на изображение
        mask_image = result.plot()  # Возвращает numpy.ndarray

        # Конвертируем цветовое пространство из BGR в RGB
        mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)

        # Конвертируем numpy.ndarray в PIL.Image
        mask_image = Image.fromarray(mask_image)

        # Конвертируем изображение с масками в base64
        buffer = BytesIO()
        mask_image.save(buffer, format="JPEG")
        mask_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "processed_image_base64": mask_base64,
            "boxes": boxes,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки изображения: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("yolo_obj_detection_service.main:app", host="0.0.0.0", port=8080, reload=True)

