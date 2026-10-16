"""Run the fixed vn-revit-mcp scripts through the pyRevit 7 agent CLI.

Every call goes through ``pyrevit agent run``: pyRevit's in-Revit host executes the
script on Revit's main thread inside a guarded transaction group, rolls queries back,
and asks the user in Revit before a modify run is committed (policy ``ask``).

Only scripts shipped in ``revit_scripts/`` can be run; no caller-supplied code.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from importlib import resources
from pathlib import Path
from typing import Any

SCRIPTS = frozenset({
    "thong_tin_du_an",
    "dem_theo_hang_muc",
    "thong_ke_cua",
    "thong_ke_phong",
    "khoi_luong_tuong",
    "khoi_luong_san",
    "khoi_luong_ket_cau",
    "kiem_tra_tham_so",
    "dat_tham_so",
})
MODES = frozenset({"query", "dry_run", "modify"})
DEFAULT_TIMEOUT_S = 300
MAX_TIMEOUT_S = 3600
# Extra seconds the CLI may need on top of the run timeout (connect, approval prompt).
CLI_GRACE_S = 120
MAX_RESULT_FILE_BYTES = 50 * 1024 * 1024

ERROR_HINTS = {
    "cli_not_found": "Chưa tìm thấy lệnh pyrevit. Cài pyRevit 7.0 trở lên, mở cửa sổ dòng lệnh mới, "
                     "hoặc đặt biến môi trường VN_REVIT_MCP_PYREVIT trỏ tới pyrevit.exe.",
    "no_instance": "Không có Revit nào đang chạy agent host. Bật bằng 'pyrevit configs agent enable', "
                   "khởi động lại Revit và mở một mô hình.",
    "revit_busy": "Revit đang bận (đang chạy lệnh khác hoặc có hộp thoại đang mở). Đóng hộp thoại rồi thử lại.",
    "no_active_document": "Chưa có mô hình nào đang mở trong Revit.",
    "policy_readonly": "pyRevit đang ở chế độ chỉ đọc. Muốn sửa mô hình: 'pyrevit configs agent policy ask'.",
    "timeout": "Script chạy quá thời gian. Thử lại với mô hình nhỏ hơn hoặc tăng thời gian chờ.",
    "engine_unavailable": "Engine Python được yêu cầu không có trong bản pyRevit này.",
    "query_modified_model": "Script chỉ đọc đã làm đổi mô hình nên bị hoàn tác. Hãy báo lỗi cho tác giả.",
    "cli_timeout": "Lệnh pyrevit không trả lời kịp. Kiểm tra Revit có đang treo hoặc chờ hộp thoại không.",
    "approval_timeout": "Hộp duyệt Giữ/Hủy có thể vẫn đang mở trong Revit. Nếu bấm Giữ, thay đổi vẫn được lưu: "
                        "kiểm tra danh sách Undo trong Revit trước khi chạy lại.",
    "ambiguous_revit": "Đang mở nhiều Revit. Truyền tham số 'revit' (năm hoặc số process) "
                       "hoặc đặt biến môi trường VN_REVIT_MCP_REVIT.",
    "document_read_only": "Mô hình đang mở ở chế độ chỉ đọc nên không sửa được.",
    "cli_error": "Lệnh pyrevit báo lỗi. Xem chi tiết trong 'chi_tiet'.",
}

# The CLI prints plain text (not JSON) for host-side errors; map known phrases to codes.
TEXT_ERRORS = (
    ("no_instance", ("agent host", "no running revit", "no revit")),
    ("revit_busy", ("busy", "another transaction")),
    ("no_active_document", ("active document",)),
    ("ambiguous_revit", ("several revit", "multiple revit", "more than one revit", "ambiguous")),
    ("document_read_only", ("read-only document", "document is read-only", "read only document")),
)


class PyRevitError(Exception):
    """A failure that the MCP tool turns into a structured, Vietnamese error."""

    def __init__(self, code: str, message: str, detail: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"loi": self.code, "thong_bao": self.message}
        hint = ERROR_HINTS.get(self.code)
        if hint:
            data["goi_y"] = hint
        if self.detail:
            data["chi_tiet"] = self.detail[-2000:]
        return data


def _candidate_paths() -> list[Path]:
    paths = []
    for env in ("APPDATA", "PROGRAMFILES", "PROGRAMDATA"):
        base = os.environ.get(env)
        if base:
            paths.append(Path(base) / "pyRevit-Master" / "bin" / "pyrevit.exe")
            paths.append(Path(base) / "pyRevit CLI" / "pyrevit.exe")
    return paths


def _allowed_cli(path: str) -> bool:
    # .bat/.cmd would run through cmd.exe, where AI-supplied --inputs could inject commands.
    # .py is only the test suite's fake pyRevit.
    return Path(path).suffix.lower() in (".exe", ".py")


def find_cli() -> str:
    """Path of pyrevit.exe: env override, then PATH, then the usual install folders."""
    override = os.environ.get("VN_REVIT_MCP_PYREVIT")
    if override:
        if not Path(override).is_file():
            raise PyRevitError("cli_not_found", f"VN_REVIT_MCP_PYREVIT không trỏ tới file có thật: {override}")
        if not _allowed_cli(override):
            raise PyRevitError("cli_not_found", f"VN_REVIT_MCP_PYREVIT phải trỏ tới pyrevit.exe: {override}")
        return override
    found = shutil.which("pyrevit")
    if found and _allowed_cli(found):
        return found
    for path in _candidate_paths():
        if path.is_file():
            return str(path)
    raise PyRevitError("cli_not_found", "Không tìm thấy pyrevit.exe.")


def _command(cli: str, args: list[str]) -> list[str]:
    # A .py "CLI" is only used by the test suite's fake pyRevit.
    if cli.lower().endswith(".py"):
        return [sys.executable, cli, *args]
    return [cli, *args]


def _run_cli(args: list[str], timeout_s: float) -> subprocess.CompletedProcess:
    cli = find_cli()
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        return subprocess.run(  # noqa: S603  (fixed argv, no shell)
            _command(cli, args),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PyRevitError("cli_timeout", f"Lệnh pyrevit chạy quá {int(timeout_s)} giây.") from exc
    except OSError as exc:
        raise PyRevitError("cli_not_found", f"Không chạy được pyrevit: {exc}") from exc


def _parse_json(text: str, opener: str, closer: str) -> Any:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def agent_status() -> list[dict[str, Any]]:
    """Running Revit sessions that have the pyRevit agent host."""
    proc = _run_cli(["agent", "status", "--json"], timeout_s=60)
    try:
        data = _parse_json(proc.stdout, "[", "]")
    except ValueError as exc:
        raise PyRevitError(
            "cli_error",
            "pyrevit không trả JSON cho 'agent status'. Có thể bản pyRevit cũ hơn 7.0.",
            (proc.stdout or "") + (proc.stderr or ""),
        ) from exc
    if not isinstance(data, list):
        raise PyRevitError("cli_error", "Kết quả 'agent status' không đúng dạng.", proc.stdout)
    return data


def script_source(name: str) -> str:
    """Prelude + script body, exactly what is sent to Revit."""
    if name not in SCRIPTS:
        raise PyRevitError("invalid_script", f"Script không có trong danh sách: {name}")
    package = resources.files("vn_revit_mcp") / "revit_scripts"
    prelude = (package / "_prelude.py").read_text(encoding="utf-8")
    body = (package / f"{name}.py").read_text(encoding="utf-8")
    return prelude + "\n" + body


def classify_text_error(output: str) -> str:
    """Best-effort error code for the CLI's plain-text error output."""
    lowered = (output or "").lower()
    for code, phrases in TEXT_ERRORS:
        if any(phrase in lowered for phrase in phrases):
            return code
    return "cli_error"


