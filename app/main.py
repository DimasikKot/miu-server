from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request

from fastapi.staticfiles import StaticFiles

from models import (
    ClientManifest,
    MinecraftInfo
)

from manifest import (
    build_manifest,
    load_manifest,
    save_manifest
)

from diff import compare


FILES_DIR = Path("/files")


app = FastAPI(
    title="Minecraft Updater",
    version="0.1"
)


app.mount(
    "/files",
    StaticFiles(directory=FILES_DIR),
    name="files"
)


@app.get("/")
def root():

    return {
        "status": "ok"
    }


@app.get("/manifest/{pack}")
def manifest(pack: str):

    path = FILES_DIR / pack

    if not path.exists():
        raise HTTPException(
            404,
            "Pack not found"
        )

    manifest = load_manifest(path)

    if manifest is None:
        raise HTTPException(
            404,
            "Manifest not found"
        )

    return manifest


@app.post("/build/{pack}")
def build(pack: str):

    pack_path = FILES_DIR / pack

    if not pack_path.exists():
        raise HTTPException(
            404,
            "Pack not found"
        )

    #
    # Пока захардкодим.
    # Потом будет читаться из instance.json
    #

    minecraft = MinecraftInfo(

        version="1.21.1",

        loader="fabric",

        loader_version="0.17.2"

    )

    servers = []

    manifest = build_manifest(

        pack_path,

        minecraft,

        servers

    )

    save_manifest(
        pack_path,
        manifest
    )

    return {
        "status": "rebuilt",
        "version": manifest.version
    }


@app.post("/update/{pack}")
def update(
    pack: str,
    client: ClientManifest,
    request: Request
):

    pack_path = FILES_DIR / pack

    if not pack_path.exists():
        raise HTTPException(
            404,
            "Pack not found"
        )

    server = load_manifest(pack_path)

    if server is None:
        raise HTTPException(
            500,
            "Manifest missing"
        )
    
    result = compare(
        pack,
        client,
        server,
        str(request.base_url).rstrip("/")
    )

    return result
