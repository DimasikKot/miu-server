from pydantic import BaseModel


class FileInfo(BaseModel):
    name: str
    sha256: str
    size: int
