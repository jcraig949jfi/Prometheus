# RSI-1: does the improver become a better improver? (DESIGN DRAFT)

Currency: 2026-09-18. Status: DRAFT, NOT FROZEN, NOT A PREREGISTRATION.
Source: the external review relayed by the operator 2026-09-18
(prompts/2026-09-18_rsi_library/RELAYED_REVIEW_verbatim.md), which
proposes RSI-1 and a charter. This file restates it operationally and
adds what the seat thinks is missing. Nothing here is launched by this
seat (operator, 2026-09-18: focus on the thought work).

## 0. Prior art found 2026-09-18 (sources/rsi_core.md)

RSI-1 is not the first transplant-style test. Hyperagents (arXiv
2603.19461) transferred an evolved meta agent to an unseen domain
(imp@50 0.630 vs 0.0); AIDE^2 (Weco blog, 2026-07-14) installed its
evolved improver as the outer loop (faster, no asymptotic gain); HGM
measures metaproductivity directly; STOP applied a frozen improved
improver to 5 new tasks (2023). What appears not to exist is the
compute-matched, multi-seed, memory-stripped, multi-substrate version
with a planted-dividend positive control. RSI-1 should adopt imp@k and
metaproductivity as secondary endpoints so results are comparable.

## 1. The object

An improvement operator I maps (agent, history, budget) -> descendant
agent. Generation 0 has I_0. Descendants may modify the worker and,
in the strongest condition, parts of I itself (search policy, memory
policy, decomposition, verifier use, experiment allocation, lineage
selection, tool orchestration).

The endpoint is NOT final capability C_t. It is the improvement rate

    R_t = [ C(I_t(A), H) - C(A, H) ] / real improvement compute

with A a fresh agent and H a fresh hidden task population drawn for
this measurement only.

## 2. Conditions (compute-matched on REAL compute, metered outside I)

    FIXED-IMPROVER  I_0 improves workers, never itself
    MEMORY-RSI      + verified memory accumulates; I frozen
    ARCHIVE-RSI     + diverse archive of variants, DGM-style; mutation
                      and selection frozen; Dream-RSI replay available
    FULL-RSI        + descendants may modify I; replay available

Replay goes to both ARCHIVE and FULL so cheap reuse of history is not
confounded with recursion (reviewer's point).

## 3. Worlds

A development (visible, feedback), B promotion (hidden from I, used by
an external evaluator), C vault (never touched; opened once after
freezing; part of C generated AFTER freezing from a generator committed
before the run, so instance memorisation is impossible). Families should
be procedural: program repair, algorithm discovery, constraint/search,
optimisation, partially observable inference, and unfamiliar worlds.

## 4. Measurements

- C_t and R_t per lineage per generation, R_t always on a fresh H.
- The four shapes: C up with R flat (ordinary optimisation); C up with
  R falling (harvesting); C up with R rising (candidate RSI); replay up
  with hidden down (history overfit). FULL ~ FIXED = no dividend.
- Transplant matrix: I_0, I_2, I_4, I_8 per surviving lineage, memory
  stripped, given identical fresh agents; tested on (a) home families,
  (b) new instances, (c) new families, (d) another model substrate,
  (e) another machine, (f) a very different budget. Improver-to-seed
  assignment randomly permuted.
- Third order: I_0 and I_8 each improve themselves again for a fixed
  budget; compare R(I'_8) - R(I_8) with R(I'_0) - R(I_0).

## 5. Structural gates (the reviewer's, restated as checks)

G1 FULL beats compute-matched FIXED on held-out improvement rate.
G2 survives memory stripping. G3 survives fresh starting agents.
G4 appears across independent lineages, not one champion.
G5 some transfer outside the developmental distribution.
G6 ancestral replacement (swap evolved I back to I_0 parts) reduces it.
G7 removing the implicated evolved mechanisms reduces it.
G8 hidden external evaluation agrees with internal evaluation.
A null (workers improve; I_8 ~ I_0 once stripped) is a first-class
result: "RSI" in this regime would then be search + memory + selection.

## 6. What the seat adds (open before freezing)

6.1 Power. 32 lineages is a guess. Before freezing, simulate the
    analysis on synthetic lineages with a planted dividend of known size
    to find the smallest detectable dividend at 32 (and at 16 / 64).
    The seat's calibration row of 2026-09-17 (compute eligibility first)
    applies here most of all.
6.2 Noise floor per measurement (from E2's X1): every R_t comparison
    carries a same-budget random-perturbation control.
6.3 The counter is out of reach. Real compute (tokens, calls, wall
    time) is metered by an authority the improver cannot edit or read
    (X2: an improver that can reach its accounting hole finds it in one
    generation). The counter itself carries a cheat control.
6.4 Positive control for the whole apparatus: plant a known
    second-order improvement (e.g. an I_8 that is I_0 plus a scripted,
    genuinely better experiment-allocation rule) and show the pipeline
    detects it through the full strip-and-transplant chain. Without it a
    null is uninterpretable.
6.5 Cheat control: an I_8 that has memorised B/C instances (injected)
    must be caught by the post-freeze vault.
6.6 Exploit persistence: when FULL-RSI finds an evaluator hole, is it
    carried forward after the hole is fixed? S3 (toy) predicts it
    persists if the exploit has no true cost; measure it.
6.7 What may never be modified by I: the counter, the B/C evaluator,
    the vault generator, the lineage log. (QUESTIONS I3.)

## 7. Two scales

7.1 TOY-RSI-1 (CPU, this seat could build it; hours not days). Workers
    are small programs (e.g. heuristic solvers for procedural
    constraint/search/optimisation families); I is a program with
    mutable, typed parts (proposal distribution, allocation rule,
    acceptance rule, archive policy, verifier-routing rule); "model
    substrate" is replaced by two different worker languages or
    primitive sets. Value: calibrates the whole analysis chain (power,
    noise floor, positive and cheat controls) before any GPU hour is
    spent. Risk: the reviewer's warning that toys are too easy -- so the
    toy's only claim is "the apparatus can detect a planted dividend and
    refuses a fake one", never "RSI exists".
7.2 GPU-RSI-1 (M1/M2 RTX 5060, or RunPod). Small open models as the
    frozen substrate (the reviewer's substrate-transfer arm needs two);
    I as code the model can edit under a sandbox. Ownership would span
    seats (the reviewer names Archaeon worlds, Vivarium execution,
    Daedalus history, Harmonia shadow evaluator, Proteus manifests,
    Techne foreign mechanisms, Necropolis for failed lineages); none of
    those seats has been asked, and this draft commits none of them.

## 8. Decisions this design needs from the operator

- Adopt the proposed charter (APHRODITE-08)? The review's wording:
  "Determine experimentally whether an autonomous, population-based
  improvement process can produce transferable improvement in its own
  improvement operator, beyond gains attributable to memory
  accumulation, fixed search, replay, selection, or evaluator
  exploitation."
- Build TOY-RSI-1 first (seat's lean: yes, as apparatus calibration)?
- Which seats would own which parts of GPU-RSI-1, if it goes ahead?
