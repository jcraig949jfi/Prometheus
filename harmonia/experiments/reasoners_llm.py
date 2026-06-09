"""LLM-backed reasoner for the reasoning-ladder Phase-0 harness (EXPERIMENTAL).

Wraps an OpenAI-compatible chat model (via scripts/llm_cascade.py) as a
`fn(probe) -> (answer, trace_dict)` reasoner compatible with
`reasoning_phase0.grade`.

Design: per probe, render a kind-specific natural-language statement + a strict
JSON output contract, call the model, then DETERMINISTICALLY map the parsed JSON
to (a) the harness answer format and (b) the trace fields the grader reads.

The reasoner is given ONLY the problem statement — never the harness ground
truth, never the hidden counterexample, never the `truth` bool. For conjectures
the `cid` is mapped to an English statement; `truth`/`cex`/`delayed` in
probe.data are NOT shown to the model (that would be cheating).

Robustness: the JSON parser strips ``` fences, finds the outermost {...},
tolerates trailing junk, and on total failure records a parse_error in the
trace (so parse failures show up as a failure SHAPE, not a silent crash).

Security: keys are handled entirely inside llm_cascade (auto-loaded); this file
never reads key files and never logs key values.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import sympy as sp

# llm_cascade lives in <repo>/scripts
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from llm_cascade import call_llm_with_provider  # noqa: E402

# ---------------------------------------------------------------- conjectures
# cid -> (english statement shown to the model). We DO NOT reveal truth/cex.
CONJ_STATEMENTS: Dict[str, str] = {
    "ab_even_then_both_even":
        "Claim: For all integers a and b, if the product a*b is even, then BOTH "
        "a and b are even. Is this claim true for all integers a, b?",
    "n2_plus_n_even":
        "Claim: For every integer n, n^2 + n is even. Is this claim true for all "
        "integers n?",
    "n2_n_41_prime":
        "Claim: For every integer n >= 0, the value n^2 + n + 41 is a prime "
        "number. Is this claim true for all such n?",
    "all_primes_odd":
        "Claim: Every prime number is odd. Is this claim true for all primes?",
    "sum_two_squares":
        "Claim: Every non-negative integer that is NOT of the form 4^a*(8b+7) "
        "can be written as a sum of three integer squares. Is this claim true?",
}

# ---------------------------------------------------------------- prompts
_SYSTEM = (
    "You are a careful mathematical reasoner. You solve each problem from first "
    "principles, track domain constraints, check for extraneous solutions, and "
    "actively search for counterexamples before affirming any general claim. "
    "You ALWAYS respond with a single JSON object and nothing else."
)

_JSON_CONTRACT = """
Respond with EXACTLY one JSON object, no prose, no markdown fences. Schema:
{
  "solutions": [ ... ],          // list of real-number solutions, as numbers or
                                 //   exact strings like "3/2"; [] if no real soln.
                                 //   For the rational-identity question use the
                                 //   string forms described below, not this list.
  "is_identity": true|false|null,// for rational-identity problems only
  "excluded_values": [ ... ],    // x-values that must be excluded (e.g. zero denom)
  "domain_constraints": [ ... ], // human-readable constraints you USED, e.g. "x>=b"
  "invalid_operations": [ ... ], // operations you considered but rejected as
                                 //   domain-unsafe, e.g. "squaring both sides"
  "rejected_extraneous": true|false, // did you discard any candidate that failed
                                 //   the original equation / domain?
  "counterexample_searched": true|false, // (conjectures) did you search for one?
  "counterexample_found": <value-or-null>, // (conjectures) the counterexample, or null
  "decision": true|false|null,   // (conjectures) is the claim true? else null
  "reasoning": "one short line"
}
""".strip()


def _prompt_for(p) -> str:
    k = p.kind
    if k == "linear":
        expr = p.data["expr"]
        var = p.data.get("var", "x")
        return (
            f"Solve for {var} (real solution): {sp.sstr(expr)} = 0.\n"
            f"Return the single real solution in `solutions` (exact fraction "
            f"string if not an integer).\n\n{_JSON_CONTRACT}"
        )
    if k == "quadratic":
        expr = p.data["expr"]
        return (
            f"Find ALL real solutions of: {sp.sstr(expr)} = 0.\n"
            f"If there are no real solutions, return an empty `solutions` list "
            f"(do NOT invent real roots).\n\n{_JSON_CONTRACT}"
        )
    if k == "sqrt":
        a, b = p.data["a"], p.data["b"]
        ph = p.data.get("phrasing", 0) % 3
        if ph == 0:   # explicit legality scaffold
            ask = (f"Solve for real x: sqrt(x + {a}) = x - {b}. Square carefully, then "
                   f"CHECK each candidate against the original equation and the domain "
                   f"(right side >= 0 and x + {a} >= 0); discard extraneous candidates.")
        elif ph == 1:  # terse, no legality hint
            ask = (f"Find every real x with sqrt(x + {a}) = x - {b}. Report only the "
                   f"values that actually satisfy the original equation.")
        else:          # framed, no legality hint
            ask = (f"For which real numbers x does sqrt(x + {a}) equal x - {b}? "
                   f"Return the valid solutions.")
        return (
            f"{ask}\nPut the surviving real solutions in `solutions` (empty list if "
            f"none), list any domain conditions you used in `domain_constraints`, and "
            f"set `rejected_extraneous` true if you discarded a candidate.\n\n{_JSON_CONTRACT}"
        )
    if k == "rational":
        num, den, rhs, exc = (
            p.data["num"], p.data["den"], p.data["rhs"], p.data["excluded"],
        )
        return (
            f"Consider the equation ({sp.sstr(num)}) / ({sp.sstr(den)}) = "
            f"{sp.sstr(rhs)}.\n"
            f"Decide whether this holds for ALL real x or holds as an identity "
            f"EXCEPT at the value(s) where the denominator is zero. Set "
            f"`is_identity` true, put any excluded x-values in `excluded_values`, "
            f"and note the domain constraint in `domain_constraints`.\n\n"
            f"{_JSON_CONTRACT}"
        )
    if k == "conjecture":
        cid = p.data["cid"]
        statement = CONJ_STATEMENTS.get(cid, f"Claim id {cid}: (unknown).")
        return (
            f"{statement}\n"
            f"Before answering, actively search for a counterexample over a wide "
            f"range of cases (including small AND structurally suspicious values). "
            f"Set `counterexample_searched` true, put any counterexample you find "
            f"in `counterexample_found` (else null), and set `decision` to true "
            f"if the claim holds for all cases, false if you found a "
            f"counterexample.\n\n{_JSON_CONTRACT}"
        )
    if k in ("abs_extra", "abs_extra_clean"):    # same shape; clean variant only filters probes
        a, b = p.data["a"], p.data["b"]
        return (
            f"Solve for all real x:  |x - {a}| = {b} - x.\n"
            f"The right side {b} - x must be >= 0 for a candidate to be a valid "
            f"solution, so check each candidate. Put the real solutions in `solutions` "
            f"(empty list if there are none).\n\n{_JSON_CONTRACT}"
        )
    if k == "log_extra":
        a, b = p.data["a"], p.data["b"]
        return (
            f"Solve for all real x:  log(x) + log(x - {a}) = log({b}).\n"
            f"Logarithms require positive arguments (x > 0 and x - {a} > 0), so reject "
            f"any candidate outside the domain. Put the valid real solutions in "
            f"`solutions` (empty list if there are none).\n\n{_JSON_CONTRACT}"
        )
    if k == "log_extra_3arg":   # H1 predictive arm: dcl=3 (three independent log-domain conditions)
        a, b, c = p.data["a"], p.data["b"], p.data["c"]
        return (
            f"Solve for all real x:  log(x) + log(x - {a}) + log(x - {b}) = log({c}).\n"
            f"Logarithms require positive arguments (x > 0, x - {a} > 0, AND "
            f"x - {b} > 0), so reject any candidate outside the domain. Put the "
            f"valid real solutions in `solutions` (empty list if there are none)."
            f"\n\n{_JSON_CONTRACT}"
        )
    if k == "rational_extra":
        c, kk = p.data["c"], p.data["k"]
        return (
            f"Solve for all real x:  (x^2 - {c * c}) / (x - {c}) = {kk}.\n"
            f"Track the domain carefully — x = {c} is excluded (it makes the denominator "
            f"zero), so any candidate equal to {c} is NOT a valid solution. Put the real "
            f"solutions in `solutions` (empty list if there are none).\n\n{_JSON_CONTRACT}"
        )
    if k == "sqrt_label":
        a, b = p.data["a"], p.data["b"]; cands = p.data["candidates"]
        listed = "\n".join(f"  Candidate {i + 1}: x = {c}" for i, c in enumerate(cands))
        return (
            f"The equation sqrt(x + {a}) = x - {b} was squared, giving these candidate "
            f"solutions:\n{listed}\n\nFor EACH candidate decide whether it is a VALID "
            f"solution of the ORIGINAL equation (the principal square root is "
            f"non-negative, so a valid solution needs x - {b} >= 0 and x + {a} >= 0 and "
            f"must satisfy the original). Return `validity`: a list of booleans, one per "
            f"candidate IN ORDER (true = valid, false = extraneous).\n\n{_JSON_CONTRACT}"
        )
    if k == "lemma_select":
        goal = p.data["goal"]; lemmas = p.data["lemmas"]
        numbered = "\n".join(f"  Lemma {i + 1}: {s}" for i, s in enumerate(lemmas))
        return (
            f"Goal to prove: {goal}\nCandidate lemmas:\n{numbered}\n\n"
            f"Exactly ONE lemma is both TRUE and the key step that unlocks a correct "
            f"proof of the goal; the others are false, irrelevant, or trivial. Put the "
            f"number of that single load-bearing lemma in `selected_index`.\n\n{_JSON_CONTRACT}"
        )
    if k == "proof_repair":
        steps = p.data["steps"]
        numbered = "\n".join(f"  Step {i + 1}: {s}" for i, s in enumerate(steps))
        return (
            f"Below is a purported proof given as numbered steps:\n{numbered}\n\n"
            f"Find the FIRST step that does not validly follow — an invalid "
            f"inference, an unjustified assumption, or a hidden division-by-zero / "
            f"domain error. Put that step's number in `failing_step_index`. If the "
            f"whole proof is valid, set `failing_step_index` to 0.\n\n{_JSON_CONTRACT}"
        )
    if k == "invariant":
        n = p.data["n"]
        removed = sorted(p.data["removed"])
        ph = p.data.get("phrasing", 0) % 3
        board = (f"an {n}x{n} chessboard (cell (i,j) is black iff i+j is even) with "
                 f"these cells removed: {removed if removed else 'none'}")
        if ph == 0:   # explicit invariant scaffold
            ask = (f"Consider {board}. Can the remaining cells be tiled exactly by "
                   f"dominoes (each covering two orthogonally adjacent cells)? Decide "
                   f"using an invariant (color parity, area parity, ...).")
        elif ph == 1:  # terse, no invariant hint
            ask = (f"Take {board}. Is a perfect domino tiling of the remaining cells "
                   f"possible? Answer yes or no and justify.")
        else:          # framed, no invariant hint
            ask = (f"Given {board}, determine whether the remaining region admits a "
                   f"domino tiling, and explain the key structural reason.")
        return (
            f"{ask}\nSet `decision` true if a tiling exists, false if impossible, and "
            f"put the invariant or structural reason you relied on in "
            f"`invariant_named`.\n\n{_JSON_CONTRACT}"
        )
    return f"Problem (kind={k}): no template.\n\n{_JSON_CONTRACT}"


# ---------------------------------------------------------------- JSON parsing
def parse_json_blob(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Return (parsed_dict, error). Tolerant of code fences and trailing junk."""
    if not text or not text.strip():
        return None, "empty_response"
    s = text.strip()
    # strip ``` / ```json fences
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s).strip()
    # fast path
    try:
        return json.loads(s), None
    except Exception:
        pass
    # find outermost {...} by brace balance (handles trailing prose / multiple)
    start = s.find("{")
    if start == -1:
        return None, "no_json_object"
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                candidate = s[start:i + 1]
                try:
                    return json.loads(candidate), None
                except Exception as e:
                    return None, f"json_decode_error:{type(e).__name__}"
    return None, "unbalanced_braces"


