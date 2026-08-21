from pydantic import BaseModel


class MiuClientResponse(BaseModel):
    path: str
    url: str
    sha256: str
    size: int
