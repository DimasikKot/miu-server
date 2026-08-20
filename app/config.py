from functools import lru_cache
from pathlib import Path


class _Settings():
    MANIFEST_NAME = "manifest.json"
    INSTANCES_FOLDER_PATH = Path("/istances")


@lru_cache
def __get_settings__():
    return _Settings()


settings: _Settings = __get_settings__()