# ---------------------------------------------------------------- value coercion
def _to_sympy_real(v: Any):
    """Coerce a model-emitted number/string to an exact sympy real, or None."""
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    try:
        if isinstance(v, (int, float)):
            return sp.nsimplify(sp.Rational(v).limit_denominator(10**9)) \
                if isinstance(v, float) else sp.Integer(v)
        if isinstance(v, str):
            v2 = v.strip().replace(" ", "")
            if v2 == "":
                return None
            return sp.nsimplify(sp.sympify(v2, rational=True))
    except Exception:
        return None
    return None


def _coerce_solution_list(raw: Any):
    """Map the model's `solutions` to a sorted list of distinct sympy reals."""
    if raw is None:
        return []
    if not isinstance(raw, (list, tuple)):
        raw = [raw]
    out = []
    for item in raw:
        s = _to_sympy_real(item)
        if s is not None and getattr(s, "is_real", True):
            out.append(s)
    # dedupe preserving sympy equality, then sort by float
    uniq = []
    for s in out:
        if not any(sp.simplify(s - u) == 0 for u in uniq):
            uniq.append(s)
    try:
        uniq.sort(key=float)
    except Exception:
        pass
    return uniq


def _coerce_bool(v: Any) -> Optional[bool]:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        t = v.strip().lower()
        if t in ("true", "yes", "1"):
            return True
        if t in ("false", "no", "0"):
            return False
    return None


