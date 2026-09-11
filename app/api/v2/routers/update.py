import re

from fastapi import APIRouter, HTTPException, Path, Request

from config import settings
from logic.update import compare
from logic.build import load_manifest
from models.UpdateGetResponse import UpdateGetResponse
from models.UpdatePostRequest import UpdatePostRequest
from models.UpdatePostResponse import UpdatePostResponse

router_update: APIRouter = APIRouter()


@router_update.get("/{instance_name}", response_model=UpdateGetResponse)
def update_get(
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> UpdateGetResponse:
    instance_path = settings.INSTANCES_DIR_PATH / instance_name
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    return UpdateGetResponse(
        files_paths=instance_manifest.files_paths,
        dirs_paths=instance_manifest.dirs_paths,
        strict_files_paths=instance_manifest.strict_files_paths,
        strict_dirs_paths=instance_manifest.strict_dirs_paths,
    )


def canon(s: str) -> str:
    # убираем пробелы и приводим к нижнему регистру
    return re.sub(r"\s+", "", s).lower()


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
    # 1. точное совпадение
    instance_path = settings.INSTANCES_DIR_PATH / instance_name

    # 2. префиксный поиск
    if not instance_path.exists():
        req = canon(instance_name)
        matches = [
            p
            for p in settings.INSTANCES_DIR_PATH.iterdir()
            if p.is_dir() and req.startswith(canon(p.name))
        ]

        if not matches:
            raise HTTPException(404, "Instance not found")

        # самая короткая = ближе всего к оригиналу
        matches.sort(key=lambda p: len(p.name))
        instance_path = matches[0]

    # фактическое имя найденной папки (например "PurMur Create (1)")
    finded_name = instance_path.name

    instance_manifest = load_manifest(instance_path)
    if instance_manifest is None:
        raise HTTPException(500, "Manifest missing")

    response = compare(
        request=request,
        instance_manifest=instance_manifest,
        instance_name=finded_name,
        base_url=str(request_class.base_url).rstrip("/"),
    )

    return response
