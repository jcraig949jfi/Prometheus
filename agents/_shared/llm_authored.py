"""LLM-authored mutations (SelfImprovingDaemon v2c).

When an agent's native menu + compositional menu + borrowed registry +
void predictions are ALL exhausted under stagnation, fire one cheap LLM
call asking for a new mutation tailored to this agent's specific shape
and recent failure history.

This is THE riskiest mechanism in the self-improvement substrate:
  - The LLM produces Python code we did not write
  - That code mutates the agent's tactics
  - Bad code can crash the daemon, corrupt state, or worse

Therefore v2c ships with strict defenses:
  - All LLM proposals require human approval before apply() runs
  - Proposed code is sandboxed (subprocess + restricted imports + time limit)
    BEFORE being marked as runnable (v2c iter 3)
  - Every proposal is logged to an audit trail with full provenance
  - Proposals that crash the sandbox are marked FAILED and not retried
  - The LLM call itself is rate-limited (default: max 1 per day per agent)

v2c iteration 1 (this file): scaffold + contract + stub.
  - Prompt template documented
  - Response schema documented
  - propose_llm_mutation() returns None (no real LLM call yet)
  - Audit log structure defined
  - Mixin integration deferred to iter 3

v2c iteration 2 (next): real LLM call wired (DeepSeek/Anthropic/OpenAI
  via existing keys.get_key infrastructure). Still no sandbox; proposed
  code is stored but not executable.

v2c iteration 3: sandbox executor (subprocess, RestrictedPython-style
  globals, time limit), wire into SelfImprovingDaemon._effective_menu()
  as Tier 4 (the very last resort). Approval ticket flow.

v2c iteration 4: post-execution learning. When a sandboxed LLM mutation
  is approved + kept, its code structure becomes a template the LLM call
  can reference in future proposals ("this kind of mutation worked").
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_LOG = REPO_ROOT / "agents" / "_shared" / "llm_authored_mutations_audit.jsonl"

# Soft import of the existing LLM cascade (DeepSeek + 4 fallbacks).
_SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
try:
    from llm_cascade import call_llm_with_provider
    HAS_LLM_CASCADE = True
except Exception:
    HAS_LLM_CASCADE = False
    call_llm_with_provider = None  # type: ignore

log = logging.getLogger("llm_authored")

# Rate limiting — per-agent default. Subclasses can raise this once
# v2c iter 3+ ships with the sandbox executor.
DEFAULT_MAX_LLM_PROPOSALS_PER_DAY = 1


# ---------------------------------------------------------------------------
# Prompt template (v2c iter 1: documented; iter 2: used)
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """You are an adversarial mutation designer for a self-improving
agent in the Prometheus research substrate.

THE AGENT:
  Name: {agent_name}
  Purpose: {agent_purpose}
  Traits: {agent_traits}
  Current failure modes: {current_failure_modes}

THE STAGNATION:
  Composite health: {composite_health:.2f} (threshold for stagnation: {threshold:.2f})
  Last {history_n} health samples: {health_history}

WHAT'S BEEN TRIED (exhausted menu):
  Native atomic adaptations: {native_names}
  Compositional pairs from native: {compound_names}
  Borrowed from other agents (registry): {borrowed_names}
  Void-predicted from neighbor inference: {void_names}

YOUR TASK:
Propose ONE new mutation as Python code. The mutation must:
  1. Mutate ONLY this agent's tactics (config, paths, modes, keyword sets,
     cached state, internal thresholds). Mission/charter/code are LOCKED.
  2. Be reversible: provide both apply(agent, agent_state) -> snapshot
     and revert(agent, agent_state, snapshot) -> None.
  3. Have non-overlap with the listed exhausted-menu adaptations.
  4. Be small (< 30 lines of code total, apply + revert combined).
  5. Use only the Python standard library. No new dependencies.
  6. Explain in 1-2 sentences WHY this mutation might break the stagnation
     (what hypothesis it tests).

OUTPUT FORMAT (strict JSON, NO prose outside the JSON block):
{{
  "name": "<UPPER_SNAKE_CASE_NAME>",
  "description": "<one-sentence description>",
  "hypothesis": "<one or two sentences: why this might help>",
  "cost": "<trivial | one_tick | medium | high>",
  "reversibility": "manual_via_revert",
  "apply_code": "def apply(agent, agent_state):\\n    # ...\\n    return snapshot",
  "revert_code": "def revert(agent, agent_state, snapshot):\\n    # ..."
}}

