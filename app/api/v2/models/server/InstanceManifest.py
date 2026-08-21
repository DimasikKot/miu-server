from pydantic import BaseModel

from api.v2.models.FileInfo import FileInfo
from api.v2.models.ServerInfo import ServerInfo


class InstanceManifest(BaseModel):
    version: int = 1
    files_paths: set[str]
    dirs_paths: set[str]
    strict_files_paths: set[str]
    strict_dirs_paths: set[str]
    resourcepacks: set[str]
    servers: list[ServerInfo]
    deleted: dict[str, set[str]]  # Название: SHA
    files: set[FileInfo]
