from pathlib import Path
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from app.api.v1.router_v1 import router_v1
from app.api.v2.routers.endpoints import router_v2

MANIFEST_NAME = "manifest.json"
INSTANCES_FOLDER_PATH = Path("/istances")

app = FastAPI(title="PurMur Instances", version="1.1.0")
app.mount("/istances", StaticFiles(directory=INSTANCES_FOLDER_PATH), name="istances")

# # Разрешённые источники
# origins: list[str] = [
#     "http://localhost:5173",  # Фронтенд на Vite
#     "http://127.0.0.1:5173",  # Альтернативный локальный хост
#     "*",
# ]

# # Добавляем CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Кто может делать запросы
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешенные методы (GET, POST и т.д.)
#     allow_headers=["*"],  # Разрешенные заголовки
# )

# Подключение всех версий API
app.include_router(router_v1)
app.include_router(router_v2, prefix="/api/v2")
