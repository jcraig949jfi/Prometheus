# C4-02 -- mutation-radius response curve

## A. STARTUP (preregistration; sealed sha256:ef21a58a09a25246ad8abbc74f323eacad244b2b9d9fecaa5877c200713b1aab)

- experiment ID: C4-02
- parents: C4-01
- QUESTION: Does genotypic distance have any usable relationship to behavioral distance? For radii 1, 2, 4, 8, 16 successive frozen-weight grammar edits from each of the 57 starting program variants: D(delta) = displacement conditional on executing, and P(D2 or D3 | delta).
- PARENT EVIDENCE: C4-01 (54ce467f2): at radius 1, D7 = 0 in 5,472 edits; displacement bimodal (0 or > 0.75); loss by operator .15-.76; gen0_random parents degenerate themselves.
- WHY THIS SLOT IS STILL WORTH SPENDING: Whether a region exists between 'nothing changes' and 'everything dies' decides what C4-05 (neutral walks) and C4-06 (recombination) can even attempt; it replaces further blind attacks on the old hard summit (directive section 4).
- ASSAY CAPABILITY REQUIREMENT: radius 0 identity 57/57 (displacement 0, parent's rewards); radius-1 D-distribution within TVD 0.10 of C4-01's frozen-weight mixture of per-operator distributions
- POSITIVE CONTROL: r0 arm: identity_ok >= 1.0 on 57/57 parents; consistency: TVD(r1, C4-01 mixture) <= 0.10
- REACHABILITY ESTIMATE:
    {"note": "evaluation census; no reachability lookup applies"}
- ARMS:
    - r0
    - r1
    - r2
    - r4
    - r8
    - r16
- COMMON-RANDOM-NUMBERS POLICY: the SAME episode sets as C4-01 (family train, index 1, E=16); children seeded from (campaign_seed, organism_id, radius, draw); operators drawn by frozen weights (name=None)
- BUDGET:
    {"E": 16, "band": 0.0625, "draws": 8, "environments": ["W0", "W0_heldout", "W1_d1", "W1_d4", "W2_K2"], "floor": 0.1875, "parents": 57, "radii": [0, 1, 2, 4, 8, 16]}
- PRIMARY OBSERVABLE: per radius and per (radius, stratum): mean displacement, displacement histogram, P(D2 or D3), P(D5), P(D6 or D7) with Wilson bands; the same by first operator at radius 1; the six named shapes as measured predicates; traversable-region cells per stratum
- CLAIM CEILING: a measured curve at 8 draws per (parent, radius) on one frozen substrate; no mechanism
- FALSIFICATION CONDITION: NEGATIVE if flat-neutral (P(D5) >= 0.8 at every radius) or complete catastrophe (P(D2 or D3) >= 0.95 at radius 1) holds for every stratum (no traversable region anywhere); SUPPORTED if a traversable region exists in >= 1 stratum
- KILL CONDITION: a control fails -> INSTRUMENT_INVALID (if the consistency control fails, C4-02 and C4-01 disagree about the same substrate; investigated before C4-03)
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - curves by radius / stratum / first operator
    - op_records per child
    - noop steps per child
    - descriptors before/after
- MACHINE CHANGES EXERCISED:
    - C4-01 classifier reused unchanged
    - radius composition of frozen-weight edits
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 2)
- decl (machine-read by archaeon.wse.states): {"n_min": 57, "positive_control": {"arm": "r0", "metric": "identity_ok", "min": 1.0, "min_rows": 57}, "primary": {"control": "r1", "metric": "loss_rate", "min_effect": 0.05, "treatment": "r8"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 342; errors 0
- timings (s): census_s=16.79, startup_s=0.02, teardown_s=0.02, total_s=31.7
- decisions: D4-006: radius = number of mutate() applications including steps whose operator noops (noop_steps recorded per child); prediction written to be lost: loss_rate(r8) - loss_rate(r1) >= 0.05
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / loss_rate          sNone    mean    n
    r0                       0.000   0.000    1
    r1                       0.250   0.250    1
    r16                      1.000   1.000    1
    r2                       0.625   0.625    1
    r4                       1.000   1.000    1
    r8                       1.000   1.000    1

    arm / neutral_rate       sNone    mean    n
    r0                       1.000   1.000    1
    r1                       0.750   0.750    1
    r16                      0.000   0.000    1
    r2                       0.375   0.375    1
    r4                       0.000   0.000    1
    r8                       0.000   0.000    1

    arm / displacement_mean   sNone    mean    n
    r0                       0.000   0.000    1
    r1                       0.242   0.242    1
    r16                      0.969   0.969    1
    r2                       0.594   0.594    1
    r4                       0.941   0.941    1
    r8                       0.961   0.961    1

    arm / exaptive_rate      sNone    mean    n
    r0                       0.000   0.000    1
    r1                       0.000   0.000    1
    r16                      0.000   0.000    1
    r2                       0.000   0.000    1
    r4                       0.000   0.000    1
    r8                       0.000   0.000    1

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.5219, "effect": 0.4079, "min_effect": 0.05, "n_control": 57, "n_treatment": 57, "paired": 1, "paired_wins": 1, "treatment_mean": 0.9298}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: a measured curve at 8 draws per (parent, radius) on one frozen substrate; no mechanism

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"radius": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-02

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
