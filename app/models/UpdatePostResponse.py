from pydantic import BaseModel

from models.FileDownloadInfo import FileDownloadInfo
from models.ServerInfo import ServerInfo


class UpdatePostResponse(BaseModel):
    new_resourcepacks: set[str]
    new_servers: list[ServerInfo]
    need_delete: set[str]
    need_download: dict[str, FileDownloadInfo]
