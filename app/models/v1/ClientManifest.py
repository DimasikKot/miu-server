from pydantic import BaseModel

from models.v1.ManifestFile import ManifestFile
from models.v2.ServerInfo import ServerInfo


class ClientManifest(BaseModel):
    pack: ManifestFile | None
    instance: ManifestFile | None
    files: dict[str, ManifestFile]
    servers: list[ServerInfo]
    resource_packs: list[str]
