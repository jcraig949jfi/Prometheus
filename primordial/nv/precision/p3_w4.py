"""P3: the precision gene in the closed loop -- held64 delta and on-policy exactness on w4, 8 run seeds.

Posted on the bus before the run (P3-precision-w4-held64):
  genomes  E9 full top-16 elites per run seed 0-7 (pm-data/E/E9-family-ranking-fused-8-seeds), w4
  eval     E7.rollout (numpy world) on E7.HELD64 with the brain forward replaced by
           primordial.nv.precision.forward at each precision; cpu, 1 thread (correctness, no lease)
  GATE     fp32 held64 == E9 held64_per_seed in 16/16 family x seed
  CONTROL  skip-odd cheat at fp32: on-policy clear-row agreement < 0.9 in 16/16
  REPORT   paired held64 delta vs fp32, on-policy clear-row agreement (E7.brain_oracle, HELD8), bytes
Scope: w4 held64 here is below the abstain floor (107.75, conductor 1789426590314-0), so rows are
engineering (exactness vs bytes), status dev, and never enter clause A.

  python -m primordial.nv.precision.p3_w4 [--seeds 0-7] [--fams linear,tt_feat] [--out ROWS]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.nv.precision import forward as pf

EXP = "P3-precision-w4-held64"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "P" / f"{EXP}.jsonl"
E9_HOT = pathlib.Path(os.environ.get("PM_DATA", "C:/Users/jcrai/lab/pm-data")) / "E" / "E9-family-ranking-fused-8-seeds"
E9_ROWS = ROOT / "primordial" / "ledger" / "rows" / "E" / "E9-family-ranking-fused-8-seeds.jsonl"
GEN_SEED = 4
ABSTAIN_FLOOR_W4 = 107.75


class PrecisionFamily:
    """Drop-in for a genomes.Family inside E7.rollout / E7.brain_oracle: forward runs one genome at a
    time at `precision` (each genome keeps its own quantization scales); the oracle stays fp64."""

    def __init__(self, fam: gm.Family, precision: str, device: str = "cpu"):
        self.fam, self.precision, self.device = fam, precision, device
        self.name, self.D, self.A = fam.name, fam.D, fam.A

    def forward(self, g, obs, gidx, cheat=False):
        out = np.empty(len(obs), np.int64)
        for q in np.unique(gidx):
            rows = np.nonzero(gidx == q)[0]
            lg = pf.precision_logits(self.name, self.fam.one(g, int(q)), obs[rows], self.precision,
                                     self.device, cheat)
            out[rows] = lg.argmax(1)
        return out

    def one(self, g, p):
        return self.fam.one(g, p)

    def ref_logits(self, g1, obs):
        return self.fam.ref_logits(g1, obs)


def parse_seeds(s):
    if "-" in s:
        lo, hi = s.split("-")
        return list(range(int(lo), int(hi) + 1))
    return [int(x) for x in s.split(",")]


def e9_held64(fam, seed):
    for line in E9_ROWS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["family"] == fam and r["gen_seed"] == GEN_SEED and r["run_seed"] == seed and r["tag"] == "full":
            return float(r["held64_per_seed"])
    raise KeyError((fam, seed))


def evaluate(fam_name, seed, precision, device="cpu", cheat=False, oracle=True):
    from primordial.qd import e7_run as E7
    g7 = E7.G7(GEN_SEED, fam_name)
    g = g7.unpack(np.load(E9_HOT / f"full_w{GEN_SEED}_{fam_name}_r{seed}_top.npy"))   # unpack with the real family
    g7.fam = PrecisionFamily(g7.fam, precision, device)
    t0 = time.perf_counter()
    fit = E7.rollout(g7, g, E7.HELD64, cheat=cheat)[0]
    wall = time.perf_counter() - t0
    out = {"held64_per_seed": float(fit.mean() / len(E7.HELD64)), "rollout_cpu_wall_s": round(wall, 3)}
    if oracle:
        bo = E7.brain_oracle(g7, g, E7.HELD8, cheat=cheat)
        out["brain_oracle"] = bo
        out["agree_clear"] = 1.0 - bo["mismatched_rows"] / max(bo["clear_rows"], 1)
    out["genome_bytes"] = pf.nbytes(fam_name, g7.D, precision) + g7.cb
    return out


def run(seeds, fams, out_path, device="cpu"):
    import torch
    from primordial.fabric.rows import RowWriter
    torch.set_num_threads(1)
    summary = {}
    with RowWriter(out_path, EXP) as w:
        for fam in fams:
            per = {p: {} for p in pf.PRECISIONS}
            gate, control = [], []
            for s in seeds:
                ref = e9_held64(fam, s)
                for p in pf.PRECISIONS:
                    r = evaluate(fam, s, p, device)
                    per[p][s] = r
                    w.write({"status": "dev", "kind": "run", "family": fam, "precision": p, "run_seed": s,
                             "substrate": pf.substrate(fam, p, device), "e9_held64_per_seed": ref, **r})
                c = evaluate(fam, s, "fp32", device, cheat=True)
                w.write({"status": "cheat", "kind": "run", "family": fam, "precision": "fp32", "run_seed": s,
                         "cheat": "skip_odd", "e9_held64_per_seed": ref, **c})
                gate.append(per["fp32"][s]["held64_per_seed"] == ref)
                control.append(c["agree_clear"] < 0.9)
            for p in pf.PRECISIONS:
                h = np.array([per[p][s]["held64_per_seed"] for s in seeds])
                d = h - np.array([per["fp32"][s]["held64_per_seed"] for s in seeds])
                ag = np.array([per[p][s]["agree_clear"] for s in seeds])
                row = {"status": "dev", "kind": "qd_cell",
                       "cell": {"representation": f"{fam}@{p}", "world": f"w{GEN_SEED}", "pressure": "train8_held64",
                                "substrate": pf.substrate(fam, p, device), "channel": "none"},
                       "mechanism": f"closed_loop_{fam}_codebook_precision_{p}",
                       "fitness": {"held64_median": float(np.median(h)),
                                   "iqr": float(np.percentile(h, 75) - np.percentile(h, 25)), "n_runs": len(seeds),
                                   "held64_by_run_seed": h.tolist()},
                       "footprint": {"genome_bytes": per[p][seeds[0]]["genome_bytes"]},
                       "exactness": {"held64_delta_vs_fp32_median": float(np.median(d)),
                                     "held64_delta_vs_fp32_min": float(d.min()), "held64_delta_vs_fp32_max": float(d.max()),
                                     "agree_clear_median": float(np.median(ag)), "agree_clear_min": float(ag.min())},
                       "floor": {"abstain_held64": ABSTAIN_FLOOR_W4, "below_floor": bool(np.median(h) < ABSTAIN_FLOOR_W4)},
                       "oracle": {"gate_fp32_eq_e9": f"{sum(gate)}/{len(gate)}",
                                  "control_cheat_caught": f"{sum(control)}/{len(control)}"},
                       "source": {"exp_id": EXP, "genomes": "E9-family-ranking-fused-8-seeds full top-16"},
                       "cohort": "P"}
                w.write(row)
                summary[f"{fam}@{p}"] = {k: row[k] for k in ("fitness", "footprint", "exactness")}
            summary[f"{fam}:gate"] = f"{sum(gate)}/{len(gate)}"
            summary[f"{fam}:control"] = f"{sum(control)}/{len(control)}"
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0-7")
    ap.add_argument("--fams", default="linear,tt_feat")
    ap.add_argument("--out", default=str(ROWS))
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args(argv)
    print(json.dumps(run(parse_seeds(a.seeds), a.fams.split(","), a.out, a.device), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
