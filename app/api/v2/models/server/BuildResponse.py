from pydantic import BaseModel

from api.v2.models.FileDownloadInfo import FileDownloadInfo
from api.v2.models.ServerInfo import ServerInfo


class BuildResponse(BaseModel):
    version: int
    new_files_paths: None | set[str]
    new_dirs_paths: None | set[str]
    new_strict_files_paths: None | set[str]
    new_strict_dirs_paths: None | set[str]
    new_resourcepacks: None | set[str]
    new_servers: None | list[ServerInfo]
    new_deleted: None | dict[str, str]  # name: path
    new_files: None | set[FileDownloadInfo]
