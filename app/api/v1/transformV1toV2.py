from api.v1.models import ClientManifest, ManifestFile, ServerManifest, UpdateResponse
from models.FileInfo import FileInfo
from models.UpdatePostRequest import UpdatePostRequest
from models.UpdatePostResponse import UpdatePostResponse
from models.server.InstanceManifest import InstanceManifest


def InstanceManifestV1toV2(data: ServerManifest) -> InstanceManifest:
    # TODO add files and strict
    data_v2 = InstanceManifest(
        version=data.version,
        api_version=2,
        files_paths=set(),
        dirs_paths=set(),
        strict_files_paths=set(),
        strict_dirs_paths=set(),
        resourcepacks=set(data.resource_packs),
        servers=data.servers,
        deleted=data.removed,
        # transform FileInfoV1toV2
        files={file.name: FileInfoV1toV2(file) for file in data.files.values()},
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
        resourcepacks=set(data.resource_packs),
        servers=data.servers,
        # transform FileInfoV1toV2
        files={file.name: FileInfoV1toV2(file) for file in data.files.values()},
    )

    return data_v2


def UpdatePostResponseV2toV1(data: UpdatePostResponse) -> UpdateResponse:
    data_v1 = UpdateResponse(
        version=0,
        download=list(data.need_download),
        delete=list(data.need_delete),
        servers=list(data.new_servers),
        resource_packs=list(data.new_resourcepacks),
    )

    return data_v1
