from pydantic import BaseModel

from models.FileInfo import FileInfo
from models.ServerInfo import ServerInfo


class InstanceManifest(BaseModel):
    version: int
    api_version: int
    files_paths: set[str]
    dirs_paths: set[str]
    strict_files_paths: set[str]
    strict_dirs_paths: set[str]
    resourcepacks: list[str]
    servers: list[ServerInfo]
    deleted: dict[str, set[str]]  # Название: SHA
    files: dict[str, FileInfo]  # path: [FileInfo]
