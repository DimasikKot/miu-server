from pydantic import BaseModel


class FileDownloadInfo(BaseModel):
    url: str
    path: str
    sha256: str
    size: int
