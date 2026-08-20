from pathlib import Path
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request

from fastapi.staticfiles import StaticFiles

from app.api.v1.models import ClientManifest
from app.api.v1.manifest import build_manifest, load_manifest, save_manifest
from app.api.v1.diff import compare
from app.main import INSTANCES_FOLDER_PATH

app = FastAPI(title="Minecraft Updater", version="1.0.0")
app.mount("/files", StaticFiles(directory=INSTANCES_FOLDER_PATH), name="files")


@app.post("/build/{instance}")
def build(instance: str):
    instance_path = INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    manifest = build_manifest(instance_path)
    save_manifest(instance_path, manifest)

    return {"status": "success", "version": manifest.version}


@app.post("/update/{instance}")
def update(instance: str, client_manifest: ClientManifest, request: Request):
    instance_path = INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    server_manifest = load_manifest(instance_path)
    if server_manifest is None:
        raise HTTPException(500, "Manifest missing")

    result = compare(
        instance, client_manifest, server_manifest, str(request.base_url).rstrip("/")
    )

    return result
