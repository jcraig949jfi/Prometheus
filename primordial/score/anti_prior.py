"""H-R5-2 / H-R6-3: the SEALED ANTI-PRIOR LEDGER, version 2 (prompt 19 s10-11, SWARM_R5 O5, SWARM_R6 O3).

A predictor (lane R, a separate session, never the experimenter) posts a prior per candidate cell BEFORE
assignment. Code publishes the candidate cells, so the predictor never chooses them (A 1789469025336-0). Priors never
enter scientific scoring.

Round 5 finding (operator 21): 12/12 priors were <= 0.2, so an absolute p filter did not discriminate. Version 2
works on RANK among the sealed set and adds a calibration arm (O3):

  candidates(store, seed=20260917, n=48)   code-published candidate list: a seeded PCG64 draw of n distinct cells from
                                           primordial.ops.draw_cell.axes(), written ONCE to pm:prior:candidates
                                           {seed, ts, n, grid_cells, cells}; a second call refuses
                                           (CANDIDATES_ALREADY_PUBLISHED). A publishes it once at launch.
  seal(store, prediction, writer_role)     predictor-only write, once per prediction_id; fields prior_p_pass in [0, 1],
                                           prior_expected_direction, prior_expected_mechanism, predictor_id,
                                           prediction_ts, cell; sha256 commitment beside it (verify()).
  freeze_ranks(store, now)                 ONCE (pm:prior:ranks): every verified prediction on a published cell with
                                           prediction_ts < now is ranked by prior_p_pass descending (rank 1 = most
                                           confident PASS); ties in p are broken by a seeded permutation (seed = the
                                           candidates seed) and the tie groups + order are recorded. quantile =
                                           (rank - 0.5) / n. Absolute prior_p_pass is kept beside rank and quantile.
  assign(store, exp_id, now)               assignment index i (0, 1, ...): u = PCG64([ARM_SEED 20260918, i]).random();
                                           arm = calibration iff u < 0.25 (pool: quantile < 0.25, the top rank
                                           quartile) else anti_prior (pool: quantile > 0.75, the bottom quartile); one
                                           unassigned prediction drawn from the arm's pool by PCG64([ARM_SEED, i, 1]).
                                           The record stores arm, u, rank, quantile. -> [{exp_id, cell}] only.
  read(store, prediction_id, role, ...)    predictor and conductor read the sealed record only (never an arm or a
                                           rank: R is not told the arms); the experimenter is denied
                                           (EXPERIMENTER_READ_DENIED) until its receipt is filed.
  calibration(store, outcomes)             descriptive: by arm, by rank quartile, and by absolute p bucket.

Sealing is API-level plus the commitment (round 5 PC D8), not cryptographic against direct Redis reads.

Store: any object with hget/hset/hgetall/hsetnx (redis.Redis with decode_responses=True).
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

SEALED = "pm:prior:sealed"            # prediction_id -> canonical json
COMMIT = "pm:prior:commit"            # prediction_id -> sha256(canonical json)
ASSIGN = "pm:prior:assign"            # exp_id -> json {prediction_id, cell, assignment_ts, index, u, arm, rank, quantile}
CANDIDATES = "pm:prior:candidates"    # field "record" -> json {seed, ts, n, grid_cells, cells}
RANKS = "pm:prior:ranks"              # field "record" -> json {ts, n, tie_seed, ranks, ties}
FIELDS = ("prior_p_pass", "prior_expected_direction", "prior_expected_mechanism", "predictor_id", "prediction_ts")
N_CANDIDATES = 48                     # SWARM_R6 s3 H-R6-3
CANDIDATES_SEED_R6 = 20260917         # SWARM_R6 seeds, fixed before any round 6 data
ARM_SEED_R6 = 20260918
ARM_P = 0.25                          # SWARM_R6 O3: calibration arm probability
TOP_Q, BOTTOM_Q = 0.25, 0.75
ARMS = ("calibration", "anti_prior")
ROLES = ("predictor", "experimenter", "conductor")
BUCKETS = (0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0)
_FROM_FILE = object()


class PriorLedgerError(PermissionError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


def _canon(rec) -> str:
    return json.dumps(rec, sort_keys=True, separators=(",", ":"))


def cell_key(cell) -> str:
    """Canonical identity of a cell (a draw_cell dict, or any JSON value) for list membership."""
    return _canon(cell)


def candidates(store, seed: int = CANDIDATES_SEED_R6, n: int = N_CANDIDATES, now: float | None = None,
               grid: dict | None = None, doc=_FROM_FILE) -> dict:
    """Publish the candidate cell list once, by seeded draw over the draw grid. The predictor never chooses cells."""
    if store.hget(CANDIDATES, "record") is not None:
        raise PriorLedgerError("CANDIDATES_ALREADY_PUBLISHED", "the candidate list is drawn once per round")
    if grid is None:
        from primordial.ops import draw_cell as DC
        grid = DC.axes() if doc is _FROM_FILE else DC.axes(doc)
    names = list(grid)
    sizes = [len(grid[k]) for k in names]
    n_cells = int(np.prod(sizes))
    if n_cells == 0:
        raise PriorLedgerError("EMPTY_GRID", "the draw grid has no cells")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    flats = sorted(rng.choice(n_cells, size=min(int(n), n_cells), replace=False).tolist())
    cells = [{k: grid[k][int(i)] for k, i in zip(names, np.unravel_index(f, sizes))} for f in flats]
    record = {"seed": int(seed), "ts": round(time.time() if now is None else float(now), 3), "n": len(cells),
              "grid_cells": n_cells, "cells": cells}
    if not store.hsetnx(CANDIDATES, "record", _canon(record)):
        raise PriorLedgerError("CANDIDATES_ALREADY_PUBLISHED", "the candidate list is drawn once per round")
    return record


def published(store) -> dict | None:
    body = store.hget(CANDIDATES, "record")
    return None if body is None else json.loads(body)


def seal(store, prediction: dict, writer_role: str, experimenter_ids=()) -> str:
    """Write one prediction. Refusals: WRITE_DENIED (not the predictor role, or the predictor is an experimenter),
    FIELD_MISSING, P_OUT_OF_RANGE, ALREADY_SEALED."""
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
    rec = {k: prediction[k] for k in FIELDS + ("prediction_id", "cell")}
    rec["prior_p_pass"], rec["prediction_ts"] = float(p), float(rec["prediction_ts"])
    body = _canon(rec)
    if not store.hsetnx(SEALED, rec["prediction_id"], body):
        raise PriorLedgerError("ALREADY_SEALED", rec["prediction_id"])
    digest = hashlib.sha256(body.encode()).hexdigest()
    store.hset(COMMIT, rec["prediction_id"], digest)
    return digest


def verify(store, prediction_id: str) -> bool:
    body = store.hget(SEALED, prediction_id)
    return body is not None and hashlib.sha256(body.encode()).hexdigest() == store.hget(COMMIT, prediction_id)


def _all(store) -> list[dict]:
    return [json.loads(v) for _, v in sorted(store.hgetall(SEALED).items())]


def freeze_ranks(store, now: float, tie_seed: int | None = None) -> dict:
    """Rank the sealed set once. Rank 1 = highest prior_p_pass; ties broken by a seeded permutation, recorded."""
    body = store.hget(RANKS, "record")
    if body is not None:
        return json.loads(body)
    pub = published(store)
    if pub is None:
        raise PriorLedgerError("CANDIDATES_NOT_PUBLISHED", "publish the candidate cells (candidates()) first")
    listed = {cell_key(c) for c in pub["cells"]}
    preds = sorted((p for p in _all(store) if p["prediction_ts"] < now and cell_key(p["cell"]) in listed
                    and verify(store, p["prediction_id"])), key=lambda p: p["prediction_id"])
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
    record = {"ts": float(now), "n": n, "tie_seed": tie_seed, "ranks": ranks,
              "ties": [{"prior_p_pass": pv, "order": ids} for pv, ids in groups.items() if len(ids) > 1]}
    if not store.hsetnx(RANKS, "record", _canon(record)):
        return json.loads(store.hget(RANKS, "record"))
    return record


def arm_of(index: int, arm_seed: int = ARM_SEED_R6, p: float = ARM_P) -> tuple[str, float]:
    u = float(np.random.Generator(np.random.PCG64([int(arm_seed), int(index)])).random())
    return ("calibration" if u < p else "anti_prior"), u


def assign(store, exp_id: str, now: float, arm_seed: int = ARM_SEED_R6, p: float = ARM_P) -> list[dict]:
    """One assignment: the arm by seeded Bernoulli(p), a prediction from that arm's rank quartile. Cells only."""
    if store.hget(ASSIGN, exp_id) is not None:
        raise PriorLedgerError("ALREADY_ASSIGNED", exp_id)
    ranks = freeze_ranks(store, now)
    existing = [json.loads(v) for v in store.hgetall(ASSIGN).values()]
    index = len(existing)
    arm, u = arm_of(index, arm_seed, p)
    taken = {a["prediction_id"] for a in existing}
    in_arm = (lambda q: q < TOP_Q) if arm == "calibration" else (lambda q: q > BOTTOM_Q)
    pool = sorted((pid for pid, rk in ranks["ranks"].items() if in_arm(rk["quantile"]) and pid not in taken
                   and verify(store, pid)), key=lambda pid: ranks["ranks"][pid]["rank"])
    if not pool:
        return []
    pick = pool[int(np.random.Generator(np.random.PCG64([int(arm_seed), index, 1])).integers(len(pool)))]
    pred = json.loads(store.hget(SEALED, pick))
    rk = ranks["ranks"][pick]
    store.hset(ASSIGN, exp_id, _canon({"prediction_id": pick, "cell": pred["cell"], "assignment_ts": float(now),
                                       "arm_seed": int(arm_seed), "index": index, "u": u, "arm": arm,
                                       "rank": rk["rank"], "quantile": rk["quantile"]}))
    return [{"exp_id": exp_id, "cell": pred["cell"]}]


