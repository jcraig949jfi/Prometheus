"""Hecate record schema and validator.

Mirrors the charter's TypeScript types (roles/Hecate/prompts/2026-09-29_charter/)
as plain JSON dicts, and enforces the rules the charter and the base role
make structural:

- every generated artifact points back to its triplicate and its pass;
- historical provenance keeps source "hephaestus", sourceArtifact, historicalId;
- every hypothesis carries one of the four honesty layers, and the upper two
  layers need evidence pointers (rows + preregistration);
- PROMISING / EXPAND need a preregistered predicate result on committed rows;
- every pass after the first names what it added (charter Pass N rule).

validate_program() returns a list of error strings; empty means valid.
"""

from __future__ import annotations

VERDICTS = (
    "UNTOUCHED", "SPECULATIVE", "PROBING", "PROMISING",
    "EXPAND", "PARK", "FOSSIL", "REJECT",
)
EVIDENCE_VERDICTS = ("PROMISING", "EXPAND")
KILL_VERDICTS = ("FOSSIL", "REJECT")

LAYERS = (
    "speculation",
    "implemented_candidate",
    "experimental_observation",
    "supported_conclusion",
)

SOURCES = ("hephaestus", "generated", "human")

PASS_KINDS = {
    0: "raw_interpretation", 1: "collision", 2: "lens_explosion",
    3: "minimal_worlds", 4: "first_falsification", 5: "deeper_lenses",
    6: "cross_substrate", 7: "engine_generation", 8: "second_order_collision",
    9: "visual_cortex", 10: "adversarial_review",
}

ADDITIONS = (
    "new observable", "new intervention", "new lens", "new substrate",
    "new falsifier", "new mechanism", "new engine architecture",
    "new cross-triplicate connection",
    # passes 0-2 are the first of their kind; they add these by construction
    "new interpretation",
)

DECISIONS = (
    "DEEPEN", "FALSIFY", "TRANSFER", "BUILD_ENGINE", "VISUALIZE",
    "CROSS_COLLIDE", "PARK", "FOSSILIZE", "REJECT",
)

RESEARCH_AXES = (
    "novelty", "mechanistic_clarity", "falsifiability", "empirical_support",
    "cross_lens_agreement", "cross_substrate_transfer", "baseline_resistance",
    "artifact_risk", "cost", "unexpectedness", "potential_importance",
)
AXIS_LEVELS = ("none", "low", "medium", "high", "unknown")

PRIOR_ART = (
    "INDEPENDENTLY_GENERATED", "KNOWN_ANALOGUE_FOUND", "PARTIAL_PRIOR_ART",
    "LIKELY_REDIRECT", "POSSIBLY_NOVEL",
)

MECHANISM_QUESTIONS = (
    "what_exists", "what_changes", "what_persists", "what_is_selected",
    "what_can_reproduce", "what_can_learn", "what_can_transfer",
    "distinguishing_observable",
)

LENS_FIELDS = (
    "id", "name", "triplicateId", "rationale", "sourceRepresentation",
    "transformation", "observables", "predictedSignals", "nullExpectation",
    "failureModes", "informationAddedBeyondExistingLenses",
)

WORLD_FIELDS = (
    "hypothesis", "mechanism", "intervention", "control",
    "positive_control", "observable", "success_criterion",
    "failure_criterion", "alternative_explanation", "null_twin",
)

ENGINE_FIELDS = (
    "name", "triplicateId", "uniqueQuestion",
    "whyExistingEnginesAreInsufficient", "worldModel", "organismModel",
    "pressures", "observables", "controls", "smallestPrototype",
    "estimatedCost", "expansionCriterion", "killCriterion",
)


def _nonempty(v) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, tuple, dict)):
        return len(v) > 0
    return True


def validate_provenance(p: dict) -> list[str]:
    errs = []
    src = p.get("source")
    if src not in SOURCES:
        errs.append(f"provenance.source {src!r} not in {SOURCES}")
    if src == "hephaestus":
        for k in ("sourceArtifact", "historicalId"):
            if not _nonempty(p.get(k)):
                errs.append(f"historical provenance missing {k}")
    if src == "generated" and not _nonempty(p.get("derived_from")):
        errs.append("generated provenance missing derived_from (list of parent ids)")
    return errs


def _check_backpointer(kind, item, tid, pass_ids, errs):
    iid = item.get("id", "?")
    if item.get("triplicateId") != tid:
        errs.append(f"{kind} {iid}: triplicateId {item.get('triplicateId')!r} != {tid!r}")
    if item.get("passId") not in pass_ids:
        errs.append(f"{kind} {iid}: passId {item.get('passId')!r} is not a pass of this program")


