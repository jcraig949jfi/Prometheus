"""B' — the held-out anti-calibration set, authored by an INDEPENDENT model family.

Why this exists
---------------
M0 (2026-06-27) measured the packaged battery at 17% reach on Set B (the novelty
arm) and diagnosed the wall as representational: `verify()` routes by `probe.kind`
(5 kinds) and by literal `cid` string, so claims whose *content* z3 can decide are
unreachable because their *shape* is unregistered.

The obvious fix — add more kinds — is a lookup table, and a lookup table cannot be
honestly measured on the same 18 items that diagnosed the wall. Widening shapes
against the diagnosing set is fitting to the test: the meter ticks because the
author typed a new entry, not because reach generalized.

So B' is built FIRST, BEFORE any translator/widening exists, by a DIFFERENT model
family (gemini-3.6-flash), and is never consulted during that build. A lookup
table cannot pass a held-out set; a genuine claim->formula translator can. That
is the discriminator between the two architectures, and it only works if B' is
pre-registered.

Separation of duties (the R6 leak, not repeated)
------------------------------------------------
  * The author model emits, per item: a natural-language STATEMENT, a domain tag,
    and an independent BRUTE-FORCE CHECKER over a bounded domain.
  * The checker is the oracle. It is executed here, in a restricted namespace, to
    confirm the claim is actually TRUE before the item is admitted.
  * `bprime_holdout.json` (statements only) is what any downstream translator is
    permitted to see. `bprime_oracle.json` (checkers + truth) is quarantined.
    Icarus R6 lost a promotion to `truth`/`cex` fields still being readable at
    grade time; that does not happen here.

Doctrine: the author is an LLM (proposal side). The admission decision is made by
executing arithmetic (selection side). No LLM certifies anything.

Usage:
    PYTHONPATH=. python harmonia/experiments/bprime_generate.py
"""
from __future__ import annotations

import ast
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from keys import get_key

MODEL = "gemini-3.6-flash"
OUT_DIR = Path(__file__).resolve().parent
HOLDOUT_PATH = OUT_DIR / "bprime_holdout.json"
ORACLE_PATH = OUT_DIR / "bprime_oracle.json"

# The calibration manifold M0 showed the instrument already recognizes. Claims in
# these shapes are re-encodings, not novelty — the author is told to avoid them.
EXCLUDED = (
    "elliptic curves, polynomial root-finding, quadratic equations, "
    "difference-of-squares factoring, sqrt-equation extraneous roots, "
    "rational-expression identities, modular forms, L-functions"
)

DOMAINS = [
    ("graph_theory", "finite simple graphs: degrees, trees, colorings, connectivity, matchings"),
    ("combinatorics", "counting, pigeonhole, binomial identities, partitions, double counting"),
    ("linear_algebra", "small integer matrices: rank, determinant, invertibility, eigenvalues, trace"),
    ("real_analysis", "inequalities over the reals: AM-GM, Cauchy-Schwarz, triangle inequality, convexity"),
    ("elementary_number_theory", "divisibility, gcd/lcm, congruences, totient, order — NOT elliptic curves"),
    ("order_and_sets", "finite posets, lattices, set identities, functions and cardinality"),
]

PROMPT = """You are constructing a held-out benchmark of TRUE elementary mathematical claims.

Domain for this batch: {domain} — {gloss}

Produce exactly {n} claims that are ALL TRUE. Requirements:

1. Each claim must be a genuine universally-quantified mathematical statement
   ("for all ...") that a competent undergraduate would recognize as true.
2. Each must be checkable by exhaustive search over a SMALL bounded domain — your
   checker will be executed to confirm truth before the claim is admitted.
3. AVOID these areas entirely (they are already covered elsewhere): {excluded}.
4. Vary the logical SHAPE across items: some with several variables, some over
   real/rational values, some over finite structures, some inequalities, some
   equalities, some existence-within-bounds. Do not make them all the same form.
5. Do NOT reference or assume any particular solver, proof assistant, or encoding.
   State the mathematics, not a formalization.

Return STRICT JSON, an array of exactly {n} objects, each with keys:
  "statement" : a self-contained natural-language statement of the claim
  "domain"    : "{domain}"
  "checker"   : a Python 3 source string defining `def check() -> bool:` that
                exhaustively tests the claim over a small bounded domain and
                returns True iff no counterexample is found. It may use only the
                standard modules `math`, `itertools`, `fractions`. It must run in
                well under 5 seconds. It must NOT import anything else, read
                files, or access the network.

Output ONLY the JSON array. No prose, no markdown fences.
"""

