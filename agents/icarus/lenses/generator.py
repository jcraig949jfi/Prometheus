"""
Generator lens -- proposes a concrete diff with rationale.

Successor to the old improve.propose_diff(). Reads upstream Diagnostician
+ Historian reports before proposing so it can target the most-acute gap.

Model preference: Claude Sonnet (best at code-diff generation in our toolbox).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from lenses._base import Lens, LensReport, CycleContext, SCORING_AXES
from lenses._llm import call_llm, extract_json_block, clamp_axis


GENERATOR_SYSTEM = (
    "You are the Generator lens for Icarus, a self-improving agent climbing "
    "Harmonia B's testable reasoning ladder. Your role: propose ONE concrete "
    "unified-diff change to Icarus's reasoner code that lets it pass the current "
    "tier's probes under perturbation.\n\n"
    "THE REASONER INTERFACE (in reasoner.py):\n"
    "    reason(probe) -> (answer, trace_dict)\n"
    "where `probe` is a harmonia.experiments.reasoning_phase0.Probe with fields "
    "`tier, version (clean|iso|adversarial|transfer), kind, data, ground_truth`. "
    "The substrate is Python + sympy (import sympy as sp). probe.data holds "
    "sympy expressions, e.g. R0/R1 probe.data['expr'], R2 probe.data['a','b','eq'], "
    "R3 probe.data['num','den','rhs','excluded'], R6 probe.data['cid','cex'], "
    "R7 probe.data['steps'].\n\n"
    "HOW YOU ARE GRADED: a DETERMINISTIC verifier lens (sympy/z3) checks your "
    "answer by SUBSTITUTION into the original problem, on a HELD-OUT probe seed "
    "you never see. You CANNOT cheat by returning probe.ground_truth or by "
    "hardcoding -- you must implement the real reasoning move. Each tier wants a "
    "specific move (e.g. R2: square then reject extraneous roots by checking the "
    "ORIGINAL sqrt equation; R3: cancel but exclude the singular value).\n\n"
    "STRICT CONSTRAINTS:\n"
    "1. Diff must be <=100 lines.\n"
    "2. Diff must be valid unified-diff format that `git apply -p1` will accept. "
    "Reproduce CONTEXT LINES EXACTLY from the source -- do not paraphrase or "
    "modify them. If you cannot reproduce a context line verbatim, omit it.\n"
    "3. Only modify reasoner.py or strategy.py. Never modify daemon.py, "
    "lineage.py, lenses/, ladder.py, tier_oracle.py, ladder_eval.py.\n"
    "4. No defensive wrappers / broad try/except / scaffolding that masks "
    "failure. Make a real reasoning change. Do NOT special-case probe.version "
    "or read probe.ground_truth -- the held-out grader will catch it.\n\n"
    "You will be given upstream lens reports (Diagnostician, Historian) + the "
    "kill_patterns from the last attempt. Target the gap; avoid recurring "
    "failure modes.\n\n"
    "OUTPUT (strict JSON, no prose around it):\n"
    "{\n"
    '  "diff": "<unified diff as a single string with \\n line breaks>",\n'
    '  "rationale": "<2-4 sentences explaining the change>",\n'
    '  "axes": {\n'
    '    "tier_proximity": <0.0-1.0>,\n'
    '    "novelty": <0.0-1.0>,\n'
    '    "regression_risk": <0.0-1.0>,  (1.0 = LOW risk, 0.0 = HIGH risk)\n'
    '    "structural_simplicity": <0.0-1.0>,\n'
    '    "evidence_quality": <0.0-1.0>\n'
    "  },\n"
    '  "confidence": <0.0-1.0>,\n'
    '  "key_observations": [<2-4 short strings>]\n'
    "}\n"
)


_STRATEGY_MODIFIERS = {
    "minimal": (
        "STRATEGY for this cycle: MINIMAL. The smallest possible diff that "
        "moves toward the tier target. Bias toward 1-3 line changes. If the "
        "current code is already close, a clarifying docstring or one new "
        "test counts. Prefer evidence-building over architecture change."
    ),
    "structural": (
        "STRATEGY for this cycle: STRUCTURAL. Address the underlying mechanism "
        "the Diagnostician identified. Acceptable to add or refactor methods, "
        "as long as the diff stays under 100 lines and existing tests still "
        "pass. Aim for a load-bearing improvement, not just a clarification."
    ),
    "exploratory": (
        "STRATEGY for this cycle: EXPLORATORY. Try a representation shift "
        "or a different decomposition than the obvious one. Acceptable to "
        "experiment with structure even if benefit is uncertain. Skeptic "
        "and TDD will catch errors -- the goal is to expose new ground."
    ),
}


class GeneratorLens(Lens):
    name = "generator"
    model_preference = "claude_sonnet"

    def observe(self, ctx: CycleContext) -> LensReport:
        source = _read_source(ctx.source_dir)
        diag_summary = _lens_excerpt(ctx.diagnostician_report)
        hist_summary = _lens_excerpt(ctx.historian_report)
        strategy_modifier = _STRATEGY_MODIFIERS.get(
            ctx.cycle_strategy, _STRATEGY_MODIFIERS["structural"]
        )

        debt_block = _debt_block(ctx.open_debts)
        direction_block = _failure_direction_block(ctx)

        user_prompt = (
            f"## Cycle strategy\n{strategy_modifier}\n\n"
            f"{debt_block}"
            f"## Tier challenge\n"
            f"Tier target: {ctx.tier_target}\n"
            f"Falsification test: {ctx.tier_challenge.get('falsification_test', '?')}\n\n"
            f"{direction_block}"
            f"## Diagnostician's read\n{diag_summary}\n\n"
            f"## Historian's read\n{hist_summary}\n\n"
            f"## Current reasoner source\n```python\n{source}\n```\n\n"
            f"Propose one diff."
        )

        result = call_llm(
            preference=self.model_preference,
            system=GENERATOR_SYSTEM,
            user=user_prompt,
            max_tokens=3500,
        )
        text = result.get("text", "")
        parsed = extract_json_block(text)
        if not parsed:
            return LensReport.empty_with_error(
                lens_name=self.name, cycle_n=ctx.cycle_n,
                error="generator_response_not_json",
                model_used=result.get("model_used", "unknown"),
            )

        diff = parsed.get("diff", "")
        rationale = parsed.get("rationale", "")
        axes = {a: clamp_axis(parsed.get("axes", {}).get(a, 0.5))
                for a in SCORING_AXES}
        confidence = clamp_axis(parsed.get("confidence", 0.5))
        observations = parsed.get("key_observations", []) or []
        if not isinstance(observations, list):
            observations = [str(observations)]

        # The diff goes in suggested_actions[0] so the panel can extract it
        return LensReport(
            lens_name=self.name,
            model_used=result.get("model_used", "unknown"),
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=rationale,
            axes=axes,
            confidence=confidence,
            key_observations=[str(o)[:300] for o in observations[:6]],
            suggested_actions=[diff],  # [0] is the diff
            raw_response_excerpt=text[:500],
            tokens_used=result.get("tokens_used", 0),
            cost_estimate_usd=result.get("cost_estimate_usd", 0.0),
        )


def _read_source(source_dir, max_chars: int = 6000) -> str:
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
        snippet = f"\n--- {rel} ---\n{text}\n"
        if total + len(snippet) > max_chars:
            chunks.append(f"\n--- {rel} ---\n[truncated]\n")
            break
        chunks.append(snippet)
        total += len(snippet)
    return "".join(chunks)


def _failure_direction_block(ctx) -> str:
    """Render the probe schema (proactive) + prior-cycle candidate exception
    (reactive). This is how failure emits direction: the Generator sees the
    exact fields the current tier's probe carries and the actual error the last
    attempt hit, instead of guessing the schema and silently KeyError-ing."""
    parts = []
    schema = getattr(ctx, "tier_probe_schema", None)
    if schema and not schema.get("error"):
        fields = schema.get("data_fields", {})
        field_lines = "\n".join(
            f"    probe.data['{k}']  -> {v['type']}  e.g. {v['sample']}"
            for k, v in fields.items()
        )
        parts.append(
            f"## Probe schema for {schema.get('tier')} (kind='{schema.get('kind')}') "
            f"-- READ THESE EXACT INPUT FIELDS\n"
            f"probe.version in {schema.get('versions')}\n"
            f"{field_lines}\n"
            f"(For the required OUTPUT/answer format, follow the Tier challenge "
            f"description above -- do NOT read probe.ground_truth.)\n"
        )
    fd = getattr(ctx, "last_failure_direction", None)
    if fd and fd.get("candidate_exception"):
        parts.append(
            f"## Last attempt's ACTUAL error (fix this exact failure)\n"
            f"On a '{fd.get('exception_on_version')}' probe, the reasoner raised:\n"
            f"```\n{fd.get('candidate_exception')}\n```\n"
        )
    return ("\n".join(parts) + "\n") if parts else ""


def _debt_block(open_debts: list) -> str:
    """Render open debts as a MANDATORY-action block for the Generator."""
    if not open_debts:
        return ""
    lines = [
        "## OPEN DEBTS (mandatory follow-up -- a prior cycle promoted despite "
        "these concerns; you MUST write a regression test addressing one of "
        "them this cycle, in tests/generated/, OR your diff should explicitly "
        "fix the underlying issue):"
    ]
    for d in open_debts[:5]:
        lines.append(
            f"- [{d.get('source')}] {d.get('concern', '')[:200]} "
            f"(suggested test: {d.get('regression_test_to_write') or 'unspecified'})"
        )
    return "\n".join(lines) + "\n\n"


def _lens_excerpt(report) -> str:
    if report is None:
        return "_(no report available)_"
    if report.error:
        return f"_(lens error: {report.error})_"
    obs = "\n".join(f"- {o}" for o in report.key_observations[:4])
    return (
        f"Summary: {report.qualitative_summary[:400]}\n"
        f"Confidence: {report.confidence:.2f}\n"
        f"{obs}"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
