from pydantic import BaseModel

from api.v2.models.FileDownloadInfo import FileDownloadInfo
from api.v2.models.ServerInfo import ServerInfo


class ManifestFile(BaseModel):
    name: str
    path: str
    sha256: str
    size: int


class ClientManifest(BaseModel):
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: dict[str, ManifestFile]
    servers: list[ServerInfo]
    resource_packs: list[str]


class UpdateResponse(BaseModel):
    version: int
    download: list[FileDownloadInfo]
    delete: list[str]
    servers: list[ServerInfo]
    resource_packs: list[str]
