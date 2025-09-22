import types

from src.services.disk_service import DiskService
import pytest

import subprocess


@pytest.mark.parametrize(
    "devices, expected",
    ((("/dev/loop0", "/dev/test123"), True), (("/dev/sda1", ""), False)),
)
def test_is_device_allowed_true(
    devices: list[str], expected: bool, disk_service: DiskService
) -> None:
    for device in devices:
        assert disk_service.is_device_allowed(device) == expected


def test_run_cmd_success(monkeypatch):
    """Проверяем успешный результат subprocess.run"""

    def fake_run(args, capture_output, text, check, timeout):
        # эмулируем subprocess.CompletedProcess
        cp = types.SimpleNamespace()
        cp.returncode = 0
        cp.stdout = "ok"
        cp.stderr = ""
        return cp

    monkeypatch.setattr("subprocess.run", fake_run)

    res = DiskService.run_cmd("echo ok")
    assert res["returncode"] == 0
    assert res["stdout"] == "ok"


def test_run_cmd_calledprocesserror(monkeypatch):
    """Проверяем ошибочный результат (CalledProcessError)"""

    def fake_run(args, capture_output, text, check, timeout):
        raise subprocess.CalledProcessError(
            returncode=1, cmd=args, output="some out", stderr="some err"
        )

    monkeypatch.setattr("subprocess.run", fake_run)

    res = DiskService.run_cmd("false")
    assert res["returncode"] == 1
    assert "some" in res["stdout"] and "some" in res["stderr"]


def test_run_cmd_timeout(monkeypatch):
    """Проверяем обработку таймаута"""

    def fake_run(args, capture_output, text, check, timeout):
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout, output="time out")

    monkeypatch.setattr("subprocess.run", fake_run)

    res = DiskService.run_cmd("sleep 10")
    assert res["returncode"] == -1
    assert res["stderr"] == "timeout"
