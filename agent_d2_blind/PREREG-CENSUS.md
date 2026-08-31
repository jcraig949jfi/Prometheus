# PREREG-CENSUS — frozen before census code was written

Applies to: phase 1 (attack the computational physics). Frozen 2026-08-27, before any
enumeration, classification or statistic was computed. Governs all three grammar bases
(G1 LISPY, G2 PATHEDIT, G3 REWRITE) identically.

Hard rule for this phase: **no grammar may be modified after its census has been run.**
A basis that fails dies and its code and census are preserved. Failures are not repaired.

---

## 1. Objects

- **Probe battery A** — 24 frozen artifacts (valid programs of the basis under test), built
  by a fixed construction rule, spanning: atoms, selectors, constructors, conditionals,
  recursive traversals, deep/shallow, error-producing and total. Hashed into the ledger.
- **Screen battery A4** — the first 4 elements of A, used only to bucket candidates before
  the full battery. A screen is never a statistic.
- **Input battery I12** — 12 frozen Vals (symbols and nested lists over {a,b,c,d}).
- **Extended input battery I24** — I12 plus 12 further Vals, used only for CG-G.

## 2. Fingerprints (both are computed; they are never conflated)

- `struct_fp(t)` = hash of the 24 outputs `apply(t, A_i)`, with errors encoded by error
  kind only, and non-programs encoded as INVALID.
- `sem_fp(t)` = hash of, for each i, the behaviour of `apply(t,A_i)` on I12
  (a 12-vector of Vals/error-kinds), with INVALID/ERR markers passed through.

Semantic equality is **probe-relative** and is reported as such. No claim of program
equivalence is made anywhere.

## 3. Trivial classes (computed before any family classifier)

- `NOOP_struct` — output equals input on every probe.
- `NOOP_sem`   — `sem_fp` equals that of the identity transform.
- `DEAD`       — every probe yields ERR or INVALID.
- `CONSTANT`   — every non-error output is the same term (independent of the probe).

"Non-trivial" = not NOOP_sem, not DEAD, not CONSTANT.

## 4. Legacy-family classifiers (executable; per probe, then aggregated)

Given probe term p and output term o (o a Val, o != p):

| label | executable predicate | legacy counterpart |
|---|---|---|
| WRAP_LIKE   | p occurs as a proper subterm of o | CONTROL_WRAP |
| APPEND_LIKE | p,o lists; len(o)>len(p); o[:len(p)] == p | APPEND_MUTATION |
| PRE_LIKE    | p,o lists; len(o)>len(p); o[-len(p):] == p | PRE_TRANSFORM |
| ROUTE_LIKE  | o is a list, o[0] is the conditional head, and p occurs in o | ROUTING_MUTATION |
| DELETE_LIKE | o is a proper subterm of p | deletion |
| RELABEL_LIKE| tree skeletons of o and p identical, o != p | REPRESENTATION_MUTATION |
| DUP_LIKE    | p occurs >= 2 times as a subterm of o | MACRO_MUTATION (fragment reuse) |

`LEGACY = {WRAP, APPEND, PRE, ROUTE, DELETE, RELABEL, DUP}`.

**Disclosed limitation:** MEMORY_MUTATION and ALGORITHM_MUTATION have no faithful
structural predicate. They are therefore *not* detectable by this classifier and will fall
into the residual by construction. This is why CG-E below charges the unaudited residual
to the legacy side rather than the novelty side.

**Aggregation.** A transform carries label F iff, over the probes whose output is a Val and
differs from the input, at least 3 qualify and at least a fraction `c` satisfy F.
Default `c = 0.9`. `MIXED` = two or more labels. `OTHER` = no label and non-trivial.

## 5. Residual audit (secondary, executable)

Applied to OTHER only:

- S1 PARTIAL_CONTAIN — a proper subterm of p of size >= 2 occurs in o, but p does not.
- S2 PERMUTE — leaf multisets of o and p are equal, o != p.
- S7 FEATURE_COLLAPSE — o is constant within each partition of probes by head symbol.
- DUP2 — some proper subterm of p occurs more often in o than in p.

