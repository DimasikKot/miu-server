from fastapi import APIRouter, HTTPException, Path, Request

from api.v2.transformV2toV3 import UpdatePostRequestV2toV3, UpdatePostResponseV3toV2
from logic.resolve_instance_path import resolve_instance_path
from logic.save_request import save_request
from logic.update import compare
from logic.build import load_manifest
from models.v2 import UpdatePostRequest, UpdatePostResponse

router_update_post: APIRouter = APIRouter()


@router_update_post.post("/{instance_name}", response_model=UpdatePostResponse)
def update_post(
    request_v2: UpdatePostRequest,
    request_class: Request,
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> UpdatePostResponse:
    request_v3 = UpdatePostRequestV2toV3(data=request_v2)

    instance_path = resolve_instance_path(instance_name)
    finded_name = instance_path.name

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    save_request(instance_path, request_v3, request_class)

    response_v3 = compare(
        request=request_v3,
        instance_manifest=instance_manifest,
        instance_name=finded_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )
    response_v2 = UpdatePostResponseV3toV2(response_v3)

    return UpdatePostResponse.model_validate(response_v2)
