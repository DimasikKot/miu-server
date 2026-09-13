from pydantic import BaseModel

from models.v2.FileDownloadInfo import FileDownloadInfo
from models.v2.ServerInfo import ServerInfo
from models.v3.Waypoint import Waypoint


class UpdatePostResponse(BaseModel):
    new_resourcepacks: list[str]
    new_incompatible_resourcepacks: list[str]
    new_servers: list[ServerInfo]
    new_waypoints: dict[str, list[Waypoint]]
    need_delete: set[str]
    need_download: dict[str, FileDownloadInfo]
