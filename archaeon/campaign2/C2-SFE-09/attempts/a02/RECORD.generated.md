# C2-SFE-09 -- CA substrate: distributed vs redundant vs artifact

## A. STARTUP (preregistration; sealed sha256:4f8854d3d7636d44b76a88b01d00249a66dac09403deb8e9c2a57790089b4d97)

- experiment ID: C2-SFE-09
- parents: SFE-04
- QUESTION: Which explanation of SFE-04's delayed-recall readout (0.608 vs 0.5 chance, flat single-window lesion map) survives: genuinely distributed computation, redundant/local computation invisible to single lesions, a readout artifact of the reset lattice, or a frozen dynamical bias?
- PARENT EVIDENCE: SFE-04: particle2 0.608 on delayed recall d=2; lesion map flat within the matched-random band; frozen whole-substrate reuse positive; reset_leakage_probe unwired (L-019).
- ASSAY CAPABILITY REQUIREMENT: the ShiftRegister (perfect memory) reads >= 0.8 under the ridge readout (READOUT_CANNOT_EXPRESS otherwise); the best CA must exceed FrozenRandom by the preregistered margin for the explanations to be about anything
- POSITIVE CONTROL: ShiftRegister base accuracy (readout capability); DirectInput and FrozenRandom as floors
- REACHABILITY ESTIMATE:
    {"note": "not a WSE cell; the CA genomes are the six recovered Herakles genomes; the reachability table does not apply"}
- ARMS:
    - ca:maj
    - ca:exp
    - ca:par
    - ca:particle1
    - ca:particle2
    - ca:GKL
    - shift
    - direct
    - random
- COMMON-RANDOM-NUMBERS POLICY: per seed: one train/confirmation partition and one reset root shared by every substrate; shuffles drawn from one generator per row
- BUDGET:
    {"delay": 2, "eps": 0.02, "horizon": 8, "li_min": 0.1, "n_cells": 31, "pair_sites": 6, "random_orders": 4, "reset_density": 0.5, "seeds": [1]}
- PRIMARY OBSERVABLE: base_acc per substrate x seed (particle2 vs random, the parent's pair); the four preregistered flags per CA row
- CLAIM CEILING: weak; one CA family, one task; the flags are measurements with fixed rules, not a verdict
- FALSIFICATION CONDITION: particle2 - random < 0.05 base accuracy => the parent's usefulness does not replicate; flag rules: reset_only >= base - 0.02 => readout artifact; time_shuffled >= base - 0.02 => dynamical bias; input_shuffled >= base - 0.02 => input-independent; LI >= 0.10 => localized (else distributed)
- TYPED FAILURE CONDITIONS:
    - READOUT_CANNOT_EXPRESS (shift < 0.8)
    - UNDERPOWERED
    - INSTRUMENT_FAILURE (probe signature)
- EXPECTED MACHINE TELEMETRY:
    - reset-only accuracy (the L-019 probe, wired)
    - time-shuffled and input-shuffled accuracies
    - greedy and random cumulative lesion curves
    - localization index and k50
    - pairwise interaction of the top-6 sites
- MACHINE CHANGES EXERCISED:
    - H (the missing telemetry L-019)
    - B (readout_control state)
    - I
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "primary": {"control": "random", "metric": "base_acc", "min_effect": 0.05, "treatment": "ca:particle2"}, "readout_control": {"arm": "shift", "chance": 0.5, "metric": "base_acc", "min_above": 0.3}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: 1; replayed steps on the attempt of record: 0
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=WEAK_POSITIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): records_s=0.0, substrates_s=11.81, total_s=12.0
- decisions: D2-017: the four explanations are decided by preregistered rules on four measurements per CA genome; no explanation is assigned by reading rows
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / base_acc              s1    mean    n
    ca:GKL                   0.549   0.549    1
    ca:exp                   0.521   0.521    1
    ca:maj                   0.518   0.518    1
    ca:par                   0.478   0.478    1
    ca:particle1             0.555   0.555    1
    ca:particle2             0.576   0.576    1
    direct                   0.505   0.505    1
    random                   0.499   0.499    1
    shift                    1.000   1.000    1

    arm / reset_only_acc        s1    mean    n
    ca:GKL                   0.452   0.452    1
    ca:exp                   0.466   0.466    1
    ca:maj                   0.441   0.441    1
    ca:par                   0.430   0.430    1
    ca:particle1             0.423   0.423    1
    ca:particle2             0.432   0.432    1
    direct                       -       -    0
    random                       -       -    0
    shift                        -       -    0

    arm / time_shuffled_acc      s1    mean    n
    ca:GKL                   0.503   0.503    1
    ca:exp                   0.535   0.535    1
    ca:maj                   0.486   0.486    1
    ca:par                   0.548   0.548    1
    ca:particle1             0.510   0.510    1
    ca:particle2             0.517   0.517    1
    direct                   0.570   0.570    1
    random                   0.499   0.499    1
    shift                    0.590   0.590    1

    arm / input_shuffled_acc      s1    mean    n
    ca:GKL                   0.513   0.513    1
    ca:exp                   0.491   0.491    1
    ca:maj                   0.475   0.475    1
    ca:par                   0.486   0.486    1
    ca:particle1             0.490   0.490    1
    ca:particle2             0.505   0.505    1
    direct                   0.546   0.546    1
    random                   0.499   0.499    1
    shift                    0.560   0.560    1

    arm / localization_index      s1    mean    n
    ca:GKL                   0.396   0.396    1
    ca:exp                   0.787   0.787    1
    ca:maj                   0.715   0.715    1
    ca:par                 4851310.484  4851310.484    1
    ca:particle1             0.113   0.113    1
    ca:particle2             0.133   0.133    1
    direct                       -       -    0
    random                       -       -    0
    shift                        -       -    0

    arm / k50                   s1    mean    n
    ca:GKL                       3   3.000    1
    ca:exp                       1   1.000    1
    ca:maj                       1   1.000    1
    ca:par                       1   1.000    1
    ca:particle1                 1   1.000    1
    ca:particle2                 1   1.000    1
    direct                       -       -    0
    random                       -       -    0
    shift                        -       -    0

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.4987, "effect": 0.0768, "min_effect": 0.05, "n_control": 1, "n_treatment": 1, "paired": 1, "paired_wins": 1, "treatment_mean": 0.5755}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: weak; one CA family, one task; the flags are measurements with fixed rules, not a verdict

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-09

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
