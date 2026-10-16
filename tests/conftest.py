import json
from pathlib import Path

import pytest

FAKE = Path(__file__).with_name("fake_pyrevit.py")


@pytest.fixture
def fake_cli(monkeypatch, tmp_path):
    """Point vn-revit-mcp at the fake pyrevit CLI; returns a reader for the call log."""
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("VN_REVIT_MCP_PYREVIT", str(FAKE))
    monkeypatch.setenv("FAKE_PYREVIT_LOG", str(log))
    monkeypatch.delenv("FAKE_PYREVIT_SCENARIO", raising=False)
    monkeypatch.delenv("VN_REVIT_MCP_REVIT", raising=False)

    def calls():
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]

    return calls
