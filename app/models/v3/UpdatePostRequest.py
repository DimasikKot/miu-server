from pydantic import BaseModel

from models.v2.FileInfo import FileInfo
from models.v2.ServerInfo import ServerInfo
from models.v3.Waypoint import Waypoint


class UpdatePostRequest(BaseModel):
    resourcepacks: list[str]
    incompatible_resourcepacks: list[str]
    servers: list[ServerInfo]
    waypoints: dict[str, list[Waypoint]]
    files: dict[str, FileInfo]  # path: [FileInfo]
