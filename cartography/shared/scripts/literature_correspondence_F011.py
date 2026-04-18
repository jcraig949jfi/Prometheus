"""literature_correspondence_F011.py — Targeted literature audit across the recursion.

For each empirical finding at depths 1-4 of the F011 investigation, ask the
literature (via frontier model with math-research training): what classical
or recent result corresponds? Does it match, extend, or contradict?

Method: single Claude Opus call with 7 specific findings and a structured
output format. The model enumerates references; I cross-walk against our
data for matches and mismatches.

Output: cartography/docs/literature_correspondence_F011.md
"""
import sys
import io
import time
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


FINDINGS = """
Seven specific empirical findings on elliptic curve L-function zero statistics at
conductor range log10(N) in [3.8, 5.6] (LMFDB data, n=2,009,089 curves with
at least 2 zeros each, unfolded via (gamma/2pi)(log(N*gamma^2/4pi^2) - 2)):

F1. Pooled first-gap variance is 0.110 vs GUE Wigner 0.178 — 38.17% deficit at
    n=2M. Second-gap variance is 0.126 vs GUE 0.178 — 29.07% deficit. First-gap
    deficit exceeds second-gap by z(d1-d2) = 96.97. Monotone shrinkage with
    conductor (decile 0 log_cond=4.17: 45.37%; decile 9 log_cond=5.58: 35.34%).

F2. Per-analytic-rank first-gap variance: rank 0 (n=773K) var=0.0954
    deficit=46.4%; rank 1 (n=1M) var=0.1161 deficit=34.8%; rank 2 (n=222K)
    var=0.1211 deficit=32.0%; rank 3 (n=5.4K) var=0.1118 deficit=37.2%.
    Rank 0 has the LARGEST deficit (no forced central zero). Rank 2 has the
    SMALLEST (two forced zeros). The naive "more forced zeros = more repulsion
    = bigger deficit" ordering is INVERTED in our data.

F3. Rank-0-only conductor-window power-law fit:
    deficit = eps_0 + C * conductor^(-beta) gives
    eps_0 = 31.08 +/- 6.19 percent, C = 77.33, beta = 0.137, chi2 = 19.6.
    A 1/log(N) classical ansatz gives eps_0 = 22.90 +/- 0.78 percent, z=29sigma,
    chi2 = 20.3. A 1/log(N)^2 CFMS heuristic gives eps_0 = 35.83 +/- 0.36,
    chi2 = 27.4. Point estimate is ansatz-sensitive; data does not constrain
    alpha in eps_0 + C/log(N)^alpha jointly.

F4. Katz-Sarnak symmetry stratification (P028 analog): SO_even (rank even)
    vs SO_odd (rank odd) give deficit spread 7.63 percent across the full data.
    At per-rank level: SO_even slope of variance vs rank is +0.0128/rank
    (INCREASING from rank 0 to rank 2); SO_odd slope is -0.0022/rank
    (slightly DECREASING). Sign flip between symmetry classes. Durable under
    block-shuffle-within-conductor-decile null at z_block=111.78 (SO_even/odd
    spread) and z_block=15.31 (slope difference).

F5. CM vs non-CM rank-0 split: CM is 0.9 percent of rank-0 curves
    (n=1,766 across full conductor range). Non-CM alone gives eps_0 = 29.94%
    +/- 7.14 -- essentially identical to the pooled 31 percent. CM
    subfamily is too thin for independent decay fit. CM is NOT carrying the
    residual.

F6. P104 block-shuffle audit of F3 residual under three confounds: class_size
    gives spurious degenerate null (dominant stratum); cm_binary gives z=0.63
    NOT_DURABLE (but noisy with 0.9 percent CM population); torsion_bin gives
    z_block=4.19 DURABLE. The residual survives the cleanest confound-audit.

F7. Low-conductor rank-0 cohort (log_cond<4.0, n=21,169) has deficit 57.12%
    -- 13 percentage-points higher than the rank-0 average. Population is
    diverse (top-20 isogeny classes concentration 0.001), not a Cremona-table
    selection artifact. CM fraction 0.9 percent, matching overall rank-0.
"""


SYSTEM_PROMPT = """You are a research-grade mathematician with expertise in
L-function random matrix theory, elliptic curve L-functions, one-level densities,
finite-conductor corrections (Duenez-Huynh-Keating-Miller-Snaith, Miller, Conrey-
Farmer-Mezzadri-Snaith, Young, Forrester-Mays), and Katz-Sarnak symmetry types.

For each of the 7 empirical findings (F1-F7) you will be given, you will
produce structured output: for each finding, state:

  - RELEVANT_PAPER: the single paper whose result most directly bears on the
    observation (author, year, short descriptor).
  - PREDICTED_MAGNITUDE: the theoretical prediction (qualitative or quantitative
    order of magnitude) at our conductor range log10(N) in [3.8, 5.6].
  - MATCH: CONSISTENT / CONTRADICTS / EXTENDS / NOT_YET_CHECKED.
  - MATCH_REASONING: one-sentence reasoning.
  - NEW_QUESTION_OPENED: if the match is CONSISTENT, what refined question does
    it raise? If CONTRADICTS, what does the contradiction suggest?

Return as markdown with one H2 heading per finding (F1 through F7). No
preamble. Start directly with ## F1.

Do NOT hallucinate paper titles or theorem content; if you are uncertain of a
specific citation, say so and give the best-known closest reference. Better to
admit uncertainty than to fabricate."""


def call_claude() -> str:
    import anthropic
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from keys import get_key
    client = anthropic.Anthropic(api_key=get_key("CLAUDE"))
    t0 = time.time()
    r = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": FINDINGS}],
    )
    print(f"[call] model={r.model} in={r.usage.input_tokens} out={r.usage.output_tokens} elapsed={time.time()-t0:.1f}s")
    return r.content[0].text


def main():
    print("[lit] calling Claude Opus for literature correspondence...")
    resp = call_claude()
    rawpath = Path("cartography/docs/literature_correspondence_F011_raw.txt")
    rawpath.parent.mkdir(parents=True, exist_ok=True)
    rawpath.write_text(resp, encoding="utf-8")

    preamble = [
        "# Literature Correspondence — F011 Rank-0 Residual Investigation",
        "",
        "**Purpose:** systematic Pattern 5 gate across every finding in the F011",
        "investigation (depths 1-4 of the recursion). For each empirical result,",
        "what does classical or recent L-function RMT literature say? Does the",
        "observation match, extend, or contradict existing theory?",
        "",
        "**Method:** single Claude Opus 4.7 call with the 7 specific findings and",
        "a structured output format. Raw response at ",
        "`cartography/docs/literature_correspondence_F011_raw.txt`.",
        "",
        "**Provenance chain:**",
        "- Aporia Report 1 → F011 pooled = DHKMS excised (confirmed)",
        "- Four-paths reflection → rank-0 residual ε₀=31%/22.9% discovered",
        "- Five threads → P104 formalized; DHKMS / Miller catalog entries drafted",
        "- Six recursion sub-threads → torsion-confound durable; confound discipline",
        "- Four depth-4 sub-sub-threads → CM ruled out as carrier",
        "- This document → literature audit buffering every finding against theory",
        "",
        "---",
        "",
    ]
    body = resp
    outpath = Path("cartography/docs/literature_correspondence_F011.md")
    outpath.write_text("\n".join(preamble) + body, encoding="utf-8")
    print(f"[lit] wrote {outpath}")
    # rough audit of the response
    n_matches = resp.lower().count("match:")
    print(f"[lit] MATCH lines: {n_matches} (expected 7)")


if __name__ == "__main__":
    main()
