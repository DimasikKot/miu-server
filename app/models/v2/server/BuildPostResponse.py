from pydantic import BaseModel, Field

from models.v2.ServerInfo import ServerInfo


class BuildPostResponse(BaseModel):
    version: int
    api_version: int

    new_files_paths: set[str] = Field(default_factory=set)
    new_dirs_paths: set[str] = Field(default_factory=set)
    new_strict_files_paths: set[str] = Field(default_factory=set)
    new_strict_dirs_paths: set[str] = Field(default_factory=set)
    new_resourcepacks: list[str] = Field(default_factory=list)
    new_incompatible_resourcepacks: list[str] = Field(default_factory=list)
    new_servers: list[ServerInfo] = Field(default_factory=list[ServerInfo])
    files_added: dict[str, str] = Field(default_factory=dict)
