# Set one parameter on a list of elements, inside one transaction.
# inputs: ids (list of int), parameter (name), value (text).
# Text and integer parameters are set directly; length/area/... parameters use
# SetValueString, so the value is read in the project's display units.
ids = inputs["ids"]  # noqa: F821
parameter_name = inputs["parameter"]  # noqa: F821
value = inputs["value"]  # noqa: F821



def element_id(raw):
    # Revit 2024+ ElementId is Int64; the Int32 constructor is gone in 2026.
    try:
        import System
        return DB.ElementId(System.Int64(raw))
    except Exception:
        return DB.ElementId(int(raw))


changed = []
skipped = []
transaction = DB.Transaction(doc, "vn-revit-mcp: dat tham so " + parameter_name)  # noqa: F821
transaction.Start()
try:
    for raw_id in ids:
        element = doc.GetElement(element_id(raw_id))  # noqa: F821
        if element is None:
            skipped.append({"id": raw_id, "reason": "not_found"})
            continue
        parameter = element.LookupParameter(parameter_name)
        if parameter is None:
            skipped.append({"id": raw_id, "reason": "no_parameter"})
            continue
        if parameter.IsReadOnly:
            skipped.append({"id": raw_id, "reason": "read_only"})
            continue
        before = parameter_text(parameter)
        storage = parameter.StorageType
        ok = False
        if storage == DB.StorageType.String:
            ok = parameter.Set(value)
        elif storage == DB.StorageType.Integer:
            try:
                ok = parameter.Set(int(value))
            except ValueError:
                skipped.append({"id": raw_id, "reason": "not_integer"})
                continue
        elif storage == DB.StorageType.Double:
            ok = parameter.SetValueString(value)
        else:
            skipped.append({"id": raw_id, "reason": "unsupported_storage"})
            continue
        if ok:
            changed.append({"id": raw_id, "before": before, "after": parameter_text(parameter)})
        else:
            skipped.append({"id": raw_id, "reason": "set_failed"})
    transaction.Commit()
except Exception:
    if transaction.HasStarted() and not transaction.HasEnded():
        transaction.RollBack()
    raise

result = {"parameter": parameter_name, "changed": changed, "skipped": skipped}
