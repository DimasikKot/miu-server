from models.v1 import (
    ClientManifest,
    DownloadFile,
    ManifestFile,
    ServerManifest,
    UpdateResponse,
)
from models.v2 import (
    FileDownloadInfo,
    FileInfo,
    UpdatePostRequest,
    UpdatePostResponse,
)
from models.v2.server import InstanceManifest


def InstanceManifestV1toV2(data: ServerManifest) -> InstanceManifest:
    data_v2 = InstanceManifest(
        version=data.version,
        api_version=2,
        files_paths=set(),
        dirs_paths=set(),
        strict_files_paths=set(),
        strict_dirs_paths=set(),
        resourcepacks=data.resource_packs,
        incompatible_resourcepacks=[],
        servers=data.servers,
        deleted=data.removed,
        # transform FileInfoV1toV2
        files={file.path: FileInfoV1toV2(file) for file in data.files.values()},
    )

    return data_v2


def FileInfoV1toV2(data: ManifestFile) -> FileInfo:
    data_v2 = FileInfo(
        name=data.name,
        sha256=data.sha256,
        size=data.size,
    )

    return data_v2


def UpdatePostRequestV1toV2(data: ClientManifest) -> UpdatePostRequest:
    data_v2 = UpdatePostRequest(
        resourcepacks=data.resource_packs,
        incompatible_resourcepacks=[],
        servers=data.servers,
        # transform FileInfoV1toV2
        files={file.path: FileInfoV1toV2(file) for file in data.files.values()},
    )

    return data_v2


def FileDownloadInfoV2toV1(path: str, data: FileDownloadInfo) -> DownloadFile:
    data_v1 = DownloadFile(
        path=path,
        sha256=data.sha256,
        size=data.size,
        url=data.url,
    )

    return data_v1


def UpdatePostResponseV2toV1(data: UpdatePostResponse) -> UpdateResponse:
    old_dirs_paths = {
        "minecraft/config",
        "minecraft/mods",
        "minecraft/resourcepacks",
        "minecraft/xaero",
    }

    data_v1 = UpdateResponse(
        version=0,
        download=[
            FileDownloadInfoV2toV1(file_path, file)
            for file_path, file in data.need_download.items()
            if any(file_path.startswith(path) for path in old_dirs_paths)
        ],
        delete=list(data.need_delete),
        servers=list(data.new_servers),
        resource_packs=list(data.new_resourcepacks),
    )

    return data_v1
