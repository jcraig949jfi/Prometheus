"""H-R5-4 (round 5 P-BUILD, builder H): the EXPECTED_REFUSAL_OBSERVED classifier (prompt 19 s3, SWARM_R5 s3).

There is one scientific judge. A deliberately under-sampled SMOKE / PILOT / REPLICATION job must get the
judge's NORMAL refusal; the campaign controller may then label that a successful test of the machinery. This
module only reads the judge's output. It never calls the judge with a stage, never changes a threshold, and its
label is never a scientific verdict.

  deliberate under-sample   envelope campaign_stage in SMOKE|PILOT|REPLICATION AND the job's sample
                            (runs_total, rng_family_count, runs_per_family, n_per_family) is below the
                            judge's own minimum (imported from qd_ledger). No agent declares the expectation.
  labels                    EXPECTED_REFUSAL_OBSERVED    deliberate, and the judge said INELIGIBLE with a sample
                                                         reason (CANDIDATE_N, BASELINE_N, FAMILY_COVERAGE)
                            UNEXPECTED_REFUSAL_REASON    deliberate, INELIGIBLE for some other reason
                            EXPECTED_REFUSAL_MISSING     deliberate, but the judge gave a verdict (a defect)
                            NOT_APPLICABLE               not a deliberate under-sample (PRODUCTION, or enough runs)

emit() writes the label to F's event stream pm:events (F 1789467306628-0); NOT_APPLICABLE is not emitted.
"""
from __future__ import annotations

import json
import time

SAMPLE_REFUSALS = ("CANDIDATE_N", "BASELINE_N", "FAMILY_COVERAGE")
UNDERSAMPLE_STAGES = ("SMOKE", "PILOT", "REPLICATION")
LABELS = ("EXPECTED_REFUSAL_OBSERVED", "UNEXPECTED_REFUSAL_REASON", "EXPECTED_REFUSAL_MISSING", "NOT_APPLICABLE")
EVENTS = "pm:events"


def _minimum() -> tuple[int, int, int]:
    from primordial.ops import qd_ledger as Q
    return Q.BASELINE_MIN_RUNS, Q.BASELINE_MIN_FAMILIES, Q.BASELINE_MIN_PER_FAMILY


def undersampled(sample: dict | None) -> list[str]:
    """The sample fields below the judge's minimum (absent counts as below)."""
    s = sample or {}
    n_runs, n_fam, n_per = _minimum()
    short = []
    for field, need in (("runs_total", n_runs), ("rng_family_count", n_fam), ("runs_per_family", n_per)):
        v = s.get(field)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < need:
            short.append(field)
    per = s.get("n_per_family")
    if isinstance(per, dict) and any(int(v) < n_per for v in per.values()):
        short.append("n_per_family")
    return short


def classify(envelope: dict | None, sample: dict | None, judge: dict | None) -> dict:
    """A campaign label from the envelope, the job's sample and the judge's (unmodified) result."""
    stage = (envelope or {}).get("campaign_stage")
    short = undersampled(sample)
    j = judge or {}
    j = j.get("clause_a_r4", j) if isinstance(j.get("clause_a_r4"), dict) else j
    verdict, why = j.get("verdict"), j.get("why")
    if stage not in UNDERSAMPLE_STAGES or not short:
        label = "NOT_APPLICABLE"
    elif verdict == "INELIGIBLE" and why in SAMPLE_REFUSALS:
        label = "EXPECTED_REFUSAL_OBSERVED"
    elif verdict == "INELIGIBLE":
        label = "UNEXPECTED_REFUSAL_REASON"
    else:
        label = "EXPECTED_REFUSAL_MISSING"
    return {"label": label, "campaign_stage": stage, "short_fields": short, "judge_verdict": verdict,
            "judge_why": why, "scientific_verdict": False}


def emit(result: dict, lane: str, exp_id: str, r=None) -> str | None:
    if result["label"] == "NOT_APPLICABLE":
        return None
    if r is None:
        from primordial.bus import bus
        r = bus.conn()
    return r.xadd(EVENTS, {"event": result["label"],
                           "json": json.dumps({**result, "lane": lane, "exp_id": exp_id, "ts": time.time()})})
