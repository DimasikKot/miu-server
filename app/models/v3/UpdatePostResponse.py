from pydantic import BaseModel

from models.v2.FileDownloadInfo import FileDownloadInfo
from models.v2.ServerInfo import ServerInfo


class UpdatePostResponse(BaseModel):
    new_resourcepacks: list[str]
    new_incompatible_resourcepacks: list[str]
    new_servers: list[ServerInfo]
    need_delete: set[str]
    need_download: dict[str, FileDownloadInfo]
