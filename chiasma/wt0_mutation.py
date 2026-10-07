"""WT-0 mutation check: does the known-answer suite catch planted one-line defects?

Each mutant copies chiasma/ to a temporary directory, applies one textual edit,
and runs the WT-0 suite there. A mutant is KILLED if the suite fails, SURVIVED if it
passes. Edits that do not apply are reported as NOT_APPLIED (never counted as kills).

Run: python -B -m chiasma.wt0_mutation  (prints one line per mutant, then a JSON summary)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

MUTANTS = [
    ("M01 A/B sampler stops forcing c->f", "world.py", "                if x & C:\n                    x |= F", "                if x & C:\n                    x |= 0"),
    ("M02 exceptions keep f", "world.py", "                    x = (x | C) & ~F", "                    x = (x | C)"),
    ("M03 weld takes the union", "organisms.py", "            inter = c.anchor & x", "            inter = c.anchor | x"),
    ("M04 consolidation prunes nothing", "organisms.py", "                if self.imp[u] & lb:", "                if False:"),
    ("M05 projection keeps subsumed negatives", "organisms.py", "                return                          # subsumed", "                pass"),
    ("M06 seams never restore", "organisms.py", "                    c.premise |= hit", "                    c.premise |= 0"),
    ("M07 Imp breaks never detected", "organisms.py", "            broken = self.imp[u] & ~new", "            broken = 0"),
    ("M08 byte ruler halves U", "organisms.py", "                U += 2 * len(c.prov)", "                U += len(c.prov)"),
    ("M09 receipts accept floats", "runner.py", "            raise TypeError(\"floats are refused in receipts\")", "            pass"),
    ("M10 retract keeps the cell", "organisms.py", "            cells.remove(c)\n            self.events[\"retract\"] += 1", "            self.events[\"retract\"] += 1"),
    ("M11 random shadow keeps content", "organisms.py", "            n = sum(1 << b for b in self.rng.sample(range(self.m), k))", "            n = n"),
    ("M12 lazy arm opens eager seams", "organisms.py", "if broken and self.seams in (\"true\", \"rand\"):", "if broken and self.seams != \"none\":"),
    ("M13 critical probes keep f", "world.py", "                x = (_draw(r, w.spec) | core | C) & ~F", "                x = (_draw(r, w.spec) | core | C)"),
    ("M14 byte cap ignored", "organisms.py", "        if total <= self.cap:\n            return", "        if True:\n            return"),
    ("M15 seam confirmation never fires", "organisms.py", "                if base & x == base and not (c.disputed & x):", "                if False:"),
    ("M16 prov records the pruned literal as its own justifier", "organisms.py", "                    j = 1 << u\n", "                    j = lb\n"),
]


def run_suite(root: str) -> int:
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "chiasma/tests", "-t", "."],
                       cwd=root, capture_output=True, text=True)
    return r.returncode


def main() -> int:
    results = []
    base = tempfile.mkdtemp(prefix="chiasma_mut_")
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
    print(json.dumps({"schema": "chiasma.wt0.mutation.v1", "summary": summary, "results": results}, sort_keys=True))
    return 0 if summary["SURVIVED"] == 0 and summary["NOT_APPLIED"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
