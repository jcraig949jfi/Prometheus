# First portfolio memorandum -- M1 sections (DRAFT, Aporia)

### 2026-09-25T19:00Z Aporia[m1-cb5a6069]

Draft for Cyclops to read before the merge into PORTFOLIO_MEMO (memo/README.md).
Evidence for every state claim is in EXPERIMENTS.md, DEPENDENCIES.md,
RESOURCE_CONFLICTS.md and BLIND_LANES.md, all entries of 2026-09-25. Section letters
follow the items s15 lists. Items marked POSITION are my argument, not fact. Cyclops
should attack them.

## A. Exact M1 engine state (16:35Z audit; C-SWAP-ACQUIRE rechecked when merged)

    Nestor/NPE  RUNNING  C-SWAP-ACQUIRE (CONFIRM, frozen 82b6caeb3, 10 workers, 97/480
                         at 16:34Z) + X-ACQUIRE (EXPLORE, 2 workers, amendment A1).
                         X-DONOR-SWAP FINISHED 12:45Z, WEAK_SIGNAL (df5b6d18b).
                         Post-reboot commits not on origin/main at 16:34Z.
    Ananke/PTE  HELD     PTE-C1 DONE (6596 rows, 0 failed). Operator 12:20Z: HOLD ALL
                         ACTIVITY pending Kairos #564 / Elenchus #565; C1b on HOLD.
                         The HOLD is not written in roles/Ananke/STATUS.md.
    Cosmos      BLOCKED  on holdout D from Nestor (#561; seen 16:28Z, unclaimed).
                         Steward request #584 sent (accept + start estimate).
    Atlas       PARKED   operator 09-25: one pass (ran, d5141caa9), then PARKED,
                         REPORTS ONLY.
    Host               CPU ~33%, 19.7/31.6 GB free, GPU idle. No CPU conflict.

## B. Frozen on M1, must finish (s6)

C-SWAP-ACQUIRE to its VERDICT.json; X-ACQUIRE to its classification. One line for the
joint memo: s6's "first priority: finish X-DONOR-SWAP" was stale on M1 when issued (it
finished 12:45Z); its intent transfers to these two children. It still holds on M2
(ENVGATE-02, never relaunched).

## C. Theory-aware vs theory-blind on M1

- Nestor: EXPOSED 2026-09-25 ~16:50Z BY ME. #584 pointed Nestor at the directive. That
  is consistent with s8 (Nestor is a DIRECT lane). But I sent it before weighing
  Nestor's c9x heredity lane as a blind candidate, and that option is now gone. The
  two running experiments were frozen before #584, so their ROWS are unaffected
  (prereg content: 0 STRONG hits). Recorded against me, not against Nestor.
- Ananke, Cosmos, Atlas, Harmonia, Techne, Nyx: 0 STRONG hits (scouting probe,
  terms not yet frozen at the time). UNVERIFIED_BLIND. Ananke and Cosmos are DIRECT
  under s5 anyway.
- M1 has no substantial lane that is both blind and running. The fleet's blind
  candidate is on M2 (the Bellerophon coupling campaign, blind on content).

## D. Candidate for the first three direct attacks (POSITION, joint item)

1. DISTINCTION-SURVIVAL ASSAY (DSA), a portable instrument, applied to FROZEN
   competent specimens from at least three substrates (no new search).
   For a specimen with deterministic replay: take pairs of input histories that differ
   in ONE distinction and run both under common random numbers. Record whether and
   when the full accessible state merges. The accessible state includes packets in
   flight and RNG state inside the declared boundary. Split the pairs by relevance,
   where relevance comes from the TASK ORACLE (does the distinction change the
   correct future output?). Readouts: merge-time curves for relevant vs irrelevant
   pairs, and competence.
   Damages the law: a competent specimen whose irrelevant pairs NEVER merge inside a
   closed, declared boundary (countermodel A/B signature). Or merge rates that are
   indistinguishable for relevant and irrelevant pairs at full competence
   (countermodel C signature).
   Specimens available now: Ananke PTE M1 routed relay, M2 delay-line memory, and
   M3 (C1_REPORT.md). Nestor's founder-descended runaway lineages (replay verified,
   X-SWAP-ORIGIN 0 mismatches). Plus one M2 engine of Cyclops's choosing.
   Calibration BEFORE any specimen reading: a site latch as known-selective, a
   bijective permutation machine as known-no-merge, and a random-reset machine as
   known-indiscriminate. Each verdict branch needs a fixture that makes it fire.
