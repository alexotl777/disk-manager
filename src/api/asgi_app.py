from typing import Iterable, Callable, Coroutine, Any
from fastapi import APIRouter, FastAPI
from fastapi.requests import Request
from fastapi.responses import Response


ExceptionHandlers = dict[
    int | type[Exception], Callable[[Request, Any], Coroutine[Any, Any, Response]]
]


def get_asgi_app(
    routes: Iterable[APIRouter], exception_handlers: ExceptionHandlers
) -> FastAPI:
    asgi_app = FastAPI(title="Disk Manager", exception_handlers=exception_handlers)
    for router in routes:
        asgi_app.include_router(
            router, prefix="/api" if router.prefix == "/v1/disks" else ""
        )

    return asgi_app
