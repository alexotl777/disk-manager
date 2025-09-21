import os
from typing import AnyStr

from pydantic_settings import BaseSettings
from pydantic import Field
from fastapi.templating import Jinja2Templates


def get_base_dir() -> AnyStr:
    return os.path.dirname(os.path.abspath(__file__))


def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory=os.path.join(get_base_dir(), "templates"))


def get_allowed_device_prefixes() -> list[str]:
    return os.environ.get("ALLOWED_DEVICE_PREFIXES", "/dev/loop").split(",")


class Configuration(BaseSettings):
    allowed_device_prefixes: list[str] = Field(
        default_factory=get_allowed_device_prefixes
    )
    enable_dangerous_ops: bool | None = Field(
        alias="ENABLE_DANGEROUS_PREFIXES", default=False
    )
    templates: Jinja2Templates = Field(default_factory=get_templates)
    base_dir: AnyStr = Field(default_factory=get_base_dir)
