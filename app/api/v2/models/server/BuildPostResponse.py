from pydantic import BaseModel

from api.v2.models.FileInfo import FileInfo
from api.v2.models.ServerInfo import ServerInfo


class BuildPostResponse(BaseModel):
    version: int
    new_files_paths: set[str]
    new_dirs_paths: set[str]
    new_strict_files_paths: set[str]
    new_strict_dirs_paths: set[str]
    new_resourcepacks: set[str]
    new_servers: list[ServerInfo]
    new_deleted: dict[str, str]  # name: path
    new_files: set[FileInfo]
