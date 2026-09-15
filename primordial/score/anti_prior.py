"""H-R5-2 / H-R6-3 / H-R7-2: the SEALED ANTI-PRIOR LEDGER, version 3 -- round-namespaced (D11).

A predictor (lane R, a separate session, never the experimenter) posts a prior per candidate cell BEFORE
assignment. Code publishes the candidate cells, so the predictor never chooses them. Priors never enter scientific
scoring.

Round 6 D11: the ledger keys were not namespaced by round, so the round 5 ledger blocked the round 6 candidate publish
(CANDIDATES_ALREADY_PUBLISHED) and A renamed keys by hand. Version 3 puts every key under the round:

    pm:prior:<round>:{sealed, commit, assign, candidates, ranks}

and every entry point takes a REQUIRED keyword round_id, so no call can reach another round's ledger by default.
candidates() refuses a redraw only within the same round. Seeds are fixed per round in SEEDS before any data
(SWARM_R6: r6 = 20260917 / 20260918; SWARM_R7: r7 = 20260919 / 20260920); a round without fixed seeds is refused.
migrate_unnamespaced(r, "r6") moves the round 6 keys (written un-namespaced by v2) with RENAMENX, never overwriting;
the round 5 archive pm:prior:r5:* is untouched.

  candidates(store, round_id=, n=48)        a seeded PCG64 draw of n distinct cells from draw_cell.axes(), ONCE per round
  seal(store, prediction, role, round_id=)  predictor-only write, once per prediction_id; sha256 commitment
  freeze_ranks(store, now, round_id=)       ONCE per round: rank by prior_p_pass desc, quantile (rank - 0.5)/n, ties by
                                            a seeded permutation (the round's candidates seed), recorded
  assign(store, exp_id, now, round_id=)     arm by PCG64([arm seed, i]) Bernoulli(0.25): calibration = top rank quartile,
                                            anti_prior = bottom; -> [{exp_id, cell}] only
  read(store, prediction_id, role, ..., round_id=)
                                            the sealed record only (R is never told arms); experimenter denied until its
                                            receipt is filed
  calibration(store, outcomes, rounds=[...]) descriptive: by arm accumulated across the rounds, per round, by rank
                                            quartile, by absolute p bucket (H-R7-3)

Sealing is API-level plus the commitment (round 5 PC D8), not cryptographic against direct Redis reads.
Store: any object with hget/hset/hgetall/hsetnx (+ exists/renamenx for the migration): redis.Redis(decode_responses=True).
"""
from __future__ import annotations

import hashlib
import json
import re
import time

import numpy as np

NAMES = ("sealed", "commit", "assign", "candidates", "ranks")
ROUND_RE = re.compile(r"r\d{1,3}")
SEEDS = {"r6": (20260917, 20260918),              # SWARM_R6 s0 (candidates, arm)
         "r7": (20260919, 20260920)}              # SWARM_R7 s0
FIELDS = ("prior_p_pass", "prior_expected_direction", "prior_expected_mechanism", "predictor_id", "prediction_ts")
N_CANDIDATES = 48
ARM_P = 0.25
TOP_Q, BOTTOM_Q = 0.25, 0.75
ARMS = ("calibration", "anti_prior")
ROLES = ("predictor", "experimenter", "conductor")
BUCKETS = (0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0)
_FROM_FILE = object()


