import hashlib
import json
from pathlib import Path


from api.v2.models.FileInfo import FileInfo
from api.v2.models.ServerInfo import ServerInfo
from api.v2.models.server.BuildPostResponse import BuildPostResponse
from api.v2.models.server.InstanceManifest import InstanceManifest
from config import settings


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
    ]

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
    new_files = scan_files(instance_path)

    deleted: dict[str, set[str]] = {}
    version = 1

    if old_manifest:
        version = old_manifest.version + 1
        deleted = old_manifest.deleted.copy()

        # сравнение старого и нового
        for old_file in old_manifest.files:
            # файл полностью удалили
            if old_file.path not in [f.path for f in new_files]:
                deleted.setdefault(old_file.path, set())
                if old_file.sha256 not in deleted[old_file.path]:
                    deleted[old_file.path].add(old_file.sha256)
                continue

            # новый файл
            new_file = [
                new_file for new_file in new_files if new_file.path == old_file.path
            ][0]

            # файл изменился
            if new_file.sha256 != old_file.sha256:
                deleted.setdefault(old_file.path, set())
                if old_file.sha256 not in deleted[old_file.path]:
                    deleted[old_file.path].add(old_file.sha256)

    # Очистка removed

    # если sha256 снова существует среди актуальных файлов,
    # он больше не является удалённым
    new_deleted: dict[str, str] = {}

    for old_path, old_hashes in list(deleted.items()):
        if old_path in [f.path for f in new_files]:
            current_file = [f for f in new_files if f.path == old_path][0]
            deleted[old_path] = {h for h in old_hashes if h != current_file.sha256}

            new_deleted[old_path] = current_file.sha256 # TODO

        # если список пустой - удалить запись
        if not deleted[old_path]:
            del deleted[old_path]

    new_manifest = InstanceManifest(
        version=version,
        files_paths=old_manifest.files_paths if old_manifest else set(),
        dirs_paths=old_manifest.dirs_paths if old_manifest else set(),
        strict_files_paths=old_manifest.strict_files_paths if old_manifest else set(),
        strict_dirs_paths=old_manifest.strict_dirs_paths if old_manifest else set(),
        resourcepacks=new_resourcepacks,
        servers=new_servers,
        deleted=deleted,
        files=new_files,
    )

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
        new_deleted=new_deleted,
        new_files=new_files,
    )
