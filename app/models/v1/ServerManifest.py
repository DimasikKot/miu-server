from pydantic import BaseModel

from models.v1.ManifestFile import ManifestFile
from models.v2.ServerInfo import ServerInfo


class ServerManifest(BaseModel):
    version: int
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: dict[str, ManifestFile]
    removed: dict[str, set[str]]
    servers: list[ServerInfo]
    resource_packs: list[str]