# ------------------------------------------------ JSON -> (answer, trace) map
def map_to_answer_and_trace(p, parsed: Optional[Dict[str, Any]],
                            parse_err: Optional[str],
                            raw: str) -> Tuple[Any, Dict[str, Any]]:
    """Deterministically convert parsed model JSON into the harness answer
    format + the trace fields grade() reads. Pure (no network)."""
    tr: Dict[str, Any] = {
        "operations_used": ["llm"],
        "_provider": None,           # filled by caller
        "_parse_error": parse_err,
        "_raw_excerpt": (raw or "")[:240],
    }
    d = parsed or {}

    # carry through self-reported trace signals (the grader reads these)
    dom = d.get("domain_constraints")
    if isinstance(dom, list) and dom:
        tr["domain_constraints_detected"] = [str(z) for z in dom]
    inval = d.get("invalid_operations")
    if isinstance(inval, list) and inval:
        tr["invalid_operations_attempted"] = [str(z) for z in inval]
    rej = _coerce_bool(d.get("rejected_extraneous"))
    if rej is not None:
        tr["rejected_extraneous"] = rej

    k = p.kind
    if k == "linear":
        sols = _coerce_solution_list(d.get("solutions"))
        # harness linear answer = list with exactly one real
        return (sols[:1] if sols else None), tr

    if k in ("quadratic", "sqrt", "rational_extra", "abs_extra", "log_extra"):
        sols = _coerce_solution_list(d.get("solutions"))
        return sols, tr

    if k == "rational":
        # NOTE on `is_identity` semantics: models reliably read this as "is it
        # true for ALL x" and answer false BECAUSE a value is excluded, while
        # still correctly reporting that excluded value. The harness's correct
        # answer ("all_x_except_excluded") is exactly "identity on a punctured
        # domain". So the operative signal is: did the model identify an
        # excluded value / domain constraint at all? If yes -> it handled the
        # exclusion. If it claims a plain identity with no exclusion -> all_x.
        is_id = _coerce_bool(d.get("is_identity"))
        excluded = d.get("excluded_values")
        has_excl = isinstance(excluded, list) and len(excluded) > 0
        handled_exclusion = has_excl or bool(tr.get("domain_constraints_detected"))
        if handled_exclusion:
            return "all_x_except_excluded", tr
        if is_id:
            return "all_x", tr
        # neither a clean identity nor an exclusion recognised -> closest bucket
        return "all_x", tr

    if k == "conjecture":
        decision = _coerce_bool(d.get("decision"))
        cex = d.get("counterexample_found")
        searched = _coerce_bool(d.get("counterexample_searched"))
        found = cex is not None and not (isinstance(cex, str) and cex.strip().lower() in ("", "none", "null"))
        tr["searched_counterexample"] = bool(searched) if searched is not None else False
        tr["found_counterexample"] = bool(found)
        # If a counterexample was found, the claim is false regardless of decision.
        if found:
            tr["overgeneralized"] = False
            return False, tr
        if decision is None:
            # no parseable decision -> treat as "affirmed" (overgeneralized) so the
            # failure shape is recorded rather than crashing
            tr["overgeneralized"] = True
            return True, tr
        # affirmed true without a counterexample = potential overgeneralization;
        # grade() will decide correctness, kill-pattern uses this flag.
        tr["overgeneralized"] = bool(decision)
        return decision, tr

    if k == "proof_repair":
        fi = d.get("failing_step_index")
        try:
            return (int(fi) if fi is not None else None), tr
        except (TypeError, ValueError):
            return None, tr

    if k == "lemma_select":
        si = d.get("selected_index")
        try:
            return (int(si) if si is not None else None), tr
        except (TypeError, ValueError):
            return None, tr

    if k == "sqrt_label":
        val = d.get("validity")
        return ([bool(z) for z in val], tr) if isinstance(val, list) else (None, tr)

    if k == "invariant":
        inv = d.get("invariant_named")
        if inv:
            tr["invariant_named"] = str(inv)
        return _coerce_bool(d.get("decision")), tr  # decision == "is it tileable"

    return None, tr


