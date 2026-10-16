# Unit helpers for agent scripts: plan data is written in mm, Revit works in feet.
# Must stay valid on IronPython 2.7, IronPython 3.4 and CPython 3 (ASCII only).

MM_PER_FT = 304.8


def ft(value_mm):
    """mm -> feet (Revit internal length)."""
    return float(value_mm) / MM_PER_FT


def mm(value_ft):
    """feet -> mm, for reading lengths back from Revit."""
    return float(value_ft) * MM_PER_FT


def diem(x_mm, y_mm):
    """Plan point in mm -> (x, y) in feet, as pyrevitlib create functions expect."""
    return (ft(x_mm), ft(y_mm))


def cac_diem(points_mm):
    return [diem(x, y) for x, y in points_mm]


def chu_nhat(x1_mm, y1_mm, x2_mm, y2_mm):
    """Corners of an axis-aligned rectangle, counter-clockwise, in feet."""
    return cac_diem([(x1_mm, y1_mm), (x2_mm, y1_mm), (x2_mm, y2_mm), (x1_mm, y2_mm)])


def m2(value_ft2):
    return float(value_ft2) * 0.09290304


def m3(value_ft3):
    return float(value_ft3) * 0.028316846592
