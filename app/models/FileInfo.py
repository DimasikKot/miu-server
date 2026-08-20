from pydantic import BaseModel


class FileInfo(BaseModel):
    name: str
    path: str
    sha256: str
    size: int
