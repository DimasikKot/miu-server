from fastapi import APIRouter, HTTPException, Request

from api.v2.diff import compare
from api.v2.manifest import load_manifest
from api.v2.models.UpdatePostRequest import UpdatePostRequest
from api.v2.models.UpdatePostResponse import UpdatePostResponse
from config import settings

router_update: APIRouter = APIRouter()


@router_update.post("/{instance}", response_model=UpdatePostResponse)
def router_update(instance: str, data: UpdatePostRequest, request: Request):
    instance_path = settings.INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    server_manifest = load_manifest(instance_path)
    if server_manifest is None:
        raise HTTPException(500, "Manifest missing")

    result = compare(instance, data, server_manifest, str(request.base_url).rstrip("/"))

    return result
