from pydantic import BaseModel

# ---------- File ----------


class ManifestFile(BaseModel):
    name: str
    path: str
    sha256: str
    size: int


# ---------- Server ----------


class ServerInfo(BaseModel):
    name: str
    ip: str


# ---------- Server Manifest ----------


class ServerManifest(BaseModel):
    version: int = 1
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: dict[str, ManifestFile]
    removed: dict[str, set[str]]
    servers: list[ServerInfo]
    resource_packs: list[str]


# ---------- Client Manifest ----------


class ClientManifest(BaseModel):
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: dict[str, ManifestFile]
    servers: list[ServerInfo]
    resource_packs: list[str]


# ---------- Download ----------


class DownloadFile(BaseModel):
    path: str
    sha256: str
    size: int
    url: str


# ---------- Update ----------


class UpdateResponse(BaseModel):
    version: int
    download: list[DownloadFile]
    delete: list[str]
    servers: list[ServerInfo]
    resource_packs: list[str]
