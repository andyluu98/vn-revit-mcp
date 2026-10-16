# Sample plan data for a 2-storey townhouse (SAMPLE ONLY, not a real project).
# All lengths in mm, plan origin at the front-left axis intersection, x across the
# frontage, y towards the back. Walls are on their axis (location line = centerline).
# Replace this data with the real drawing, then run kiem_tra() before building.
# Must stay valid on IronPython 2.7, IronPython 3.4 and CPython 3 (ASCII only).

TEN_CONG_TRINH = "Nha pho mau 5x15m"
NHAN = "vn:"  # prefix of the Comments tag of every element an agent stage creates

# name, elevation (mm, +-0.000 = finished floor of Tang 1)
TANG = [
    ("Tang 1", 0),
    ("Tang 2", 3600),
    ("Mai", 7200),
]

# Wall types are looked up in the model by thickness; names differ between templates.
TUONG = [
    # name, start, end, thickness, base level, top level
    {"ten": "T1-truoc", "tu": (0, 0), "den": (5000, 0), "day": 200, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T1-phai", "tu": (5000, 0), "den": (5000, 15000), "day": 200, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T1-sau", "tu": (5000, 15000), "den": (0, 15000), "day": 200, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T1-trai", "tu": (0, 15000), "den": (0, 0), "day": 200, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T1-ngan-1", "tu": (0, 6000), "den": (5000, 6000), "day": 100, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T1-ngan-2", "tu": (0, 11000), "den": (5000, 11000), "day": 100, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T1-ngan-3", "tu": (2500, 11000), "den": (2500, 15000), "day": 100, "tang": "Tang 1", "den_tang": "Tang 2"},
    {"ten": "T2-truoc", "tu": (0, 0), "den": (5000, 0), "day": 200, "tang": "Tang 2", "den_tang": "Mai"},
    {"ten": "T2-phai", "tu": (5000, 0), "den": (5000, 15000), "day": 200, "tang": "Tang 2", "den_tang": "Mai"},
    {"ten": "T2-sau", "tu": (5000, 15000), "den": (0, 15000), "day": 200, "tang": "Tang 2", "den_tang": "Mai"},
    {"ten": "T2-trai", "tu": (0, 15000), "den": (0, 0), "day": 200, "tang": "Tang 2", "den_tang": "Mai"},
    {"ten": "T2-ngan-1", "tu": (0, 7500), "den": (5000, 7500), "day": 100, "tang": "Tang 2", "den_tang": "Mai"},
]

# Door and window types are looked up in the model by width x height.
CUA = [
    # kind (cua_di / cua_so), mark, host wall, point on the wall axis, width, height, sill
    {"loai": "cua_di", "ky_hieu": "D1", "tuong": "T1-truoc", "vi_tri": (2500, 0), "rong": 2400, "cao": 2600, "cao_be": 0},
    {"loai": "cua_di", "ky_hieu": "D2", "tuong": "T1-ngan-1", "vi_tri": (1200, 6000), "rong": 900, "cao": 2200, "cao_be": 0},
    {"loai": "cua_di", "ky_hieu": "D3", "tuong": "T1-ngan-2", "vi_tri": (1250, 11000), "rong": 800, "cao": 2200, "cao_be": 0},
    {"loai": "cua_di", "ky_hieu": "D3", "tuong": "T1-ngan-2", "vi_tri": (3750, 11000), "rong": 800, "cao": 2200, "cao_be": 0},
    {"loai": "cua_so", "ky_hieu": "S1", "tuong": "T1-sau", "vi_tri": (1250, 15000), "rong": 1000, "cao": 1200, "cao_be": 900},
    {"loai": "cua_so", "ky_hieu": "S2", "tuong": "T2-truoc", "vi_tri": (2500, 0), "rong": 2400, "cao": 1800, "cao_be": 900},
    {"loai": "cua_di", "ky_hieu": "D2", "tuong": "T2-ngan-1", "vi_tri": (1200, 7500), "rong": 900, "cao": 2200, "cao_be": 0},
    {"loai": "cua_so", "ky_hieu": "S3", "tuong": "T2-sau", "vi_tri": (2500, 15000), "rong": 1400, "cao": 1400, "cao_be": 900},
]

# Floors: closed outline (mm), level, offset above the level (mm).
SAN = [
    {"ten": "San tang 1", "vien": [(0, 0), (5000, 0), (5000, 15000), (0, 15000)], "tang": "Tang 1", "cao_do": 0},
    {"ten": "San tang 2", "vien": [(0, 0), (5000, 0), (5000, 15000), (0, 15000)], "tang": "Tang 2", "cao_do": 0},
    {"ten": "San mai", "vien": [(0, 0), (5000, 0), (5000, 15000), (0, 15000)], "tang": "Mai", "cao_do": 0},
]

