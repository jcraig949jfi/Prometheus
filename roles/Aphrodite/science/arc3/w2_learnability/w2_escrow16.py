"""W2 stage 3: the PRISTINE walk run for real (a18.fast_cost, exact) at 16x escrow
(4,000,000 charges) on every T4-qualified NATURAL family, the same 4 pilot cells.
Records the first dev-consistent hit, its charge, its segment (coverage / expr /
fallback) and whether it is T4-qualified. Measures what the fallback yields
beyond the 250k escrow. Pool of 2 workers (lease W2).
"""
import sys
from concurrent.futures import ProcessPoolExecutor
from w2_common import *

ESC = 4_000_000


def job(r):
    a18.worker_init()
    lib = FR.KLib(FR.pristine().entries)
    prov, cs = cells(r)
    out = []
    for c in cs:
        ch, prog = a18.fast_cost(lib, c, ESC)
        q = bool(prog) and C.t4_qualified(prov, r["name"], prog)[0]
        seg = None if not prog else ("cov" if ch <= N_COV else ("expr" if prog[0] == "expr" else "fallback"))
        out.append({"charge": ch, "prog": list(prog) if prog else None, "segment": seg, "T4": q})
    return {"name": r["name"], "p_PRISTINE": r["p_PRISTINE"], "cells": out}


if __name__ == "__main__":
    rs = rows("NAT")
    shard, nsh = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
    rs = rs[shard::nsh]
    rev = len(sys.argv) > 4 and sys.argv[4] == "rev"
    if rev:
        rs = rs[::-1]      # second worker on the same shard from the other end (deterministic; deduplicated by name)
    done = set()
    outp = HERE / ("w2_escrow16_NAT_s%d%s.jsonl" % (shard, "r" if rev else ""))
    if outp.exists():
        done = {json.loads(l)["name"] for l in open(outp)}
    todo = [r for r in rs if r["name"] not in done]
    with ProcessPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 2, initializer=a18.worker_init) as ex, \
            open(outp, "a", encoding="utf-8") as fh:
        for res in ex.map(job, todo):
            fh.write(json.dumps(res) + "\n"); fh.flush()
    print("done")
