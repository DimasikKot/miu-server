from pydantic import BaseModel


class ManifestFile(BaseModel):
    name: str
    path: str
    sha256: str
    size: int
