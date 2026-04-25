"""LLM-driven mutation operator for MAP-Elites on polymul-n3 over F_2.

Design discipline (cost-bounded):
  - Model: claude-haiku-4-5-20251001 (cheap, fast; per project rules).
  - Hard cap: <= MAX_LLM_CALLS LLM calls per pilot run, enforced at the
    BudgetCounter level. Refuses to exceed.
  - No web search, no extended thinking. Single short request, low max_tokens.
  - Defensive JSON parsing: handle code-fence wrappers, comments, trailing
    text. Parse failures are logged and skipped — they do NOT crash the run.
  - Validity check: the candidate is returned regardless; the caller
    (Archive.submit) decides whether the candidate reconstructs the polymul
    tensor.

Claim discipline (load-bearing):
  - We do NOT claim to find novel matmul algorithms (AlphaEvolve already
    does that without QD; our budget is much smaller).
  - The defensible contribution is whether wrapping an LLM mutation in
    a MAP-Elites archive surfaces additional orbits beyond local-mutation
    baseline (polymul_n3 found 12 sub-optimal rank-9 orbits via local moves).
"""
from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np

# Project-local imports (relative; this module is part of the pilot package).
from ..pilot_polymul_n3.core import DIM_AB, DIM_C


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

# Per CLAUDE.md security rule: keys go through keys.py, never read .env files.
LLM_MODEL = "claude-haiku-4-5-20251001"
LLM_MAX_TOKENS = 1024            # response cap; small edits don't need more
LLM_TIMEOUT_S = 30.0
LLM_MAX_RETRIES = 1              # SDK default is 2; one is enough for a budgeted run

# Hard budget for the entire pilot run.
DEFAULT_BUDGET = 200


# ----------------------------------------------------------------------------
# Budget counter (process-local, thread-safe)
# ----------------------------------------------------------------------------

@dataclass
class BudgetCounter:
    """Thread-safe budget tracker for LLM calls.

    Tracks: total attempted calls, successful API responses, parse successes,
    parse failures, and validity rate of returned candidates.
    """
    max_calls: int = DEFAULT_BUDGET
    api_attempts: int = 0
    api_successes: int = 0
    api_failures: int = 0
    parse_successes: int = 0
    parse_failures: int = 0
    valid_decomps: int = 0
    invalid_decomps: int = 0
    novel_orbits_found: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def can_call(self) -> bool:
        with self._lock:
            return self.api_attempts < self.max_calls

    def record_attempt(self) -> bool:
        """Atomically reserve a call slot. Returns True if reserved, False if exhausted."""
        with self._lock:
            if self.api_attempts >= self.max_calls:
                return False
            self.api_attempts += 1
            return True

    def record_api_success(self) -> None:
        with self._lock:
            self.api_successes += 1

    def record_api_failure(self) -> None:
        with self._lock:
            self.api_failures += 1

    def record_parse_success(self) -> None:
        with self._lock:
            self.parse_successes += 1

    def record_parse_failure(self) -> None:
        with self._lock:
            self.parse_failures += 1

    def record_validity(self, valid: bool) -> None:
        with self._lock:
            if valid:
                self.valid_decomps += 1
            else:
                self.invalid_decomps += 1

    def record_novel_orbit(self) -> None:
        with self._lock:
            self.novel_orbits_found += 1

    def summary(self) -> dict:
        with self._lock:
            return {
                "api_attempts": self.api_attempts,
                "api_successes": self.api_successes,
                "api_failures": self.api_failures,
                "parse_successes": self.parse_successes,
                "parse_failures": self.parse_failures,
                "valid_decomps": self.valid_decomps,
                "invalid_decomps": self.invalid_decomps,
                "novel_orbits_found": self.novel_orbits_found,
                "budget_remaining": self.max_calls - self.api_attempts,
            }


# ----------------------------------------------------------------------------
# Client construction
# ----------------------------------------------------------------------------

