import json


from config import settings
from models.v2.server import MiuClientManifest, MiuClientSettingsManifest


def load_miu_client_manifest() -> MiuClientManifest | None:
    file = settings.MIU_CLIENT_DIR_PATH / settings.MIU_CLIENT_MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        return MiuClientManifest.model_validate(manifest_json)


def load_miu_client_settings_manifest() -> MiuClientSettingsManifest | None:
    file = settings.MIU_CLIENT_DIR_PATH / settings.MIU_CLIENT_SETTINGS_MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        return MiuClientSettingsManifest.model_validate(manifest_json)


def save_miu_client_manifest(manifest: MiuClientManifest):
    with open(
        settings.MIU_CLIENT_DIR_PATH / settings.MIU_CLIENT_MANIFEST_NAME,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)
