# Rooms: number, name, level, area (m2), perimeter (m), volume (m3), status.
rows = []
truncated = False
for room in collect("OST_Rooms"):
    if len(rows) >= MAX_ROWS:
        truncated = True
        break
    area = None
    perimeter = None
    volume = None
    try:
        area = room.Area
        perimeter = room.Perimeter
        volume = room.Volume
    except Exception:
        pass
    status = "ok"
    try:
        if room.Location is None:
            status = "unplaced"
        elif not area:
            status = "not_enclosed"
    except Exception:
        pass
    level = ""
    try:
        level = element_name(room.Level) if room.Level is not None else ""
    except Exception:
        level = level_name(room)
    rows.append({
        "id": eid_int(room.Id),
        "number": param_text(room, "ROOM_NUMBER"),
        "name": param_text(room, "ROOM_NAME"),
        "level": level,
        "area_m2": to_m2(area),
        "perimeter_m": to_m(perimeter),
        "volume_m3": to_m3(volume) if volume else None,
        "status": status,
    })

result = {"rows": rows, "truncated": truncated}