# Modules the sandboxed checker may use. Anything else is unavailable by
# construction: __import__ is not exposed, so `import x` inside check() fails.
import fractions
import itertools
import math

_ALLOWED_MODULES = {"math": math, "itertools": itertools, "fractions": fractions}

# Hygiene screen, not a security boundary: the author model is careless, not
# adversarial. We block filesystem/eval/introspection surface and restrict
# imports to the three arithmetic modules, then execute in a small namespace.
_FORBIDDEN_NAMES = frozenset({
    "open", "exec", "eval", "compile", "__import__", "globals", "locals",
    "getattr", "setattr", "delattr", "vars", "input", "breakpoint",
    "memoryview", "exit", "quit", "help",
})


def _screen(src: str) -> str | None:
    """Static AST screen. Returns a rejection reason, or None if the source passes.

    Regex screening is what broke the first run: `from itertools import
    combinations` reads as `import combinations` to a regex and was rejected
    though it is exactly what we allow. Parse the source instead of matching it.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return f"rejected: checker does not parse ({exc.msg})"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in _ALLOWED_MODULES:
                    return f"rejected: imports disallowed module {root!r}"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in _ALLOWED_MODULES:
                return f"rejected: imports from disallowed module {root!r}"
        elif isinstance(node, ast.Name) and node.id in _FORBIDDEN_NAMES:
            return f"rejected: references forbidden name {node.id!r}"
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            # dunder attribute walking is the standard escape route out of a
            # restricted namespace; no legitimate arithmetic checker needs it.
            return f"rejected: dunder attribute access {node.attr!r}"
    return None


def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Import hook exposing only the arithmetic modules.

    The first run failed 20/20 here: the screen permitted `import itertools`
    but the execution namespace had no `__import__`, so every checker died with
    ImportError before evaluating any mathematics. Permitting a form statically
    and then blocking it dynamically is the same shape of interface wall this
    whole experiment exists to measure.
    """
    root = name.split(".")[0]
    if root not in _ALLOWED_MODULES:
        raise ImportError(f"module {name!r} is not available to checkers")
    return _ALLOWED_MODULES[root]


_RETRYABLE = frozenset({429, 500, 502, 503, 504})


def _call_model(prompt: str, *, max_tokens: int = 32000, attempts: int = 5) -> str:
    """One generateContent call, retried on transient upstream failures.

    The first generation run lost an entire domain batch to a single 503. Free-tier
    capacity is bursty, so a transient upstream error must not be recorded as a
    measurement outcome — that would silently bias the set toward whichever
    domains happened to be served.
    """
    key = get_key("GEMINI")
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 1.0},
    }
    last: Exception | None = None
    for attempt in range(attempts):
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": key},
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.load(resp)
            cand = data["candidates"][0]
            return "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in _RETRYABLE:
                raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
        if attempt < attempts - 1:
            delay = 4 * (2 ** attempt)  # 4s, 8s, 16s, 32s
            print(f"    transient {type(last).__name__} — retry in {delay}s "
                  f"({attempt + 1}/{attempts - 1})")
            time.sleep(delay)
    raise RuntimeError(f"model call failed after {attempts} attempts: {last}")


def _parse_json_array(raw: str) -> List[Dict[str, Any]]:
    """Extract the JSON array, tolerating stray fences or prose."""
    txt = raw.strip()
    txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.MULTILINE).strip()
    start, end = txt.find("["), txt.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON array found in model output: {txt[:200]!r}")
    return json.loads(txt[start : end + 1])


