from pydantic import BaseModel


class MiuClientGetResponse(BaseModel):
    MiuClientFile: str
    PreLaunchCommand: str
    path: str
    url: str
    sha256: str
    size: int
