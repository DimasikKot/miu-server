from pydantic import BaseModel

from models.v2 import FileInfo
from models.v2 import ServerInfo
from models.v3 import Waypoint


class InstanceManifest(BaseModel):
    version: int
    api_version: int
    files_paths: set[str]
    dirs_paths: set[str]
    strict_files_paths: set[str]
    strict_dirs_paths: set[str]
    resourcepacks: list[str]
    incompatible_resourcepacks: list[str]
    servers: list[ServerInfo]
    waypoints: dict[str, list[Waypoint]]
    deleted: dict[str, set[str]]  # Название: SHA
    files: dict[str, FileInfo]  # path: [FileInfo]
