"""Fake `pyrevit` CLI for the test suite (no Revit needed).

Mimics the JSON that `pyrevit agent status --json` and `pyrevit agent run` print in
pyRevit 7 (see dev/pyRevitLabs/pyRevitCLI/PyRevitCLIAgentCmds.cs and
dev/pyRevitLabs.PyRevit.Runtime/Agent/AgentRunService.cs).

FAKE_PYREVIT_SCENARIO: ok (default) | busy | busytext | nojson | truncated | discard | readonly | noinstance
FAKE_PYREVIT_LOG: when set, each call's argv and inputs are appended there as JSON lines.
"""

import json
import os
import sys
import tempfile

SCENARIO = os.environ.get("FAKE_PYREVIT_SCENARIO", "ok")

RESULTS = {
    "thong_tin_du_an": {
        "title": "Nha pho mau", "path": "C:\\DuAn\\nha-pho.rvt", "revit_version": "2025",
        "is_family_document": False, "is_workshared": False,
        "project_name": "Nha pho mau", "project_number": "", "client_name": "",
        "levels": [{"id": 1, "name": "Tang 1", "elevation_m": 0.0}, {"id": 2, "name": "Tang 2", "elevation_m": 3.6}],
        "active_view": {"id": 10, "name": "Tang 1", "type": "FloorPlan"}, "phases": ["New Construction"],
    },
    "dem_theo_hang_muc": {"total": 3, "categories": [{"category": "Walls", "count": 2}, {"category": "Doors", "count": 1}]},
    "thong_ke_cua": {"rows": [
        {"kind": "door", "id": 101, "family": "Cua di 1 canh", "type": "900x2200", "level": "Tang 1",
         "width_mm": 900.0000001, "height_mm": 2200.0, "sill_mm": 0.0, "mark": "D1"},
        {"kind": "door", "id": 102, "family": "Cua di 1 canh", "type": "900x2200", "level": "Tang 2",
         "width_mm": 900.0000001, "height_mm": 2200.0, "sill_mm": 0.0, "mark": ""},
        {"kind": "window", "id": 201, "family": "Cua so", "type": "1200x1400", "level": "Tang 1",
         "width_mm": 1200.0, "height_mm": 1400.0, "sill_mm": 900.0, "mark": "S1"},
    ], "truncated": False},
    "thong_ke_phong": {"rows": [
        {"id": 301, "number": "101", "name": "Phong khach", "level": "Tang 1", "area_m2": 20.123456,
         "perimeter_m": 18.0, "volume_m3": None, "status": "ok"},
        {"id": 302, "number": "102", "name": "Bep", "level": "Tang 1", "area_m2": 10.5, "perimeter_m": 13.0,
         "volume_m3": None, "status": "ok"},
        {"id": 303, "number": "", "name": "Phong chua dat", "level": "", "area_m2": 0.0, "perimeter_m": 0.0,
         "volume_m3": None, "status": "unplaced"},
    ], "truncated": False},
    "khoi_luong_tuong": {"rows": [
        {"id": 1, "type": "Tuong 200", "level": "Tang 1", "kind": "basic", "thickness_mm": 200.0,
         "length_m": 5.004, "area_m2": 18.0144, "volume_m3": 3.60288},
        {"id": 2, "type": "Tuong 200", "level": "Tang 1", "kind": "basic", "thickness_mm": 200.0,
         "length_m": 4.003, "area_m2": 14.4108, "volume_m3": 2.88216},
        {"id": 3, "type": "Vach kinh", "level": "Tang 1", "kind": "curtain", "thickness_mm": 0.0,
         "length_m": 3.0, "area_m2": 9.0, "volume_m3": None},
    ], "truncated": False, "skipped_stacked_parents": 0, "in_place": 0},
    "khoi_luong_san": {"rows": [
        {"id": 11, "type": "San BTCT 120", "level": "Tang 2", "structural": True, "thickness_mm": 120.0,
         "area_m2": 70.0, "volume_m3": 8.4},
    ], "truncated": False},
    "khoi_luong_ket_cau": {"rows": [
        {"kind": "column", "id": 21, "family": "Cot BTCT", "type": "220x220", "level": "Tang 1",
         "length_m": None, "material": "Be tong B20", "volume_m3": 0.174},
        {"kind": "column", "id": 22, "family": "Cot BTCT", "type": "220x220", "level": "Tang 1",
         "length_m": None, "material": "Be tong B20", "volume_m3": 0.174},
    ], "truncated": False},
    "kiem_tra_tham_so": None,  # built from inputs below
    "dat_tham_so": None,
}


def log(entry):
    path = os.environ.get("FAKE_PYREVIT_LOG")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def option(args, name, default=None):
    for arg in args:
        if arg.startswith(name + "="):
            return arg[len(name) + 1:]
    return default


def main(argv):
    if SCENARIO == "nojson":
        print("Error: something went wrong in pyrevit")
        return 1
    if argv[:3] == ["agent", "status", "--json"]:
        if SCENARIO == "noinstance":
            print("[]")
        else:
            print(json.dumps([{"pid": 4242, "revit_version": "2025", "pipe": "pyrevit-agent-4242"}], indent=2))
        return 0
    if argv[:2] != ["agent", "run"]:
        print("Usage: pyrevit ...")
        return 1
    if SCENARIO == "noinstance":
        print("No running Revit with the agent host.")
        return 1

    script_path = argv[2]
    with open(script_path, encoding="utf-8") as handle:
        source = handle.read()
    mode = option(argv, "--mode", "query")
    inputs = json.loads(option(argv, "--inputs", "{}"))
    name = os.path.splitext(os.path.basename(script_path))[0]
    log({"argv": argv, "name": name, "mode": mode, "inputs": inputs, "has_prelude": "def eid_int" in source})

    response = {"run_id": "fake", "run_dir": tempfile.gettempdir(), "mode": mode, "title": option(argv, "--title"),
                "status": "ok", "decision": "rolled_back", "output": "", "output_truncated": False,
                "result": None, "result_truncated": False, "warnings": [], "error": None}

    if SCENARIO == "busytext":
        # Host-side errors reach the CLI as JSON-RPC errors and are printed as plain text.
        print("Error: Revit is busy: another transaction is open.")
        return 1

    if SCENARIO == "busy":
        response.update(status="error", error={"type": "revit_busy", "message": "Revit is busy", "traceback": None})
        print(json.dumps(response))
        return 1

    if name == "kiem_tra_tham_so":
        result = {"category": inputs["category"], "parameter": inputs["parameter"], "total": 3, "filled": 1,
                  "missing_count": 1, "empty_count": 1, "missing": [{"id": 1, "name": "a"}],
                  "empty": [{"id": 2, "name": "b", "source": "instance"}], "list_limit": 500}
    elif name == "dat_tham_so":
        result = {"parameter": inputs["parameter"],
                  "changed": [{"id": i, "before": "", "after": inputs["value"]} for i in inputs["ids"]], "skipped": []}
        if mode == "modify":
            if SCENARIO == "discard":
                response.update(status="rejected", decision="discarded", approval="user")
            elif SCENARIO == "readonly":
                response.update(status="rejected", decision="rolled_back")
            else:
                response.update(decision="committed", approval="user")
    else:
        result = RESULTS[name]

    if SCENARIO == "truncated":
        path = os.path.join(tempfile.mkdtemp(prefix="fake-run-"), "result.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(result, handle)
        response.update(result=None, result_truncated=True, result_path=path)
    else:
        response["result"] = result
    print(json.dumps(response, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
