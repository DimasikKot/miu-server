from pydantic import BaseModel

from models.FileInfo import FileInfo
from models.ServerInfo import ServerInfo


class UpdatePostRequest(BaseModel):
    resourcepacks: set[str]
    servers: list[ServerInfo]
    files: set[FileInfo]
