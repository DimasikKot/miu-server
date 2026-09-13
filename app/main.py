from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.v1.endpoints import router_v1
from api.v2.endpoints import router_v2
from api.v3.endpoints import router_v3
from config import settings

app = FastAPI(title="PurMur Instances", version="2.0.0")
app.mount(
    str(settings.INSTANCES_DIR_PATH),
    StaticFiles(directory=settings.INSTANCES_DIR_PATH),
    name="instances",
)
app.mount(
    str(settings.MIU_CLIENT_DIR_PATH),
    StaticFiles(directory=settings.MIU_CLIENT_DIR_PATH),
    name="miu-client",
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
app.include_router(router_v2, tags=["V2"], prefix="/api/v2")
app.include_router(router_v3, tags=["V3"], prefix="/api/v3")
app.include_router(router_v1, tags=["V1"])
