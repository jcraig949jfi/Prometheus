"""C6b: audit lane B's B6b fused rollout for the linear and tt_feat families (hypothesis: bus 1789394767458-0).

Reference = lane E's own E7 rollout (primordial/qd/e7_run.rollout, numpy family forward).
Subject   = lane B's B6b fused rollout with the family selected (primordial/soup/b6).
Both imported read-only; seeds are passed explicitly to both.

Conditions per family (linear, tt_feat) x world (1, 3, 4), compared per genome on fitness AND cell:
  a_elites_train     E7's saved top-16 elites (run seed r0) on E6 TRAIN
  b_elites_heldout   the same elites on E6 HELD64
  c_p1 / c_p7        the first 1 / 7 elites on TRAIN
  c_mutated          128 G7.init genomes after 200 G7.mutate steps, TRAIN
  d_ties             output params zeroed (every logit tied)                  [report-only]
  d_overflow         weight params x 1e20 (float32 overflow)                   [report-only]
Mismatch tracing (posted rule): for every genome whose fitness or cell differs, find each env's first tick where
the two paths' actions differ; the row passes as a NEAR-TIE iff its top-2 margin under fam.ref_logits is
< 1e-4 relative. A mismatch whose first divergence is a CLEAR row in (a)(b)(c) refutes B6b.
Brain oracle on (b): B6b recorded actions == argmax fam.ref_logits on clear rows, 0 mismatches.
Cheat: B6b with brain stride 2 vs honest E7 on (a): >=14/16 elites mismatch per world per family.

usage: python -m primordial.brain.c6b_audit_b6b [--worlds 1,3,4] [--families linear,tt_feat]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import pathlib
import subprocess
import time

import numpy as np
import psutil

EXP_ID = "C6b-audit-b6b-linear-tt-feat"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
ELITES = pathlib.Path("C:/Users/jcrai/lab/pm-data/E/E7-c4-families-heldout")
ROOT = pathlib.Path(__file__).resolve().parents[1]
NEAR_TIE_REL = 1e-4
CORE = ("a_elites_train", "b_elites_heldout", "c_p1", "c_p7", "c_mutated")


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


# ------------------------------------------------------------------ subject adapter (the ONLY B6b-specific code)

def b6b_run(g7, g, seeds, stride: int = 1, record=None):
    """Run lane B's B6b fused rollout for g7.fam on genome batch g = (params_tuple, codebook).

    Returns (fitness int32 [P], cells uint32 [P], done_tick [P*k], logs dict with 'idx' [T, nr, S] and
    'obs' [T, nr, S, D], rec env indices). API as posted by B for B6b (2add9828b, bus 1789394981128-0):
    FusedRollout(g7.spec, P, seeds, family=...).run((params, codebook), brain_stride=, record=).
    With record = arange(P*k), log slot j is env j.
    """
    from primordial.soup.b6.fused import FusedRollout      # lane B, read-only
    fr = FusedRollout(g7.spec, len(g[1]), np.asarray(seeds, np.int64), family=g7.fam.name)
    return fr.run(g, brain_stride=stride, record=record)


# ------------------------------------------------------------------ reference side

def ref_margin_rel(fam, params1, obs_row):
    ref = fam.ref_logits(params1, obs_row[None, :])[0]
    top = np.sort(ref)
    return (top[-1] - top[-2]) / max(abs(top[-1]), 1e-30), int(ref.argmax())


def sub(g, n):
    p, C = g
    return tuple(x[:n].copy() for x in p), C[:n].copy()


def zero_outputs(fam_name, g):
    p, C = g
    p = tuple(x.copy() for x in p)
    if fam_name == "linear":
        p[0][:] = 0.0                                   # W
        p[1][:] = 0.0                                   # b
    else:
        p[2][:] = 0.0                                   # Wo
    return p, C.copy()


def overflow(fam_name, g):
    p, C = g
    p = [x.copy() for x in p]
    j = 0 if fam_name == "linear" else 1                # W for linear, G for tt_feat
    with np.errstate(over="ignore"):
        p[j] = (p[j].astype(np.float64) * 1e20).astype(np.float32)
    return tuple(p), C.copy()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,3,4")
    ap.add_argument("--families", default="linear,tt_feat")
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    import primordial.qd.e7_run as E7                   # lane E, read-only

    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    rows = []
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(json.dumps(row)[:400], flush=True)

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "near_tie_rel": NEAR_TIE_REL,
              "train": [int(E7.TRAIN[0]), int(E7.TRAIN[-1]), len(E7.TRAIN)],
              "held64": [int(E7.HELD64[0]), int(E7.HELD64[-1]), len(E7.HELD64)]})

        def compare(g7, g, seeds, cond, stride=1, record_all_mismatch=True):
            psutil.cpu_percent(None)
            fit_e, cells_e, _, L = E7.rollout(g7, g, seeds, log=True)
            fit_b, cells_b, done_tick, logs, rec = b6b_run(g7, g, seeds, stride=stride,
                                                          record=np.arange(len(g[1]) * len(seeds)))
            host = psutil.cpu_percent(None)
            exact = (fit_e == fit_b) & (cells_e == cells_b)
            k = len(seeds)
            near, clear_div = 0, 0
            if stride == 1:
                for p in np.flatnonzero(~exact):
                    params1 = tuple(x[p] for x in g[0])
                    for e in range(p * k, (p + 1) * k):
                        diff = np.argwhere(L["idx"][:, e] != logs["idx"][:, e])
                        if len(diff) == 0:
                            continue
                        t, s = diff[0]
                        rel, _ = ref_margin_rel(g7.fam, params1, L["obs"][t, e, s])
                        if rel < NEAR_TIE_REL:
                            near += 1
                        else:
                            clear_div += 1
                        break                            # first divergent env of this genome decides it
            return {"condition": cond, "P": len(g[1]), "k": k, "stride": stride, "genomes_exact": int(exact.sum()),
                    "mismatch_first_divergence_near_tie": near, "mismatch_first_divergence_clear": clear_div,
                    "host_cpu_pct": host}, (logs, rec, done_tick)

        for fam_name in a.families.split(","):
            for gs in [int(x) for x in a.worlds.split(",")]:
                g7 = E7.G7(gs, fam_name)
                elites = g7.unpack(np.load(ELITES / f"full_w{gs}_{fam_name}_r0_top.npy"))
                base = {"kind": "cell", "family": fam_name, "gen_seed": gs}

                r, _ = compare(g7, elites, E7.TRAIN, "a_elites_train")
                emit({**base, **r})

                r, (logs, rec, done_tick) = compare(g7, elites, E7.HELD64, "b_elites_heldout")
                k = len(E7.HELD64)
                clear_rows = mism = 0
                for p in range(len(elites[1])):
                    params1 = tuple(x[p] for x in elites[0])
                    e = p * k                                 # env 0 of each elite
                    t_end = int(done_tick[e])
                    for s in range(g7.S):
                        obs = logs["obs"][:t_end, e, s]
                        if len(obs) == 0:
                            continue
                        ref = g7.fam.ref_logits(params1, obs)
                        top = np.sort(ref, 1)
                        clear = (top[:, -1] - top[:, -2]) > NEAR_TIE_REL * np.maximum(np.abs(top[:, -1]), 1e-30)
                        clear_rows += int(clear.sum())
                        mism += int(((ref.argmax(1) != logs["idx"][:t_end, e, s]) & clear).sum())
                emit({**base, **r, "brain_oracle_clear_rows": clear_rows, "brain_oracle_mismatches": mism})

                for cond, n in (("c_p1", 1), ("c_p7", 7)):
                    r, _ = compare(g7, sub(elites, n), E7.TRAIN, cond)
                    emit({**base, **r})
                rng = np.random.Generator(np.random.PCG64([616, gs, len(fam_name)]))
                g = g7.init(rng, 128)
                for _ in range(200):
                    g = g7.mutate(rng, g)
                r, _ = compare(g7, g, E7.TRAIN, "c_mutated")
                emit({**base, **r})

                r, _ = compare(g7, zero_outputs(fam_name, elites), E7.TRAIN, "d_ties")
                emit({**base, **r})
                with np.errstate(all="ignore"):
                    r, _ = compare(g7, overflow(fam_name, elites), E7.TRAIN, "d_overflow")
                emit({**base, **r})

                r, _ = compare(g7, elites, E7.TRAIN, "cheat_stride2", stride=2)
                emit({**base, **r})

        cells = [r for r in rows if r["kind"] == "cell"]
        core = [c for c in cells if c["condition"] in CORE]
        refuted = [c for c in core if c["mismatch_first_divergence_clear"] > 0]
        core_ok = not refuted and all(c["genomes_exact"] + c["mismatch_first_divergence_near_tie"] == c["P"]
                                      for c in core)
        oracle_ok = all(c["brain_oracle_mismatches"] == 0 and c["brain_oracle_clear_rows"] > 0
                        for c in cells if c["condition"] == "b_elites_heldout")
        cheat = [c for c in cells if c["condition"] == "cheat_stride2"]
        cheat_ok = bool(cheat) and all(c["P"] - c["genomes_exact"] >= 14 for c in cheat)
        status = "KILL" if refuted else ("PASS" if core_ok and oracle_ok and cheat_ok else "INDETERMINATE")
        emit({"kind": "summary", "core_cells": len(core), "core_ok": core_ok, "oracle_ok": oracle_ok,
              "cheat_ok": cheat_ok, "refuting_cells": [(c["family"], c["gen_seed"], c["condition"]) for c in refuted],
              "near_tie_mismatches": sum(c["mismatch_first_divergence_near_tie"] for c in core),
              "status_by_posted_rule": status})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
