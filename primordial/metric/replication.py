"""G-R6-3 (round 6 R6-BUILD, builder G): the REPLICATION trigger (SWARM_R6 O1).

The first time eligibility reports a NEW SURVIVED cell, code publishes ONE record on pm:replication. B reads it; A does
not relay. The recipe is the FROZEN B-R5-1 recipe -- no hyperparameter changes:

  code           primordial/cohorts/b/r5_1_candidate.py + b1_qlinear.py at RECIPE_CODE_SHA
  layout rule    QLin(gen_seed, bits=4, acts=4): int4 linear + a4 nibble codebook, byte count derived from the cell's
                 (D, A, W) by the same function B-R5-1 used (conductor 1789479784674-0: freeze the RULE, not the dims)
  search budget  ABSOLUTE search_generations 800, search_batch 128 (search_evals 102,400 per run), not rescaled
  sample         runs_total 32, rng_family_count 4, runs_per_family 8
  readout        top1_train;  judge  qd_ledger.check_r4
  applicability  APPLICABLE iff the layout rule instantiates on the cell without error and without any parameter
                 change (the instantiated genome_bytes is recorded); INAPPLICABLE otherwise, with the reason named --
                 not a fail, not a retune.

Idempotent: a Redis SETNX key pm:replication:published:<world>|<pressure> guards the XADD, so re-running the trigger
(or two processes racing) publishes at most one record per cell. The recipe's origin cell (w13 train128_held64) never
triggers a replication of itself.
"""
from __future__ import annotations

import json
import subprocess
import time

from primordial.metric import screen as SC

STREAM = "pm:replication"
PUBLISHED = "pm:replication:published:{}|{}"
RECIPE_ID = "B-R5-1"
RECIPE_CODE_SHA = "c2e9b5ec3"
RECIPE_FILES = ("primordial/cohorts/b/r5_1_candidate.py", "primordial/cohorts/b/b1_qlinear.py")
ORIGIN = ("w13", "train128_held64")
RECIPE = {
    "id": RECIPE_ID, "frozen_code_sha": RECIPE_CODE_SHA, "code_files": list(RECIPE_FILES),
    "fn": "primordial.cohorts.b.r5_1_candidate:job",
    "genome_layout_rule": "b1_qlinear.QLin(gen_seed, bits=4, acts=4): int4 linear params + a4 nibble codebook",
    "bits": 4, "acts": 4,
    "search_budget": {"search_generations": 800, "search_batch": 128, "search_evals": 102_400,
                      "rule": "absolute; not rescaled by genome size (conductor 1789479784674-0)"},
    "sample": {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8, "families": [4200, 2101, 3303, 5501]},
    "readout": "top1_train", "judge": "primordial.ops.qd_ledger.check_r4", "origin_cell": list(ORIGIN),
    "origin_rows": "primordial/ledger/rows/B/B-R5-1-cand-int4a4-w13-train128.jsonl (4e69568e8)",
}


def applicability(gen_seed: int) -> dict:
    """Instantiate the frozen layout rule on the cell. -> {applicable, genome_bytes, D, A, W, reason}."""
    try:
        from primordial.cohorts.b.b1_qlinear import QLin
        q = QLin(int(gen_seed), RECIPE["bits"], RECIPE["acts"])
        return {"applicable": True, "genome_bytes": int(q.glen), "D": int(q.D), "A": int(q.A), "W": int(q.W), "reason": None}
    except Exception as e:
        return {"applicable": False, "genome_bytes": None, "reason": f"{type(e).__name__}: {e}"}


def predicate_template(world: str, pressure: str, app: dict) -> dict:
    return {"exp_id": f"B-REPL-{RECIPE_ID}-{world}-{pressure}", "experiment_class": "REPLICATION",
            "campaign_stage": "REPLICATION", "recipe": RECIPE_ID, "frozen_code_sha": RECIPE_CODE_SHA,
            "cell": {"world": world, "pressure": pressure}, "genome_bytes": app.get("genome_bytes"),
            "metric": {"field": "verdict", "judge": RECIPE["judge"], "readout": RECIPE["readout"]},
            "comparator": "==", "threshold": "PASS", **RECIPE["sample"],
            "search_budget": RECIPE["search_budget"], "prior": None,
            "note": "fill prior and post as PREDICATE before any run; no parameter of the recipe may change"}


def survived_cells(doc: dict) -> list[tuple[str, str]]:
    k = SC.vkey(doc["q1_floor_policy"], doc["q2_policy"])
    return sorted((c["world"], c["pressure"]) for c in doc["cells"] if c["verdicts"][k]["verdict"] == "SURVIVED")


def frozen_code_intact(root=None) -> bool:
    """True iff the recipe files are byte-identical to RECIPE_CODE_SHA in the working tree."""
    from primordial.metric.r16 import ROOT
    q = subprocess.run(["git", "-C", str(root or ROOT), "diff", "--quiet", RECIPE_CODE_SHA, "--", *RECIPE_FILES],
                       capture_output=True)
    return q.returncode == 0


def publish_new_survivors(r, doc: dict, source: str = "eligibility", now: float | None = None) -> list[dict]:
    """Publish one pm:replication record per SURVIVED cell not yet published (origin excluded). -> the records
    published by THIS call (empty when nothing is new)."""
    out = []
    for world, pressure in survived_cells(doc):
        if (world, pressure) == ORIGIN:
            continue
        if not r.set(PUBLISHED.format(world, pressure), json.dumps({"ts": now or time.time()}), nx=True):
            continue
        gs = int(world[1:])
        app = applicability(gs)
        rec = {"kind": "REPLICATION_TRIGGER", "cell": {"world": world, "pressure": pressure, "gen_seed": gs},
               "source": source, "detected_ts": round(now or time.time(), 3), "recipe": RECIPE,
               "applicability": "APPLICABLE" if app["applicable"] else "INAPPLICABLE", "layout": app,
               "predicate_template": predicate_template(world, pressure, app)}
        rec["stream_id"] = r.xadd(STREAM, {"json": json.dumps(rec, sort_keys=True)})
        out.append(rec)
    return out


def records(r) -> list[dict]:
    return [json.loads(f["json"]) | {"stream_id": mid} for mid, f in r.xrange(STREAM)]
