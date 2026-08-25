"""Read-only. Reviewer challenge 2026-08-25: 48 sampled orderings is not exhaustive.
Compute the EXACT number of Mazurkiewicz trace classes over O1's ceiling pipeline,
using the dependency relation derived from declared reads/writes.

Key fact that makes this exact and cheap: the ceiling pipeline uses each operator at
most once, so a trace class is determined precisely by the ORIENTATION of each
dependent pair. Trace classes <= 2^(#dependent pairs).

Also reproduces O1's applicability rule as a self-check against its reported 166,320.
"""
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
                    decl[nm or node.name] = (set(kwl(dec, "reads")), set(kwl(dec, "writes")))

CEIL = ["parse_box_items", "op_aggregate_quantities", "parse_comparison",
        "parse_names_and_relations", "parse_ordinal", "parse_rules", "forward_chain",
        "parse_which_extreme", "relations_from_facts", "op_build_ordering"]
SEED = {"problem_text", "candidates"}

def indep(a, b):
    ra, wa = decl[a]; rb, wb = decl[b]
    return not (wa & rb) and not (wb & ra) and not (wa & wb)

dep_pairs = [ (a,b) for a,b in combinations(CEIL, 2) if not indep(a,b) ]
print("operators: %d   dependent pairs: %d   independent: %d"
      % (len(CEIL), len(dep_pairs), len(list(combinations(CEIL,2))) - len(dep_pairs)))
print("upper bound on trace classes = 2^%d = %d\n" % (len(dep_pairs), 2**len(dep_pairs)))

# Enumerate valid orderings under O1's applicability rule: an op is applicable iff
# every slot it reads is already written (seed inputs excepted).
valid_count = 0
signatures = {}          # orientation vector -> one witness ordering

def dfs(seq, written, remaining):
    global valid_count
    if not remaining:
        valid_count += 1
        pos = {op: i for i, op in enumerate(seq)}
        sig = tuple(pos[a] < pos[b] for a, b in dep_pairs)
        signatures.setdefault(sig, list(seq))
        return
    for op in list(remaining):
        reads, writes = decl[op]
        if reads <= written:
            dfs(seq + [op], written | writes, remaining - {op})

dfs([], set(SEED), set(CEIL))

print("valid orderings under the applicability rule : %d" % valid_count)
print("O1 reported for the known 10-op subset        : 166,320")
print("match" if valid_count == 166320 else "MISMATCH -- applicability model differs from O1's")
print()
print("DISTINCT TRACE CLASSES (semantically distinct schedules): %d" % len(signatures))
print()
for sig, witness in sorted(signatures.items()):
    forced = [(dep_pairs[i], sig[i]) for i in range(len(dep_pairs))]
    flipped = [ "%s BEFORE %s" % (a if o else b, b if o else a) for (a,b), o in forced ]
    print("  class: " + " | ".join(flipped[:2]) + (" ..." if len(flipped) > 2 else ""))
print()
print("Free orientations (pairs that actually vary across valid orderings):")
varying = [dep_pairs[i] for i in range(len(dep_pairs))
           if len({s[i] for s in signatures}) > 1]
for a, b in varying:
    print("   %s <-> %s" % (a, b))
if not varying:
    print("   NONE -- every dependent pair is forced by the applicability rule.")
