from fastapi import APIRouter, HTTPException, Path, Request

from api.v2.transformV2toV3 import UpdatePostRequestV2toV3, UpdatePostResponseV3toV2
from models.v1 import ClientManifest, UpdateResponse
from api.v1.transformV1toV2 import UpdatePostRequestV1toV2, UpdatePostResponseV2toV1
from logic.resolve_instance_path import resolve_instance_path
from logic.update import compare
from logic.build import load_manifest

router_v1: APIRouter = APIRouter()


@router_v1.post("/update/{instance_name}", response_model=UpdateResponse)
def update(
    request_v1: ClientManifest,
    request_class: Request,
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> UpdateResponse:
    request_v2 = UpdatePostRequestV1toV2(data=request_v1)
    request_v3 = UpdatePostRequestV2toV3(data=request_v2)

    instance_path = resolve_instance_path(instance_name)
    finded_name = instance_path.name

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    response_v3 = compare(
        request=request_v3,
        instance_manifest=instance_manifest,
        instance_name=finded_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )
    response_v2 = UpdatePostResponseV3toV2(response_v3)
    response_v1 = UpdatePostResponseV2toV1(response_v2)

    return UpdateResponse.model_validate(response_v1)
