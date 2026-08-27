# PREREG-CENSUS — AGENT D-3 Phase 1
Frozen 2026-08-27, before any execution of census, M0, reachability or witness code.
Everything numeric in this document is mirrored machine-readably in `prereg/gates.json`.

---

## A. Frozen constants

    VALUE DOMAIN      ints in [-512, 512]; sequence length cap 48
    PROGRAM CAP       32 tokens
    FUEL              S1: 400 eval steps | S2: 300 machine steps | S3: 80 rewrites | S4: 64 instructions
    VALUE PROBES      12 fixed inputs (probes/battery.py, hashed into probe_hashes.json)
    LIVENESS PROBES   the first 4 value probes (used for downstream-consumer liveness only)
    ARTIFACT PROBES   4 reference artifacts per (basis, order), generated from RNG seed 913 and
                      required to be live; they are the inputs on which an artifact is exercised
                      *as a transformer of executable artifacts*
    SEEDS             8 live seed artifacts per (basis, order), RNG seed 20260827,
                      <=800 rejection tries; if <8 live seeds exist that is recorded, not repaired
    RADII             r in {1, 2, 3, 5, 8}
    RADIUS CENSUS     order 0: 120 mutants per (seed, radius) = 4800 candidates/basis
                      orders 1,2: 30 mutants per (seed, radius) = 1200 candidates/basis
    CHAIN CENSUS      order 0 only: 8 seeds x 24 walks x 12 radius-1 steps = 2304 steps/basis
    M0 BUDGET         200,000 metered substrate runs per variant per basis (identical for all variants)
    WITNESS BUDGET    150,000 metered runs per witness per basis
    RNG               all streams derived from fixed integer seeds recorded in the ledgers

## B. Definitions (preregistered, probe-relative)

- `sem_fp(P)` = sha1 over the 12-tuple of (output | status) of P on the value probes.
- `struct_fp(P)` = sha1 over, for each of the 4 artifact probes A: (status, validity of P(A),
  bucketed length delta, P(A)==A, coarse symbol-set sketch of P(A)).
- **live(P)** = valid AND ok on >= 6 of 12 value probes AND >= 2 distinct outputs.
- **destructive candidate** = invalid, or not live.
- **identity candidate** = valid and `sem_fp == sem_fp(parent)`.
- **mixed/nontrivial** = valid, live, and not identity.
- **downstream-consumer liveness** = exists an artifact probe A with P(A) ok, P(A) valid, and
  P(A) live on the 4 liveness probes (>=2 ok, >=2 distinct).
- **semantic class** = equivalence class of `sem_fp`. **structural class** = class of `struct_fp`.
- Equivalence is probe-relative everywhere. No global equivalence is claimed.

## C. Probe-battery stability protocol (fixed in advance)

On a fixed subsample of 800 order-0 candidates per basis, recount semantic classes using
probe prefixes of size 4, 8, 12 and the 12 probes plus 4 extension probes (16).
Tolerance: abs(classes(16) - classes(12)) / classes(12) <= 0.02.
If the tolerance fails for a basis, that basis's semantic-class counts are reported with an
explicit instability flag and gate G3 is evaluated using the **16-probe** count, which is the
conservative direction: more probes can only split classes, never merge them, so an unstable
12-probe count is an under-resolved view and the 16-probe count is the better-resolved one.
Instability is recorded, not repaired.

## D. Canonical-order robustness (fixed in advance)

Three preregistered orders. Order k applies a fixed permutation (seeded 101+k) to the
basis opcode-index space and to the payload space, and re-derives seeds and artifact
probes under that order. Order 0 = identity permutation.
Reported: per-gate verdict under each order, Spearman rank correlation of mutation-family
densities across order pairs, and stability of the minimal live-seed size.

## E. Mutation-bias audit (offline, never learner-visible)

Primary track — substrate-generic syntactic shape of (parent -> child) token sequences:
`identity, append, prepend, wrap, delete, relabel, permutation, duplication, splice,
lengthen-other, shorten-other, residual`.
Secondary descriptive track — operation-level deltas where an op table exists
(`control-like, memory-like, representation-like, route-like`), reported but not gated.
Residual handling: **residual is charged adversarially** — its mass is added to the
largest non-residual family before computing the max-family share used by gate G6.

## F. M0 suite (frozen before any learner exists; no learner is built this generation)

All four variants receive: the same physics, the same mutation process, the same 8 seed
artifacts, the same probe batteries, the same verification, and the same 200,000-run meter.
None may import the classifiers, the target list, or any semantic diagnostic label.

    M0a  generic local mutation walk (accept any valid child; restart every 200 steps)
    M0b  generic quality-diversity / MAP-Elites over substrate-generic behavior descriptors
         d1 = bucketed mean output length, d2 = number of distinct probe outputs,
         d3 = bucketed fraction of probes where output == input
    M0c  cost-biased random sampling of fresh valid programs, size ~ 2^(-size/8)
    M0d  recombination (splice) of two members of the archive of valid distinct-semantics
         artifacts, plus optional single mutation; no failure history

