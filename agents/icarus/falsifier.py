"""
Icarus Falsifier sub-agent (co-evolving) -- spec v0.2 sect "Shift 2".

The independent verifier in the hot loop. Runs AFTER TDD passes but BEFORE
the freeze decision. Uses a DIFFERENT model than Icarus's Improve() backend
to break the shared-weights tautology trap.

Asymmetric model selection:
  Icarus Improve() backend  ->  Falsifier model
  claude                    ->  Gemini
  chimera (human-in-loop)   ->  Claude API
  qwen_menial               ->  Claude API

Per-cycle: generate fresh-seed adversarial probes, run them, produce a
structured falsifier_report.md, return verdict.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")

_REPO_ROOT = Path(r"D:\Prometheus")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_falsifier_review(
    cycle_n: int,
    source_dir: Path,
    tier_challenge: dict,
    proposed_diff: str,
    icarus_improve_backend: str,
) -> dict:
    """Run an independent-model adversarial review of the cycle's diff.

    Returns:
        {
          "verdict": "approved" | "rejected" | "inconclusive",
          "probes_attempted": int,
          "probes_failed": int,
          "diagnosis": str,
          "report_path": str,
          "model_used": str,
        }
    """
    # Asymmetric model selection
    falsifier_model = _select_falsifier_model(icarus_improve_backend)

    # If diff is empty, nothing to falsify
    if not proposed_diff or not proposed_diff.strip():
        return _write_report(
            cycle_n=cycle_n,
            verdict="inconclusive",
            probes_attempted=0,
            probes_failed=0,
            diagnosis="empty_diff_nothing_to_review",
            model_used=falsifier_model,
        )

    # Try to call the falsifier model
    try:
        probes = _generate_adversarial_probes(
            tier_challenge=tier_challenge,
            diff=proposed_diff,
            source_dir=source_dir,
            model=falsifier_model,
        )
    except Exception as e:
        return _write_report(
            cycle_n=cycle_n,
            verdict="inconclusive",
            probes_attempted=0,
            probes_failed=0,
            diagnosis=f"falsifier_model_unavailable: {e}",
            model_used=falsifier_model,
        )

    # Run each probe against the diff'd source (Phase 0: shallow check;
    # Phase 1+ will apply the diff in a sandbox and actually run probes)
    breaks = []
    for probe in probes:
        result = _run_probe(probe, source_dir, proposed_diff)
        if not result.get("passed", True):
            breaks.append({"probe": probe, "result": result})

    verdict = "rejected" if breaks else "approved"
    diagnosis = (
        f"{len(breaks)} of {len(probes)} probes found breaks"
        if breaks else
        f"all {len(probes)} probes passed; no breaks found"
    )

    return _write_report(
        cycle_n=cycle_n,
        verdict=verdict,
        probes_attempted=len(probes),
        probes_failed=len(breaks),
        diagnosis=diagnosis,
        model_used=falsifier_model,
        probes=probes,
        breaks=breaks,
    )


def _select_falsifier_model(icarus_backend: str) -> str:
    """Asymmetric model selection per spec v0.2 Shift 2."""
    if icarus_backend == "claude":
        return "gemini"
    if icarus_backend in ("chimera_pending", "chimera_consumed", "chimera"):
        return "claude"
    if icarus_backend == "qwen_menial":
        return "claude"
    return "claude"  # default


_FALSIFIER_SYSTEM = (
    "You are the Falsifier sub-agent for Icarus, a self-improving reasoning "
    "agent. Your job is to BREAK proposed code changes -- find inputs that "
    "expose hidden assumptions, brittleness, or surface-pattern matching.\n\n"
    "You will receive: (1) a tier challenge, (2) a unified diff of the "
    "proposed change, (3) a brief description of the reasoner's public API.\n\n"
    "Generate exactly 5 adversarial probes. Each probe is a JSON object:\n"
    "  {\n"
    "    \"name\": <slug>,\n"
    "    \"kind\": \"perturbation\" | \"boundary\" | \"null\" | \"structural\" | \"regression\",\n"
    "    \"input\": <JSON-serializable input to reasoner.apply()>,\n"
    "    \"expected\": <expected output for that input, or \"None\" if invalid>,\n"
    "    \"why_this_breaks\": <one-sentence rationale>\n"
    "  }\n\n"
    "Return ONLY a JSON array of 5 probe objects. No prose. No code blocks.\n"
    "Each probe must be EXECUTABLE -- the input must be valid JSON, and the "
    "expected output must be deterministic.\n\n"
    "Focus on:\n"
    "- Type confusion (string where int expected, None, bool-as-int)\n"
    "- Boundary cases (zero, very large, negative, identity element)\n"
    "- Operation diversity (does the diff handle ALL claimed ops?)\n"
    "- Hidden assumptions in the diff's logic\n"
)


def _generate_adversarial_probes(
    tier_challenge: dict,
    diff: str,
    source_dir: Path,
    model: str,
) -> list[dict]:
    """Phase 1b: actually call the falsifier model to generate probes.

    model is "gemini" or "claude" -- per asymmetric selection.
    """
    api_description = _summarize_reasoner_api(source_dir)
    user_prompt = (
        f"## Tier challenge\n"
        f"Tier: {tier_challenge.get('tier', '?')}\n"
        f"Falsification test: {tier_challenge.get('falsification_test', '?')}\n\n"
        f"## Reasoner API summary\n{api_description}\n\n"
        f"## Proposed diff\n```diff\n{diff[:4000]}\n```\n\n"
        f"Generate 5 adversarial probes that target this diff."
    )

    if model == "gemini":
        return _gemini_probes(user_prompt)
    return _claude_probes(user_prompt)


def _summarize_reasoner_api(source_dir: Path) -> str:
    """Read reasoner.py and extract the public API surface for the Falsifier."""
    reasoner_path = source_dir / "reasoner.py"
    if not reasoner_path.exists():
        return "(reasoner.py not found)"
    try:
        text = reasoner_path.read_text(encoding="utf-8", errors="ignore")
        # Strip comments and trim to 2000 chars
        return text[:2000]
    except Exception:
        return "(reasoner.py unreadable)"


def _gemini_probes(user_prompt: str) -> list[dict]:
    """Call Gemini to generate adversarial probes. Returns list of probe dicts."""
    try:
        from keys import get_key  # type: ignore
        import google.generativeai as genai
        api_key = get_key("GEMINI")
        genai.configure(api_key=api_key)
        model_obj = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=_FALSIFIER_SYSTEM,
        )
        resp = model_obj.generate_content(user_prompt)
        return _parse_probes_from_text(resp.text or "")
    except ImportError:
        # google-generativeai not installed; bail to Claude
        return _claude_probes(user_prompt)
    except Exception as e:
        print(f"[falsifier] gemini call failed: {e}; falling back to claude",
              file=sys.stderr)
        return _claude_probes(user_prompt)


def _claude_probes(user_prompt: str) -> list[dict]:
    """Call Claude with the adversarial role + minimal context."""
    try:
        from keys import get_key  # type: ignore
        from anthropic import Anthropic
        api_key = get_key("CLAUDE")
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=_FALSIFIER_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = resp.content[0].text if resp.content else ""
        return _parse_probes_from_text(text)
    except Exception as e:
        print(f"[falsifier] claude call failed: {e}", file=sys.stderr)
        return []


def _parse_probes_from_text(text: str) -> list[dict]:
    """Extract a JSON array of probes from the model's response."""
    import re
    text = text.strip()
    # Strip code fences if model added them
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data[:10]  # cap at 10 probes
    except Exception as e:
        print(f"[falsifier] probe parse failed: {e}", file=sys.stderr)
    return []


