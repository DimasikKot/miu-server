from pydantic import BaseModel

from models.v1.DownloadFile import DownloadFile
from models.v2.ServerInfo import ServerInfo


class UpdateResponse(BaseModel):
    version: int
    download: list[DownloadFile]
    delete: list[str]
    servers: list[ServerInfo]
    resource_packs: list[str]
