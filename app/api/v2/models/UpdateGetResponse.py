from typing import Dict

from pydantic import BaseModel, Field


class UpdateGetResponse(BaseModel):
    files_paths: Dict[str] = Field(default_factory=dict)
    dirs_paths: Dict[str] = Field(default_factory=dict)
    strict_files_paths: Dict[str] = Field(default_factory=dict)
    strict_dirs_paths: Dict[str] = Field(default_factory=dict)
