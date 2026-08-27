# VERDICT — AGENT D-3, Phase 1

    PREREG          d3-phase1-v1, frozen and committed at 38a5304d before any recorded run
    RUN             2026-08-27, four bases, ~5.2M metered substrate runs total
    ANTI-CHEAT      11/11 checks pass (results/anti_cheat.json)
    VERDICT         NO_BASIS_PASSED  -- generation stops. No worlds, no learner.

No basis passed the preregistered precondition set G1-G10. Under the frozen
precedence rules none of the preregistered verdict *terms* matched either,
because every basis failed and no single failure mode was universal. That is a
gap in the preregistered vocabulary, reported as such; the stop decision is
identical under any label.

---

## 1. Result table (order 0, preregistered gates)

    gate                       S1 TPC      S2 FLAT     S3 TRS      S4 REV
    G1  viable neighbour rate  PASS        PASS        FAIL        PASS
    G2  non-collapse           PASS        PASS        PASS        PASS
    G3  phenotype count        PASS        PASS        PASS        PASS
    G4  consumer liveness      PASS        PASS        PASS        PASS
    G5  connectivity           PASS        PASS        PASS        FAIL
    G6  taxonomy neutrality    FAIL        FAIL        PASS(k)     FAIL
    G7  order robustness       FAIL        PASS(k)     PASS(k)     PASS(k)
    G8  M0 coverage            PASS        FAIL(k)     FAIL        FAIL
    G9  M0 fairness            PASS(k)     PASS(k)     PASS(k)     FAIL(k)
    G10 witness access         PASS        PASS(k)     FAIL(k)     FAIL(k)
    ----------------------------------------------------------------------
    gates passed               8/10        8/10        7/10        5/10

`(k)` = KNIFE-EDGE: the verdict flips inside the preregistered +/-20% threshold
band and may not be described as robust. Full margins and both perturbed
verdicts for every condition are in `results/threshold_sensitivity.json`.

Each basis is blocked by a *different* precondition:

- **S1 (typed point-free calculus)** — the most navigable substrate found, and
  the only basis to pass both M0 coverage and witness access. Blocked purely on
  taxonomy: its edit distribution concentrates on one family.
- **S2 (total flat bytecode)** — passes everything on the substrate side except
  taxonomy, and is blocked on far-stratum reachability (0.15 vs 0.20).
- **S3 (rewrite rules)** — the only basis whose edits spread across families, and
  the only one where validity is a real predicate. Blocked on viability: 44% of
  radius-1 edits and 12.8% of radius-3 edits stay inside the language.
- **S4 (reversible register machine)** — the adversarial control. Behaves best on
  every counting metric and worst on every navigation metric.

## 2. The central quantitative finding

**Free validity and rich viable navigation did not co-occur in any of the four
bases.** The two properties traded off cleanly across the family:

    basis   P(valid|r=1)   P(valid|r=3)   families >=5% (r=1)   best M0 coverage
    S1      1.000          1.000          4                     0.533
    S2      1.000          1.000          6                     0.400
    S3      0.440          0.128          6                     0.317
    S4      1.000          1.000          6                     0.100

S3 is the only basis with a genuinely partial validity predicate, and it is the
only basis whose radius-1 edit distribution is broad *and* whose semantic-class
graph still holds together (giant component 0.81). It pays for that with a
viability curve that collapses with radius: 0.440 -> 0.222 -> 0.128 -> 0.045 ->
0.022 across r = 1,2,3,5,8. Under the frozen budget its far-stratum coverage is
0.10 and three of the four witnesses were never constructed.

S4 is the sharpest single lesson. It has total validity, zero destructive
outputs at every radius, 100% downstream-consumer liveness, 84% semantically
distinct neighbours at radius 1, and the largest phenotype space measured
anywhere in the experiment (6,019 census classes; one M0a run alone emitted
14,193 distinct semantic classes). Its giant component is 0.24 and its best M0
target coverage is 0.10, with **zero** hits in the mid and far strata. Every
mutation lands in a fresh phenotype, so nothing accumulates and no target can be
re-found. A phenotype space can be enormous and still be unnavigable.

## 3. Instrument defects found (these are the load-bearing findings)

### 3.1 G6 conflates operator bias with composition depth

The preregistered G6 statistic aggregates families over all radii (1,2,3,5,8).
At composed radii the substrate-generic syntactic taxonomy degenerates towards
its catch-all bucket, because a child that differs from its parent by several
composed edits looks like one general block replacement. Aggregated, `splice`
holds 0.47 / 0.88 / 0.51 / 0.83 of the semantically-distinct children for
S1/S2/S3/S4. Restricted to radius 1 — the only radius at which the shape
classification means anything — the picture inverts:

    basis   aggregated max share    radius-1 max share    radius-1 families >=5%
    S1      0.475 (splice)          0.628 (relabel)       4
    S2      0.879 (splice)          0.252 (splice)        6
    S3      0.509 (splice)          0.244 (delete)        6
    S4      0.832 (splice)          0.220 (relabel)       6

