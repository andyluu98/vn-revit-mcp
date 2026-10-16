"""Install the ``ve-revit`` skill for Claude Code and for pyRevit's MCP.

``vn-revit-mcp cai-skill`` copies the skill shipped in this package to:

- ``~/.claude/skills/ve-revit`` (Claude Code reads it),
- ``%APPDATA%/pyRevit/agent/skills/ve-revit`` (pyRevit's ``get_skill`` serves it once user
  skills are enabled with ``pyrevit configs agent skills enable``),
- optionally a workspace folder with the sample plan data modules.

An existing different copy is moved to ``Documents/vn-revit-mcp/_backup`` first, never deleted.
Workspace files that already exist are left untouched.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from datetime import datetime
from importlib import resources
from pathlib import Path

SKILL_NAME = "ve-revit"
_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def skill_source() -> Path:
    return Path(str(resources.files("vn_revit_mcp") / "skills" / SKILL_NAME))


def claude_dir() -> Path:
    return Path.home() / ".claude" / "skills" / SKILL_NAME


def pyrevit_dir() -> Path:
    appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(appdata) / "pyRevit" / "agent" / "skills" / SKILL_NAME


def backup_root() -> Path:
    return Path.home() / "Documents" / "vn-revit-mcp" / "_backup"


def _same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(_same_tree(a / sub, b / sub) for sub in cmp.common_dirs)


def install_skill(dest: Path, source: Path | None = None, backups: Path | None = None) -> str:
    """Copy the skill folder to ``dest``. Returns what happened, in Vietnamese."""
    source = source or skill_source()
    if dest.exists():
        if dest.is_dir() and _same_tree(source, dest):
            return f"Đã có bản mới nhất: {dest}"
        backups = backups or backup_root()
        backups.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%y%m%d-%H%M%S")
        moved = backups / f"{dest.name}_{dest.parent.parent.name}_{stamp}"
        shutil.move(str(dest), str(moved))
        note = f" (bản cũ chuyển vào {moved})"
    else:
        note = ""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, ignore=_IGNORE)
    return f"Đã cài: {dest}{note}"


def copy_workspace(dest: Path, source: Path | None = None) -> list[str]:
    """Copy the sample workspace modules; never overwrite an existing file."""
    source = (source or skill_source()) / "workspace-mau"
    if not dest.is_absolute():
        raise ValueError("Thư mục workspace phải là đường dẫn tuyệt đối.")
    dest.mkdir(parents=True, exist_ok=True)
    lines = []
    for item in sorted(source.glob("*.py")):
        target = dest / item.name
        if target.exists():
            lines.append(f"Giữ nguyên (đã có): {target}")
        else:
            shutil.copy2(item, target)
            lines.append(f"Đã chép: {target}")
    return lines


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="vn-revit-mcp cai-skill",
                                     description="Cài skill ve-revit cho Claude Code và pyRevit.")
    parser.add_argument("--workspace", help="Thư mục tuyệt đối để chép dữ liệu mặt bằng mẫu")
    parser.add_argument("--bo-claude", action="store_true", help="Không cài cho Claude Code")
    parser.add_argument("--bo-pyrevit", action="store_true", help="Không cài cho pyRevit")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        if not args.bo_claude:
            print(install_skill(claude_dir()))
        if not args.bo_pyrevit:
            print(install_skill(pyrevit_dir()))
        if args.workspace:
            for line in copy_workspace(Path(args.workspace).expanduser()):
                print(line)
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    if not args.bo_pyrevit:
        print("Bước tiếp: chạy 'pyrevit configs agent skills enable' để pyRevit đọc skill này, "
              "rồi khởi động lại Revit.")
    return 0
