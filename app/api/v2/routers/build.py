from fastapi import APIRouter, HTTPException

from api.v2.manifest import build_manifest, save_manifest
from main import INSTANCES_FOLDER_PATH

router_build: APIRouter = APIRouter()


@router_build.post("/{instance}")
def router_build(instance: str):
    instance_path = INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    manifest = build_manifest(instance_path)
    save_manifest(instance_path, manifest)

    return {"status": "success", "version": manifest.version}
