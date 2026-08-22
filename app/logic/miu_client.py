import json

from models.server.MiuClientManifest import MiuClientManifest
from config import settings


def load_miu_client_manifest() -> MiuClientManifest | None:
    file = settings.MIU_CLIENT_DIR_PATH / settings.MIU_CLIENT_MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        return MiuClientManifest.model_validate(manifest_json)
