from fastapi import APIRouter

from api.v2.routers.build import router_build
from api.v2.routers.update import router_update
from api.v2.routers.miu_client import router_miu_client

router_v2: APIRouter = APIRouter()


router_v2.include_router(router_build, prefix="/build")
router_v2.include_router(router_update, prefix="/update")
router_v2.include_router(router_miu_client, prefix="/miu-client")
