# -*- coding: utf-8 -*-
# Shared helpers prepended to every vn-revit-mcp script before it is sent to
# `pyrevit agent run`. Runs inside Revit on IronPython 2.7, IronPython 3.4 or
# CPython 3.12, so keep the syntax to the common subset: no f-strings, no type
# annotations, no walrus operator, ASCII only.
#
# The pyRevit agent runner injects: doc, uidoc, uiapp, DB, inputs.
# Scripts assign their output to `result` (JSON-serializable).

try:
    DB  # noqa: F821  (injected by the pyRevit agent runner)
except NameError:
    from pyrevit.api import DB  # noqa: F401

FT_TO_M = 0.3048
FT2_TO_M2 = 0.09290304
FT3_TO_M3 = 0.028316846592

try:
    MAX_ROWS = int(inputs.get("max_rows", 5000))  # noqa: F821
except Exception:
    MAX_ROWS = 5000


def eid_int(eid):
    """ElementId -> int on every Revit version (Value on 2024+, IntegerValue before)."""
    if eid is None:
        return None
    value = getattr(eid, "Value", None)
    if value is None:
        value = getattr(eid, "IntegerValue", None)
    if value is None:
        return None
    return int(value)


def bip(name):
    """BuiltInParameter by name, or None when this Revit version does not have it."""
    return getattr(DB.BuiltInParameter, name, None)


def bic(name):
    """BuiltInCategory by name, or None when this Revit version does not have it."""
    return getattr(DB.BuiltInCategory, name, None)


def element_name(element):
    """Name of an element or element type; IronPython hides Name on some types."""
    if element is None:
        return ""
    try:
        return element.Name or ""
    except Exception:
        pass
    try:
        return DB.Element.Name.GetValue(element) or ""
    except Exception:
        pass
    for bip_name in ("SYMBOL_NAME_PARAM", "ALL_MODEL_TYPE_NAME"):
        text = param_text(element, bip_name)
        if text:
            return text
    return ""


def get_param(element, bip_name):
    built_in = bip(bip_name)
    if element is None or built_in is None:
        return None
    try:
        return element.get_Parameter(built_in)
    except Exception:
        return None


def param_double(element, bip_name):
    """Raw double (Revit internal units) of a built-in parameter, or None."""
    parameter = get_param(element, bip_name)
    try:
        if parameter is not None and parameter.HasValue and parameter.StorageType == DB.StorageType.Double:
            return parameter.AsDouble()
    except Exception:
        pass
    return None


def param_text(element, bip_name):
    parameter = get_param(element, bip_name)
    return parameter_text(parameter)


def parameter_text(parameter):
    """Value of any parameter as text, or "" when empty."""
    if parameter is None:
        return ""
    try:
        if not parameter.HasValue:
            return ""
        storage = parameter.StorageType
        if storage == DB.StorageType.String:
            return parameter.AsString() or ""
        text = parameter.AsValueString()
        if text:
            return text
        if storage == DB.StorageType.Integer:
            return str(parameter.AsInteger())
        if storage == DB.StorageType.Double:
            return str(parameter.AsDouble())
        if storage == DB.StorageType.ElementId:
            return str(eid_int(parameter.AsElementId()))
    except Exception:
        pass
    return ""


def element_type(element):
    try:
        type_id = element.GetTypeId()
        if type_id is None or type_id == DB.ElementId.InvalidElementId:
            return None
        return doc.GetElement(type_id)  # noqa: F821
    except Exception:
        return None


def family_name(element_type_obj):
    if element_type_obj is None:
        return ""
    try:
        return element_type_obj.FamilyName or ""
    except Exception:
        return param_text(element_type_obj, "ALL_MODEL_FAMILY_NAME")


def level_name(element):
    """Level of an element from LevelId or the usual level parameters."""
    level_id = None
    try:
        level_id = element.LevelId
    except Exception:
        level_id = None
    if level_id is None or level_id == DB.ElementId.InvalidElementId:
        level_id = None
        for bip_name in ("FAMILY_LEVEL_PARAM", "WALL_BASE_CONSTRAINT", "LEVEL_PARAM",
                         "SCHEDULE_LEVEL_PARAM", "INSTANCE_REFERENCE_LEVEL_PARAM",
                         "FAMILY_BASE_LEVEL_PARAM"):
            parameter = get_param(element, bip_name)
            try:
                if parameter is not None and parameter.StorageType == DB.StorageType.ElementId:
                    candidate = parameter.AsElementId()
                    if candidate is not None and candidate != DB.ElementId.InvalidElementId:
                        level_id = candidate
                        break
            except Exception:
                continue
    if level_id is None:
        return ""
    return element_name(doc.GetElement(level_id))  # noqa: F821


def collect(bic_name):
    """Model instances of one built-in category."""
    category = bic(bic_name)
    if category is None:
        return []
    collector = DB.FilteredElementCollector(doc).OfCategory(category)  # noqa: F821
    return list(collector.WhereElementIsNotElementType())


def material_volumes(element):
    """[(material name, volume ft3)] from the element's materials; [] when unavailable."""
    rows = []
    try:
        for material_id in element.GetMaterialIds(False):
            volume = element.GetMaterialVolume(material_id)
            if volume:
                rows.append((element_name(doc.GetElement(material_id)), volume))  # noqa: F821
    except Exception:
        rows = []
    return rows


def to_m(value):
    return None if value is None else value * FT_TO_M


def to_mm(value):
    return None if value is None else value * FT_TO_M * 1000.0


def to_m2(value):
    return None if value is None else value * FT2_TO_M2


def to_m3(value):
    return None if value is None else value * FT3_TO_M3


# ---------------------------------------------------------------- script body
