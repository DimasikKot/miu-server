from pydantic import BaseModel

from models.ServerInfo import ServerInfo


class BuildPostResponse(BaseModel):
    version: int
    new_files_paths: set[str]
    new_dirs_paths: set[str]
    new_strict_files_paths: set[str]
    new_strict_dirs_paths: set[str]
    new_resourcepacks: set[str]
    new_servers: list[ServerInfo]
    files_deleted: dict[str, str]  # name: path
    files_edited: dict[str, str]
    files_added: dict[str, str]
