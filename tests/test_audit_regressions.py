import os
import subprocess
import sys
from pathlib import Path

import pytest

from interface.execution import (
    _managed_run_dir,
    cancel_managed_buy,
    managed_task_status,
)
from util.Storage.KVDatabase import KVDatabase


@pytest.mark.parametrize(
    ("stored", "expected"),
    [
        ("false", False),
        ("0", False),
        ("true", True),
        ("1", True),
        (False, False),
        (True, True),
    ],
)
def test_kv_database_parses_serialized_booleans(stored, expected):
    database = KVDatabase(None)
    database.insert("flag", stored)

    assert database.get_as_bool("flag", default=not expected) is expected


def test_managed_run_id_must_resolve_inside_runs_root(tmp_path):
    runs_root = tmp_path / "runs"
    runs_root.mkdir()

    assert _managed_run_dir(runs_root, "a_valid_run-1") == runs_root / "a_valid_run-1"
    with pytest.raises(ValueError, match="invalid run_id"):
        _managed_run_dir(runs_root, "../escaped-run")

    assert managed_task_status("../escaped-run", runs_root=runs_root)["error"] == "invalid run_id"
    assert cancel_managed_buy("../escaped-run", runs_root=runs_root)["error"] == "invalid run_id"


def test_help_is_safe_when_parent_console_uses_gbk():
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "gbk"
    environment["BTB_SKIP_INITIAL_TIME_SYNC"] = "1"

    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        cwd=project_root,
        env=environment,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert b"usage:" in result.stdout.lower()
