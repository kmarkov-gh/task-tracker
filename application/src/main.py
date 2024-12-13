from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from prometheus_client import generate_latest, CollectorRegistry, Counter, Gauge, Summary
import psutil
import os
from database import SessionLocal, engine
from models import Task
from schemas import TaskCreate, TaskUpdate
from crud import get_tasks, create_task, update_task, delete_task

app = FastAPI()

# Создание одного реестра метрик
registry = CollectorRegistry()

# Прометей метрики
request_count = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint'], registry=registry)
request_duration = Summary('http_request_duration_seconds', 'Duration of HTTP requests in seconds', ['method', 'endpoint'], registry=registry)
system_cpu_usage = Gauge('system_cpu_usage', 'Percentage of CPU usage', registry=registry)
system_memory_usage = Gauge('system_memory_usage', 'Percentage of memory usage', registry=registry)
system_disk_usage = Gauge('system_disk_usage', 'Percentage of disk usage', registry=registry)

@app.get("/api/test")
def test_endpoint():
    return {"message": "Test endpoint works"}

@app.get("/api/tasks", response_class=JSONResponse)
async def read_tasks(request: Request):
    # Используем контекстный менеджер для измерения времени с ярлыками
    with request_duration.labels(method='GET', endpoint='/api/tasks').time():
        # Увеличиваем счетчик с ярлыками
        request_count.labels(method='GET', endpoint='/api/tasks').inc()

        # Получаем данные из базы данных
        with SessionLocal() as session:
            tasks = get_tasks(session)

        return tasks

from fastapi.responses import RedirectResponse, JSONResponse

# Эндпоинт для добавления новой задачи
@app.post("/api/tasks", response_class=JSONResponse)
async def add_task(request: Request, task: TaskCreate):
    with request_duration.labels(method='POST', endpoint='/api/tasks').time():
        request_count.labels(method='POST', endpoint='/api/tasks').inc()  # Увеличиваем счетчик с ярлыками
        with SessionLocal() as session:
            create_task(session, task)
    return RedirectResponse(url="/api/tasks", status_code=303)  # Исправлено на /api/tasks

# Эндпоинт для изменения задачи
@app.put("/api/tasks/{task_id}", response_class=JSONResponse)
async def modify_task(request: Request, task_id: int, task: TaskUpdate):
    with request_duration.labels(method='PUT', endpoint=f'/api/tasks/{task_id}').time():
        request_count.labels(method='PUT', endpoint=f'/api/tasks/{task_id}').inc()  # Увеличиваем счетчик с ярлыками
        with SessionLocal() as session:
            updated_task = update_task(session, task_id, task)
            if not updated_task:
                raise HTTPException(status_code=404, detail="Task not found")
    return RedirectResponse(url="/api/tasks", status_code=303)  # Исправлено на /api/tasks

# Эндпоинт для удаления задачи
@app.delete("/api/tasks/{task_id}", response_class=JSONResponse)
async def remove_task(request: Request, task_id: int):
    with request_duration.labels(method='DELETE', endpoint=f'/api/tasks/{task_id}').time():
        request_count.labels(method='DELETE', endpoint=f'/api/tasks/{task_id}').inc()  # Увеличиваем счетчик с ярлыками
        with SessionLocal() as session:
            if not delete_task(session, task_id):
                raise HTTPException(status_code=404, detail="Task not found")
    return RedirectResponse(url="/api/tasks", status_code=303)  # Исправлено на /api/tasks

# Endpoint для проверки статуса базы данных
@app.get("/api/db-status")
def db_status():
    try:
        # Проверка подключения к базе данных
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "Database is available"}
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database is unavailable")

# Endpoint для мониторинга производительности системы
@app.get("/api/system-metrics")
def system_metrics():
    # Системные метрики
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    # Обновляем метрики
    system_cpu_usage.set(cpu_usage)
    system_memory_usage.set(memory_info.percent)
    system_disk_usage.set(disk_usage.percent)

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_info.percent,
        "disk_usage": disk_usage.percent
    }

# Endpoint для Prometheus метрик
@app.get("/api/metrics")
def metrics():

    # Регистрируем метрики
    request_count.labels(method="GET", endpoint="/api/metrics").inc()  # Увеличиваем счетчик для метрик
#    print(generate_latest(registry).decode('utf-8'))
#    print(type(generate_latest(registry).decode('utf-8')))
    return Response(generate_latest(registry), media_type="text/plain; version=0.0.4; charset=utf-8")  # Даем Prometheus метрики

# Healthcheck эндпоинт
@app.get("/api/health")
def healthcheck():
    try:
        # Проверка подключения к базе данных
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except OperationalError as e:
        raise HTTPException(status_code=503, detail="Database is unavailable")

# Логи приложения
@app.get("/api/logs")
def get_logs():
    log_file_path = "/var/log/app.log"  # Путь к логам
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            logs = log_file.readlines()[-100:]  # Читаем последние 100 строк
        return {"logs": logs}
    else:
        raise HTTPException(status_code=404, detail="Logs not found")

