# Project overview: title, Revit version, levels, active view, phases.
# elevation_m: from the project base point (ProjectElevation);
# level_elevation_m: the Level's own Elevation, relative to its Elevation Base setting.
levels = []
for level in DB.FilteredElementCollector(doc).OfClass(DB.Level):  # noqa: F821
    try:
        elevation = level.ProjectElevation
    except Exception:
        elevation = level.Elevation
    levels.append({"id": eid_int(level.Id), "name": element_name(level), "elevation_m": to_m(elevation),
                   "level_elevation_m": to_m(level.Elevation)})
levels.sort(key=lambda item: item["elevation_m"] if item["elevation_m"] is not None else 0.0)

active_view = None
try:
    view = uidoc.ActiveView if uidoc else None  # noqa: F821
    if view is not None:
        active_view = {"id": eid_int(view.Id), "name": element_name(view), "type": str(view.ViewType)}
except Exception:
    active_view = None

version = ""
try:
    version = doc.Application.VersionNumber  # noqa: F821
except Exception:
    version = ""

phases = []
try:
    for phase in doc.Phases:  # noqa: F821
        phases.append(element_name(phase))
except Exception:
    phases = []

info = doc.ProjectInformation  # noqa: F821
result = {
    "title": doc.Title,  # noqa: F821
    "path": doc.PathName,  # noqa: F821
    "revit_version": version,
    "is_family_document": bool(doc.IsFamilyDocument),  # noqa: F821
    "is_workshared": bool(doc.IsWorkshared),  # noqa: F821
    "project_name": param_text(info, "PROJECT_NAME") if info is not None else "",
    "project_number": param_text(info, "PROJECT_NUMBER") if info is not None else "",
    "client_name": param_text(info, "CLIENT_NAME") if info is not None else "",
    "levels": levels,
    "active_view": active_view,
    "phases": phases,
}
