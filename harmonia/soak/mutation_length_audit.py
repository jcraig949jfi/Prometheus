"""Which of this soak's mutations could have left stale bytecode? (soak P37)

P36 found that a same-BYTE-LENGTH mutation restored in the SAME SECOND leaves a
.pyc Python keeps serving, and logged WITHHELD how many earlier passes were at
risk. Same length is the NECESSARY condition: a length-changing mutation makes
the restored source mismatch the .pyc header, forcing a recompile.

Every mutation I ran is a literal (old, new) pair inside a committed probe script
under harmonia/soak/. This extracts them and compares lengths. Static analysis --
nothing is executed, nothing is mutated.
"""
import ast
import re
from pathlib import Path

SOAK = Path("harmonia/soak")
# probe scripts that mutate a file in place, and the pass that ran them
PROBES = {
 "p18_pin_check.py":            "P28",
 "p54_pin_mutation.py":         "P30",
 "p54_pin_patch_probe.py":      "P30",
 "p54_line_power.py":           "P30",
 "p14_pin_efficacy.py":         "P29",
 "blessed_pin_audit.py":        "P31",
 "p40_pin_patch_probe.py":      "P31",
 "pin_vs_suite_attribution.py": "P32",
 "suite_redundancy_census.py":  "P32",
 "conj_coupling_probe.py":      "P34",
 "predicate_corruption_probe.py": "P35",
 "three_copies_probe.py":       "P35",
}

def string_constants(path):
    """Every string literal in the file, with its length."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return None, f"parse error: {e.msg}"
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node.value)
    return out, None

print(f"{'probe script':32s} {'pass':>5s} {'literals':>9s}  same-length pairs (AT RISK)")
print("-" * 96)
at_risk_total = 0
missing = []
for name, passid in sorted(PROBES.items(), key=lambda kv: kv[1]):
    p = SOAK / name
    if not p.exists():
        missing.append(name); continue
    lits, err = string_constants(p)
    if err:
        print(f"{name:32s} {passid:>5s}  {err}"); continue
    # multi-line literals are the mutation payloads; group by length
    payloads = [s for s in lits if "\n" in s or len(s) > 30]
    bylen = {}
    for s in payloads:
        bylen.setdefault(len(s), []).append(s)
    # a risk pair = two DISTINCT payloads of identical length in the same script
    risky = {L: v for L, v in bylen.items() if len(set(v)) > 1}
    at_risk_total += len(risky)
    detail = ", ".join(f"len={L} x{len(set(v))}" for L, v in sorted(risky.items())) or "none"
    print(f"{name:32s} {passid:>5s} {len(payloads):>9d}  {detail}")

print("-" * 96)
print(f"scripts audited: {len(PROBES) - len(missing)}   missing: {missing or 'none'}")
print(f"same-length distinct payload pairs found: {at_risk_total}")
print()
print("NOTE: same length is NECESSARY, not sufficient — the restore must also land in")
print("the same filesystem second. This bounds the at-risk set from above.")