Only S1, S2, S7, DUP2 count as **substantive** audits. Pure size descriptors (grew /
shrank / same size) are recorded but do **not** count as characterisation.
`R2` = OTHER classes with no substantive audit hit. R2 is the unaudited residual.

## 6. Census gates (per basis). Margins are reported for every gate.

- **CG-A expressiveness floor** — the basis expresses a hand-built witness transform for
  every world admitted in phase 2. Checked after the world census; a basis failing CG-A
  cannot host the evidence run.
- **CG-B structural richness** — distinct `struct_fp` among non-DEAD transforms at the
  horizon >= 500. Attainable maximum is the enumerated program count and is reported, so
  the gate is shown reachable before it is read.
- **CG-C legacy dominance** — among **non-trivial semantically distinct classes**,
  `share(carrying >= 1 LEGACY label) <= 0.60`.
  Rationale: above a clear majority, the physics has effectively supplied the taxonomy.
  Sensitivity reported across 0.40–0.80.
- **CG-C_worst adversarial residual** — `share(LEGACY) + share(R2) <= 0.60`.
  This is the section-9 attack taken at face value: the unaudited residual is charged
  against the hypothesis, not for it. If CG-C passes but CG-C_worst fails, the leakage
  result is recorded as **NOT ESTABLISHED**, not as a pass.
- **CG-D cheapness / low-rank privilege** — `median_minsize(LEGACY classes) >=
  median_minsize(non-LEGACY non-trivial classes) - 1.0` (grammar nodes).
  Rationale: legacy families may be expressible, but must not be systematically cheaper
  than the surrounding behaviour space by more than one node. Sensitivity over -0.5..-2.0.
- **CG-E residual size** — `share(R2) <= 0.25` of non-trivial classes. Reported either way;
  it does not by itself kill a basis, but a large R2 makes CG-C_worst decisive.
- **CG-F canonical order** — battery of 12 token orderings: declaration, reverse, and 10
  seeded random permutations (seeds 1..10). Minimal-size statistics must be **identical**
  across all 12 (invariant by construction; any deviation is an implementation defect and
  forces SUBSTRATE_INVALID). Rank statistics: median Spearman rho between per-family
  min-rank vectors >= 0.8 for rank claims to be called robust; otherwise rank-based
  statements are reported as ordering-sensitive and are not used in any verdict.
- **CG-G alias stability** — growing I12 to I24 changes the count of semantic classes by
  <= 10%. Otherwise semantic claims are flagged probe-unstable.
- **CG-H classifier sensitivity** — consistency threshold c varied over {0.7,0.8,0.9,1.0};
  the CG-C and CG-C_worst verdicts must be invariant, else reported classifier-sensitive.

**ST4 (non-privilege) passes for a basis iff CG-B, CG-C, CG-C_worst and CG-D all pass.**

## 7. Horizon

`H_exact` is the largest program size such that the cumulative count of typed-valid
transforms is <= 1,000,000 and the projected full census cost is <= ~40 minutes per basis.
Counts and timing are measured first; H is then frozen and recorded before any classifier
statistic is computed. Sizes above H are covered by uniform stratified sampling
(N = 100,000 per size) and reported separately, never merged into exact counts.

Program size = number of grammar productions used (the enumeration's own length measure).
Val-node count is recorded alongside but is not the enumeration measure.

## 8. Basis selection rule (frozen, neutral, chosen before any result)

If more than one basis passes ST4, the **lowest-index passing basis** hosts the evidence
run (G1 < G2 < G3) and the next passing basis is the replication basis if compute allows.
Selection is never made on census outcome magnitude.

If **no** basis passes ST4, the verdict is `SUBSTRATE_INVALID` and the run stops there.
That is an admissible and valuable outcome.

## 9. What this phase cannot show

The census speaks only to **P0**. A rich or neutral transformation space is not evidence
that experience discovers anything. No census number may appear in support of P1–P4.
