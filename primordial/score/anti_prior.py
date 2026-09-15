"""H-R5-2 (round 5 P-BUILD, builder H): the SEALED ANTI-PRIOR LEDGER (prompt 19 s10-11, SWARM_R5 O5).

A predictor (a separate session, never the experimenter) posts a prior per candidate cell BEFORE assignment.
Code then assigns falsification attempts among the confident expected failures; the experimenter receives
only the cell and cannot read the prior until its receipt is filed. Priors never enter scientific scoring.

  seal(store, prediction, writer_role)      predictor-only write, once per prediction_id; fields
                                            prior_p_pass in [0, 1], prior_expected_direction,
                                            prior_expected_mechanism, predictor_id, prediction_ts, cell.
                                            A sha256 commitment of the canonical record is stored beside it,
                                            so a changed prior is detectable (verify()).
  assign(store, exp_id, seed, now, k=1)     code assignment: among predictions with prior_p_pass <= P_MAX (0.2)
                                            and prediction_ts < now, a seeded PCG64 draw of k in prediction_id
                                            order. -> {exp_id, cell} only. A prediction made at or after the
                                            assignment time is never eligible (PREDICTION_NOT_BEFORE_ASSIGNMENT).
  read(store, prediction_id, reader_role, receipt_filed)
                                            predictor and conductor may read; the experimenter is denied
                                            (EXPERIMENTER_READ_DENIED) until receipt_filed(exp_id) is true for the
                                            assignment that holds the prediction.
  calibration(store, outcomes)              descriptive close-of-round table per prior bucket: n, mean prior,
                                            observed PASS rate, Brier. No inference from small N (19 s11).

Sealing is enforced by this API (the only reader the experimenter is given), plus the commitment for tamper
evidence. It is not cryptographic against a session that reads Redis keys directly: that is a
PRODUCTION_CANDIDATE note, not a SMOKE-stage requirement.

Store: any object with hget/hset/hgetall/hsetnx (redis.Redis with decode_responses=True).
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

SEALED = "pm:prior:sealed"            # prediction_id -> canonical json
COMMIT = "pm:prior:commit"            # prediction_id -> sha256(canonical json)
ASSIGN = "pm:prior:assign"            # exp_id -> json {prediction_id, cell, assignment_ts, seed}
FIELDS = ("prior_p_pass", "prior_expected_direction", "prior_expected_mechanism", "predictor_id", "prediction_ts")
P_MAX = 0.2                           # SWARM_R5 O5: high-confidence expected failures
ROLES = ("predictor", "experimenter", "conductor")
BUCKETS = (0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0)


class PriorLedgerError(PermissionError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


def _canon(rec: dict) -> str:
    return json.dumps(rec, sort_keys=True, separators=(",", ":"))


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


def assign(store, exp_id: str, seed: int, now: float, k: int = 1, p_max: float = P_MAX) -> list[dict]:
    """Seeded draw among confident expected failures predicted before `now`. The caller gets cells only."""
    if store.hget(ASSIGN, exp_id) is not None:
        raise PriorLedgerError("ALREADY_ASSIGNED", exp_id)
    taken = {json.loads(v)["prediction_id"] for v in store.hgetall(ASSIGN).values()}
    pool = [p for p in _all(store)
            if p["prior_p_pass"] <= p_max and p["prediction_ts"] < now and p["prediction_id"] not in taken
            and verify(store, p["prediction_id"])]
    if not pool:
        return []
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    picks = sorted(rng.choice(len(pool), size=min(k, len(pool)), replace=False).tolist())
    out = []
    for i, idx in enumerate(picks):
        p = pool[idx]
        key = exp_id if len(picks) == 1 else f"{exp_id}.{i}"
        store.hset(ASSIGN, key, _canon({"prediction_id": p["prediction_id"], "cell": p["cell"],
                                       "assignment_ts": float(now), "seed": int(seed)}))
        out.append({"exp_id": key, "cell": p["cell"]})
    return out


def eligible_at(prediction: dict, assignment_ts: float) -> None:
    """Refuse a prediction that does not predate its assignment."""
    if not float(prediction["prediction_ts"]) < float(assignment_ts):
        raise PriorLedgerError("PREDICTION_NOT_BEFORE_ASSIGNMENT",
                               f"{prediction['prediction_ts']} >= {assignment_ts}")


def read(store, prediction_id: str, reader_role: str, receipt_filed=lambda exp_id: False) -> dict:
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


def calibration(store, outcomes: dict) -> dict:
    """outcomes: {prediction_id: True (PASS) | False (not PASS)} for resolved predictions. Descriptive only."""
    rows = []
    for lo, hi in zip(BUCKETS, BUCKETS[1:]):
        ps = [p for p in _all(store) if p["prediction_id"] in outcomes
              and (lo <= p["prior_p_pass"] < hi or (hi == 1.0 and p["prior_p_pass"] == 1.0))]
        if not ps:
            rows.append({"bucket": [lo, hi], "n": 0})
            continue
        pr = np.array([p["prior_p_pass"] for p in ps])
        hit = np.array([1.0 if outcomes[p["prediction_id"]] else 0.0 for p in ps])
        rows.append({"bucket": [lo, hi], "n": len(ps), "mean_prior": round(float(pr.mean()), 4),
                     "pass_rate": round(float(hit.mean()), 4), "brier": round(float(((pr - hit) ** 2).mean()), 4)})
    n = sum(r["n"] for r in rows)
    return {"kind": "anti_prior_calibration", "descriptive_only": True, "n": n, "buckets": rows,
            "note": "small N: no inference (prompt 19 s11)"}
