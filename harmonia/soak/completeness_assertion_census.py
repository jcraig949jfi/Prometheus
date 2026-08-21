"""Do other harness tests substitute soundness for completeness? (soak P44, rotation (c))

P43 found test_abs_extra_clean_ground_truth asserts the recorded root IS a solution
and never that it is THE solution set, leaving a green suite over 22 degenerate
probes per run. It logged WITHHELD whether that is a house habit -- the base-rate
question this soak has been caught on before.

Census every ground-truth-asserting test in harmonia/experiments and classify:
  COMPLETENESS  -- solves/enumerates and constrains the SOLUTION SET
  SOUNDNESS-ONLY -- checks the recorded answer satisfies the relation

Static classification is only half; a soundness-only test is a DEFECT only if an
incompleteness witness exists. Classification without a witness is reported as
unconfirmed.
"""
import ast
import re
from pathlib import Path

EXP = Path("harmonia/experiments")
# markers of an actual completeness check
COMPLETE = re.compile(
    r"sp\.solve|sympy\.solve|solveset|nroots|all_roots|real_roots|"
    r"unique|len\(\s*in_domain\s*\)|no other|exhaust|for\s+\w+\s+in\s+range\(.*\):\s*$", re.I)
# markers of a soundness check on the recorded answer
SOUND = re.compile(r"ground_truth|gt\[0\]|p\.ground_truth", re.I)

print(f"{'file':34s} {'test':44s} {'ground-truth?':>13s} {'completeness?':>14s}")
print("-" * 112)
rows = []
for f in sorted(EXP.glob("test_*.py")):
    try:
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception:
        continue
    lines = src.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        seg = "\n".join(lines[node.lineno - 1: (node.end_lineno or node.lineno)])
        if not SOUND.search(seg):
            continue
        has_complete = bool(COMPLETE.search(seg))
        rows.append((f.name, node.name, has_complete))
        print(f"{f.name:34s} {node.name[:44]:44s} {'yes':>13s} "
              f"{('YES' if has_complete else '*** no ***'):>14s}")
print("-" * 112)
n = len(rows)
comp = sum(r[2] for r in rows)
print(f"ground-truth-asserting tests found : {n}")
print(f"  with a completeness check        : {comp}")
print(f"  SOUNDNESS-ONLY                   : {n - comp}")
for fn, t, c in rows:
    if not c:
        print(f"     {fn}::{t}")
print()
print("NOTE: this is a STATIC classification by marker. A soundness-only test is a")
print("defect only where an incompleteness witness exists (P43 produced one for")
print("abs_extra_clean: x=2 at a=b=3). Others below are unconfirmed until witnessed.")
