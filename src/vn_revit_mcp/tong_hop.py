"""Group raw rows from the Revit scripts into quantity summaries.

Sums use full precision; rounding happens only in ``round_values`` for display.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any, Iterable

# Vietnamese / common names a user may type -> Revit BuiltInCategory.
CATEGORY_ALIASES = {
    "tuong": "OST_Walls", "walls": "OST_Walls",
    "san": "OST_Floors", "floors": "OST_Floors",
    "cua di": "OST_Doors", "cua": "OST_Doors", "doors": "OST_Doors",
    "cua so": "OST_Windows", "windows": "OST_Windows",
    "phong": "OST_Rooms", "rooms": "OST_Rooms",
    "cot": "OST_StructuralColumns", "structural columns": "OST_StructuralColumns",
    "cot kien truc": "OST_Columns", "columns": "OST_Columns",
    "dam": "OST_StructuralFraming", "structural framing": "OST_StructuralFraming",
    "mong": "OST_StructuralFoundation", "structural foundations": "OST_StructuralFoundation",
    "mai": "OST_Roofs", "roofs": "OST_Roofs",
    "tran": "OST_Ceilings", "ceilings": "OST_Ceilings",
    "cau thang": "OST_Stairs", "stairs": "OST_Stairs",
    "lan can": "OST_StairsRailing", "railings": "OST_StairsRailing",
    "noi that": "OST_Furniture", "furniture": "OST_Furniture",
    "thiet bi ve sinh": "OST_PlumbingFixtures", "plumbing fixtures": "OST_PlumbingFixtures",
    "mo hinh chung": "OST_GenericModel", "generic models": "OST_GenericModel",
}
_BIC_PATTERN = re.compile(r"^OST_[A-Za-z0-9]{2,60}$")
_VN_MAP = str.maketrans(
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
    "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd",
)


def normalize(text: str) -> str:
    return " ".join(text.lower().translate(_VN_MAP).split())


def resolve_category(text: str) -> str:
    """Accept 'OST_Doors' or a Vietnamese/English alias; reject anything else."""
    text = (text or "").strip()
    if _BIC_PATTERN.match(text):
        return text
    key = normalize(text)
    if key in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[key]
    raise ValueError(
        "Hạng mục không hợp lệ. Dùng tên BuiltInCategory (ví dụ OST_Doors) hoặc một trong: "
        + ", ".join(sorted(CATEGORY_ALIASES))
    )


def check_parameter_name(name: str) -> str:
    name = (name or "").strip()
    if not name or len(name) > 120 or any(ord(ch) < 32 for ch in name):
        raise ValueError("Tên tham số phải có 1 đến 120 ký tự, không có ký tự điều khiển.")
    return name


def check_ids(ids: Iterable[Any], limit: int = 200) -> list[int]:
    result = []
    for value in ids:
        if isinstance(value, bool):
            raise ValueError("Id phần tử phải là số nguyên.")
        number = int(value)
        if number <= 0:
            raise ValueError("Id phần tử phải là số nguyên dương.")
        result.append(number)
    if not result:
        raise ValueError("Cần ít nhất 1 id phần tử.")
    if len(result) > limit:
        raise ValueError(f"Mỗi lần chỉ sửa tối đa {limit} phần tử.")
    return list(dict.fromkeys(result))


def _add(total: dict[str, Any], key: str, value: Any) -> None:
    if value is None:
        return
    total[key] = (total.get(key) or 0.0) + float(value)


def group_rows(rows: list[dict[str, Any]], keys: tuple[str, ...], sums: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: "OrderedDict[tuple, dict[str, Any]]" = OrderedDict()
    for row in rows:
        group_key = tuple(row.get(k) for k in keys)
        group = groups.get(group_key)
        if group is None:
            group = {k: row.get(k) for k in keys}
            group["so_luong"] = 0
            for s in sums:
                group[s] = None
            groups[group_key] = group
        group["so_luong"] += 1
        for s in sums:
            _add(group, s, row.get(s))
    return list(groups.values())


def round_values(data: Any, digits: int = 2) -> Any:
    if isinstance(data, float):
        return round(data, digits)
    if isinstance(data, list):
        return [round_values(item, digits) for item in data]
    if isinstance(data, dict):
        return {key: round_values(value, digits) for key, value in data.items()}
    return data


def totals(rows: list[dict[str, Any]], sums: tuple[str, ...]) -> dict[str, Any]:
    total: dict[str, Any] = {"so_luong": len(rows)}
    for s in sums:
        total[s] = None
        for row in rows:
            _add(total, s, row.get(s))
    return total


def tong_hop_tuong(result: dict[str, Any]) -> dict[str, Any]:
    rows = result.get("rows", [])
    sums = ("length_m", "area_m2", "volume_m3")
    return {
        "theo_loai_va_tang": group_rows(rows, ("type", "level", "kind", "thickness_mm"), sums),
        "tong": totals([r for r in rows if r.get("kind") != "curtain"], sums),
        "tong_vach_kinh": totals([r for r in rows if r.get("kind") == "curtain"], sums),
        "bo_qua_tuong_xep_chong_cha": result.get("skipped_stacked_parents", 0),
        "tuong_in_place": result.get("in_place", 0),
        "bi_cat_bot": bool(result.get("truncated")),
    }


def tong_hop_san(result: dict[str, Any]) -> dict[str, Any]:
    rows = result.get("rows", [])
    sums = ("area_m2", "volume_m3")
    return {
        "theo_loai_va_tang": group_rows(rows, ("type", "level", "structural", "thickness_mm"), sums),
        "tong": totals(rows, sums),
        "bi_cat_bot": bool(result.get("truncated")),
    }


def tong_hop_ket_cau(result: dict[str, Any]) -> dict[str, Any]:
    rows = result.get("rows", [])
    return {
        "theo_vat_lieu": group_rows(rows, ("kind", "material"), ("volume_m3",)),
        "theo_loai": group_rows(rows, ("kind", "type", "material", "level"), ("volume_m3", "length_m")),
        "tong_the_tich_m3": totals(rows, ("volume_m3",))["volume_m3"],
        "bi_cat_bot": bool(result.get("truncated")),
    }


def _round_mm(value: Any) -> Any:
    return round(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else value


def tong_hop_cua(result: dict[str, Any]) -> dict[str, Any]:
    # Round sizes to 1 mm first so 900.0000001 and 900.0 fall in the same group.
    rows = [dict(r, width_mm=_round_mm(r.get("width_mm")), height_mm=_round_mm(r.get("height_mm")))
            for r in result.get("rows", [])]
    by_type = group_rows(rows, ("kind", "family", "type", "width_mm", "height_mm"), ())
    for group in by_type:
        levels = OrderedDict()
        for row in rows:
            if all(row.get(k) == group.get(k) for k in ("kind", "family", "type", "width_mm", "height_mm")):
                levels[row.get("level") or ""] = levels.get(row.get("level") or "", 0) + 1
        group["theo_tang"] = dict(levels)
    return {
        "theo_loai": by_type,
        "so_cua_di": sum(1 for r in rows if r.get("kind") == "door"),
        "so_cua_so": sum(1 for r in rows if r.get("kind") == "window"),
        "khong_co_ky_hieu": [r.get("id") for r in rows if not r.get("mark")][:200],
        "bi_cat_bot": bool(result.get("truncated")),
    }


def tong_hop_phong(result: dict[str, Any]) -> dict[str, Any]:
    rows = result.get("rows", [])
    placed = [r for r in rows if r.get("status") == "ok"]
    return {
        "phong": rows,
        "theo_tang": group_rows(placed, ("level",), ("area_m2",)),
        "tong_dien_tich_m2": totals(placed, ("area_m2",))["area_m2"],
        "chua_dat_vi_tri": [r.get("id") for r in rows if r.get("status") == "unplaced"],
        "chua_khep_kin": [r.get("id") for r in rows if r.get("status") == "not_enclosed"],
        "bi_cat_bot": bool(result.get("truncated")),
    }