So the preregistered G6 failure on S2 and S4 is an artifact of my own statistic,
not a property of those substrates. The preregistered verdict stands as computed
(`results/phase1_verdict.json`); the diagnostic is in
`results/mutation_bias_r1.json`. It is **not** load-bearing for the stop: under
the radius-1 reading S2 still fails G8, S4 still fails G5/G8/G9/G10, S1 still
fails G6 (0.628 > 0.60), and no basis reaches 10/10 either way.

### 3.2 G6 is near-tautological even when measured correctly

The atomic-operator -> family confusion table kills the taxonomy-neutrality
measurement outright on the sequence bases:

    S2/S3/S4:  E-DELETE    -> delete       1.00
               E-SUBST     -> relabel      0.98-1.00
               E-DUPBLOCK  -> duplication  0.97-1.00
               E-TRANSPOSE -> permutation  0.86-0.89
               E-SPLICE    -> splice       0.85-0.93
               E-INSERT    -> lengthen-other 0.61-0.82

Each frozen edit operator maps onto exactly one human family. The measured
"family distribution" is therefore a relabelling of the uniform distribution I
chose over my own six operators. **A taxonomy-neutrality gate built from a
classifier over the mutation operator's output shapes cannot distinguish "the
physics does not privilege human categories" from "I sampled my six edit
operators uniformly, and each one is a human category."** Whatever G6 measured,
it was not the substrate.

S1 is the one place the map is not one-to-one: E-PERTURB, E-PRUNE and E-REPLACE
all collapse onto `relabel` (0.88-1.00), E-GRAFT splits across
prepend/wrap/splice, and **E-SWAP produces an identical token string in 100% of
806 sampled draws** — one of five tree operators is dead, because same-typed
sibling subtrees in small typed terms are usually literally equal. That dead
operator was not detected before the freeze and was not repaired after it.

### 3.3 G4 is vacuous wherever validity is total

Downstream-consumer liveness asks whether an artifact, applied to a reference
artifact, emits something valid and non-constant. On S2 and S4 every in-range
tuple is a program, so the gate reduces to "does the output vary at all":
S4 scores 1.000 at every radius and S2 scores 0.87-0.97. Only S1 (0.50-0.60) and
S3 (0.76-0.95) put any pressure on it. G4 passed on all four bases and
discriminated nothing.

### 3.4 G3 rewards the pathology G8 punishes

Raw semantic-class counts and target reachability are anti-correlated across the
family: S4 has the most classes and the worst coverage; S3's M0c found 9,402
classes and hit 10% of targets. Counting phenotypes is not measuring a navigable
space, which is the thing the mission asked to be counted instead of syntax —
and this experiment shows the replacement metric has the same defect one level
up.

### 3.5 Probe-relative classes are under-resolved on two bases

Preregistered tolerance was 2% between the 12-probe and 16-probe class counts.
Measured: S1 4.3% (345 -> 360), S3 6.1% (314 -> 333) — both FAIL; S2 1.4% and S4
0.0% pass. Class counts are monotone non-decreasing in probe count, so the
12-probe count is the conservative (lower) bound and G3 was gated on it; the
literal prereg wording said to gate on the 16-probe count, which is the looser
direction. The deviation is disclosed here and is not decisive: G3 passed by
1583/500 and 709/500.

## 4. M0 fairness (the part that did work)

All four baselines ran under one meter, one validity API, one probe battery, one
observation whitelist, and identical 200,000-unit budgets. No baseline could see
a semantic fingerprint, a family label, a target, a witness, the filesystem or
the host. Eleven anti-cheat checks pass, including meter equality (every substrate
run inside an M0 phase went through the harness) and post-budget refusal.

    basis   M0a walk   M0b QD   M0c cost-biased   M0d recombination   best
    S1      0.517      0.517    0.433             0.533               M0d
    S2      0.233      0.400    0.267             0.367               M0b
    S3      0.183      0.317    0.100             0.150               M0b
    S4      0.017      0.100    0.000             0.017               M0b

No monoculture: the winner is M0d once and M0b three times, and the naive walk
M0a is never best. G9 (>=2 variants within half of the best) holds on S1/S2/S3
and fails only on S4, where coverage is near zero for everyone. The weak-M0
trap the mission warned about is therefore avoided for three bases — the
denominator for any future history-conditioned learner would be a
quality-diversity or recombination baseline, not a random walk.

