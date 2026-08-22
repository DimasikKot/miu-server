from pydantic import BaseModel


class MiuClientSettingsManifest(BaseModel):
    MiuClientFile: str
    PreLaunchCommand: str
