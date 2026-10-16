# Structural columns, framing and foundations: volume per material (m3).
CATEGORIES = (
    ("column", "OST_StructuralColumns"),
    ("framing", "OST_StructuralFraming"),
    ("foundation", "OST_StructuralFoundation"),
)

rows = []
truncated = False
for kind, bic_name in CATEGORIES:
    for element in collect(bic_name):
        if len(rows) >= MAX_ROWS:
            truncated = True
            break
        type_obj = element_type(element)
        base = {
            "kind": kind,
            "id": eid_int(element.Id),
            "family": family_name(type_obj),
            "type": element_name(type_obj) or element_name(element),
            "level": level_name(element),
            "length_m": to_m(param_double(element, "STRUCTURAL_FRAME_CUT_LENGTH")),
        }
        material_rows = material_volumes(element)
        if not material_rows:
            volume = param_double(element, "HOST_VOLUME_COMPUTED")
            material_rows = [("", volume)]
        for material_name, volume in material_rows:
            row = dict(base)
            row["material"] = material_name
            row["volume_m3"] = to_m3(volume)
            rows.append(row)

result = {"rows": rows, "truncated": truncated}
