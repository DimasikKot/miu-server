from typing import List
from urllib.parse import quote

from models import ClientManifest, DownloadFile, ServerManifest, UpdateResponse


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

    server_pack = server_manifest.pack
    if client_manifest.pack.sha256 != server_pack.sha256:

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

    server_instance = server_manifest.instance
    if client_manifest.instance.sha256 != server_instance.sha256:

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

        # SHA отличается
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
        servers=server_manifest.servers,
        resource_packs=server_manifest.resource_packs,
    )
