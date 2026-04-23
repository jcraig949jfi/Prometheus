"""Probe Gemini on FRAME_INCOMPATIBILITY_TEST@v1.1 formal-definition tightening.

Cross-FAMILY 4th seed (after sessionA Sonnet 4-6 x2, sessionB Sonnet 4-5,
sessionC Opus 4-7 — all Anthropic). Gemini = different model family, tests
whether the meta-pattern (classifier underspecified) is family-invariant or
Anthropic-internal artifact.

Per sessionA replication-check (1776906957066-0), Y_IDENTITY_DISPUTE labeling
was prompt-steered. Revised v1.1 direction (sessionA + sessionB + sessionC
consensus): tighten existing 3-way classifier definitions, don't add 4th outcome.

Specifically test whether Gemini agrees with the team's revised direction
(definition-tightening) AND with the specific underspecifications named:
- "incompatible" undefined (logical vs different-magnitude)
- "measurable now" context-indexed not lens-set property
- "shared observable" needs identity criterion
- "consensus" not operationalizable
- classes not exhaustive (no-prediction lenses)
- classes not mutually exclusive

Output: cartography/docs/probe_gemini_v11_definitions_results.md
"""
import sys, io, json, time, urllib.request
from pathlib import Path
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from keys import get_key

GEMINI_KEY = get_key("gemini")
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
)

# Neutral prompt — minimal anchor detail, asks ONLY whether the classifier is
# well-specified. Does NOT prime with the Irrationality Paradox shape that
# sessionA's first probe accidentally injected.
PROMPT = """\
Evaluate the following three-way classifier for whether it is well-specified.
The classifier sorts research-problem catalogs of "multiple disciplinary
lenses on the same problem" into three categories:

CLASS A (PASS): the catalog's lenses make incompatible predictions on at least
one downstream observable Y, where Y is measurable at currently-accessible
data scale AND has not yet been resolved by past measurement.

CLASS B (FAIL via no-substrate-Y, "CND_FRAME"): the catalog's lenses agree on
the primary measurable Y but disagree on a meta-axis (which obstruction
applies, which truth-axis the disagreement lives on, which framing names the
phenomenon).

CLASS C (FAIL via uniform alignment, "CONSENSUS_CATALOG"): all the catalog's
lenses align with a community consensus on the primary truth-axis; no
adversarial frame is catalogued.

Question 1: Is this classifier well-specified? List any places where its
admission criteria are under-defined or admit adversarial steering.
Question 2: For each underspecification you identify, propose a concrete
formal tightening that would close the loophole.
Question 3: Are these three classes EXHAUSTIVE (cover all possible catalogs)
and MUTUALLY EXCLUSIVE (a catalog can sit in at most one)?

Be specific. Output as numbered objections + proposed fixes; not prose
narrative. Aim for 5-8 distinct objections.
"""


def call_gemini(prompt, timeout=180):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    cand = data["candidates"][0]
    return cand["content"]["parts"][0]["text"], cand.get("finishReason", "?")


def main():
    print("[probe] gemini-2.5-flash on v1.1 definition tightening...")
    t0 = time.time()
    text, finish = call_gemini(PROMPT)
    elapsed = time.time() - t0
    print(f"[probe] {elapsed:.1f}s, {len(text)} chars, finish={finish}")
    out = Path("cartography/docs/probe_gemini_v11_definitions_results.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Probe: Gemini cross-family seed on FRAME_INCOMPATIBILITY_TEST@v1.1\n\n"
        f"**Probed by:** Harmonia_M2_auditor at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
        "**Model:** gemini-2.5-flash (Google) — 4th seed, FIRST cross-FAMILY (prior 3 all Anthropic Claude)\n"
        "**Purpose:** add cross-family corroboration for the team's converged finding "
        "(classifier under-defined; tighten formal definitions in v1.1 rather than add 4th outcome)\n"
        "**Prior seeds (all Claude):** sessionA Sonnet 4-6 x2 (1776906584732, 1776906957066); "
        "sessionB Sonnet 4-5 (1776906965662); sessionC Opus 4-7 (1776907144722)\n\n"
        "**Prompt was neutral** — no specific catalog anchored, no leading framing toward "
        "Y-IDENTITY-DISPUTE. Tests whether the meta-pattern (under-definition) replicates "
        "across model family or is Anthropic-internal.\n\n"
        f"**Elapsed:** {elapsed:.1f}s; **finish_reason:** {finish}; **response:** {len(text)} chars\n\n"
        "---\n\n## Gemini-2.5-flash response\n\n"
    )
    out.write_text(header + text + "\n", encoding="utf-8")
    print(f"[probe] wrote {out}")


if __name__ == "__main__":
    main()
