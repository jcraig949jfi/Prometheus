"""H replay of B-R5-1 (round 5 pilot, conductor order): recompute B's CANDIDATE_N-eligible Clause A PASS from its
committed rows and saved elites, with no new QD (predicate posted before the run).

Inputs: primordial/ledger/rows/B/B-R5-1-cand-int4a4-w13-train128.jsonl (32 run rows + 1 candidate row) and the elite
file each run row names. Nothing is read from B's candidate row except to COMPARE: every number is recomputed.

  1. per run: readout.read (top1_train) over the saved elites with the family scorer (B's QLin decode + fused linear
     rollout); held64_per_seed, top_sha256, train_fit == the committed run row.
  2. pooled in (rng_family 4200, 2101, 3303, 5501; run_seed) order: median + metric.ci.median_ci; the sample stamp
     (runs_total, rng_family_count, runs_per_family, n_per_family) from the run rows == B's candidate row.
  3. progress_above_floor + progress_ci95 against metric.eligibility.w13_eligibility().
  4. qd_ledger.check_r4 on eligibility.r16_doc(), readout top1_train, the recomputed sample -> verdict / why / progress.
  5. obs-use control on each selected elite: W zeroed == the cell's abstain floor part, input_invariant_elites 0,
     and == B's committed control values.

Outcome AGREE iff every check holds; else DISAGREE with every mismatching field. Oracle cleanliness is B's recorded
value (not re-run). Same model family: a cross-lane check, not a promotion.

    worker job: primordial.score.replay_b_r5_1:job
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from primordial.score.round2 import ROOT

EXP = "H-R5-replay-B-R5-1"
B_ROWS = "primordial/ledger/rows/B/B-R5-1-cand-int4a4-w13-train128.jsonl"
FAMILY_ORDER = (4200, 2101, 3303, 5501)       # SWARM_R4 s9 / G bootstrap.order; B's plan order (BL.FAMILIES)
TOL = 1e-9


def _rows(path) -> list[dict]:
    p = pathlib.Path(path)
    p = p if p.is_absolute() else ROOT / p
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _near(a, b, tol=TOL) -> bool:
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)) and len(a) == len(b)
                and all(_near(x, y, tol) for x, y in zip(a, b)))
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def b_family():
    """(score_factory(zero_w) -> score_fn, glen, g7, decode) for B-R5-1's genome family (int4 linear + a4 codebook)."""
    from primordial.cohorts.b import r5_1_candidate as B
    from primordial.cohorts.b.b1_qlinear import QLin
    q = QLin(B.GS, B.BITS, B.ACTS)
    return (lambda zero_w=False: B.scorer(q, zero_w=zero_w)), q


def invariance(q, raw1) -> int:
    from primordial.cohorts.e.oracles import brain_oracle_cheats
    from primordial.metric import floors as F
    return int(brain_oracle_cheats(q.g7, q.decode(q.unpack(raw1)), np.asarray(F.HELD64[:8]))["input_invariant_elites"])