# ---------------------------------------------------------------- the reasoner
def make_llm_reasoner(model: str = "auto", temperature: float = 0.0,
                      max_tokens: int = 900, timeout: int = 120,
                      exclude_providers=None, call_log: Optional[list] = None):
    """Return a `fn(probe) -> (answer, trace)` backed by the LLM cascade.

    `model="auto"` uses the cascade's natural ordering (cheapest/fastest first).
    `call_log`, if given, gets one dict appended per call (provider, parse_err,
    kind, tier) for cost/diagnostic reporting.
    """
    def reasoner(p):
        prompt = _prompt_for(p)
        try:
            text, provider = call_llm_with_provider(
                prompt, system=_SYSTEM, max_tokens=max_tokens,
                temperature=temperature, timeout=timeout,
                exclude_providers=exclude_providers,
            )
        except Exception as e:  # network / unexpected
            text, provider = "", None
            parsed, perr = None, f"call_exception:{type(e).__name__}"
            ans, tr = map_to_answer_and_trace(p, parsed, perr, text)
            tr["_provider"] = provider
            if call_log is not None:
                call_log.append({"tier": p.tier, "version": p.version,
                                 "kind": p.kind, "provider": provider,
                                 "parse_error": perr})
            return ans, tr

        if provider is None or text.startswith("(LLM cascade failed"):
            parsed, perr = None, "cascade_failed"
            ans, tr = map_to_answer_and_trace(p, parsed, perr, text)
            tr["_provider"] = None
            if call_log is not None:
                call_log.append({"tier": p.tier, "version": p.version,
                                 "kind": p.kind, "provider": None,
                                 "parse_error": perr})
            return ans, tr

        parsed, perr = parse_json_blob(text)
        ans, tr = map_to_answer_and_trace(p, parsed, perr, text)
        tr["_provider"] = provider
        if call_log is not None:
            call_log.append({"tier": p.tier, "version": p.version,
                             "kind": p.kind, "provider": provider,
                             "parse_error": perr})
        return ans, tr

    return reasoner


