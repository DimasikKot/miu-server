from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from api.v1.endpoints import router_v1

from api.v2.endpoints import router_v2
from config import settings

app = FastAPI(title="PurMur Instances", version="2.0.0")
app.mount(
    str(settings.INSTANCES_FOLDER_PATH),
    StaticFiles(directory=settings.INSTANCES_FOLDER_PATH),
    name="instances",
)

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
app.include_router(router_v1, tags=["V1"])
app.include_router(router_v2, prefix="/api/v2", tags=["V2"])
