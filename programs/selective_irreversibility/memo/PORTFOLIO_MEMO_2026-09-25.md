# Selective Irreversibility -- first portfolio memorandum (directive s15)

### 2026-09-25T19:20Z Aporia[m1-cb5a6069] -- MERGE DRAFT

STATUS: merged by Aporia from memo/M1_sections.md (e9ef51e6c) and memo/M2_sections.md
(be5636af4). It becomes the joint memorandum when Cyclops co-signs it with an entry
below. Items tagged [PENDING-CYCLOPS] are Aporia refinements Cyclops has not yet seen.
Every state claim is sourced in the two drafts and in EXPERIMENTS.md,
RESOURCE_CONFLICTS.md and BLIND_LANES.md. This memo repeats conclusions, not
evidence. Directive: roles/Cyclops/prompts/2026-09-25_selective_irreversibility/
01_OPERATOR_DIRECTIVE_verbatim.md (sha256 f0dd0599).

## 1. Exact engine states (M1 16:35Z, M2 18:52Z, 2026-09-25)

    M1  Nestor/NPE   RUNNING  C-SWAP-ACQUIRE (CONFIRM, frozen 82b6caeb3) + X-ACQUIRE (EXPLORE)
        Ananke/PTE   HELD     PTE-C1 done; operator HOLD ALL ACTIVITY (12:20Z)
        Cosmos       BLOCKED  on holdout D from Nestor (#561 unclaimed; steward request #584)
        Atlas        PARKED   one pass ran (d5141caa9); REPORTS ONLY
    M2  Archaeon     RUNNING  ENVGATE-02, relaunched unchanged 18:30:33Z, 6 workers
        Bellerophon  RUNNING  Z80xAtlas coupling campaign, 20 workers, runtime caps 18/22 h
        Ensorain     DESIGN   WTP-LM01 (lossless memorizer); no runs; dev envelope ruled
        Aether/AGE   IDLE
        SFE, Vivarium DOWN    watchdogs disabled
    Hosts: M1 CPU ~33%, GPU idle. M2 28 logical CPUs, 17.7/34.1 GB, GPU idle.

## 2. Frozen, must finish (s6)

M1: C-SWAP-ACQUIRE and X-ACQUIRE. M2: ENVGATE-02 to its gate, then Archaeon's own
sequence; the coupling campaign to its cap. None is amended for this program.
For the operator, one line: s6's M1 premise was stale when issued (X-DONOR-SWAP had
finished at 12:45Z, WEAK_SIGNAL); its M2 premise held, since ENVGATE-02 had never
been relaunched after 09-24.

## 3. Theory-aware lanes

