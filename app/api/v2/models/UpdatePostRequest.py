from typing import Dict, List

from pydantic import BaseModel, Field

from api.v2.models.FileInfo import FileInfo
from api.v2.models.ServerInfo import ServerInfo


class UpdatePostRequest(BaseModel):
    resourcepacks: Dict[str] = Field(default_factory=dict)
    servers: List[ServerInfo] = Field(default_factory=list)
    files: Dict[FileInfo] = Field(default_factory=dict)
