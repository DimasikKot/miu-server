from pydantic import BaseModel


class MiuClientManifest(BaseModel):
    MiuClientFile: str
    PreLaunchCommand: str
