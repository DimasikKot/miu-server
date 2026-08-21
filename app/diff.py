from urllib.parse import quote

from api.v2.models.FileDownloadInfo import FileDownloadInfo
from api.v2.models.ServerInfo import ServerInfo
from api.v2.models.UpdatePostRequest import UpdatePostRequest
from api.v2.models.UpdatePostResponse import UpdatePostResponse
from api.v2.models.server.InstanceManifest import InstanceManifest
from api.v2.models.ServerInfo import ServerInfo
from config import settings


def is_deleted(path: str, sha256: str, instance_manifest: InstanceManifest) -> bool:
    # Проверяет, считается ли данный SHA удалённым
    deleted = instance_manifest.deleted.get(path, [])
    return sha256 in deleted


def build_delete_list(
    request: UpdatePostRequest, instance_manifest: InstanceManifest
) -> set[str]:
    delete: set[str] = set()
    for client_path, client_file in request.files:

        # Если файла больше нет на сервере,
        # но его SHA находится в removed
        if client_path not in instance_manifest.files:
            if is_deleted(client_path, client_file.sha256, instance_manifest):
                delete.append(client_path)
            continue

        # Если SHA клиента совпадает
        # с одним из старых SHA
        if is_deleted(client_path, client_file.sha256, instance_manifest):
            delete.append(client_path)

    return delete


def build_download_list(
    request: UpdatePostRequest,
    instance_manifest: InstanceManifest,
    instance_name: str,
    base_url: str,
) -> list[FileDownloadInfo]:
    download: list[FileDownloadInfo] = []

    # Проходим по всем файлам внутри Instance на сервере
    for server_path, server_file in instance_manifest.files.items():

        # Нет файла
        if server_path not in request.files:
            url = (
                f"{base_url}{settings.INSTANCES_FOLDER_PATH}/"
                f"{quote(instance_name)}/"
                f"{quote(server_path, safe='/')}"
            )
            download.append(
                FileDownloadInfo(
                    path=server_path,
                    sha256=server_file.sha256,
                    size=server_file.size,
                    url=url,
                )
            )
            continue

        client_file = request.files[server_path]

        # SHA совпадает
        if client_file.sha256 == server_file.sha256:
            continue

        # SHA отличается и это строгое место (моды)
        strict_folders = ["minecraft/mods"]
        if any(server_path.startswith(folder) for folder in strict_folders):
            download.append(
                FileDownloadInfo(
                    path=server_path,
                    sha256=server_file.sha256,
                    size=server_file.size,
                    url=f"{base_url}/files/"
                    f"{quote(instance_name)}/"
                    f"{quote(server_path, safe='/')}",
                )
            )

    return download


def compare_servers(
    request_servers: List[ServerInfo], instance_servers: List[ServerInfo]
) -> List[ServerInfo]:
    # 1. Создаём копию списка клиента, чтобы не изменять исходный массив
    result = list(request_servers)

    # 2. Создаём множество IP-адресов уже существующих серверов для быстрого поиска
    # IP используем как уникальный идентификатор сервера
    existing_ips = {server.ip for server in result}

    # 3. Проходим по списку серверов
    for server in instance_servers:
        # Если сервера с таким IP ещё нет у клиента, добавляем его в конец
        if server.ip not in existing_ips:
            result.append(server)
            existing_ips.add(server.ip)  # Обновляем множество

    return result


def compare_resource_packs(
    request_resourcepacks: set[str], instance_resourcepacks: set[str]
) -> set[str]:
    # 1. Создаём копию списка клиента, чтобы не изменять исходный массив
    result = set(request_resourcepacks)

    # 2. Создаём множество из текущих ресурс паков клиента для быстрого поиска (O(1))
    # Также это автоматически убирает возможные дубликаты, если они вдруг были в client_resource_packs
    existing_resource_packs = set(result)

    # 3. Проходим по списку ресурс паков
    for resource_pack in instance_resourcepacks:
        # Если ресурс паков ещё нет у клиента, добавляем его в конец
        if resource_pack not in existing_resource_packs:
            result.add(resource_pack)
            existing_resource_packs.add(
                resource_pack
            )  # Обновляем множество, чтобы не добавить его повторно

    return result


def compare(
    request: UpdatePostRequest,
    instance_manifest: InstanceManifest,
    instance_name: str,
    base_url: str,
) -> UpdatePostResponse:
    download = build_download_list(request, instance_manifest, instance_name, base_url)
    delete = build_delete_list(request, instance_manifest)

    return UpdatePostResponse(
        new_resourcepacks=compare_resource_packs(
            request.resourcepacks, instance_manifest.resourcepacks
        ),
        new_servers=compare_servers(request.servers, instance_manifest.servers),
        need_delete=set(delete),
        need_download=set(download),
    )
