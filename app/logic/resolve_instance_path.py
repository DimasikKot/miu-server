import re
import pathlib
from fastapi import HTTPException

from config import settings


def canon(s: str) -> str:
    # убираем пробелы и приводим к нижнему регистру
    return re.sub(r"\s+", "", s).lower()


def resolve_instance_path(instance_name: str) -> pathlib.Path:
    """
    Находит папку инстанса по имени.
    1. Точное совпадение.
    2. Префиксный поиск (без учёта пробелов и регистра).
    3. Самая короткая из найденных = ближайшая к оригиналу.
    """

    # 1. точное совпадение
    exact = settings.INSTANCES_DIR_PATH / instance_name
    if exact.exists():
        return exact

    # 2. префиксный поиск
    req = canon(instance_name)
    matches = [
        p
        for p in settings.INSTANCES_DIR_PATH.iterdir()
        if p.is_dir() and req.startswith(canon(p.name))
    ]

    if not matches:
        raise HTTPException(404, "Instance not found")

    # самая короткая = ближе всего к оригиналу
    matches.sort(key=lambda p: (len(p.name), p.name))
    return matches[0]
