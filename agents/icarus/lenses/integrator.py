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
    "You are the Integrator lens for Icarus. You have 4 lens reports + "
    "infrastructure measurements (diff apply + TDD). Your job: synthesize a "
    "recommendation and CITE which lens carried the most weight in your "
    "decision.\n\n"
    "STRICT RULES:\n"
    "1. Decision is binary: 'mark_stable' OR 'park'.\n"
    "2. You MUST identify the single lens whose perspective was most load-"
    "bearing for your decision. State it explicitly.\n"
    "3. If the Skeptic returned a minority_position, you MUST address it -- "
    "either explicitly defend against it or honor it.\n"
    "4. Do not rubber-stamp positive consensus. If Skeptic objected and you "
    "still vote mark_stable, explain why the objection isn't load-bearing.\n"
    "5. Park if TDD failed, regardless of other lens votes.\n\n"
    "OUTPUT (strict JSON):\n"
    "{\n"
    '  "decision": "mark_stable" | "park",\n'
    '  "load_bearing_lens": "generator" | "diagnostician" | "historian" '
    '| "skeptic",\n'
    '  "load_bearing_rationale": "<2-3 sentences on why that lens drove the decision>",\n'
    '  "minority_response": "<how you handled Skeptic minority position, '
    'or \\"no_minority\\" if none>",\n'
    '  "qualitative_summary": "<3-5 sentences synthesizing the panel>",\n'
    '  "axes": {\n'
    '    "tier_proximity": <0.0-1.0; your synthesized estimate>,\n'
    '    "novelty": <0.0-1.0>,\n'
    '    "regression_risk": <0.0-1.0; 1=LOW risk>,\n'
    '    "structural_simplicity": <0.0-1.0>,\n'
    '    "evidence_quality": <0.0-1.0>\n'
    "  },\n"
    '  "confidence": <0.0-1.0>,\n'
    '  "key_observations": [<2-5 short strings>]\n'
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
            ("skeptic", ctx.skeptic_report),
        ):
            upstream.append(_lens_block(lens_name, lens_report))

        apply_summary = json.dumps(ctx.apply_result or {}, default=str)[:400]
        tdd_summary = json.dumps(ctx.tdd_result or {}, default=str)[:400]

        # Pre-compute panel-wide summary for the integrator's reference
        reports_in_panel = [r for r in (
            ctx.diagnostician_report, ctx.historian_report,
            ctx.generator_report, ctx.skeptic_report,
        ) if r is not None]
        agreement = lens_agreement_patterns(reports_in_panel)

        user_prompt = (
            f"## Cycle\nN={ctx.cycle_n}, tier={ctx.tier_target}\n\n"
            f"## Lens reports\n" + "\n\n".join(upstream) + "\n\n"
            f"## Infrastructure: diff apply\n{apply_summary}\n\n"
            f"## Infrastructure: TDD\n{tdd_summary}\n\n"
            f"## Pre-computed panel axis agreement\n"
            f"{json.dumps(agreement, indent=2, default=str)[:1500]}\n\n"
            f"Synthesize."
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
        if load_bearing not in ("generator", "diagnostician", "historian", "skeptic"):
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
