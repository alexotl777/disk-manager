import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles

from src.api.asgi_app import get_asgi_app
from src.api.exception_handlers import exception_handler
from src.api.routes import get_routes
from src.config.settings import Configuration
from src.internal.io import dependencies
from src.services.disk_service import DiskService


def get_app() -> FastAPI:
    config = Configuration()
    disk_service = DiskService(config)

    app = get_asgi_app(
        routes=get_routes(),
        exception_handlers={
            Exception: exception_handler
        }
    )
    app.mount("/static", StaticFiles(directory=os.path.join(config.base_dir, "static")), name="static")
    app.dependency_overrides = {
        dependencies.config_provider: lambda: config,
        dependencies.disk_service_provider: lambda: disk_service
    }

    return app
