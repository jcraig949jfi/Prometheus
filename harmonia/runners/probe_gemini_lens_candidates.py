"""Probe Gemini for cross-disciplinary lens candidates beyond methodology_toolkit.md.

Active-mode iteration per James (2026-04-22): use external API (Gemini, different
model family from Claude) to surface candidate conceptual lenses Prometheus
might be missing. Many-lenses, conceptual not domain-specific.

Output: cartography/docs/probe_gemini_lens_candidates_results.md
"""
import os
import sys
import io
import json
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from keys import get_key

GEMINI_KEY = get_key("gemini")
# Try multiple Gemini models in order; first one not rate-limited wins.
GEMINI_MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-pro",
]


def gemini_url(model):
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={GEMINI_KEY}"
    )

EXISTING_LENSES_CONTEXT = """\
Project Prometheus catalogs methodological "lenses" for measuring mathematical
structure. The current shelf (methodology_toolkit.md) has six entries — each
borrows vocabulary from a non-mathematical discipline:

1. KOLMOGOROV_HAT (CS) — fingerprint compressibility via gzip-style estimator
2. CRITICAL_EXPONENT (statistical mechanics) — scaling-law extraction at phase
   transitions; equivalence-class index
3. CHANNEL_CAPACITY (Shannon information theory) — bits-per-object that survive
   a projection
4. MDL_SCORER (Rissanen MDL) — model comparison via total description length
5. RG_FLOW (renormalization group) — trajectories not endpoints; fixed-point
   universality classes
6. FREE_ENERGY (variational free energy) — temperature-parameterized model
   mixture decisiveness

The pattern: each tool's scorer is concrete (input signature + output shape),
and each tool measures "how much structure is in this data under a
compression / information-theoretic / physical lens?"

Each lens entry must include:
  (a) FRAME — non-mathematical discipline of origin
  (b) SCORER — concrete input signature -> output shape (writable as pseudocode)
  (c) RESOLVES — what equivalence class or claim the lens makes tractable
      that current arithmetic projections cannot
  (d) EFFORT — honest tick estimate
  (e) COMPOSES_WITH — which generators / sweeps / shelf tools it interlocks with
"""

PROMPT = (
    EXISTING_LENSES_CONTEXT + "\n\n"
    + """\
TASK: Propose 6 NEW lens candidates for Prometheus's methodology shelf, drawn
from disciplines NOT YET represented above (the existing shelf already covers
CS, statistical mechanics, Shannon information theory, MDL/Bayesian model
comparison, renormalization group, and variational free energy).

Look toward: linguistics, ecology, evolutionary biology, neuroscience,
economics, control theory, systems biology, sociology of knowledge,
topology of data, category theory, formal verification, music theory,
crystallography, nonequilibrium thermodynamics, signal processing.
Or any other discipline where a generative analytic concept exists.

CONSTRAINTS:
- Each candidate MUST cite a specific concrete concept from its source
  discipline (not "ideas from X" but "concept Y from X").
- Each candidate MUST sketch a SCORER pseudocode — input(s) -> output shape.
  If you cannot write the pseudocode in 3-5 lines, the lens isn't ready.
- Each candidate MUST name what equivalence class or measurement it would
  make TRACTABLE that the existing 6 lenses can't.
- AVOID: candidates that are merely re-labellings of the existing 6 (e.g.,
  "complexity" as a vague restatement of K̂; "self-organization" as a
  hand-wave at RG flow). Prometheus has Pattern 30 discipline against
  symbol-coupling; the same applies at the lens level.
- AVOID: candidates that are domain-specific to mathematics (e.g., "Galois
  cohomology"). Lenses must be conceptual transplants from elsewhere.
- AVOID: stacking multiple disciplines into one candidate. One candidate =
  one source discipline.

OUTPUT FORMAT (strict, parsable):

CANDIDATE 1
NAME: <short symbolic name, ALL_CAPS>
FRAME: <discipline + specific concept>
SCORER: <3-5 lines pseudocode>
RESOLVES: <equivalence class or measurement made tractable; ~2 sentences>
EFFORT: <ticks, honest>
COMPOSES_WITH: <existing tools or generators>

CANDIDATE 2
... (same structure)

... up to CANDIDATE 6.

After the 6 candidates, add ONE additional section:

META: <2-3 sentences on which of your 6 candidates you'd promote first if
you could only ship one; and which discipline you'd target NEXT if asked
for 6 more.>
"""
)


