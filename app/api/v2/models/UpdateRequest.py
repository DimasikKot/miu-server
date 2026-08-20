from typing import Dict, List

from pydantic import BaseModel, Field

from FileInfo import FileInfo
from ServerInfo import ServerInfo


class UpdateRequest(BaseModel):
    resourcepacks: Dict[str] = Field(default_factory=dict)
    servers: List[ServerInfo] = Field(default_factory=list)
    files: Dict[FileInfo] = Field(default_factory=dict)
