from typing import Dict, List
from pydantic import BaseModel, Field


class File(BaseModel):
    name: str
    path: str
    sha256: str
    size: int


class Server(BaseModel):
    name: str
    ip: str


class ManifestServer(BaseModel):
    version: int = 1
    pack: File | None
    instance: File | None
    files: Dict[str, File] = Field(default_factory=dict)
    removed: Dict[str, List[str]] = Field(default_factory=dict)
    servers: List[Server] = Field(default_factory=list)
    resource_packs: List[str] = Field(default_factory=list)


class ManifestClient(BaseModel):
    pack: File | None
    instance: File | None
    files: Dict[str, File]
    servers: List[Server] = Field(default_factory=list)
    resource_packs: List[str] = Field(default_factory=list)


class FileDownload(BaseModel):
    path: str
    sha256: str
    size: int
    url: str


class UpdateResponse(BaseModel):
    version: int
    download: List[FileDownload]
    delete: List[str]
    servers: List[Server]
    resource_packs: List[str] = Field(default_factory=list)
