from typing import List

from pydantic import BaseModel, Field

from FileDownloadInfo import FileDownloadInfo
from ServerInfo import ServerInfo


class UpdateResponse(BaseModel):
    version: int
    download: List[FileDownloadInfo]
    delete: List[str]
    servers: List[ServerInfo]
    resource_packs: List[str] = Field(default_factory=list)
