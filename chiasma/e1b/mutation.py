"""E1b mutation check: do the E1b known-answer tests catch planted one-line defects in
the E1b code (world_h3.py, arms.py, run.py)?

Reuses chiasma.wt0_mutation's harness (copy chiasma/ to a temp dir, apply one edit,
run the whole test suite there). KILLED = suite fails; SURVIVED = passes;
NOT_APPLIED = the edit did not match exactly once (never counted as a kill).

Run: python -B -m chiasma.e1b.mutation
"""
import json
import os
import shutil
import sys
import tempfile

from ..wt0_mutation import HERE, run_suite

MUTANTS = [
    ("E01 A/B sampler forces only the first pair", "e1b/world_h3.py",
     "                for C, F in CF:\n                    if x & C:", "                for C, F in CF[:1]:\n                    if x & C:"),
    ("E02 exceptions keep f", "e1b/world_h3.py",
     "                    x = (x | C) & ~F", "                    x = (x | C)"),
    ("E03 crit probes use pair 0 for every target", "e1b/world_h3.py",
     "            c, f = w.pairs[w.abs_of[t.name]]\n            C, F = 1 << c, 1 << f\n            core",
     "            c, f = w.pairs[0]\n            C, F = 1 << c, 1 << f\n            core"),
    ("E04 decoys carry f", "e1b/world_h3.py",
     "\"decoy\", (C | fresh_pair(),)", "\"decoy\", (C | F | fresh_pair(),)"),
    ("E05 loads swapped (ydep count = decoy count)", "e1b/world_h3.py",
     "        for i in range(ny):", "        for i in range(nd):"),
    ("E06 O4LR records the true pruned literal", "e1b/arms.py",
     "        if outside:\n", "        if False:\n"),
    ("E07 O4LR draws inside the anchor", "e1b/arms.py",
     "        outside = [b for b in range(self.m) if not (anchor >> b) & 1]",
     "        outside = [b for b in range(self.m) if (anchor >> b) & 1]"),
    ("E08 O3U keeps the cap", "e1b/arms.py",
     "O3U=dict(neg=\"proj\", consolidate=True, seams=\"none\", uncapped=True)",
     "O3U=dict(neg=\"proj\", consolidate=True, seams=\"none\")"),
    ("E09 run.py err_CDE drops D", "e1b/run.py",
     "    CDE = (\"C\", \"D\", \"E\")", "    CDE = (\"C\", \"E\")"),
    ("E10 run.py collateral baseline is end of A", "e1b/run.py",
     "    last_B = [cp for cp in cps if cp[\"phase\"] == \"B\"][-1]",
     "    last_B = [cp for cp in cps if cp[\"phase\"] == \"A\"][-1]"),
    ("E11 C breaks every pair at once", "e1b/world_h3.py",
     "                    C, F = CF[r.randrange(len(CF))]\n                    x = (x | C) & ~F",
     "                    for C, F in CF:\n                        x = (x | C) & ~F"),
    ("E12 O4LR counterfeit drops entries (fewer U bytes)", "e1b/arms.py",
     "            c.prov = [(1 << self.rng.choice(outside), j) for _l, j in c.prov]",
     "            c.prov = [(1 << self.rng.choice(outside), j) for _l, j in c.prov][:0]"),
    ("E13 weldable flag ignored", "e1b/arms.py",
     "        self.weldable = bool(self.ARMS[arm].get(\"weldable\"))", "        self.weldable = False"),
    ("E14 weldable arm welds with the stale anchor", "e1b/arms.py",
     "            anchor = c.premise if c.consolidated else c.anchor", "            anchor = c.anchor if c.anchor is not None else 0"),
    ("E15 binding budget evicts nothing", "e1b/arms.py",
     "            self.cells[vname].remove(victim)\n", "            break\n"),
]


def main() -> int:
    results = []
    base = tempfile.mkdtemp(prefix="chiasma_e1b_mut_")
    try:
        clean = os.path.join(base, "clean")
        shutil.copytree(HERE, os.path.join(clean, "chiasma"), ignore=shutil.ignore_patterns("__pycache__", "runs"))
        rc0 = run_suite(clean)
        print("clean suite rc={}".format(rc0))
        if rc0 != 0:
            print("CLEAN SUITE FAILS; mutation check not meaningful")
            return 2
        for i, (name, fn, old, new) in enumerate(MUTANTS):
            root = os.path.join(base, "m{:02d}".format(i))
            shutil.copytree(os.path.join(clean, "chiasma"), os.path.join(root, "chiasma"))
            path = os.path.join(root, "chiasma", fn)
            src = open(path, encoding="utf-8").read()
            if src.count(old) != 1:
                status = "NOT_APPLIED"
            else:
                open(path, "w", encoding="utf-8", newline="\n").write(src.replace(old, new))
                status = "KILLED" if run_suite(root) != 0 else "SURVIVED"
            results.append({"mutant": name, "status": status})
            print("{:<12} {}".format(status, name))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    summary = {k: sum(1 for r in results if r["status"] == k) for k in ("KILLED", "SURVIVED", "NOT_APPLIED")}
    print(json.dumps({"schema": "chiasma.e1b.mutation.v1", "summary": summary, "results": results}, sort_keys=True))
    return 0 if summary["SURVIVED"] == 0 and summary["NOT_APPLIED"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