def _run_checker(src: str) -> tuple[bool | None, str]:
    """Execute a checker in a restricted namespace. Returns (verdict, note).

    verdict True/False is the oracle's answer; None means the checker itself was
    unusable (rejected statically, crashed, or returned a non-bool). A checker we
    cannot trust never admits an item — this fails CLOSED.
    """
    reason = _screen(src)
    if reason is not None:
        return None, reason
    ns: Dict[str, Any] = {"__builtins__": {
        "__import__": _restricted_import,
        # a deliberately small builtin surface: enough for arithmetic search,
        # nothing that touches the filesystem, network, or import machinery.
        "range": range, "len": len, "abs": abs, "min": min, "max": max,
        "sum": sum, "all": all, "any": any, "sorted": sorted, "list": list,
        "set": set, "dict": dict, "tuple": tuple, "int": int, "float": float,
        "bool": bool, "str": str, "enumerate": enumerate, "zip": zip,
        "map": map, "filter": filter, "round": round, "pow": pow,
        "divmod": divmod, "frozenset": frozenset, "reversed": reversed,
        "True": True, "False": False, "None": None,
    }}
    ns.update(_ALLOWED_MODULES)
    try:
        exec(src, ns)  # noqa: S102 — statically screened, restricted namespace
        fn = ns.get("check")
        if not callable(fn):
            return None, "rejected: checker defines no callable `check`"
        out = fn()
    except Exception as exc:
        return None, f"checker raised {type(exc).__name__}: {exc}"
    if not isinstance(out, bool):
        return None, f"checker returned {type(out).__name__}, not bool"
    return out, "ok"


def generate(per_domain: int = 4) -> Dict[str, Any]:
    admitted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    for domain, gloss in DOMAINS:
        prompt = PROMPT.format(domain=domain, gloss=gloss, n=per_domain, excluded=EXCLUDED)
        try:
            items = _parse_json_array(_call_model(prompt))
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as exc:
            print(f"  [{domain}] generation FAILED: {type(exc).__name__}: {exc}")
            continue
        for item in items:
            stmt, checker = item.get("statement"), item.get("checker")
            if not stmt or not checker:
                rejected.append({"domain": domain, "reason": "missing statement/checker",
                                 "statement": stmt})
                continue
            verdict, note = _run_checker(checker)
            rec = {"domain": domain, "statement": stmt, "checker": checker,
                   "oracle_verdict": verdict, "oracle_note": note}
            # Admit ONLY claims the oracle independently confirms TRUE. A False
            # verdict means the author model asserted something untrue; that is
            # itself worth recording, but it never enters the held-out set.
            (admitted if verdict is True else rejected).append(rec)
        print(f"  [{domain}] {len([a for a in admitted if a['domain']==domain])} admitted "
              f"of {len(items)} proposed")

    for i, rec in enumerate(admitted, 1):
        rec["bid"] = f"BP-{i:03d}"

    # The holdout: statements ONLY. No checker, no truth value. This is the sole
    # artifact any downstream translator is permitted to read.
    holdout = {
        "set": "B_prime",
        "purpose": "held-out novelty-reach benchmark; pre-registered before any widening",
        "author_model": MODEL,
        "n": len(admitted),
        "items": [{"bid": r["bid"], "domain": r["domain"], "statement": r["statement"]}
                  for r in admitted],
    }
    oracle = {
        "set": "B_prime_oracle",
        "warning": "QUARANTINED. Never expose to a translator/solver at build or grade time.",
        "author_model": MODEL,
        "items": admitted,
        "rejected": rejected,
    }
    HOLDOUT_PATH.write_text(json.dumps(holdout, indent=2), encoding="utf-8")
    ORACLE_PATH.write_text(json.dumps(oracle, indent=2), encoding="utf-8")
    return {"admitted": len(admitted), "rejected": len(rejected)}


if __name__ == "__main__":
    print(f"Authoring B' with {MODEL} (independent family) ...")
    stats = generate()
    print(f"\nadmitted={stats['admitted']}  rejected={stats['rejected']}")
    print(f"holdout (statements only): {HOLDOUT_PATH}")
    print(f"oracle  (QUARANTINED)    : {ORACLE_PATH}")
