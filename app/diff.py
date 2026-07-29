from typing import List
from urllib.parse import quote

from models import (
    ClientManifest,
    DownloadFile,
    ServerInfo,
    ServerManifest,
    UpdateResponse,
)


def is_removed(path: str, sha256: str, server_manifest: ServerManifest) -> bool:
    # Проверяет, считается ли данный SHA удалённым
    removed = server_manifest.removed.get(path, {})
    return sha256 in removed


def build_delete_list(
    client_manifest: ClientManifest, server_manifest: ServerManifest
) -> List[str]:
    delete = []
    for client_path, client_file in client_manifest.files.items():

        # Если файла больше нет на сервере,
        # но его SHA находится в removed
        if client_path not in server_manifest.files:
            if is_removed(client_path, client_file.sha256, server_manifest):
                delete.append(client_path)
            continue

        # Если SHA клиента совпадает
        # с одним из старых SHA
        if is_removed(client_path, client_file.sha256, server_manifest):
            delete.append(client_path)

    return delete


def build_download_list(
    client_manifest: ClientManifest,
    server_manifest: ServerManifest,
    instance: str,
    base_url: str,
) -> List[DownloadFile]:
    download = []

    client_pack = client_manifest.pack
    server_pack = server_manifest.pack
    if (
        server_pack is not None
        and client_pack is not None
        and client_pack.sha256 != server_pack.sha256
    ):

        # SHA отличается
        download.append(
            DownloadFile(
                path=server_pack.path,
                sha256=server_pack.sha256,
                size=server_pack.size,
                url=f"{base_url}/files/"
                f"{quote(instance)}/"
                f"{quote(server_pack.path, safe='/')}",
            )
        )

    client_instance = client_manifest.instance
    server_instance = server_manifest.instance
    if (
        server_instance is not None
        and client_instance is not None
        and client_instance.sha256 != server_instance.sha256
    ):

        # SHA отличается
        download.append(
            DownloadFile(
                path=server_instance.path,
                sha256=server_instance.sha256,
                size=server_instance.size,
                url=f"{base_url}/files/"
                f"{quote(instance)}/"
                f"{quote(server_instance.path, safe='/')}",
            )
        )

    # Проходим по всем файлам внутри Instance на сервере
    for server_path, server_file in server_manifest.files.items():

        # Нет файла
        if server_path not in client_manifest.files:
            url = (
                f"{base_url}/files/"
                f"{quote(instance)}/"
                f"{quote(server_path, safe='/')}"
            )
            download.append(
                DownloadFile(
                    path=server_path,
                    sha256=server_file.sha256,
                    size=server_file.size,
                    url=url,
                )
            )
            continue

        client_file = client_manifest.files[server_path]

        # SHA совпадает
        if client_file.sha256 == server_file.sha256:
            continue

        # SHA отличается и это строгое место (моды)
        strict_folders = ["minecraft/mods"]
        if any(server_path.startswith(folder) for folder in strict_folders):
            download.append(
                DownloadFile(
                    path=server_path,
                    sha256=server_file.sha256,
                    size=server_file.size,
                    url=f"{base_url}/files/"
                    f"{quote(instance)}/"
                    f"{quote(server_path, safe='/')}",
                )
            )

    return download


def compare_servers(
    client_servers: List[ServerInfo], server_servers: List[ServerInfo]
) -> List[ServerInfo]:
    # 1. Создаём копию списка клиента, чтобы не изменять исходный массив
    result = list(client_servers)

    # 2. Создаём множество IP-адресов уже существующих серверов для быстрого поиска
    # IP используем как уникальный идентификатор сервера
    existing_ips = {server.ip for server in result}

    # 3. Проходим по списку серверов
    for server in server_servers:
        # Если сервера с таким IP ещё нет у клиента, добавляем его в конец
        if server.ip not in existing_ips:
            result.append(server)
            existing_ips.add(server.ip)  # Обновляем множество

    return result


def compare_resource_packs(
    client_resource_packs: List[str], server_resource_packs: List[str]
) -> List[str]:
    # 1. Создаём копию списка клиента, чтобы не изменять исходный массив
    result = list(client_resource_packs)

    # 2. Создаём множество из текущих ресурс паков клиента для быстрого поиска (O(1))
    # Также это автоматически убирает возможные дубликаты, если они вдруг были в client_resource_packs
    existing_resource_packs = set(result)

    # 3. Проходим по списку ресурс паков
    for resource_pack in server_resource_packs:
        # Если ресурс паков ещё нет у клиента, добавляем его в конец
        if resource_pack not in existing_resource_packs:
            result.append(resource_pack)
            existing_resource_packs.add(
                resource_pack
            )  # Обновляем множество, чтобы не добавить его повторно

    return result


def compare(
    instance: str,
    client_manifest: ClientManifest,
    server_manifest: ServerManifest,
    base_url: str,
) -> UpdateResponse:
    download = build_download_list(client_manifest, server_manifest, instance, base_url)
    delete = build_delete_list(client_manifest, server_manifest)

    return UpdateResponse(
        version=server_manifest.version,
        download=download,
        delete=delete,
        servers=compare_servers(client_manifest.servers, server_manifest.servers),
        resource_packs=compare_resource_packs(
            client_manifest.resource_packs, server_manifest.resource_packs
        ),
    )
