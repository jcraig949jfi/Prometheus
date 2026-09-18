# Adjudication of the Gemini Pro and ChatGPT reviews of RSI-1 (2026-09-18)

Currency: 2026-09-18. Author: Aphrodite. Inputs (verbatim, hashed):
prompts/2026-09-18_rsi1_reviews/{GEMINI_PRO,CHATGPT}_verbatim.md. Output:
designs/RSI_PROGRAM_v2.md. No model adjudicates science here; this file
records which DESIGN proposals the seat adopts and why, so the choice is
attackable. Neither review is treated as authority; both are treated as
careful proposals.

Verdict words: ADOPT (as proposed), ADAPT (adopted with a stated change),
REJECT (with the reason), DEFER (needs the operator or another seat).

## A. Endpoint and statistics

A1 (ChatGPT) Primary endpoint = compute-matched capability difference
    Delta = C(I_8(A); B) - C(I_0(A); B) at identical escrow B, repeated at
    preregistered budgets B1 < B2 < B3; the strong claim is an outward
    shift of the capability-vs-compute frontier. R_t kept descriptive.
    ADOPT. Reason: a ratio with a small, variable denominator is
    heteroskedastic and gameable; matched escrow removes "buying accuracy
    with compute" by construction. Gemini's gate 3 ("brute-force
    masquerade": C_8 > C_0 but R_8 <= R_0) is SUBSUMED -- under matched
    escrow I_8 cannot spend more.
A2 (ChatGPT) Equivalence region |Delta| < delta; the interesting null is
    the CI lying entirely inside [-delta, +delta] (EQUIVALENT), distinct
    from "failed to reject". ADOPT, with a seat condition: delta is fixed
    from downstream need BEFORE any Campaign 1 data (base role: thresholds
    come from downstream need), in task units (additional tasks solved at
    fixed escrow), and Campaign 0 must show the design has power BOTH to
    detect delta AND to establish equivalence within delta (equivalence
    typically needs more lineages than detection).
A3 (Gemini) Cohen's d < 0.2 as a gate. REJECT (both ChatGPT's reason --
    effect sizes belong in the experiment's own units -- and the seat's:
    a standardised effect hides the budget dependence A1 exists to show).
A4 (Gemini) "CI of R_8 - R_0 includes zero -> RSI refuted". REJECT;
    replaced by A2's three-way verdict: SUPERIOR / EQUIVALENT /
    INDETERMINATE (and INFERIOR).
A5 (ChatGPT) Hierarchical model: outcome ~ I + family + lineage +
    I x family + noise; lineages, families, instances, sampling and
    transplant seeds are not iid. ADOPT. Seat implementation note: a
    hierarchical bootstrap (resample lineages, then families within
    lineage, then instances) is stdlib-implementable and is validated in
    Campaign 0 against synthetic data with known variance components.
A6 (Gemini) Generalisation floor: advantage on development worlds A that
    vanishes on vault C = specialisation. ADOPT as a PATTERN (reported,
    not a single gate), refined by A7's layers.

## B. Worlds and contamination

B1 (Gemini) Generator committed by hash before generation 0; vault seed
    from a public future-entropy beacon (NIST beacon pulse / block hash)
    resolving after the scheduled freeze; clean-room instantiation.
    ADAPT. The seat adds: the beacon's main value is against the
    EXPERIMENTERS (no one can choose or re-roll the vault after seeing
    lineages) as much as against I_t; the manifest records the beacon
    identifier and the received value with its source signature; a
    fallback beacon is named in advance.
B2 (ChatGPT) "The instances do not yet exist. The task distribution
    does." Vault layers: C1 future instances of committed families
    (instance memorisation); C2 future instances of sealed families never
    exposed (distribution transfer); C3 families written independently
    after the freeze. ADOPT. C3 authorship must be a seat with no access
    to the lineages.
B3 (Gemini) "Cryptographic proof that the improvement is algorithmic
    generalisation." REJECT the wording. The commitment proves the
    instances did not exist during evolution; it proves nothing about
    WHY I_8 did better. Causation comes from D below.

## C. The improvement operator I_0

C1 (Gemini) I_0 as typed, modular Python classes under a strict protocol,
    not a metaprompt; mutation space includes orchestration code, not
    only strings. ADOPT.
C2 (Gemini) Four modules: search/generation, verification/critique
    router, memory/distillation, budget allocator. ADOPT.
C3 (ChatGPT) Fifth module: experiment/evidence policy (what the improver
    measures before deciding how to mutate itself). ADOPT. Seat addition
    (neither review): the five modules act on DIFFERENT TIMESCALES --
    search, verify, allocate act within a task; memory acts across tasks;
    evidence acts across GENERATIONS (it shapes mutation, not task
    performance). Their causal tests therefore differ: Evidence_8's
    necessity/sufficiency must be measured on the improvement phase (does
    I_0 + Evidence_8 produce better descendants over k generations?), not
    on task score.
