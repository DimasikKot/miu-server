from typing import Dict, List

from pydantic import BaseModel, Field

from models.FileInfo import FileInfo
from models.ServerInfo import ServerInfo


class UpdateRequest(BaseModel):
    resourcepacks: List[str] = Field(default_factory=list)
    servers: List[ServerInfo] = Field(default_factory=list)
    files: Dict[str, FileInfo]
