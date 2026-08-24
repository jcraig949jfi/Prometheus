"""G1 rungs 1-2, read-only: for each T2 forged tool, which primitives does it
IMPORT, and which of those does it actually CALL? Pure AST. No execution, no model.
Writes nothing outside stdout."""
import ast, glob, os
from pathlib import Path

FORGE = Path(r"F:/Prometheus/forge/v2/hephaestus_t2/forge")
PRIM_MODULES = {"forge_primitives_t2", "forge_primitives", "_t1_parsers"}

rows = []
for fp in sorted(FORGE.glob("*.py")):
    src = fp.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        rows.append((fp.name, None, None, "PARSE ERROR %s" % e)); continue

    imported = {}          # name -> source module
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            mod = n.module.split(".")[-1]
            if mod in PRIM_MODULES or mod.startswith("t2_") or mod.startswith("t1_"):
                for a in n.names:
                    imported[a.asname or a.name] = mod

    called = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            nm = None
            if isinstance(f, ast.Name):
                nm = f.id
            elif isinstance(f, ast.Attribute):
                nm = f.attr
            if nm in imported:
                called[nm] = called.get(nm, 0) + 1
    rows.append((fp.name, imported, called, None))

print("G1 rungs 1-2 -- declared vs called primitive usage, T2 forge")
print("=" * 74)
tot_imp = tot_used = 0
for name, imported, called, err in rows:
    if err:
        print("  %-36s %s" % (name, err)); continue
    if not imported:
        print("  %-36s no primitive imports" % name); continue
    used = [k for k in imported if k in called]
    unused = [k for k in imported if k not in called]
    tot_imp += len(imported); tot_used += len(used)
    print("  %-36s %d/%d imported primitives called" % (name, len(used), len(imported)))
    for k in sorted(used):
        print("      CALLED   %-24s x%-3d  (%s)" % (k, called[k], imported[k]))
    for k in sorted(unused):
        print("      IMPORTED %-24s x0    (%s)  <-- never called" % (k, imported[k]))

print("=" * 74)
if tot_imp:
    print("TOTAL: %d of %d imported primitives are called at least once (%.0f%%)"
          % (tot_used, tot_imp, 100.0 * tot_used / tot_imp))
    print("NOTE: 'called' is a static call site, NOT an executed one. Rung 3")
    print("      (coverage trace) and rung 4 (ablation) are the decisive rungs.")
else:
    print("no primitive imports found -- check PRIM_MODULES against the real layout")
