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
    old = load_manifest(pack_path)
    files = scan_files(pack_path)

    removed = {}
    version = 1

    if old:
        version = old.version + 1
        removed = old.removed.copy()

        # сравнение старого и нового
        for path, old_file in old.files.items():
            # файл полностью удалили
            if path not in files:
                removed.setdefault(path, [])
                if old_file.sha256 not in removed[path]:
                    removed[path].append(old_file.sha256)
                continue

            # новый файл
            new_file = files[path]

            # файл изменился
            if new_file.sha256 != old_file.sha256:
                removed.setdefault(path, [])
                if old_file.sha256 not in removed[path]:
                    removed[path].append(old_file.sha256)

    # Очистка removed
    # если sha256 снова существует среди актуальных файлов,
    # он больше не является удалённым
    for path, hashes in list(removed.items()):
        if path in files:
            current_hash = files[path].sha256
            removed[path] = [h for h in hashes if h != current_hash]

        # если список пустой - удалить запись
        if not removed[path]:
            del removed[path]

    manifest = ServerManifest(
        version=version, files=files, removed=removed, servers=servers
    )

    save_manifest(pack_path, manifest)

    return manifest
