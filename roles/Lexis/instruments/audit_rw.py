"""Read-only audit: do @blackboard_op declared reads/writes match the body?
Writes nothing to the Apollo tree."""
import ast, glob, sys
from pathlib import Path

SRC = Path(r"F:/Prometheus/apollo/src")

def kwarg_list(call, name):
    for kw in call.keywords:
        if kw.arg == name and isinstance(kw.value, (ast.List, ast.Tuple)):
            return [e.value for e in kw.value.elts if isinstance(e, ast.Constant)]
    return None

rows = []
for f in sorted(glob.glob(str(SRC / "blackboard_ops*.py"))):
    tree = ast.parse(Path(f).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not (isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "blackboard_op"):
                continue
            declared_r = set(kwarg_list(dec, "reads") or [])
            declared_w = set(kwarg_list(dec, "writes") or [])
            # precondition lambda reads count as reads
            actual_r, actual_w = set(), set()
            for kw in dec.keywords:
                if kw.arg == "precondition":
                    for n in ast.walk(kw.value):
                        if isinstance(n, ast.Attribute) and getattr(n.value, "id", "") == "s":
                            actual_r.add(n.attr)
            for n in ast.walk(node):
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Attribute) and getattr(t.value, "id", "") == "state":
                            actual_w.add(t.attr)
                elif isinstance(n, ast.AugAssign):
                    t = n.target
                    if isinstance(t, ast.Attribute) and getattr(t.value, "id", "") == "state":
                        actual_w.add(t.attr); actual_r.add(t.attr)
                elif isinstance(n, ast.Attribute) and getattr(n.value, "id", "") == "state":
                    if isinstance(n.ctx, ast.Load):
                        actual_r.add(n.attr)
            rows.append((Path(f).name, node.name, declared_r, declared_w, actual_r, actual_w))

print(f"{len(rows)} declared operators audited\n")
undeclared_w = undeclared_r = 0
for fn, name, dr, dw, ar, aw in rows:
    uw = aw - dw
    ur = ar - dr - dw          # writing then reading your own slot is fine
    flags = []
    if uw: flags.append(f"UNDECLARED WRITE {sorted(uw)}"); 
    if ur: flags.append(f"undeclared read {sorted(ur)}")
    if uw: undeclared_w += 1
    if ur: undeclared_r += 1
    if flags:
        print(f"  {name:<28} ({fn})  " + " | ".join(flags))
print(f"\nops with undeclared WRITES: {undeclared_w}/{len(rows)}")
print(f"ops with undeclared reads : {undeclared_r}/{len(rows)}")

# write-write hazards on shared slots
print("\n=== write-write hazard pairs (do NOT commute) ===")
from itertools import combinations
seen = set()
for (f1,n1,_,w1,_,_), (f2,n2,_,w2,_,_) in combinations(rows, 2):
    shared = w1 & w2
    if shared and (n1,n2) not in seen:
        seen.add((n1,n2))
        print(f"  {n1} <-> {n2}  on {sorted(shared)}")
