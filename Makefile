# Переменные окружения (можно переопределять при запуске make)
PORT ?= 8000
HOST ?= 0.0.0.0
DEVICE ?= cpu
MODEL_PATH ?= ./models/yolov8_1280_car_06_02_25.pt
CONTAINER_NAME ?= yolo-container  # <== Добавил недостающую переменную

# Сборка Docker-образа
build:
	docker build -t yolo-app .

# Запуск контейнера на CPU (с удалением старого)
run-cpu: stop
	docker run --name $(CONTAINER_NAME) -p $(PORT):$(PORT) \
		-e HOST=$(HOST) \
		-e PORT=$(PORT) \
		-e DEVICE=cpu \
		-e MODEL_PATH=$(MODEL_PATH) \
		yolo-app

# Запуск контейнера на GPU (с удалением старого)
run-gpu: stop
	docker run --name $(CONTAINER_NAME) -p $(PORT):$(PORT) --gpus all \
		-e HOST=$(HOST) \
		-e PORT=$(PORT) \
		-e DEVICE=cuda:0 \
		-e MODEL_PATH=$(MODEL_PATH) \
		yolo-app

# Остановка и удаление контейнера (если он существует)
stop:
	@if [ ! -z "$$(docker ps -aq -f name=$(CONTAINER_NAME))" ]; then \
		echo "Stopping and removing existing container: $(CONTAINER_NAME)"; \
		docker stop $(CONTAINER_NAME); \
		docker rm $(CONTAINER_NAME); \
	else \
		echo "No container to stop."; \
	fi

# Удаление контейнера yolo-container
clean:
	docker rm $(CONTAINER_NAME) || true

# Удаление образа yolo-app
remove-image:
	docker rmi -f yolo-app || true

# Полная очистка проекта (только yolo-app)
reset: stop clean remove-image