def eligible_at(prediction: dict, assignment_ts: float) -> None:
    """Refuse a prediction that does not predate its assignment."""
    if not float(prediction["prediction_ts"]) < float(assignment_ts):
        raise PriorLedgerError("PREDICTION_NOT_BEFORE_ASSIGNMENT",
                               f"{prediction['prediction_ts']} >= {assignment_ts}")


def read(store, prediction_id: str, reader_role: str, receipt_filed=lambda exp_id: False) -> dict:
    """The sealed record only: no arm, rank or quantile is ever returned (R is not told the arms)."""
    if reader_role not in ROLES:
        raise PriorLedgerError("READ_DENIED", f"unknown role {reader_role!r}")
    body = store.hget(SEALED, prediction_id)
    if body is None:
        raise PriorLedgerError("NOT_FOUND", prediction_id)
    if reader_role == "experimenter":
        exps = [e for e, v in store.hgetall(ASSIGN).items() if json.loads(v)["prediction_id"] == prediction_id]
        if not exps or not all(receipt_filed(e) for e in exps):
            raise PriorLedgerError("EXPERIMENTER_READ_DENIED", f"no filed receipt for {exps or 'an assignment'}")
    return json.loads(body)


def _stats(ps: list[float], hits: list[float], quantiles: list[float] | None = None) -> dict:
    if not ps:
        return {"n": 0}
    pr, hit = np.array(ps), np.array(hits)
    out = {"n": len(ps), "mean_prior": round(float(pr.mean()), 4), "pass_rate": round(float(hit.mean()), 4),
           "brier": round(float(((pr - hit) ** 2).mean()), 4)}
    if quantiles:
        out["mean_quantile"] = round(float(np.mean(quantiles)), 4)
    return out


