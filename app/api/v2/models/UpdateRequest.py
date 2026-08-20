from typing import Dict, List

from pydantic import BaseModel, Field

from FileInfo import FileInfo
from ServerInfo import ServerInfo


class UpdateRequest(BaseModel):
    resourcepacks: List[str] = Field(default_factory=list)
    servers: List[ServerInfo] = Field(default_factory=list)
    files: Dict[str, FileInfo]