# Rooms: a point inside the room (mm), level, number, name.
PHONG = [
    {"so": "101", "ten": "Phong khach", "diem": (2500, 3000), "tang": "Tang 1"},
    {"so": "102", "ten": "Bep an", "diem": (2500, 8500), "tang": "Tang 1"},
    {"so": "103", "ten": "WC", "diem": (1250, 13000), "tang": "Tang 1"},
    {"so": "104", "ten": "Kho", "diem": (3750, 13000), "tang": "Tang 1"},
    {"so": "201", "ten": "Phong ngu 1", "diem": (2500, 3750), "tang": "Tang 2"},
    {"so": "202", "ten": "Phong ngu 2", "diem": (2500, 11250), "tang": "Tang 2"},
]

# Revit warns when an opening is closer than half its width plus 6" (152.4 mm)
# to a wall end or to a wall meeting its host (pyRevit modeling skill).
KHOANG_HO_CUA_MM = 152.4
SAI_SO_MM = 1.0


def _len(a, b):
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5


def _along(wall, point):
    """(distance from wall start along the axis, distance off the axis) in mm."""
    a, b = wall["tu"], wall["den"]
    length = _len(a, b)
    ux, uy = (b[0] - a[0]) / float(length), (b[1] - a[1]) / float(length)
    dx, dy = point[0] - a[0], point[1] - a[1]
    return dx * ux + dy * uy, abs(dx * uy - dy * ux)


def _diem_noi(wall, walls):
    """Positions (mm along the axis) of the wall ends and of other walls ending on it."""
    length = _len(wall["tu"], wall["den"])
    positions = [0.0, length]
    for other in walls:
        if other is wall or other["tang"] != wall["tang"]:
            continue
        for end in (other["tu"], other["den"]):
            s, off = _along(wall, end)
            if off <= SAI_SO_MM and SAI_SO_MM < s < length - SAI_SO_MM:
                positions.append(s)
    return positions


def kiem_tra(tang=None, tuong=None, cua=None, san=None, phong=None):
    """Check the plan data before building. Returns a list of problems (empty = OK)."""
    tang = TANG if tang is None else tang
    tuong = TUONG if tuong is None else tuong
    cua = CUA if cua is None else cua
    san = SAN if san is None else san
    phong = PHONG if phong is None else phong
    loi = []
    levels = [name for name, _ in tang]
    elevations = [elev for _, elev in tang]
    if elevations != sorted(elevations):
        loi.append("TANG: cao do chua sap xep tang dan")
    walls = {}
    for w in tuong:
        if w["ten"] in walls:
            loi.append("TUONG %s: trung ten" % w["ten"])
        walls[w["ten"]] = w
        if _len(w["tu"], w["den"]) <= SAI_SO_MM:
            loi.append("TUONG %s: dai bang 0" % w["ten"])
        for key in ("tang", "den_tang"):
            if w.get(key) and w[key] not in levels:
                loi.append("TUONG %s: khong co tang '%s'" % (w["ten"], w[key]))
        if w.get("den_tang") in levels and w["tang"] in levels and \
                levels.index(w["den_tang"]) <= levels.index(w["tang"]):
            loi.append("TUONG %s: tang tren khong cao hon tang duoi" % w["ten"])
    for c in cua:
        w = walls.get(c["tuong"])
        if w is None:
            loi.append("CUA %s: khong co tuong '%s'" % (c["ky_hieu"], c["tuong"]))
            continue
        s, off = _along(w, c["vi_tri"])
        if off > SAI_SO_MM:
            loi.append("CUA %s: vi tri lech truc tuong %s %.0f mm" % (c["ky_hieu"], w["ten"], off))
            continue
        need = c["rong"] / 2.0 + KHOANG_HO_CUA_MM
        for p in _diem_noi(w, tuong):
            if abs(s - p) < need:
                loi.append("CUA %s: cach diem noi tuong %.0f mm, can toi thieu %.0f mm" % (c["ky_hieu"], abs(s - p), need))
                break
    for f in san:
        if f["tang"] not in levels:
            loi.append("SAN %s: khong co tang '%s'" % (f["ten"], f["tang"]))
        if len(f["vien"]) < 3:
            loi.append("SAN %s: vien can it nhat 3 diem" % f["ten"])
    numbers = set()
    for r in phong:
        if r["tang"] not in levels:
            loi.append("PHONG %s: khong co tang '%s'" % (r["so"], r["tang"]))
        if r["so"] in numbers:
            loi.append("PHONG %s: trung so phong" % r["so"])
        numbers.add(r["so"])
    return loi
