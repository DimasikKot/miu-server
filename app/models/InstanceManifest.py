from typing import Dict, List

from pydantic import BaseModel, Field

from app.models.FileInfo import FileInfo
from app.models.ServerInfo import ServerInfo


class InstanceManifest(BaseModel):
    version: int = 1
    pack: FileInfo | None
    instance: FileInfo | None
    files: Dict[str, FileInfo] = Field(default_factory=dict)
    removed: Dict[str, List[str]] = Field(default_factory=dict)
    servers: List[ServerInfo] = Field(default_factory=list)
    resource_packs: List[str] = Field(default_factory=list)
    FILES_PATHS
    FOLDERS_PATHS
    STRICT_FILES_PATHS
    STRICT_FOLDERS_PATHS
    resourcepacks: List[str] = Field(default_factory=list)
    servers: List[ServerInfo] = Field(default_factory=list)
    removed
    files
