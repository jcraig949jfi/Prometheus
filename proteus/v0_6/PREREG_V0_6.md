# V0.6 Full-Space Nonequilibrium Crucible — PREREGISTRATION. Frozen before the production run.

Brief: `roles/Proteus/PROMPT_PROTEUS_V0_6_FULL_SPACE_NONEQUILIBRIUM_2026-09-03.txt`
sha256 `d97de9ead687745a3616434b64fc2351246064295b13c4ed1cddd658d602fa96`.

## 0. Frozen active physics

    grammar    proteus.grammar.v0.4
      5043f5e11a726b63a9553cc4855995c3ac324e55f8154ffe4adf28dad553a832
    runtime    73f110e21b9df879...
    affordance f1607ee8be680acc...
    manifest schema  hash recorded in PREREG_V0_6.json

Asserted by unit test and re-asserted by every runner. No operator, weight, VM rule, manifest
bound, initialization rule or configuration rule changes in this pass. There is no authorized
repair. Any source change affecting mutation physics invalidates the pass.

## 1. Structural space — regenerated, not inherited

The valid state set is regenerated from the PUBLISHED manifest rules (the committed manifest
JSON schema plus the affordance table's storage bounds) by a construction independent of the one
V0.4/V0.5 used, then compared by cardinality and hash. Result, obtained before the production run:

    regenerated states       2,044
    space hash               64e55c9d31b39b6b...
    matches prior set        yes (exact set equality)
    closure probe            400 mutations x 2,044 states = 817,600 proposals
    ESCAPED_VALID_STRUCTURAL_STATE_COUNT = 0

The precondition is met. Any escape during the production run is also ledgered and is an
instrument failure.

## 2. The adjudicated kernel is the LIVE operator

V0.5 showed the analytic kernel differs from the live one by median TV 0.0162 and maximum 0.1661.
The analytic form is therefore inadmissible as the primary kernel here and appears only as
historical evidence. The V0.6 kernel is estimated by EXECUTING `grammar.mutate`, marginalising
over uniformly random genome content, with self-loops from rejected proposals included and the
operator's own recorded rejection reason retained.

Parallelism is exact: each state's stream is `root.derive(L, T)` and `derive` does not advance the
parent, so a state's samples depend only on (seed, tag, L, T) and are independent of worker count.
A test asserts serial and parallel measurement agree exactly.

## 3. Sampling power — calibrated BEFORE any current was computed

A pilot on a frozen positional subset (every 20th state, 103 of 2,044) measured the row-wise total
variation between two independent estimates of the SAME kernel at n = 1,000 / 2,000 / 4,000 /
8,000. It computed no current, no stationary distribution and no direction. Fitted:

    median row TV = 1.0775 / sqrt(n)
    p95    row TV = 1.7940 / sqrt(n)

Required sample counts, computed from that fit:

    median <= 0.020   n >=  2,903      (the brief's floor)
    median <= 0.010   n >= 11,611
    p95    <= 0.020   n >=  8,047

**Frozen production sample count: n = 12,000 per state, per kernel.** This satisfies the
materially tighter pair of criteria below, which the brief invites when compute allows.

## 4. Gates, all frozen here

**G3 kernel precision** — primary criteria, on K_A versus K_B over all 2,044 rows:

    median row TV <= 0.010
    95th percentile row TV <= 0.020

Maximum row TV is reported but is NOT a criterion, because rare low-probability transitions make
it unstable. Also reported: mean, p90, p99, edge-presence disagreements. Failure ⇒
`FULL_SPACE_KERNEL_UNDERPOWERED` and `INSTRUMENT_INSUFFICIENT_TO_ADJUDICATE`, with any further
quantity emitted only as NON-ADJUDICATIVE.

**G4 stationary solve** — three methods, two of them numerically independent:

    power iteration      tolerance 1e-14 on the L1 change, fsum-normalised
    Gauss-Seidel         tolerance 1e-14, in-place sweeps on the incoming-edge form
    empirical occupancy  5,000,000 steps, external check with its own sampling error

    adjudicated residual   ||pi P - pi||_1 <= 1e-10
    solver agreement       ||pi_power - pi_gauss_seidel||_1 <= 1e-8

The adjudicated solution is the power-iteration one. The choice is fixed here so that no solver
can be picked after the fact for giving a cleaner current.

**G5 reversible control** — two references, both on the same support:

    additive:    Q(i,j) = (pi_i P_ij + pi_j P_ji) / (2 pi_i), which satisfies detailed balance
                 exactly and targets THE MEASURED STATIONARY DISTRIBUTION of the active kernel
    Metropolis:  uniform proposal over support neighbours with Metropolis acceptance, targeting
                 the DECLARED UNIFORM measure over the 2,044 valid states -- independent of
                 anything measured from the active process

    required: max |J| <= the material threshold defined below, |sigma| <= 1e-12

Failure of either control invalidates the instrument.

**G6 material current** — the threshold is defined from replicated estimation, not from a single
same-kernel maximum, and is fixed before the active current map is inspected:

    noise distribution = { |J_A(e) - J_B(e)| : e in connected pairs }
    material threshold = 1.0 x the 99th percentile of that distribution

Aggregate statistics (total |J|, entropy production, cycle affinities) are reported with their own
uncertainty and are the primary evidence; per-edge declarations are secondary and are counted, not
individually adjudicated.

## 5. Numerical replay contract

**EXACT layer** — byte-identical across every tested runtime: the structural state enumeration and
its hash, state ids, mutation seeds, per-state transition COUNTS, manifest and source identity
hashes, and all integer ledgers.

**NUMERICAL layer** — tolerances set by conditioning, not by observed differences, and each far
below the smallest quantity that could change a classification:

    stationary probabilities   |delta| <= 1e-9 absolute or 1e-6 relative
    probability currents       |delta| <= 1e-12 absolute
    entropy production         |delta| <= 1e-9 absolute
    residuals                  |delta| <= 1e-10 absolute

All adjudicated float sums use `math.fsum`, which is exactly rounded, so the CPython 3.12 `sum()`
change that broke V0.5's byte-identity does not enter any adjudicated quantity. Replay runs on
every CPython/OS combination available on this machine and the claim is bounded to those.

## 6. Attribution, made counterfactual

Per-operator destination counts are recorded for every state, so the kernel can be exactly
recomposed offline as

    P'(i -> j) = sum_op w'_op * ( count_op(i -> j) / count_op(i -> .) )

With the frozen weights this reproduces the measured kernel, which is checked and reported. With
any other weight vector it is an exact offline counterfactual. Variants evaluated, all analysis
only and none creating an active grammar: length-balanced weights, unreachable_removal removed,
config_perturbation removed, insertion and deletion equalised. The question answered is the
brief's: if the authored weights were replaced by a reversible weighting on the same support,
would the current disappear?

## 7. Arms deliberately NOT run, decided here

**Behavioral coupling (brief section 16).** Under the active grammar a single operator draw
produces the structural change and the content change as one event: an insertion both lengthens
the genome and writes random instructions. There is therefore no way to substitute the reversible
structural kernel while holding content treatment fixed without altering more than the structural
kernel. The brief instructs that this be said and the arm omitted. It is omitted, and this is
recorded before the run rather than after.

**Marginal battery (brief section 8 / G8).** Not rerun. The V0.5 fresh-seed battery under the same
global (coordinate x cohort) architecture is the standing result and nothing in V0.6 changes the
grammar it was measured on.

**Cohort-256 length cell (brief section 17).** No targeted test. No new seed.

## 8. Adjudication order

G1 source and audit identity; G2 complete-space closure; G3 kernel precision; G4 stationary solve;
G5 reversible control; G6 active full-space current; G7 attribution; G8 marginal battery (not
rerun). Verdict strings are exactly those the brief supplies, including the new
`NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`, whose prospective rule was written by external
review before any V0.6 measurement existed.

## 9. Commitments

No grammar change. No Metropolis correction of the active kernel, no reverse operators, no weight
rebalance, no step-size change — the Metropolis construction here is a CONTROL on a separate
object. No campaign, no world, no adapter, no selection. No threshold lowered after the run. No
solver chosen for its answer. Failed and inconclusive results are kept under their own identity.