def replay(rows_path=B_ROWS, family=None, eligibility=None, doc=None, judge=None, invariant=None) -> dict:
    """-> {outcome AGREE|DISAGREE, mismatches: [{field, run?, b, h}], runs: [...], recomputed: {...}}."""
    from primordial.metric import floors as F
    from primordial.metric import readout as RO
    from primordial.metric.ci import median_ci
    rows = _rows(rows_path)
    runs = sorted((r for r in rows if r.get("kind") == "run"),
                  key=lambda r: (FAMILY_ORDER.index(int(r["rng_family"])), int(r["run_seed"])))
    [cand] = [r for r in rows if r.get("kind") == "candidate"]
    if family is None:
        factory, q = b_family()
        glen = q.glen
        invariant = invariant or (lambda raw1: invariance(q, raw1))
    else:
        factory, glen = family
    if eligibility is None or doc is None:
        from primordial.metric import eligibility as EL
        doc = doc if doc is not None else EL.r16_doc()
        eligibility = eligibility if eligibility is not None else EL.eligibility("w13", "train128_held64", doc)
    mm: list[dict] = []

    def miss(field, b, h, run=None):
        mm.append({"field": field, "run": run, "b": b, "h": h})

    score, zero_score = factory(False), factory(True)
    abstain = float(eligibility["floor_parts"]["abstain"])
    out_runs = []
    for r in runs:
        rid = f"{int(r['rng_family'])}|{int(r['run_seed'])}"
        doc_e = json.loads(pathlib.Path(r["elites"]).read_text(encoding="utf-8"))
        elites = RO.elites_of(doc_e)
        got = RO.read(elites, glen, score)
        raw1 = RO.packed(RO.select(elites), glen)
        zero = float(zero_score(raw1, F.HELD64))
        inv = int(invariant(raw1)) if invariant else 0
        for field, h in (("held64_per_seed", got["held64_per_seed"]), ("top_sha256", got["top_sha256"]),
                         ("train_fit", got["train_fit"])):
            if r.get(field) != h:
                miss(field, r.get(field), h, rid)
        ctl = r.get("control_obs_use") or {}
        if not _near(ctl.get("held64_w_zeroed"), zero):
            miss("control_obs_use.held64_w_zeroed", ctl.get("held64_w_zeroed"), zero, rid)
        if not _near(zero, abstain):
            miss("obs_use.w_zeroed_equals_abstain", abstain, zero, rid)
        if inv != 0 or int(ctl.get("input_invariant_selected", 0)) != inv:
            miss("obs_use.input_invariant_selected", ctl.get("input_invariant_selected"), inv, rid)
        out_runs.append({"run_id": rid, "rng_family": int(r["rng_family"]), "run_seed": int(r["run_seed"]),
                         "held64_per_seed": got["held64_per_seed"], "top_sha256": got["top_sha256"],
                         "train_fit": got["train_fit"], "held64_w_zeroed": zero, "input_invariant_selected": inv})

    held = [x["held64_per_seed"] for x in out_runs]
    fams = sorted({x["rng_family"] for x in out_runs})
    per = {str(f): sum(x["rng_family"] == f for x in out_runs) for f in fams}
    sample = {"runs_total": len(held), "rng_family_count": len(fams),
              "runs_per_family": min(per.values()) if len(set(per.values())) == 1 else None, "n_per_family": per}
    med = float(np.median(held))
    lo, hi = median_ci(held)
    floor, den = float(eligibility["floor"]), float(eligibility["progress_denominator"])
    prog, prog_ci = (med - floor) / den, [(lo - floor) / den, (hi - floor) / den]
    for field, h in (("runs_total", sample["runs_total"]), ("rng_family_count", sample["rng_family_count"]),
                     ("runs_per_family", sample["runs_per_family"])):
        if cand.get(field) != h:
            miss(field, cand.get(field), h)
    if {str(k): int(v) for k, v in (cand.get("n_per_family") or {}).items()} != per:
        miss("n_per_family", cand.get("n_per_family"), per)
    for field, h in (("candidate_score", med), ("candidate_ci95", [lo, hi]), ("floor", floor),
                     ("progress_above_floor", prog), ("progress_ci95", prog_ci)):
        if not _near(cand.get(field), h):
            miss(field, cand.get(field), h)
    if not _near(cand.get("baseline"), eligibility["baseline"]["median"]):
        miss("baseline", cand.get("baseline"), eligibility["baseline"]["median"])
    bh = cand.get("held64_by_run") or {}
    if {k: float(v) for k, v in bh.items()} != {x["run_id"]: x["held64_per_seed"] for x in out_runs}:
        miss("held64_by_run", "B map", "recomputed map differs")

    if judge is None:
        from primordial.ops import qd_ledger as QL
        judge = QL.check_r4
    verdict = judge("w13", "train128_held64", med, int(cand.get("bytes") or glen), sample["runs_total"],
                    oracle_clean=bool(cand.get("oracle_clean")), held=held, doc=doc, readout=RO.NAME,
                    runs_total=sample["runs_total"], rng_family_count=sample["rng_family_count"],
                    runs_per_family=sample["runs_per_family"], n_per_family=per)
    bj = cand.get("judge") or {}
    for field in ("verdict", "why"):
        if bj.get(field) != verdict.get(field):
            miss(f"judge.{field}", bj.get(field), verdict.get(field))
    if not _near(bj.get("progress"), verdict.get("progress")):
        miss("judge.progress", bj.get("progress"), verdict.get("progress"))
    if cand.get("verdict") != verdict.get("verdict"):
        miss("verdict", cand.get("verdict"), verdict.get("verdict"))

    return {"outcome": "AGREE" if not mm else "DISAGREE", "first_mismatch": mm[0]["field"] if mm else None,
            "mismatches": mm, "runs": out_runs,
            "recomputed": {**sample, "candidate_score": med, "candidate_ci95": [lo, hi], "floor": floor,
                           "baseline": eligibility["baseline"]["median"], "progress_denominator": den,
                           "progress_above_floor": prog, "progress_ci95": prog_ci, "abstain": abstain,
                           "judge": {k: verdict.get(k) for k in ("verdict", "why", "progress", "readout")},
                           "obs_use": {"runs_w_zeroed_equals_abstain": sum(_near(x["held64_w_zeroed"], abstain)
                                                                           for x in out_runs),
                                       "runs_input_invariant": sum(x["input_invariant_selected"] for x in out_runs)}}}


def job(ctx, rows_path=B_ROWS):
    """F7 worker job: one replay_run row per B run, then the replay row (status control: a check, not a claim)."""
    out = replay(rows_path)
    for x in out["runs"]:
        ctx.emit({"kind": "replay_run", "exp_id": EXP, "replays": "B-R5-1-cand-int4a4-w13-train128", **x,
                  "status": "control"})
    ctx.emit({"kind": "replay", "exp_id": EXP, "replays": "B-R5-1-cand-int4a4-w13-train128",
              "b_receipt": "1789473262958-0", "b_rows": B_ROWS, "outcome": out["outcome"],
              "first_mismatch": out["first_mismatch"], "mismatches": out["mismatches"], **out["recomputed"],
              "note": "same model family: a cross-lane check, not a promotion", "status": "control"})
    return out["outcome"]
