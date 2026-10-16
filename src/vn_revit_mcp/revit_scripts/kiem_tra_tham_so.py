# Which elements of one category lack a value for one parameter.
# inputs: category (BuiltInCategory name, validated by the server), parameter (name).
category_name = inputs["category"]  # noqa: F821
parameter_name = inputs["parameter"]  # noqa: F821
LIST_LIMIT = 500

missing = []
empty = []
missing_count = 0
empty_count = 0
filled = 0
total = 0
for element in collect(category_name):
    total += 1
    source = "instance"
    parameter = element.LookupParameter(parameter_name)
    if parameter is None:
        type_obj = element_type(element)
        parameter = type_obj.LookupParameter(parameter_name) if type_obj is not None else None
        source = "type"
    if parameter is None:
        missing_count += 1
        if len(missing) < LIST_LIMIT:
            missing.append({"id": eid_int(element.Id), "name": element_name(element)})
        continue
    if parameter_text(parameter).strip() == "":
        empty_count += 1
        if len(empty) < LIST_LIMIT:
            empty.append({"id": eid_int(element.Id), "name": element_name(element), "source": source})
        continue
    filled += 1

result = {
    "category": category_name,
    "category_found": bic(category_name) is not None,
    "parameter": parameter_name,
    "total": total,
    "filled": filled,
    "missing_count": missing_count,
    "empty_count": empty_count,
    "missing": missing,
    "empty": empty,
    "list_limit": LIST_LIMIT,
}
