# V0.5 Equilibrium and Confirmation Crucible — PREREGISTRATION. Frozen before any measurement.

Brief: `roles/Proteus/PROMPT_PROTEUS_V0_5_EQUILIBRIUM_CONFIRMATION_2026-09-03.txt`
sha256 `59314e9da89a1a3c9233de513390ea69bbbc05337e28a7db9c9caded34c1afcd`.

## 0. Zero grammar changes

The active grammar is `proteus.grammar.v0.4`, hash
`5043f5e11a726b63a9553cc4855995c3ac324e55f8154ffe4adf28dad553a832`. Asserted at import by unit
test and re-asserted by every runner. No operator, weight, VM rule, manifest bound, initialization
rule, probe or configuration rule is touched in this pass. There is no authorized repair.

## 1. Global multiplicity architecture

    hypothesis cell = (coordinate, cohort)
    family          = every cell in the qualification claim (70 coordinates x 5 cohorts = 350)
    procedure       = ONE step-down Holm over the whole family, alpha = 0.05

This replaces V0.4's within-cohort correction, which was mismatched to a decision rule that
searched across both coordinates and cohorts. The within-cohort procedure is still computed and
reported so the packet can show what it would have concluded, but it decides nothing.

Two independent implementations (step-down on z against normal quantiles; step-down on
erfc-derived p-values) must agree exactly or adjudication aborts. Frozen fixtures cover zero, one,
several and cross-cohort discoveries, plus a case where within-cohort correction passes a cell
that global correction rejects.

## 2. Confirmatory test of the V0.4 discovery — every parameter fixed here

    coordinate              class_halt_yield
    cohort                  128
    primary null            NC4 (length- and configuration-matched geometry reference)
    claimed direction       NEGATIVE (V0.4 delta = -0.0191)
    horizon                 400 generations, checkpoints 0/25/50/100/200/400
    lineages                100 per cohort
    persistence criterion   sign of the delta over generations 200..400 equals the sign of the
                            delta over 0..400
    confirmation test       ONE-SIDED in the claimed direction, on the delta against the primary
                            null, using a lineage-cluster bootstrap (2,000 resamples, seeded)
    confirmation alpha      0.05, one-sided, uncorrected (there is exactly one confirmatory
                            hypothesis, so there is no multiplicity to correct)
    replication criterion   CONFIRMED iff sign matches AND one-sided p <= 0.05 AND the persistence
                            criterion holds
    magnitude               NOT required to equal V0.4's

One dataset. No early stop if it confirms. No additional seeds if it fails. Effect size and
interval are reported either way.

## 3. Fresh seed, derived from a public value

The V0.5 replication seed is derived from the sha256 of the V0.5 brief,
`59314e9d…`, a value James created before any V0.5 measurement existed and which Proteus could not
have chosen for its outcome. Derivation: `int(brief_sha256[:16], 16)`.

## 4. Primary and sensitivity nulls, assigned before execution

    coordinate family                    PRIMARY        SENSITIVITY
    genome_length, config_log2_tape_words  NC5          NC1B
    other configuration                    NC1B         NC5
    content (opcode, class, operand, NOP)  NC4          NC3
    phenotype (status, executed, silence,
      occupancies, mutation-touch)         NC4          NC3

The primary null alone determines qualification. Sensitivity nulls are reported beside it. A
disagreement between primary and sensitivity is epistemically important, must be discussed, and
does NOT automatically become a pass or a fail. This forbids null shopping in either direction,
including the retrospective "both nulls must agree" rule that V0.4's result might have invited.

## 5. Structural Markov kernel

    state                (genome_length, tape_words); only tape_words gates structural validity
    PRIMARY space        tapes {16,32,64,128,256}, L in [1, T/4]  -> 124 states, enumerated
    SENSITIVITY space    tapes {16..4096}, L in [1, min(1024, T/4)] -> 2,044 states
    kernel               MEASURED from the live operator, marginalising over uniform genome
                         content; self-loops from rejected proposals included
    samples              50,000 per state (primary), 300 per state (sensitivity)
    truncation           a transition leaving the analysed space is folded into the self-loop
                         (rejection semantics), applied identically to the active kernel and to
                         the reversible reference; escaped mass reported per state

