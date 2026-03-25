"""
enrichment.py — Generate per-triplet causal enrichment context.

Takes a CausalGraph and produces enrichment JSON + human-readable text
for each concept triple. This text gets injected into Hephaestus's
code generation prompt to improve forge quality.
"""

import json
import logging
from pathlib import Path

log = logging.getLogger("coeus.enrichment")


def _concept_directive(name: str, influence: dict, forge_rate: float | None,
                       confounder_status: str | None = None,
                       interventional: dict | None = None) -> str:
    """Generate a prescriptive code-generation directive for one concept.

    Instead of just reporting statistics, tells the 397B model HOW to use
    each concept in the implementation.
    """
    forge_eff = influence.get("forge_effect", 0)
    nonlinear_eff = influence.get("nonlinear_effect")

    # Use the strongest available signal
    weight = forge_eff
    if nonlinear_eff is not None and abs(nonlinear_eff) > abs(forge_eff):
        weight = nonlinear_eff

    # Determine interventional drop if available
    drop = 0.0
    if interventional:
        drop = interventional.get("drop", 0)

    # Build the directive
    parts = [f"**{name}**: "]

    if weight > 0.5 or drop > 0.3:
        parts.append(
            "Strong primary driver of forge success. "
            "Make this concept the core architectural pattern of the evaluate() method. "
        )
        if forge_rate is not None and forge_rate > 0:
            parts.append(f"Historical forge rate: {forge_rate:.0%}. ")
    elif weight > 0.1 or drop > 0.1:
        parts.append(
            "Moderate positive synergy. "
            "Use this concept to support the primary logic, "
            "perhaps as a secondary validation step or scoring modifier. "
        )
    elif weight < -0.1 or drop < -0.1:
        parts.append(
            "Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. "
            "Do NOT use this for direct scoring; restrict it to the confidence() "
            "wrapper or structural parsing support only. "
        )
    else:
        parts.append(
            "Causally neutral. Implement as requested without over-indexing on its mechanics. "
        )

    # Confounder warnings
    if confounder_status == "confounded":
        parts.append(
            "WARNING: Past correlation with success is confounded by an unobserved variable. "
            "Ensure the implementation is strictly deterministic and does not rely on "
            "implicit linguistic priors that may not generalize. "
        )
    elif confounder_status == "direct_cause":
        parts.append("This concept has a proven, unconfounded mechanical advantage. ")

    return "".join(parts)


def _concept_summary(name: str, influence: dict, forge_rate: float | None,
                     confounder_status: str | None = None,
                     interventional: dict | None = None) -> str:
    """Short statistical summary for reports (not prompts)."""
    parts = []
    forge_eff = influence.get("forge_effect", 0)

    if interventional and abs(interventional.get("drop", 0)) > 0.05:
        drop = interventional["drop"]
        rate_with = interventional["rate_with"]
        if drop > 0:
            parts.append(f"removing it drops forge probability by {drop:.0%} "
                         f"(from {rate_with:.0%})")
        else:
            parts.append(f"removing it increases forge probability by {-drop:.0%}")
    elif abs(forge_eff) > 0.05:
        direction = "positive" if forge_eff > 0 else "negative"
        parts.append(f"{direction} forge driver ({forge_eff:+.2f})")

    nonlinear_eff = influence.get("nonlinear_effect")
    if nonlinear_eff is not None and abs(nonlinear_eff) > 0.1:
        parts.append(f"non-linear effect: {nonlinear_eff:+.2f}")

    if forge_rate is not None and forge_rate > 0:
        parts.append(f"forge rate: {forge_rate:.0%}")

    if confounder_status == "confounded":
        parts.append("WARNING: possibly confounded")

    if not parts:
        return f"{name}: no significant causal signal detected"

    return f"{name}: {'; '.join(parts)}"


def _find_similar_forges(concept_names: list[str], forge_entries: list[dict],
                         top_n: int = 3) -> list[dict]:
    """Find successful forges with overlapping concepts."""
    name_set = set(concept_names)
    scored = []
    for entry in forge_entries:
        entry_names = set(entry.get("concept_names", []))
        overlap = len(name_set & entry_names)
        if overlap > 0:
            scored.append((overlap, entry))

    scored.sort(key=lambda x: (-x[0], -x[1].get("accuracy", 0)))
    return [entry for _, entry in scored[:top_n]]


