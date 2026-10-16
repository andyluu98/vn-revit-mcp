"""Static checks on the scripts that run inside Revit.

pyRevit's default engine is IronPython 2.7, so every script must stay in the syntax
subset shared by Python 2.7 and 3.x, and be plain ASCII.
"""

import ast

import pytest

from vn_revit_mcp import pyrevit_cli

FORBIDDEN = {
    ast.JoinedStr: "f-string",
    ast.AnnAssign: "annotated assignment",
    ast.NamedExpr: "walrus operator",
    ast.AsyncFunctionDef: "async def",
    ast.Await: "await",
    ast.Nonlocal: "nonlocal",
    ast.YieldFrom: "yield from",
    ast.MatMult: "@ operator",
    ast.Match: "match statement",
}

SCRIPTS = sorted(pyrevit_cli.SCRIPTS)


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_is_python27_compatible(name):
    source = pyrevit_cli.script_source(name)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        for kind, label in FORBIDDEN.items():
            assert not isinstance(node, kind), f"{name}: {label} at line {getattr(node, 'lineno', '?')}"
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            args = node.args
            assert not args.kwonlyargs, f"{name}: keyword-only args"
            assert not args.posonlyargs, f"{name}: positional-only args"
            if isinstance(node, ast.FunctionDef):
                assert node.returns is None, f"{name}: return annotation"
                for arg in args.args:
                    assert arg.annotation is None, f"{name}: argument annotation"


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_is_ascii(name):
    pyrevit_cli.script_source(name).encode("ascii")


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_sets_result(name):
    tree = ast.parse(pyrevit_cli.script_source(name))
    targets = [t.id for node in tree.body if isinstance(node, ast.Assign) for t in node.targets if isinstance(t, ast.Name)]
    assert "result" in targets


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_compiles(name):
    compile(pyrevit_cli.script_source(name), name, "exec")


def test_only_set_parameter_script_opens_a_transaction():
    for name in SCRIPTS:
        source = pyrevit_cli.script_source(name)
        if name == "dat_tham_so":
            assert "DB.Transaction(" in source
        else:
            assert "Transaction(" not in source, f"{name} must stay read-only"


def test_unknown_script_is_refused():
    with pytest.raises(pyrevit_cli.PyRevitError):
        pyrevit_cli.script_source("../../evil")
