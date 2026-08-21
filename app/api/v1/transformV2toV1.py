from api.v1.models import ClientManifest, ManifestFile, UpdateResponse
from models.FileInfo import FileInfo
from models.UpdatePostRequest import UpdatePostRequest
from models.UpdatePostResponse import UpdatePostResponse


def FileInfoV2toV1(data: ManifestFile) -> FileInfo:
    data_v1 = FileInfo(
        name=data.name,
        path=data.path,
        sha256=data.sha256,
        size=data.size,
    )

    return FileInfo.model_validate(data_v1)


def UpdatePostRequestV1toV2(data: ClientManifest) -> UpdatePostRequest:
    data_v2 = UpdatePostRequest(
        resourcepacks=set(data.resource_packs),
        servers=data.servers,
        files=set(map(FileInfoV2toV1, data.files.values())),  # transform FileInfoV2toV1
    )

    return UpdatePostRequest.model_validate(data_v2)


def UpdatePostResponseV2toV1(data: UpdatePostResponse) -> UpdateResponse:
    data_v1 = UpdateResponse(
        version=0,
        download=list(data.need_download),
        delete=list(data.need_delete),
        servers=list(data.new_servers),
        resource_packs=list(data.new_resourcepacks),
    )

    return UpdateResponse.model_validate(data_v1)
