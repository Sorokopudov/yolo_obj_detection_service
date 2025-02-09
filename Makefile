# Переменные окружения (можно переопределять при запуске make)
PORT ?= 8000
HOST ?= 0.0.0.0
DEVICE ?= cpu
MODEL_PATH ?= ./models/yolov8_1280_car_06_02_25.pt

# Сборка Docker-образа
build:
	docker build -t yolo-app .

# Запуск контейнера на CPU
run-cpu:
	docker run --name yolo-container -p $(PORT):$(PORT) \
		-e HOST=$(HOST) \
		-e PORT=$(PORT) \
		-e DEVICE=$(DEVICE) \
		-e MODEL_PATH=$(MODEL_PATH) \
		yolo-app

# Запуск контейнера на GPU
run-gpu:
	docker run --name yolo-container -p $(PORT):$(PORT) --gpus all \
		-e HOST=$(HOST) \
		-e PORT=$(PORT) \
		-e DEVICE=cuda:0 \
		-e MODEL_PATH=$(MODEL_PATH) \
		yolo-app

# Остановка и удаление контейнера (если он существует)
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Удаление контейнера yolo-container
clean:
	docker rm yolo-container || true

# Удаление образа yolo-app
remove-image:
	docker rmi -f yolo-app || true

# Полная очистка проекта (только yolo-app)
reset: stop clean remove-image