def enrich_triplet(concept_names: list[str], graph, forge_entries: list[dict]) -> dict:
    """Generate enrichment data for a single concept triple.

    Returns dict with:
        concept_strengths: per-concept causal summary
        pair_synergies: relevant pair interactions
        field_effects: relevant field-level effects
        similar_forges: nearby successful forges
        enrichment_text: human-readable paragraph for prompt injection
    """
    concept_strengths = {}
    for name in concept_names:
        influence = graph.concept_influence.get(name, {})
        forge_rate = graph.forge_rate_by_concept.get(name)
        confounder = graph.confounders.get(name) if hasattr(graph, "confounders") else None
        interv = graph.interventional.get(name) if hasattr(graph, "interventional") else None
        concept_strengths[name] = {
            "influence": influence,
            "forge_rate": forge_rate,
            "forge_effect": influence.get("forge_effect", 0),
            "confounder_status": confounder,
            "interventional": interv,
            "summary": _concept_summary(name, influence, forge_rate,
                                        confounder, interv),
            "directive": _concept_directive(name, influence, forge_rate,
                                           confounder, interv),
        }

    # Relevant pair synergies
    relevant_synergies = {}
    for i, c1 in enumerate(concept_names):
        for c2 in concept_names[i+1:]:
            for key_form in [f"{c1} + {c2}", f"{c2} + {c1}"]:
                if key_form in graph.pair_synergy:
                    relevant_synergies[key_form] = graph.pair_synergy[key_form]

    # Relevant field effects
    concept_fields = set()
    # We don't have fields in graph directly, but field_effects has field names
    relevant_fields = {}
    for field, effect in graph.field_effects.items():
        relevant_fields[field] = effect

    # Similar forges
    similar = _find_similar_forges(concept_names, forge_entries)

    # Build enrichment text — prescriptive directives for the code gen model
    text_parts = []
    text_parts.append(
        "The following concepts have historical causal signatures regarding their "
        "ability to form computable reasoning tools. Adjust your implementation "
        "strategy accordingly:"
    )
    text_parts.append("")

    # Per-concept directives (prescriptive, not descriptive)
    for name in concept_names:
        text_parts.append(f"- {concept_strengths[name]['directive']}")

    # Synergies as implementation guidance
    if relevant_synergies:
        text_parts.append("")
        for pair, syn in relevant_synergies.items():
            if syn > 0.1:
                text_parts.append(
                    f"- {pair}: strong positive synergy ({syn:+.3f}). "
                    f"These concepts reinforce each other — integrate them tightly "
                    f"rather than implementing as independent checks."
                )
            elif syn < -0.05:
                text_parts.append(
                    f"- {pair}: negative interaction ({syn:+.3f}). "
                    f"Keep these concepts in separate code paths to avoid interference."
                )

    # Similar forges as concrete examples
    if similar:
        text_parts.append("")
        text_parts.append("Similar combinations that forged successfully:")
        for entry in similar:
            sim_names = " + ".join(entry.get("concept_names", []))
            acc = entry.get("accuracy", 0)
            cal = entry.get("calibration", 0)
            text_parts.append(f"- {sim_names} (accuracy: {acc:.0%}, calibration: {cal:.0%})")

    # Global directive
    text_parts.append("")
    text_parts.append(
        "GLOBAL: The final tool must strictly beat the NCD compression baseline. "
        "Use structural parsing (negations, comparatives, conditionals, numeric evaluation) "
        "as the primary scoring signal. NCD is only a tiebreaker for candidates where "
        "no structural signal is detected."
    )

    enrichment_text = "\n".join(text_parts)

    return {
        "concept_names": concept_names,
        "concept_strengths": concept_strengths,
        "pair_synergies": relevant_synergies,
        "field_effects": relevant_fields,
        "similar_forges": [
            {"concept_names": e.get("concept_names", []),
             "accuracy": e.get("accuracy", 0),
             "calibration": e.get("calibration", 0)}
            for e in similar
        ],
        "enrichment_text": enrichment_text,
    }


def generate_all_enrichments(nous_entries: list[dict], graph,
                             forge_entries: list[dict],
                             combo_key_fn, output_dir: Path) -> int:
    """Generate enrichment JSON files for all Nous entries.

    Returns count of enrichments generated.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for entry in nous_entries:
        names = entry.get("concept_names", [])
        key = combo_key_fn(entry)

        enrichment = enrich_triplet(names, graph, forge_entries)

        # Save as JSON keyed by combo key
        safe_key = key.replace(" ", "_").replace("+", "x")
        out_path = output_dir / f"{safe_key}.json"
        out_path.write_text(json.dumps(enrichment, indent=2, default=str), encoding="utf-8")
        count += 1

    return count


def load_enrichment(concept_names: list[str], combo_key_fn,
                    enrichments_dir: Path) -> dict | None:
    """Load enrichment for a specific triplet. Used by Hephaestus."""
    key = combo_key_fn({"concept_names": concept_names})
    safe_key = key.replace(" ", "_").replace("+", "x")
    path = enrichments_dir / f"{safe_key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None
