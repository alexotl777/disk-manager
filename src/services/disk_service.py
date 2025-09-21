import shlex
import subprocess
import traceback
from typing import Any

from loguru import logger

from src.config.settings import Configuration


class DiskService:
    def __init__(self, config: Configuration) -> None:
        self.allowed_device_prefixes = config.allowed_device_prefixes

    def is_device_allowed(self, dev: str) -> bool:
        dev = dev.strip()
        for p in self.allowed_device_prefixes:
            logger.debug(f"Allowed prefix: {p}")
            if p and dev.startswith(p):
                return True
        return False

    @staticmethod
    def run_cmd(cmd: str, check: bool = True, timeout: int = 30) -> dict[str, Any]:
        args = shlex.split(cmd)
        try:
            completed = subprocess.run(args, capture_output=True, text=True, check=check, timeout=timeout)
            return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
        except subprocess.CalledProcessError as e:
            logger.error(traceback.format_exc())
            return {"returncode": e.returncode, "stdout": e.stdout or "", "stderr": e.stderr or ""}
        except subprocess.TimeoutExpired as e:
            logger.error(traceback.format_exc())
            return {"returncode": -1, "stdout": e.stdout or "", "stderr": "timeout"}
