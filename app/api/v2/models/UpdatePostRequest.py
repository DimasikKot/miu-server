from pydantic import BaseModel

from api.v2.models.FileInfo import FileInfo
from api.v2.models.ServerInfo import ServerInfo


class UpdatePostRequest(BaseModel):
    resourcepacks: set[str]
    servers: list[ServerInfo]
    files: set[FileInfo]