# ------------------------------------------------ Opus (Anthropic structured outputs)
def make_opus_reasoner(model: str = "claude-opus-4-8", max_tokens: int = 6000,
                       use_thinking: bool = True, effort: Optional[str] = None,
                       call_log: Optional[list] = None):
    """Return a `fn(probe) -> (answer, trace)` backed by Claude Opus via the
    Anthropic SDK with STRUCTURED OUTPUTS — the JSON schema is enforced by the
    API, so the free-text parse-failure class (the 24% we saw on the cascade)
    cannot occur. Prompt caching is applied to the shared system prompt.

    Reuses `_prompt_for` and `map_to_answer_and_trace` so grading is identical to
    the cascade reasoner. Security: api key via keys.get_key, never logged.
    """
    import anthropic
    from keys import get_key
    from pydantic import BaseModel, Field
    from typing import List
    from typing import Optional as _Opt

    # Per-kind schemas — small grammars compile fast; one fat 12-field schema with
    # nullable unions + arrays hit the API's "Grammar compilation timed out".
    class _Eq(BaseModel):          # linear / quadratic / sqrt
        solutions: List[str] = Field(default_factory=list)
        domain_constraints: List[str] = Field(default_factory=list)
        invalid_operations: List[str] = Field(default_factory=list)
        rejected_extraneous: bool = False
        reasoning: str = ""

    class _Rat(BaseModel):         # rational
        is_identity: bool = False
        excluded_values: List[str] = Field(default_factory=list)
        domain_constraints: List[str] = Field(default_factory=list)
        reasoning: str = ""

    class _Conj(BaseModel):        # conjecture
        counterexample_searched: bool = False
        counterexample_found: _Opt[str] = None
        decision: _Opt[bool] = None
        reasoning: str = ""

    class _Inv(BaseModel):         # invariant
        decision: _Opt[bool] = None
        invariant_named: _Opt[str] = None
        reasoning: str = ""

    class _Proof(BaseModel):       # proof_repair (0 == fully valid)
        failing_step_index: int = 0
        reasoning: str = ""

    class _LemmaSel(BaseModel):    # lemma_select (1-indexed load-bearing lemma)
        selected_index: int = 0
        reasoning: str = ""

    class _Labels(BaseModel):      # sqrt_label (per-candidate validity, in order)
        validity: List[bool] = Field(default_factory=list)
        reasoning: str = ""

    KIND_SCHEMA = {"linear": _Eq, "quadratic": _Eq, "sqrt": _Eq, "rational": _Rat,
                   "conjecture": _Conj, "invariant": _Inv, "proof_repair": _Proof,
                   "lemma_select": _LemmaSel, "sqrt_label": _Labels,
                   "rational_extra": _Eq, "abs_extra": _Eq, "log_extra": _Eq,
                   "abs_extra_clean": _Eq, "log_extra_3arg": _Eq}

    client = anthropic.Anthropic(api_key=get_key("claude"), max_retries=8)  # backoff absorbs transient 429/500/529
    # cache_control on the (stable) system block; note: Opus min cacheable prefix
    # is ~4096 tokens, so this short prompt likely won't actually cache — harmless.
    sys_blocks = [{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}]

    def reasoner(p):
        prompt = _prompt_for(p)
        kw = dict(model=model, max_tokens=max_tokens, system=sys_blocks,
                  messages=[{"role": "user", "content": prompt}],
                  output_format=KIND_SCHEMA.get(p.kind, _Eq))
        if use_thinking:
            kw["thinking"] = {"type": "adaptive"}
        if effort:                          # C-THINK: pin thinking depth (low/medium/high/xhigh/max)
            kw["output_config"] = {"effort": effort}
        last_err = None
        for _attempt in range(2):   # retry once — absorbs transient grammar/validation flakes
            try:
                resp = client.messages.parse(**kw)
                po = resp.parsed_output
                d = po.model_dump() if po is not None else {}
                ans, tr = map_to_answer_and_trace(p, d, None, "")
                tr["_provider"] = model
                if call_log is not None:
                    u = resp.usage
                    call_log.append({
                        "tier": p.tier, "version": p.version, "kind": p.kind,
                        "provider": model, "parse_error": None,
                        "in": getattr(u, "input_tokens", 0),
                        "out": getattr(u, "output_tokens", 0),
                        "cache_read": getattr(u, "cache_read_input_tokens", 0),
                        "cache_write": getattr(u, "cache_creation_input_tokens", 0),
                    })
                return ans, tr
            except Exception as e:
                last_err = e
        perr = f"api_error:{type(last_err).__name__}"
        ans, tr = map_to_answer_and_trace(p, None, perr, str(last_err)[:200])
        tr["_provider"] = model
        if call_log is not None:
            call_log.append({"tier": p.tier, "version": p.version, "kind": p.kind,
                             "provider": model, "parse_error": perr})
        return ans, tr
    return reasoner


# ---------------------------------------------------------------- mock (offline)
def mock_reasoner(p):
    """Deterministic offline stand-in (NO network). Used only when every
    provider is unreachable, so the harness still runs end-to-end. Clearly
    labelled in the trace so results are never mistaken for real LLM output."""
    tr = {"operations_used": ["mock"], "_provider": "MOCK", "_parse_error": None}
    if p.kind == "conjecture":
        tr["searched_counterexample"] = False
        tr["overgeneralized"] = True
        return True, tr
    if p.kind == "rational":
        return "all_x", tr
    if p.kind == "sqrt":
        a, b = p.data["a"], p.data["b"]
        allroots = sp.solve(sp.Eq(x_sym + a, (x_sym - b) ** 2), x_sym)
        return sorted({s for s in allroots if s.is_real}, key=float), tr
    expr = p.data.get("expr")
    if expr is not None:
        try:
            var = list(expr.free_symbols)
            var = var[0] if var else x_sym
            sols = sorted({s for s in sp.solve(expr, var) if s.is_real}, key=float)
            return (sols[:1] if p.kind == "linear" else sols), tr
        except Exception:
            return None, tr
    return None, tr


x_sym = sp.symbols("x")