**Live-code agreement, with the tolerance frozen here.** A second independent sample under a
different seed is compared per state by total-variation distance. Adjudication ABORTS if the
median TV exceeds 0.02 or the maximum TV exceeds 0.05. The V0.4 ANALYTIC kernel is also compared;
a discrepancy there is a finding about the V0.4 model, not an abort, because the V0.5 analysis
uses the measured kernel.

## 6. Equilibrium quantities

Stationary distribution by power iteration to an L1 change below 1e-14 or 200,000 iterations,
with communicating classes by Tarjan and closed classes identified. Probability current
`J(i,j) = pi_i P_ij - pi_j P_ji` for every connected unordered pair. Cycle currents on short
cycles. Stationary entropy production `sum pi_i P_ij log(pi_i P_ij / pi_j P_ji)`, with one-way
edges (zero reverse probability) reported explicitly and never smoothed.

**Reversible reference.** `Q(i,j) = (pi_i P_ij + pi_j P_ji) / (2 pi_i)`, remainder on the
self-loop. This satisfies detailed balance exactly and targets **the measured stationary
distribution pi of the active kernel** — stated explicitly as the brief requires. It preserves
local connectivity (`Q_ij > 0` iff `P_ij > 0` or `P_ji > 0`) and is the unique additive
symmetrisation of the stationary flux, so it is not tuned toward any outcome.

Matched long-run trajectories under the active kernel and the reference, same start states, same
length, comparing occupancy, transition-direction frequencies, states visited and first-passage
behaviour.

## 7. Kernel classification, chosen before measurement

    STRUCTURAL_KERNEL_REVERSIBLE_WITHIN_TESTED_PRECISION
        if the maximum |J| over all pairs does not exceed the Monte-Carlo noise floor, estimated
        as the maximum |J| computed between the two independent kernel samples of the SAME kernel
    STRUCTURAL_KERNEL_NONREVERSIBLE_NO_MATERIAL_CURRENT_DETECTED
        if currents exceed that noise floor but the matched trajectory comparison shows no
        difference in structural occupancy beyond its own sampling error
    STRUCTURAL_KERNEL_NONREVERSIBLE_AUTHORED_CURRENT_DETECTED
        if currents exceed the noise floor AND are attributable to operator design rather than to
        boundary or validity geometry

No hard qualification consequence is frozen for the third outcome. Per the brief, that consequence
belongs to external review.

## 8. Verdict order

1. G1 instrument validity: replay, null construction, multiplicity agreement, kernel/live-code
   agreement within the frozen tolerance, audit identity. Any failure ⇒
   `INSTRUMENT_INSUFFICIENT_TO_ADJUDICATE`, stop.
2. G2 confirmatory halt/yield: `CONFIRMED_CONTENT_DIRECTIONAL_EFFECT` (qualification fails) or
   `V0_4_CONTENT_DISCOVERY_NOT_REPLICATED`. The V0.4 discovery is not erased either way.
3. G3 fresh-seed battery: any other cell surviving the GLOBAL family ⇒
   `NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS`.
4. G4 probability current: one of the three kernel classifications above.
5. G5 final: if the ordinary directional gates clear ⇒
   `NO_REPLICATED_MARGINAL_DIRECTIONAL_PRIOR_DETECTED`, which is explicitly not permission to
   launch if authored current was detected.

## 9. Commitments

No grammar change. No Metropolis correction, no reverse operators, no weight or step-size change,
even if the source of an asymmetry is obvious. No additional seeds. No pooling of V0.4 and V0.5
except as a clearly labelled secondary analysis after both are reported separately. Failed and
non-replicating results are kept under their own identity and never repaired.