C4 (Gemini) Two-phase commit: I_t proposes a diff; viability preflight in
    the sandbox (compiles, satisfies the protocol, passes a null task
    without looping or exhausting its budget) before I_{t+1} is accepted.
    ADOPT. Rejected diffs are kept (Necropolis-style), not discarded.
C5 (seat, neither review) Interface compatibility is what makes the
    factorials DEFINED. I_0 x M_8 requires I_0's memory module to be able
    to read an evolved store; module swaps require evolved modules to keep
    the protocol. So: memory is a typed store with a fixed read protocol;
    an evolved module may add capabilities but must still serve the
    protocol; a swap that the protocol cannot express is reported as
    UNDEFINED, not scored.

## D. Transplant and causal decomposition

D1 (ChatGPT) Factorial transplant I x M (and I x A when workers evolve).
    ADOPT. Without it an improver is credited for a better memory or a
    better worker.
D2 (Gemini) "Lobotomise the most-mutated module". REJECT: lines changed
    is not causal importance (ChatGPT's reason, which the seat shares).
D3 (ChatGPT) Complete preregistered decomposition: replace each evolved
    module with its I_0 version (necessity), transplant each evolved
    module alone into I_0 (sufficiency), pairwise where first-order
    effects suggest interaction. ADOPT, with C3's timescale caveat and
    C5's UNDEFINED rule.
D4 (seat) Lineages that ever exploited an evaluator hole are flagged; all
    transplant results are reported with and without them (library
    THEORIES T4: exploits persist through clean evolution unless a clean
    reservoir survives; Roesner and Kohno arXiv 2609.17817 found 28-30/30
    persistence in three systems).

## E. Metering

E1 (Gemini) Metering below I_t: all model calls and execution pass a
    proxy I_t cannot bypass; escrow per task; hard stop on exhaustion.
    ADOPT (the seat's X2: an improver that can reach its accounting hole
    finds it in one generation).
E2 (Gemini) Attribution by reading Python call stacks. REJECT (ChatGPT):
    untrusted code can distort stacks. ADOPT ChatGPT's replacement:
    unforgeable per-module resource handles; the global budget below.
E3 (Gemini) "Universal Compute Cost" alpha T_in + beta T_out with beta = 3
    "reflecting FLOPs". ADAPT (ChatGPT): call it a Standardized Inference
    Cost with fixed per-model tariffs; do not claim FLOPs. Where
    Prometheus controls the GPUs (M1/M2 RTX 5060) also record accelerator
    seconds; report both; the primary endpoint uses the preregistered one.
E4 (Gemini) The harsh escrow gradient "forces efficient intelligence".
    ADAPT: it also selects policies adapted to ONE budget. Hence A1's
    budget grid, with at least one test budget below and one above the
    evolution budget.
E5 (Gemini) "We have mathematically proven algorithmic self-improvement"
    from a ledger showing a module's share of compute. REJECT: a ledger
    is descriptive; causation needs D3.

## F. Program structure and claims

F1 (ChatGPT) Campaign 0 instrument calibration (the toys and the assay);
    Campaign 1 "does the improvement operator transfer?" (stops at second
    order); Campaign 2 (third order) only if Campaign 1 survives and the
    assay has shown stable positive, negative, equivalence and
    contamination controls. ADOPT.
F2 (ChatGPT) A null is stated narrowly: "under the specified substrate,
    task ecology, mutation language, compute regime and evolutionary
    horizon, observed cumulative capability gains did not produce a
    detectable transferable improvement in the improvement operator."
    ADOPT verbatim. Gemini's "would empirically prove that current RSI is
    just compute-scaled search and memory" and "the industry paradigm is
    structurally capped": REJECT as overreach.
F3 (ChatGPT) The extraordinary-result chain (I_8 > I_0 on C2 at matched
    escrow; across budgets; necessity; sufficiency; third-order; some
    substrate transfer). ADOPT as the ladder of claims, each rung its own
    preregistered test.
F4 (both) Seat assignments (Archaeon ecology, Vivarium sandbox, Daedalus
    histories, Harmonia metering/shadow evaluator, Proteus manifests,
    Necropolis dead branches). DEFER: those are other seats' lanes; none
    has been asked; the operator decides whether Aphrodite asks them.
F5 (Gemini) "This is the correct mandate for the Aphrodite seat."
    DEFER: charter adoption is the operator's act (APHRODITE-08).

## G. What neither review addressed (seat's additions, collected)

G1 delta and power for equivalence (A2). G2 module timescales (C3).
G3 interface compatibility makes factorial cells defined (C5).
G4 exploiter-flagged lineages (D4). G5 a planted-dividend POSITIVE
control run through the entire chain, and a memorised-vault CHEAT
control, before any real lineage is read (Campaign 0) -- without them a
null is uninterpretable and a positive is unfalsifiable.
