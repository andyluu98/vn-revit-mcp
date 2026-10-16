import ast
import importlib.util
import re

import pytest

from vn_revit_mcp import cai_skill
from test_revit_scripts import FORBIDDEN

SKILL = cai_skill.skill_source()
WORKSPACE = SKILL / "workspace-mau"
MODULES = sorted(p.name for p in WORKSPACE.glob("*.py"))


def load(name):
    spec = importlib.util.spec_from_file_location(name[:-3], WORKSPACE / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skill_front_matter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\nname: (.+)\ndescription: (.+)\n---\n", text)
    assert match and match.group(1) == "ve-revit"
    assert "—" not in text and "–" not in text


@pytest.mark.parametrize("name", MODULES)
def test_workspace_module_runs_on_ironpython27(name):
    source = (WORKSPACE / name).read_text(encoding="utf-8")
    source.encode("ascii")
    for node in ast.walk(ast.parse(source)):
        for kind, label in FORBIDDEN.items():
            assert not isinstance(node, kind), f"{name}: {label}"
        if isinstance(node, ast.FunctionDef):
            assert node.returns is None and not node.args.kwonlyargs
            assert all(a.annotation is None for a in node.args.args)


def test_units():
    u = load("vn_don_vi.py")
    assert u.ft(304.8) == 1.0
    assert u.mm(u.ft(3600)) == pytest.approx(3600)
    assert u.chu_nhat(0, 0, 304.8, 609.6) == [(0, 0), (1, 0), (1, 2), (0, 2)]


def test_sample_plan_is_consistent():
    plan = load("nha_pho_mau.py")
    assert plan.kiem_tra() == []


def test_plan_check_catches_door_too_close_to_junction():
    plan = load("nha_pho_mau.py")
    doors = [dict(plan.CUA[2], vi_tri=(2200, 11000))]  # 300 mm from the T1-ngan-3 junction
    problems = plan.kiem_tra(cua=doors)
    assert problems and "diem noi" in problems[0]


def test_plan_check_catches_door_off_wall_and_bad_level():
    plan = load("nha_pho_mau.py")
    assert "lech truc" in plan.kiem_tra(cua=[dict(plan.CUA[0], vi_tri=(2500, 300))])[0]
    walls = plan.TUONG + [dict(plan.TUONG[0], ten="X", tang="Tang 9")]
    assert any("Tang 9" in p for p in plan.kiem_tra(tuong=walls))


def test_install_never_deletes_old_copy(tmp_path):
    dest = tmp_path / "skills" / "ve-revit"
    backups = tmp_path / "_backup"
    assert cai_skill.install_skill(dest, backups=backups).startswith("Đã cài")
    assert (dest / "SKILL.md").is_file()
    assert not list(dest.rglob("__pycache__"))
    assert cai_skill.install_skill(dest, backups=backups).startswith("Đã có bản mới nhất")

    (dest / "SKILL.md").write_text("ban sua tay", encoding="utf-8")
    message = cai_skill.install_skill(dest, backups=backups)
    assert "bản cũ chuyển vào" in message
    old = next(backups.iterdir())
    assert (old / "SKILL.md").read_text(encoding="utf-8") == "ban sua tay"
    assert (dest / "SKILL.md").read_text(encoding="utf-8") != "ban sua tay"


def test_workspace_copy_keeps_existing_files(tmp_path):
    (tmp_path / "nha_pho_mau.py").write_text("# du lieu that", encoding="utf-8")
    lines = cai_skill.copy_workspace(tmp_path)
    assert (tmp_path / "nha_pho_mau.py").read_text(encoding="utf-8") == "# du lieu that"
    assert (tmp_path / "vn_don_vi.py").is_file()
    assert any(line.startswith("Giữ nguyên") for line in lines)


def test_workspace_must_be_absolute():
    with pytest.raises(ValueError):
        cai_skill.copy_workspace(cai_skill.Path("tuong-doi"))
