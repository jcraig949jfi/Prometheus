"""C3: the first CA corpus, as a human-issued batch (Track B, 2026-09-10).

Builds the rows of packet v2.1 §2.10 against the `ca_density_v0` contract
(Vivarium e43a6c7f2 wraps herakles/evca): the six historical genomes, the
constant-output and centre-only baselines, the transform nulls, and the
random-rule acquisition. Every row shares the same seed_root, so Vivarium's
per-repeat seed derivation gives every rule the SAME four IC samples --
paired by construction, the unit for accuracy being the IC sample.

`plan()` is pure. `check()` validates each spec with Vivarium's validator
when the kind is registered in the tree it runs in, and says plainly when it
is not (the wrapper lives on Vivarium's branch until landed). `issue()` is
the operator's act and registers the batch as one candidate set, all
retained, source_reason='human', no cadence ordinal -- the same path as
M-ELIGIBLE.

Encoding (Herakles, re-earned by test): bit k from the LEFT of the 32-hex
string is the output for neighbourhood index k, where k = sum cell[i+j] *
2^(3-j) over j = -3..3 (leftmost cell is the MSB of k). The centre cell is
bit 3 of k (value 8).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any, Dict, List, Optional

from .. import config as cfg
from .. import vivqueue as vq
from . import specbuild

CAMPAIGN_ID = "C3-1"
KIND = "ca_density_v0"
SEED_ROOT = 930_001            # one seed_root -> the same four IC samples for every rule
N_CELLS, RADIUS, STEPS, N_IC = 149, 3, 320, 100
IC_MODE, IC_DENSITIES = "bernoulli", [0.5]
SUCCESS = "stable"
N_RANDOM = 120                  # Harmonia be9c22959 F-4: multinomial region counts; E[eligible] = 9.2 of 10
REPEAT = {"count": 4, "order": "sequential", "seed_derivation": "sha256_index",
          "state": "reset", "budget": {"max_seconds": 600, "max_observations": 8}}
HISTORICAL = ("maj", "exp", "par", "particle1", "particle2", "GKL")
TRANSFORMS = ("reflect", "complement", "reflect_complement")


def _hex_from_bits_left_msb(bits: List[int]) -> str:
    assert len(bits) == 128
    n = 0
    for b in bits:                 # bit k from the LEFT is neighbourhood k
        n = (n << 1) | (b & 1)
    return "{:032x}".format(n)


def centre_only_rule(f0: int, f1: int) -> str:
    """The 128-entry table whose output depends only on the centre cell
    (bit 3 of the neighbourhood index): centre 0 -> f0, centre 1 -> f1."""
    return _hex_from_bits_left_msb([f1 if (k >> 3) & 1 else f0 for k in range(128)])


CONSTANT_RULES = {"all_zero": "0" * 32, "all_one": "f" * 32}
CENTRE_RULES = {"centre_00": centre_only_rule(0, 0), "centre_01": centre_only_rule(0, 1),
                "centre_10": centre_only_rule(1, 0), "centre_11": centre_only_rule(1, 1)}


def historical_rules() -> Dict[str, str]:
    from herakles.evca import genomes as G      # on main since 0641c567b
    return {name: G.rule_hex(name) for name in HISTORICAL}


def random_rule(i: int) -> str:
    h = hashlib.sha256("c3.random_rule|{}|{}".format(SEED_ROOT, i).encode()).digest()
    return h[:16].hex()


def _spec(rule_hex: str, transform: str, hypothesis: str) -> Dict[str, Any]:
    return {
        "spec_version": 3,
        "world": {"seed_root": SEED_ROOT},
        "hypothesis": hypothesis,
        "prediction": {"basis": "packet v2.1 s2.9: guarantees G1-G3, hypotheses H1-H3; "
                                "nothing here predicts a per-rule accuracy",
                       "success_criterion": SUCCESS},
        "work": {"kind": KIND, "payload": {
            "rule_hex": rule_hex, "radius": RADIUS, "n_cells": N_CELLS, "steps": STEPS,
            "n_ic": N_IC, "ic_mode": IC_MODE, "ic_density_set": IC_DENSITIES,
            "transform": transform, "success_criterion": SUCCESS}},
        # accuracy above the density prior is the only scalar rule that is
        # attainable for every arm; the science is in the ANALYSIS (X1)
        "outcome_rule": {"field": "accuracy", "op": ">", "value": 0.5,
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE"},
        "pew": {"required": True,
                "encounter_id": "ENC-archaeon-c3-" + hashlib.sha256(
                    "{}|{}|{}".format(rule_hex, transform, SEED_ROOT).encode()).hexdigest()[:16],
                "players": []},
        "repeat": dict(REPEAT),
    }


def plan() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    i = 0

    def add(arm, label, rule_hex, transform, hyp):
        nonlocal i
        i += 1
        rows.append({"index": i, "family_id": "fam-C3-1", "arm_id": arm, "label": label,
                     "rule_hex": rule_hex, "transform": transform,
                     "request_key": "{}-{:03d}".format(CAMPAIGN_ID, i),
                     "spec": _spec(rule_hex, transform, hyp)})

    hist = historical_rules()
    for name, rh in hist.items():
        add("C3-hist", name, rh, "none", "historical genome {} under the family default protocol".format(name))
    for name, rh in {**CONSTANT_RULES, **CENTRE_RULES}.items():
        add("C3-base", name, rh, "none", "baseline rule {}: constant-output or centre-only".format(name))
    for name, rh in hist.items():
        for t in TRANSFORMS:
            add("C3-null", "{}:{}".format(name, t), rh, t,
                "G1: {} under {} has an identical correctness mask (exact symmetry)".format(name, t))
    for j in range(N_RANDOM):
        add("C3-acq", "random_{:03d}".format(j), random_rule(j), "none",
            "random rule table {} (the frozen random control of the CA family)".format(j))
    return rows


def check(rows: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    rows = rows or plan()
    arms: Dict[str, int] = {}
    for r in rows:
        arms[r["arm_id"]] = arms.get(r["arm_id"], 0) + 1
    out: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "rows": len(rows), "arms": arms,
                           "observations_planned": len(rows) * REPEAT["count"],
                           "shared_ic_samples": REPEAT["count"],
                           "independent_unit_for_accuracy": "IC sample (shared across rules); never the rule or the repeat",
                           "kind_registered": None, "invalid": [], "blockers": []}
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    from viv import kinds as vk
    k = vk.get(KIND)
    out["kind_registered"] = bool(k and k.implemented)
    if not out["kind_registered"]:
        out["blockers"].append({"lane": "vivarium", "what": "ca_density_v0 is not registered in this tree; "
                                "the wrapper (e43a6c7f2) is on the campaign branch until landed on main"})
        return out
    for r in rows:
        try:
            specbuild.validate(r["spec"])
        except specbuild.SpecInvalid as exc:
            out["invalid"].append({"index": r["index"], "reason": str(exc)[:240]})
    if out["invalid"]:
        out["blockers"].append({"lane": "archaeon", "what": "specs rejected by Vivarium's validator", "n": len(out["invalid"])})
    out["ok_to_issue"] = not out["invalid"]
    return out


def issue(conn, rows: Optional[List[Dict[str, Any]]] = None, config=None) -> Dict[str, Any]:
    rows = rows or plan(); config = config or cfg.DEFAULT
    c = check(rows)
    if not c.get("ok_to_issue"):
        raise RuntimeError("C3 does not validate or the kind is absent: {}".format(c["blockers"] or c["invalid"]))
    csid = "cs-" + CAMPAIGN_ID.lower()
    ids = []
    for r in rows:
        cand = vq.make_candidate(r["spec"], family_id=r["family_id"], arm_id=r["arm_id"],
                                 request_key=r["request_key"],
                                 source_evidence={"schema": "archaeon.campaign.v0", "campaign": CAMPAIGN_ID,
                                                  "mode": "human", "policy_version": "campaign.C3.v0",
                                                  "template_id": "campaign.C3-1", "label": r["label"],
                                                  "selection_basis": "operator_directed_family",
                                                  "authority": "first CA corpus: acquisition, baselines, "
                                                               "exact-symmetry nulls, and the frozen random "
                                                               "control; not a fossil-directed proposal",
                                                  "upstream_selection_history": "UNKNOWN"})
        res = vq.submit(conn, candidates=[cand], selected_index=0, source_reason="human",
                        created_by="archaeon", config=config, candidate_set_id=csid)
        ids.append(res["selected_experiment_id"])
    return {"campaign": CAMPAIGN_ID, "candidate_set_id": csid, "experiment_ids": ids, "registered": len(ids)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.campaign_c3")
    ap.add_argument("--plan", action="store_true"); ap.add_argument("--issue", action="store_true")
    a = ap.parse_args(argv)
    if a.plan:
        print(json.dumps([{k: v for k, v in r.items() if k != "spec"} for r in plan()], indent=1)); return 0
    if a.issue:
        from evidence_wiki.ew import db as ewdb
        conn = ewdb.connect()
        try:
            print(json.dumps(issue(conn), indent=2, default=str))
        finally:
            conn.close()
        return 0
    print(json.dumps(check(), indent=2, default=str)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
