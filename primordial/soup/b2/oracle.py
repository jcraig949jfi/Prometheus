"""B2 oracle: a form is the SAME GraphWorld iff its trajectory hash equals the plain-Python
reference on every spec. Cheat no_flee must differ wherever a prey was ever threatened.

usage: python -m primordial.soup.b2.oracle --forms gb --specs 50 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys

from .graphworld import Spec, run_gb, run_ref, step_cell


def specs(k: int) -> list[Spec]:
    out = []
    for j in range(k):
        L = (6, 8, 12, 16, 24)[j % 5]
        out.append(Spec(L=L, n_pred=1 + j % 4, n_prey=2 + (j * 3) % 9, n_food=1 + (j * 5) % 11,
                        ticks=64, seed=1000 + 17 * j))
    return out


def ever_threatened(s: Spec) -> bool:
    """Replay the reference and report whether any live prey sat within 1 cell of a
    predator at a MOVE phase (i.e. the no_flee semantic was exercised)."""
    cell = {i: s.init_cell(i) for i in range(s.n)}
    for t in range(s.ticks):
        pred = [i for i in cell if s.kind(i) == 0]
        prey = [i for i in cell if s.kind(i) == 1]
        prey_cells = {cell[q] for q in prey}
        for f in [i for i in cell if s.kind(i) == 2]:
            if cell[f] in prey_cells:
                del cell[f]
        pred_cells = {cell[p] for p in pred}
        for q in prey:
            if cell[q] in pred_cells:
                del cell[q]
        prey = [q for q in prey if q in cell]
        near = set()
        for p in pred:
            near.add(cell[p])
            near.update(step_cell(s.L, cell[p], d) for d in range(4))
        if any(cell[q] in near for q in prey):
            return True
        for i in pred + prey:
            cell[i] = step_cell(s.L, cell[i], (i * 7 + t * 3) % 4)
    return False


def _cypher(s, cheat=""):
    from .cypher_world import run_cypher
    return run_cypher(s, cheat=cheat)


FORMS = {"gb": run_gb, "cy": _cypher}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", default="gb")
    ap.add_argument("--specs", type=int, default=50)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for j, s in enumerate(specs(a.specs)):
        ref = run_ref(s)
        thr = ever_threatened(s)
        for form in a.forms.split(","):
            for cheat in ("", "no_flee"):
                got = FORMS[form](s, cheat=cheat)
                rows.append({"spec": j, "L": s.L, "n": s.n, "form": form, "cheat": cheat or None,
                             "threatened": thr, "equal": got == ref})
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    summ = {}
    for form in a.forms.split(","):
        hon = [r for r in rows if r["form"] == form and r["cheat"] is None]
        ch = [r for r in rows if r["form"] == form and r["cheat"] == "no_flee"]
        summ[form] = {"honest_equal": sum(r["equal"] for r in hon), "specs": len(hon),
                      "cheat_detected_threatened": sum(not r["equal"] for r in ch if r["threatened"]),
                      "threatened_specs": sum(r["threatened"] for r in ch),
                      "cheat_detected_unthreatened": sum(not r["equal"] for r in ch if not r["threatened"])}
    print(json.dumps(summ, indent=1))
    return 0 if all(v["honest_equal"] == v["specs"] for v in summ.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
