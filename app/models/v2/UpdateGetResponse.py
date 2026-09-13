from pydantic import BaseModel


class UpdateGetResponse(BaseModel):
    files_paths: set[str]
    dirs_paths: set[str]
    strict_files_paths: set[str]
    strict_dirs_paths: set[str]
