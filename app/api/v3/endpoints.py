from fastapi import APIRouter

from api.v3.routers.update_post import router_update_post

router_v3: APIRouter = APIRouter()


router_v3.include_router(router_update_post, prefix="/update")
