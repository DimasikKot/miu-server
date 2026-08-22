from functools import lru_cache
from pathlib import Path


class _Settings:
    INSTANCES_DIR_PATH = Path("/instances")
    MANIFEST_NAME = "manifest.json"
    MANIFEST_DIRS_NAME = "manifest_dirs.json"

    MIU_CLIENT_DIR_PATH = Path("/miu-client")
    MIU_CLIENT_MANIFEST_NAME = Path("manifest.json")
    MIU_CLIENT_SETTINGS_MANIFEST_NAME = Path("settings.json")


@lru_cache
def __get_settings__():
    return _Settings()


settings: _Settings = __get_settings__()
