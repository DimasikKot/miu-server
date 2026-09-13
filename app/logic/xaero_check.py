from pathlib import Path

from models.v3 import Waypoint

DIMENSION_MAP = {
    "dim%0": "overworld",
    "dim%-1": "nether",
    "dim%1": "end",
}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def parse_waypoint_line(line: str) -> Waypoint | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split(":")
    if len(parts) < 14 or parts[0] != "waypoint":
        return None

    return Waypoint(
        name=parts[1],
        initials=parts[2],
        x=int(parts[3]),
        y=int(parts[4]),
        z=int(parts[5]),
        color=int(parts[6]),
        disabled=_parse_bool(parts[7]),
        type=int(parts[8]),
        set=parts[9],
        rotate_on_tp=_parse_bool(parts[10]),
        tp_yaw=int(parts[11]),
        visibility_type=int(parts[12]),
        destination=_parse_bool(parts[13]),
    )


def get_waypoints(instance_path: Path) -> dict[str, list[Waypoint]]:
    """
    Читает метки из:
      minecraft/xaero/minimap/<server>/dim%<N>/mw$default_1.txt
    Возвращает {'overworld': [...], 'nether': [...], 'end': [...]}.
    """
    result: dict[str, list[Waypoint]] = {}
    minimap_path = instance_path / "minecraft/xaero/minimap"
    if not minimap_path.exists():
        return result

    for server_dir in minimap_path.iterdir():
        if not server_dir.is_dir():
            continue

        for dim_dir in server_dir.iterdir():
            if not dim_dir.is_dir() or not dim_dir.name.startswith("dim%"):
                continue

            file_path = dim_dir / "mw$default_1.txt"
            if not file_path.exists():
                continue

            dimension = DIMENSION_MAP.get(dim_dir.name, dim_dir.name)
            bucket = result.setdefault(dimension, [])

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    waypoint = parse_waypoint_line(line)
                    if waypoint is not None:
                        bucket.append(waypoint)

    return result
