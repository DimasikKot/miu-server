from fastapi import APIRouter, HTTPException, Path

from logic.resolve_instance_path import resolve_instance_path
from logic.build import load_manifest
from models.v2 import UpdateGetResponse

router_update_get: APIRouter = APIRouter()


@router_update_get.get("/{instance_name}", response_model=UpdateGetResponse)
def update_get(
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> UpdateGetResponse:
    instance_path = resolve_instance_path(instance_name)

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    return UpdateGetResponse(
        files_paths=instance_manifest.files_paths,
        dirs_paths=instance_manifest.dirs_paths,
        strict_files_paths=instance_manifest.strict_files_paths,
        strict_dirs_paths=instance_manifest.strict_dirs_paths,
    )
