from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Path, Request

from logic.build import sha256
from logic.miu_client import (
    load_miu_client_manifest,
    load_miu_client_settings_manifest,
    save_miu_client_manifest,
)

from logic.resolve_instance_path import resolve_instance_path
from models.MiuClientGetResponse import MiuClientGetResponse
from models.FileDownloadInfo import FileDownloadInfo
from models.server.MiuClientManifest import MiuClientManifest
from config import settings

router_miu_client: APIRouter = APIRouter()


def escape_pre_launch_command(command: str) -> str:
    return command.replace("\\", "\\\\").replace('"', '\\"')


@router_miu_client.get("/{instance_name}", response_model=MiuClientGetResponse)
def miu_client_get(
    request_class: Request,
    instance_name: str = Path(
        ...,
        description="PurMur Vanilla . . PurMur Create . . PurMur Homestead",
        example="PurMur Vanilla",
    ),
) -> MiuClientGetResponse:
    miu_client_manifest = load_miu_client_manifest()
    if miu_client_manifest is None:
        raise HTTPException(404, "Miu-Client manifest not found")

    instance_path = resolve_instance_path(instance_name)
    finded_name = instance_path.name
    mmc_pack_path = instance_path / "mmc-pack.json"
    if not instance_path.exists():
        raise HTTPException(404, "Instance not found")
    if not mmc_pack_path.exists():
        raise HTTPException(404, "Mmc-pack not found")

    relative = mmc_pack_path.relative_to(instance_path)
    download_url = f"{str(request_class.base_url).rstrip("/")}{settings.INSTANCES_DIR_PATH}/{quote(finded_name)}/{quote("mmc-pack.json", safe='/')}"

    return MiuClientGetResponse(
        pre_launch_command=escape_pre_launch_command(
            miu_client_manifest.PreLaunchCommand
        ),
        miu_client_path=miu_client_manifest.MiuClientFile,
        miu_client_file=FileDownloadInfo(
            url=miu_client_manifest.url,
            sha256=miu_client_manifest.sha256,
            size=miu_client_manifest.size,
        ),
        mmc_pack_path=str(relative),
        mmc_pack_file=FileDownloadInfo(
            sha256=sha256(mmc_pack_path),
            size=mmc_pack_path.stat().st_size,
            url=download_url,
        ),
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
