from pydantic import BaseModel


class FileDownloadInfo(BaseModel):
    url: str
    sha256: str
    size: int