Two asymmetries are recorded rather than fixed. First, the target pool is built
from chain-census classes *and* from an independent fresh-sampling pool
precisely so no single baseline owns the denominator; the far stratum is
dominated by classes that 12-step chains never reached (861/2531/3964/6359
candidates per basis), which is why far coverage is the binding condition in G8.
Second, on S3 invalid candidates cost 1 unit instead of 13, so the same budget
buys ~40,000 evaluations there against 15,385 on the total-validity bases — the
resource model pays for validity, and S3 still lost.

## 5. Witnesses

    witness         S1               S2               S3            S4
    W1 REVCOND      built, 204 runs  built, 10.5k     failed 4.95/12  failed 1.13/12
    W2 DEDUP        failed 11.14/12  failed 10.2/12   failed 11.12/12 failed 1.66/12
    W3 PREFIXSUM    built, 3.1k      failed 3.98/12   failed 4.96/12  failed 1.61/12
    W4 UNIVERSAL    built, 4.9k      built, 708       built, 2.7k     built, 116

W2 DEDUP was constructed by nobody, and got within one probe of the oracle on
three bases (11.14, 10.20, 11.12 out of 12) — a witness that is nearly reachable
everywhere and actually reachable nowhere is the most informative of the four.

W4 turned out to be a weak witness: "emit a valid, live, different artifact from
every reference artifact" is nearly free wherever validity is total (S4 built it
in 116 metered runs, with a 15-token program). An artifact-level witness has to
demand a *specified* behavioural relation between input and output artifact, not
merely difference. That is a design error in the witness set, disclosed rather
than repaired.

## 6. What this does and does not license

Licensed by the data:

- In four independently frozen computational bases, generic self-transformation
  did **not** produce a large, behaviorally diverse, locally viable *and*
  fairly navigable phenotype space. Each basis failed a different precondition.
- The failure modes are structurally distinct and reproducible: viability
  collapse under composed edits (S3), phenotype isolation with total validity
  (S4), edit-family concentration (S1), and far-region unreachability (S2).
- A history-free M0 suite can be constructed that is not a straw man: three
  bases had at least two independent baselines within a factor of two of the
  best, and the best was never the naive walk.

Not licensed, and not claimed: anything about cognition, intelligence,
understanding, autonomous diagnosis, open-endedness, or the elimination of human
priors. No global program equivalence is claimed anywhere; every equivalence in
this repository is relative to a 12-input probe battery, and on two bases that
battery is measurably under-resolved.

## 7. Stop

Preconditions failed, so Phase 2 (worlds) and Phase 3 (history-conditioned
learner) are not built. Per the no-rescue rule: no primitive was added, no
typing relaxed, no horizon widened, no mutation operator changed, no threshold
moved, and no fifth basis was built after the census was read. The failing bases
are preserved as failed.

## 8. What a successor experiment inherits

1. **Do not measure taxonomy neutrality with a classifier over the mutation
   operator's own output shapes.** The operator menu and the family taxonomy are
   the same object seen twice (3.2). A real test has to derive the family
   assignment from *behavioural* relations between parent and child phenotypes,
   with the operator identity held out — and must show that the derived families
   are not a permutation of the operator set.
2. **Gate on navigable structure, never on phenotype counts.** S4 maximised
   every counting metric and minimised every navigation metric (3.4). The
   candidate replacement is target re-findability per unit cost, measured
   against a pool built by a generator independent of the searcher.
3. **A liveness gate is only informative where validity is partial** (3.3).
4. **Audit the mutation operators for dead members before freezing.** One of
   S1's five tree operators was a no-op in 100% of draws and this was invisible
   until the post-hoc confusion table.
5. **The trade-off itself is the next hypothesis.** Across four bases, the
   breadth of the radius-1 edit-family distribution and the radius-3 viability
   rate moved in opposite directions. Whether a physics exists that is both
   validity-closed and family-broad is now a sharper question than the one this
   generation asked, and it should be attacked directly rather than as a
   precondition to a learning experiment.

---

### Artifacts

    MANIFEST.md, PREREG-CENSUS.md, prereg/gates.json     frozen design, committed pre-run
    results/phase1_verdict.json                          mechanical verdict
    results/basis_reports.json                           every gate, every condition, per basis
    results/threshold_sensitivity.json                   margins and +/-20% perturbed verdicts
    results/order_robustness.json                        3 canonical orders, Spearman pairs
    results/classifier_audit.json                        aggregated family shares
    results/mutation_bias_r1.json                        radius-1 shares + operator confusion
    results/m0_comparison.json                           4 baselines x 4 bases
    results/reachability_targets.json                    60 targets per basis, stratified
    results/phenotype_graph.json                         class-graph size and components
    results/census_rows.jsonl                            28,800 candidate rows
    results/substrate_specs.json, mutation_specs.json    frozen physics and operators
    results/probe_hashes.json, frozen_hashes.json        probe and file hashes
    results/anti_cheat.json                              11 checks
    ledgers/basis_*.json, graph_*.json, census_rows_*    raw per-basis ledgers
