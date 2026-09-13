from fastapi import APIRouter, HTTPException, Path, Request

from logic.resolve_instance_path import resolve_instance_path
from logic.save_request import save_request
from logic.update import compare
from logic.build import load_manifest
from models.v2 import UpdateGetResponse, UpdatePostRequest, UpdatePostResponse

router_update: APIRouter = APIRouter()


@router_update.get("/{instance_name}", response_model=UpdateGetResponse)
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
    instance_path = resolve_instance_path(instance_name)
    finded_name = instance_path.name

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    save_request(instance_path, request, request_class)

    response = compare(
        request=request,
        instance_manifest=instance_manifest,
        instance_name=finded_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )

    return response
