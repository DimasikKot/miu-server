from fastapi import APIRouter, Path

from logic.resolve_instance_path import resolve_instance_path
from models.server.BuildPostResponse import BuildPostResponse
from logic.build import build_manifest
from models.server.InstanceManifest import InstanceManifest

router_build: APIRouter = APIRouter()


@router_build.post(
    "/{instance_name}", response_model=BuildPostResponse | InstanceManifest
)
def build_post(
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    )
) -> BuildPostResponse | InstanceManifest:
    instance_path = resolve_instance_path(instance_name)

    response = build_manifest(instance_path)

    return response
