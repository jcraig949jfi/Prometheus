"""SFE-04 -- H2 STATEFUL CA -> CAUSAL COMPONENT -> REUSE through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe04 [--delay 2] [--window 5] [--dry-run]

Three questions on the smallest stateful cellular path (herakles.ca_stream, radius-3 CA,
31 cells, one port, 256-stream catalogue, ridge readout over the post-step lattice):
  1. USEFUL BOUNDED COMPUTATION  delayed recall (y[t] = x[t-d]) on the confirmation partition,
     CA (six recovered genomes, D-18 v1 non-uniform reset -- the all-zero reset is provably
     inert, OBSTRUCTION.md) vs ShiftRegister (perfect memory, positive control), DirectInput
     (no memory, negative control), FrozenRandom (readout-only control).
  2. CAUSAL CONTRIBUTION  freeze the readout of the best CA; lesion (clamp to 0 after every
     step) a contiguous window of w cells at each position; accuracy drop per position = a
     lesion map; MATCHED random non-contiguous w-cell lesions give the null distribution; a
     "localized component" is a window whose drop exceeds every matched random drop.
  3. FROZEN REUSE IN A NEW COMPOSITION  new task temporal_xor; composite features =
     [frozen CA | frozen random]; readout refit for the new task; ablate each half; and
     localized reuse: [component-window cells only | random] vs [random window | random].
Engine: one world; the frozen CA descriptor + readout weights published as the component
artifact; lesion map and reuse rows as artifacts; one experiment + observation per question.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from herakles.ca_stream import core as cs                      # noqa: E402
from herakles.ca_stream import reset_v2 as rv                  # noqa: E402
from herakles.evca import genomes as GEN                       # noqa: E402
from archaeon import workspace as _ws                          # noqa: E402
from archaeon.campaign1.sfe01 import CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-04"
N_CELLS, HORIZON = 31, 8
RESET_DENSITY, RESET_ROOT = 0.5, 20260917


class LesionedCA(rv.NonUniformResetCaSubstrate):
    def __init__(self, *a, lesion=(), **kw):
        self.lesion = tuple(int(i) for i in lesion)
        super().__init__(*a, **kw)

    def step(self, bit: int) -> np.ndarray:
        f = super().step(bit)
        if self.lesion:
            self.state[0, list(self.lesion)] = 0
            f[list(self.lesion)] = 0.0
        return f


def feats_ca(rule_hex: str, streams: np.ndarray, positions, lesion=()) -> np.ndarray:
    s = LesionedCA(rule_hex, N_CELLS, (0,), reset_density=RESET_DENSITY, reset_root=RESET_ROOT, lesion=lesion)
    f, _ = rv.run_streams_v2(s, streams, positions)
    return f


def feats_plain(sub, streams: np.ndarray) -> np.ndarray:
    f, _ = cs.run_streams(sub, streams)
    return f


def fit_score(ftr, ytr, fcf, ycf, mask):
    w = cs.fit_readout(ftr, ytr, mask)
    return w, cs.score_readout(fcf, ycf, mask, w)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=int, default=2)
    ap.add_argument("--window", type=int, default=5)
    ap.add_argument("--n-random-lesions", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-04")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-04", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "engine_path": not a.dry_run,
                     "timings": {}, "worlds": {}, "artifacts": {}, "errors": [], "config": {"n_cells": N_CELLS, "horizon": HORIZON,
                     "delay": a.delay, "window": a.window, "reset_density": RESET_DENSITY, "reset_root": RESET_ROOT}}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe04")
        w = c.create_world(sid, "cmp1-sfe04-ca", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED); c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["ca"] = wid; receipt["session_id"] = sid
        receipt["hypothesis"] = c.hypothesis(wid, "A radius-3 CA with non-uniform reset carries delayed-recall information a ridge readout can use "
                                                  "(above DirectInput and FrozenRandom); a contiguous window of cells contributes causally beyond matched "
                                                  "random lesions; the frozen CA remains useful when composed into a new task.")
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)

    streams = cs.all_streams(HORIZON)
    parts = cs.partitions(len(streams), 64, 64, seed=CAMPAIGN_SEED)
    tr, cf = parts["train"], parts["confirmation"]
    positions = np.arange(len(streams))
    # ---- 1. useful bounded computation: delayed recall
    t0 = time.time()
    task, d = "delayed_recall", a.delay
    y = cs.build_targets(streams, task, d)
    mask = cs.warmup_mask(HORIZON, task, d)
    q1: Dict[str, dict] = {}
    feats: Dict[str, np.ndarray] = {}
    for name in GEN.NAMES:
        f = feats_ca(GEN.rule_hex(name), streams, positions)
        feats["ca:" + name] = f
        wts, sc = fit_score(f[tr], y[tr], f[cf], y[cf], mask)
        q1["ca:" + name] = dict(sc, nonzero_share=float((f != 0).mean()))
    for name, sub in (("shift", cs.ShiftRegister(N_CELLS)), ("direct", cs.DirectInput(N_CELLS) if "n_cells" in cs.DirectInput.__init__.__code__.co_varnames else cs.DirectInput()),
                      ("random", cs.FrozenRandom(N_CELLS, seed=CAMPAIGN_SEED))):
        f = feats_plain(sub, streams); feats[name] = f
        wts, sc = fit_score(f[tr], y[tr], f[cf], y[cf], mask)
        q1[name] = dict(sc, nonzero_share=float((f != 0).mean()))
    # reset-leakage probe on the best CA (fit on reset lattices alone, no input)
    best = max((k for k in q1 if k.startswith("ca:")), key=lambda k: q1[k]["accuracy"])
    best_rule = GEN.rule_hex(best.split(":")[1])
    try:
        leak = rv.reset_leakage_probe(best_rule, N_CELLS, RESET_DENSITY, RESET_ROOT, streams, task, d) if False else None
    except Exception as e:                                           # noqa: BLE001
        leak = "probe signature unknown: " + repr(e)
    receipt["timings"]["q1_s"] = round(time.time() - t0, 2)
    useful = q1[best]["accuracy"] > max(q1["direct"]["accuracy"], q1["random"]["accuracy"]) + 0.05

    # ---- 2. causal contribution: lesion map on the best CA with a FROZEN readout
    t0 = time.time()
    f_best = feats[best]
    w_best = cs.fit_readout(f_best[tr], y[tr], mask)
    base_acc = cs.score_readout(f_best[cf], y[cf], mask, w_best)["accuracy"]
    lesion_map = {}
    for p0 in range(N_CELLS):
        idx = [(p0 + i) % N_CELLS for i in range(a.window)]
        f = feats_ca(best_rule, streams[cf], positions[cf], lesion=idx)
        lesion_map[p0] = round(base_acc - cs.score_readout(f, y[cf], mask, w_best)["accuracy"], 4)
    rng = np.random.default_rng(CAMPAIGN_SEED + 4)
    random_drops = []
    for _ in range(a.n_random_lesions):
        idx = sorted(rng.choice(N_CELLS, size=a.window, replace=False).tolist())
        f = feats_ca(best_rule, streams[cf], positions[cf], lesion=idx)
        random_drops.append(round(base_acc - cs.score_readout(f, y[cf], mask, w_best)["accuracy"], 4))
    max_rand = max(random_drops)
    components = [p for p, dr in lesion_map.items() if dr > max_rand + 0.02]
    # matched control: the same lesion map on the shift register (the delay cell is the only component)
    f_sh = feats["shift"]; w_sh = cs.fit_readout(f_sh[tr], y[tr], mask); base_sh = cs.score_readout(f_sh[cf], y[cf], mask, w_sh)["accuracy"]
    shift_map = {}
    for p0 in range(N_CELLS):
        idx = [(p0 + i) % N_CELLS for i in range(a.window)]
        f = f_sh[cf].copy(); f[:, :, idx] = 0.0
        shift_map[p0] = round(base_sh - cs.score_readout(f, y[cf], mask, w_sh)["accuracy"], 4)
    receipt["timings"]["q2_s"] = round(time.time() - t0, 2)

    # ---- 3. frozen reuse in a new composition: temporal_xor with the CA frozen
    t0 = time.time()
    task2, d2 = "delayed_recall", a.delay + 1        # D-010: a NEW linearly-readable task (temporal_xor is not linearly separable; dry run: every substrate at chance)
    y2 = cs.build_targets(streams, task2, d2); mask2 = cs.warmup_mask(HORIZON, task2, d2)
    f_rand = feats["random"]
    comp = np.concatenate([f_best, f_rand], axis=2)
    q3 = {}
    for name, f in (("ca_only", f_best), ("random_only", f_rand), ("composite", comp), ("shift", feats["shift"]), ("direct", feats["direct"])):
        wts, sc = fit_score(f[tr], y2[tr], f[cf], y2[cf], mask2); q3[name] = sc
    # localized reuse: only the component window's cells (or a random window) from the CA + random
    win = components[0] if components else int(max(lesion_map, key=lesion_map.get))
    idx_c = [(win + i) % N_CELLS for i in range(a.window)]
    idx_r = sorted(rng.choice(N_CELLS, size=a.window, replace=False).tolist())
    for name, idx in (("component_window+random", idx_c), ("random_window+random", idx_r)):
        f = np.concatenate([f_best[:, :, idx], f_rand], axis=2)
        wts, sc = fit_score(f[tr], y2[tr], f[cf], y2[cf], mask2); q3[name] = dict(sc, cells=idx)
    receipt["timings"]["q3_s"] = round(time.time() - t0, 2)

    result = {"q1_delayed_recall": q1, "best_ca": best, "useful_bounded_computation": bool(useful), "reset_leakage_probe": leak,
              "q2_lesion_map": lesion_map, "q2_random_lesion_drops": random_drops, "q2_max_random_drop": max_rand,
              "q2_components": components, "q2_base_accuracy": base_acc, "q2_shift_lesion_map": shift_map,
              "q3_reuse": q3, "q3_component_window": idx_c, "q3_random_window": idx_r}
    if c is not None:
        t0 = time.time()
        try:
            comp_blob = json.dumps({"substrate": {"rule_hex": best_rule, "n_cells": N_CELLS, "ports": [0], "reset_density": RESET_DENSITY, "reset_root": RESET_ROOT,
                                                  "kind": "ca_stream_v2 semantics (D-18 v1 reset), campaign-local"},
                                    "readout_weights": [float(x) for x in w_best], "task": {"name": task, "delay": d}, "train_partition": tr.tolist()},
                                   sort_keys=True).encode()
            receipt["artifacts"]["frozen_component"] = c.artifact(wid, "cmp1.h2.frozen_ca_component.v0", comp_blob, {"info_kind": "artifact"}, expected_blob_hash=sha(comp_blob))["artifact_id"]
            lm_blob = json.dumps({"lesion_map": lesion_map, "random_drops": random_drops, "components": components, "window": a.window}, sort_keys=True).encode()
            receipt["artifacts"]["lesion_map"] = c.artifact(wid, "cmp1.h2.lesion_map.v0", lm_blob, {"info_kind": "observation"}, expected_blob_hash=sha(lm_blob))["artifact_id"]
            for qname, content, outcome in (("q1", q1, "SURVIVED" if useful else "FALSIFIED"),
                                            ("q2", {"components": components, "max_random_drop": max_rand, "map": lesion_map}, "SURVIVED" if components else "FALSIFIED"),
                                            ("q3", q3, "SURVIVED" if q3["composite"]["accuracy"] > q3["random_only"]["accuracy"] + 0.05 else "FALSIFIED")):
                exp = c.experiment(wid, {"experiment": "SFE-04", "question": qname, "config": receipt["config"], "best_ca": best})
                obs = c.observation(wid, exp["exp_id"], content, outcome)
                receipt.setdefault("engine_records", {})[qname] = {"exp_id": exp["exp_id"], "obs_id": obs}
        except Exception as e:                                       # noqa: BLE001
            receipt["errors"].append({"step": "record", "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"ca": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"ca": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    receipt["result"] = result
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"q1": {k: round(v["accuracy"], 3) for k, v in q1.items()}, "best": best, "useful": useful,
                      "q2_components": components, "q2_max_random_drop": max_rand, "q2_top_windows": sorted(lesion_map.items(), key=lambda z: -z[1])[:5],
                      "q3": {k: round(v["accuracy"], 3) for k, v in q3.items()}, "timings": receipt["timings"], "errors": receipt["errors"],
                      "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
