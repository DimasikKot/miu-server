from fastapi import APIRouter, HTTPException, Path

from models.server.BuildPostResponse import BuildPostResponse
from config import settings
from logic.build import build_manifest, save_manifest

router_build: APIRouter = APIRouter()


@router_build.post("/{instance_name}", response_model=BuildPostResponse)
def build_post(
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    )
) -> BuildPostResponse:
    instance_path = settings.INSTANCES_DIR_PATH / instance_name
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    manifest, response = build_manifest(instance_path)
    save_manifest(instance_path, manifest)

    return BuildPostResponse.model_validate(response)
