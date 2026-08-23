from pydantic import BaseModel

from models.ServerInfo import ServerInfo


class BuildPostResponse(BaseModel):
    version: int
    api_version: int
    new_files_paths: set[str]
    new_dirs_paths: set[str]
    new_strict_files_paths: set[str]
    new_strict_dirs_paths: set[str]
    new_resourcepacks: list[str]
    new_incompatible_resourcepacks: list[str]
    new_servers: list[ServerInfo]
    files_deleted: dict[str, str]  # path: sha256
    files_edited: dict[str, str]
    files_added: dict[str, str]
