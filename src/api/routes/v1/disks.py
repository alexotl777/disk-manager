import os
import shlex

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.dto.input import Unmount, Mount, Format
from src.api.dto.output import Disks, CommandResponse
from src.config.settings import Configuration
from src.internal.io.dependencies import disk_service_provider, config_provider
from src.services.disk_service import DiskService


async def get_disks(
    disks_service: DiskService = Depends(disk_service_provider),
) -> JSONResponse:
    out = disks_service.run_cmd("lsblk -b -o NAME,SIZE,MOUNTPOINT -J", check=False)

    if out["returncode"] != 0:
        raise HTTPException(status_code=500, detail=f"lsblk failed: {out['stderr']}")
    try:
        import json

        data = json.loads(out["stdout"])
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse lsblk output")

    devices = []

    def collect(node, parent_name=None):
        name = node.get("name")
        size = node.get("size")
        mount = node.get("mountpoint")
        dev_path = f"/dev/{name}"
        devices.append(
            {"name": name, "device": dev_path, "size": size, "mountpoint": mount}
        )
        for child in node.get("children", []) or []:
            collect(child, name)

    for d in data.get("blockdevices", []):
        collect(d)

    return JSONResponse(
        {"devices": devices, "allowed_prefixes": disks_service.allowed_device_prefixes}
    )


async def make_unmount(
    unmount: Unmount, disks_service: DiskService = Depends(disk_service_provider)
) -> JSONResponse:
    if not disks_service.is_device_allowed(unmount.device):
        raise HTTPException(
            status_code=400,
            detail=f"Device {unmount.device} not allowed by server policy.",
        )
    # umount
    res = disks_service.run_cmd(
        f"sudo umount {shlex.quote(unmount.device)}", check=False
    )
    return JSONResponse(res)


async def make_mount(
    mount: Mount, disks_service: DiskService = Depends(disk_service_provider)
) -> JSONResponse:
    logger.info(f"device: {mount.device}, mount point: {mount.mount_point}")
    if not disks_service.is_device_allowed(mount.device):
        raise HTTPException(
            status_code=400,
            detail=f"Device {mount.device} not allowed by server policy.",
        )

    try:
        os.makedirs(os.path.expanduser(mount.mount_point), exist_ok=True)
    except Exception as e:
        logger.error(f"error for {mount.mount_point} - {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to create mount point: {e}"
        )
    # mount
    res = disks_service.run_cmd(
        f"sudo mount {shlex.quote(mount.device)} {shlex.quote(os.path.expanduser(mount.mount_point))}",
        check=True,
    )
    return JSONResponse(res)


async def make_format(
    format_disk: Format,
    disks_service: DiskService = Depends(disk_service_provider),
    config: Configuration = Depends(config_provider),
) -> JSONResponse:
    if (
        not disks_service.is_device_allowed(format_disk.device)
        and not config.enable_dangerous_ops
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Device not allowed by policy. To format real disks you must set "
                "ALLOWED_DEVICE_PREFIXES env and ENABLE_DANGEROUS_OPS=1."
            ),
        )

    check = disks_service.run_cmd(
        f"lsblk -n -o MOUNTPOINT {shlex.quote(format_disk.device)}", check=False
    )
    if check["stdout"].strip():
        raise HTTPException(
            status_code=400,
            detail=f"Device {format_disk.device} seems mounted: {check['stdout']}. Unmount first.",
        )

    # mkfs
    res = disks_service.run_cmd(
        f"sudo mkfs -t {shlex.quote(format_disk.fstype)} {shlex.quote(format_disk.device)}",
        check=False,
        timeout=300,
    )
    return JSONResponse(res)


def get_disk_router() -> APIRouter:
    router: APIRouter = APIRouter(prefix="/v1/disks", tags=["Disks"])

    router.add_api_route(
        "",
        get_disks,
        methods={
            "GET",
        },
        response_model=Disks,
    )
    router.add_api_route(
        "/unmount",
        make_unmount,
        methods={
            "POST",
        },
        response_model=CommandResponse,
    )
    router.add_api_route(
        "/mount",
        make_mount,
        methods={
            "POST",
        },
        response_model=CommandResponse,
    )
    router.add_api_route(
        "/format",
        make_format,
        methods={
            "POST",
        },
        response_model=CommandResponse,
    )

    return router
