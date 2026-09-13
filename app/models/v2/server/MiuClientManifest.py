from pydantic import BaseModel


class MiuClientManifest(BaseModel):
    MiuClientFile: str
    PreLaunchCommand: str
    path: str
    url: str
    sha256: str
    size: int
