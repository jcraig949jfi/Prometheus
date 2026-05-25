"""
Historian lens -- mines wisdom.md + recent park outcomes for patterns.

Cheap, fast lens. Reads the local artifacts (wisdom + recent_parks already
in the context), summarizes what's been tried, what's been failing, and
flags any anti-patterns the Generator should avoid.

Model preference: Claude Haiku (cheap, summary-class task).
"""
from __future__ import annotations

from datetime import datetime, timezone

from lenses._base import Lens, LensReport, CycleContext, SCORING_AXES
from lenses._llm import call_llm, extract_json_block, clamp_axis


HISTORIAN_SYSTEM = (
    "You are the Historian lens for Icarus. Your role: read the wisdom log "
    "and the recent parked-cycle reasons, identify recurring patterns, and "
    "produce one short briefing for the Generator.\n\n"
    "Focus on:\n"
    "  - Recurring failure modes (parks with same reason >2x)\n"
    "  - Strategies that have worked recently (look at stable cycles)\n"
    "  - Anti-patterns to avoid this cycle\n"
    "  - Whether the recent trend suggests momentum (toward stable) or stall\n\n"
    "OUTPUT (strict JSON):\n"
    "{\n"
    '  "recurring_failure_modes": [<2-4 short strings>],\n'
    '  "strategies_that_have_worked": [<0-3 short strings>],\n'
    '  "anti_patterns_to_avoid": [<2-4 short strings>],\n'
    '  "trend": "momentum_forward" | "stalling" | "thrashing" | "no_data",\n'
    '  "qualitative_summary": "<2-3 sentences>",\n'
    '  "axes": {\n'
    '    "tier_proximity": <0.0-1.0 estimate based on trajectory>,\n'
    '    "novelty": <0.0-1.0; how novel are recent attempts>,\n'
    '    "regression_risk": <0.0-1.0; have recent attempts been safe>,\n'
    '    "structural_simplicity": <0.0-1.0; how simple have winning diffs been>,\n'
    '    "evidence_quality": <0.0-1.0; how robust is wisdom so far>\n'
    "  },\n"
    '  "confidence": <0.0-1.0>,\n'
    '  "key_observations": [<2-5 short strings>]\n'
    "}\n"
)


class HistorianLens(Lens):
    name = "historian"
    model_preference = "claude_haiku"

    def observe(self, ctx: CycleContext) -> LensReport:
        wisdom = ctx.wisdom or "_(no wisdom yet)_"
        parks_summary = _summarize_parks(ctx.recent_parks)

        user_prompt = (
            f"## Wisdom log (current)\n{wisdom[:3000]}\n\n"
            f"## Recent parked cycles\n{parks_summary}\n\n"
            f"## Last stable\n{ctx.last_stable_id}\n\n"
            f"## Tier target\n{ctx.tier_target}\n\n"
            f"Brief the Generator."
        )

        result = call_llm(
            preference=self.model_preference,
            system=HISTORIAN_SYSTEM,
            user=user_prompt,
            max_tokens=1500,
        )
        text = result.get("text", "")
        parsed = extract_json_block(text)
        if not parsed:
            return LensReport.empty_with_error(
                lens_name=self.name, cycle_n=ctx.cycle_n,
                error="historian_response_not_json",
                model_used=result.get("model_used", "unknown"),
            )

        axes = {a: clamp_axis(parsed.get("axes", {}).get(a, 0.5))
                for a in SCORING_AXES}
        confidence = clamp_axis(parsed.get("confidence", 0.5))

        observations = []
        for label in ("recurring_failure_modes", "anti_patterns_to_avoid",
                      "strategies_that_have_worked"):
            for item in (parsed.get(label) or [])[:3]:
                observations.append(f"{label}: {str(item)[:200]}")
        observations.append(f"trend={parsed.get('trend', '?')}")
        for o in (parsed.get("key_observations") or [])[:3]:
            observations.append(str(o)[:300])

        return LensReport(
            lens_name=self.name,
            model_used=result.get("model_used", "unknown"),
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=parsed.get("qualitative_summary", "")[:1000],
            axes=axes,
            confidence=confidence,
            key_observations=observations[:10],
            raw_response_excerpt=text[:500],
            tokens_used=result.get("tokens_used", 0),
            cost_estimate_usd=result.get("cost_estimate_usd", 0.0),
        )


def _summarize_parks(parks: list[dict]) -> str:
    if not parks:
        return "_(no recent parks)_"
    lines = []
    for p in parks[:10]:
        cyc = p.get("cycle", "?")
        reason = (p.get("reason") or "?")[:140]
        lines.append(f"  - cycle {cyc}: {reason}")
    return "\n".join(lines)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
