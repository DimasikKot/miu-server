import hashlib
import json
from pathlib import Path

from fastapi import HTTPException

from api.v1.transformV1toV2 import InstanceManifestV1toV2
from api.v2.transformV2toV3 import InstanceManifestV2toV3
from logic.get_servers import get_servers
from config import settings
from logic.xaero_check import get_waypoints
from models.v1 import ServerManifest as InstanceManifestV1
from models.v2 import FileInfo, ServerInfo
from models.v2.server import (
    InstanceManifest as InstanceManifestV2,
    InstanceManifestDirs as InstanceManifestDirsV2,
)
from models.v3 import Waypoint
from models.v3.server import (
    BuildPostResponse,
    ReBuildPostResponse,
    InstanceManifest as InstanceManifestV3,
)


def load_manifest(instance_path: Path) -> InstanceManifestV3 | None:
    file = instance_path / settings.MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        if manifest_json.get("api_version") is None:
            manifest_v1 = InstanceManifestV1.model_validate(manifest_json)
            manifest_v2 = InstanceManifestV1toV2(data=manifest_v1)
            manifest_v3 = InstanceManifestV2toV3(data=manifest_v2)
            return InstanceManifestV3.model_validate(manifest_v3)
        if manifest_json.get("api_version") == 2:
            manifest_v2 = InstanceManifestV2.model_validate(manifest_json)
            manifest_v3 = InstanceManifestV2toV3(data=manifest_v2)
            return InstanceManifestV3.model_validate(manifest_v3)

        return InstanceManifestV3.model_validate(manifest_json)


def load_manifest_dirs(instance_path: Path) -> InstanceManifestDirsV2 | None:
    file = instance_path / settings.MANIFEST_DIRS_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        manifest_json = json.load(f)
        return InstanceManifestDirsV2.model_validate(manifest_json)


def save_manifest(instance_path: Path, manifest: InstanceManifestV3):
    instance_path.parent.mkdir(parents=True, exist_ok=True)
    with open(instance_path, "w", encoding="utf-8") as f:
        # json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)
        json_str = manifest.model_dump_json(indent=2, warnings=False)
        f.write(json_str)


def save_response(instance_path: Path, response: ReBuildPostResponse):
    instance_path.parent.mkdir(parents=True, exist_ok=True)
    with open(instance_path, "w", encoding="utf-8") as f:
        # json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)
        json_str = response.model_dump_json(indent=2, warnings=False)
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


def get_resourcepacks(instance_path: Path) -> list[str]:
    options_path = instance_path / "minecraft/options.txt"

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


