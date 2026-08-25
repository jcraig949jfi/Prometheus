"""Read-only. Decompose the forge's 89.7% zero-delta ablation result.

A delta of exactly 0.000 has two very different causes and they must not be pooled:

  (a) DEAD IMPORT   - the primitive is imported but never called anywhere in the tool.
                      Stubbing it cannot change anything. This is an R2 finding.
  (b) DECORATION    - the primitive IS called, on a reachable-looking path, and stubbing
                      it to `return None` still changes no answer. This is the R4 finding
                      and it is the one that means "primitives were decoration".

It also bounds the known confound in `forge/tester.py:_stub_function`, which neutralises a
primitive by commenting out its import line and inserting `def NAME(*a,**k): return None`.
That binds only for BARE-NAME calls. A module-qualified call (`mod.NAME(...)`) is untouched,
so its delta would be a false zero. We count those separately.

Direction of the confound, stated before the number is read (feedback_truncation_can_flatter_a_gate):
a failed stub can only produce a FALSE ZERO, never a false nonzero. So any stubbing failure
INFLATES the decoration estimate. Subtracting these cases makes the decoration finding
strictly more conservative.

Population: the 198 `forge/verdicts/*_verdict.json` files carrying an ablation block,
joined to their source in `forge/candidates/`.

Repo-relative by design (feedback_paths). Run from the Prometheus root.
"""
import ast
import json
import glob
import os
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
VERDICTS = os.path.join(ROOT, "forge", "verdicts", "*_verdict.json")
CANDIDATES = os.path.join(ROOT, "forge", "candidates")
PRIM_MODULES = ("forge_primitives", "amino_acids")


def call_profile(src):
    """-> (bare_called, attr_called, imported_prim_names)

    bare_called : names invoked as NAME(...)          -> the stub WILL bind
    attr_called : attribute tails invoked as x.NAME(...) -> the stub will NOT bind
    """
    tree = ast.parse(src)
    bare, attr, imported = set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and any(m in node.module for m in PRIM_MODULES):
                for a in node.names:
                    imported.add(a.asname or a.name)
        elif isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                bare.add(f.id)
            elif isinstance(f, ast.Attribute):
                attr.add(f.attr)
    return bare, attr, imported


tally = collections.Counter()
dead_import_examples, decoration_examples, unstubbable = [], [], []
missing_src = 0

for path in sorted(glob.glob(VERDICTS)):
    d = json.load(open(path, encoding="utf-8"))
    abl = d.get("ablation")
    if not abl:
        continue
    tid = d.get("tool_id")
    src_path = os.path.join(CANDIDATES, "%s.py" % tid)
    if not os.path.exists(src_path):
        missing_src += 1
        continue
    try:
        src = open(src_path, encoding="utf-8").read()
        bare, attr, _imported = call_profile(src)
    except SyntaxError:
        tally["tool_unparseable"] += 1
        continue

    for prim, rec in abl.items():
        delta = rec.get("delta")
        if delta is None:
            tally["ablation_error"] += 1
            continue
        zero = abs(float(delta)) <= 1e-12
        called_bare = prim in bare
        called_attr = prim in attr

        if not zero:
            tally["nonzero_delta"] += 1
            continue
        # zero delta -- classify
        if not called_bare and not called_attr:
            tally["zero__dead_import"] += 1
            if len(dead_import_examples) < 6:
                dead_import_examples.append((tid, prim))
        elif not called_bare and called_attr:
            tally["zero__unstubbable_attr_call"] += 1
            if len(unstubbable) < 6:
                unstubbable.append((tid, prim))
        else:
            tally["zero__DECORATION"] += 1
            if len(decoration_examples) < 6:
                decoration_examples.append((tid, prim))

total = sum(v for k, v in tally.items()
            if k in ("nonzero_delta", "zero__dead_import",
                     "zero__unstubbable_attr_call", "zero__DECORATION"))

print("POPULATION: forge/verdicts ablation blocks joined to forge/candidates sources")
print("  classified ablations: %d   (sources missing for %d verdicts, %d unparseable tools,"
      " %d ablation errors)" % (total, missing_src, tally["tool_unparseable"],
                                tally["ablation_error"]))
print()
print("--- decomposition of every primitive ablation ---")
for k, label in (
    ("nonzero_delta", "delta != 0        primitive changed at least one answer"),
    ("zero__dead_import", "delta == 0 (a)    DEAD IMPORT - imported, never called"),
    ("zero__unstubbable_attr_call", "delta == 0 (b)    UNSTUBBABLE - called as x.NAME(), stub cannot bind"),
    ("zero__DECORATION", "delta == 0 (c)    DECORATION - called bare, stubbed, still no effect"),
):
    n = tally[k]
    print("  %-70s %5d  (%5.2f%%)" % (label, n, 100.0 * n / max(1, total)))
print()

dec = tally["zero__DECORATION"]
nz = tally["nonzero_delta"]
live = dec + nz
print("--- the conservative R4 reading ---")
print("  Restricted to primitives that are actually CALLED and actually STUBBABLE,")
print("  i.e. rows where the ablation was a valid experiment: n = %d" % live)
if live:
    print("  of those, removal changed nothing : %d / %d  (%.2f%%)"
          % (dec, live, 100.0 * dec / live))
    print("  of those, removal changed something: %d / %d  (%.2f%%)"
          % (nz, live, 100.0 * nz / live))
print()
print("  examples, dead import      :", dead_import_examples[:3])
print("  examples, unstubbable      :", unstubbable[:3])
print("  examples, true decoration  :", decoration_examples[:3])
