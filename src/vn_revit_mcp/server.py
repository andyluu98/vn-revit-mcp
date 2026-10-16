"""vn-revit-mcp: MCP server with fixed Vietnamese tools for Autodesk Revit.

Talks to Revit only through the pyRevit 7 agent CLI (``pyrevit agent ...``), which
reaches the in-Revit host over a local named pipe. No network port is opened.
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Callable

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from . import __version__, excel, pyrevit_cli, tong_hop
from .pyrevit_cli import PyRevitError

INSTRUCTIONS = """\
vn-revit-mcp đọc mô hình Revit đang mở qua pyRevit (agent runtime) và trả số liệu đã đổi sang mét.

Quy tắc:
- Gọi kiem_tra_ket_noi trước. Không có Revit nào thì hướng dẫn người dùng theo 'goi_y'.
- Số liệu lấy từ mô hình Revit, chưa phải bản vẽ phát hành. Khi báo cáo, ghi rõ nguồn là mô hình Revit.
- Không tự điền đơn giá, hao hụt. Chỗ thiếu ghi [Chờ bổ sung].
- dat_tham_so sửa mô hình: mặc định chỉ chạy thử (dry_run). Chỉ chạy thật khi người dùng đồng ý rõ ràng;
  khi đó Revit còn hiện hộp duyệt Giữ/Hủy để người dùng quyết định.
- Mọi công cụ nhận tham số tùy chọn 'revit' (năm, ví dụ "2025", hoặc số process) khi mở nhiều Revit.
- Vẽ, dựng mô hình (tường, sàn, cửa...): vn-revit-mcp không vẽ. Dùng MCP của pyRevit (run_modify)
  theo skill ve-revit, rồi quay lại đây kiểm khối lượng.