def _run_probe(probe: dict, source_dir: Path, diff: str) -> dict:
    """Phase 1b: execute the probe by importing the (already-patched) reasoner
    and feeding it the probe's input. Compare against expected.

    The diff has already been applied to source_dir by the daemon's
    step_1b_apply_diff, so we can just import and call.
    """
    probe_input = probe.get("input")
    expected = probe.get("expected")

    if probe_input is None:
        return {"passed": True, "detail": "no_input_provided_skip"}

    # Subprocess-isolated import + call (so we don't pollute the daemon's
    # interpreter with stale imports across cycles)
    runner_script = (
        f"import json, sys\n"
        f"sys.path.insert(0, r'{source_dir}')\n"
        f"try:\n"
        f"    from reasoner import Reasoner\n"
        f"    r = Reasoner()\n"
        f"    result = r.apply({probe_input!r})\n"
        f"    print(json.dumps({{'ok': True, 'result': result}}))\n"
        f"except Exception as e:\n"
        f"    print(json.dumps({{'ok': False, 'error': str(e), 'error_type': type(e).__name__}}))\n"
    )
    try:
        import subprocess
        proc = subprocess.run(
            [sys.executable, "-c", runner_script],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0:
            return {
                "passed": False,
                "detail": f"reasoner_crashed: {proc.stderr[:200]}",
                "expected": expected,
            }
        try:
            actual = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            return {
                "passed": False,
                "detail": f"could_not_parse_reasoner_output: {proc.stdout[:200]}",
                "expected": expected,
            }
        if not actual.get("ok"):
            # Reasoner raised; that's a probe FAIL if expected wasn't None
            if expected in (None, "None", "null"):
                return {"passed": True, "detail": "reasoner_returned_None_as_expected"}
            return {
                "passed": False,
                "detail": f"reasoner_raised_{actual.get('error_type')}: {actual.get('error', '')[:200]}",
                "expected": expected,
            }
        actual_result = actual.get("result")
        # Compare with type-tolerant equality (1 == 1.0 ok)
        if _values_match(actual_result, expected):
            return {"passed": True, "actual": actual_result, "expected": expected}
        return {
            "passed": False,
            "detail": f"mismatch: expected={expected!r} actual={actual_result!r}",
            "expected": expected, "actual": actual_result,
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "detail": "probe_timeout_10s"}
    except Exception as e:
        return {"passed": False, "detail": f"probe_runner_error: {e}"}


def _values_match(actual, expected) -> bool:
    """Type-tolerant equality. Strings 'None' / 'null' match Python None."""
    if expected in ("None", "null", None) and actual is None:
        return True
    try:
        return actual == expected
    except Exception:
        return False


def _write_report(
    cycle_n: int,
    verdict: str,
    probes_attempted: int,
    probes_failed: int,
    diagnosis: str,
    model_used: str,
    probes: Optional[list] = None,
    breaks: Optional[list] = None,
) -> dict:
    """Write the falsifier_report.md and return the verdict dict."""
    from lineage import cycle_path
    cp = cycle_path(cycle_n)
    cp.mkdir(parents=True, exist_ok=True)
    report_path = cp / "falsifier_report.md"

    lines = [
        f"# Falsifier Report -- cycle {cycle_n}",
        "",
        f"- **Verdict:** {verdict}",
        f"- **Probes attempted:** {probes_attempted}",
        f"- **Probes failed:** {probes_failed}",
        f"- **Model used:** {model_used}",
        f"- **Generated at:** {_now_iso()}",
        "",
        "## Diagnosis",
        "",
        diagnosis,
        "",
    ]
    if probes:
        lines.append("## Probes attempted")
        lines.append("")
        for p in probes:
            lines.append(f"- **{p.get('name')}** ({p.get('kind', '?')}): {p.get('expected', '')}")
        lines.append("")
    if breaks:
        lines.append("## Breaks found")
        lines.append("")
        for b in breaks:
            lines.append(f"- **{b['probe'].get('name')}**: {b['result'].get('detail', '')}")
        lines.append("")

    try:
        report_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        print(f"[falsifier] report write failed: {e}", file=sys.stderr)

    return {
        "verdict": verdict,
        "probes_attempted": probes_attempted,
        "probes_failed": probes_failed,
        "diagnosis": diagnosis,
        "report_path": str(report_path),
        "model_used": model_used,
    }
