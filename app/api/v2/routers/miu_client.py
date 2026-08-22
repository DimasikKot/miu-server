from fastapi import APIRouter, HTTPException, Request

from logic.build import sha256
from logic.miu_client import (
    load_miu_client_manifest,
    load_miu_client_settings_manifest,
    save_miu_client_manifest,
)
from models.MiuClientManifest import MiuClientManifest
from config import settings

router_miu_client: APIRouter = APIRouter()


@router_miu_client.get("", response_model=MiuClientManifest)
def miu_client_get() -> MiuClientManifest:
    miu_client_manifest = load_miu_client_manifest()
    if miu_client_manifest is None:
        raise HTTPException(404, "Miu-Client manifest not found")

    return MiuClientManifest(
        MiuClientFile=miu_client_manifest.MiuClientFile,
        PreLaunchCommand=miu_client_manifest.PreLaunchCommand,
        path=miu_client_manifest.MiuClientFile,
        url=miu_client_manifest.url,
        sha256=miu_client_manifest.sha256,
        size=miu_client_manifest.size,
    )


@router_miu_client.post("", response_model=MiuClientManifest)
def miu_client_post(request_class: Request) -> MiuClientManifest:
    miu_client_settings_manifest = load_miu_client_settings_manifest()
    if miu_client_settings_manifest is None:
        raise HTTPException(404, "Miu-Client settings manifest not found")

    miu_client_file_path = (
        settings.MIU_CLIENT_DIR_PATH / miu_client_settings_manifest.MiuClientFile
    )

    if not miu_client_file_path.exists():
        raise HTTPException(404, "Miu-Client not found")

    new_sha256 = sha256(miu_client_file_path)
    new_size = miu_client_file_path.stat().st_size

    new_manifest = MiuClientManifest(
        MiuClientFile=miu_client_settings_manifest.MiuClientFile,
        PreLaunchCommand=miu_client_settings_manifest.PreLaunchCommand,
        path=miu_client_settings_manifest.MiuClientFile,
        url=str(request_class.base_url).rstrip("/") + str(miu_client_file_path),
        sha256=new_sha256,
        size=new_size,
    )

    save_miu_client_manifest(new_manifest)

    return new_manifest
