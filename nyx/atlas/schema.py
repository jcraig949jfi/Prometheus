"""nyx.atlas/0 -- the Atlas of Computational Behavior (Nyx, ATLAS PASS 01, 2026-09-13).

One schema family for every atlas artifact. Per fossil ONE file, nyx/atlas/fossils/<fossil_id>.json, holding the
whole-system record, the machinery tree (organs, each naming its parent), the rejected cuts, the pressures, the
composition edges INSIDE the fossil, the ancestry edges OUT of the fossil, and the residue accounting. Fingerprints
(measured) live under nyx/atlas/fingerprints/, recurrence candidates under nyx/atlas/recurrence/, blind-cut protocols
under nyx/atlas/blind/. build.py assembles the eleven directive artifacts from these; nothing is authored twice.

Evidence discipline. Every field that is not UNKNOWN carries a basis. A cut carries an evidence grade:
  METADATA     -- Techne's record only; no source opened (this is context, never anatomy)
  SOURCE_READ  -- Nyx read the named files
  EXECUTED     -- the fossil (or fragment) ran under Nyx's hand; receipt named
  INTERVENED   -- an ablation / intervention ran; receipt named
An organ is CANDIDATE until something beyond reading supports its boundary; ACCEPTED requires SOURCE_READ of the
boundary at minimum and says so; REJECTED cuts stay in the file with their reason (negative anatomy is evidence).
UNKNOWN is a legal value everywhere. Filling a field to satisfy the schema is the failure mode this file exists to
prevent: the validator accepts UNKNOWN and rejects invented vocabulary, not the other way round.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SCHEMA = "nyx.atlas/0"
ROOT = Path(__file__).resolve().parent

EVIDENCE_GRADES = ("METADATA", "SOURCE_READ", "EXECUTED", "INTERVENED")
BASIS = ("TECHNE_RECORD", "NYX_DERIVED", "SOURCE_READ", "EXECUTED", "UNKNOWN")
CUT_STATUS = ("CANDIDATE", "ACCEPTED", "REJECTED")
CUT_MODE = ("ANCESTRY_AWARE", "BLIND")
FOSSIL_CUT_STATE = ("NOT_CUT", "COARSE", "DEEP", "ORGAN0", "BLOCKED")
RESIDUE_STATES = ("EXPLAINED_BY_CURRENT_CUT", "PARTIALLY_EXPLAINED", "LARGE_RESIDUE", "CUT_INSTRUMENT_INSUFFICIENT", "NOT_CHECKED")
RECURRENCE_LEVELS = ("R0", "R1", "R2", "R3", "R4", "R5")
TRI = ("YES", "NO", "UNKNOWN", "N/A")

# provisional operational labels for composition edges (directive list); others allowed but flagged by the validator
COMPOSITION_LABELS = ("feeds", "gates", "retries", "selects", "updates", "stores", "forgets", "predicts", "verifies",
                      "schedules", "restores", "transforms", "competes", "suppresses", "triggers")
# ancestry relations mirror Techne's record vocabulary so the two graphs never share a label space by accident
# Techne owns the provenance vocabulary: import it, never copy it (a hand copy drifted on 2026-09-14 when
# spacewar-pdp1-1962 arrived with inspired_by). Nyx adds only the three relations Techne does not publish.
try:
    from techne.fossils.record import LINEAGE_RELATIONS as _TECHNE_RELATIONS
except Exception:  # validator must still run in a checkout without techne/
    _TECHNE_RELATIONS = ("forked_from", "derived_from", "rewrote", "superseded", "inspired_by", "port_of",
                         "reimplementation_of", "historical_version_of", "algorithm_from", "shares_ancestor_with")
ANCESTRY_RELATIONS = tuple(_TECHNE_RELATIONS) + ("predecessor_of", "successor_of", "rival_of")

REJECTION_REASONS = ("DISAPPEARS_UNDER_ABLATION", "INHERITED_FROM_RUNTIME_OR_LIBRARY", "DUPLICATES_A_CONTROL",
                     "EFFECT_FROM_ENVIRONMENT", "STATE_OBSERVATIONALLY_IRRELEVANT", "CANNOT_BE_ISOLATED",
                     "NAME_HAS_NO_EXECUTABLE_BOUNDARY", "BELOW_MEANINGFUL_GRAIN", "GENERIC_LANGUAGE_MECHANICS", "OTHER")

# the wind tunnel (directive list); a fingerprint records a measured response or N/A per intervention
INTERVENTIONS = ("input_permutation", "identifier_permutation", "representation_permutation", "state_reset",
                 "partial_state_reset", "state_corruption", "history_truncation", "delayed_feedback",
                 "duplicated_observation", "missing_observation", "noise", "resource_restriction",
                 "update_order_reversal", "randomized_update_order", "repeated_state", "cycles", "branching",
                 "adversarial_boundary", "compute_limit", "memory_limit")

# behavioural coverage dimensions (directive list). Values: a small vocabulary per dim, or UNMEASURED.
# Each organ carries coverage[dim] = {"value": ..., "basis": "READ"|"MEASURED"}; the map counts them separately.
COVERAGE_DIMS: Dict[str, tuple] = {
    "input_topology": ("SCALAR", "VECTOR", "SEQUENCE", "STREAM", "SET", "GRAPH", "TREE", "MATRIX", "EVENT", "MIXED"),
    "output_topology": ("SCALAR", "VECTOR", "SEQUENCE", "STREAM", "SET", "GRAPH", "TREE", "MATRIX", "EVENT", "DECISION", "MIXED"),
    "state_amount": ("NONE", "CONSTANT", "LOG", "LINEAR_IN_INPUT", "SUPERLINEAR", "UNBOUNDED"),
    "state_persistence": ("NONE", "PER_CALL", "PER_EPISODE", "PERSISTENT", "DURABLE"),
    "feedback": ("NONE", "OPEN_LOOP", "CLOSED_LOOP", "DELAYED_CLOSED_LOOP"),
    "memory": ("NONE", "LAST_VALUE", "WINDOW", "SUMMARY_STATISTIC", "FULL_HISTORY", "ARCHIVE"),
    "stochasticity": ("DETERMINISTIC", "SEEDED_RANDOM", "ENVIRONMENT_RANDOM", "ADVERSARIAL"),
    "update_topology": ("SINGLE_STEP", "SWEEP", "PARALLEL_ROUNDS", "EVENT_DRIVEN", "PRIORITY", "RECURSIVE"),
    "order_sensitivity": ("INVARIANT", "SENSITIVE", "PARTIALLY"),
    "resource_dependence": ("NONE", "TIME", "MEMORY", "BANDWIDTH", "COMPUTE", "SHARED_RESOURCE"),
    "failure_mode": ("NONE_KNOWN", "DIVERGES", "STALLS", "DEGRADES", "CORRUPTS", "STARVES", "OSCILLATES", "COLLAPSES"),
    "recovery": ("NONE", "SELF_RESETS", "RETRIES", "ROLLS_BACK", "DEGRADES_GRACEFULLY", "EXTERNAL_RESET"),
    "adaptation": ("NONE", "PARAMETER", "STRUCTURE", "POLICY"),
    "competition": ("NONE", "CONTENDS", "ARBITRATES", "ISOLATES"),
    "cooperation": ("NONE", "COORDINATES", "AGREES", "SHARES"),
    "hidden_state": ("NONE", "ESTIMATES", "ASSUMES", "IGNORES"),
    "uncertainty": ("NONE", "POINT", "INTERVAL", "DISTRIBUTION", "SAMPLE"),
    "representation_sensitivity": ("INVARIANT", "SENSITIVE", "UNKNOWN_BY_READ"),
    "temporal_horizon": ("INSTANT", "STEP", "WINDOW", "EPISODE", "UNBOUNDED"),
}
UNMEASURED = "UNMEASURED"

ORGAN_FIELDS = ("organ_id", "fossil_ancestry", "human_name", "human_interpretation", "mechanism", "input", "output",
                "state", "update", "assumptions", "interface", "dependencies", "parent_mechanism", "child_mechanisms",
                "composition_neighbors", "fitness_value_in_ancestor", "failure_landscape", "ablation", "decomposability",
                "composability", "human_prior", "control", "cheat", "observability", "intervention_readiness", "evidence",
                "confidence", "portability", "compatibility", "utility", "source_boundary", "status", "cut_mode", "depth",
                "coverage")
PRESSURE_FIELDS = ("pressure_id", "source_fossil", "source_evidence", "condition", "resource_or_constraint",
                   "failure_condition", "world_punishes", "world_rewards", "observable_consequence", "vacuity_condition",
                   "trivial_shortcuts", "cheat_control", "cost_class", "purpose_separated_from_pressure")
WHOLE_SYSTEM_FIELDS = ("FOSSIL_ID", "CANONICAL_NAME", "VERSION", "ERA", "HUMAN_SYSTEM", "HUMAN_PROBLEM",
                       "OBSERVED_HUMAN_CAPABILITY", "DOCUMENTED_ENVIRONMENTAL_PRESSURE", "LANGUAGE", "EXECUTION_MODEL",
                       "ANCESTRY", "KNOWN_PREDECESSORS", "KNOWN_SUCCESSORS", "KNOWN_RIVALS",
                       "KNOWN_HISTORICAL_DISPOSITION", "SOURCE_STATUS", "RUN_STATUS", "OBSERVABILITY", "ORACLE_STATUS",
                       "INTERVENTION_READINESS")


def _need(d: dict, keys, where: str, problems: list) -> None:
    for k in keys:
        if k not in d:
            problems.append(f"{where}: missing {k}")


def validate_fossil(f: dict) -> List[str]:
    p: List[str] = []
    if f.get("schema") != SCHEMA:
        p.append("schema")
    ws = f.get("whole_system", {})
    _need(ws, WHOLE_SYSTEM_FIELDS, "whole_system", p)
    for k, v in ws.items():
        if not (isinstance(v, dict) and "value" in v and v.get("basis") in BASIS):
            p.append(f"whole_system.{k}: needs {{value, basis in {BASIS}}}")
    cut = f.get("cut", {})
    if cut.get("state") not in FOSSIL_CUT_STATE:
        p.append("cut.state")
    if cut.get("state") not in ("NOT_CUT", "BLOCKED"):
        if cut.get("mode") not in CUT_MODE:
            p.append("cut.mode")
        if not cut.get("evidence"):
            p.append("cut.evidence empty on a cut fossil")
        for e in cut.get("evidence", []):
            if e.get("grade") not in EVIDENCE_GRADES or not e.get("ref"):
                p.append(f"cut.evidence entry {e}")
        if cut.get("state") != "ORGAN0" and not f.get("organs"):
            p.append("cut fossil with no organs and not ORGAN0")
    ids = {o.get("organ_id") for o in f.get("organs", [])}
    for o in f.get("organs", []):
        _need(o, ORGAN_FIELDS, f"organ {o.get('organ_id')}", p)
        if o.get("status") not in CUT_STATUS:
            p.append(f"organ {o.get('organ_id')}: status")
        if o.get("cut_mode") not in CUT_MODE:
            p.append(f"organ {o.get('organ_id')}: cut_mode")
        par = o.get("parent_mechanism")
        if par not in (None, "WHOLE_SYSTEM") and par not in ids:
            p.append(f"organ {o.get('organ_id')}: parent {par} not in fossil")
        for c in o.get("child_mechanisms", []):
            if c not in ids:
                p.append(f"organ {o.get('organ_id')}: child {c} not in fossil")
        ev = o.get("evidence", {})
        if not isinstance(ev, dict) or ev.get("grade") not in EVIDENCE_GRADES:
            p.append(f"organ {o.get('organ_id')}: evidence.grade")
        if o.get("status") == "ACCEPTED" and ev.get("grade") == "METADATA":
            p.append(f"organ {o.get('organ_id')}: ACCEPTED on METADATA alone")
        for dim, cell in (o.get("coverage") or {}).items():
            if dim not in COVERAGE_DIMS:
                p.append(f"organ {o.get('organ_id')}: coverage dim {dim}")
            elif cell.get("value") != UNMEASURED and cell.get("value") not in COVERAGE_DIMS[dim]:
                p.append(f"organ {o.get('organ_id')}: coverage {dim}={cell.get('value')} not in vocabulary")
            elif cell.get("basis") not in ("READ", "MEASURED"):
                p.append(f"organ {o.get('organ_id')}: coverage {dim} basis")
        for t in ("portability", "compatibility", "utility"):
            if o.get(t) not in TRI:
                p.append(f"organ {o.get('organ_id')}: {t} must be in {TRI}")
    for r in f.get("rejected_cuts", []):
        if r.get("reason") not in REJECTION_REASONS:
            p.append(f"rejected cut {r.get('candidate')}: reason")
        if not r.get("evidence"):
            p.append(f"rejected cut {r.get('candidate')}: evidence")
    for pr in f.get("pressures", []):
        _need(pr, PRESSURE_FIELDS, f"pressure {pr.get('pressure_id')}", p)
    for e in f.get("composition_edges", []):
        if e.get("from") not in ids | {"WHOLE_SYSTEM", "ENVIRONMENT"} or e.get("to") not in ids | {"WHOLE_SYSTEM", "ENVIRONMENT"}:
            p.append(f"composition edge {e}: endpoint not an organ of this fossil")
        if e.get("label") not in COMPOSITION_LABELS:
            p.append(f"composition edge {e}: label {e.get('label')} outside the provisional list (allowed, flagged)")
    for e in f.get("ancestry_edges", []):
        if e.get("relation") not in ANCESTRY_RELATIONS:
            p.append(f"ancestry edge {e}: relation")
    if f.get("residue", {}).get("state") not in RESIDUE_STATES:
        p.append("residue.state")
    return p


def load_fossils(root: Path = ROOT / "fossils") -> List[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*.json"))]


def validate_all(root: Path = ROOT / "fossils") -> Dict[str, List[str]]:
    out = {}
    for p in sorted(root.glob("*.json")):
        f = json.loads(p.read_text(encoding="utf-8"))
        probs = [x for x in validate_fossil(f) if "outside the provisional list" not in x]
        if probs:
            out[p.stem] = probs
    return out


if __name__ == "__main__":
    import sys
    bad = validate_all()
    for k, v in bad.items():
        print(k, v)
    print(f"{len(list((ROOT / 'fossils').glob('*.json')))} fossil files, {len(bad)} with problems")
    sys.exit(1 if bad else 0)
