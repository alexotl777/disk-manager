from pydantic import BaseModel


class Unmount(BaseModel):
    device: str


class Mount(Unmount):
    mount_point: str


class Format(Unmount):
    fstype: str
