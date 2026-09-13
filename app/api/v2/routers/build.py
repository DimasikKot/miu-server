from fastapi import APIRouter, Path

from logic.resolve_instance_path import resolve_instance_path
from logic.build import build_manifest
from models.v3.server import BuildPostResponse, InstanceManifest, ReBuildPostResponse

router_build: APIRouter = APIRouter()


@router_build.post(
    "/{instance_name}",
    response_model=BuildPostResponse | ReBuildPostResponse | InstanceManifest,
    response_model_exclude_defaults=True,
)
def build_post(
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Create",
    )
) -> BuildPostResponse | ReBuildPostResponse | InstanceManifest:
    instance_path = resolve_instance_path(instance_name)

    response = build_manifest(instance_path)

    return response
