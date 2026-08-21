from fastapi import APIRouter, HTTPException, Request

from models.MiuClientResponse import MiuClientResponse
from config import settings

router_miu_client: APIRouter = APIRouter()


@router_miu_client.get("", response_model=MiuClientResponse)
def miu_client_post(request_class: Request) -> MiuClientResponse:
    miu_client_dir_path = settings.MIU_CLIENT_DIR_PATH

    if not miu_client_dir_path.exists():
        raise HTTPException(404, "Miu-Client not found")

    return MiuClientResponse(
        path=str(miu_client_dir_path),
        url=str(request_class.base_url).rstrip("/") + str(miu_client_dir_path),
        sha256="",
        size=0,
    )
