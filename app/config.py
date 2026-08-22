from functools import lru_cache
from pathlib import Path


class _Settings:
    MANIFEST_NAME = "manifest.json"
    MANIFEST_DIRS_NAME = "manifest_dirs.json"
    INSTANCES_DIR_PATH = Path("/instances")

    MIU_CLIENT_DIR_PATH = Path("/miu-client")
    MIU_CLIENT_MANIFEST_NAME = Path("manifest.json")


@lru_cache
def __get_settings__():
    return _Settings()


settings: _Settings = __get_settings__()
