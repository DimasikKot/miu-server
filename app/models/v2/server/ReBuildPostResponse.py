from pydantic import BaseModel, Field

from models.v2 import ServerInfo


class ReBuildPostResponse(BaseModel):
    version: int
    api_version: int

    new_files_paths: set[str] = Field(default_factory=set)
    del_files_paths: set[str] = Field(default_factory=set)
    new_dirs_paths: set[str] = Field(default_factory=set)
    del_dirs_paths: set[str] = Field(default_factory=set)
    new_strict_files_paths: set[str] = Field(default_factory=set)
    del_strict_files_paths: set[str] = Field(default_factory=set)
    new_strict_dirs_paths: set[str] = Field(default_factory=set)
    del_strict_dirs_paths: set[str] = Field(default_factory=set)
    new_resourcepacks: list[str] = Field(default_factory=list)
    del_resourcepacks: list[str] = Field(default_factory=list)
    new_incompatible_resourcepacks: list[str] = Field(default_factory=list)
    del_incompatible_resourcepacks: list[str] = Field(default_factory=list)
    new_servers: list[ServerInfo] = Field(default_factory=list[ServerInfo])
    del_servers: list[ServerInfo] = Field(default_factory=list[ServerInfo])
    files_deleted: dict[str, str] = Field(default_factory=dict)  # path: sha256
    files_strict_deleted: dict[str, str] = Field(default_factory=dict)
    files_edited: dict[str, str] = Field(default_factory=dict)
    files_strict_edited: dict[str, str] = Field(default_factory=dict)
    files_added: dict[str, str] = Field(default_factory=dict)
