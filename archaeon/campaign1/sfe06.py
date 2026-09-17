"""SFE-06 -- H5 ENCODING AND ACCESS TO USEFUL VARIATION through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe06 [--seeds 1 2 3] [--parents 8 --steps 40 --lam 4] [--dry-run]

Evaluator and phenotype scope FIXED: the 256 elementary CA rules scored by Herakles's
block-output criterion (Capcarrere-Sipper-Tomassini) on 64 seeded Bernoulli ICs of a 21-cell
ring at horizon 11 (chance 0.5, range [0,1]). One score table per seed, shared by every
decoder, so decoders can differ only in ACCESS. Genotype: 12 bits; three decoders from
archaeon.producer.h5_decoders, each total with multiplicity exactly 16 per rule:
direct (rule = low 8 bits), balanced (seeded genome permutation), scrambled (seeded rule
permutation over direct). Search: (1+lambda) hill climbing with single-bit flips from
independent parents, matched budget (parents x steps x lambda evaluations) per decoder.
Measures: best score reached, evaluations to first >= 0.9, distinct rules visited,
neighbourhood accessible variation (h5_decoders.accessible_variation, collapsed to the
224 behavioural classes at 7-ring/8-step). Engine: decoder tables (sha256 identity) and the
score table as artifacts; experiment + observation per decoder x seed.
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

from herakles.eca import core as E                             # noqa: E402
from archaeon.producer import h5_decoders as H                 # noqa: E402
from archaeon import workspace as _ws                          # noqa: E402
from archaeon.campaign1.sfe01 import CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-06"
N_CELLS, N_ICS, STEPS = 21, 64, 11
THRESHOLD = 0.9


def score_table(seed: int) -> List[float]:
    ics = E.make_ics(N_ICS, N_CELLS, seed, "bernoulli")
    return [E.block_output_score(r, ics, STEPS)["score"] for r in range(256)]


def hill_climb(dec, table: List[float], parents: List[int], steps: int, lam: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    evals = 0
    best_overall = -1.0
    first_hit = None
    visited = set()
    trajs = []
    for g0 in parents:
        g = g0
        s = table[dec(g)]; evals += 1; visited.add(dec(g))
        traj = [s]
        for _ in range(steps):
            cands = [g ^ (1 << int(b)) for b in rng.choice(H.GENOME_BITS, size=lam, replace=False)]
            scored = [(table[dec(c)], c) for c in cands]
            evals += lam
            for sc, c in scored:
                visited.add(dec(c))
                if sc >= THRESHOLD and first_hit is None:
                    first_hit = evals
            sc, c = max(scored, key=lambda z: z[0])
            if sc >= s:
                g, s = c, sc
            traj.append(s)
            best_overall = max(best_overall, s)
        trajs.append(traj)
    return {"best": best_overall, "evals": evals, "first_hit_evals": first_hit, "distinct_rules_visited": len(visited),
            "mean_final": float(np.mean([t[-1] for t in trajs])), "trajectories": trajs}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--parents", type=int, default=8)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--lam", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-06")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-06", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "engine_path": not a.dry_run,
                     "timings": {}, "worlds": {}, "artifacts": {}, "errors": [],
                     "config": {"n_cells": N_CELLS, "n_ics": N_ICS, "steps": STEPS, "threshold": THRESHOLD, "parents": a.parents,
                                "climb_steps": a.steps, "lambda": a.lam, "budget_per_decoder": a.parents * (1 + a.steps * a.lam)}}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe06")
        w = c.create_world(sid, "cmp1-sfe06-h5", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED); c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["h5"] = wid; receipt["session_id"] = sid
        receipt["hypothesis"] = c.hypothesis(wid, "With the evaluator and the 256-rule phenotype catalogue fixed (multiplicity 16 per rule under every decoder), "
                                                  "the genotype->phenotype decoder changes search success and accessible variation: balanced != direct != scrambled.")
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)
    decoders = {"direct": H.direct, "balanced": H.make_balanced(CAMPAIGN_SEED), "scrambled": H.make_scrambled(H.direct, CAMPAIGN_SEED)}
    checks = {name: {k: v for k, v in H.check_exact(d).items() if k != "table"} for name, d in decoders.items()}
    tables = {name: H.decoder_table(d) for name, d in decoders.items()}
    receipt["decoders"] = {name: {"check": checks[name], "table_sha256": H.table_sha256(tables[name])} for name in decoders}
    classes = E.equivalence_classes(7, 8)
    equiv = {}
    for cid, (digest, rules) in enumerate(classes.items()):
        for r in rules:
            equiv[r] = cid
    if c is not None:
        for name in decoders:
            b = bytes(int(v) for v in tables[name])
            receipt["artifacts"]["decoder_" + name] = c.artifact(wid, "cmp1.h5.decoder_table.v0", b, {"info_kind": "artifact", "decoder": name},
                                                                expected_blob_hash=sha(b))["artifact_id"]
    rows = []
    for seed in a.seeds:
        t0 = time.time()
        table = score_table(CAMPAIGN_SEED * 10 + seed)
        best_rule = int(np.argmax(table))
        if c is not None:
            tb = json.dumps({"seed": seed, "scores": table, "criterion": "block_output", "n_cells": N_CELLS, "n_ics": N_ICS, "steps": STEPS}).encode()
            receipt["artifacts"]["score_table_s%d" % seed] = c.artifact(wid, "cmp1.h5.score_table.v0", tb, {"info_kind": "observation", "seed": seed}, expected_blob_hash=sha(tb))["artifact_id"]
        parents = H.independent_parents(CAMPAIGN_SEED + seed, a.parents)
        probe_parents = H.independent_parents(CAMPAIGN_SEED + 100 + seed, 256)
        for name, dec in decoders.items():
            hc = hill_climb(dec, table, parents, a.steps, a.lam, seed=CAMPAIGN_SEED + seed)
            av = H.accessible_variation(dec, probe_parents, equiv)
            avr = H.accessible_variation(dec, probe_parents, None)
            row = {"seed": seed, "decoder": name, "best": hc["best"], "first_hit_evals": hc["first_hit_evals"], "evals": hc["evals"],
                   "distinct_rules_visited": hc["distinct_rules_visited"], "mean_final": hc["mean_final"],
                   "accessible_classes": av["mean_distinct_neighbour_phenotypes"], "accessible_rules": avr["mean_distinct_neighbour_phenotypes"],
                   "table_max": max(table), "table_best_rule": best_rule, "table_share_ge_threshold": sum(1 for s in table if s >= THRESHOLD) / 256.0,
                   "trajectories": hc["trajectories"]}
            if c is not None:
                try:
                    exp = c.experiment(wid, {"experiment": "SFE-06", "decoder": name, "seed": seed, "config": receipt["config"],
                                             "decoder_table_sha256": receipt["decoders"][name]["table_sha256"]})
                    obs = c.observation(wid, exp["exp_id"], {k: v for k, v in row.items() if k != "trajectories"},
                                        "SURVIVED" if hc["best"] >= THRESHOLD else "FALSIFIED")
                    row["engine"] = {"exp_id": exp["exp_id"], "obs_id": obs}
                except Exception as e:                               # noqa: BLE001
                    receipt["errors"].append({"step": "record", "seed": seed, "decoder": name, "error": repr(e)})
            rows.append(row)
        print(json.dumps({"seed": seed, "table_max": round(max(table), 3), "best_rule": best_rule,
                          "rows": {r["decoder"]: (round(r["best"], 3), r["first_hit_evals"], r["distinct_rules_visited"], round(r["accessible_classes"], 2)) for r in rows if r["seed"] == seed},
                          "wall_s": round(time.time() - t0, 1)}), flush=True)
    if c is not None:
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"h5": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"h5": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    summ = {}
    for name in decoders:
        rs = [r for r in rows if r["decoder"] == name]
        summ[name] = {"best_mean": sum(r["best"] for r in rs) / len(rs), "hits": sum(1 for r in rs if r["first_hit_evals"] is not None),
                      "first_hit_evals": [r["first_hit_evals"] for r in rs], "distinct_rules_visited": [r["distinct_rules_visited"] for r in rs],
                      "accessible_classes": round(sum(r["accessible_classes"] for r in rs) / len(rs), 3),
                      "accessible_rules": round(sum(r["accessible_rules"] for r in rs) / len(rs), 3)}
    receipt["summary"] = summ
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"summary": summ, "timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