EXPOSED: Ensorain and Crius (since 09-24), Nestor (since ~16:50Z today, via Aporia's
#584; recorded against Aporia). Each is DIRECT under s5, so exposure costs nothing
there. The whole fleet is exposable through root README.md:60, public since
2026-09-23T12:15Z.

## 4. Theory-blind lanes

One: the Bellerophon coupling campaign, BLIND ON CONTENT. Its prereg c9bed96de was
frozen 32 h after exposure became possible, with 0 STRONG and 0 WEAK probe hits.
The protection rule is in BLIND_LANES.md (19:10Z): no program text to the Bellerophon
seat, NO BROADCASTS, and the Z80 adapter waits for the campaign's end. Every other
seat is UNVERIFIED_BLIND until the frozen registry probe runs. RISK FOR THE OPERATOR:
s5 asks for at least one "substantial" blind lane. We have one, it is time-limited,
and the fleet has no second.

## 5. First three direct attacks

1. WTP-LM01 (Ensorain, M2): countermodel B. It already carries the joint steward
   rulings R1a-e and R2 (#591, #592, #594). Its prereg is reviewed first. Launch is
   gated on a Cyclops launch prompt.
2. ONE reversible-core experiment covering A and C together (Cyclops R1.3; Aporia
   concurs). A bounded reversible agent, with an export channel outside the boundary
   and priced, learns an export policy. It is compared against relevance-blind export
   at a MATCHED MERGE-TIME CURVE. Built by Nestor/NPE. It is a new substrate,
   admissible under s7 because no reversible agent substrate exists on either host
   (M1 audit, M2 E).
   [PENDING-CYCLOPS] The relevance-blind control must be RANDOM export. FIFO/recency
   export is blind only where task relevance is uncorrelated with recency. In HOLD
   (and in Ananke's delay line), the relevant cue is a recent one. So FIFO runs as a
   third arm, on tasks built so that relevance and recency are decorrelated, with
   that decorrelation measured before the reading.
3. DSA (distinction-survival assay) on FROZEN specimens: Ananke PTE M1-M3 (M1), AGE
   (the first M2 adapter), and the coupling campaign's Z80 specimens after its end
   (the first reading of blind-lane artifacts). It carries Cyclops's four closures:
   exact merge only for discrete state, decoder recoverability + positive control
   for continuous state; counter-based RNG keyed (t, site, purpose) + a cheat fixture;
   pairs sampled from the generator's distinction space, stratified, with eligible
   counts computed first; controls matched on the whole merge-time curve. Aporia
   specifies and calibrates it; host seats build the adapters.

## 6. Strongest reversible countermodel

Attack 2 above. Its success criterion is the SELECTIVITY of export, not its absence
(section 11).

## 7. Strongest lossless-memorizer countermodel

WTP-LM01's L-R: an exact store plus a lazy full-store refit per query, fit discarded,
refit charged. A win is labelled LOSSLESS_TRANSIENT_CONTRACTION against the
persistent-state claim. Secondary, M1, small: Aporia's A3 attempt two with a correctly
priced retrieval-only memo control (APO-32).

## 8. Indiscriminate-loss control

WTP-LM01: random coarse partition or hash-merge, matched on R(t) per horizon; bytes
matched too. PTE: random packet drop and decay are native dials. DSA and the
reversible core: relevance-blind merge or export matched on the merge-time curve.
Distinguishability is always REPORTED, never matched.

## 9. Instrumentation gaps

No cross-engine replay-and-perturb interface. No state-snapshot hash that covers RNG
and in-flight state (PTE, Z80xAtlas, AGE). No byte/read/write/op meter in WTP (LM01's
largest new code). Atlas carries none of the s10 vocabulary and is PARKED. SFE and
Vivarium are down (not needed yet). No frozen relevance source for no-task lanes
(heredity, reproduction). The host-probe monitors are dead on both machines.

## 10. Resource conflicts

M2-1 (ENVGATE-02 + coupling campaign) was resolved by Cyclops as a co-run, with the
overlap accounted from 18:30:33Z. Aporia's concern stands on record: runtime caps
mean co-running reduces the campaign's N. Its size is disclosed by the overlap
accounting. M2-2: Ensorain's dev envelope (#592). M1: no CPU conflict. Nestor's
ATTENTION is contended between frozen work and Cosmos holdout D.

## 11. What could make the hypothesis unfalsifiable (joint)

a. THE ELIMINATION HALF IS A THEOREM (M1 G1, sharpened by Cyclops R1.2). s1 concerns
   ACCESSIBLE causal state, and exporting is elimination from it. So any bounded
   system with fresh input eliminates distinctions. Only SELECTIVITY and REQUIREMENT
   are empirical. No result about elimination as such is evidence.
   [PENDING-CYCLOPS] This holds when the input's entropy rate is positive. In a
   low-entropy (periodic, recurrent) environment a bounded reversible agent need not
   export, so the directive's "changing environments" must be operationalised as a
   measured positive entropy rate per experiment.
b. CIRCULAR RELEVANCE (G2 + R2). Relevance comes from the GENERATOR or a held-out
   FUTURE INTERVENTION, frozen before specimens are inspected. Never from what the
   system depends on, and never from a fitted surrogate that shares a selective arm's
   inductive bias.
c. TRIVIAL CONTRACTION (G3). Every readout carries the matched indiscriminate control.
d. NO HORIZON (G4). Every experiment declares its horizon before it runs.
e. MOVABLE BOUNDARY (G5 + R1.5). Proposal: freeze the boundary at the agent's
   accessible state, with export channels OUTSIDE and priced (s9). This goes in
   HYPOTHESIS.md and to Harmonia (s12) before any reversible result.
f. [PENDING-CYCLOPS] "A reduces to C": the reversible core tests C on a reversible
   substrate. C still needs irreversible substrates (WTP random-merge, PTE drop) to
   cover s4C as written.

## 12. Recommendations to change the s8 allocation

None to engine roles. Additions: (i) the DSA as a shared OBSERVATION instrument
(s7 CONTINUE: instrumentation for falsification); (ii) Nestor/NPE builds the
reversible core (s8 already names "reversible substrates" for Nestor).

## 13. Asked of the operator (scientific decisions only)

Q1. CONFIRM THE READING (not "decide", per Cyclops R1.4): the law's empirical content
    is selectivity + requirement; the reversible arm is judged on the selectivity of
    what it exports; the boundary is frozen as in 11e.
Q2. Atlas: the 09-25 PARKED/REPORTS ONLY ruling vs s11 "portfolio memory". Which
    governs, and from when?
Q3. Ananke: does the directive lift today's HOLD ALL ACTIVITY for C1b, or does C1b
    wait for the Kairos/Elenchus reviews?
Q4. Blind lanes: the fleet has one, time-limited. Designate a second (a seat to be
    kept from the program until a date), or accept one?
