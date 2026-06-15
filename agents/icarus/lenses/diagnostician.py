"""
Diagnostician lens -- characterizes the current state of the reasoner.

Does NOT propose changes. Asks: "where is the reasoner on the ladder right
now? what specific capability is missing for the next tier?" Its output
informs the Generator.

Model preference: DeepSeek (different family from Claude/Gemini -- gives
cross-family diversity in the panel).
"""
from __future__ import annotations

from datetime import datetime, timezone

from lenses._base import Lens, LensReport, CycleContext, SCORING_AXES
from lenses._llm import call_llm, extract_json_block, clamp_axis


DIAGNOSTICIAN_SYSTEM = (
    "You are the Diagnostician lens for Icarus. Your role is to "
    "CHARACTERIZE -- not propose. Read the current reasoner source and "
    "the tier target. Identify:\n"
    "  - Which tier the reasoner currently satisfies (R0-R12)\n"
    "  - The specific capability or property missing for the next tier\n"
    "  - What kind of change would close that gap (structural? new operation? "
    "    representation shift? error-handling tighten?)\n"
    "  - Hidden assumptions in the current code that may be fragile\n\n"
    "Do not propose a diff. Stay diagnostic.\n\n"
    "OUTPUT (strict JSON):\n"
    "{\n"
    '  "current_tier_estimate": "R0" | "R1" | ... | "R12",\n'
    '  "gap_to_target": "<1-2 sentences>",\n'
    '  "kind_of_change_needed": "<one of: new_operation, representation_shift, '
    'error_handling, composition, control_flow, other>",\n'
    '  "hidden_assumptions": [<2-4 short strings>],\n'
    '  "qualitative_summary": "<3-5 sentences>",\n'
    '  "axes": {\n'
    '    "tier_proximity": <0.0-1.0; how close is current code to passing target>,\n'
    '    "novelty": <0.0-1.0; how novel is the gap (vs textbook)>,\n'
    '    "regression_risk": <0.0-1.0; 1=LOW risk if we change>,\n'
    '    "structural_simplicity": <0.0-1.0; how clean is the current code>,\n'
    '    "evidence_quality": <0.0-1.0; how well do tests cover claimed tier>\n'
    "  },\n"
    '  "confidence": <0.0-1.0>,\n'
    '  "key_observations": [<3-5 short strings>]\n'
    "}\n"
)


class DiagnosticianLens(Lens):
    name = "diagnostician"
    model_preference = "deepseek"

    def observe(self, ctx: CycleContext) -> LensReport:
        source = _read_source(ctx.source_dir, max_chars=5000)
        user_prompt = (
            f"## Tier target\n"
            f"Tier: {ctx.tier_target}\n"
            f"Falsification test: {ctx.tier_challenge.get('falsification_test', '?')}\n\n"
            f"## Current reasoner source\n```python\n{source}\n```\n\n"
            f"## Recent failure context\n"
            f"Last stable cycle: {ctx.last_stable_id}\n"
            f"Recent parked cycles ({len(ctx.recent_parks)}): "
            f"{'; '.join(p.get('reason', '?')[:60] for p in ctx.recent_parks[:5])}\n\n"
            f"Diagnose."
        )

        result = call_llm(
            preference=self.model_preference,
            system=DIAGNOSTICIAN_SYSTEM,
            user=user_prompt,
            max_tokens=2000,
        )
        text = result.get("text", "")
        parsed = extract_json_block(text)
        if not parsed:
            return LensReport.empty_with_error(
                lens_name=self.name, cycle_n=ctx.cycle_n,
                error="diagnostician_response_not_json",
                model_used=result.get("model_used", "unknown"),
            )

        axes = {a: clamp_axis(parsed.get("axes", {}).get(a, 0.5))
                for a in SCORING_AXES}
        confidence = clamp_axis(parsed.get("confidence", 0.5))
        observations = parsed.get("key_observations", []) or []
        if not isinstance(observations, list):
            observations = [str(observations)]

        # Pack diagnostic info into key_observations + qualitative_summary
        observations_full = [
            f"current_tier={parsed.get('current_tier_estimate', '?')}",
            f"kind_needed={parsed.get('kind_of_change_needed', '?')}",
            f"gap={parsed.get('gap_to_target', '')[:200]}",
        ]
        for hyp in (parsed.get("hidden_assumptions") or [])[:3]:
            observations_full.append(f"hidden_assumption: {str(hyp)[:200]}")
        for o in observations[:3]:
            observations_full.append(str(o)[:300])

        return LensReport(
            lens_name=self.name,
            model_used=result.get("model_used", "unknown"),
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=parsed.get("qualitative_summary", "")[:1500],
            axes=axes,
            confidence=confidence,
            key_observations=observations_full[:8],
            raw_response_excerpt=text[:500],
            tokens_used=result.get("tokens_used", 0),
            cost_estimate_usd=result.get("cost_estimate_usd", 0.0),
        )


def _read_source(source_dir, max_chars: int = 30000) -> str:
    if not source_dir.exists():
        return ""
    chunks = []
    total = 0
    for p in sorted(source_dir.rglob("*.py")):
        if "__pycache__" in str(p) or "/tests/" in str(p).replace("\\", "/"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = p.relative_to(source_dir)
        header = f"\n--- {rel} ---\n"
        remaining = max_chars - total - len(header)
        if remaining <= 0:
            chunks.append(f"{header}[omitted: char budget exhausted]\n")
            break
        # Truncate an oversized file's BODY into the remaining budget instead
        # of dropping it whole -- a single file larger than max_chars used to
        # blank the entire source, leaving lenses to (correctly) report the
        # reasoner as "empty/missing" when it was merely too big to fit.
        if len(text) > remaining:
            chunks.append(f"{header}{text[:remaining]}\n[... truncated]\n")
            break
        chunks.append(f"{header}{text}\n")
        total += len(header) + len(text) + 1
    return "".join(chunks)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
