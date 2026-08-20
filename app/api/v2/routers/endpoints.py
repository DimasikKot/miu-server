from fastapi import APIRouter

from app.api.v2.routers.build import router_build
from app.api.v2.routers.update import router_update

router_v2: APIRouter = APIRouter()

router_v2.include_router(router_build, prefix="/build", tags=["Build"])
router_v2.include_router(router_update, prefix="/update", tags=["Update"])
