from models.v2 import (
    UpdatePostRequest as UpdatePostRequestV2,
    UpdatePostResponse as UpdatePostResponseV2,
)
from models.v2.server import InstanceManifest as InstanceManifestV2
from models.v3 import (
    UpdatePostRequest as UpdatePostRequestV3,
    UpdatePostResponse as UpdatePostResponseV3,
)
from models.v3.server import InstanceManifest as InstanceManifestV3


def InstanceManifestV2toV3(data: InstanceManifestV2) -> InstanceManifestV3:
    data_v3 = InstanceManifestV3(
        version=data.version,
        api_version=3,
        files_paths=data.files_paths,
        dirs_paths=data.dirs_paths,
        strict_files_paths=data.strict_files_paths,
        strict_dirs_paths=data.strict_dirs_paths,
        resourcepacks=data.resourcepacks,
        incompatible_resourcepacks=data.incompatible_resourcepacks,
        servers=data.servers,
        deleted=data.deleted,
        files=data.files,
        waypoints={},
    )

    return data_v3


def UpdatePostRequestV2toV3(data: UpdatePostRequestV2) -> UpdatePostRequestV3:
    data_v3 = UpdatePostRequestV3(
        resourcepacks=data.resourcepacks,
        incompatible_resourcepacks=data.incompatible_resourcepacks,
        servers=data.servers,
        waypoints={},
        files=data.files,
    )

    return data_v3


def UpdatePostResponseV3toV2(data: UpdatePostResponseV3) -> UpdatePostResponseV2:
    data_v2 = UpdatePostResponseV2(
        need_download=data.need_download,
        need_delete=data.need_delete,
        new_servers=data.new_servers,
        new_resourcepacks=data.new_resourcepacks,
        new_incompatible_resourcepacks=data.new_incompatible_resourcepacks,
    )

    return data_v2
