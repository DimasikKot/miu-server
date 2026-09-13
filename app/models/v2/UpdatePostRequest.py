from pydantic import BaseModel

from models.v2.FileInfo import FileInfo
from models.v2.ServerInfo import ServerInfo


class UpdatePostRequest(BaseModel):
    resourcepacks: list[str]
    incompatible_resourcepacks: list[str]
    servers: list[ServerInfo]
    files: dict[str, FileInfo]  # path: [FileInfo]
