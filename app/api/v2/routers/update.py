from fastapi import APIRouter, HTTPException, Path, Request

from models.UpdatePostRequest import UpdatePostRequest
from models.UpdatePostResponse import UpdatePostResponse
from config import settings
from update import compare
from build import load_manifest

router_update: APIRouter = APIRouter()


@router_update.post("/{instance_name}", response_model=UpdatePostResponse)
def update_post(
    request: UpdatePostRequest,
    request_class: Request,
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> UpdatePostResponse:
    instance_path = settings.INSTANCES_FOLDER_PATH / instance_name
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    response = compare(
        request=request,
        instance_manifest=instance_manifest,
        instance_name=instance_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )

    return response
