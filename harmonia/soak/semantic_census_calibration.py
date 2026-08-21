"""Test SOAK-108's own doctrine: does a SEMANTIC census beat a marker one? (soak P45)

SOAK-108 claimed that where a question needs meaning rather than pattern, a marker
regex "will produce a confident wrong number every time". That is a doctrine claim
this channel made about its own method, and it is testable.

RULE, STATED BEFORE RUNNING (not tuned to the known answer):
  IN SCOPE  -- a test asserting a generator's ground truth is CORRECT, detected as:
               `.ground_truth` appearing as the SUBJECT of an assertion, i.e. inside
               a Compare, or under len(), or subscripted -- and NOT merely passed as
               an argument to a call (verify(...), _ans_correct(...)).
  COMPLETE  -- the test body calls a solver (sp.solve / solveset / real_roots /
               nroots / all_roots) or enumerates candidates and compares cardinality.

CALIBRATION SET (hand-verified in P44): test_legality_generators.py and
test_verifier_lens.py. Known answer: 2 in scope; 1 with a completeness check; and
four specific tests that must be EXCLUDED.

HELD-OUT SET: every other test file. Results there are hand-verified afterwards --
without that, agreement on the calibration set only shows I fitted to the answer.
"""
import ast
from pathlib import Path

SOLVERS = {"solve", "solveset", "real_roots", "nroots", "all_roots"}
CAL = {"harmonia/experiments/test_legality_generators.py",
       "harmonia/experiments/test_verifier_lens.py"}
KNOWN_IN_SCOPE = {"test_abs_extra_clean_ground_truth", "test_log_extra_3arg_ground_truth"}
KNOWN_COMPLETE = {"test_log_extra_3arg_ground_truth"}


def gt_nodes(fn):
    """Every `<expr>.ground_truth` attribute access inside this function."""
    return [n for n in ast.walk(fn)
            if isinstance(n, ast.Attribute) and n.attr == "ground_truth"]


def is_subject(fn, node):
    """True if this .ground_truth access is the SUBJECT of an assertion rather than
    an argument handed to a call. Subject == appears in a Compare, or under len(),
    or is subscripted."""
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            if child is not node:
                continue
            if isinstance(parent, ast.Compare):
                return True
            if isinstance(parent, ast.Subscript):
                return True
            if isinstance(parent, ast.Call):
                f = parent.func
                name = f.id if isinstance(f, ast.Name) else getattr(f, "attr", "")
                return name == "len"          # len(gt) is a subject; verify(gt) is not
    return False


def classify(path):
    src = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("test_"):
            continue
        nodes = gt_nodes(fn)
        if not nodes or not any(is_subject(fn, n) for n in nodes):
            continue
        complete = any(
            isinstance(c, ast.Call) and (
                (isinstance(c.func, ast.Attribute) and c.func.attr in SOLVERS) or
                (isinstance(c.func, ast.Name) and c.func.id in SOLVERS))
            for c in ast.walk(fn))
        out.append((fn.name, complete))
    return out


print("CALIBRATION SET (answer known from P44 hand-verification)")
cal_scope, cal_complete = set(), set()
for f in sorted(CAL):
    for name, comp in classify(f):
        cal_scope.add(name)
        if comp:
            cal_complete.add(name)
        print(f"  {Path(f).name:34s} {name:44s} complete={comp}")
print(f"\n  in scope   : got {sorted(cal_scope)}")
print(f"               want {sorted(KNOWN_IN_SCOPE)}")
print(f"  completeness: got {sorted(cal_complete)}  want {sorted(KNOWN_COMPLETE)}")
ok = (cal_scope == KNOWN_IN_SCOPE) and (cal_complete == KNOWN_COMPLETE)
print(f"  CALIBRATION {'PASSES' if ok else 'FAILS'}")

print("\nHELD-OUT SET (never hand-verified for this question)")
held = [p for p in
        list(Path("harmonia/experiments").glob("test_*.py")) +
        list(Path("harmonia/primitives").glob("test_*.py"))
        if str(p).replace("\\", "/") not in CAL]
found = []
for f in held:
    try:
        rows = classify(f)
    except Exception as e:
        print(f"  {f.name:34s} parse error: {type(e).__name__}"); continue
    for name, comp in rows:
        found.append((f.name, name, comp))
        print(f"  {f.name:34s} {name:44s} complete={comp}")
if not found:
    print("  (no in-scope tests found in the held-out set)")
print(f"\nheld-out files scanned: {len(held)}   in-scope tests found: {len(found)}")
print("\nNEXT: hand-verify every held-out hit. Calibration agreement alone would only")
print("show the classifier was fitted to an answer I already knew (pre-stated reading 3).")
