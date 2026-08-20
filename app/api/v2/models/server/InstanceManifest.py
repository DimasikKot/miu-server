from typing import Dict, List

from pydantic import BaseModel, Field

from app.api.v2.models.FileInfo import FileInfo
from app.api.v2.models.ServerInfo import ServerInfo


class InstanceManifest(BaseModel):
    version: int = 1
    files_paths: Dict[str] = Field(default_factory=dict)
    dirs_paths: Dict[str] = Field(default_factory=dict)
    strict_files_paths: Dict[str] = Field(default_factory=dict)
    strict_dirs_paths: Dict[str] = Field(default_factory=dict)
    resourcepacks: Dict[str] = Field(default_factory=dict)
    servers: List[ServerInfo] = Field(default_factory=list)
    deleted: Dict[str, Dict[str]] = Field(default_factory=dict)  # Название: SHA
    files: Dict[FileInfo] = Field(default_factory=dict)