class PriorLedgerError(PermissionError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


def keys(round_id: str) -> dict:
    if not isinstance(round_id, str) or not ROUND_RE.fullmatch(round_id):
        raise PriorLedgerError("ROUND_ID_INVALID", repr(round_id))
    return {n: f"pm:prior:{round_id}:{n}" for n in NAMES}


def seeds(round_id: str) -> tuple[int, int]:
    keys(round_id)
    if round_id not in SEEDS:
        raise PriorLedgerError("SEED_NOT_FIXED", f"no seeds fixed for {round_id} (SEEDS is committed before data)")
    return SEEDS[round_id]


def _canon(rec) -> str:
    return json.dumps(rec, sort_keys=True, separators=(",", ":"))


def cell_key(cell) -> str:
    return _canon(cell)


def candidates(store, *, round_id: str, seed: int | None = None, n: int = N_CANDIDATES, now: float | None = None,
               grid: dict | None = None, doc=_FROM_FILE) -> dict:
    """Publish the round's candidate cell list once, by seeded draw over the draw grid."""
    k = keys(round_id)
    seed = seeds(round_id)[0] if seed is None else int(seed)
    if store.hget(k["candidates"], "record") is not None:
        raise PriorLedgerError("CANDIDATES_ALREADY_PUBLISHED", f"the {round_id} candidate list is drawn once")
    if grid is None:
        from primordial.ops import draw_cell as DC
        grid = DC.axes() if doc is _FROM_FILE else DC.axes(doc)
    names = list(grid)
    sizes = [len(grid[x]) for x in names]
    n_cells = int(np.prod(sizes))
    if n_cells == 0:
        raise PriorLedgerError("EMPTY_GRID", "the draw grid has no cells")
    rng = np.random.Generator(np.random.PCG64(seed))
    flats = sorted(rng.choice(n_cells, size=min(int(n), n_cells), replace=False).tolist())
    cells = [{x: grid[x][int(i)] for x, i in zip(names, np.unravel_index(f, sizes))} for f in flats]
    record = {"round": round_id, "seed": seed, "ts": round(time.time() if now is None else float(now), 3),
              "n": len(cells), "grid_cells": n_cells, "cells": cells}
    if not store.hsetnx(k["candidates"], "record", _canon(record)):
        raise PriorLedgerError("CANDIDATES_ALREADY_PUBLISHED", f"the {round_id} candidate list is drawn once")
    return record


def published(store, *, round_id: str) -> dict | None:
    body = store.hget(keys(round_id)["candidates"], "record")
    return None if body is None else json.loads(body)


def seal(store, prediction: dict, writer_role: str, *, round_id: str, experimenter_ids=()) -> str:
    k = keys(round_id)
    if writer_role != "predictor":
        raise PriorLedgerError("WRITE_DENIED", f"role {writer_role!r} may not write priors")
    if prediction.get("predictor_id") in set(experimenter_ids):
        raise PriorLedgerError("WRITE_DENIED", "the predictor must not be an experimenter")
    missing = [f for f in FIELDS + ("prediction_id", "cell") if prediction.get(f) in (None, "")]
    if missing:
        raise PriorLedgerError("FIELD_MISSING", str(missing))
    p = prediction["prior_p_pass"]
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not 0.0 <= float(p) <= 1.0:
        raise PriorLedgerError("P_OUT_OF_RANGE", repr(p))
    rec = {x: prediction[x] for x in FIELDS + ("prediction_id", "cell")}
    rec["prior_p_pass"], rec["prediction_ts"] = float(p), float(rec["prediction_ts"])
    body = _canon(rec)
    if not store.hsetnx(k["sealed"], rec["prediction_id"], body):
        raise PriorLedgerError("ALREADY_SEALED", rec["prediction_id"])
    digest = hashlib.sha256(body.encode()).hexdigest()
    store.hset(k["commit"], rec["prediction_id"], digest)
    return digest


def verify(store, prediction_id: str, *, round_id: str) -> bool:
    k = keys(round_id)
    body = store.hget(k["sealed"], prediction_id)
    return body is not None and hashlib.sha256(body.encode()).hexdigest() == store.hget(k["commit"], prediction_id)


def _all(store, round_id: str) -> list[dict]:
    return [json.loads(v) for _, v in sorted(store.hgetall(keys(round_id)["sealed"]).items())]


def freeze_ranks(store, now: float, *, round_id: str, tie_seed: int | None = None) -> dict:
    k = keys(round_id)
    body = store.hget(k["ranks"], "record")
    if body is not None:
        return json.loads(body)
    pub = published(store, round_id=round_id)
    if pub is None:
        raise PriorLedgerError("CANDIDATES_NOT_PUBLISHED", f"publish the {round_id} candidate cells first")
    listed = {cell_key(c) for c in pub["cells"]}
    preds = sorted((p for p in _all(store, round_id) if p["prediction_ts"] < now and cell_key(p["cell"]) in listed
                    and verify(store, p["prediction_id"], round_id=round_id)), key=lambda p: p["prediction_id"])
    if not preds:
        raise PriorLedgerError("NO_PREDICTIONS", "no sealed prediction on a published cell before the freeze")
    tie_seed = int(pub["seed"] if tie_seed is None else tie_seed)
    perm = np.random.Generator(np.random.PCG64(tie_seed)).permutation(len(preds)).tolist()
    tie_break = {p["prediction_id"]: int(perm[i]) for i, p in enumerate(preds)}
    order = sorted(preds, key=lambda p: (-p["prior_p_pass"], tie_break[p["prediction_id"]]))
    n = len(order)
    ranks = {p["prediction_id"]: {"rank": i + 1, "quantile": (i + 0.5) / n, "prior_p_pass": p["prior_p_pass"],
                                  "tie_break": tie_break[p["prediction_id"]]} for i, p in enumerate(order)}
    groups: dict[float, list[str]] = {}
    for p in order:
        groups.setdefault(p["prior_p_pass"], []).append(p["prediction_id"])
    record = {"round": round_id, "ts": float(now), "n": n, "tie_seed": tie_seed, "ranks": ranks,
              "ties": [{"prior_p_pass": pv, "order": ids} for pv, ids in groups.items() if len(ids) > 1]}
    if not store.hsetnx(k["ranks"], "record", _canon(record)):
        return json.loads(store.hget(k["ranks"], "record"))
    return record


def arm_of(index: int, arm_seed: int, p: float = ARM_P) -> tuple[str, float]:
    u = float(np.random.Generator(np.random.PCG64([int(arm_seed), int(index)])).random())
    return ("calibration" if u < p else "anti_prior"), u


def assign(store, exp_id: str, now: float, *, round_id: str, arm_seed: int | None = None, p: float = ARM_P) -> list[dict]:
    k = keys(round_id)
    arm_seed = seeds(round_id)[1] if arm_seed is None else int(arm_seed)
    if store.hget(k["assign"], exp_id) is not None:
        raise PriorLedgerError("ALREADY_ASSIGNED", exp_id)
    ranks = freeze_ranks(store, now, round_id=round_id)
    existing = [json.loads(v) for v in store.hgetall(k["assign"]).values()]
    index = len(existing)
    arm, u = arm_of(index, arm_seed, p)
    taken = {a["prediction_id"] for a in existing}
    in_arm = (lambda q: q < TOP_Q) if arm == "calibration" else (lambda q: q > BOTTOM_Q)
    pool = sorted((pid for pid, rk in ranks["ranks"].items() if in_arm(rk["quantile"]) and pid not in taken
                   and verify(store, pid, round_id=round_id)), key=lambda pid: ranks["ranks"][pid]["rank"])
    if not pool:
        return []
    pick = pool[int(np.random.Generator(np.random.PCG64([arm_seed, index, 1])).integers(len(pool)))]
    pred = json.loads(store.hget(k["sealed"], pick))
    rk = ranks["ranks"][pick]
    store.hset(k["assign"], exp_id, _canon({"round": round_id, "prediction_id": pick, "cell": pred["cell"],
                                            "assignment_ts": float(now), "arm_seed": arm_seed, "index": index, "u": u,
                                            "arm": arm, "rank": rk["rank"], "quantile": rk["quantile"]}))
    return [{"exp_id": exp_id, "cell": pred["cell"]}]


def eligible_at(prediction: dict, assignment_ts: float) -> None:
    if not float(prediction["prediction_ts"]) < float(assignment_ts):
        raise PriorLedgerError("PREDICTION_NOT_BEFORE_ASSIGNMENT",
                               f"{prediction['prediction_ts']} >= {assignment_ts}")


def read(store, prediction_id: str, reader_role: str, receipt_filed=lambda exp_id: False, *, round_id: str) -> dict:
    k = keys(round_id)
    if reader_role not in ROLES:
        raise PriorLedgerError("READ_DENIED", f"unknown role {reader_role!r}")
    body = store.hget(k["sealed"], prediction_id)
    if body is None:
        raise PriorLedgerError("NOT_FOUND", prediction_id)
    if reader_role == "experimenter":
        exps = [e for e, v in store.hgetall(k["assign"]).items() if json.loads(v)["prediction_id"] == prediction_id]
        if not exps or not all(receipt_filed(e) for e in exps):
            raise PriorLedgerError("EXPERIMENTER_READ_DENIED", f"no filed receipt for {exps or 'an assignment'}")
    return json.loads(body)


def migrate_unnamespaced(r, round_id: str) -> dict:
    """D11: move the un-namespaced v2 keys pm:prior:<name> to pm:prior:<round_id>:<name> by RENAMENX (never overwrite).
    -> {moved, skipped (no source), conflict (destination exists; nothing moved)}. pm:prior:r5:* is never read."""
    k = keys(round_id)
    out = {"round": round_id, "moved": [], "skipped": [], "conflict": []}
    for name in NAMES:
        src = f"pm:prior:{name}"
        if not r.exists(src):
            out["skipped"].append(src)
        elif r.exists(k[name]) or not r.renamenx(src, k[name]):
            out["conflict"].append(src)
        else:
            out["moved"].append([src, k[name]])
    return out


def _stats(ps, hits, quantiles=None) -> dict:
    if not ps:
        return {"n": 0}
    pr, hit = np.array(ps), np.array(hits)
    out = {"n": len(ps), "mean_prior": round(float(pr.mean()), 4), "pass_rate": round(float(hit.mean()), 4),
           "brier": round(float(((pr - hit) ** 2).mean()), 4)}
    if quantiles:
        out["mean_quantile"] = round(float(np.mean(quantiles)), 4)
    return out


def calibration(store, outcomes: dict, *, rounds: list[str]) -> dict:
    """outcomes: {round_id: {prediction_id: True (PASS) | False}}. Descriptive only (H-R7-3): by arm accumulated across
    `rounds`, per round by arm, by rank quartile and by absolute p bucket."""
    pooled = {arm: ([], [], []) for arm in ARMS}
    per_round, quart, bucket_rows = {}, {q: ([], [], []) for q in ("top", "middle", "bottom")}, []
    all_ps, all_hits = [], []
    for rid in rounds:
        k = keys(rid)
        sealed = {p["prediction_id"]: p for p in _all(store, rid)}
        out_r = {pid: v for pid, v in (outcomes.get(rid) or {}).items() if pid in sealed}
        body = store.hget(k["ranks"], "record")
        ranks = json.loads(body)["ranks"] if body else {}
        assigned = [json.loads(v) for v in store.hgetall(k["assign"]).values()]
        per_arm = {}
        for arm in ARMS:
            ids = [a["prediction_id"] for a in assigned if a.get("arm") == arm and a["prediction_id"] in out_r]
            ps = [sealed[i]["prior_p_pass"] for i in ids]
            hits = [1.0 if out_r[i] else 0.0 for i in ids]
            qs = [ranks[i]["quantile"] for i in ids if i in ranks]
            per_arm[arm] = _stats(ps, hits, qs)
            pooled[arm][0].extend(ps), pooled[arm][1].extend(hits), pooled[arm][2].extend(qs)
        per_round[rid] = per_arm
        for i, v in out_r.items():
            all_ps.append(sealed[i]["prior_p_pass"])
            all_hits.append(1.0 if v else 0.0)
            if i in ranks:
                q = ranks[i]["quantile"]
                name = "top" if q < TOP_Q else ("bottom" if q > BOTTOM_Q else "middle")
                quart[name][0].append(sealed[i]["prior_p_pass"]), quart[name][1].append(1.0 if v else 0.0)
                quart[name][2].append(q)
    for lo, hi in zip(BUCKETS, BUCKETS[1:]):
        idx = [j for j, pv in enumerate(all_ps) if lo <= pv < hi or (hi == 1.0 and pv == 1.0)]
        bucket_rows.append({"bucket": [lo, hi], **_stats([all_ps[j] for j in idx], [all_hits[j] for j in idx])})
    return {"kind": "anti_prior_calibration", "version": 3, "rounds": list(rounds), "descriptive_only": True,
            "n": len(all_ps), "by_arm": {arm: _stats(*pooled[arm]) for arm in ARMS}, "per_round": per_round,
            "by_quartile": {q: _stats(*v) for q, v in quart.items()}, "buckets": bucket_rows,
            "note": "small N: no inference (prompt 19 s11)"}