CONSTRAINTS:
  - Do NOT propose: file deletion, subprocess execution, network calls,
    importing non-stdlib modules, modifying the agent's CHARTER, modifying
    the agent's daemon.py code, mutating other agents' state.
  - DO propose: changing config dict values, clearing caches, adjusting
    thresholds, switching modes, adding/removing paths from walk roots,
    expanding/contracting regex keyword sets.
"""


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

@dataclass
class LLMAuthoredProposal:
    """One LLM-generated mutation proposal. Lives in audit log."""
    proposal_id: str                # sha256[:16] of (agent_name, prompt_hash, ts)
    agent_name: str
    proposed_at: str
    prompt_hash: str                # sha256[:16] of the rendered prompt
    llm_model: str                  # which model produced this
    raw_response: str               # full text returned by the LLM
    parsed: dict                    # parsed JSON if it parsed, else {}
    parse_succeeded: bool
    name: str = ""                  # parsed.name if available
    description: str = ""
    hypothesis: str = ""
    cost: str = "unknown"
    reversibility: str = "unknown"
    apply_code: str = ""
    revert_code: str = ""
    sandbox_status: str = "untested"  # untested | sandbox_passed | sandbox_failed | applied
    safety_violations: list = field(default_factory=list)
    human_approval: str = "pending"   # pending | approved | rejected
    notes: str = ""


# ---------------------------------------------------------------------------
# Safety pre-checks (run BEFORE sandbox; static analysis)
# ---------------------------------------------------------------------------

FORBIDDEN_TOKENS = (
    "import os", "import subprocess", "import socket", "import urllib",
    "import requests", "import http", "import shutil",
    "open(", "exec(", "eval(", "compile(", "__import__",
    "globals(", "locals(", "vars(", "setattr(", "getattr(",
    "delattr(", "rm ", "unlink(", "rmtree(",
)


def static_safety_check(apply_code: str, revert_code: str) -> list[str]:
    """Cheap textual checks. Returns list of violations; empty list = clean.

    This is necessary-not-sufficient — sandbox executor is the real
    enforcement. Static check catches the obvious cases cheaply."""
    violations = []
    for code, label in [(apply_code, "apply"), (revert_code, "revert")]:
        for tok in FORBIDDEN_TOKENS:
            if tok in code:
                violations.append(f"{label}_code contains forbidden token '{tok}'")
    # Length limit
    total = len(apply_code) + len(revert_code)
    if total > 2000:
        violations.append(f"combined code too long: {total} chars (limit 2000)")
    return violations


# ---------------------------------------------------------------------------
# Audit log (append-only; the source of truth for what LLM proposed)
# ---------------------------------------------------------------------------

def append_to_audit_log(proposal: LLMAuthoredProposal,
                       audit_path: Optional[Path] = None) -> None:
    p = audit_path or DEFAULT_AUDIT_LOG
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(proposal), ensure_ascii=False) + "\n")


def count_today_proposals_for_agent(agent_name: str,
                                    audit_path: Optional[Path] = None) -> int:
    """Rate-limit support. Counts proposals from the given agent that
    were recorded today (UTC)."""
    p = audit_path or DEFAULT_AUDIT_LOG
    if not p.exists():
        return 0
    today = datetime.now(timezone.utc).date().isoformat()
    n = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("agent_name") != agent_name:
            continue
        if (row.get("proposed_at") or "")[:10] == today:
            n += 1
    return n


# ---------------------------------------------------------------------------
# The public API (v2c iter 1: stub; iter 2: real LLM call)
# ---------------------------------------------------------------------------

def _extract_json_from_response(text: str) -> Optional[dict]:
    """LLMs often wrap JSON in ```json ... ``` fences or include preamble.
    Try a few extraction strategies before giving up."""
    if not text:
        return None
    # Strategy 1: raw JSON parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass
    # Strategy 2: extract from ```json ... ``` fence
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            pass
    # Strategy 3: find first balanced {...} block
    start = text.find("{")
    if start >= 0:
        depth = 0
        in_str = False
        esc = False
        for i, ch in enumerate(text[start:], start):
            if esc:
                esc = False
                continue
            if ch == "\\" and in_str:
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except (json.JSONDecodeError, ValueError):
                        return None
    return None


def propose_llm_mutation(
    *,
    agent_name: str,
    agent_purpose: str,
    agent_traits: list[str],
    current_failure_modes: list[str],
    composite_health: float,
    stagnation_threshold: float,
    health_history: list[dict],
    native_names: list[str],
    compound_names: list[str],
    borrowed_names: list[str],
    void_names: list[str],
    max_per_day: int = DEFAULT_MAX_LLM_PROPOSALS_PER_DAY,
    llm_timeout_sec: int = 120,
    llm_max_tokens: int = 1500,
    llm_temperature: float = 0.4,
    audit_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Optional[LLMAuthoredProposal]:
    """Ask an LLM for one new mutation tailored to this agent's stagnation.

    v2c iteration 2: REAL LLM call via the llm_cascade.call_llm_with_provider
    pipeline (DeepSeek primary, 4 fallbacks). Parses JSON response, runs
    static safety check, appends to audit log. Returns the proposal
    regardless of safety violations (caller decides). Does NOT sandbox-execute
    or apply — that's iter 3.

    Returns None when:
      - LLM cascade unavailable (import failed)
      - Rate limit hit (count_today_proposals_for_agent >= max_per_day)
      - All providers in cascade failed
      - dry_run=True (returns None for testing without burning quota)
    """
    if not HAS_LLM_CASCADE:
        log.warning("llm_cascade not importable; v2c LLM call disabled")
        return None

    if count_today_proposals_for_agent(agent_name, audit_path) >= max_per_day:
        log.info(f"{agent_name}: LLM proposal rate limit hit ({max_per_day}/day)")
        return None

    prompt = PROMPT_TEMPLATE.format(
        agent_name=agent_name,
        agent_purpose=agent_purpose,
        agent_traits=agent_traits,
        current_failure_modes=current_failure_modes,
        composite_health=composite_health,
        threshold=stagnation_threshold,
        history_n=len(health_history),
        health_history=health_history[-5:],
        native_names=native_names,
        compound_names=compound_names[:10],
        borrowed_names=borrowed_names[:10],
        void_names=void_names[:10],
    )
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    now = datetime.now(timezone.utc).isoformat()
    proposal_id = hashlib.sha256(
        f"{agent_name}|{prompt_hash}|{now}".encode()
    ).hexdigest()[:16]

    if dry_run:
        return None

    # Fire the cascade
    try:
        raw_text, provider = call_llm_with_provider(
            prompt=prompt,
            system=("You are an adversarial mutation designer. Output ONLY the "
                    "JSON object specified. No prose outside it."),
            max_tokens=llm_max_tokens,
            temperature=llm_temperature,
            timeout=llm_timeout_sec,
        )
    except Exception as e:
        log.error(f"LLM cascade raised: {e}")
        return None

    if not raw_text or raw_text.startswith("(LLM cascade failed"):
        log.warning(f"LLM cascade returned no usable text: {raw_text[:80]}")
        return None

    parsed = _extract_json_from_response(raw_text)
    parse_succeeded = parsed is not None and isinstance(parsed, dict)
    parsed_safe = parsed if parse_succeeded else {}

    name = str(parsed_safe.get("name", "")).strip()
    description = str(parsed_safe.get("description", "")).strip()
    hypothesis = str(parsed_safe.get("hypothesis", "")).strip()
    cost = str(parsed_safe.get("cost", "unknown")).strip()
    reversibility = str(parsed_safe.get("reversibility", "unknown")).strip()
    apply_code = str(parsed_safe.get("apply_code", "")).strip()
    revert_code = str(parsed_safe.get("revert_code", "")).strip()

    safety_violations = (static_safety_check(apply_code, revert_code)
                         if (apply_code or revert_code) else [])

    proposal = LLMAuthoredProposal(
        proposal_id=proposal_id,
        agent_name=agent_name,
        proposed_at=now,
        prompt_hash=prompt_hash,
        llm_model=provider or "unknown",
        raw_response=raw_text[:5000],
        parsed=parsed_safe,
        parse_succeeded=parse_succeeded,
        name=name,
        description=description,
        hypothesis=hypothesis,
        cost=cost,
        reversibility=reversibility,
        apply_code=apply_code,
        revert_code=revert_code,
        sandbox_status="untested",   # iter 3 will flip to passed/failed
        safety_violations=safety_violations,
        human_approval="pending",
    )
    try:
        append_to_audit_log(proposal, audit_path)
    except Exception as e:
        log.warning(f"audit log append failed: {e}")
    return proposal
