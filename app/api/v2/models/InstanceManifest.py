from typing import Dict, List

from pydantic import BaseModel, Field

from FileInfo import FileInfo
from ServerInfo import ServerInfo


class InstanceManifest(BaseModel):
    version: int = 1
    files_paths: List[str] = Field(default_factory=list)
    dirs_paths: List[str] = Field(default_factory=list)
    strict_files_paths: List[str] = Field(default_factory=list)
    strict_dirs_paths: List[str] = Field(default_factory=list)
    resourcepacks: List[str] = Field(default_factory=list)
    servers: List[ServerInfo] = Field(default_factory=list)
    removed: Dict[str, List[str]] = Field(default_factory=dict)
    files: Dict[str, FileInfo] = Field(default_factory=dict)
