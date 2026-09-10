"""H5 alpha on eca_rule_eval_v1 (Track C).

Vivarium's kind reports the OBSERVABLE (terminal-behaviour digest and the
equivalence class at the payload's scope), never a score. That fixes what
the H5 alpha on this kind is: ONE exhaustive campaign of the 256 rules at
the fixture scope (7-ring, 8 steps) establishes the rule -> class map on
the live consumer; every H5 quantity (reach, neutrality, accessible
variation per decoder, the direct-vs-permuted access gap) is then exact
producer-side arithmetic over that live map (archaeon/producer/h5_reference,
h5_decoders), collapsed to classes. Nothing adaptive; a decoder is applied
to genomes offline and the phenotype is a rule number.

Not issued without the operator's word. 256 rows, one observation each.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence

from . import specbuild

KIND = "eca_rule_eval_v1"
CAMPAIGN_ID = "H5-1"
SEED_ROOT = 950_001
N_CELLS = 7
STEPS = 8
SCOPE = "terminal behaviour at {} steps on the {}-ring".format(STEPS, N_CELLS)


def spec_for(rule: int) -> Dict[str, Any]:
    return {"spec_version": 3, "world": {"seed_root": SEED_ROOT},
            "hypothesis": "rule {} at the fixture scope: the live consumer reproduces the published class".format(rule),
            "prediction": None,
            "work": {"kind": KIND, "payload": {"rule_number": rule, "n_cells": N_CELLS, "steps": STEPS}},
            "outcome_rule": {"field": "on_fixture_scope", "op": "==", "value": True,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE", "aggregate": "first"},
            "pew": {"required": True,
                    "encounter_id": "ENC-archaeon-h5-" + hashlib.sha256("{}|{}|{}|{}".format(rule, N_CELLS, STEPS, SEED_ROOT).encode()).hexdigest()[:16],
                    "players": []},
            "repeat": {"count": 1, "order": "sequential", "seed_derivation": "constant",
                       "state": "reset", "budget": {"max_seconds": 120, "max_observations": 1}}}


def plan() -> List[Dict[str, Any]]:
    return [{"index": r + 1, "family_id": "fam-H5-1", "arm_id": "map", "rule": r, "label": "rule_{:03d}".format(r),
             "request_key": "{}-{:03d}".format(CAMPAIGN_ID, r), "spec": spec_for(r)} for r in range(256)]


def check(rows: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    rows = rows or plan()
    out: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "rows": len(rows), "scope": SCOPE, "kind_registered": None,
                           "invalid": [], "blockers": []}
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    from viv import kinds as vk
    k = vk.get(KIND)
    out["kind_registered"] = bool(k and k.implemented)
    if not out["kind_registered"]:
        out["blockers"].append({"lane": "vivarium", "what": "eca_rule_eval_v1 is not registered in this tree"})
        return out
    for r in rows:
        try:
            specbuild.validate(r["spec"])
        except specbuild.SpecInvalid as exc:
            out["invalid"].append({"index": r["index"], "reason": str(exc)[:240]})
    from viv import executors as X
    ran, refused = {}, {}
    for r in (rows[0], rows[90], rows[255]):            # rule 0, rule 90, rule 255 executed offline
        try:
            o = X.run(r["spec"], seed=0)
            ran[r["label"]] = {"class_size": o.get("equivalence_class_size"), "on_fixture_scope": o.get("on_fixture_scope"),
                               "fixture_class_agrees": o.get("fixture_class_agrees")}
        except Exception as exc:                                 # noqa: BLE001
            refused[r["label"]] = "{}: {}".format(type(exc).__name__, str(exc)[:200])
    out["executor_preflight"] = {"ran": ran, "refused": refused}
    if out["invalid"]:
        out["blockers"].append({"lane": "archaeon", "what": "specs rejected by Vivarium's validator", "n": len(out["invalid"])})
    if refused:
        out["blockers"].append({"lane": "archaeon", "what": "executor refuses a payload", "detail": refused})
    out["ok_to_issue"] = not out["invalid"] and not refused
    return out


def live_class_map(results: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """From 256 live results, the rule -> class map (class id = smallest
    member, as the fixture), compared with the published fixture."""
    from . import h5_reference as R
    by_digest: Dict[str, List[int]] = {}
    for rule, res in results.items():
        by_digest.setdefault(res["behaviour_digest"], []).append(rule)
    live = {}
    for members in by_digest.values():
        cid = min(members)
        for m in members:
            live[m] = cid
    published = R.load_class_map()["equivalence"]
    return {"n_rules": len(live), "n_classes": len(set(live.values())), "equivalence": live,
            "agrees_with_published": live == published if len(live) == 256 else None,
            "disagreements": sorted(r for r in live if published.get(r) != live[r]),
            "scope": SCOPE}


def h5_readout(equivalence: Dict[int, int]) -> Dict[str, Any]:
    """The H5 quantities, exact, collapsed to the (live) classes."""
    from . import h5_decoders as H
    from . import h5_reference as R
    decs = {"direct": H.direct, "balanced_7": H.make_balanced(7), "scrambled_direct_3": H.make_scrambled(H.direct, 3)}
    out = {}
    for name, dec in decs.items():
        raw = R.exact_reference(dec)
        col = R.exact_reference(dec, equivalence=equivalence)
        out[name] = {"mean_reach_rules": raw["mean_reach"], "mean_reach_classes": col["mean_reach"],
                     "max_reach_rules": raw["max_reach"], "max_reach_classes": col["max_reach"],
                     "mean_neutral": raw.get("mean_neutral"), "digest_classes": col["reference_digest"]}
    out["construction_fact"] = "direct reach <= 8 and permuted up to 12 is analytic; only the excess over that bound is evidence (Harmonia)"
    out["scope"] = SCOPE
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.campaign_h5")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        print(json.dumps(check(), indent=1, default=str)); return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
