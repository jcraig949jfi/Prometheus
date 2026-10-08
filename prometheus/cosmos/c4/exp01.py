"""EXP-01: LOCAL SYSID on fresh DISCOVERY worlds of four visible families (exploratory; prereg
roles/Cosmos/c4/prereg/EXP-01_LOCAL_DISCOVERY.md).

Per world: native knobs (natural distribution P), k, LOCAL coordinates (k-free; computed once per world and
verified identical across k only in tests), Certificate A class, Certificate B (linear decoder), T3-DOWN.
Rows are appended to a JSONL checkpoint as they finish, so an interrupted run resumes where it stopped.

    python -m prometheus.cosmos.c4.exp01 <out.jsonl> <n_per_family> [workers] [batch]
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.substrates import RNN, Graph, Stig
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4 import firewall as FW
from prometheus.cosmos.c4.baselines import t3_down
from prometheus.cosmos.c4.cert_b import b_use
from prometheus.cosmos.c4.families.theseus_sediment import world as SED
from prometheus.cosmos.c4.sysid_local import LocalProbe, coordinates
from prometheus.cosmos.hashing import h

KS = (2, 4, 8)
V = 4
# Natural distribution P for the C3 families: uniform over the INTERVAL spanned by the C3 lattice (continuous
# knobs) or the lattice itself (integer knobs), so DISCOVERY worlds are fresh (the C3 visible worlds are burned).
P_C3 = {
    "rnn": {"rho": (0.0, 1.1), "a": (0.2, 1.0), "sigma": (0.01, 1.0)},
    "graph": {"K": [1, 2, 3, 4, 6], "b": (-1.0, 0.5), "p": (0.0, 0.1)},
    "stig": {"delta": (0.02, 0.6), "D": (0.0, 0.3), "v": [0, 1, 2], "j": (0.0, 0.3)},
}
FAMILIES = ("rnn", "graph", "stig", "sediment")


def sample_world(fam: str, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    if fam == "sediment":
        kn = SED.sample_natural(rng)
    else:
        kn = {}
        for f, spec in P_C3[fam].items():
            kn[f] = int(spec[rng.integers(len(spec))]) if isinstance(spec, list) else float(rng.uniform(*spec))
        if fam in ("rnn", "graph"):
            kn["wseed"] = int(rng.integers(1, 2 ** 31))
    return {"family": fam, "knobs": kn, "k": int(KS[rng.integers(len(KS))])}


def build(fam: str, kn: dict, k: int):
    t = Task(V, k)
    if fam == "rnn":
        return RNN(t, kn["rho"], kn["a"], kn["sigma"], wseed=kn["wseed"]), t
    if fam == "graph":
        return Graph(t, kn["K"], kn["b"], kn["p"], wseed=kn["wseed"]), t
    if fam == "stig":
        return Stig(t, kn["delta"], kn["D"], kn["v"], kn["j"]), t
    if fam == "sediment":
        return SED.build_world(**kn), t
    raise ValueError(fam)


def run_world(job: dict) -> dict:
    t0 = time.time()
    fam, kn, k = job["family"], job["knobs"], job["k"]
    sys_, task = build(fam, kn, k)
    wid = h({"family": fam, "knobs": kn})
    coords = coordinates(LocalProbe(sys_, task.n_symbols, seed=int(wid[:8], 16)))
    A = certify(sys_, task, seed=int(wid[8:16], 16))
    B = b_use(sys_, task, "linear", seed=int(wid[16:24], 16))
    return {**job, "world_id": wid, "coords": coords, "A": A["class"], "A_P1_D": A["P1"]["D_bits"],
            "A_P2_effect": A["P2"]["effect"], "B": B["functional"], "B_acc": B["acc"], "T3": t3_down(sys_, task),
            "sec": round(time.time() - t0, 1)}


def jobs(n_per_family: int, batch: int = 0, split: str = "DISCOVERY"):
    out = []
    for fi, fam in enumerate(FAMILIES):
        for i in range(n_per_family):
            j = sample_world(fam, FW.split_seed(split, batch, fi * 100000 + i))
            j.update({"split": split, "batch": batch, "i": i})
            out.append(j)
    return out


def main(out: str, n: int, workers: int = 3, batch: int = 0, split: str = "DISCOVERY"):
    p = Path(out)
    done = set()
    if p.exists():
        done = {(r["family"], r["i"]) for r in map(json.loads, p.read_text().splitlines()) if r}
    todo = [j for j in jobs(n, batch, split) if (j["family"], j["i"]) not in done]
    ctx = get_context("spawn")
    with ctx.Pool(workers, maxtasksperchild=4) as pool, open(p, "a") as fh:
        for r in pool.imap_unordered(run_world, todo):
            fh.write(json.dumps(r, default=float) + "\n")
            fh.flush()


if __name__ == "__main__":
    a = sys.argv
    main(a[1], int(a[2]), int(a[3]) if len(a) > 3 else 3, int(a[4]) if len(a) > 4 else 0,
         a[5] if len(a) > 5 else "DISCOVERY")
