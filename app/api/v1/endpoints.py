from fastapi import APIRouter, HTTPException, Request

from api.v1.models import ClientManifest
from api.v1.manifest import build_manifest, load_manifest, save_manifest
from api.v1.diff import compare
from config import settings

router_v1: APIRouter = APIRouter()


@router_v1.post("/build/{instance}")
def build(instance: str):
    instance_path = settings.INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    manifest = build_manifest(instance_path)
    save_manifest(instance_path, manifest)

    return {"status": "success", "version": manifest.version}


@router_v1.post("/update/{instance}")
def update(instance: str, client_manifest: ClientManifest, request: Request):
    instance_path = settings.INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    server_manifest = load_manifest(instance_path)
    if server_manifest is None:
        raise HTTPException(500, "Manifest missing")

    result = compare(
        instance, client_manifest, server_manifest, str(request.base_url).rstrip("/")
    )

    return result
