from pydantic import BaseModel

from models.FileDownloadInfo import FileDownloadInfo
from models.ServerInfo import ServerInfo


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


class ServerManifest(BaseModel):
    version: int
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: dict[str, ManifestFile]
    removed: dict[str, set[str]]
    servers: list[ServerInfo]
    resource_packs: list[str]


class UpdateResponse(BaseModel):
    version: int
    download: list[FileDownloadInfo]
    delete: list[str]
    servers: list[ServerInfo]
    resource_packs: list[str]
