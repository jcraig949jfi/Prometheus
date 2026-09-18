## A. STARTUP (preregistration; sealed sha256:8e96396d1d8613bebd2d354abd054d172a6502c34fccc7a5a8195f4a446fa6b1)

- experiment ID: C5-01
- parents: C4-05
- QUESTION: Does held-out exaptation continue increasing materially beyond neutral depth 16, or has the network entered a yield plateau? Marginal discovery yield per accepted step and per evaluation, not monotonicity.
- PARENT EVIDENCE: C4-05: depths 2/4/8/16 = .016/.032/.037/.043 (single edit .006); 188/188 walkers reached 16; acceptance ~.55.
- WHY THIS SLOT IS STILL WORTH SPENDING: Phase A of the substrate-decision campaign: the first of the two live C4 signals, closed cheaply.
- ASSAY CAPABILITY REQUIREMENT: walkers 1-4 reproduce C4-05's depth-16 steps digest for digest; identity walker depth 64 in 64; randomize-all stalls; determinism; cheat
- POSITIVE CONTROL: controls arm: positive_ok >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "acceptance walk; no search"}
- ARMS:
    - viable
    - degenerate_gen0
    - controls
- COMMON-RANDOM-NUMBERS POLICY: C4-05's episode sets and walker seeds (campaign_seed 20260921 for the walks, so walkers 1-4 ARE C4-05's); walkers 5-6 new draws from the same rule
- BUDGET:
    {"E": 16, "archive_depths": [0, 16, 32, 48, 64], "depth": 64, "max_proposals": 32, "parents": 57, "walkers": 6}
- PRIMARY OBSERVABLE: exaptation rate by depth with Wilson bands; yield per evaluation by depth; marginal rate per accepted step between archives; acceptance by bin; the three branches; PRESERVE rule (continued gradient AND Y_64 >= 2 x .0012)
- CLAIM CEILING: a rate curve at 6 walkers x 64 steps per competent parent on one substrate; no mechanism
- FALSIFICATION CONDITION: PLATEAU or DEGRADATION or MIXED -> the neutral mechanism is not preserved for Phase A's disposition
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
- EXPECTED MACHINE TELEMETRY:
    - steps with proposals per walker
    - archived exposures at 5 depths
    - yield table
- MACHINE CHANGES EXERCISED:
    - C4-05 walk reused with a deeper archive set
    - yield-per-evaluation accounting
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase A, slot 1)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1}, "primary": {"control": "degenerate_gen0", "metric": "exaptation_64", "min_effect": 0.02, "treatment": "viable"}}