def validate_program(prog: dict) -> list[str]:
    errs: list[str] = []
    tid = prog.get("id")
    if not _nonempty(tid):
        return ["program has no id"]

    concepts = prog.get("concepts")
    if not isinstance(concepts, list) or len(concepts) != 3:
        errs.append("concepts must be a list of exactly 3")
    else:
        for c in concepts:
            if not _nonempty(c.get("name")):
                errs.append("concept without name")

    errs += validate_provenance(prog.get("provenance") or {})

    passes = prog.get("passes") or []
    pass_ids = set()
    for i, ps in enumerate(passes):
        pid = ps.get("id")
        if not _nonempty(pid):
            errs.append(f"pass #{i} has no id")
            continue
        if pid in pass_ids:
            errs.append(f"duplicate pass id {pid}")
        pass_ids.add(pid)
        if ps.get("triplicateId") != tid:
            errs.append(f"pass {pid}: triplicateId mismatch")
        if ps.get("index") not in PASS_KINDS and not (
            isinstance(ps.get("index"), int) and ps.get("index", -1) > 10
        ):
            errs.append(f"pass {pid}: index {ps.get('index')!r} invalid")
        added = ps.get("added") or []
        if not added:
            errs.append(f"pass {pid}: names nothing it added (charter Pass N rule)")
        for a in added:
            if a not in ADDITIONS:
                errs.append(f"pass {pid}: addition {a!r} not in charter list")
        gen = ps.get("generator") or {}
        if not _nonempty(gen.get("model")):
            errs.append(f"pass {pid}: generator.model missing")
        if ps.get("decision") is not None and ps.get("decision") not in DECISIONS:
            errs.append(f"pass {pid}: decision {ps.get('decision')!r} invalid")
        st = ps.get("research_state")
        if st is not None:
            for ax in RESEARCH_AXES:
                if st.get(ax) not in AXIS_LEVELS:
                    errs.append(f"pass {pid}: research_state.{ax} missing/invalid")

    for h in prog.get("hypotheses") or []:
        _check_backpointer("hypothesis", h, tid, pass_ids, errs)
        layer = h.get("layer")
        if layer not in LAYERS:
            errs.append(f"hypothesis {h.get('id')}: layer {layer!r} not one of {LAYERS}")
        if layer in ("experimental_observation", "supported_conclusion"):
            if not _nonempty(h.get("evidence_rows")):
                errs.append(f"hypothesis {h.get('id')}: layer {layer} without evidence_rows")
        if layer == "supported_conclusion" and not _nonempty(h.get("prereg")):
            errs.append(f"hypothesis {h.get('id')}: supported_conclusion without prereg")
        if h.get("kind") == "mechanism":
            q = h.get("questions") or {}
            for k in MECHANISM_QUESTIONS:
                if not _nonempty(q.get(k)):
                    errs.append(f"mechanism {h.get('id')}: question {k} unanswered")
        pa = h.get("prior_art")
        if pa is not None and pa.get("label") not in PRIOR_ART:
            errs.append(f"hypothesis {h.get('id')}: prior_art label invalid")

    for lens in prog.get("lenses") or []:
        _check_backpointer("lens", lens, tid, pass_ids, errs)
        for k in LENS_FIELDS:
            if not _nonempty(lens.get(k)):
                errs.append(f"lens {lens.get('id')}: field {k} empty")

    for w in prog.get("experiments") or []:
        _check_backpointer("world", w, tid, pass_ids, errs)
        for k in WORLD_FIELDS:
            if not _nonempty(w.get(k)):
                errs.append(f"world {w.get('id')}: field {k} empty")

    for e in prog.get("candidateEngines") or []:
        _check_backpointer("engine", e, tid, pass_ids, errs)
        for k in ENGINE_FIELDS:
            if not _nonempty(e.get(k)):
                errs.append(f"engine {e.get('id')}: field {k} empty")

    v = prog.get("currentVerdict")
    if v not in VERDICTS:
        errs.append(f"currentVerdict {v!r} not in {VERDICTS}")
    ev = prog.get("evidenceSummary") or {}
    if v in EVIDENCE_VERDICTS:
        pred = ev.get("predicate") or {}
        if not (_nonempty(pred.get("prereg")) and _nonempty(pred.get("rows"))
                and pred.get("result") == "PASS"):
            errs.append(f"verdict {v} without a PASSing preregistered predicate on committed rows")
    if v in KILL_VERDICTS and not _nonempty(ev.get("rows")):
        errs.append(f"verdict {v} without the rows that killed the tested claim")
    if v != "UNTOUCHED" and not passes:
        errs.append(f"verdict {v} with no passes")
    return errs
