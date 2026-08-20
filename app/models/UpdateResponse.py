from typing import List

from pydantic import BaseModel, Field

from app.models.FileDownloadInfo import FileDownloadInfo
from app.models.ServerInfo import ServerInfo


class UpdateResponse(BaseModel):
    version: int
    download: List[FileDownloadInfo]
    delete: List[str]
    servers: List[ServerInfo]
    resource_packs: List[str] = Field(default_factory=list)
