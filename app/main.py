from pathlib import Path
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request

from fastapi.staticfiles import StaticFiles

from models.UpdateRequest import UpdateRequest
from manifest import build_manifest, load_manifest, save_manifest
from diff import compare

MANIFEST_NAME = "manifest.json"

INSTANCES_FOLDER_PATH = Path("/istances")


app = FastAPI(title="PurMur Instances", version="1.1.0")
app.mount("/istances", StaticFiles(directory=INSTANCES_FOLDER_PATH), name="istances")


@app.post("/build/{instance}")
def build(instance: str):
    instance_path = INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    manifest = build_manifest(instance_path)
    save_manifest(instance_path, manifest)

    return {"status": "success", "version": manifest.version}


@app.post("/update/{instance}")
def update(instance: str, manifest_client: UpdateRequest, request: Request):
    instance_path = INSTANCES_FOLDER_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    server_manifest = load_manifest(instance_path)
    if server_manifest is None:
        raise HTTPException(500, "Manifest missing")

    result = compare(
        instance, manifest_client, server_manifest, str(request.base_url).rstrip("/")
    )

    return result