def get_incompatible_resourcepacks(instance_path: Path) -> list[str]:
    options_path = instance_path / "minecraft/options.txt"

    # Если файла нет, возвращаем пустой список
    if not options_path.exists():
        return []

    with open(options_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("incompatibleResourcePacks:"):
                # Получаем часть строки после "incompatibleResourcePacks:" и убираем пробелы по краям
                value = line[len("incompatibleResourcePacks:") :].strip()

                # Убираем квадратные скобки по краям, если они есть (аналог substring в Java)
                value = value.strip("[]")
                if not value:
                    return []

                # Разделяем по запятой, убираем пробелы и кавычки у каждого элемента
                return [part.strip().strip('"') for part in value.split(",")]
    return []


def _diff_sets(new_set: set[str], old_set: set[str] | None) -> set[str]:
    """Возвращает элементы new_list, которых не было в old_list (с сохранением порядка)."""
    if old_set is None:
        return set(new_set)
    old_set = set(old_set)
    return {item for item in new_set if item not in old_set}


def _diff_lists(new_list: list[str], old_list: list[str] | None) -> list[str]:
    """Возвращает элементы new_list, которых не было в old_list (с сохранением порядка)."""
    if old_list is None:
        return list(new_list)
    old_set = set(old_list)
    return [item for item in new_list if item not in old_set]


def _diff_servers(new_servers: list[ServerInfo], old_servers: list[ServerInfo]):
    """Возвращает серверы из new_servers, которых не было в old_servers."""

    def key(s: ServerInfo):
        return (s.name, s.ip)

    old_keys = {key(s) for s in old_servers}
    return [s for s in new_servers if key(s) not in old_keys]


def _waypoint_key(w: Waypoint):
    return (w.name, w.x, w.y, w.z)


def _diff_waypoints(
    new_waypoints: dict[str, list[Waypoint]],
    old_waypoints: dict[str, list[Waypoint]] | None,
) -> dict[str, list[Waypoint]]:
    """Возвращает точки из new_waypoints, которых не было в old_waypoints."""
    if old_waypoints is None:
        return {dim: list(pts) for dim, pts in new_waypoints.items()}

    result: dict[str, list[Waypoint]] = {}
    for dim, new_points in new_waypoints.items():
        old_points = old_waypoints.get(dim, [])
        old_keys = {_waypoint_key(w) for w in old_points}
        diff = [w for w in new_points if _waypoint_key(w) not in old_keys]
        if diff:
            result[dim] = diff
    return result


def get_alternative_path(path: str) -> str | None:
    """Возвращает альтернативное имя файла (.jar <-> .jar.disabled), если применимо."""
    if path.endswith(".jar.disabled"):
        return path[:-9]  # Убираем '.disabled'
    elif path.endswith(".jar"):
        return path + ".disabled"
    return None


def _is_strict(path: str, dirs: InstanceManifestDirsV2) -> bool:
    if path in dirs.strict_files_paths:
        return True
    return any(path.startswith(d.rstrip("/") + "/") for d in dirs.strict_dirs_paths)


def build_manifest(
    instance_path: Path,
) -> BuildPostResponse | ReBuildPostResponse | InstanceManifestV3:
    new_resourcepacks = get_resourcepacks(instance_path)
    new_incompatible_resourcepacks = get_incompatible_resourcepacks(instance_path)
    new_servers = get_servers(instance_path)
    new_waypoints = get_waypoints(instance_path)

    old_manifest = load_manifest(instance_path)
    files_deleted: dict[str, str] = {}
    files_strict_deleted: dict[str, str] = {}
    files_edited: dict[str, str] = {}
    files_strict_edited: dict[str, str] = {}
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
                # Проверяем, не является ли это простым переименованием .jar <-> .jar.disabled
                alt_path = get_alternative_path(new_file_path)
                if alt_path and alt_path in old_manifest.files:
                    # Если файл существовал под альтернативным именем и его sha256 совпадает,
                    # то это просто переименование, а не добавление нового файла.
                    if old_manifest.files[alt_path].sha256 == new_file.sha256:
                        # узнаём новые изменённые файлы
                        print(f"file edited[{alt_path}] = {new_file.sha256}")
                        files_edited[alt_path] = new_file.sha256
                        continue

                # узнаём новые файлы
                print(f"file added[{new_file_path}] = {new_file.sha256}")
                files_added[new_file_path] = new_file.sha256

        new_deleted = old_manifest.deleted.copy()

        # сравнение старого и нового манифеста
        for old_file_path, old_file in old_manifest.files.items():
            # Ищем файл в new_files по точному имени или альтернативному
            actual_new_path = old_file_path if old_file_path in new_files else None
            if actual_new_path is None:
                alt_path = get_alternative_path(old_file_path)
                if alt_path and alt_path in new_files:
                    actual_new_path = alt_path

            # файл полностью удалили (нет ни точного, ни альтернативного имени)
            if actual_new_path is None:
                if _is_strict(old_file_path, manifest_dirs):
                    # узнаём новые удалённые файлы
                    print(f"file strict deleted[{old_file_path}] = {old_file.sha256}")
                    files_strict_deleted[old_file_path] = old_file.sha256

                    new_deleted.setdefault(old_file_path, set())
                    if old_file.sha256 not in new_deleted[old_file_path]:
                        new_deleted[old_file_path].add(old_file.sha256)
                else:
                    # узнаём новые удалённые файлы
                    print(f"file deleted[{old_file_path}] = {old_file.sha256}")
                    files_deleted[old_file_path] = old_file.sha256
                continue

            # уже существовал файл (под точным или альтернативным именем)
            edited_file = new_files[actual_new_path]

            # файл изменился (или был переименован с изменением содержимого)
            if edited_file.sha256 != old_file.sha256:
                if _is_strict(old_file_path, manifest_dirs):
                    # узнаём новые удалённые файлы
                    print(f"file strict edited[{old_file_path}] = {old_file.sha256}")
                    files_strict_edited[old_file_path] = old_file.sha256

                    new_deleted.setdefault(old_file_path, set())
                    if old_file.sha256 not in new_deleted[old_file_path]:
                        new_deleted[old_file_path].add(old_file.sha256)
                else:
                    # узнаём новые удалённые файлы
                    print(f"file edited[{old_file_path}] = {old_file.sha256}")
                    files_edited[old_file_path] = old_file.sha256

        # если sha256 снова существует среди актуальных файлов,
        # он больше не является удалённым
        for old_deleted_file_path, old_deleted_file_shas256 in list(
            new_deleted.items()
        ):
            # Проверяем наличие файла под точным или альтернативным именем
            current_file = new_files.get(old_deleted_file_path)
            if current_file is None:
                alt_path = get_alternative_path(old_deleted_file_path)
                if alt_path:
                    current_file = new_files.get(alt_path)

            if current_file:
                new_deleted[old_deleted_file_path] = {
                    sha256
                    for sha256 in old_deleted_file_shas256
                    if sha256 != current_file.sha256
                }

            # если список shas256 пустой - удалить запись
            if not new_deleted[old_deleted_file_path]:
                del new_deleted[old_deleted_file_path]

    new_manifest = InstanceManifestV3(
        version=version,
        api_version=2,
        files_paths=manifest_dirs.files_paths,
        dirs_paths=manifest_dirs.dirs_paths,
        strict_files_paths=manifest_dirs.strict_files_paths,
        strict_dirs_paths=manifest_dirs.strict_dirs_paths,
        resourcepacks=new_resourcepacks,
        incompatible_resourcepacks=new_incompatible_resourcepacks,
        servers=new_servers,
        waypoints=new_waypoints,
        deleted=new_deleted,
        files=new_files,
    )

    if old_manifest is not None and new_manifest != old_manifest:
        new_manifest.version += 1
        save_manifest(
            instance_path
            / "old"
            / (f"ver{old_manifest.version}." + settings.MANIFEST_NAME),
            old_manifest,
        )

    save_manifest(instance_path / settings.MANIFEST_NAME, new_manifest)

    if old_manifest is not None and new_manifest != old_manifest:
        response = ReBuildPostResponse(
            version=new_manifest.version,
            api_version=new_manifest.api_version,
            del_files_paths=_diff_sets(
                old_manifest.files_paths, new_manifest.files_paths
            ),
            new_files_paths=_diff_sets(
                new_manifest.files_paths, old_manifest.files_paths
            ),
            del_dirs_paths=_diff_sets(old_manifest.dirs_paths, new_manifest.dirs_paths),
            new_dirs_paths=_diff_sets(new_manifest.dirs_paths, old_manifest.dirs_paths),
            del_strict_files_paths=_diff_sets(
                old_manifest.strict_files_paths, new_manifest.strict_files_paths
            ),
            new_strict_files_paths=_diff_sets(
                new_manifest.strict_files_paths, old_manifest.strict_files_paths
            ),
            del_strict_dirs_paths=_diff_sets(
                old_manifest.strict_dirs_paths, new_manifest.strict_dirs_paths
            ),
            new_strict_dirs_paths=_diff_sets(
                new_manifest.strict_dirs_paths, old_manifest.strict_dirs_paths
            ),
            del_resourcepacks=_diff_lists(
                old_manifest.resourcepacks, new_manifest.resourcepacks
            ),
            new_resourcepacks=_diff_lists(
                new_manifest.resourcepacks, old_manifest.resourcepacks
            ),
            del_incompatible_resourcepacks=_diff_lists(
                old_manifest.incompatible_resourcepacks,
                new_manifest.incompatible_resourcepacks,
            ),
            new_incompatible_resourcepacks=_diff_lists(
                new_manifest.incompatible_resourcepacks,
                old_manifest.incompatible_resourcepacks,
            ),
            del_servers=_diff_servers(old_manifest.servers, new_manifest.servers),
            new_servers=_diff_servers(new_manifest.servers, old_manifest.servers),
            del_waypoints=_diff_waypoints(
                old_manifest.waypoints, new_manifest.waypoints
            ),
            new_waypoints=_diff_waypoints(
                new_manifest.waypoints, old_manifest.waypoints
            ),
            files_deleted=files_deleted,
            files_strict_deleted=files_strict_deleted,
            files_edited=files_edited,
            files_strict_edited=files_strict_edited,
            files_added=files_added,
        )

        save_response(
            instance_path
            / "old"
            / (f"ver{old_manifest.version}-{new_manifest.version}." + "response.json"),
            response,
        )
        return response

    return (
        BuildPostResponse(
            version=new_manifest.version,
            api_version=new_manifest.api_version,
            new_files_paths=new_manifest.files_paths,
            new_dirs_paths=new_manifest.dirs_paths,
            new_strict_files_paths=new_manifest.strict_files_paths,
            new_strict_dirs_paths=new_manifest.strict_dirs_paths,
            new_resourcepacks=new_manifest.resourcepacks,
            new_incompatible_resourcepacks=new_manifest.incompatible_resourcepacks,
            new_servers=new_manifest.servers,
            files_added={
                file_path: file.sha256 for file_path, file in new_manifest.files.items()
            },
        )
        if old_manifest is None
        else new_manifest
    )
