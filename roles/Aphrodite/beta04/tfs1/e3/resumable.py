"""Checkpointed lifetimes: a production lifetime at B = 2e5 exceeds the 15 CPU-min single-run cap, so it is run as a
sequence of processes, each continuing from a JSON checkpoint written after a completed family.

The checkpoint holds the organism's complete developmental state (solved corpus, candidate store, promotion cost
ledger, seen entry ids, library, library snapshots, archive, ledger, family records) and the configuration; the
lifetime is deterministic per family, so a resumed lifetime is IDENTICAL to an uninterrupted one (tested:
decision_sha256, library and archive).

  python -m tfs1.e3.resumable --world W --arm ARM --seed S --B 200000 --ckpt PATH --max-cpu 780
  (re-invoke with the same arguments until it prints DONE; the final record is written to PATH with "done": true)
"""
import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                      # noqa: E402
from tfs1.library import Library                # noqa: E402
from tfs1.e3 import organism as O               # noqa: E402
from tfs1.e3 import worlds as WD                # noqa: E402


def _cand_out(c):
    d = {k: v for k, v in c.items() if k != "body"}
    d["body"] = C.to_str(c["body"])
    return d


def _cand_in(d):
    c = dict(d)
    c["body"] = C.parse(d["body"])
    return c


class ResumableOrganism(O.Organism):
    def state(self, families, next_i) -> dict:
        st = {"next": next_i, "families": families, "library": self.lib.to_json(),
              "library_snapshots": self.lib_snapshots, "archive": self.archive, "ledger": dict(self.ledger)}
        if self.dev is not None:
            st["dev"] = {"corpus": [C.to_str(p) for p in self.dev.corpus],
                         "cands": {k: _cand_out(c) for k, c in self.dev.cands.items()},
                         "cost": self.dev.cost, "seen_ids": sorted(self.dev.seen_ids)}
        return st

    def load_state(self, st):
        self.lib = Library.from_json(st["library"])
        self.lib_snapshots = st["library_snapshots"]
        self.archive = st["archive"]
        self.ledger = Counter(st["ledger"])
        if self.dev is not None and "dev" in st:
            d = st["dev"]
            self.dev.corpus = [C.parse(s) for s in d["corpus"]]
            self.dev.cands = {k: _cand_in(c) for k, c in d["cands"].items()}
            self.dev.cost = d["cost"]
            self.dev.seen_ids = set(d["seen_ids"])
        return st["families"], st["next"]

    def run_until(self, ckpt_path, max_cpu_s: float) -> dict:
        p = Path(ckpt_path)
        families, i = [], 0
        if p.exists():
            ck = json.loads(p.read_text())
            if ck.get("done"):
                return ck
            families, i = self.load_state(ck["state"])
        t0 = time.process_time()
        while i < len(self.order):
            families.append(self.run_family(self.order[i]))
            i += 1
            if time.process_time() - t0 > max_cpu_s and i < len(self.order):
                break
        if i < len(self.order):
            p.write_text(json.dumps({"done": False, "config": self.cfg, "arm": self.arm, "seed": self.seed,
                                     "state": self.state(families, i)}, sort_keys=True))
            return {"done": False, "next": i}
        rec = self._finish(families)
        rec["done"] = True
        p.write_text(json.dumps(rec, sort_keys=True))
        return rec

    def _finish(self, fams):
        decisions = [(f["slot"], f["hit_charge"], f["program"], f["origin"], f["library_sha256"], f["charges"])
                     for f in fams]
        led = dict(self.ledger)
        if self.dev is not None:
            led.update({"promotion_" + k: (round(v, 3) if isinstance(v, float) else v)
                        for k, v in self.dev.cost.items()})
        return {"version": O.ORGANISM_VERSION, "arm": self.arm, "spec": self.spec, "seed": self.seed,
                "config": self.cfg, "arm_world": self.W.arm_world, "order": self.order, "families": fams,
                "final_library": self.lib.to_json(), "final_library_sha256": self.lib.sha256(),
                "library_snapshots": self.lib_snapshots, "archive_final": self.archive, "ledger": led,
                "solved": sum(f["solved"] for f in fams), "decision_sha256": O.sha(decisions),
                "cpu_s": round(sum(f["cpu_s"] for f in fams), 2), "resumable": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="foundry/pilot_v2")
    ap.add_argument("--world", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--B", type=int, default=200_000)
    ap.add_argument("--R", type=int, default=100)
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--max-cpu", type=float, default=780.0)
    a = ap.parse_args()
    po = WD.presentation_order(a.root, a.world, O.order_name(a.arm, a.seed))
    order = po["order"][:a.n] if a.n else po["order"]
    W = WD.ArmWorld(a.root, po["arm_world"])
    r = ResumableOrganism(W, order, a.arm, a.seed, B=a.B, R=a.R, K=a.K).run_until(a.ckpt, a.max_cpu)
    if r.get("done"):
        r["world_id"], r["order_name"] = a.world, po["order_name"]
        r["code_sha256"] = O.e3_code_hashes()
        Path(a.ckpt).write_text(json.dumps(r, sort_keys=True))
        print("DONE", r["decision_sha256"], r["solved"])
    else:
        print("CONTINUE next", r["next"])


if __name__ == "__main__":
    main()