def calibration(store, outcomes: dict) -> dict:
    """outcomes: {prediction_id: True (PASS) | False (not PASS)} for resolved predictions. Descriptive only:
    by arm (assigned predictions), by rank quartile (ranked predictions) and by absolute p bucket."""
    sealed = {p["prediction_id"]: p for p in _all(store)}
    resolved = [pid for pid in outcomes if pid in sealed]
    hit = lambda pid: 1.0 if outcomes[pid] else 0.0
    buckets = []
    for lo, hi in zip(BUCKETS, BUCKETS[1:]):
        ids = [pid for pid in resolved
               if lo <= sealed[pid]["prior_p_pass"] < hi or (hi == 1.0 and sealed[pid]["prior_p_pass"] == 1.0)]
        buckets.append({"bucket": [lo, hi], **_stats([sealed[i]["prior_p_pass"] for i in ids], [hit(i) for i in ids])})
    body = store.hget(RANKS, "record")
    ranks = json.loads(body)["ranks"] if body else {}
    by_arm = {}
    assigned = [json.loads(v) for v in store.hgetall(ASSIGN).values()]
    for arm in ARMS:
        ids = [a["prediction_id"] for a in assigned if a.get("arm") == arm and a["prediction_id"] in outcomes]
        by_arm[arm] = _stats([sealed[i]["prior_p_pass"] for i in ids], [hit(i) for i in ids],
                             [ranks[i]["quantile"] for i in ids if i in ranks])
    by_quartile = {}
    for name, rule in (("top", lambda q: q < TOP_Q), ("middle", lambda q: TOP_Q <= q <= BOTTOM_Q),
                       ("bottom", lambda q: q > BOTTOM_Q)):
        ids = [i for i in resolved if i in ranks and rule(ranks[i]["quantile"])]
        by_quartile[name] = _stats([sealed[i]["prior_p_pass"] for i in ids], [hit(i) for i in ids],
                                   [ranks[i]["quantile"] for i in ids])
    return {"kind": "anti_prior_calibration", "version": 2, "descriptive_only": True,
            "n": sum(b["n"] for b in buckets), "buckets": buckets, "by_arm": by_arm, "by_quartile": by_quartile,
            "note": "small N: no inference (prompt 19 s11)"}
