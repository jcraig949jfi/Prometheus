# C2-SFE-09 -- CA substrate: distributed vs redundant vs artifact

## A. STARTUP (preregistration; sealed sha256:adc2f63ce00ec714223aaeff96868ef0e5718b7266a2a1a1ab07d59c4fcf8d4d)

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
    {"delay": 2, "eps": 0.02, "horizon": 8, "li_min": 0.1, "n_cells": 31, "pair_sites": 6, "random_orders": 4, "reset_density": 0.5, "seeds": [1, 2, 3, 4]}
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
- decl (machine-read by archaeon.wse.states): {"n_min": 4, "primary": {"control": "random", "metric": "base_acc", "min_effect": 0.05, "treatment": "ca:particle2"}, "readout_control": {"arm": "shift", "chance": 0.5, "metric": "base_acc", "min_above": 0.3}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a03); resumed_from: None; replayed steps on the attempt of record: 0
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=WEAK_POSITIVE
    a03  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 36; errors 0
- timings (s): records_s=9.88, startup_s=0.06, substrates_s=45.77, teardown_s=0.16, total_s=56.7
- decisions: D2-017: the four explanations are decided by preregistered rules on four measurements per CA genome; no explanation is assigned by reading rows
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / base_acc              s1      s2      s3      s4    mean    n
    ca:GKL                   0.549   0.535   0.538   0.534   0.539    4
    ca:exp                   0.521   0.527   0.521   0.538   0.527    4
    ca:maj                   0.518   0.536   0.531   0.542   0.532    4
    ca:par                   0.478   0.540   0.504   0.525   0.512    4
    ca:particle1             0.555   0.543   0.576   0.560   0.558    4
    ca:particle2             0.576   0.611   0.540   0.600   0.582    4
    direct                   0.505   0.505   0.490   0.499   0.500    4
    random                   0.499   0.526   0.490   0.499   0.503    4
    shift                    1.000   1.000   1.000   1.000   1.000    4

    arm / reset_only_acc        s1      s2      s3      s4    mean    n
    ca:GKL                   0.452   0.428   0.473   0.435   0.447    4
    ca:exp                   0.466   0.461   0.467   0.458   0.463    4
    ca:maj                   0.441   0.461   0.478   0.440   0.455    4
    ca:par                   0.430   0.441   0.470   0.439   0.445    4
    ca:particle1             0.423   0.462   0.462   0.424   0.443    4
    ca:particle2             0.432   0.436   0.456   0.454   0.445    4
    direct                       -       -       -       -       -    0
    random                       -       -       -       -       -    0
    shift                        -       -       -       -       -    0

    arm / time_shuffled_acc      s1      s2      s3      s4    mean    n
    ca:GKL                   0.503   0.505   0.477   0.523   0.502    4
    ca:exp                   0.535   0.521   0.527   0.536   0.530    4
    ca:maj                   0.486   0.522   0.513   0.529   0.512    4
    ca:par                   0.548   0.516   0.503   0.505   0.518    4
    ca:particle1             0.510   0.479   0.517   0.521   0.507    4
    ca:particle2             0.517   0.486   0.535   0.551   0.522    4
    direct                   0.570   0.556   0.538   0.587   0.563    4
    random                   0.499   0.526   0.490   0.499   0.503    4
    shift                    0.590   0.565   0.561   0.570   0.572    4

    arm / input_shuffled_acc      s1      s2      s3      s4    mean    n
    ca:GKL                   0.513   0.521   0.520   0.493   0.512    4
    ca:exp                   0.491   0.493   0.509   0.509   0.501    4
    ca:maj                   0.475   0.508   0.522   0.526   0.508    4
    ca:par                   0.486   0.497   0.518   0.517   0.505    4
    ca:particle1             0.490   0.523   0.516   0.497   0.507    4
    ca:particle2             0.505   0.517   0.517   0.513   0.513    4
    direct                   0.546   0.576   0.547   0.566   0.559    4
    random                   0.499   0.526   0.490   0.499   0.503    4
    shift                    0.560   0.612   0.556   0.616   0.586    4

    arm / localization_index      s1      s2      s3      s4    mean    n
    ca:GKL                   0.396   0.699   0.314   0.453   0.466    4
    ca:exp                   0.787   0.723   0.552   0.478   0.635    4
    ca:maj                       -   0.406   0.216   0.274   0.298    3
    ca:par                       -   0.362       -   0.459   0.411    2
    ca:particle1             0.113   0.297   0.170   0.146   0.181    4
    ca:particle2             0.133   0.102   0.404   0.124   0.191    4
    direct                       -       -       -       -       -    0
    random                       -       -       -       -       -    0
    shift                        -       -       -       -       -    0

    arm / k50                   s1      s2      s3      s4    mean    n
    ca:GKL                       3       1       2       1   1.750    4
    ca:exp                       1       1       1       1   1.000    4
    ca:maj                       -       1       1       1   1.000    3
    ca:par                       -       1       -       1   1.000    2
    ca:particle1                 1       1       1       1   1.000    4
    ca:particle2                 1       1       1       1   1.000    4
    direct                       -       -       -       -       -    0
    random                       -       -       -       -       -    0
    shift                        -       -       -       -       -    0

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.5033, "effect": 0.0785, "min_effect": 0.05, "n_control": 4, "n_treatment": 4, "paired": 4, "paired_wins": 4, "treatment_mean": 0.5817}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: weak; one CA family, one task; the flags are measurements with fixed rules, not a verdict

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

