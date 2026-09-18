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
