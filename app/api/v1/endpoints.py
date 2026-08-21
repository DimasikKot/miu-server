from fastapi import APIRouter, HTTPException, Request

from api.v1.models import ClientManifest, UpdateResponse
from api.v1.transformV2toV1 import UpdatePostRequestV1toV2, UpdatePostResponseV2toV1
from config import settings
from diff import compare
from manifest import load_manifest

router_v1: APIRouter = APIRouter()


@router_v1.post("/update/{instance_name}", response_model=UpdateResponse)
def update(
    request: ClientManifest,
    request_class: Request,
    instance_name: str,
) -> UpdateResponse:
    request_v2 = UpdatePostRequestV1toV2(data=request)

    instance_path = settings.INSTANCES_FOLDER_PATH / instance_name
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    response = compare(
        request=request_v2,
        instance_manifest=instance_manifest,
        instance_name=instance_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )

    return UpdatePostResponseV2toV1(response)
