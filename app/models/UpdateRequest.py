from typing import Dict, List

from pydantic import BaseModel, Field

from app.models.FileInfo import FileInfo
from app.models.ServerInfo import ServerInfo


class UpdateRequest(BaseModel):
    pack: FileInfo | None
    instance: FileInfo | None
    files: Dict[str, FileInfo]
    servers: List[ServerInfo] = Field(default_factory=list)
    resource_packs: List[str] = Field(default_factory=list)
