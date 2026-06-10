"""
Icarus Improve() function -- 3-backend Chimera architecture.

Per spec v0.2 sect "Shift 1: Chimera Improve() -- 3 backends with explicit
fallback":

  Backend 1 (primary):  CLAUDE API     -- synchronous, in-cycle
  Backend 2 (fallback): CHIMERA MODE   -- asynchronous via outbox/inbox
  Backend 3 (menial):   QWEN CODER     -- local Ollama; ONLY for menial tasks

The dispatch policy: try Claude first; on failure or budget-exhaust, fall
through to Chimera. Qwen menial is invoked separately for ancillary tasks.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")
STATE_DIR = ICARUS_DIR / "state"
OUTBOX_DIR = ICARUS_DIR / "chimera_outbox"
INBOX_DIR = ICARUS_DIR / "chimera_inbox"

DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-6"
FALLBACK_CLAUDE_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_DAILY_TOKEN_CAP = 200_000
MIN_TOKENS_TO_ATTEMPT_CLAUDE = 12_000

# Path to repo root so we can pick up keys.py
_REPO_ROOT = Path(r"D:\Prometheus")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ---------------------------------------------------------------------------
# Prompt-injection sanitizer (per spec v0.2 #11)
# ---------------------------------------------------------------------------

import re

_INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions"),
    re.compile(r"(?i)disregard\s+(?:the\s+)?(?:system|prior|previous)\s+prompt"),
    re.compile(r"<\|im_start\|>\s*system"),
    re.compile(r"<system-reminder>"),
    re.compile(r"</?system>"),
    re.compile(r"^###\s+Instruction:", re.MULTILINE),
    re.compile(r"^\s*(?:###|#)\s*system\b", re.IGNORECASE | re.MULTILINE),
]


def sanitize_external(text: str) -> str:
    """Strip injection-looking patterns; wrap with delimiters so the LLM
    treats this as external content, not instructions."""
    if not text:
        return ""
    cleaned = text
    for pat in _INJECTION_PATTERNS:
        cleaned = pat.sub("[SANITIZED]", cleaned)
    return f"<<<EXTERNAL>>>\n{cleaned}\n<<</EXTERNAL>>>"


# ---------------------------------------------------------------------------
# Claude API backend
# ---------------------------------------------------------------------------

_anthropic_client = None


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is not None:
        return _anthropic_client
    try:
        from keys import get_key  # type: ignore
        from anthropic import Anthropic
        api_key = get_key("CLAUDE")
        _anthropic_client = Anthropic(api_key=api_key)
        return _anthropic_client
    except Exception as e:
        print(f"[improve] Anthropic client unavailable: {e}", file=sys.stderr)
        return None


def _claude_token_budget_remaining() -> int:
    """Read state/claude_token_usage_<today>.json + claude_daily_cap.json
    and return tokens-remaining-today."""
    cap_data = _read_json(STATE_DIR / "claude_daily_cap.json",
                          {"daily_cap": DEFAULT_DAILY_TOKEN_CAP})
    cap = int(cap_data.get("daily_cap", DEFAULT_DAILY_TOKEN_CAP))
    usage_path = STATE_DIR / f"claude_token_usage_{_today_iso()}.json"
    usage = _read_json(usage_path, {"used": 0})
    return cap - int(usage.get("used", 0))


def _claude_token_record(tokens_used: int) -> None:
    usage_path = STATE_DIR / f"claude_token_usage_{_today_iso()}.json"
    usage = _read_json(usage_path, {"used": 0, "calls": 0})
    usage["used"] = int(usage.get("used", 0)) + int(tokens_used)
    usage["calls"] = int(usage.get("calls", 0)) + 1
    usage["last_call_at"] = _now_iso()
    _write_json(usage_path, usage)


def _read_source_summary(source_dir: Path, max_chars: int = 8000) -> str:
    """Cheap summary of the source: concatenate the .py files, trimmed.
    For Phase 0; later cycles may use diff against bootstrap or AST-based
    summaries."""
    if not source_dir.exists():
        return ""
    chunks: list[str] = []
    total = 0
    for p in sorted(source_dir.rglob("*.py")):
        if "__pycache__" in str(p):
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


def _build_claude_prompt(
    source_dir: Path,
    tier_challenge: dict,
    failure_context: dict,
    wisdom: str,
) -> tuple[str, str]:
    """Returns (system, user) for the Claude API call."""
    system = (
        "You are Icarus's Improve() function. Icarus is a self-improving "
        "agent in Project Prometheus that climbs a reasoning ladder (R0-R12). "
        "Each cycle, you propose a small unified-diff patch to Icarus's "
        "reasoner code that moves it closer to passing the current tier's "
        "falsification test, without breaking lower-tier tests.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. Diff must be <=100 lines.\n"
        "2. Diff must be valid unified-diff format (apply-able via `patch`).\n"
        "3. Only modify reasoner.py, strategy.py, or files under "
        "generated_tests/. Never modify daemon.py, lineage.py, improve.py, "
        "falsifier.py, ladder.py -- those are FIXED infrastructure.\n"
        "4. The change must be motivated by the tier's falsification test "
        "and informed by the wisdom (prior failures) and failure_context.\n"
        "5. Do NOT add wrappers, broad try/except, or scaffolding designed "
        "to mask failure. Make a real reasoning change.\n\n"
        "OUTPUT FORMAT:\n"
        "```diff\n<unified diff>\n```\n\n"
        "## Rationale\n<2-4 sentences explaining the change>\n"
    )

    wisdom_section = (
        f"## Wisdom (DAG-mined failure patterns)\n{sanitize_external(wisdom)}\n\n"
        if wisdom else ""
    )

    user = (
        f"{wisdom_section}"
        f"## Current tier challenge\n"
        f"Tier: {tier_challenge.get('tier', '?')}\n"
        f"Falsification test: {tier_challenge.get('falsification_test', '?')}\n\n"
        f"## Recent failure context\n"
        f"{json.dumps(failure_context, indent=2)[:2000]}\n\n"
        f"## Current source\n"
        f"{_read_source_summary(source_dir, max_chars=8000)}\n\n"
        f"Propose a diff."
    )
    return system, user


def _call_claude(
    source_dir: Path,
    tier_challenge: dict,
    failure_context: dict,
    wisdom: str,
    model: Optional[str] = None,
) -> Optional[dict]:
    model = model or DEFAULT_CLAUDE_MODEL
    system, user = _build_claude_prompt(source_dir, tier_challenge,
                                         failure_context, wisdom)

    # Loop backend: route through the Claude Code subscription CLI instead of
    # the metered API (James 2026-06-09). Reuses _llm.py's CLI caller.
    from agents.icarus.lenses._llm import _use_loop, _call_claude_cli
    if _use_loop():
        r = _call_claude_cli(system, user, 4000, model)
        if r.get("error"):
            print(f"[improve] loop CLI call failed: {r['error']}", file=sys.stderr)
            return None
        tokens_used = r.get("tokens_used", 0)
        _claude_token_record(tokens_used)
        diff, rationale = _parse_claude_response(r.get("text", ""))
        return {
            "diff": diff,
            "rationale": rationale,
            "tokens_used": tokens_used,
            "cost_estimate_usd": r.get("cost_estimate_usd", 0.0),
            "model_used": f"{model}:loop",
        }

    client = _get_anthropic_client()
    if client is None:
        return None
    try:
        # Use prompt caching for the system + wisdom (which doesn't change
        # per cycle). The newer Anthropic SDK supports cache_control.
        response = client.messages.create(
            model=model,
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        content = response.content[0].text if response.content else ""
        tokens_used = (
            getattr(response.usage, "input_tokens", 0) +
            getattr(response.usage, "output_tokens", 0)
        )
        _claude_token_record(tokens_used)

        diff, rationale = _parse_claude_response(content)
        return {
            "diff": diff,
            "rationale": rationale,
            "tokens_used": tokens_used,
            "cost_estimate_usd": _estimate_cost(model, response.usage),
            "model_used": model,
        }
    except Exception as e:
        print(f"[improve] Claude API call failed: {e}", file=sys.stderr)
        return None


def _parse_claude_response(content: str) -> tuple[str, str]:
    """Extract diff block + rationale from Claude's markdown output."""
    diff = ""
    rationale = ""
    diff_match = re.search(r"```diff\s*\n(.*?)```", content, re.DOTALL)
    if diff_match:
        diff = diff_match.group(1).strip()
    rat_match = re.search(r"##\s+Rationale\s*\n(.*?)(?=\n##|\Z)", content,
                          re.DOTALL | re.IGNORECASE)
    if rat_match:
        rationale = rat_match.group(1).strip()
    return diff, rationale


