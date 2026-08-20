from typing import Dict, List

from pydantic import BaseModel, Field

from FileDownloadInfo import FileDownloadInfo
from ServerInfo import ServerInfo


class UpdateResponse(BaseModel):
    new_resourcepacks: Dict[str] = Field(default_factory=dict)
    new_servers: List[ServerInfo] = Field(default_factory=list)
    need_delete: Dict[str] = Field(default_factory=dict)
    need_download: Dict[FileDownloadInfo] = Field(default_factory=dict)
