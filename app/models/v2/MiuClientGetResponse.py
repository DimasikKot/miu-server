from pydantic import BaseModel

from models.v2.FileDownloadInfo import FileDownloadInfo


class MiuClientGetResponse(BaseModel):
    pre_launch_command: str
    miu_client_path: str
    miu_client_file: FileDownloadInfo
    mmc_pack_path: str
    mmc_pack_file: FileDownloadInfo
