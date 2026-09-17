"""SWARM_R7 O8 (A ruling on E-R7-1-val-negative PASS, fixed before any further data): the Clause B control's
FALSE-PASS rate, measured before the live w14 -> w13 pair may run.

  draws      K = 40 independent planted-negative draws at EVIDENCE_N_v1 32/4/8 (families 4200, 2101, 3303, 5501 x 8
             run seeds), recipient w13 train128_held64, VAL7 budget (gens 50, batch 64) -- the cheap planted pair E-R7-1
             re-validated. Draw d:
               donor      16 untrained init genomes from PCG64([F, DONOR_TAG0 + d, rs, 13])  (fresh tag per draw; disjoint
                          from 1707 and from every stream tag used before: 1501-1507, 1701-1707, 7707)
               run seeds  RUN_SEED0 + 8 d .. + 8 (disjoint per draw and from every run seed set used before: 0..31,
                          100..107), so filler / mutation / sham streams are fresh per draw too (independent draws)
               scratch, sham, check_b v2   exactly E-R7-1's code (transfer_v2.validation_job path, mode "negative")
             One worker job per draw, non-checkpointable, SMOKE/PRODUCTION <= 900 s.
  decision   from rows (decide): completed = draws with a check_b row; false_pass = those judged PASS.
               completed == 40:  INSTRUMENT_ADMISSIBLE iff false_pass <= 5, else INSTRUMENT_NOT_VALIDATED
               completed <  40:  PENDING (INDETERMINATE when called with at_no_new_work=True)
             Errored draws are counted as error rows and never replace a completed draw.
  gate       the live pair runs ONLY after INSTRUMENT_ADMISSIBLE; otherwise PC "Clause B control false-positive rate".

    python -m primordial.fabric.worker submit E primordial.cohorts.e.r7_clauseb_calibration:draw_job \\
        --exp E-R7-O8-calibration --rows primordial/ledger/rows/E/E-R7-O8-calibration.jsonl --ttl-cpu-s 1200 --kwargs '{"draw": 0}'
"""
from __future__ import annotations

import json
import pathlib

from primordial.cohorts.e import transfer_v2 as V

K = 40
MAX_FALSE_PASS = 5
DONOR_TAG0 = 27000
RUN_SEED0 = 2000
USED_TAGS = frozenset(range(1501, 1508)) | frozenset(range(1701, 1708)) | {7707}
USED_RUN_SEEDS = frozenset(range(0, 32)) | frozenset(range(100, 108))
EXP = "E-R7-O8-calibration"
ROWS = "primordial/ledger/rows/E/E-R7-O8-calibration.jsonl"
ADMISSIBLE, NOT_VALIDATED, PENDING, INDETERMINATE = (
    "INSTRUMENT_ADMISSIBLE", "INSTRUMENT_NOT_VALIDATED", "PENDING", "INDETERMINATE")


def plan(k: int = K) -> list[dict]:
    """The committed seed list: one entry per draw."""
    return [{"draw": d, "donor_tag": DONOR_TAG0 + d, "run_seeds": list(range(RUN_SEED0 + 8 * d, RUN_SEED0 + 8 * d + 8))}
            for d in range(k)]


class _Tagged:
    """Wraps the worker ctx: stamps the draw on every emitted row."""

    def __init__(self, ctx, draw: int, tag: int):
        self.ctx, self.draw, self.tag = ctx, int(draw), int(tag)

    def __getattr__(self, name):
        return getattr(self.ctx, name)

    def emit(self, row: dict) -> None:
        self.ctx.emit(dict(row, calibration="O8", draw=self.draw, donor_tag=self.tag))


def draw_job(ctx, draw: int, gens: int = V.VAL7["gens"], batch: int = V.VAL7["batch"], pressure: str = V.VAL7["pressure"],
             families=V.FAMILIES7, campaign_stage: str = "PRODUCTION"):
    p = plan()[int(draw)]
    exp = f"{EXP}-d{int(draw):02d}"
    tagged = _Tagged(ctx, p["draw"], p["donor_tag"])
    from primordial.metric import floors as F
    from primordial.score.transfer_b import check_b
    run_seeds = p["run_seeds"]
    n_train = len(F.PRESSURES[pressure])
    base = dict(V.base_row("random", 13, 13, "linear", pressure, gens, batch, n_train, "O8-negative"),
                campaign_stage=campaign_stage, expected="NOT_PASS", **V.sample_block(list(families), run_seeds))
    st, per, keys = V._runs(tagged, "random", 13, 13, "linear", list(families), run_seeds, gens, batch, n_train, base,
                            random_tag=p["donor_tag"])
    summ = V.summarize(base, per, keys, [st["wall"][k] for k in keys])
    tagged.emit(summ)
    rows = [dict(r, exp_id=exp) for k in keys for r in st["done"][k].values()] + [dict(summ, exp_id=exp)]
    got = check_b(rows)
    verdict = got["pairs"][0]["verdict"] if got["pairs"] else "INDETERMINATE"
    tagged.emit({"kind": "check_b", "status": "record", "exp_id": exp, "control_version": V.CONTROL_VERSION,
                 "mode": "negative", "expected": "NOT_PASS", "verdict": verdict, **V.sample_block(list(families), run_seeds),
                 **got})


def decide(rows: list[dict], k: int = K, at_no_new_work: bool = False) -> dict:
    chk = {}
    errors = 0
    for x in rows:
        if x.get("calibration") != "O8":
            continue
        if x.get("kind") == "check_b" and x.get("draw") is not None:
            chk.setdefault(int(x["draw"]), x)                              # the first check_b row per draw counts
        if x.get("status") in ("aborted", "timeout"):
            errors += 1
    completed = len(chk)
    false_pass = sum(1 for x in chk.values() if x.get("verdict") == "PASS")
    indeterminate = sum(1 for x in chk.values() if x.get("verdict") == "INDETERMINATE")
    if completed >= k:
        decision = ADMISSIBLE if false_pass <= MAX_FALSE_PASS else NOT_VALIDATED
    else:
        decision = INDETERMINATE if at_no_new_work else PENDING
    return {"rule": "SWARM_R7 O8", "k": k, "max_false_pass": MAX_FALSE_PASS, "completed": completed,
            "false_pass": false_pass, "judged_indeterminate": indeterminate, "error_rows": errors,
            "draws_pass": sorted(d for d, x in chk.items() if x.get("verdict") == "PASS"), "decision": decision,
            "live_pair_allowed": decision == ADMISSIBLE}


def decide_file(path=ROWS, at_no_new_work: bool = False) -> dict:
    rows = [json.loads(l) for l in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return decide(rows, at_no_new_work=at_no_new_work)