def call_gemini(prompt, timeout=180):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
    }
    last_err = None
    for model in GEMINI_MODELS_TO_TRY:
        url = gemini_url(model)
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            cand = data["candidates"][0]
            finish_reason = cand.get("finishReason", "unknown")
            text = cand["content"]["parts"][0]["text"]
            print(f"[probe] {model}: text_len={len(text)} finish_reason={finish_reason}")
            if finish_reason in ("STOP", None) and len(text) > 1500:
                return text, data, model
            print(f"[probe] {model} response too short or truncated; trying next...")
            last_err = RuntimeError(f"{model}: short/truncated response")
        except urllib.error.HTTPError as e:
            print(f"[probe] {model} -> HTTP {e.code}, trying next...")
            last_err = e
        except Exception as e:
            print(f"[probe] {model} -> {type(e).__name__}: {e}, trying next...")
            last_err = e
    raise RuntimeError(f"all Gemini models failed; last error: {last_err}")


def call_deepseek(prompt, timeout=180):
    """Fallback: DeepSeek Chat (OpenAI-compatible API)."""
    deepseek_key = get_key("deepseek")
    url = "https://api.deepseek.com/v1/chat/completions"
    body = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {deepseek_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    text = data["choices"][0]["message"]["content"]
    return text, data, "deepseek-chat"


def main():
    print("[probe] calling Gemini for cross-disciplinary lens candidates...")
    t0 = time.time()
    try:
        text, raw, model_used = call_gemini(PROMPT)
    except Exception as e:
        print(f"[probe] all Gemini fallbacks exhausted ({e}); trying DeepSeek...")
        text, raw, model_used = call_deepseek(PROMPT)
    elapsed = time.time() - t0
    print(f"[probe] response in {elapsed:.1f}s; {len(text)} chars from {model_used}")

    out_path = Path("cartography/docs/probe_gemini_lens_candidates_results.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Probe: Gemini cross-disciplinary lens candidates\n\n"
        f"**Probed by:** Harmonia_M2_auditor at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
        f"**Model:** {model_used} (via Google REST API)\n"
        "**Purpose:** active-mode brainstorm per James 2026-04-22; surface candidate conceptual lenses\n"
        "beyond the 6 currently in `harmonia/memory/methodology_toolkit.md`. Many-lenses CONCEPTUAL,\n"
        "not domain-specific. Cross-model variance for analogy diversity per\n"
        "`harmonia/memory/methodology_multi_perspective_attack.md`.\n\n"
        f"**Elapsed:** {elapsed:.1f}s; **response length:** {len(text)} chars\n\n"
        "**Caveat:** these are LLM-generated candidates. Per the MPA LLM-variance caveat,\n"
        "any single run is one realization, not the distribution. Treat as candidates for\n"
        "inspection by Harmonia auditor + sessionB + sessionC + cartographer; vet each\n"
        "before promoting any to `methodology_toolkit.md`. Specifically check:\n"
        "(a) does the named source-discipline concept actually exist as described?\n"
        "(b) is the scorer concrete enough to write Python in <100 lines?\n"
        "(c) is it genuinely new (not a re-labelling of one of the 6 existing)?\n"
        "(d) does it pass the Pattern 30 / FRAME_INCOMPATIBILITY_TEST analog at the lens level\n"
        "    (does it make a measurement none of the 6 existing tools can)?\n\n"
        "---\n\n"
        "## Gemini response\n\n"
    )
    out_path.write_text(header + text + "\n", encoding="utf-8")
    print(f"[probe] wrote {out_path}")
    return text


if __name__ == "__main__":
    main()
