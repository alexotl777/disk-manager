from src.config.settings import Configuration
import pytest
from src.services.disk_service import DiskService


@pytest.fixture(scope="session")
def disk_service() -> DiskService:
    cfg = Configuration(allowed_device_prefixes=["/dev/loop", "/dev/test"])
    return DiskService(cfg)
