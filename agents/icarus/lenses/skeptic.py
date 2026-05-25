"""
Skeptic lens -- the dissenter. Carries the minority-report obligation.

Runs AFTER the diff is applied and TDD has been measured. Its job is to
find what's STILL broken even when TDD passes. Looks for hidden assumptions,
brittleness, places where the new diff might not generalize.

Asymmetric model selection (per spec v0.2 Shift 2): uses a different family
than the Generator. Generator = Claude, so Skeptic = Gemini.

Skeptic populates minority_position when its view differs strongly from the
panel consensus. The Integrator MUST address the minority position in its
rationale.

Model preference: Gemini (different family than Generator's Claude).
"""
from __future__ import annotations

import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from lenses._base import Lens, LensReport, CycleContext, SCORING_AXES
from lenses._llm import call_llm, extract_json_block, clamp_axis


SKEPTIC_SYSTEM = (
    "You are the Skeptic lens for Icarus. Your role: ASSUME the proposed "
    "diff is wrong somewhere, and find where.\n\n"
    "You have minority-report obligation: if you see something the panel "
    "may miss, you must flag it as your minority_position even if everything "
    "else looks fine.\n\n"
    "Focus on:\n"
    "- Hidden assumptions the diff makes about input shape\n"
    "- Boundary cases the tier-falsification tests don't probe (zero, "
    "  negative, identity element, very large, very small, types just outside "
    "  the expected)\n"
    "- Whether the diff actually closes the tier gap or just papers over it\n"
    "- Whether the diff introduces brittleness that will break NEXT tier's test\n\n"
    "Also: generate 3-5 concrete adversarial probe inputs (JSON-serializable) "
    "and predict the reasoner's behavior. These will be EXECUTED.\n\n"
    "OUTPUT (strict JSON):\n"
    "{\n"
    '  "qualitative_summary": "<3-5 sentences of skepticism>",\n'
    '  "minority_position": <string or null; non-null if you see something major>,\n'
    '  "probes": [\n'
    "    {\n"
    '      "name": "<slug>",\n'
    '      "input": <json-serializable input to reasoner.apply()>,\n'
    '      "expected": <expected output, or "None">,\n'
    '      "why_this_breaks": "<one sentence>"\n'
    "    }\n"
    "  ],\n"
    '  "axes": {\n'
    '    "tier_proximity": <0.0-1.0; 1.0=truly closes the tier gap>,\n'
    '    "novelty": <0.0-1.0; meaningfully novel>,\n'
    '    "regression_risk": <0.0-1.0; 1=LOW risk, 0=HIGH>,\n'
    '    "structural_simplicity": <0.0-1.0>,\n'
    '    "evidence_quality": <0.0-1.0; is there real proof not just TDD theater>\n'
    "  },\n"
    '  "confidence": <0.0-1.0>,\n'
    '  "key_observations": [<2-5 strings, skeptical-flavored>]\n'
    "}\n"
)


