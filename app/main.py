from pathlib import Path
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request

from fastapi.staticfiles import StaticFiles
from models import ManifestClient
from manifest import build_manifest, load_manifest, save_manifest
from diff import compare

FILES_DIR_PATH = Path("/istances")


app = FastAPI(title="PurMur Instances", version="1.1.0")
app.mount("/istances", StaticFiles(directory=FILES_DIR_PATH), name="istances")


@app.post("/build/{instance}")
def build(instance: str):
    instance_path = FILES_DIR_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    manifest = build_manifest(instance_path)
    save_manifest(instance_path, manifest)

    return {"status": "success", "version": manifest.version}


@app.post("/update/{instance}")
def update(instance: str, manifest_client: ManifestClient, request: Request):
    instance_path = FILES_DIR_PATH / instance
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")

    server_manifest = load_manifest(instance_path)
    if server_manifest is None:
        raise HTTPException(500, "Manifest missing")

    result = compare(
        instance, manifest_client, server_manifest, str(request.base_url).rstrip("/")
    )

    return result