def _estimate_cost(model: str, usage) -> float:
    """Rough cost estimate in USD. Update with real pricing as needed."""
    in_tokens = getattr(usage, "input_tokens", 0)
    out_tokens = getattr(usage, "output_tokens", 0)
    if "opus" in model.lower():
        return (in_tokens / 1e6) * 15.0 + (out_tokens / 1e6) * 75.0
    if "sonnet" in model.lower():
        return (in_tokens / 1e6) * 3.0 + (out_tokens / 1e6) * 15.0
    return (in_tokens / 1e6) * 0.80 + (out_tokens / 1e6) * 4.0  # haiku-ish


# ---------------------------------------------------------------------------
# Chimera mode (asynchronous outbox)
# ---------------------------------------------------------------------------

def _write_chimera_request(
    cycle_n: int,
    source_dir: Path,
    tier_challenge: dict,
    failure_context: dict,
    wisdom: str,
) -> Path:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    request_id = f"cycle_{cycle_n:03d}_{ts}"
    path = OUTBOX_DIR / f"improve_request_{request_id}.md"

    body = (
        f"# Icarus Improve() Request -- cycle {cycle_n}\n\n"
        f"**Request ID:** `{request_id}`\n"
        f"**Generated at:** {_now_iso()}\n"
        f"**Backend mode:** Chimera (Claude API unavailable or budget-exhausted)\n\n"
        f"---\n\n"
        f"## Tier challenge\n"
        f"- Tier: **{tier_challenge.get('tier', '?')}**\n"
        f"- Falsification test: {tier_challenge.get('falsification_test', '?')}\n\n"
        f"## Recent failure context\n"
        f"```json\n{json.dumps(failure_context, indent=2)[:1500]}\n```\n\n"
        f"## Wisdom (DAG-mined patterns)\n"
        f"{wisdom or '_no patterns yet_'}\n\n"
        f"## Current source\n"
        f"```\n{_read_source_summary(source_dir, max_chars=6000)}\n```\n\n"
        f"---\n\n"
        f"## What I need from you (Harmonia / Claude in conversation)\n\n"
        f"Propose a unified diff (<=100 lines) that moves Icarus closer to\n"
        f"passing the tier challenge above, without breaking lower-tier tests.\n\n"
        f"**Constraints:**\n"
        f"1. Only modify `reasoner.py`, `strategy.py`, or files under `generated_tests/`.\n"
        f"2. Never modify `daemon.py`, `lineage.py`, `improve.py`, `falsifier.py`, `ladder.py`.\n"
        f"3. No defensive wrappers / broad try-except / scaffolding designed to mask failure.\n"
        f"4. Make a real reasoning change, not a syntactic refactor.\n\n"
        f"## Expected response format\n\n"
        f"James will paste your response into:\n"
        f"`D:\\Prometheus\\agents\\icarus\\chimera_inbox\\improve_response_{request_id}.md`\n\n"
        f"Sections required:\n"
        f"- `## Diff` (unified diff in a ```diff code block)\n"
        f"- `## Rationale` (2-4 sentences)\n"
        f"- `## New Tests` (optional; pytest test cases for the change)\n"
        f"- `## Notes` (optional; any context for future cycles)\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Public API: propose_diff
# ---------------------------------------------------------------------------

def propose_diff(
    cycle_n: int,
    source_dir: Path,
    tier_challenge: dict,
    failure_context: Optional[dict] = None,
    wisdom: str = "",
    backend: str = "auto",
) -> dict:
    """Main Improve() entry point. See spec v0.2 §Shift 1 for the 3-backend
    architecture. Returns a dict with keys:
      - backend_used: "claude" | "chimera_pending" | "chimera_consumed" | "no_op"
      - diff: str or None
      - rationale: str
      - tokens_used: int
      - cost_estimate_usd: float
      - request_id: str (for chimera tracking)
    """
    failure_context = failure_context or {}
    result = {
        "backend_used": "no_op",
        "diff": None,
        "rationale": "",
        "tokens_used": 0,
        "cost_estimate_usd": 0.0,
        "request_id": None,
        "model_used": None,
    }

    # Backend-selection
    if backend == "claude" or backend == "auto":
        # Check budget
        remaining = _claude_token_budget_remaining()
        if remaining >= MIN_TOKENS_TO_ATTEMPT_CLAUDE:
            try:
                claude_result = _call_claude(source_dir, tier_challenge,
                                              failure_context, wisdom)
                if claude_result and claude_result.get("diff"):
                    result.update({
                        "backend_used": "claude",
                        "diff": claude_result["diff"],
                        "rationale": claude_result["rationale"],
                        "tokens_used": claude_result["tokens_used"],
                        "cost_estimate_usd": claude_result["cost_estimate_usd"],
                        "model_used": claude_result["model_used"],
                    })
                    return result
            except Exception as e:
                print(f"[improve] claude path failed: {e}", file=sys.stderr)
        if backend == "claude":
            # explicit claude request failed; don't fall through
            result["backend_used"] = "no_op"
            result["rationale"] = "claude_unavailable_or_budget_exhausted"
            return result

    # Chimera fallback
    if backend == "chimera" or backend == "auto":
        # Check inbox first -- maybe a response is already there from a prior
        # cycle's request
        consumed = _consume_chimera_inbox(cycle_n)
        if consumed:
            result.update({
                "backend_used": "chimera_consumed",
                "diff": consumed.get("diff"),
                "rationale": consumed.get("rationale", ""),
                "request_id": consumed.get("request_id"),
            })
            return result

        # No inbox response -- write a new request to outbox
        req_path = _write_chimera_request(
            cycle_n=cycle_n,
            source_dir=source_dir,
            tier_challenge=tier_challenge,
            failure_context=failure_context,
            wisdom=wisdom,
        )
        result.update({
            "backend_used": "chimera_pending",
            "rationale": f"awaiting chimera response at {req_path.name}",
            "request_id": req_path.stem.replace("improve_request_", ""),
        })
        return result

    return result


def _consume_chimera_inbox(cycle_n: int) -> Optional[dict]:
    """Scan chimera_inbox/ for the most-recent improve_response_*.md.
    If one matches a prior request and hasn't been consumed yet, parse and
    return its content."""
    if not INBOX_DIR.exists():
        return None
    seen_path = STATE_DIR / "seen_chimera_responses.json"
    seen = set(_read_json(seen_path, []))
    for p in sorted(INBOX_DIR.glob("improve_response_*.md"),
                    key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name in seen:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        diff = _extract_section(text, "Diff", as_code_block=True)
        rationale = _extract_section(text, "Rationale")
        seen.add(p.name)
        _write_json(seen_path, sorted(seen))
        return {
            "diff": diff,
            "rationale": rationale,
            "request_id": p.stem.replace("improve_response_", ""),
            "consumed_from": str(p),
        }
    return None


def _extract_section(text: str, heading: str, as_code_block: bool = False) -> str:
    """Extract a markdown section by heading."""
    pat = re.compile(rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##|\Z)",
                     re.DOTALL | re.IGNORECASE)
    m = pat.search(text)
    if not m:
        return ""
    body = m.group(1).strip()
    if as_code_block:
        cb = re.search(r"```(?:diff|patch)?\s*\n(.*?)```", body, re.DOTALL)
        if cb:
            return cb.group(1).strip()
    return body


# ---------------------------------------------------------------------------
# Backend 3: Qwen menial (stubbed in Phase 0)
# ---------------------------------------------------------------------------

def menial_task(task_type: str, payload: dict) -> dict:
    """Local Qwen2.5-Coder via Ollama for menial tasks (test stubs,
    docstring gen, syntax checks, renaming). Stubbed in Phase 0 -- returns
    no-op until Ollama is wired in Phase 1."""
    valid_types = ("test_stub", "docstring_gen", "syntax_check", "rename")
    if task_type not in valid_types:
        return {"result": None, "reason": f"unknown task_type: {task_type}"}
    # Phase 0 stub
    return {
        "result": None,
        "reason": "ollama_not_yet_wired",
        "task_type": task_type,
        "stubbed": True,
    }
