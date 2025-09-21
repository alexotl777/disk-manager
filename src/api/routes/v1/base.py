from fastapi import APIRouter, Depends, Request

from src.config.settings import Configuration
from src.internal.io.dependencies import config_provider


async def index(request: Request, config: Configuration = Depends(config_provider)):
    return config.templates.TemplateResponse("index.html", {"request": request})


def get_base_router() -> APIRouter:
    router: APIRouter = APIRouter()

    router.add_api_route(
        "/",
        index,
        methods={"GET",}
    )

    return router
