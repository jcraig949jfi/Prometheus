"""ENVGATE-01 forensic replay (descriptive; after the frozen analysis). Re-runs chosen (block, arm) worlds with an observation-only
subclass that records, for every exact birth in every lineage, the input byte and the parent's generation, and samples descendant
genomes. Admitted only if the replayed established arrivals equal the recorded run exactly. Frozen files are not modified.

    python -m archaeon.envgate.forensic_replay --blocks 2 3 6 --arms U RESCUE_128 --workers 6
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.z80atlas.grammar import FROZEN as F
from archaeon.envgate import mechanism as M
from archaeon.envgate.engine import World, Memo, EnvStream, inflow_stream, N
from archaeon.envgate.ruler import measure
from archaeon.envgate.run_assay import SCHEDULE

HERE = Path(__file__).resolve().parent


class ForensicWorld(World):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fx = defaultdict(lambda: defaultdict(int)); self.fgen = defaultdict(lambda: defaultdict(int)); self.samples = defaultdict(dict)

    def _place(self, j, child, p, fid, epoch, x, donor):
        exact = child == self.genomes[p]; L = self.lin[p]; g = self.gen[p]
        super()._place(j, child, p, fid, epoch, x, donor)
        if exact:
            self.fx[L][x] += 1; self.fgen[L]["chamber" if p >= N else ("gen1" if g == 1 else "gen2+")] += 1
            if len(self.samples[L]) < 12 and child.hex() not in self.samples[L]: self.samples[L][child.hex()] = {"gen": g + 1, "input": x, "epoch": epoch}


def replay(block: int, arm: str) -> dict:
    K = SCHEDULE["K_chambers"]; dwell = SCHEDULE["dwell"]; E_in = SCHEDULE["refills"] * dwell; tail = M.DEFAULTS["persistence_multiple"] * F["max_age"] + 1
    memo = Memo(); env = EnvStream(block); w = ForensicWorld(arm, block, K); stream = inflow_stream(block); arrival = 0
    for epoch in range(E_in + tail):
        if epoch < E_in and epoch % dwell == 0:
            for c in range(K):
                t = next(stream); measure(t, memo); w.arrive(N + c, t, arrival, epoch); arrival += 1
        if epoch == E_in: w.clear_chambers(epoch)
        w.step(epoch, env, memo)
    est = w.established(); rec = json.loads((HERE / "runs" / ("block_%02d.json" % block)).read_text(encoding="utf-8"))["arms"][arm]["established_arrivals"]
    got = sorted(w.founder[f]["arrival"] for f in est); out = {"block": block, "arm": arm, "admitted": got == rec, "established": len(got), "lineages": []}
    estset = set(est); report = []
    for f, rec_f in w.founder.items():                                    # established lineages + every copier-founded lineage (established or not)
        cls = measure(bytes.fromhex(rec_f["tape"]))["class"] if rec_f["tape"] else "none"
        if f in estset or cls in ("EXACT_GATED", "EXACT_UNGATED", "NEAR_COPIER"): report.append((f, cls))
    for f, cls in report:
        samp = {}
        for th, meta in w.samples[f].items():
            r = measure(bytes.fromhex(th)); samp[th] = dict(meta, exact_inputs=r.get("exact_inputs", []), cls=r["class"])
        st = w.lstat[f]
        out["lineages"].append({"arrival": w.founder[f]["arrival"], "established": f in estset, "founder_class": cls, "births": st["births"], "peak": st["peak"],
                                "max_gen": st["max_gen"], "lifespan_after_removal": (st["last_alive"] - w.founder[f]["removed_epoch"]) if w.founder[f]["removed_epoch"] is not None else None,
                                "founder_exact_inputs": measure(bytes.fromhex(w.founder[f]["tape"])).get("exact_inputs", []),
                                "exact_births_by_input": dict(w.fx[f]), "exact_births_by_parent_generation": dict(w.fgen[f]), "descendant_samples": samp})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--blocks", type=int, nargs="+", required=True); ap.add_argument("--arms", nargs="+", required=True); ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args(argv); res = []
    with ProcessPoolExecutor(a.workers) as ex:
        for fu in as_completed([ex.submit(replay, b, arm) for b in a.blocks for arm in a.arms]):
            r = fu.result(); res.append(r); print(json.dumps({k: r[k] for k in ("block", "arm", "admitted", "established")}), flush=True)
    (HERE / "FORENSIC_REPLAY.json").write_text(json.dumps(sorted(res, key=lambda r: (r["block"], r["arm"])), indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0 if all(r["admitted"] for r in res) else 5


if __name__ == "__main__":
    sys.exit(main())
