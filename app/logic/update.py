from urllib.parse import quote

from models.FileDownloadInfo import FileDownloadInfo
from models.ServerInfo import ServerInfo
from models.UpdatePostRequest import UpdatePostRequest
from models.UpdatePostResponse import UpdatePostResponse
from models.server.InstanceManifest import InstanceManifest
from models.ServerInfo import ServerInfo
from config import settings


# Проверяет, считается ли данный SHA удалённым
def is_deleted(path: str, sha256: str, instance_manifest: InstanceManifest) -> bool:
    deleted = instance_manifest.deleted.get(path, [])
    return sha256 in deleted


def build_delete_list(
    request: UpdatePostRequest, instance_manifest: InstanceManifest
) -> set[str]:
    need_delete: set[str] = set()
    for request_file_path, request_file in request.files.items():
        # Если файла больше нет на сервере, но его SHA находится в removed
        if request_file_path not in instance_manifest.files.keys():
            if is_deleted(request_file_path, request_file.sha256, instance_manifest):
                need_delete.add(request_file_path)
            continue

        # Если SHA клиента совпадает с одним из старых SHA
        if is_deleted(request_file_path, request_file.sha256, instance_manifest):
            need_delete.add(request_file_path)

    return need_delete


def build_download_list(
    request: UpdatePostRequest,
    instance_manifest: InstanceManifest,
    instance_name: str,
    base_url: str,
) -> dict[str, FileDownloadInfo]:
    need_download: dict[str, FileDownloadInfo] = {}
    # Проходим по всем файлам внутри InstanceManifest
    for instance_file_path, instance_file in instance_manifest.files.items():
        download_url = f"{base_url}{settings.INSTANCES_DIR_PATH}/{quote(instance_name)}/{quote(instance_file_path, safe='/')}"
        # Нет файла
        if instance_file_path not in request.files.keys():
            need_download[instance_file_path] = FileDownloadInfo(
                sha256=instance_file.sha256,
                size=instance_file.size,
                url=download_url,
            )
            continue

        request_file = request.files[instance_file_path]

        # SHA совпадает
        if request_file.sha256 == instance_file.sha256:
            continue

        # SHA отличается и это строгое место
        if instance_file_path in instance_manifest.strict_files_paths:
            need_download[instance_file_path] = FileDownloadInfo(
                sha256=instance_file.sha256,
                size=instance_file.size,
                url=download_url,
            )
            continue

        # SHA отличается и это строгое место (например, моды)
        if any(
            instance_file_path.startswith(folder)
            for folder in instance_manifest.strict_dirs_paths
        ):
            need_download[instance_file_path] = FileDownloadInfo(
                sha256=instance_file.sha256,
                size=instance_file.size,
                url=download_url,
            )

    return need_download


def compare_servers(
    request_servers: list[ServerInfo], instance_servers: list[ServerInfo]
) -> list[ServerInfo]:
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


def compare_resourcepacks(
    request_resourcepacks: list[str], instance_resourcepacks: list[str]
) -> list[str]:
    # 1. Создаём копию списка клиента, чтобы не изменять исходный массив
    result = request_resourcepacks

    # 2. Создаём множество из текущих ресурс паков клиента для быстрого поиска (O(1))
    # Также это автоматически убирает возможные дубликаты, если они вдруг были в client_resource_packs
    existing_resource_packs = set(result)

    # 3. Проходим по списку ресурс паков
    for resource_pack in instance_resourcepacks:
        # Если ресурс паков ещё нет у клиента, добавляем его в конец
        if resource_pack not in existing_resource_packs:
            result.append(resource_pack)
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
    new_resourcepacks = compare_resourcepacks(
        request.resourcepacks, instance_manifest.resourcepacks
    )
    new_servers = compare_servers(request.servers, instance_manifest.servers)
    need_delete = build_delete_list(request, instance_manifest)
    need_download = build_download_list(
        request, instance_manifest, instance_name, base_url
    )

    return UpdatePostResponse(
        new_resourcepacks=new_resourcepacks,
        new_servers=new_servers,
        need_delete=need_delete,
        need_download=need_download,
    )
