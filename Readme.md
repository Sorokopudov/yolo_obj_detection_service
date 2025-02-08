# YOLO Object Detection API
## Описание

Проект предоставляет API для обработки изображений с использованием модели YOLOv8. API принимает изображение в формате base64 и возвращает bounding boxes объектов и обработанное изображение.

## Установка и запуск
### Зависимости

Убедитесь, что у вас установлены Docker и Make.

### Сборка Docker-образа
```bash
make build
```

### Запуск контейнера на CPU
```bash
make run-cpu
```
### Запуск контейнера на GPU
```bash
make run-gpu
```

### Остановка контейнера
```bash
make stop
```

### Удаление контейнера и образа
```bash
make reset
```

## Использование API
Пример запроса
```bash
import requests
import base64

API_URL = "http://localhost:8000/process_image"
IMAGE_PATH = "path/to/your/image.jpg"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_base64 = encode_image_to_base64(IMAGE_PATH)
payload = {"image_base64": image_base64}
response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    result = response.json()
    print("Bounding Boxes:", result["boxes"])
else:
    print(f"Ошибка: {response.status_code}, {response.text}")
```

## Параметры запуска

- **HOST**: Хост для запуска API (по умолчанию `0.0.0.0`).
- **PORT**: Порт для запуска API (по умолчанию `8000`).
- **DEVICE**: Устройство для выполнения модели (`cpu` или `cuda:0`).
- **MODEL_PATH**: Путь к модели YOLOv8.