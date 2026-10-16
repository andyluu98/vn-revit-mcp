# Doors and windows: family, type, level, size (mm), sill height (mm), mark.
SIZE_PARAMS = {
    "door": ("DOOR_WIDTH", "DOOR_HEIGHT"),
    "window": ("WINDOW_WIDTH", "WINDOW_HEIGHT"),
}


def size_of(element, type_obj, bip_name):
    value = param_double(element, bip_name)
    if value is None:
        value = param_double(type_obj, bip_name)
    if value is None:
        value = param_double(type_obj, "FAMILY_WIDTH_PARAM" if "WIDTH" in bip_name else "FAMILY_HEIGHT_PARAM")
    return to_mm(value)


rows = []
truncated = False
for kind, bic_name in (("door", "OST_Doors"), ("window", "OST_Windows")):
    for element in collect(bic_name):
        if len(rows) >= MAX_ROWS:
            truncated = True
            break
        type_obj = element_type(element)
        width_bip, height_bip = SIZE_PARAMS[kind]
        rows.append({
            "kind": kind,
            "id": eid_int(element.Id),
            "family": family_name(type_obj),
            "type": element_name(type_obj),
            "level": level_name(element),
            "width_mm": size_of(element, type_obj, width_bip),
            "height_mm": size_of(element, type_obj, height_bip),
            "sill_mm": to_mm(param_double(element, "INSTANCE_SILL_HEIGHT_PARAM")),
            "mark": param_text(element, "ALL_MODEL_MARK"),
        })

result = {"rows": rows, "truncated": truncated}
