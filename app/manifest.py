import hashlib
import json
from pathlib import Path

from models.FileInfo import FileInfo
from models.ServerInfo import ServerInfo
from models.server.BuildPostResponse import BuildPostResponse
from models.server.InstanceManifest import InstanceManifest
from config import settings


def load_manifest(instance_path: Path) -> InstanceManifest | None:
    file = instance_path / settings.MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        return InstanceManifest.model_validate(json.load(f))


def save_manifest(instance_path: Path, manifest: InstanceManifest):
    with open(instance_path / settings.MANIFEST_NAME, "w", encoding="utf-8") as f:
        # json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)
        json_str = manifest.model_dump_json(indent=4, warnings=False)
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


def scan_files(instance_path: Path) -> set[FileInfo]:
    result: set[FileInfo] = set()
    folders = [
        "minecraft/config",
        "minecraft/mods",
        "minecraft/resourcepacks",
        "minecraft/xaero",
    ]  # TODO

    for folder in folders:
        current = instance_path / folder
        if not current.exists():
            continue

        for file in current.rglob("*"):
            if not file.is_file():
                continue

            relative = file.relative_to(instance_path)

            result.add(
                FileInfo(
                    name=file.name,
                    path=str(relative),
                    sha256=sha256(file),
                    size=file.stat().st_size,
                )
            )

    return result


def get_resource_packs(minecraft_dir_path: Path) -> set[str]:
    options_path = minecraft_dir_path / "options.txt"

    # Если файла нет, возвращаем пустой список
    if not options_path.exists():
        return set()

    with open(options_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("resourcePacks:"):
                # Получаем часть строки после "resourcePacks:" и убираем пробелы по краям
                value = line[len("resourcePacks:") :].strip()

                # Убираем квадратные скобки по краям, если они есть (аналог substring в Java)
                value = value.strip("[]")
                if not value:
                    return set()

                # Разделяем по запятой, убираем пробелы и кавычки у каждого элемента
                return {part.strip().strip('"') for part in value.split(",")}
    return set()


def build_manifest(instance_path: Path) -> tuple[InstanceManifest, BuildPostResponse]:
    new_resourcepacks = get_resource_packs(instance_path / "minecraft")

    new_pack = Path(instance_path / "mmc-pack.json")
    if not new_pack.exists():
        new_pack = None
    else:
        # with open(new_pack, encoding="utf-8") as f:
        new_pack = FileInfo(
            name=new_pack.name,
            path=str(new_pack.relative_to(instance_path)),
            sha256=sha256(new_pack),
            size=new_pack.stat().st_size,
        )

    new_instance = Path(instance_path / "instance.cfg")
    if not new_instance.exists():
        new_instance = None
    else:
        # with open(new_instance, encoding="utf-8") as f:
        new_instance = FileInfo(
            name=new_instance.name,
            path=str(new_instance.relative_to(instance_path)),
            sha256=sha256(new_instance),
            size=new_instance.stat().st_size,
        )

    new_servers: list[ServerInfo] = []  # TODO minecraft/servers.dat

    old_manifest = load_manifest(instance_path)
    files_deleted: dict[str, str] = {}
    files_edited: dict[str, str] = {}
    files_added: dict[str, str] = {}
    new_files = scan_files(instance_path)

    new_deleted: dict[str, set[str]] = {}
    version = 1

    if old_manifest:
        # файл полностью новый
        for new_file in new_files:
            if new_file.path not in [file.path for file in old_manifest.files]:
                files_added[new_file.path] = new_file.sha256

        new_deleted = old_manifest.deleted.copy()

        # сравнение старого и нового манифеста
        for old_file in old_manifest.files:
            # файл полностью удалили
            if old_file.path not in [file.path for file in new_files]:
                new_deleted.setdefault(old_file.path, set())
                if old_file.sha256 not in new_deleted[old_file.path]:
                    new_deleted[old_file.path].add(old_file.sha256)
                    # узнаём новые удалённые файлы
                    files_deleted[old_file.path] = old_file.sha256
                continue

            # уже существовал файл
            edited_file = [file for file in new_files if file.path == old_file.path][0]

            # файл изменился
            if edited_file.sha256 != old_file.sha256:
                new_deleted.setdefault(old_file.path, set())
                if old_file.sha256 not in new_deleted[old_file.path]:
                    new_deleted[old_file.path].add(old_file.sha256)
                    # узнаём новые изменённые файлы
                    files_edited[old_file.path] = old_file.sha256

        # если sha256 снова существует среди актуальных файлов,
        # он больше не является удалённым
        for old_path, old_shas256 in list(new_deleted.items()):
            if old_path in [file.path for file in new_files]:
                current_file = [file for file in new_files if file.path == old_path][0]
                new_deleted[old_path] = {
                    sha256 for sha256 in old_shas256 if sha256 != current_file.sha256
                }

            # если список shas256 пустой - удалить запись
            if not new_deleted[old_path]:
                del new_deleted[old_path]

    new_manifest = InstanceManifest(
        version=version,
        files_paths=old_manifest.files_paths if old_manifest else set(),
        dirs_paths=old_manifest.dirs_paths if old_manifest else set(),
        strict_files_paths=old_manifest.strict_files_paths if old_manifest else set(),
        strict_dirs_paths=old_manifest.strict_dirs_paths if old_manifest else set(),
        resourcepacks=new_resourcepacks,
        servers=new_servers,
        deleted=new_deleted,
        files=new_files,
    )

    files_added: dict[str, str] = {}

    if new_manifest != old_manifest:
        new_manifest.version += 1

    save_manifest(instance_path, new_manifest)

    return new_manifest, BuildPostResponse(
        version=version,
        new_files_paths=old_manifest.files_paths if old_manifest else set(),
        new_dirs_paths=old_manifest.dirs_paths if old_manifest else set(),
        new_strict_files_paths=(
            old_manifest.strict_files_paths if old_manifest else set()
        ),
        new_strict_dirs_paths=old_manifest.strict_dirs_paths if old_manifest else set(),
        new_resourcepacks=new_resourcepacks,
        new_servers=new_servers,
        files_deleted=files_deleted,
        files_edited=files_edited,
        files_added=files_added,
    )