## G. Reachability targets and witnesses (frozen procedure)

Target pool is built from two *independent* generators so that no single M0 owns the
denominator: (i) semantic classes discovered by the chain census, (ii) semantic classes
discovered by fresh cost-biased random sampling of 6000 valid programs. Targets are
stratified by minimal known construction depth into near (<=2), mid (3-5), far (>=6),
20 sampled per stratum, 60 total, RNG seed 4242. Hit = an M0 emits any program with the
target `sem_fp` within budget.

Four behavioral witnesses, specified by oracle on the value probes, none of which is a
single human edit category:

    W1 REVCOND    reverse the input iff its sum is even, else identity
    W2 DEDUP      delete adjacent duplicates
    W3 PREFIXSUM  running sums
    W4 UNIVERSAL  a *universal live self-transformer*: for all 4 artifact probes A,
                  P(A) is valid, live, and semantically different from A

Witness construction cost is estimated by bounded generic search with oracle-guided
hill-climbing (human-side cost estimate only; not available to any M0).

## H. GATES (preregistered; not movable)

Evaluated per basis. A basis PASSES Phase 1 only if G1-G10 all hold for it and the
anti-cheat battery passes globally.

    G1  VIABLE NEIGHBOR RATE       P(valid | r=1) >= 0.60  AND  P(valid | r=3) >= 0.35
    G2  NON-COLLAPSE               P(sem != parent | valid, r=1) >= 0.25
    G3  PHENOTYPE COUNT            distinct semantic classes over the order-0 census >= 500
    G4  CONSUMER LIVENESS          fraction of valid candidates with >=1 live downstream
                                   consumer >= 0.30
    G5  CONNECTIVITY               largest connected component of the semantic-class graph
                                   (radius-1 edges) >= 0.50 of classes in that graph
    G6  TAXONOMY NEUTRALITY        adversarially-charged max family share <= 0.60 among
                                   semantically-distinct children AND >= 4 families each
                                   with >= 5% share
    G7  ORDER ROBUSTNESS           G1, G2, G4, G6 verdicts identical across all 3 orders AND
                                   family-density Spearman >= 0.60 for every order pair
    G8  M0 COVERAGE                best M0 hits >= 0.35 of the 60 targets within budget AND
                                   >= 0.20 of the far stratum
    G9  M0 FAIRNESS                >= 2 distinct M0 variants reach >= 0.50 x best-M0 coverage,
                                   AND the static no-label test passes for all variants
    G10 WITNESS ACCESS             >= 2 of the 4 witnesses constructed by bounded generic search,
                                   AND >= 1 witness class reached by some M0 within budget

Sensitivity reporting is mandatory for every gate: the margin, and the gate verdict under
+/-20% perturbation of the threshold. A pass whose margin is inside the +/-20% band is
reported as KNIFE-EDGE and may not be described as robust.

## I. Verdict vocabulary (stop-on-invalid)

    SUBSTRATE_INVALID          anti-cheat or construction failure
    VIABILITY_COLLAPSE         G1/G2 fail on every basis
    PHENOTYPE_POVERTY          G3/G4/G5 fail on every basis
    TAXONOMY_BIASED            G6/G7 fail on every basis
    M0_UNFAIR                  G9 fails where G1-G7 passed
    M0_COVERAGE_INSUFFICIENT   G8/G10 fail where G1-G7 passed
    WORLD_PHASE_READY          some basis passes G1-G10 and anti-cheat passes

Precedence when several apply: SUBSTRATE_INVALID > VIABILITY_COLLAPSE > PHENOTYPE_POVERTY
> TAXONOMY_BIASED > M0_UNFAIR > M0_COVERAGE_INSUFFICIENT > WORLD_PHASE_READY.
Any non-READY verdict stops the generation. Worlds and learners are not built.

## J. Anti-cheat battery (must pass before the evidence phase is read)

Static: learner-visible observation records restricted to a numeric key whitelist;
no host introspection (`eval`, `exec`, `__import__`, `globals`, `inspect`) in M0 code;
no filesystem access in M0 code; no import of classifiers / targets / witnesses / oracles
by M0 or by the mutation process; identical validity API for all variants.
Dynamic: the metered run counter equals the substrate internal run counter (no work
outside the meter); no result is accepted after the budget is exhausted; probe hashes are
identical across all variants and orders; seed streams for M0 and for target construction
are disjoint; targets are never passed into a baseline.

## K. No within-generation rescue

Once this file is committed: no primitive added, no typing relaxed, no horizon widened,
no mutation operator changed, no threshold moved, no fifth basis built. A failing basis is
preserved as failed. If all bases fail, the verdict is failure and the generation stops.
