from pydantic import BaseModel


class ServerInfo(BaseModel):
    name: str
    ip: str
