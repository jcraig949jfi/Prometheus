# C4-05 -- neutral-network walk

## A. STARTUP (preregistration; sealed sha256:8d255afa872bf4664c6459c2990c88744053c438acee3b140b449b59aaa411d9)

- experiment ID: C4-05
- parents: C4-01, C4-02, C4-04
- QUESTION: Can lineages move through genotype space while preserving current competence (band 1/16 around the ORIGINAL parent's reward on its environment), and does such movement expose new reachable behaviours on held-out environments?
- PARENT EVIDENCE: C4-01: D5 mass .22-.67 per operator at radius 1; C4-02: neutral share .467 at r1 decaying to .004 at r16 under unconstrained edits; C4-04: insertion/movement steps that break a jump lose ~.2 more.
- WHY THIS SLOT IS STILL WORTH SPENDING: Replaces repeated measurement of the flat shelf with a direct test of whether the band has traversable internal structure.
- ASSAY CAPABILITY REQUIREMENT: identity-proposal walker reaches depth 16 in 16 proposals; randomize-all walker stalls at depth 0; determinism; cheat
- POSITIVE CONTROL: controls arm: positive_ok >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "bounded acceptance walk; no search for the challenge"}
- ARMS:
    - viable
    - degenerate_gen0
    - controls
- COMMON-RANDOM-NUMBERS POLICY: same episode sets as C4-01/02; walkers seeded (campaign_seed, organism_id, walk, w); one rng per walker for all proposals
- BUDGET:
    {"E": 16, "archive_depths": [0, 2, 4, 8, 16], "band": 0.0625, "depth": 16, "floor": 0.1875, "max_proposals_per_step": 32, "parents": 57, "walkers": 4}
- PRIMARY OBSERVABLE: connected neutral depth (median over viable parents; histogram), acceptance rate by depth bin, structural and behavioural diversity by archived depth, held-out exaptation rate by depth with Wilson bands, reference-break share of accepted steps; the four named shapes
- CLAIM CEILING: a measured walk at 4 walkers x 16 steps per parent on one substrate; no mechanism; no selection claim
- FALSIFICATION CONDITION: NEGATIVE if neutral swamp, disconnected or silent walk holds in every viable stratum
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
- EXPECTED MACHINE TELEMETRY:
    - steps with operator/args/proposals/ref_broken/descriptor
    - archived walkers' held-out rewards
    - diversity by depth
- MACHINE CHANGES EXERCISED:
    - acceptance walk
    - C4-04 reference facts per step
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 5)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1}, "primary": {"control": "degenerate_gen0", "metric": "exaptation_16", "min_effect": 0.05, "treatment": "viable"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 57; errors 0
- timings (s): startup_s=0.02, teardown_s=0.03, total_s=16.6, walk_s=13.99
- decisions: D4-009: the band is relative to the ORIGINAL parent (not the current walker) so a walk cannot ratchet; a noop-returning proposal is not a proposal; stall = 32 rejected proposals at one depth; degenerate gen0 parents walked but reported apart
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / connected_depth    sNone    mean    n
    controls                     -       -    0
    degenerate_gen0             16  16.000    1
    viable                      16  16.000    1

    arm / exaptation_16      sNone    mean    n
    controls                     -       -    0
    degenerate_gen0          0.000   0.000    1
    viable                   0.000   0.000    1

    arm / ref_break_share    sNone    mean    n
    controls                     -       -    0
    degenerate_gen0          0.078   0.078    1
    viable                   0.172   0.172    1

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0, "effect": 0.0426, "min_effect": 0.05, "n_control": 10, "n_treatment": 47, "paired": 1, "paired_wins": 0, "treatment_mean": 0.0426}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: a measured walk at 4 walkers x 16 steps per parent on one substrate; no mechanism; no selection claim

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"walk": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-05

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
