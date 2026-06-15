"""fp_void_map.py — the PREDICTIVE layer of the failure-primitive atlas.

The atlas is a sparse tensor (failure-shape x agent x detector x mitigation);
this module computes its VOIDS — the Mendeleev gaps. A void is a cell where an
agent's DESIGN CLASS predicts a failure shape but no detector has ever been
run against it. The void report is the audit schedule: highest-value cells
first.

Predictive use for new agents: `predict_fps(["generator_menu", ...])` returns
the detector suite a new agent of that design should be born instrumented
with (Proposal D §3.3 birth-instrumentation, made mechanical).

Cell states:
  FIRED              detector ran, failure shape present (anchor or escrow)
  RUN_CLEAN          detector ran on adequate data, did not fire
  RUN_INSUFFICIENT   detector ran, data volume below the detector's floor
  PREDICTED_UNTESTED design class predicts liability; detector never run (VOID)
  BLOCKED            predicted, but the data is currently unreachable
  NOT_PREDICTED      design class gives no reason to expect the shape

Audit evidence is read from harmonia/experiments/fp_void_audits_*.json
(written by audit scripts, one row per (fp, target) detector run).
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_GLOB = str(REPO_ROOT / "harmonia" / "experiments" / "fp_void_audits_*.json")


# ----------------------------------------------------------------------------
# Agent design classes (failure-relevant architecture, not org chart).
# An agent can hold several. Sources: Stage-2 lineage audit 2026-06-10,
# agent charters, pivot docs.
# ----------------------------------------------------------------------------
AGENT_DESIGN_CLASSES: dict = {
    # substrate generators: bounded menu -> promotion gate -> ledger
    "theseus-substrate": {"generator_menu"},
    "apollo": {"generator_menu", "self_improving_loop", "llm_in_loop"},
    "ergon": {"generator_menu"},
    "polyhymnia": {"generator_menu", "self_improving_loop"},
    "arachne": {"generator_menu", "self_improving_loop"},   # population layer, planned
    "techne": {"operator_role"},  # operates theseus-substrate; library, no own loop
    # falsification organs: kill ledgers, verdicts, motif claims
    "harmonia": {"falsifier_auditor"},
    "erebos": {"falsifier_auditor"},
    "charon-plugins": {"falsifier_auditor"},
    "nemesis": {"falsifier_auditor"},
    "aporia": {"synthesis_writer", "falsifier_auditor"},
    # self-improving loops. CORRECTED 2026-06-10 after a live audit: the
    # agents-swarm siblings (hypatia/atalanta/pheme/talos) share only the
    # daemon SHELL with polyhymnia, NOT the self_improving adaptation-menu
    # mixin (0 stub-menu matches; polyhymnia was the registry's only adopter).
    # Their simultaneous DEAD timestamps (all 2026-05-30) are a common-cause
    # fleet stop, not four walls. First documented PREDICTION MISS of the
    # void map — kept here as calibration data.
    "icarus": {"self_improving_loop", "llm_in_loop"},
    "hypatia": {"generator_menu", "llm_in_loop"},     # D-track curator: produces worked solutions
    "atalanta": {"generator_menu"},                   # E-track primitive hunter over Apollo organisms
    "pheme": {"data_infra"},                          # demand-signal voicer, reads Ergon evals
    "talos": {"data_infra", "llm_in_loop"},           # Learner corpus builder (Phase 0)
    # LLM-probe instruments
    "zoo-matrix": {"llm_in_loop"},
    "legality-replication": {"llm_in_loop"},
    # infra / synthesis
    "mnemosyne": {"data_infra"},
    "hephaestus": {"generator_menu", "llm_in_loop"},
    "forge": {"generator_menu", "llm_in_loop"},
    "noesis": {"generator_menu"},
    "arcanum": {"generator_menu"},
    "cartography": {"data_infra", "synthesis_writer"},
}

# Which design classes are liable to which failure primitive.
# Grown by the Stage-3 hunt as new FPs register.
PREDICTS: dict = {
    "FP-001": {"generator_menu", "falsifier_auditor", "synthesis_writer"},
    "FP-002": {"falsifier_auditor", "generator_menu", "self_improving_loop"},
    "FP-003": {"generator_menu", "self_improving_loop"},
    # FP-004 degenerate_field_flatline: any agent that computes metrics over a
    # declared-varying field — i.e. nearly everyone that instruments itself.
    "FP-004": {"generator_menu", "self_improving_loop", "falsifier_auditor",
               "llm_in_loop", "data_infra"},
}

# Cells whose data is known-unreachable right now (kept honest, not hidden).
BLOCKED: dict = {
    # Postgres at 192.168.1.176:5432 timed out 2026-06-10 (Harmonia E session);
    # all DB-resident ledgers are unreachable from M2 until it returns.
    ("FP-002", "charon-plugins"): "kill ledger lives in Postgres (prometheus_fire); host unreachable 2026-06-10",
    ("FP-002", "theseus-substrate"): "200K-kill corpus not on this machine (theseus/corpus empty); Postgres unreachable",
}

# Map audit-target strings (from audit JSONs) -> canonical agent names.
TARGET_TO_AGENT = {
    "apollo-branch-c-r1-cellfills": "apollo",
    "apollo-branch-c-r1-improvements": "apollo",
    "apollo-branch-c-r2-cellfills": "apollo",
    "apollo-branch-c-r2-improvements": "apollo",
    "icarus-training-stream": "icarus",
    "icarus-cycle-stream": "icarus",
    "ergon-20260418-deep": "ergon",
    "ergon-20260418-survived": "ergon",
}


def _load_audit_rows() -> list:
    rows = []
    for p in sorted(glob.glob(AUDIT_GLOB)):
        try:
            rows.extend(json.loads(Path(p).read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return rows


def _anchor_agents(fp) -> set:
    """Canonical agent names with non-escrow anchors for an FP."""
    out = set()
    for a in fp.anchor_cases:
        name = a.agent.split(" ")[0].strip().lower()
        out.add(name)
    return out


def cell_state(fp_id: str, agent_name: str, registry, audit_rows) -> str:
    fp = registry[fp_id]
    classes = AGENT_DESIGN_CLASSES.get(agent_name, set())
    predicted = bool(PREDICTS.get(fp_id, set()) & classes)

    for a in fp.anchor_cases:
        if a.agent.split(" ")[0].strip().lower() == agent_name:
            return "FIRED(escrow)" if a.escrow else "FIRED"

    ran = [r for r in audit_rows
           if r.get("fp") == fp_id
           and TARGET_TO_AGENT.get(r.get("target", ""), r.get("target")) == agent_name]
    if ran:
        if any(r.get("fired") for r in ran):
            return "FIRED(escrow)"   # fired in audit but not yet promoted to anchor
        if any("min_records" in str(r.get("context", {})) or
               (r.get("evidence", {}).get("n", 10**9)
                < r.get("evidence", {}).get("threshold_n", 0))
               or "RUN_INSUFFICIENT" in str(r.get("context", {}))
               for r in ran):
            return "RUN_INSUFFICIENT"
        return "RUN_CLEAN"

    if not predicted:
        return "NOT_PREDICTED"
    if (fp_id, agent_name) in BLOCKED:
        return "BLOCKED"
    return "PREDICTED_UNTESTED"


def predict_fps(design_classes) -> list:
    """Birth-instrumentation: detector suite for a new agent of these classes."""
    cs = set(design_classes)
    return sorted(fp_id for fp_id, liable in PREDICTS.items() if liable & cs)


def build_void_map() -> dict:
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    from harmonia.primitives.failure_primitives import REGISTRY
    audit_rows = _load_audit_rows()
    cells: dict = {}
    for fp_id in REGISTRY:
        for agent_name in AGENT_DESIGN_CLASSES:
            cells[(fp_id, agent_name)] = cell_state(
                fp_id, agent_name, REGISTRY, audit_rows)
    return cells


def void_schedule() -> list:
    """Ranked audit schedule: PREDICTED_UNTESTED cells first (by how cheap and
    local the data is), then BLOCKED (with unblock condition)."""
    cells = build_void_map()
    # Hand-ranked data locality: which voids have ledgers ON this machine.
    LOCAL_DATA = {
        ("FP-002", "icarus"): "agents/icarus/state/training_stream.jsonl (grows with icarus runs)",
        ("FP-003", "icarus"): "agents/icarus/state/ (proposal/adaptation history)",
        ("FP-001", "apollo"): "apollo archive snapshots (checkpoints/) — claim shape needs definition",
        ("FP-003", "ergon"): "ergon/ shadow archive + operator menu",
        ("FP-003", "aporia"): "aporia/meta/experiments attempt ledger",
        ("FP-002", "erebos"): "charon/agents/erebos local fixtures (full ledger in Postgres)",
        ("FP-003", "hypatia"): "agents/hypatia daemon output ledger (D-track worked-solution promotions)",
        ("FP-003", "atalanta"): "agents/atalanta daemon output ledger (E-track primitive proposals)",
    }
    out = []
    for (fp_id, agent_name), state in sorted(cells.items()):
        if state in ("PREDICTED_UNTESTED", "BLOCKED"):
            out.append({
                "fp": fp_id, "agent": agent_name, "state": state,
                "local_data": LOCAL_DATA.get((fp_id, agent_name), ""),
                "blocked_reason": BLOCKED.get((fp_id, agent_name), ""),
            })
    # voids with local data first, then plain voids, then blocked
    out.sort(key=lambda r: (r["state"] == "BLOCKED", r["local_data"] == "",
                            r["fp"], r["agent"]))
    return out


if __name__ == "__main__":
    cells = build_void_map()
    from collections import Counter
    print("cell states:", dict(Counter(cells.values())))
    print("\nVOID SCHEDULE (audits to run next):")
    for row in void_schedule():
        tag = " [LOCAL DATA]" if row["local_data"] else (
            " [BLOCKED]" if row["state"] == "BLOCKED" else "")
        print(f"  {row['fp']} x {row['agent']}{tag}"
              + (f" — {row['local_data']}" if row["local_data"] else "")
              + (f" — {row['blocked_reason']}" if row["blocked_reason"] else ""))
    print("\nbirth-instrumentation example — new generator+self-improving agent:",
          predict_fps({"generator_menu", "self_improving_loop"}))
