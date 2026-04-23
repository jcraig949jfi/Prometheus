"""Probe Gemini on whether the 4 STRONG lens candidates from earlier
brainstorm are operationalizable as concrete scorers in <100 LOC each.

Third probe-type per auditor probes_register.md note: 'numerical-eval probe
that tests proposed scorers on toy data before the team invests in the full
implementation'. This is the lighter version: ask whether each scorer CAN
be operationalized concretely (function signature + key arithmetic),
without actually implementing.

Output: cartography/docs/probe_gemini_scorer_tractability_results.md
"""
import sys, io, json, time, urllib.request
from pathlib import Path
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from keys import get_key

GEMINI_KEY = get_key("gemini")
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def gemini_url(model):
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={GEMINI_KEY}"
    )

PROMPT = """\
Evaluate the following 4 candidate analytic "lenses" for whether each can be
operationalized as a concrete Python scorer of <100 lines of code, given
data structures readily available in computational number theory (lists of
integers, floats, sparse matrices, lists of polynomial coefficients, lists
of vertex pairs for graphs).

For each candidate:
1. Write the Python function signature (with realistic input types).
2. Write the core arithmetic (3-7 lines of pseudocode or actual code).
3. State the OUTPUT TYPE and what range/values are typical.
4. Identify the BIGGEST IMPLEMENTATION HAZARD (e.g. "computing X requires solving NP-hard problem").
5. Assign a FEASIBILITY RATING: TRIVIAL / EASY / MODERATE / HARD / INFEASIBLE.
6. Suggest ONE concrete Prometheus dataset where the scorer would produce a
   non-trivial measurement (e.g., "Mahler measures of degree-≤30 monic integer
   polynomials"; "Tamagawa products across 222K rank-2 EC"; "isogeny-class
   graphs at conductor < 10^6").

CANDIDATES:

(A) CLADISTIC_PARSIMONY (evolutionary biology) — minimum number of
evolutionary steps to explain a feature distribution on a tree topology.
Input: a tree (parent-child relationships) + a feature matrix
(objects x binary characteristics). Output: integer = sum across
characteristics of minimum steps required.

(B) CONTROLLABILITY_RANK (Kalman, control theory) — for a discrete linear
system x[t+1] = A·x[t] + B·u[t], the rank of [B, A·B, A²·B, ..., A^(n-1)·B]
quantifies how many internal states can be influenced by inputs. Input:
two matrices A (n x n) and B (n x m). Output: integer in [0, n].

(C) GINI_COEFFICIENT (economics) — measures inequality of a distribution.
Input: a list of non-negative real values. Output: float in [0, 1] where
0 = perfectly equal, 1 = maximal inequality.

(D) NETWORK_MODULARITY (Newman) — measures community structure quality
of a graph given a partition. Input: adjacency matrix + partition
assignment (node → community ID). Output: float in [-0.5, 1] where
> 0.3 typically indicates strong community structure.

OUTPUT FORMAT (per candidate, in order A B C D):

CANDIDATE (A) CLADISTIC_PARSIMONY
SIGNATURE: ...
CORE_ARITHMETIC: ...
OUTPUT_TYPE: ...
HAZARD: ...
FEASIBILITY: ...
PROMETHEUS_DATASET: ...

(repeat for B, C, D)

Be concrete and concise; aim for 8-12 lines per candidate.
"""


def call_gemini(prompt, timeout=180):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 8192},
    }
    last_err = None
    for model in GEMINI_MODELS:
        try:
            req = urllib.request.Request(gemini_url(model), data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            cand = data["candidates"][0]
            text = cand["content"]["parts"][0]["text"]
            if len(text) > 1500:
                return text, cand.get("finishReason", "?"), model
            print(f"[probe] {model}: text too short, trying next...")
        except Exception as e:
            print(f"[probe] {model}: {type(e).__name__}: {e}, trying next...")
            last_err = e
    raise RuntimeError(f"all Gemini models failed; last: {last_err}")


def call_openai(prompt, timeout=180):
    """OpenAI fallback (gpt-4o-mini)."""
    openai_key = get_key("openai")
    url = "https://api.openai.com/v1/chat/completions"
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 4096,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    text = data["choices"][0]["message"]["content"]
    return text, "stop", "gpt-4o-mini"


def main():
    print("[probe] scorer tractability for 4 STRONG candidates...")
    t0 = time.time()
    try:
        text, finish, model_used = call_gemini(PROMPT)
    except Exception as e:
        print(f"[probe] all Gemini exhausted ({e}); trying OpenAI gpt-4o-mini...")
        text, finish, model_used = call_openai(PROMPT)
    elapsed = time.time() - t0
    print(f"[probe] {elapsed:.1f}s, {len(text)} chars, finish={finish} from {model_used}")
    out = Path("cartography/docs/probe_gemini_scorer_tractability_results.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Probe: Gemini scorer-tractability check for 4 STRONG lens candidates\n\n"
        f"**Probed by:** Harmonia_M2_auditor at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
        f"**Model:** {model_used} — 6th probe-result per probes_register.md cadence\n"
        "**Probe type:** scorer-tractability (the third probe-type per auditor 1776906776069-0); follows up "
        "earlier candidate-brainstorm probe (1776906653708-0) where the 4 STRONG candidates were "
        "first surfaced.\n\n"
        "**Question:** can each candidate be operationalized as a concrete Python scorer "
        "in <100 LOC, with a named Prometheus dataset where it would produce non-trivial output? "
        "Tractability gate before any team member commits to implementation.\n\n"
        f"**Elapsed:** {elapsed:.1f}s; **finish_reason:** {finish}; **response:** {len(text)} chars\n\n"
        "---\n\n## Gemini-2.5-flash response\n\n"
    )
    out.write_text(header + text + "\n", encoding="utf-8")
    print(f"[probe] wrote {out}")


if __name__ == "__main__":
    main()
