import hashlib
import json
from pathlib import Path

from fastapi import HTTPException

from api.v1.models import ServerManifest
from api.v1.transformV1toV2 import InstanceManifestV1toV2
from logic.get_servers import get_servers
from models.FileInfo import FileInfo
from models.server.BuildPostResponse import BuildPostResponse
from models.server.InstanceManifest import InstanceManifest
from config import settings
from models.server.InstanceManifestDirs import InstanceManifestDirs


def load_manifest(instance_path: Path) -> InstanceManifest | None:
    file = instance_path / settings.MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        if manifest_json.get("api_version") is None:
            manifest_v1 = ServerManifest.model_validate(manifest_json)
            manifest_v2 = InstanceManifestV1toV2(data=manifest_v1)
            return InstanceManifest.model_validate(manifest_v2)

        return InstanceManifest.model_validate(manifest_json)


def load_manifest_dirs(instance_path: Path) -> InstanceManifestDirs | None:
    file = instance_path / settings.MANIFEST_DIRS_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        return InstanceManifestDirs.model_validate(manifest_json)


def save_manifest(instance_path: Path, manifest: InstanceManifest):
    with open(instance_path / settings.MANIFEST_NAME, "w", encoding="utf-8") as f:
        # json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)
        json_str = manifest.model_dump_json(indent=2, warnings=False)
        f.write(json_str)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_files(
    instance_path: Path, files_paths: set[str], dirs_paths: set[str]
) -> dict[str, FileInfo]:
    result: dict[str, FileInfo] = {}

    for file in files_paths:
        current_file_path = instance_path / file
        if not current_file_path.exists():
            continue

        relative = current_file_path.relative_to(instance_path)

        result[str(relative)] = FileInfo(
            name=current_file_path.name,
            sha256=sha256(current_file_path),
            size=current_file_path.stat().st_size,
        )

    for dir in dirs_paths:
        current_dir_path = instance_path / dir
        if not current_dir_path.exists():
            continue

        for file in current_dir_path.rglob("*"):
            if not file.is_file():
                continue

            relative = file.relative_to(instance_path)

            result[str(relative)] = FileInfo(
                name=file.name,
                sha256=sha256(file),
                size=file.stat().st_size,
            )

    return result


def get_resourcepacks(minecraft_dir_path: Path) -> list[str]:
    options_path = minecraft_dir_path / "minecraft/options.txt"

    # Если файла нет, возвращаем пустой список
    if not options_path.exists():
        return []

    with open(options_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("resourcePacks:"):
                # Получаем часть строки после "resourcePacks:" и убираем пробелы по краям
                value = line[len("resourcePacks:") :].strip()

                # Убираем квадратные скобки по краям, если они есть (аналог substring в Java)
                value = value.strip("[]")
                if not value:
                    return []

                # Разделяем по запятой, убираем пробелы и кавычки у каждого элемента
                return [part.strip().strip('"') for part in value.split(",")]
    return []


def build_manifest(instance_path: Path) -> BuildPostResponse | InstanceManifest:
    new_resourcepacks = get_resourcepacks(instance_path)
    new_servers = get_servers(instance_path)

    old_manifest = load_manifest(instance_path)
    files_deleted: dict[str, str] = {}
    files_edited: dict[str, str] = {}
    files_added: dict[str, str] = {}

    manifest_dirs = load_manifest_dirs(instance_path)
    if manifest_dirs is None:
        raise HTTPException(404, "Instance manifest dirs not found")

    new_files = scan_files(
        instance_path=instance_path,
        files_paths=manifest_dirs.files_paths,
        dirs_paths=manifest_dirs.dirs_paths,
    )

    new_deleted: dict[str, set[str]] = {}
    version = 1

    if old_manifest:
        version = old_manifest.version

        # файл полностью новый
        for new_file_path, new_file in new_files.items():
            if new_file_path not in old_manifest.files:
                # узнаём новые файлы
                print(f"file added[{new_file_path}] = {new_file.sha256}")
                files_added[new_file_path] = new_file.sha256

        new_deleted = old_manifest.deleted.copy()

        # сравнение старого и нового манифеста
        for old_file_path, old_file in old_manifest.files.items():
            # файл полностью удалили
            if old_file_path not in new_files:
                new_deleted.setdefault(old_file_path, set())
                if old_file.sha256 not in new_deleted[old_file_path]:
                    new_deleted[old_file_path].add(old_file.sha256)
                    # узнаём новые удалённые файлы
                    print(f"file deleted[{old_file_path}] = {old_file.sha256}")
                    files_deleted[old_file_path] = old_file.sha256
                continue

            # уже существовал файл
            edited_file = new_files[old_file_path]

            # файл изменился
            if edited_file.sha256 != old_file.sha256:
                new_deleted.setdefault(old_file_path, set())
                if old_file.sha256 not in new_deleted[old_file_path]:
                    new_deleted[old_file_path].add(old_file.sha256)
                    # узнаём новые изменённые файлы
                    print(f"file edited[{old_file_path}] = {old_file.sha256}")
                    files_edited[old_file_path] = old_file.sha256

        # если sha256 снова существует среди актуальных файлов,
        # он больше не является удалённым
        for old_deleted_file_path, old_deleted_file_shas256 in list(
            new_deleted.items()
        ):
            if old_deleted_file_path in new_files:
                current_file = new_files[old_deleted_file_path]
                new_deleted[old_deleted_file_path] = {
                    sha256
                    for sha256 in old_deleted_file_shas256
                    if sha256 != current_file.sha256
                }

            # если список shas256 пустой - удалить запись
            if not new_deleted[old_deleted_file_path]:
                del new_deleted[old_deleted_file_path]

    new_manifest = InstanceManifest(
        version=version,
        api_version=2,
        files_paths=manifest_dirs.files_paths,
        dirs_paths=manifest_dirs.dirs_paths,
        strict_files_paths=manifest_dirs.strict_files_paths,
        strict_dirs_paths=manifest_dirs.strict_dirs_paths,
        resourcepacks=new_resourcepacks,
        servers=new_servers,
        deleted=new_deleted,
        files=new_files,
    )

    if new_manifest != old_manifest:
        new_manifest.version += 1

    save_manifest(instance_path, new_manifest)

    return (
        BuildPostResponse(
            version=new_manifest.version,
            api_version=new_manifest.api_version,
            new_files_paths=new_manifest.files_paths,
            new_dirs_paths=new_manifest.dirs_paths,
            new_strict_files_paths=new_manifest.strict_files_paths,
            new_strict_dirs_paths=new_manifest.strict_dirs_paths,
            new_resourcepacks=new_manifest.resourcepacks,
            new_servers=new_manifest.servers,
            files_deleted=files_deleted,
            files_edited=files_edited,
            files_added=files_added,
        )
        if old_manifest is None or new_manifest.version != old_manifest.version
        else new_manifest
    )
