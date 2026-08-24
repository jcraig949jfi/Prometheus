"""Read-only: derive the independence (commutation) relation over O1's ceiling
pipeline from declared reads/writes, via Bernstein's conditions."""
import ast, glob
from pathlib import Path
from itertools import combinations

SRC = Path(r"F:/Prometheus/apollo/src")
def kwl(call, name):
    for kw in call.keywords:
        if kw.arg == name and isinstance(kw.value, (ast.List, ast.Tuple)):
            return [e.value for e in kw.value.elts if isinstance(e, ast.Constant)]
    return []

decl = {}
for f in glob.glob(str(SRC / "blackboard_ops*.py")):
    tree = ast.parse(Path(f).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "blackboard_op":
                    nm = None
                    for kw in dec.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                            nm = kw.value.value
                    nm = nm or node.name
                    decl[nm] = (set(kwl(dec,"reads")), set(kwl(dec,"writes")))

CEIL = ["parse_box_items","op_aggregate_quantities","parse_comparison",
        "parse_names_and_relations","parse_ordinal","parse_rules","forward_chain",
        "parse_which_extreme","relations_from_facts","op_build_ordering"]

missing = [o for o in CEIL if o not in decl]
print("ops not found in declarations:", missing or "none")
ops = [o for o in CEIL if o in decl]
print(f"analysing {len(ops)} transformers of O1's ceiling pipeline\n")

def independent(a, b):
    ra, wa = decl[a]; rb, wb = decl[b]
    return not (wa & rb) and not (wb & ra) and not (wa & wb)

dep, ind = [], []
for a, b in combinations(ops, 2):
    (ind if independent(a,b) else dep).append((a,b))

print(f"DEPENDENT pairs (order matters): {len(dep)}")
for a,b in dep:
    ra,wa = decl[a]; rb,wb = decl[b]
    why = []
    if wa & rb: why.append(f"{a} writes {sorted(wa&rb)} that {b} reads")
    if wb & ra: why.append(f"{b} writes {sorted(wb&ra)} that {a} reads")
    if wa & wb: why.append(f"both write {sorted(wa&wb)}")
    print(f"   {a} -- {b}: " + "; ".join(why))
print(f"\nINDEPENDENT pairs (commute freely): {len(ind)} of {len(dep)+len(ind)} total pairs")
print(f"→ {100*len(ind)//(len(dep)+len(ind))}% of operator pairs in the ceiling pipeline are order-irrelevant")