"""

mcp = MCPServer(name="vn-revit-mcp", instructions=INSTRUCTIONS, version=__version__)

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
WRITES_FILE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
MODIFIES_MODEL = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=False)


def _revit(revit: str | None) -> str | None:
    value = (revit or os.environ.get("VN_REVIT_MCP_REVIT") or "").strip()
    if not value:
        return None
    if not value.isdigit() or len(value) > 10:
        raise ValueError("Tham số 'revit' phải là năm (ví dụ 2025) hoặc số process.")
    return value


async def _call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    return await asyncio.to_thread(func, *args, **kwargs)


async def _query(name: str, revit: str | None, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    response = await _call(pyrevit_cli.run_script, name, inputs or {}, "query", _revit(revit))
    result = response.get("result") or {}
    if response.get("warnings") and isinstance(result, dict):
        result["canh_bao_pyrevit"] = response["warnings"]
    return result


def _error(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, PyRevitError):
        return exc.to_dict()
    if isinstance(exc, ValueError):
        return {"loi": "dau_vao_khong_hop_le", "thong_bao": str(exc)}
    return {"loi": "loi_khong_ro", "thong_bao": f"{type(exc).__name__}: {exc}"}


def _round(data: Any) -> Any:
    return tong_hop.round_values(data, 2)


@mcp.tool(annotations=READ_ONLY)
async def kiem_tra_ket_noi() -> dict[str, Any]:
    """Kiểm tra pyRevit và các phiên Revit đang chạy agent host. Gọi đầu tiên."""
    try:
        cli = await _call(pyrevit_cli.find_cli)
        instances = await _call(pyrevit_cli.agent_status)
    except Exception as exc:  # noqa: BLE001
        return _error(exc)
    data: dict[str, Any] = {"pyrevit": cli, "phien_revit": instances, "phien_ban_mcp": __version__}
    if not instances:
        data["goi_y"] = pyrevit_cli.ERROR_HINTS["no_instance"]
    return data


@mcp.tool(annotations=READ_ONLY)
async def thong_tin_du_an(revit: str | None = None) -> dict[str, Any]:
    """Tên mô hình, phiên bản Revit, danh sách tầng (cao độ m), view đang mở, phase."""
    try:
        return _round(await _query("thong_tin_du_an", revit))
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def dem_theo_hang_muc(revit: str | None = None) -> dict[str, Any]:
    """Đếm số phần tử mô hình theo từng hạng mục (category)."""
    try:
        return await _query("dem_theo_hang_muc", revit)
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def thong_ke_cua(revit: str | None = None, chi_tiet: bool = False) -> dict[str, Any]:
    """Thống kê cửa đi, cửa sổ theo family, loại, kích thước (mm) và tầng.

    chi_tiet=True trả thêm từng cửa (id, tầng, cao bệ, ký hiệu).
    """
    try:
        result = await _query("thong_ke_cua", revit)
        data = tong_hop.tong_hop_cua(result)
        if chi_tiet:
            data["chi_tiet"] = result.get("rows", [])
        return _round(data)
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def thong_ke_phong(revit: str | None = None) -> dict[str, Any]:
    """Danh sách phòng: số, tên, tầng, diện tích (m2), chu vi (m); tổng theo tầng; phòng lỗi."""
    try:
        return _round(tong_hop.tong_hop_phong(await _query("thong_ke_phong", revit)))
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def khoi_luong_tuong(revit: str | None = None) -> dict[str, Any]:
    """Khối lượng tường theo loại và tầng: chiều dài (m), diện tích (m2), thể tích (m3), độ dày (mm)."""
    try:
        return _round(tong_hop.tong_hop_tuong(await _query("khoi_luong_tuong", revit)))
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def khoi_luong_san(revit: str | None = None) -> dict[str, Any]:
    """Khối lượng sàn theo loại và tầng: diện tích (m2), thể tích (m3), độ dày (mm)."""
    try:
        return _round(tong_hop.tong_hop_san(await _query("khoi_luong_san", revit)))
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def khoi_luong_ket_cau(revit: str | None = None) -> dict[str, Any]:
    """Thể tích (m3) cột, dầm, móng kết cấu theo vật liệu và loại."""
    try:
        return _round(tong_hop.tong_hop_ket_cau(await _query("khoi_luong_ket_cau", revit)))
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@mcp.tool(annotations=READ_ONLY)
async def kiem_tra_tham_so(hang_muc: str, tham_so: str, revit: str | None = None) -> dict[str, Any]:
    """Tìm phần tử của một hạng mục chưa có hoặc để trống một tham số.

    hang_muc: tên BuiltInCategory (OST_Doors) hoặc tên quen dùng (cua, tuong, phong, cot, dam...).
    tham_so: tên tham số đúng như trong Revit, ví dụ "Mark" hoặc "Comments".
    """
    try:
        inputs = {"category": tong_hop.resolve_category(hang_muc), "parameter": tong_hop.check_parameter_name(tham_so)}
        data = await _query("kiem_tra_tham_so", revit, inputs)
    except Exception as exc:  # noqa: BLE001
        return _error(exc)
    if data.get("category_found") is False:
        data["goi_y"] = f"Revit bản này không có hạng mục {inputs['category']}. Kiểm tra lại tên OST_."
    return data


@mcp.tool(annotations=WRITES_FILE)
async def xuat_excel_khoi_luong(thu_muc: str | None = None, revit: str | None = None) -> dict[str, Any]:
    """Xuất bảng khối lượng (tường, sàn, kết cấu, cửa, phòng) ra file Excel.

    thu_muc: thư mục tuyệt đối để lưu; bỏ trống thì lưu vào Documents\\vn-revit-mcp.
    File đánh số NN_ và không bao giờ ghi đè. Hao hụt và mã hiệu để trống cho kỹ sư điền.
    Chỉ đọc mô hình, không sửa gì trong Revit.
    """
    try:
        folder = excel.check_folder(thu_muc)
        project = await _query("thong_tin_du_an", revit)
        tuong = tong_hop.tong_hop_tuong(await _query("khoi_luong_tuong", revit))
        san = tong_hop.tong_hop_san(await _query("khoi_luong_san", revit))
        ket_cau = tong_hop.tong_hop_ket_cau(await _query("khoi_luong_ket_cau", revit))
        cua = tong_hop.tong_hop_cua(await _query("thong_ke_cua", revit))
        phong = tong_hop.tong_hop_phong(await _query("thong_ke_phong", revit))
        path = await _call(excel.write_boq, folder, project, tuong, san, ket_cau, cua, phong)
    except Exception as exc:  # noqa: BLE001
        return _error(exc)
    return {
        "file": str(path),
        "mo_hinh": project.get("title"),
        "ghi_chu": "Khối lượng lấy từ mô hình Revit; đối chiếu bản vẽ trước khi dùng. Hao hụt và mã hiệu [Chờ bổ sung].",
    }


@mcp.tool(annotations=MODIFIES_MODEL)
async def dat_tham_so(ids: list[int], tham_so: str, gia_tri: str, chay_thu: bool = True,
                      revit: str | None = None) -> dict[str, Any]:
    """Gán giá trị cho một tham số trên tối đa 200 phần tử.

    chay_thu=True (mặc định): chỉ xem trước, mô hình được hoàn tác.
    chay_thu=False: sửa thật; Revit hiện hộp duyệt, người dùng bấm Giữ hoặc Hủy.
    Tham số độ dài, diện tích nhận giá trị theo đơn vị hiển thị của dự án (ví dụ "2500" mm).
    Chỉ dùng chay_thu=False khi người dùng đã đồng ý rõ ràng.
    """
    try:
        inputs = {
            "ids": tong_hop.check_ids(ids),
            "parameter": tong_hop.check_parameter_name(tham_so),
            "value": str(gia_tri)[:500],
        }
        mode = "dry_run" if chay_thu else "modify"
        response = await _call(pyrevit_cli.run_script, "dat_tham_so", inputs, mode, _revit(revit))
    except Exception as exc:  # noqa: BLE001
        return _error(exc)
    decision = response.get("decision")
    meaning = {
        "rolled_back": "Chạy thử xong, mô hình đã được hoàn tác.",
        "committed": "Đã lưu thay đổi vào mô hình (một mục Undo).",
        "discarded": "Người dùng đã bấm Hủy trong Revit, mô hình không đổi.",
        "no_changes": "Không có phần tử nào đổi.",
    }.get(decision, f"Quyết định: {decision}")
    if response.get("status") == "rejected" and decision != "discarded":
        meaning = "pyRevit đang ở chế độ chỉ đọc nên không sửa. Đổi: pyrevit configs agent policy ask"
    data = {
        "che_do": mode,
        "ket_qua": meaning,
        "quyet_dinh": decision,
        "chi_tiet": response.get("result"),
    }
    if response.get("warnings") or response.get("failures"):
        data["canh_bao_pyrevit"] = {"warnings": response.get("warnings"), "failures": response.get("failures")}
    return data


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "cai-skill":
        from . import cai_skill
        sys.exit(cai_skill.main(sys.argv[2:]))
    mcp.run("stdio")


if __name__ == "__main__":
    main()
