from pathlib import Path

import nbtlib  # type: ignore

from models.ServerInfo import ServerInfo


def get_servers(minecraft_dir_path: Path) -> list[ServerInfo]:
    servers_path = minecraft_dir_path / "minecraft/servers.dat"

    # Если файла нет, возвращаем пустой список
    if not servers_path.exists():
        return []

    servers: list[ServerInfo] = []

    try:
        nbt_data = nbtlib.load(servers_path)  # type: ignore
        servers_list = nbt_data["servers"]  # type: ignore
        for server_tag in servers_list:  # type: ignore
            name = server_tag.get("name", "Нет имени")  # type: ignore
            ip = server_tag.get("ip", "Нет IP")  # type: ignore
            servers.append(ServerInfo(name=name, ip=ip))  # type: ignore
    except Exception as e:
        print(f"Error servers.dat: {e}")
        return []

    return servers
