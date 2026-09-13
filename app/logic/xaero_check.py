from pathlib import Path

from models.v3 import Waypoint

DIMENSION_MAP = {
    "dim%0": "overworld",
    "dim%-1": "nether",
    "dim%1": "end",
}
REVERSE_DIMENSION_MAP = {v: k for k, v in DIMENSION_MAP.items()}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def parse_waypoint_line(line: str) -> Waypoint | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split(":")
    if len(parts) < 14 or parts[0] != "waypoint":
        return None

    # Имя может содержать ':' — берём всё между "waypoint" и последними 12 полями.
    tail = parts[-12:]
    name = ":".join(parts[1:-12])

    return Waypoint(
        name=name,
        initials=tail[0],
        x=int(tail[1]),
        y=int(tail[2]),
        z=int(tail[3]),
        color=int(tail[4]),
        disabled=_parse_bool(tail[5]),
        type=int(tail[6]),
        set=tail[7],
        rotate_on_tp=_parse_bool(tail[8]),
        tp_yaw=int(tail[9]),
        visibility_type=int(tail[10]),
        destination=_parse_bool(tail[11]),
    )


def get_waypoints(instance_path: Path) -> dict[str, list[Waypoint]]:
    """
    Читает метки из: minecraft/xaero/minimap/<server>/dim%<N>/mw$default_1.txt

    Возвращает словарь с ключом "<server>/<dimension>",
    например {"Multiplayer_purmur.exaroton.me/overworld": [...]}.
    """
    result: dict[str, list[Waypoint]] = {}
    minimap_path = instance_path / "minecraft/xaero/minimap"
    if not minimap_path.exists():
        return result

    for server_dir in minimap_path.iterdir():
        if not server_dir.is_dir():
            continue
        server_name = server_dir.name

        for dim_dir in server_dir.iterdir():
            if not dim_dir.is_dir() or not dim_dir.name.startswith("dim%"):
                continue

            file_path = dim_dir / "mw$default_1.txt"
            if not file_path.exists():
                continue

            dimension = DIMENSION_MAP.get(dim_dir.name, dim_dir.name)
            key = f"{server_name}/{dimension}"
            bucket = result.setdefault(key, [])

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    waypoint = parse_waypoint_line(line)
                    if waypoint is not None:
                        bucket.append(waypoint)

    return result