class SkepticLens(Lens):
    name = "skeptic"
    model_preference = "gemini"

    def observe(self, ctx: CycleContext) -> LensReport:
        diff_text = ctx.proposed_diff or ""
        source = _read_source(ctx.source_dir)
        tdd_summary = json.dumps(ctx.tdd_result or {}, default=str)[:1000]

        user_prompt = (
            f"## Tier challenge\n"
            f"Tier: {ctx.tier_target}\n"
            f"Falsification test: {ctx.tier_challenge.get('falsification_test', '?')}\n\n"
            f"## Diff that was applied\n```diff\n{diff_text[:3500]}\n```\n\n"
            f"## TDD result\n{tdd_summary}\n\n"
            f"## Current reasoner (post-apply)\n```python\n{source[:4000]}\n```\n\n"
            f"Be skeptical."
        )

        result = call_llm(
            preference=self.model_preference,
            system=SKEPTIC_SYSTEM,
            user=user_prompt,
            max_tokens=2500,
        )
        text = result.get("text", "")
        parsed = extract_json_block(text)
        if not parsed:
            return LensReport.empty_with_error(
                lens_name=self.name, cycle_n=ctx.cycle_n,
                error="skeptic_response_not_json",
                model_used=result.get("model_used", "unknown"),
            )

        # Execute the probes against the (already-applied) reasoner
        probes = parsed.get("probes") or []
        probe_results = []
        breaks = 0
        for probe in probes[:6]:
            r = _run_probe(probe, ctx.source_dir)
            probe_results.append({"probe": probe, "result": r})
            if not r.get("passed", True):
                breaks += 1

        axes = {a: clamp_axis(parsed.get("axes", {}).get(a, 0.5))
                for a in SCORING_AXES}
        # Downweight evidence_quality + tier_proximity if probes broke
        if probes:
            break_ratio = breaks / max(1, len(probes))
            axes["evidence_quality"] = max(0.0, axes["evidence_quality"] - break_ratio * 0.5)
            axes["tier_proximity"] = max(0.0, axes["tier_proximity"] - break_ratio * 0.5)
            # regression_risk in our schema: 1=LOW risk. Probes breaking means HIGH risk.
            axes["regression_risk"] = max(0.0, axes["regression_risk"] - break_ratio * 0.5)

        confidence = clamp_axis(parsed.get("confidence", 0.5))
        minority = parsed.get("minority_position")
        if isinstance(minority, str) and minority.strip().lower() in ("null", "none", ""):
            minority = None

        observations = [str(o)[:300] for o in (parsed.get("key_observations") or [])[:4]]
        observations.append(f"probes_run={len(probes)} probes_failed={breaks}")
        if breaks > 0:
            broken_names = [r["probe"].get("name", "?") for r in probe_results
                           if not r["result"].get("passed", True)]
            observations.append(f"probes_failed_on: {', '.join(broken_names[:5])}")

        return LensReport(
            lens_name=self.name,
            model_used=result.get("model_used", "unknown"),
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=parsed.get("qualitative_summary", "")[:1500],
            axes=axes,
            confidence=confidence,
            key_observations=observations[:10],
            minority_position=minority,
            suggested_actions=[json.dumps(p, default=str) for p in probe_results[:6]],
            raw_response_excerpt=text[:500],
            tokens_used=result.get("tokens_used", 0),
            cost_estimate_usd=result.get("cost_estimate_usd", 0.0),
        )


def _read_source(source_dir, max_chars: int = 4000) -> str:
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
            break
        chunks.append(snippet)
        total += len(snippet)
    return "".join(chunks)


def _run_probe(probe: dict, source_dir: Path) -> dict:
    """Execute a probe by importing the reasoner and feeding it the probe's
    input. Subprocess-isolated to avoid polluting the daemon's interpreter."""
    probe_input = probe.get("input")
    expected = probe.get("expected")
    if probe_input is None and expected is None:
        return {"passed": True, "detail": "empty_probe_skipped"}

    runner_script = (
        f"import json, sys\n"
        f"sys.path.insert(0, r'{source_dir}')\n"
        f"try:\n"
        f"    from reasoner import Reasoner\n"
        f"    r = Reasoner()\n"
        f"    result = r.apply({probe_input!r})\n"
        f"    print(json.dumps({{'ok': True, 'result': result}}, default=str))\n"
        f"except Exception as e:\n"
        f"    print(json.dumps({{'ok': False, 'error': str(e), "
        f"'error_type': type(e).__name__}}))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", runner_script],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0:
            return {"passed": False, "detail": f"crash: {proc.stderr[:200]}"}
        try:
            actual = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            return {"passed": False, "detail": f"parse_fail: {proc.stdout[:200]}"}
        if not actual.get("ok"):
            if expected in (None, "None", "null"):
                return {"passed": True, "detail": "returned_None_as_expected"}
            return {"passed": False, "detail": f"raised: {actual.get('error', '')[:200]}"}
        actual_val = actual.get("result")
        if _values_match(actual_val, expected):
            return {"passed": True, "actual": actual_val}
        return {"passed": False,
                "detail": f"mismatch: expected={expected!r} actual={actual_val!r}",
                "actual": actual_val, "expected": expected}
    except subprocess.TimeoutExpired:
        return {"passed": False, "detail": "probe_timeout"}
    except Exception as e:
        return {"passed": False, "detail": f"probe_runner_error: {e}"}


def _values_match(actual, expected) -> bool:
    if expected in ("None", "null", None) and actual is None:
        return True
    try:
        return actual == expected
    except Exception:
        return False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
