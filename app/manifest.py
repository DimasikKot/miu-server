import hashlib
import json
from pathlib import Path

from main import MANIFEST_NAME
from models.FileInfo import FileInfo
from models.InstanceManifest import InstanceManifest


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_files(instance_path: Path):
    result = {}
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

            result[str(relative)] = FileInfo(
                name=file.name,
                path=str(relative),
                sha256=sha256(file),
                size=file.stat().st_size,
            )

    return result


def get_resource_packs(minecraft_dir_path: Path) -> list[str]:
    options_path = minecraft_dir_path / "options.txt"

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


def load_manifest(instance_path: Path):
    file = instance_path / MANIFEST_NAME
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        return InstanceManifest.model_validate(json.load(f))


def save_manifest(instance_path: Path, manifest: InstanceManifest):
    with open(instance_path / MANIFEST_NAME, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, indent=4, ensure_ascii=False)


def build_manifest(instance_path: Path):
    new_resource_packs = get_resource_packs(instance_path / "minecraft")

    new_pack = Path(instance_path / "mmc-pack.json")
    if not new_pack.exists():
        new_pack = None
    else:
        with open(new_pack, encoding="utf-8") as f:
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
        with open(new_instance, encoding="utf-8") as f:
            new_instance = FileInfo(
                name=new_instance.name,
                path=str(new_instance.relative_to(instance_path)),
                sha256=sha256(new_instance),
                size=new_instance.stat().st_size,
            )

    new_servers = []  # TODO minecraft/servers.dat

    old_manifest = load_manifest(instance_path)
    new_files = scan_files(instance_path)

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

    new_manifest = InstanceManifest(
        version=version,
        pack=new_pack,
        instance=new_instance,
        files=new_files,
        removed=removed,
        servers=new_servers,
        resource_packs=new_resource_packs,
    )

    save_manifest(instance_path, new_manifest)

    return new_manifest