def _read_result_file(path_text: str) -> Any:
    path = Path(path_text)
    if path.name != "result.json" or not path.is_file():
        raise PyRevitError("cli_error", "Kết quả lớn được ghi ra file nhưng không đọc được.", path_text)
    if path.stat().st_size > MAX_RESULT_FILE_BYTES:
        raise PyRevitError("cli_error", "Kết quả quá lớn (trên 50 MB).", path_text)
    return json.loads(path.read_text(encoding="utf-8"))


def run_script(
    name: str,
    inputs: dict[str, Any] | None = None,
    mode: str = "query",
    revit: str | None = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    title: str | None = None,
) -> dict[str, Any]:
    """Run one shipped script and return pyRevit's response with ``result`` filled in."""
    if mode not in MODES:
        raise PyRevitError("invalid_mode", f"Chế độ không hợp lệ: {mode}")
    timeout_s = max(1, min(int(timeout_s), MAX_TIMEOUT_S))
    source = script_source(name)

    tmp_dir = Path(tempfile.mkdtemp(prefix="vn-revit-mcp-"))
    script_path = tmp_dir / f"{name}.py"
    try:
        script_path.write_text(source, encoding="utf-8")
        args = [
            "agent", "run", str(script_path),
            f"--mode={mode}",
            f"--title=vn-revit-mcp {name}" if title is None else f"--title={title}",
            "--inputs=" + json.dumps(inputs or {}, ensure_ascii=True),
            f"--timeout={timeout_s}",
        ]
        if revit:
            args.append(f"--revit={revit}")
        # A modify run waits for the Keep/Discard prompt in Revit, so give the user time.
        cli_timeout = (MAX_TIMEOUT_S if mode == "modify" else timeout_s) + CLI_GRACE_S
        try:
            proc = _run_cli(args, timeout_s=cli_timeout)
        except PyRevitError as exc:
            if exc.code == "cli_timeout" and mode == "modify":
                raise PyRevitError("approval_timeout", "Không nhận được kết quả từ Revit trong thời gian chờ.") from exc
            raise
    finally:
        try:
            script_path.unlink(missing_ok=True)
            tmp_dir.rmdir()
        except OSError:
            pass

    try:
        response = _parse_json(proc.stdout, "{", "}")
    except ValueError as exc:
        output = (proc.stdout or "") + (proc.stderr or "")
        raise PyRevitError(classify_text_error(output), "pyrevit không trả kết quả JSON.", output) from exc
    if not isinstance(response, dict):
        raise PyRevitError("cli_error", "Kết quả 'agent run' không đúng dạng.", proc.stdout)

    if response.get("result_truncated") and response.get("result_path"):
        response["result"] = _read_result_file(str(response["result_path"]))
        response["result_truncated"] = False

    # "rejected" = the user pressed Discard in Revit, or policy is readonly: not a failure.
    if response.get("status") not in ("ok", "rejected"):
        error = response.get("error") or {}
        code = error.get("type") or "run_failed"
        message = error.get("message") or f"Lần chạy kết thúc với trạng thái {response.get('status')}."
        raise PyRevitError(code, message, error.get("traceback"))
    return response
