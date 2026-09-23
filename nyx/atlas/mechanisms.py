"""The MECHANISM LEDGER (operator directive 2026-09-19b s2).

A MECHANISM IS NOT A PACKET. A packet is an evidence-bearing experiment; a mechanism is a persistent
identity that accumulates evidence across packets. One mechanism may gather many packets; one packet
may carry several predictions about one mechanism. Neither multiplies the mechanism count.

The headline scoreboard count -- MECHANISMS_THAT_SURVIVED_TRANSPLANT -- counts UNIQUE mechanism_ids,
never packets and never supported clauses.

Ledger file: nyx/atlas/gates/MECHANISMS.json   (beside the packet/handoff ledger, gates/LEDGER.json)
    python -m nyx.atlas.mechanisms        # validate + print the ledger summary
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

SCHEMA = "nyx.mechanism_ledger/1"
ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "gates" / "MECHANISMS.json"

# a mechanism's standing, from the evidence so far. PROPOSED is the honest default: located and
# bounded, but nothing independent has tested it yet.
DISPOSITIONS = (
    "PROPOSED",            # cut to a boundary; no independent adjudication yet
    "EVIDENCE_SUPPORTED",  # at least one independent ruling supported the boundary/claim
    "CONTESTED",           # supporting and counter evidence both stand
    "FALSIFIED",           # an independent ruling falsified the mechanism claim itself
    "WITHDRAWN",           # Nyx retracted it (not counted as isolated)
    "SURVIVED_TRANSPLANT", # an independent ecology reproduced its predicted effect
)

# Harmonia's A/B/C dispositions (directive 2026-09-19b s1) plus the honest pre-test states.
OBSERVER_DEPENDENCE = (
    "UNKNOWN",                  # not yet measured through a second observer
    "NOT_APPLICABLE",           # the mechanism has no observer in its boundary
    "OBSERVER_STABLE",          # A: the phenomenon substantially survives the native observer
    "STRUCTURED_DEPENDENCE",    # B: particular classes/lineages systematically gain or lose status
    "RECONSTRUCTION_SPECIFIC",  # C: it disappears under the native observer; the claim stops
)

TRANSPLANT_OUTCOMES = ("OFFERED", "ACCEPTED", "SUPPORTED", "FAILED", "INDETERMINATE")

REQUIRED = ("mechanism_id", "source_lineage", "minimal_executable_organ", "proposed_behavior",
            "predicted_intervention", "falsifier", "evidence_packets", "counterevidence_packets",
            "observer_dependence", "transplant_history", "current_disposition")


def validate(led: dict) -> List[str]:
    """Return a list of problems; empty means the ledger is well formed."""
    bad: List[str] = []
    if led.get("schema") != SCHEMA:
        bad.append(f"schema must be {SCHEMA}")
    seen = set()
    for i, m in enumerate(led.get("mechanisms", [])):
        tag = m.get("mechanism_id", f"#{i}")
        for k in REQUIRED:
            if k not in m:
                bad.append(f"{tag}: missing {k}")
        mid = m.get("mechanism_id")
        if mid in seen:
            bad.append(f"{tag}: duplicate mechanism_id (identity must be unique -- that is the point)")
        seen.add(mid)
        if m.get("current_disposition") not in DISPOSITIONS:
            bad.append(f"{tag}: current_disposition {m.get('current_disposition')!r} outside {DISPOSITIONS}")
        if m.get("observer_dependence") not in OBSERVER_DEPENDENCE:
            bad.append(f"{tag}: observer_dependence {m.get('observer_dependence')!r} outside {OBSERVER_DEPENDENCE}")
        org = m.get("minimal_executable_organ") or {}
        if not isinstance(org, dict) or not org.get("cut_id") or not org.get("boundary"):
            bad.append(f"{tag}: minimal_executable_organ needs cut_id and boundary (a mechanism without an "
                       f"executable boundary is a name, not a mechanism)")
        if not str(m.get("falsifier", "")).strip():
            bad.append(f"{tag}: falsifier must say what observation would kill it")
        for t in m.get("transplant_history", []):
            if t.get("outcome") not in TRANSPLANT_OUTCOMES:
                bad.append(f"{tag}: transplant outcome {t.get('outcome')!r} outside {TRANSPLANT_OUTCOMES}")
            if not t.get("receiving_ecology"):
                bad.append(f"{tag}: a transplant row needs the receiving_ecology it was tried in")
        # a mechanism that claims to have survived transplant must carry the receipt
        if m.get("current_disposition") == "SURVIVED_TRANSPLANT" and not any(
                t.get("outcome") == "SURVIVED" or t.get("outcome") == "SUPPORTED" for t in m.get("transplant_history", [])):
            bad.append(f"{tag}: disposition SURVIVED_TRANSPLANT with no SUPPORTED transplant row")
    return bad


def load(path: Path = LEDGER) -> dict:
    if not path.exists():
        return {"schema": SCHEMA, "mechanisms": []}
    return json.loads(path.read_text(encoding="utf-8"))


def counts(led: dict) -> dict:
    """The scoreboard's mechanism block. Every count is over UNIQUE mechanism_ids (s2)."""
    ms = led.get("mechanisms", [])
    isolated = [m for m in ms if m.get("current_disposition") != "WITHDRAWN"]
    def _supported(m):
        return [t for t in m.get("transplant_history", []) if t.get("outcome") == "SUPPORTED"]
    return {
        "mechanisms_registered": len({m.get("mechanism_id") for m in ms}),
        "mechanisms_isolated": len({m.get("mechanism_id") for m in isolated}),
        "mechanisms_evidence_supported": len({m.get("mechanism_id") for m in isolated
                                              if m.get("current_disposition") in ("EVIDENCE_SUPPORTED", "SURVIVED_TRANSPLANT")}),
        "mechanisms_falsified": len({m.get("mechanism_id") for m in ms if m.get("current_disposition") == "FALSIFIED"}),
        "observer_stable_mechanisms": len({m.get("mechanism_id") for m in isolated
                                           if m.get("observer_dependence") == "OBSERVER_STABLE"}),
        "observer_dependence_unresolved": len({m.get("mechanism_id") for m in isolated
                                               if m.get("observer_dependence") == "UNKNOWN"}),
        # transplant EVENTS vs the headline, which is unique mechanism ids
        "successful_independent_transplants": sum(len(_supported(m)) for m in isolated),
        "mechanisms_that_survived_transplant": len({m.get("mechanism_id") for m in isolated if _supported(m)}),
    }


def main() -> int:
    led = load()
    bad = validate(led)
    for b in bad:
        print("INVALID:", b)
    c = counts(led)
    print(json.dumps(c, indent=1))
    for m in led.get("mechanisms", []):
        print(f"  {m['mechanism_id']:34s} {m['current_disposition']:20s} observer={m['observer_dependence']:24s} "
              f"evidence={len(m.get('evidence_packets', []))} counter={len(m.get('counterevidence_packets', []))}")
    print(f"{len(led.get('mechanisms', []))} mechanisms, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
