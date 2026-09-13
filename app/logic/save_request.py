from pathlib import Path
import time

from fastapi import Request

from models.v2 import UpdatePostRequest


def save_request(
    instance_name: Path, request: UpdatePostRequest, request_class: Request
):
    if request_class.client is None:
        return

    host = request_class.client.host
    port = request_class.client.port
    file_path = (
        instance_name
        / "requests"
        / f"{host}={port}{time.strftime(' %Y-%m-%d %H-%M-%S')}.request.json"
    )

    save_temp = UpdatePostRequest(
        resourcepacks=request.resourcepacks,
        incompatible_resourcepacks=request.incompatible_resourcepacks,
        servers=request.servers,
        files={},
    )

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json_str = save_temp.model_dump_json(indent=2, warnings=False)
        f.write(json_str)
