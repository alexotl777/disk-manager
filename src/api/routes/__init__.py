from fastapi import APIRouter
from src.api.routes.v1.base import get_base_router
from src.api.routes.v1.disks import get_disk_router


def get_routes() -> list[APIRouter]:
    return [get_disk_router(), get_base_router()]
