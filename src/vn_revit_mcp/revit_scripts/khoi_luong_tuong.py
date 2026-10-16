# Walls: type, level, kind, thickness (mm), length (m), area (m2), volume (m3).
# Stacked wall parents are skipped because their members are walls of their own.
rows = []
skipped_stacked = 0
in_place = 0
truncated = False
for element in collect("OST_Walls"):
    if len(rows) >= MAX_ROWS:
        truncated = True
        break
    if not isinstance(element, DB.Wall):
        # In-place walls are family instances: no HOST_VOLUME_COMPUTED, use material volumes.
        in_place += 1
        volume = param_double(element, "HOST_VOLUME_COMPUTED")
        if not volume:
            material_rows = material_volumes(element)
            volume = sum(v for _, v in material_rows) if material_rows else None
        rows.append({
            "id": eid_int(element.Id),
            "type": element_name(element_type(element)) or element_name(element),
            "level": level_name(element),
            "kind": "in_place",
            "thickness_mm": None,
            "length_m": None,
            "area_m2": to_m2(param_double(element, "HOST_AREA_COMPUTED")),
            "volume_m3": to_m3(volume),
        })
        continue
    try:
        if element.IsStackedWall:
            skipped_stacked += 1
            continue
    except Exception:
        pass
    # Compare enum values: str() of a .NET enum may be a number under pythonnet.
    kind = "basic"
    try:
        wall_kind = element.WallType.Kind
        if wall_kind == DB.WallKind.Curtain:
            kind = "curtain"
        elif wall_kind == DB.WallKind.Stacked:
            kind = "stacked"
    except Exception:
        pass
    thickness = None
    try:
        thickness = element.Width
    except Exception:
        thickness = None
    rows.append({
        "id": eid_int(element.Id),
        "type": element_name(element.WallType),
        "level": level_name(element),
        "kind": kind,
        "thickness_mm": to_mm(thickness),
        "length_m": to_m(param_double(element, "CURVE_ELEM_LENGTH")),
        "area_m2": to_m2(param_double(element, "HOST_AREA_COMPUTED")),
        "volume_m3": to_m3(param_double(element, "HOST_VOLUME_COMPUTED")),
    })

result = {"rows": rows, "truncated": truncated, "skipped_stacked_parents": skipped_stacked, "in_place": in_place}
