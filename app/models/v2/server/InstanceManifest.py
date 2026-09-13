from pydantic import BaseModel

from models.v2.FileInfo import FileInfo
from models.v2.ServerInfo import ServerInfo


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
    deleted: dict[str, set[str]]  # Название: SHA
    files: dict[str, FileInfo]  # path: [FileInfo]