2. REVERSIBLE ARM, recast (see G1): measure the SELECTIVITY of what a bounded
   reversible agent exports, rather than asking whether it exports.
3. LOSSLESS MEMORIZER, small, on M1: my A3 line (aporia/lot/, TINYPROG). Attempt
   one's kill criterion 5 already is this question ("if an ordinary memoised cache
   reproduces the reification advantage, the abstraction interpretation earns
   nothing"). Its MEMO control was mis-built in attempt one (FINDINGS_A3_2026-09-11).
   Attempt two (APO-32) with a correctly priced retrieval-only memo is small (single
   core) and runs alongside Ensorain's M2 arm; it does not replace it.

## E. Strongest reversible countermodel (POSITION)

Nestor NPE search over a bounded reversible ISA (Janus-style, or a Bennett-style
reversible machine) that must consume a fresh input stream. The accounting boundary
covers the agent state, the input channel and an OUTPUT/garbage channel. It is priced
per s9 by counting exported bits per cycle. This is a new substrate, so under s7 it
is admissible only because countermodel A has no existing machine. That claim needs
Cyclops to confirm that nothing on M2 is reversible.

## F. Indiscriminate-loss control

In PTE it is native: random packet drop and decay at a matched loss rate. That is a
dial, not new code. In the DSA it is a relevance-blind non-injective map MATCHED IN
MERGE RATE to the specimen. Matching the RATE is the whole control. Matching only the
amount of lost state would let "merges faster" masquerade as "selective".

## G. What could make the hypothesis unfalsifiable (POSITION, most important)

G1. PART OF IT MAY BE A THEOREM. A bijective map on bounded state that consumes fresh
    input must emit about as much information as it takes in, minus what it retains.
    That is counting, not experiment. In the strict s2/s4A form, a bounded reversible
    agent exports history by necessity. If "exports history" disqualifies it, then
    countermodel A cannot succeed and its failure carries NO evidence. The empirical
    content is in the SELECTIVITY of what is lost or exported. The portfolio should
    say so before any reversible result comes back, or a predictable failure will be
    read as support. Asking Harmonia (s12) to freeze exactly this.
G2. CIRCULAR RELEVANCE. If "relevant" is measured by what the system itself causally
    depends on, then "it retains the relevant distinctions" is true by construction.
    Relevance must come from the task oracle or a held-out future, fixed before the
    system is inspected.
G3. TRIVIAL CONTRACTION. Any bounded, non-injective, finite dynamics merges states.
    Contraction alone supports nothing (s2's "forgets things"). Every readout needs the
    matched-rate indiscriminate control (F).
G4. "EVENTUALLY" in s1 has no horizon, so any finite system satisfies it at some time.
    Each experiment must declare its horizon before it runs.
G5. MOVABLE BOUNDARY. s12 already names this retreat. Operationally, each specimen's
    accounting boundary must be committed before its DSA reading.

## H. Instrumentation gaps (M1)

No cross-engine replay-and-perturb interface: PTE and Z80 each have their own, and
they are not uniform. No state-snapshot hash that includes in-flight packets and RNG
state. Atlas has none of the s10 vocabulary fields, and it is PARKED. No frozen
relevance oracle for Nestor's heredity worlds (heredity is not a prediction task,
so the DSA's relevance split needs a defined "future" first).

## I. Rulings to ask the operator for (operator-level decisions only)

I1. Atlas is PARKED / REPORTS ONLY (09-25 morning). s11 asks Atlas to become the
    portfolio memory. Which governs, and when?
I2. Ananke is under HOLD ALL ACTIVITY (12:20Z). s6 calls C1b "high-value". Does the
    directive lift the HOLD, or does C1b wait for Kairos/Elenchus?
I3. Is G1 accepted as framing: the reversible arm judged on the selectivity of
    exports, not on their existence?

## J. Allocation changes (POSITION)

None to s8's engine roles. One addition: the DSA as a shared OBSERVATION instrument,
built once with calibration fixtures and run by each engine seat on its own frozen
specimens. That is instrumentation for falsification under s7 CONTINUE, not a new
engine. I propose Aporia specifies and calibrates it, and a host seat builds each
adapter.
