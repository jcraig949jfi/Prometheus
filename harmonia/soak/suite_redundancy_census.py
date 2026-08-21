"""Does the verifier_lens suite have redundant coverage anywhere? (soak P32)

P32 found the unknown_kind contract is held by exactly ONE test, with zero other
tests firing on any of four mutations. Claiming "this suite has no redundancy"
from a single contract is the base-rate error -- one instance is not a
disposition. This measures the reference class: six one-line, semantically severe
mutations at DIFFERENT sites, counting how many tests catch each.

Line-based rather than string-based: three of the target lines are byte-identical
to each other, so a string replace could not address them individually.
"""
import re
import subprocess
import sys
from pathlib import Path

VL = Path("harmonia/experiments/verifier_lens.py")
original = VL.read_text(encoding="utf-8")
lines = original.splitlines(keepends=True)

# (1-indexed line, substring to replace, replacement, description)
SITES = [
 (238, '"valid": bool(valid)', '"valid": True',  "verifier A always passes"),
 (311, '"valid": bool(valid)', '"valid": True',  "verifier B always passes"),
 (366, '"valid": bool(valid)', '"valid": True',  "verifier C always passes"),
 (441, '"valid": False',       '"valid": True',  "bogus counterexample ACCEPTED"),
 (478, '"valid": None',        '"valid": False', "unverifiable universal -> killed"),
 (485, '"valid": None',        '"valid": False', "unverifiable universal -> killed (2)"),
]
CMD = [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_lens.py",
       "-q", "--tb=no", "-rf"]


def failing():
    r = subprocess.run(CMD, capture_output=True, text=True, timeout=300)
    return sorted({m.group(1) for m in re.finditer(r"FAILED \S+::(\w+)", r.stdout)})


assert not failing(), "suite not green at baseline"
print("baseline green.\n")
print(f"{'site':>5s}  {'description':38s} {'#tests red':>10s}  tests")
print("-" * 104)
counts = []
try:
    for ln, old, new, desc in SITES:
        idx = ln - 1
        if old not in lines[idx]:
            print(f"{ln:>5d}  {desc:38s} {'--':>10s}  TARGET MOVED — skipped")
            continue
        mutated = list(lines)
        mutated[idx] = mutated[idx].replace(old, new)
        VL.write_text("".join(mutated), encoding="utf-8")
        f = failing()
        counts.append((ln, desc, f))
        shown = ", ".join(t.replace("test_", "") for t in f[:3])
        if len(f) > 3:
            shown += f" +{len(f)-3}"
        print(f"{ln:>5d}  {desc:38s} {len(f):>10d}  {shown or '*** NONE — mutation SURVIVES ***'}")
finally:
    VL.write_text(original, encoding="utf-8")
    assert VL.read_text(encoding="utf-8") == original, "RESTORE FAILED"

print("-" * 104)
caught = [c for c in counts if c[2]]
survived = [c for c in counts if not c[2]]
singles = [c for c in caught if len(c[2]) == 1]
print(f"sites mutated              : {len(counts)}")
print(f"caught by >=1 test         : {len(caught)}")
print(f"SURVIVED (no test fires)   : {len(survived)}")
for ln, desc, _ in survived:
    print(f"    line {ln}: {desc}")
print(f"caught by EXACTLY ONE test : {len(singles)} of {len(caught)}")
if caught:
    dist = sorted(len(c[2]) for c in caught)
    print(f"tests-firing distribution  : {dist}")
print("\nfile restored byte-identical: True")
