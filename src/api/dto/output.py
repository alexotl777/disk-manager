from pydantic import BaseModel


class Device(BaseModel):
    name: str
    device: str
    size: str
    mountpoint: str


class Disks(BaseModel):
    devices: list[Device] | None = None
    allowed_prefixes: list[str]


class CommandResponse(BaseModel):
    returncode: int
    stdout: str | None = None
    stderr: str | None = None

