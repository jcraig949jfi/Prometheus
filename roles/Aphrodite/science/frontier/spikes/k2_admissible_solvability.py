"""SPIKE K2 -- for the K1-admissible witnesses: does Q2 (generator
qualification, exact-fast form) pass, and can PRISTINE / L1 (G1) find a
program consistent with the dev set within the frozen escrow? Read-only.

Solvability is measured as 'a hit within escrow' on 4 cells per arm (no
tribunal on the hit -- an upper bound on qualified solves). Labels are
forensic ('K2-...'), never campaign labels.
"""
import json
import random
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
import os  # noqa: E402
os.environ["A17_FASTEVAL"] = "1"
import a17  # noqa: E402
import engine as E  # noqa: E402
import fair as FR  # noqa: E402
import identity as I  # noqa: E402
import tier3e as T3E  # noqa: E402

HERE = Path(__file__).resolve().parent


def job(args):
    a17.worker_init()
    k, op, init, body, final, g1b = args
    name = "kfam_%s_%s" % (op, "".join("abcdefghijklmnopqrstuvwxyz"[int(c)] for c in "%04d" % k))
    prov = a17.Prov({name: (body, final, init)})
    a17.M.use_provider(prov)
    size = a17.qualify(prov, name, "K2")
    row = {"op": op, "init": init, "body": body, "final": final, "g1_body": g1b, "Q2_size": size}
    if size is None:
        return row
    for arm, ents in (("PRISTINE", FR.pristine().entries), ("L1", a17.L1_entries())):
        lib = FR.KLib(ents)
        solved, coords, charges = 0, Counter(), []
        for i in range(4):
            c = FR.Cell(prov, name, i, size, label="K2-%s" % arm)
            esc = E.Escrow(a17.ESCROW)
            hits = FR.search_collect(lib, c.parsed, esc, a17.ESCROW, c.seed, max_hits=1)
            if hits:
                solved += 1
                coords[hits[0][1]] += 1
                charges.append(hits[0][2])
        row[arm] = {"solved": solved, "coords": dict(coords), "charges": charges}
    return row


if __name__ == "__main__":
    census = json.loads((HERE / "K1_SUPPLY_CENSUS.json").read_text())
    # re-derive the admissible list deterministically from K1's sampler
    import k1_supply_census as K1
    samp = K1.sample()
    with ProcessPoolExecutor(8) as ex:
        rows = list(ex.map(K1._w, samp, chunksize=20))
    adm = [(op, r) for op, r in rows if r["admissible"]]
    ng = [(op, r) for op, r in adm if not r["g1_body"]]
    g1 = [(op, r) for op, r in adm if r["g1_body"]]
    random.Random(7).shuffle(g1)
    pick = ng + g1[:60]
    jobs = [(k, op, r["init"], r["body"], r["final"], r["g1_body"]) for k, (op, r) in enumerate(pick)]
    with ProcessPoolExecutor(8, initializer=a17.worker_init) as ex:
        out = list(ex.map(job, jobs, chunksize=1))
    summ = defaultdict(Counter)
    for r in out:
        key = ("G1body" if r["g1_body"] else "nonG1") + "/" + r["op"]
        s = summ[key]
        s["n"] += 1
        s["Q2_pass"] += r["Q2_size"] is not None
        if r["Q2_size"] is not None:
            for arm in ("PRISTINE", "L1"):
                s[arm + "_any"] += r[arm]["solved"] > 0
                s[arm + "_cells"] += r[arm]["solved"]
            s["L1_only"] += r["L1"]["solved"] > 0 and r["PRISTINE"]["solved"] == 0
            s["neither"] += r["L1"]["solved"] == 0 and r["PRISTINE"]["solved"] == 0
    (HERE / "K2_ADMISSIBLE_SOLVABILITY.json").write_text(json.dumps({"summary": {k: dict(v) for k, v in summ.items()},
                                                                     "rows": out}, indent=1))
    for k in sorted(summ):
        print(k, dict(summ[k]))
