import hashlib
import json
from pathlib import Path

from models import ManifestFile, ServerManifest

MANIFEST_NAME = "manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_files(pack_path: Path):
    result = {}
    folders = ["mods", "resourcepacks", "xaero"]

    for folder in folders:
        current = pack_path / folder
        if not current.exists():
            continue

        for file in current.rglob("*"):
            if not file.is_file():
                continue

            relative = file.relative_to(pack_path)

            result[str(relative)] = ManifestFile(
                name=file.name,
                path=str(relative),
                sha256=sha256(file),
                size=file.stat().st_size,
            )

    return result


def load_manifest(pack_path: Path):
    file = pack_path / MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        return ServerManifest.model_validate(json.load(f))


def save_manifest(pack_path: Path, manifest: ServerManifest):
    with open(pack_path / MANIFEST_NAME, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)


def build_manifest(pack_path: Path, servers):
    old_manifest = load_manifest(pack_path)
    new_files = scan_files(pack_path)

    removed = {}
    version = 1

    if old_manifest:
        version = old_manifest.version + 1
        removed = old_manifest.removed.copy()

        # сравнение старого и нового
        for old_path, old_file in old_manifest.files.items():

            # файл полностью удалили
            if old_path not in new_files:
                removed.setdefault(old_path, [])
                if old_file.sha256 not in removed[old_path]:
                    removed[old_path].append(old_file.sha256)
                continue

            # новый файл
            new_file = new_files[old_path]

            # файл изменился
            if new_file.sha256 != old_file.sha256:
                removed.setdefault(old_path, [])
                if old_file.sha256 not in removed[old_path]:
                    removed[old_path].append(old_file.sha256)

    # Очистка removed

    # если sha256 снова существует среди актуальных файлов,
    # он больше не является удалённым
    for old_path, old_hashes in list(removed.items()):
        if old_path in new_files:
            current_hash = new_files[old_path].sha256
            removed[old_path] = [h for h in old_hashes if h != current_hash]

        # если список пустой - удалить запись
        if not removed[old_path]:
            del removed[old_path]

    new_manifest = ServerManifest(
        version=version, files=new_files, removed=removed, servers=servers
    )

    save_manifest(pack_path, new_manifest)

    return new_manifest