def make_client():
    """Construct an Anthropic client using the project key loader.

    Per CLAUDE.md: never read .env / key files directly; use get_key().
    """
    import anthropic
    from keys import get_key
    api_key = get_key("claude")
    return anthropic.Anthropic(
        api_key=api_key,
        timeout=LLM_TIMEOUT_S,
        max_retries=LLM_MAX_RETRIES,
    )


# ----------------------------------------------------------------------------
# Serialization helpers
# ----------------------------------------------------------------------------

def serialize_decomp(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> str:
    """Compact human/LLM-readable serialization of a (U, V, W) decomposition.

    Uses Python list-of-lists JSON, dropping any zero columns to keep prompts
    short and to make the effective rank obvious to the model.
    """
    nz = ~((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    Uc = U[:, nz]
    Vc = V[:, nz]
    Wc = W[:, nz]
    obj = {
        "rank": int(Uc.shape[1]),
        "A": Uc.astype(int).tolist(),  # shape (3, r)
        "B": Vc.astype(int).tolist(),  # shape (3, r)
        "C": Wc.astype(int).tolist(),  # shape (5, r)
    }
    return json.dumps(obj, separators=(",", ":"))


# ----------------------------------------------------------------------------
# Prompt design
# ----------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are an expert in tensor decomposition over the finite field F_2 "
    "(arithmetic mod 2). The user gives you a CP decomposition (A, B, C) of "
    "the polynomial-multiplication tensor T for degree-2 polynomials over F_2, "
    "where T[i,j,k] = 1 iff i+j=k (i,j in 0..2; k in 0..4). The decomposition "
    "satisfies T = sum_r outer(A[:,r], B[:,r], C[:,r]) mod 2.\n\n"
    "You will propose a SMALL VARIATION of the input: 1-3 entry-level bit "
    "flips, OR a single column-level edit (replace one column with a new "
    "random F_2 column, or zero one column out, or duplicate-and-perturb a "
    "column). The variation should plausibly stay valid, or move it to a "
    "different valid decomposition orbit (possibly at a different rank). "
    "Avoid identity moves.\n\n"
    "Output ONLY a single JSON object with keys 'A' (3-by-r), 'B' (3-by-r), "
    "'C' (5-by-r), all entries in {0, 1}. No prose, no code fences, no "
    "explanation. Keep r between 6 and 12 inclusive. Each row of A and B has "
    "length r; A and B have 3 rows each; C has 5 rows."
)


def build_user_prompt(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> str:
    payload = serialize_decomp(U, V, W)
    return (
        f"Current decomposition (JSON):\n{payload}\n\n"
        f"Propose a small variation as instructed. JSON only."
    )


# ----------------------------------------------------------------------------
# Response parsing (defensive)
# ----------------------------------------------------------------------------

_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_json_blob(text: str) -> Optional[str]:
    """Pull the most likely JSON object out of a possibly-fenced response."""
    if not text:
        return None
    # 1. Code-fence wrapped JSON.
    m = _CODE_FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    # 2. Find the first top-level {...} block.
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def parse_response(text: str) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Parse an LLM response into (U, V, W) matrices over F_2.

    Returns None on any failure (malformed JSON, wrong shapes, non-binary
    entries, etc.). The caller is expected to log the failure and continue.
    """
    blob = _extract_json_blob(text)
    if blob is None:
        return None
    try:
        obj = json.loads(blob)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    if not all(k in obj for k in ("A", "B", "C")):
        return None
    try:
        A = np.array(obj["A"], dtype=np.int64)
        B = np.array(obj["B"], dtype=np.int64)
        C = np.array(obj["C"], dtype=np.int64)
    except (TypeError, ValueError):
        return None
    # Shape gates.
    if A.ndim != 2 or B.ndim != 2 or C.ndim != 2:
        return None
    if A.shape[0] != DIM_AB or B.shape[0] != DIM_AB or C.shape[0] != DIM_C:
        return None
    if not (A.shape[1] == B.shape[1] == C.shape[1]):
        return None
    r = A.shape[1]
    if r < 1 or r > 64:                     # sanity bound; pilots use up to 12
        return None
    # Reduce mod 2 and clamp to {0,1} (LLM may emit -1 or 2; we mod-reduce).
    A = (A % 2).astype(np.uint8)
    B = (B % 2).astype(np.uint8)
    C = (C % 2).astype(np.uint8)
    if not np.all((A == 0) | (A == 1)):
        return None
    if not np.all((B == 0) | (B == 1)):
        return None
    if not np.all((C == 0) | (C == 1)):
        return None
    return A, B, C


# ----------------------------------------------------------------------------
# The mutation function
# ----------------------------------------------------------------------------

def llm_mutate(
    U: np.ndarray,
    V: np.ndarray,
    W: np.ndarray,
    client,
    budget: BudgetCounter,
    log_path: Optional[str] = None,
) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Ask the LLM to propose a variation of (U, V, W) and return the parsed
    candidate. Returns None on parse failure, API failure, or budget exhaustion.

    The Archive is responsible for evaluating validity (reconstruct == T).
    """
    # Atomic budget reservation.
    if not budget.record_attempt():
        return None

    user_msg = build_user_prompt(U, V, W)

    try:
        # Per project rules: cheap & minimal. No web search, no thinking.
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:                # noqa: BLE001 — defensive boundary
        budget.record_api_failure()
        if log_path:
            _append_log(log_path, f"API_ERR: {type(e).__name__}: {e}\n")
        return None

    budget.record_api_success()
    text = ""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text += block.text

    parsed = parse_response(text)
    if parsed is None:
        budget.record_parse_failure()
        if log_path:
            _append_log(
                log_path,
                f"PARSE_FAIL: text-snippet={text[:200]!r}\n",
            )
        return None

    budget.record_parse_success()
    return parsed


def _append_log(path: str, line: str) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass        # logging must never crash the run


# ----------------------------------------------------------------------------
# Self-test (run as: python -m exploratory.tensor_decomp_qd.pilot_LLM_mutation.llm_mutate)
# ----------------------------------------------------------------------------

def _selftest():
    """Validate the parser without spending any API calls."""
    # Bare JSON.
    text1 = '{"A":[[1,0,0],[0,1,0],[0,0,1]],"B":[[1,0,0],[0,1,0],[0,0,1]],"C":[[1,0,0],[0,1,0],[0,0,1],[0,0,0],[0,0,0]]}'
    out1 = parse_response(text1)
    assert out1 is not None and out1[0].shape == (3, 3), f"basic parse failed: {out1}"

    # Code-fenced JSON.
    text2 = "Here you go:\n```json\n" + text1 + "\n```\n"
    out2 = parse_response(text2)
    assert out2 is not None and out2[0].shape == (3, 3), "code-fence parse failed"

    # Malformed JSON.
    out3 = parse_response("not json at all {{{")
    assert out3 is None, "malformed json should fail"

    # Wrong shape (C has 4 rows instead of 5).
    bad = '{"A":[[1],[0],[0]],"B":[[1],[0],[0]],"C":[[1],[0],[0],[0]]}'
    out4 = parse_response(bad)
    assert out4 is None, "wrong-shape C should be rejected"

    # Mod-2 reduction (LLM may emit 2).
    text5 = '{"A":[[2,0],[0,1],[0,0]],"B":[[1,0],[0,1],[0,0]],"C":[[1,0],[0,1],[0,0],[0,0],[0,0]]}'
    out5 = parse_response(text5)
    assert out5 is not None
    assert out5[0][0, 0] == 0, "mod-2 reduction failed"

    # Empty / non-dict JSON.
    assert parse_response("[1, 2, 3]") is None

    # Missing keys.
    assert parse_response('{"A": [], "B": []}') is None

    print("llm_mutate self-test: 6/6 parse-cases pass")


if __name__ == "__main__":
    _selftest()
