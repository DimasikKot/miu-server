from typing import List
from urllib.parse import quote

from models import ClientManifest, DownloadFile, ServerManifest, UpdateResponse


def is_removed(path: str, sha256: str, server: ServerManifest) -> bool:
    # Проверяет, считается ли данный SHA удалённым
    removed = server.removed.get(path, {})
    return sha256 in removed


def build_delete_list(client: ClientManifest, server: ServerManifest) -> List[str]:
    delete = []
    for path, file in client.files.items():

        # Если файла больше нет на сервере,
        # но его SHA находится в removed
        if path not in server.files:
            if is_removed(path, file.sha256, server):
                delete.append(path)
            continue

        # Если SHA клиента совпадает
        # с одним из старых SHA
        if is_removed(path, file.sha256, server):
            delete.append(path)

    return delete


def build_download_list(
    client: ClientManifest, server: ServerManifest, pack: str, base_url: str
) -> List[DownloadFile]:
    download = []
    for path, server_file in server.files.items():

        # Нет файла
        if path not in client.files:
            url = f"{base_url}/files/" f"{quote(pack)}/" f"{quote(path, safe='/')}"

            download.append(
                DownloadFile(
                    path=path, sha256=server_file.sha256, size=server_file.size, url=url
                )
            )

            continue

        client_file = client.files[path]

        # SHA совпадает
        if client_file.sha256 == server_file.sha256:
            continue

        # SHA отличается
        download.append(
            DownloadFile(
                path=path,
                sha256=server_file.sha256,
                size=server_file.size,
                url=f"{base_url}/files/" f"{quote(pack)}/" f"{quote(path, safe='/')}",
            )
        )

    return download


def compare(
    pack: str, client: ClientManifest, server: ServerManifest, base_url: str
) -> UpdateResponse:
    download = build_download_list(client, server, pack, base_url)
    delete = build_delete_list(client, server)

    return UpdateResponse(
        version=server.version, download=download, delete=delete, servers=server.servers
    )
