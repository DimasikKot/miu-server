from typing import Dict, List

from pydantic import BaseModel, Field

from api.v2.models.FileDownloadInfo import FileDownloadInfo
from api.v2.models.ServerInfo import ServerInfo


class BuildResponse(BaseModel):
    version: int
    new_files_paths: None | Dict[str] = Field(default_factory=dict)
    new_dirs_paths: None | Dict[str] = Field(default_factory=dict)
    new_strict_files_paths: None | Dict[str] = Field(default_factory=dict)
    new_strict_dirs_paths: None | Dict[str] = Field(default_factory=dict)
    new_resourcepacks: None | Dict[str] = Field(default_factory=dict)
    new_servers: None | List[ServerInfo] = Field(default_factory=list)
    new_deleted: None | Dict[str, str] = Field(default_factory=dict)  # name: path
    new_files: None | Dict[FileDownloadInfo] = Field(default_factory=dict)
