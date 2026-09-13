from pydantic import BaseModel


class DownloadFile(BaseModel):
    path: str
    sha256: str
    size: int
    url: str
