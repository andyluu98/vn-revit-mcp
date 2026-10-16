# Count model element instances per category.
counts = {}
total = 0
for element in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():  # noqa: F821
    category = element.Category
    if category is None:
        continue
    try:
        if category.CategoryType != DB.CategoryType.Model:
            continue
    except Exception:
        continue
    try:
        if element.ViewSpecific:
            continue
    except Exception:
        pass
    name = category.Name or ""
    counts[name] = counts.get(name, 0) + 1
    total += 1

rows = [{"category": name, "count": count} for name, count in counts.items()]
rows.sort(key=lambda item: -item["count"])
result = {"total": total, "categories": rows}
