FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем приложение и зависимости
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY *.py /app

# Запускаем Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
