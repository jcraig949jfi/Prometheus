"""Phase 0 detector calibration on Campaign 4/5 lineages (BASELINE_ADMITTED stage).

    python -m archaeon.campaign6.observatory.calibrate [--procs 12] [--out archaeon/campaign6/observatory/CALIBRATION_v0.1.json]

Calibration set (all v0 profile, OLD evaluator, parent environment, 16 train episodes, rng 0):
  library    the 57 C4 starting parents (their fingerprints are the behaviour library)
  children   C5-05 attempt of record, grammar-B arm: 4,878 single-edit children + 57 identity + 57
             randomize-all controls, regenerated from the census recipe (digest-checked), each with
             its C4 label under OLD (D2..D7) and its structural distance to the parent
  walks      C5-01 walkers at depths 16/32/48/64 with rewards on the five environments (detector 3)
Threshold rule (DETECTORS_v0.1.md, fixed before this ran): a threshold is the smallest value at
which the NEGATIVE controls fire at <= 1% ; every POSITIVE control must fire at that value or the
detector is reported NOT ADMITTABLE on this set. Nothing here chooses a threshold by looking at
a natural anomaly; there are none in the set.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[3]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                    # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from archaeon.wse.evolve import evaluate                                     # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED as C5_SEED           # noqa: E402
from archaeon.campaign5.repb import gen_b, grammar_b                         # noqa: E402
from archaeon.campaign6.observatory.fingerprint import rows_v0, spread_from, fp_distance, struct_distance   # noqa: E402
from archaeon.campaign6.observatory import detectors as D                    # noqa: E402

HERE = Path(__file__).resolve().parent
BAND = C1.BAND


def _digest(m: dict) -> str:
    return hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def latest_c505() -> Path:
    return sorted(d for d in (C5 / "C5-05" / "attempts").iterdir() if (d / "children.json.gz").exists())[-1]


def canonical_parents() -> Dict[str, dict]:
    return {p["organism_id"]: {**p, "parent": gen_b.canonicalize(p["parent"])} for p in C1.parents_from_population()}


def regen_child(row: dict, pm: dict) -> dict:
    org, grammar, op, r = row["parent_id"], row["grammar"], row["operator"], row["draw"]
    if op == "control_identity":
        return json.loads(json.dumps(pm))
    if op == "control_randomize_all":
        rng = SplitMix64(seed_from("c5.05.control", C5_SEED, org, grammar)); child = json.loads(json.dumps(pm))
        g = []
        for _ in range(len(child["genome"]) // 4):
            g.extend(gen_b.valid_instr(rng, child["n_regs"]))
        child["genome"] = g; return child
    rng = SplitMix64(seed_from("c5.05.edit", C5_SEED, org, grammar, op, r))
    child, _ = (grammar_b.mutate_b if grammar == "B" else GR.mutate)(pm, rng, mate=None, name=op)
    assert _digest(child) == row["child_digest"], "regenerated child digest mismatch"
    return child


def fp_job(job: dict) -> dict:
    """One organism on one environment -> (t0, ext) + reward."""
    m, env, oid, pid = job["manifest"], job["env"], job["organism_id"], job["parent_id"]
    eps = C1.episodes(env, 16)
    ev = evaluate(m, eps, rng_seed=0); a = C1.answers(m, eps)
    t0, ext = rows_v0(m, oid, pid, job.get("eval", 0), job.get("lt", 0), ev, a, world_features=[env], asks_per_episode=[e.n_asks() for e in eps])
    return {"key": job["key"], "pair": (t0, ext), "reward": ev["reward_per_ask"], "organism_id": oid}


def percentile(xs: List[float], q: float) -> float:
    if not xs:
        return float("nan")
    xs = sorted(xs); i = min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))
    return xs[i]


def choose_threshold(neg: List[float], pos: List[float]) -> dict:
    """Smallest threshold with negatives firing <= 1%; then the positives' fire rate at it."""
    if not neg:
        return {"threshold": None, "neg_n": 0, "pos_n": len(pos), "admittable": False, "reason": "no negatives"}
    thr = percentile(neg, 0.99)
    neg_fire = sum(1 for x in neg if x > thr) / len(neg)
    pos_fire = (sum(1 for x in pos if x > thr) / len(pos)) if pos else None
    return {"threshold": thr, "neg_n": len(neg), "neg_fire": round(neg_fire, 4), "pos_n": len(pos), "pos_fire": None if pos_fire is None else round(pos_fire, 4),
            "pos_min": min(pos) if pos else None, "admittable": bool(pos) and pos_fire == 1.0, "reason": "" if (pos and pos_fire == 1.0) else "a positive control does not fire at the 1% threshold"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--out", default=str(HERE / "CALIBRATION_v0.1.json"))
    a = ap.parse_args(argv)
    t0 = time.time()
    att = latest_c505()
    with gzip.open(att / "children.json.gz", "rt", encoding="utf-8") as f:
        rows = json.load(f)
    rows = [r for r in rows if r["grammar"] == "B" and (r["operator"] in C1.OPERATORS and r["applied"] or r["operator"].startswith("control_"))]
    cps = canonical_parents()
    jobs = []
    for pid, p in cps.items():
        jobs.append({"key": ("P", pid), "manifest": p["parent"], "env": C1.PARENT_ENV[p["stratum"]], "organism_id": pid, "parent_id": None})
    child_meta = {}
    for r in rows:
        pm = cps[r["parent_id"]]["parent"]; child = regen_child(r, pm)
        key = ("C", r["parent_id"], r["operator"], r["draw"])
        child_meta[key] = {"manifest": child, "row": r, "struct": struct_distance(child, pm)}
        jobs.append({"key": key, "manifest": child, "env": r["parent_env"], "organism_id": _digest(child)[:24], "parent_id": r["parent_id"][:24]})
    with ProcessPoolExecutor(max_workers=a.procs) as ex:
        results = list(ex.map(fp_job, jobs, chunksize=32))
    by = {tuple(x["key"]) if isinstance(x["key"], list) else x["key"]: x for x in results}
    lib_pairs = [by[("P", pid)]["pair"] for pid in cps]
    spread = spread_from(lib_pairs + [by[k]["pair"] for k in child_meta])
    subjects_P = {pid: D.Subject(pid, cps[pid]["parent"], by[("P", pid)]["pair"]) for pid in cps}
    # ---- detectors 1, 2, 4 scores on every child (thresholds None -> we read scores through a permissive context)
    ctx_scores = D.Context({"behavioral_novelty": 0.0, "lineage_discontinuity": 0.0, "structural_reuse": 2, "lineage_discontinuity.struct_max": 0.25}, spread, library=lib_pairs)
    scored = []
    for key, cm in child_meta.items():
        r = cm["row"]; pid = r["parent_id"]
        s = D.Subject(by[key]["organism_id"], cm["manifest"], by[key]["pair"], parent=subjects_P[pid], generation=1)
        v1 = D.behavioral_novelty(s, ctx_scores); v2 = D.lineage_discontinuity(s, ctx_scores); v4 = D.structural_reuse(s, ctx_scores)
        scored.append({"key": key, "op": r["operator"], "D": r["by"]["OLD"]["D"], "struct": cm["struct"], "degenerate": r["parent_degenerate"],
                       "d1": v1["score"], "d2": v2["score"], "d2_outcome": v2["outcome"], "d4": v4["score"], "d4_outcome": v4["outcome"], "reward": by[key]["reward"]})
    # round 2 (D6-009): behavioural labels from the C4 answer-vector DISPLACEMENT under OLD, not the reward-based D label
    for x in scored:
        x["disp"] = child_meta[x["key"]]["row"]["by"]["OLD"].get("displacement", 0.0)
    ident = [x for x in scored if x["op"] == "control_identity"]
    for x in scored:
        x["alive"] = child_meta[x["key"]]["row"]["by"]["OLD"].get("answered_share", 0.0) > 0 and child_meta[x["key"]]["row"]["by"]["OLD"]["D"] != "D2"
    still = [x for x in scored if x["op"] in C1.OPERATORS and x["disp"] == 0.0 and not x["degenerate"]]
    # round 3: a positive for NOVELTY is a child that moved AND is alive (a child that collapsed to silence matches the dead parents in the library
    # and is, correctly, not novel); lineage_discontinuity keeps all moved children (dead or alive, the jump is the event)
    moved = [x for x in scored if x["op"] in C1.OPERATORS and x["disp"] >= 0.5 and not x["degenerate"]]
    moved_alive = [x for x in moved if x["alive"]]
    still_small = [x for x in still if x["struct"] <= 0.25]
    moved_small = [x for x in moved if x["struct"] <= 0.25]
    cal = {}
    cal["behavioral_novelty"] = {"negatives": "identity + children with displacement 0 (non-degenerate parents)", "positives": "ALIVE children with displacement >= .5 (round 3)",
                                 **choose_threshold([x["d1"] for x in ident + still if x["d1"] is not None], [x["d1"] for x in moved_alive if x["d1"] is not None]),
                                 "identity_scores_all_zero": all((x["d1"] or 0.0) == 0.0 for x in ident)}
    thr1 = cal["behavioral_novelty"]["threshold"]
    cal["behavioral_novelty"]["misses"] = [{"op": x["op"], "displacement_vs_parent": x["disp"], "nearest_distance": x["d1"], "struct": x["struct"],
                                            "parent": x["key"][1][:12], "draw": x["key"][3]} for x in moved_alive if x["d1"] is not None and x["d1"] <= thr1]
    thr1 = cal["behavioral_novelty"]["threshold"]
    cal["behavioral_novelty"]["misses"] = [{"op": x["op"], "displacement_vs_parent": x["disp"], "nearest_distance": x["d1"], "struct": x["struct"],
                                            "parent": x["key"][1][:12], "draw": x["key"][3]} for x in moved_alive if x["d1"] is not None and x["d1"] <= thr1]
    cal["lineage_discontinuity"] = {"negatives": "identity + displacement-0 children with struct <= .25", "positives": "displacement >= .5 children with struct <= .25",
                                    **choose_threshold([x["d2"] for x in ident + still_small if x["d2"] is not None], [x["d2"] for x in moved_small if x["d2"] is not None])}
    d4_rates = {"parents_fire": sum(1 for pid in cps if D.structural_reuse(subjects_P[pid], ctx_scores)["outcome"] == "FIRE") / len(cps),
                "children_fire": sum(1 for x in scored if x["d4_outcome"] == "FIRE") / max(1, len(scored)),
                "children_unable": sum(1 for x in scored if x["d4_outcome"] == "UNABLE") / max(1, len(scored))}
    cal["structural_reuse"] = {"threshold": 2, "note": "count threshold fixed by definition; base rates reported, no positive control exists on v0 (the profile has no components)", **d4_rates,
                               "admittable": False, "reason": "no positive control on the v0 profile; C6_GEOMETRY stage (graph profile) needed"}
    # ---- detector 3 from the C5-01 walks
    walks = json.load(gzip.open(sorted(d for d in (C5 / "C5-01" / "attempts").iterdir() if (d / "walks.json.gz").exists())[-1] / "walks.json.gz", "rt"))
    pos3 = neg3 = fire_pos = fire_neg = 0
    for w in walks:
        if w["parent_degenerate"]:
            continue
        env = w["parent_env"]; prew = w["parent_rewards"]
        for depth, ex in w["exposure"].items():
            if depth == "0":
                continue
            for wk in ex["walkers"]:
                rw = wk["rewards"]; gains = {e: rw[e] - prew[e] for e in rw if e != env}
                eligible = [e for e, g in gains.items() if g >= BAND and rw[e] >= C1.FLOOR]      # round 2: the floor is part of the definition
                home_moved = abs(rw[env] - prew[env]) > BAND
                fire = bool(eligible) and not home_moved
                if wk["exaptive_on"]:
                    pos3 += 1; fire_pos += fire
                else:
                    neg3 += 1; fire_neg += fire
    cal["unexpected_transfer"] = {"threshold": BAND, "positives": "C5-01 walkers exaptive on another environment (C4 rule)", "negatives": "all other archived walkers",
                                  "pos_n": pos3, "pos_fire": round(fire_pos / max(1, pos3), 4), "neg_n": neg3, "neg_fire": round(fire_neg / max(1, neg3), 4),
                                  "admittable": pos3 > 0 and fire_pos == pos3 and fire_neg / max(1, neg3) <= 0.01,
                                  "reason": "" if (pos3 > 0 and fire_pos == pos3 and fire_neg / max(1, neg3) <= 0.01) else "negative fire rate above 1% (gain >= band below the floor) or a positive missed"}
    for name in ("environmental_modification", "niche_divergence", "regime_persistence", "unexplained_gain", "unexpected_causal_dependence"):
        cal[name] = {"threshold": None, "admittable": False, "reason": "UNABLE on the whole v0 calibration set (no persistent world state / one resource / no regime change / no replay D / no ablation set); C6_GEOMETRY stage"}
    # ---- 10 and 11 over the full verdict vectors with the chosen thresholds
    thr = {"behavioral_novelty": cal["behavioral_novelty"]["threshold"], "lineage_discontinuity": cal["lineage_discontinuity"]["threshold"], "structural_reuse": 2,
           "lineage_discontinuity.struct_max": 0.25}
    ctx = D.Context(thr, spread, library=lib_pairs)
    vec_counts = {"disagreement_fire": 0, "classifier_fire": 0, "n": 0}
    for key, cm in list(child_meta.items()):
        r = cm["row"]
        s = D.Subject(by[key]["organism_id"], cm["manifest"], by[key]["pair"], parent=subjects_P[r["parent_id"]], generation=1)
        vs = D.run_all(s, ctx)
        vec_counts["n"] += 1
        vec_counts["disagreement_fire"] += vs[-2]["outcome"] == "FIRE"; vec_counts["classifier_fire"] += vs[-1]["outcome"] == "FIRE"
    cal["detector_disagreement"] = {"threshold": 1, "rate_on_children": round(vec_counts["disagreement_fire"] / max(1, vec_counts["n"]), 4), "admittable": True,
                                    "reason": "definitional over the verdict vector; rate reported"}
    cal["classifier_failure"] = {"threshold": 3, "rate_on_children": round(vec_counts["classifier_fire"] / max(1, vec_counts["n"]), 4), "admittable": True,
                                 "reason": "definitional; on v0 it fires whenever >= 3 detectors are UNABLE and one fires -- the blind-spot count of the old geometry, reported"}
    code_digest = {f: hashlib.sha256((HERE / f).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for f in ("detectors.py", "fingerprint.py", "calibrate.py")}
    out = {"schema": "archaeon.c6.calibration.v1", "stage": "BASELINE_ADMITTED_CANDIDATE", "c5_05_attempt": att.name, "n_children": len(child_meta), "n_parents": len(cps),
           "spread": spread, "weights": "fingerprint.DEFAULT_WEIGHTS", "calibration": cal, "code_sha256": code_digest, "wall_s": round(time.time() - t0, 1),
           "admittable_now": [k for k, v in cal.items() if v.get("admittable")],
           "not_admittable_on_v0": [k for k, v in cal.items() if not v.get("admittable")]}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("negatives", "positives")} for k, v in cal.items()}, indent=1, default=str))
    print("admittable_now", out["admittable_now"], "wall", out["wall_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
