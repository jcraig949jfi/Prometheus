"""
Integrator lens -- synthesizes the panel into a recommendation.

Reads all 4 prior lens reports + the apply/TDD infrastructure results.
Produces a recommendation (mark_stable | park) AND a load-bearing-lens
citation. The citation requirement is the countermeasure to committee
paralysis: every decision points to which perspective carried the most weight
and why.

The Integrator must address the Skeptic's minority_position if present --
either explicitly defend against it or honor it.

Model preference: Claude Sonnet (synthesis is hard; needs the better model).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from lenses._base import (
    Lens, LensReport, CycleContext, SCORING_AXES,
    axes_summary, lens_agreement_patterns,
)
from lenses._llm import call_llm, extract_json_block, clamp_axis


INTEGRATOR_SYSTEM = (
    "You are the Integrator lens for Icarus, a failure-to-representation "
    "instrumentation harness. You have lens reports + infrastructure "
    "measurements (diff apply + TDD) + a DETERMINISTIC Contract Lens result. "
    "Your job: synthesize a recommendation, cite the load-bearing lens, AND "
    "emit a typed training object so this cycle becomes reusable substrate.\n\n"
    "STRICT RULES:\n"
    "1. Decision is binary: 'mark_stable' OR 'park'.\n"
    "2. You MUST identify the single load-bearing lens. State it explicitly.\n"
    "3. If the Skeptic returned a minority_position OR the Contract Lens "
    "found a violation, you MUST address it. The Contract Lens is "
    "DETERMINISTIC -- if it reports a contract_violation, that finding is a "
    "fact, not an opinion. You may still promote, but only by explicitly "
    "acknowledging the debt; it will be recorded and the next cycle will be "
    "FORCED to write a regression test for it.\n"
    "4. Do not rubber-stamp positive consensus.\n"
    "5. Park if TDD failed, regardless of other votes.\n"
    "6. Emit the training_enrichment object honestly. improvement_kind must "
    "distinguish 'capability' (a new tier dimension genuinely passes) from "
    "'test_weakness' (promoted because tests are vacuous/easy) from "
    "'metric_shaped' (tests added that lock current behavior; docstring "
    "claims without demonstration). Be self-critical: most cycles are NOT "
    "pure capability gains.\n\n"
    "OUTPUT (strict JSON):\n"
    "{\n"
    '  "decision": "mark_stable" | "park",\n'
    '  "load_bearing_lens": "generator"|"diagnostician"|"historian"|"skeptic"|"contract",\n'
    '  "load_bearing_rationale": "<2-3 sentences>",\n'
    '  "minority_response": "<how you handled Skeptic/Contract concern, or \\"no_minority\\">",\n'
    '  "qualitative_summary": "<3-5 sentences>",\n'
    '  "axes": {"tier_proximity": <0-1>, "novelty": <0-1>, "regression_risk": <0-1; 1=LOW risk>, "structural_simplicity": <0-1>, "evidence_quality": <0-1>},\n'
    '  "confidence": <0.0-1.0>,\n'
    '  "key_observations": [<2-5 short strings>],\n'
    '  "training_enrichment": {\n'
    '    "proposal_type": "reasoner_logic_change|batch_orchestration_change|new_method|representation_shift|test_addition|docstring_change|refactor|no_change|unknown",\n'
    '    "failure_subclass": "<one of the curated subclasses, or none>",\n'
    '    "nearby_survivor": "<what move WOULD have survived, or null>",\n'
    '    "future_tier_risk": [<tier ids this change threatens, e.g. \\"R3\\">],\n'
    '    "regression_test_to_write": "<the test that would expose the concern, or null>",\n'
    '    "representation_change_hint": "<what representation change would make the right move cheap, or null>",\n'
    '    "improvement_kind": "capability|test_weakness|metric_shaped|none",\n'
    '    "improvement_rationale": "<1-2 sentences justifying improvement_kind>"\n'
    "  }\n"
    "}\n"
)


class IntegratorLens(Lens):
    name = "integrator"
    model_preference = "claude_sonnet"

    def observe(self, ctx: CycleContext) -> LensReport:
        # Gather upstream lens summaries
        upstream = []
        for lens_name, lens_report in (
            ("diagnostician", ctx.diagnostician_report),
            ("historian", ctx.historian_report),
            ("generator", ctx.generator_report),
            ("contract", ctx.contract_lens_report),
            ("skeptic", ctx.skeptic_report),
        ):
            upstream.append(_lens_block(lens_name, lens_report))

        apply_summary = json.dumps(ctx.apply_result or {}, default=str)[:400]
        tdd_summary = json.dumps(ctx.tdd_result or {}, default=str)[:400]
        contract_summary = json.dumps(ctx.contract_report or {}, default=str)[:600]
        debts_summary = (
            json.dumps(ctx.open_debts, default=str)[:600]
            if ctx.open_debts else "none"
        )

        # Pre-compute panel-wide summary for the integrator's reference
        reports_in_panel = [r for r in (
            ctx.diagnostician_report, ctx.historian_report,
            ctx.generator_report, ctx.contract_lens_report, ctx.skeptic_report,
        ) if r is not None]
        agreement = lens_agreement_patterns(reports_in_panel)

        user_prompt = (
            f"## Cycle\nN={ctx.cycle_n}, tier={ctx.tier_target}, strategy={ctx.cycle_strategy}\n\n"
            f"## Lens reports\n" + "\n\n".join(upstream) + "\n\n"
            f"## Infrastructure: diff apply\n{apply_summary}\n\n"
            f"## Infrastructure: TDD\n{tdd_summary}\n\n"
            f"## DETERMINISTIC Contract Lens report (this is fact, not opinion)\n{contract_summary}\n\n"
            f"## Open debts inherited from prior cycles (must be addressed)\n{debts_summary}\n\n"
            f"## Pre-computed panel axis agreement\n"
            f"{json.dumps(agreement, indent=2, default=str)[:1200]}\n\n"
            f"Synthesize. Emit the training_enrichment honestly -- be self-critical "
            f"about improvement_kind."
        )

        result = call_llm(
            preference=self.model_preference,
            system=INTEGRATOR_SYSTEM,
            user=user_prompt,
            max_tokens=2000,
        )
        text = result.get("text", "")
        parsed = extract_json_block(text)
        if not parsed:
            # Integrator failed -- conservative fallback: park
            return LensReport(
                lens_name=self.name,
                model_used=result.get("model_used", "unknown"),
                cycle_n=ctx.cycle_n,
                ts=_now_iso(),
                qualitative_summary=(
                    "[Integrator parse failure -- conservative park] "
                    "Could not parse Integrator JSON response."
                ),
                axes={a: 0.3 for a in SCORING_AXES},
                confidence=0.0,
                key_observations=["integrator_response_unparseable"],
                suggested_actions=["park", "diagnostician"],
                error="integrator_response_not_json",
                tokens_used=result.get("tokens_used", 0),
                cost_estimate_usd=result.get("cost_estimate_usd", 0.0),
            )

        decision = str(parsed.get("decision", "park")).strip().lower()
        if decision not in ("mark_stable", "park"):
            decision = "park"
        load_bearing = str(parsed.get("load_bearing_lens", "diagnostician")).strip().lower()
        if load_bearing not in ("generator", "diagnostician", "historian", "skeptic", "contract"):
            load_bearing = "diagnostician"

        axes = {a: clamp_axis(parsed.get("axes", {}).get(a, 0.5))
                for a in SCORING_AXES}
        confidence = clamp_axis(parsed.get("confidence", 0.5))

        observations = [str(o)[:300] for o in (parsed.get("key_observations") or [])[:4]]
        observations.append(f"load_bearing={load_bearing}")
        observations.append(f"load_bearing_rationale={parsed.get('load_bearing_rationale', '')[:200]}")
        observations.append(f"minority_response={parsed.get('minority_response', 'n/a')[:200]}")

        # Encode decision + load-bearing into suggested_actions[0] and [1]
        suggested = [decision, load_bearing,
                     parsed.get("load_bearing_rationale", "")[:300],
                     parsed.get("minority_response", "")[:300]]

        enrichment = parsed.get("training_enrichment", {}) or {}

        return LensReport(
            lens_name=self.name,
            model_used=result.get("model_used", "unknown"),
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=parsed.get("qualitative_summary", "")[:1500],
            axes=axes,
            confidence=confidence,
            key_observations=observations[:8],
            suggested_actions=suggested,
            raw_response_excerpt=text[:500],
            tokens_used=result.get("tokens_used", 0),
            cost_estimate_usd=result.get("cost_estimate_usd", 0.0),
            extra={
                "training_enrichment": enrichment,
                "minority_response": parsed.get("minority_response", ""),
                "load_bearing_rationale": parsed.get("load_bearing_rationale", ""),
            },
        )


def _lens_block(name: str, report) -> str:
    if report is None:
        return f"### {name}\n_(not run)_"
    if report.error:
        return f"### {name}\n_(error: {report.error})_"
    obs = "\n".join(f"  - {o}" for o in report.key_observations[:5])
    axes_line = ", ".join(f"{k}={v:.2f}" for k, v in (report.axes or {}).items())
    minority = (
        f"\n  MINORITY_POSITION: {report.minority_position}"
        if getattr(report, "minority_position", None) else ""
    )
    return (
        f"### {name} (model: {report.model_used}, confidence: {report.confidence:.2f})\n"
        f"Summary: {report.qualitative_summary[:800]}\n"
        f"Axes: {axes_line}\n"
        f"Observations:\n{obs}{minority}"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
