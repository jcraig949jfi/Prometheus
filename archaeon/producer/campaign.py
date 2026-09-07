"""The M-ELIGIBLE campaign request builder.

    2 declared comparison groups x 2 arms x 2 worlds x 4 ORDERED observations
    = 8 queue rows, each spec_version 3 with repeat.count = 4
    = 8 worlds, 32 observations

Builds the requests Archaeon owes the campaign, validates them against
Vivarium's live validator, and -- only on an explicit ``--issue`` -- registers
them as one candidate set of eight, all retained, with ``family_id`` and
``arm_id`` in the queue's provenance columns and ``source_reason='human'``:
the operator chose to run this family, not a fossil.

The one thing this module deliberately does NOT do is make the arms legible in
the engine's own record. That needs the arm contract Daedalus and Vivarium
currently disagree on (``roles/Daedalus/INBOX_ARCHAEON_ARM_KEY_CONFLICT.md``).
Until it is settled, the family will fossilize its OBSERVATIONS with full
provenance in the queue, and Stage 0 will still report the arms as
ungroupable from the substrate alone. ``--check`` says so explicitly.

Authentic variation, per the operator: a constant per-repeat seed would make
the four observations identical and the within-world features degenerate by
construction. ``seed_derivation`` is ``sha256_index`` and the arms differ by an
execution parameter (``length`` 24 vs 28), so the contrast is a real condition
and not a label.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any, Dict, List, Optional

from .. import config as cfg
from .. import vivqueue as vq
from . import contract, specbuild

CAMPAIGN_ID = "M-ELIGIBLE-1"
FAMILIES = ("fam-ME1-A", "fam-ME1-B")
ARMS = {"arm-a": {"length": 24}, "arm-b": {"length": 28}}
WORLDS_PER_ARM = 2
OBSERVATIONS_PER_WORLD = 4
SEED_ROOT_BASE = 910_000


def _seed_root(i: int) -> int:
    return SEED_ROOT_BASE + i


def _bits(seed_root: int, length: int) -> str:
    """A deterministic candidate per world, derived from the world's own seed
    so the plan is re-derivable and carries no hidden choice."""
    h = hashlib.sha256("bits:{}:{}".format(seed_root, length).encode()).digest()
    return "".join(str((h[i // 8] >> (i % 8)) & 1) for i in range(length))


def plan() -> List[Dict[str, Any]]:
    """The eight requests, in issue order. Pure; no I/O."""
    rows: List[Dict[str, Any]] = []
    i = 0
    for fam in FAMILIES:
        for arm, cond in ARMS.items():
            for w in range(WORLDS_PER_ARM):
                i += 1
                sr = _seed_root(i)
                length = cond["length"]
                spec = specbuild.build({"bits": _bits(sr, length),
                                        "length": length, "seed_root": sr})
                # spec v3: repeat is REQUIRED and every axis declared
                spec["spec_version"] = 3
                spec["repeat"] = {
                    "count": OBSERVATIONS_PER_WORLD,
                    "order": "sequential",
                    "seed_derivation": "sha256_index",   # authentic variation
                    "state": "reset",
                    "budget": {"max_seconds": 120,
                               "max_observations": OBSERVATIONS_PER_WORLD * 2},
                }
                rows.append({"index": i, "family_id": fam, "arm_id": arm,
                             "world_ordinal": w, "seed_root": sr,
                             "length": length, "spec": spec,
                             "request_key": "{}-{:02d}".format(CAMPAIGN_ID, i)})
    return rows


def check(rows: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Validate every spec with Vivarium's validator; report the blockers."""
    rows = rows or plan()
    out: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "rows": len(rows),
                           "families": sorted({r["family_id"] for r in rows}),
                           "arms": sorted({r["arm_id"] for r in rows}),
                           "observations_planned":
                               len(rows) * OBSERVATIONS_PER_WORLD,
                           "invalid": [], "blockers": []}
    for r in rows:
        try:
            specbuild.validate(r["spec"])
        except specbuild.SpecInvalid as exc:
            out["invalid"].append({"index": r["index"], "reason": str(exc)[:300]})
    if out["invalid"]:
        out["blockers"].append(
            {"lane": "vivarium", "what": "spec v3 rejected by the live validator",
             "n": len(out["invalid"])})
    out["blockers"].append(
        {"lane": "daedalus+vivarium",
         "what": ("arm identity is not yet legible from the engine's record. "
                  "Operator's recommended ruling: arm is DESIGN provenance, "
                  "bound by the sealed family manifest, never in spec_hash "
                  "(same execution under labels A and B keeps one execution "
                  "hash; reassignment after commitment refused; PEW preserves "
                  "the binding). Pending Harmonia's confirmation and "
                  "Daedalus's binding."),
         "ref": "roles/Daedalus/INBOX_ARCHAEON_ARM_KEY_CONFLICT.md"})
    # Harmonia's ruling (5759518f0): the DESIGN OWNER must declare the three
    # levels before any power statement. Declared here, by the design's owner.
    out["levels"] = {
        "selected": "8 worlds: the 2 families x 2 arms x 2 worlds grid",
        "randomized": "WORLD. Each world receives one arm; arms differ by an "
                      "execution parameter (length 24 vs 28). n = 4 worlds "
                      "per arm across both families.",
        "analyzed": "WORLD (never finer). The 4 ordered observations within a "
                    "world are repeats and are summarised to one value per "
                    "world before any contrast. Under seed_derivation "
                    "sha256_index each repeat is scored against a different "
                    "derived target, so within-world variation is exchangeable "
                    "(Binomial(L,1/2)/L) and carries no arm information.",
        "power_note": "Harmonia measured 80% power only at d ~ 3.0 at this "
                      "n; M-ELIGIBLE establishes ELIGIBILITY of the frozen "
                      "features, not a contrast. Two families are two "
                      "conditions, not n = 2.",
        "declared_by": "archaeon (design owner)", "declared_on": "2026-09-07",
    }
    out["release_condition"] = (
        "sealed arm binding -> granted readback (LIVE v7 + Archaeon's own "
        "credentials returning the intended observations with census and "
        "family metadata) -> one complete arm-bound PEW round trip -> "
        "release M-ELIGIBLE. Check with `python -m "
        "archaeon.producer.readback_probe`.")
    out["ok_to_issue"] = not out["invalid"]
    out["note"] = ("32 rows alone do not guarantee eligibility or establish "
                   "S17 transfer; eligibility is reported by rerunning Stage 0 "
                   "unchanged after execution.")
    return out


