from typing import Dict, List
from pydantic import BaseModel, Field

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
    files: Dict[str, ManifestFile] = Field(default_factory=dict)
    removed: Dict[str, List[str]] = Field(default_factory=dict)
    servers: List[ServerInfo] = Field(default_factory=list)
    resource_packs: List[str] = Field(default_factory=list)


# ---------- Client Manifest ----------


class ClientManifest(BaseModel):
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: Dict[str, ManifestFile]
    servers: List[ServerInfo] = Field(default_factory=list)
    resource_packs: List[str] = Field(default_factory=list)


# ---------- Download ----------


class DownloadFile(BaseModel):
    path: str
    sha256: str
    size: int
    url: str


# ---------- Update ----------


class UpdateResponse(BaseModel):
    version: int
    download: List[DownloadFile]
    delete: List[str]
    servers: List[ServerInfo]
    resource_packs: List[str] = Field(default_factory=list)
