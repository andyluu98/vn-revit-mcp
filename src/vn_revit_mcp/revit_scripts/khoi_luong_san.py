# Floors: type, level, structural flag, thickness (mm), area (m2), volume (m3).
rows = []
truncated = False
for element in collect("OST_Floors"):
    if len(rows) >= MAX_ROWS:
        truncated = True
        break
    type_obj = element_type(element)
    structural = False
    parameter = get_param(element, "FLOOR_PARAM_IS_STRUCTURAL")
    try:
        structural = parameter is not None and parameter.AsInteger() == 1
    except Exception:
        structural = False
    thickness = param_double(element, "FLOOR_ATTR_THICKNESS_PARAM")
    if thickness is None:
        thickness = param_double(type_obj, "FLOOR_ATTR_DEFAULT_THICKNESS_PARAM")
    rows.append({
        "id": eid_int(element.Id),
        "type": element_name(type_obj) or element_name(element),
        "level": level_name(element),
        "structural": structural,
        "thickness_mm": to_mm(thickness),
        "area_m2": to_m2(param_double(element, "HOST_AREA_COMPUTED")),
        "volume_m3": to_m3(param_double(element, "HOST_VOLUME_COMPUTED")),
    })

result = {"rows": rows, "truncated": truncated}
