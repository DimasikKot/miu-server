from fastapi import APIRouter, HTTPException, Path, Request

from api.v1.models import ClientManifest, UpdateResponse
from api.v1.transformV1toV2 import UpdatePostRequestV1toV2, UpdatePostResponseV2toV1
from logic.resolve_instance_path import resolve_instance_path
from logic.update import compare
from logic.build import load_manifest

router_v1: APIRouter = APIRouter()


@router_v1.post("/update/{instance_name}", response_model=UpdateResponse)
def update(
    request: ClientManifest,
    request_class: Request,
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> UpdateResponse:
    request_v2 = UpdatePostRequestV1toV2(data=request)

    instance_path = resolve_instance_path(instance_name)
    finded_name = instance_path.name

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    response = compare(
        request=request_v2,
        instance_manifest=instance_manifest,
        instance_name=finded_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )

    return UpdateResponse.model_validate(UpdatePostResponseV2toV1(response))
