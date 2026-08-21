from pydantic import BaseModel

from api.v2.models.FileDownloadInfo import FileDownloadInfo
from api.v2.models.ServerInfo import ServerInfo


class UpdatePostResponse(BaseModel):
    new_resourcepacks: set[str]
    new_servers: list[ServerInfo]
    need_delete: set[str]
    need_download: set[FileDownloadInfo]