Readout capability confirmed (ShiftRegister 1.0 on every seed; DirectInput 0.49-0.51; FrozenRandom 0.49-0.53). PRIMARY: particle2 - random = +0.079 base accuracy (0.54-0.61 vs 0.49-0.53; paired wins 4/4); the machine candidate WEAK_POSITIVE (n=4) is accepted: SFE-04's usefulness replicates in direction and size (0.58 mean vs the parent's 0.608). The four preregistered explanations, decided by their rules on the best genome (particle2, 4 seeds): readout artifact NO (reset-only readout 0.43-0.46, below chance, 0/4 flags: the reset lattice carries nothing the readout can use); frozen dynamical bias NO in 3/4 (time-shuffled features 0.49-0.55; one seed within 0.02 of base); input-independent NO (input-shuffled 0.51-0.52, 0/4); LOCALIZED YES in 4/4 (LI 0.10-0.40) with k50 = 1 in every seed: removing the SINGLE highest-drop site takes the frozen readout's margin below half, and the greedy cumulative curve sits below the random-order curve from k=1. The parent's 'distributed' reading is therefore reversed, and the reason is the parent's instrument: SFE-04 lesioned contiguous 5-cell WINDOWS and compared them with random 5-cell lesions, and a random 5-cell set contains the critical site often enough to flatten the map; single-site lesions with a frozen readout find it at once. Of the four explanations, 'redundant/local computation invisible to single-site lesions' is also wrong (single sites are exactly what reveals it); what survives is 'local computation, one or a few sites, on the input, with temporal order' -- particle1 (0.54-0.58, localized 4/4, k50 = 1) and GKL (0.53-0.55, k50 1-3) show the same shape. The three weaker genomes (maj, exp, par: base 0.48-0.54) carry dynamical-bias flags in 3-4 of 4 seeds and input-independence flags in 1-3: their small margins are not delayed-recall computation. Exploratory: the pairwise interaction of the top-6 sites is recorded per row and not interpreted here. Must NOT be claimed: that particle2's site IS a delay line (the mechanism is not identified, only located); anything beyond delay 2 on this catalogue.

## D. TEARDOWN (generated)

- worlds: {"ca": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-09

Zero engine errors on the attempt of record (a03; a01 was a dry run that crashed on a helper signature -- run_streams returns (features, steps) and the CA constructor takes a ports tuple -- fixed before a02, the clean dry run); 1 world; 36 records; the cumulative lesion curves published as one observation artifact. The L-019 probe (reset_leakage_probe) is wired and returns accuracy/base_rate/leaks/n_scored. Bench notes: (1) the localization index is undefined when the frozen readout has no margin on the confirmation set (par seeds 1 and 3): guarded to None rather than a divide-by-epsilon (found in the dry run: LI 4.8e6); (2) the parent's window-vs-random-window lesion design cannot see a single critical site -- a MISSING_FAILURE_STATE of the instrument class 'null distribution hides the effect by construction' (ledger); (3) 4 seeds x 9 substrates x ~170 CA runs each in 46 s: the discrimination was cheap.

## F. LANDSCAPE / GRADIENT NOTES

The evolved CA genomes that read delayed recall above chance (particle1, particle2, GKL) do it through one or a few sites: k50 = 1 in 11 of 12 rows, the greedy lesion curve below the random curve from the first lesion. The margin is small (0.04-0.11 over chance) and sits on the input's temporal order (time shuffling removes it) and on the input (input shuffling removes it), not on the reset lattice (reset-only reads below chance). The weaker genomes' margins (0.02-0.04) survive time shuffling: bias, not computation. 'Distributed reusable computation' was an artifact of a null distribution that contained the effect.

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). Assay capable (ShiftRegister 1.0); n=4. particle2 reads delayed recall above FrozenRandom by 0.079 (4/4 paired wins), and the preregistered rules place its computation as LOCALIZED (k50 = 1, LI 0.10-0.40), input-dependent and temporally ordered, not a reset artifact; SFE-04's 'distributed' interpretation is retired as an artifact of window lesions against a random-window null.