def issue(conn, rows: Optional[List[Dict[str, Any]]] = None,
          config: Optional[cfg.ArchaeonConfig] = None) -> Dict[str, Any]:
    """Register the eight as one candidate set, all retained, human-issued."""
    rows = rows or plan()
    config = config or cfg.DEFAULT
    c = check(rows)
    if not c["ok_to_issue"]:
        raise RuntimeError("campaign does not validate: {}".format(c["invalid"]))
    cands = [vq.make_candidate(
        r["spec"], family_id=r["family_id"], arm_id=r["arm_id"],
        request_key=r["request_key"],
        source_evidence={"schema": "archaeon.campaign.v0",
                         "campaign": CAMPAIGN_ID,
                         "mode": "human",
                         "policy_version": "campaign.M-ELIGIBLE.v0",
                         "template_id": "campaign.M-ELIGIBLE-1",
                         "world_ordinal": r["world_ordinal"],
                         "selection_basis": "operator_directed_family",
                         "authority": ("Operator-directed seeding of the "
                                       "fossil record so the frozen S17 "
                                       "primitive has structure to read. Not "
                                       "a fossil-directed proposal; not a "
                                       "scientific claim."),
                         "upstream_selection_history": "UNKNOWN"})
             for r in rows]
    # Every candidate is selected: register all, cancel none. vivqueue.submit
    # selects one; issue each as its own set-of-one is dishonest (they are one
    # family), so we submit the set once per row with the same candidate_set_id
    # and no cancellation, via the human path (no cadence, no ordinal).
    csid = "cs-" + CAMPAIGN_ID.lower()
    results = []
    for i, cand in enumerate(cands):
        res = vq.submit(conn, candidates=[cand], selected_index=0,
                        source_reason="human", created_by="archaeon",
                        config=config, candidate_set_id=csid)
        results.append(res["selected_experiment_id"])
    return {"campaign": CAMPAIGN_ID, "candidate_set_id": csid,
            "experiment_ids": results, "registered": len(results)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.campaign")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--issue", action="store_true",
                    help="register the eight requests (operator act)")
    a = ap.parse_args(argv)
    if a.plan:
        print(json.dumps(plan(), indent=2, default=str))
        return 0
    if a.issue:
        from evidence_wiki.ew import db as ewdb
        conn = ewdb.connect()
        try:
            print(json.dumps(issue(conn), indent=2, default=str))
        finally:
            conn.close()
        return 0
    print(json.dumps(check(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
