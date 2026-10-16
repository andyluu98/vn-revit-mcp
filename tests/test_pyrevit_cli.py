import pytest

from vn_revit_mcp import pyrevit_cli
from vn_revit_mcp.pyrevit_cli import PyRevitError


def test_status(fake_cli):
    instances = pyrevit_cli.agent_status()
    assert instances[0]["revit_version"] == "2025"


def test_run_sends_prelude_mode_and_inputs(fake_cli):
    response = pyrevit_cli.run_script("kiem_tra_tham_so", {"category": "OST_Doors", "parameter": "Mark"}, revit="2025")
    assert response["result"]["total"] == 3
    call = fake_cli()[-1]
    assert call["has_prelude"] is True
    assert call["mode"] == "query"
    assert call["inputs"] == {"category": "OST_Doors", "parameter": "Mark"}
    assert "--revit=2025" in call["argv"]


def test_temp_script_is_removed(fake_cli):
    pyrevit_cli.run_script("thong_tin_du_an")
    from pathlib import Path
    assert not Path(fake_cli()[-1]["argv"][2]).exists()


def test_truncated_result_is_read_from_file(fake_cli, monkeypatch):
    monkeypatch.setenv("FAKE_PYREVIT_SCENARIO", "truncated")
    response = pyrevit_cli.run_script("thong_tin_du_an")
    assert response["result"]["title"] == "Nha pho mau"
    assert response["result_truncated"] is False


def test_busy_becomes_structured_error(fake_cli, monkeypatch):
    monkeypatch.setenv("FAKE_PYREVIT_SCENARIO", "busy")
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.run_script("thong_tin_du_an")
    data = info.value.to_dict()
    assert data["loi"] == "revit_busy"
    assert "goi_y" in data


def test_plain_text_busy_gets_hint(fake_cli, monkeypatch):
    monkeypatch.setenv("FAKE_PYREVIT_SCENARIO", "busytext")
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.run_script("thong_tin_du_an")
    assert info.value.code == "revit_busy"
    assert "goi_y" in info.value.to_dict()


def test_modify_timeout_warns_prompt_may_be_open(monkeypatch):
    def slow(args, timeout_s):
        assert timeout_s >= pyrevit_cli.MAX_TIMEOUT_S
        raise PyRevitError("cli_timeout", "het gio")
    monkeypatch.setattr(pyrevit_cli, "_run_cli", slow)
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.run_script("dat_tham_so", {"ids": [1], "parameter": "Comments", "value": "x"}, mode="modify")
    assert info.value.code == "approval_timeout"


def test_batch_file_cli_is_refused(monkeypatch, tmp_path):
    bat = tmp_path / "pyrevit.bat"
    bat.write_text("@echo off", encoding="utf-8")
    monkeypatch.setenv("VN_REVIT_MCP_PYREVIT", str(bat))
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.find_cli()
    assert info.value.code == "cli_not_found"


def test_no_instance(fake_cli, monkeypatch):
    monkeypatch.setenv("FAKE_PYREVIT_SCENARIO", "noinstance")
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.run_script("thong_tin_du_an")
    assert info.value.code == "no_instance"


def test_non_json_output(fake_cli, monkeypatch):
    monkeypatch.setenv("FAKE_PYREVIT_SCENARIO", "nojson")
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.agent_status()
    assert info.value.code == "cli_error"


def test_discard_is_not_an_error(fake_cli, monkeypatch):
    monkeypatch.setenv("FAKE_PYREVIT_SCENARIO", "discard")
    response = pyrevit_cli.run_script("dat_tham_so", {"ids": [1], "parameter": "Comments", "value": "x"}, mode="modify")
    assert response["decision"] == "discarded"


def test_invalid_mode_is_refused(fake_cli):
    with pytest.raises(PyRevitError):
        pyrevit_cli.run_script("thong_tin_du_an", mode="exec")


def test_missing_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("VN_REVIT_MCP_PYREVIT", str(tmp_path / "khong-co.exe"))
    with pytest.raises(PyRevitError) as info:
        pyrevit_cli.find_cli()
    assert info.value.code == "cli_not_found"


def test_result_file_must_be_result_json(tmp_path):
    other = tmp_path / "secret.txt"
    other.write_text("{}", encoding="utf-8")
    with pytest.raises(PyRevitError):
        pyrevit_cli._read_result_file(str(other))
