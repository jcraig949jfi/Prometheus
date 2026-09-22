"""B2 entity-ticks/s by world size for ref (plain Python), gb (python-graphblas), cy (FalkorDB).
Density fixed: entities ~ cells / 8 (pred : prey : food = 1 : 3 : 4). Setup is untimed,
except that the gb/cy forms build their static relations inside run_*, so small worlds
include that cost; recorded as a caveat, and every form pays it equally for ref=0.

usage: python -m primordial.soup.b2.bench --forms ref,gb,cy --L 16,32,64,128,256 --ticks 16 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
import time

from .graphworld import Spec, run_gb, run_ref


def _cy(s):
    from .cypher_world import run_cypher
    return run_cypher(s, graph="b2bench")


FORMS = {"ref": run_ref, "gb": run_gb, "cy": _cy}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", default="ref,gb,cy")
    ap.add_argument("--L", default="16,32,64,128,256")
    ap.add_argument("--ticks", type=int, default=16)
    ap.add_argument("--cap", default="cy:64", help="form:max_L")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    caps = dict((kv.split(":")[0], int(kv.split(":")[1])) for kv in a.cap.split(",") if kv)
    with open(a.out, "a", encoding="utf-8", newline="\n") as fh:
        for L in (int(x) for x in a.L.split(",")):
            e = max(8, (L * L) // 8)
            s = Spec(L=L, n_pred=e // 8, n_prey=3 * e // 8, n_food=e // 2, ticks=a.ticks, seed=L)
            hashes = {}
            for form in a.forms.split(","):
                if form in caps and L > caps[form]:
                    continue
                t0 = time.perf_counter()
                hashes[form] = FORMS[form](s)
                wall = time.perf_counter() - t0
                row = {"form": form, "L": L, "entities": s.n, "ticks": s.ticks, "wall_s": wall,
                       "entity_ticks_per_s": s.n * s.ticks / wall,
                       "equal_ref": (hashes[form] == hashes["ref"]) if "ref" in hashes else None}
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                fh.flush()
                print(f"{form:3s} L={L:4d} n={s.n:6d} ent-ticks/s={row['entity_ticks_per_s']:,.0f} "
                      f"eq_ref={row['equal_ref']}", flush=True)


if __name__ == "__main__":
    main()
