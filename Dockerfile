# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения
COPY . .

# Устанавливаем системные зависимости для OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска
CMD ["sh", "-c", "uvicorn main:app --host $HOST --port $PORT"]

