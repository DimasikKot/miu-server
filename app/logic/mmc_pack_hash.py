import hashlib
import json
from pathlib import Path
from typing import Any


def _remove_cached_fields(node: Any):
    if isinstance(node, dict):
        # Собираем ключи, которые нужно удалить (нельзя менять dict во время итерации)
        for key in [k for k in node.keys() if k.startswith("cached")]: # type: ignore
            del node[key]
        for value in node.values(): # type: ignore
            _remove_cached_fields(value)
    elif isinstance(node, list):
        for item in node: # type: ignore
            _remove_cached_fields(item)


def normalized_sha256(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        root = json.loads(f.read().decode("utf-8"))

    _remove_cached_fields(root)

    # sort_keys=True — аналог ORDER_MAP_ENTRIES_BY_KEYS
    # separators=(",", ":") — компактно, без пробелов, как Jackson по умолчанию
    canonical = json.dumps(
        root,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    print(list(canonical))

    return hashlib.sha256(canonical).hexdigest()
