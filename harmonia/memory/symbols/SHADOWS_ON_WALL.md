---
name: SHADOWS_ON_WALL
type: pattern
version: 1
version_timestamp: 2026-04-21T00:10:00Z
immutable: true
status: active
previous_version: null
precision:
  canonical_definition: "Every measurement is a shadow; the thing measured is the fire that casts it. No single lens shows the territory directly. The territory is what survives across ALL coordinate systems. What fails to survive a coordinate change was a property of the ruler, not of the thing."
  operational_tiers:
    one_lens: "shadow — informative but coordinate-dependent"
    two_lenses_agreeing: "surviving candidate under one measurement class"
    three_lenses_agreeing: "coordinate-system-invariant within the tested class"
    all_known_lenses_agreeing: "durable; closest we get to the fire"
    disagreement_across_lenses: "the disagreement IS the map; the compression direction is unresolved"
  minimum_lenses_for_claim_tier:
    shadow: 1
    surviving_candidate: 2
    coordinate_invariant: 3
    durable: all_applicable_lenses
  override_protocol: "Any stance taken under fewer lenses than the tier requires must explicitly name the single shadow it rests on and list lenses not yet applied. Silent single-lens claims are forbidden."
  foundational_lineage: "Plato Republic VII (cave allegory); Lorentz/Einstein special relativity (invariant interval vs coordinate-dependent length); Pattern 6 (verdicts are coordinate systems); landscape_charter (domains are projections)."
proposed_by: Harmonia_M2_sessionA@c6729e3b8
promoted_commit: pending
references:
  - PATTERN_30@v1
  - MULTI_PERSPECTIVE_ATTACK@v1
  - GATE_VERDICT@v1
  - Pattern_6@c45fd79d5
  - Pattern_14@c45fd79d5
  - Pattern_18@c45fd79d5
  - methodology_multi_perspective_attack@cde766053
  - methodology_toolkit@c882e2ac5
  - landscape_charter@c45fd79d5
  - user_prometheus_north_star@cb83d41ef
  - F043@c9fc25706
  - F011@cb083d869
redis_key: symbols:SHADOWS_ON_WALL:v1:def
implementation: null
---

## Definition

**Every measurement is a shadow; the thing measured is the fire that
casts it.** No single lens — disciplinary prior, null model,
projection, scoring function, researcher perspective, LLM sampling
realization — shows the territory directly. Every measurement is a
projection of the territory onto one coordinate system. The territory
is what survives across *all* coordinate systems. What fails to
survive a coordinate change was a property of the ruler, not of
the thing.

This is Harmonia's most important foundational lesson. Every other
pattern, every verdict, every symbol, every finding rests on it.
When this principle is dropped, the substrate degrades into
"bookkeeping of shadows mistaken for fire" — which is exactly the
F043 failure mode, exactly the Pattern 19 "stale entry" failure
mode, and exactly the Pattern 20 "pooled artifact" failure mode,
generalized to the meta-level.

## Operational tiers (the drill)

Every finding carries a lens-count. Before it advances in tier, the
count must meet the threshold.

| Tier | Lens count | Verdict semantics |
|---|---|---|
| `shadow` | 1 | informative but coordinate-dependent; never a promotion basis |
| `surviving_candidate` | 2 agreeing | real within one measurement class; not yet invariant |
| `coordinate_invariant` | 3+ agreeing across distinct coordinate classes | evidence the feature survives projection change |
| `durable` | all applicable lenses agree | closest we get to the fire |
| `map_of_disagreement` | lenses disagree | the disagreement IS the finding; compression direction unresolved |

"Distinct coordinate classes" is load-bearing: three nulls from the
same null-family do not count as three lenses. The lenses must be
drawn from genuinely different disciplinary priors (measure-theoretic,
combinatorial, information-theoretic, etc.) for the count to apply.

## Anchor cases from the 2026-04-20 session

1. **Lehmer's conjecture** — five lenses (dynamical, information-
   theoretic, RG, adversarial, mass-gap) reached three different
   directional stances on the asymptote. `map_of_disagreement` mode.
   The community's "Lehmer's constant" is a *single-lens shadow* (one
   projection: reciprocal integer polynomials up to degree 44 under
   Mahler-measure definition). The fire's shape — the actual
   asymptotic floor of min M(f) — is not yet known; the shadow has
   been mistaken for it for 90+ years. Methodology caught this by
   forbidding deference to Smyth's theorem across threads; the
   consensus dissolved when each discipline argued from its own
   vocabulary.
2. **Collatz's conjecture** — five lenses (ergodic, information,
   random-walk, graph, computability) converged on stance A
   (termination) with three of them arriving at the SAME numerical
   constant τ(n)/log n ≈ 6.95 via independent mechanisms. `coordinate
   _invariant` evidence for the fire's shape on the truth dimension.
   Thread 5 (computability) disagreed on the *provability* axis —
   a second shadow dimension orthogonal to the first. Both dimensions
   now require drilling.
3. **F043 retraction** — the canonical case of shadow mistaken for
   fire. A z_block = −348 correlation under one lens (block-shuffle
   within conductor decile) looked durable. But the lens was
   blind to the algebraic coupling (BSD identity rearranges one
   variable into the other). The finding was one projection of an
   identity, not a measurement of arithmetic structure. Retraction
   is the substrate self-correcting when a second lens (Pattern 30
   algebraic-lineage check) revealed that the first lens was
   measuring the ruler, not the thing.
4. **F011 rank-0 residual** — currently labeled "surviving candidate
   under one properly specified test" precisely because its lens
   count under the SHADOWS_ON_WALL discipline is ONE (conductor-
   shuffle sanity null). Not durable, not coordinate-invariant.
   Track D (replication across independent implementations) is the
   add-a-second-lens task. Sage/lcalc external verification is the
   add-a-third-lens task. Until those land, F011 stays at
   `surviving_candidate`.

## The operational check (drill form)

Before any of the following:
- promoting a cell from +1 to +2
- citing a finding as "durable"
- committing to a stance in a multi-perspective attack
- claiming a new coordinate has resolved a feature

**Invoke the check**:

1. **How many lenses have been applied?** Name them. Each must be
   from a distinct disciplinary class, not variants of the same
   method.
2. **Which lenses have NOT been applied?** Name them too. The
   `methodology_toolkit.md` shelf is the live catalog of available
   lenses; cross-disciplinary transplants under gen_09 are extending
   it. If a canonical lens for this feature class has not been
   applied, note the absence.
3. **Which tier does the count support?** `shadow` /
   `surviving_candidate` / `coordinate_invariant` / `durable` /
   `map_of_disagreement`. Use that exact label, not "survives" or
   "confirmed."
4. **If the answer is a shadow or surviving_candidate, are you about
   to act as if it's durable?** If yes, the check failed; stop and
   add lenses first.

Silent single-lens claims are forbidden. A session that promotes a
finding without naming its lens count is in the F043 failure mode
regardless of whether it gets caught.

## Connected patterns / symbols

- **`PATTERN_30@v1`** — detects a specific class of single-shadow
  failure (algebraic-coupling-invisible-to-one-lens).
  SHADOWS_ON_WALL is the foundational frame; PATTERN_30 is one
  operational sweep that enforces it.
- **`MULTI_PERSPECTIVE_ATTACK@v1`** — the deployment pattern for
  applying SHADOWS_ON_WALL at the problem-level. Methodologically
  implements the drill on open problems.
- **`GATE_VERDICT@v1`** — every gate output is itself a shadow;
  SHADOWS_ON_WALL is the discipline that prevents a GATE_VERDICT
  from being mistaken for a verdict on the thing itself.
- **`Pattern_6`** (verdicts are coordinate systems) — the pattern-
  library entry this symbol canonicalizes. SHADOWS_ON_WALL is
  Pattern 6 renamed, promoted to symbol, and given operational
  tiers.
- **`Pattern_14`** (verdict vs shape) — same family; SHADOWS_ON_WALL
  says the shape matters because the verdict is always a shadow.
- **`Pattern_18`** (uniform visibility is axis-class orphan) —
  concrete instance of the principle: if every lens returns +1, the
  resolving axis is still outside the catalog; the feature is real
  but its fire is not yet located.
- **`landscape_charter`** — "domains are projections, not
  territories" is this symbol in one sentence. SHADOWS_ON_WALL is
  the operational expansion.
- **`user_prometheus_north_star`** — "compressing coordinate systems
  of legibility, not laws." SHADOWS_ON_WALL is the load-bearing
  reason WHY: because laws themselves are shadow-compressions;
  what we compress is the invariance across lenses.

## Lineage

- **Plato**, Republic VII — the cave. Prisoners mistake shadows on
  the wall for reality. The sun (or fire) is what actually projects.
  Mathematics has always had this problem; Prometheus is making it
  operational.
- **Lorentz / Einstein, special relativity** — length and duration
  are coordinate-dependent; the spacetime interval is the invariant.
  Physics solved this for its domain a century ago. Prometheus
  applies the same move to mathematics.
- **Gödel, incompleteness** — the reason the map never closes: no
  finite set of lenses can span all possible projections AND prove
  it does. The substrate must always be growing, and always
  acknowledge what it has not yet tested.

## Usage

**Tight:**
```
Finding F046: shadow (one lens — NULL_BSWCD under P020). Promotion
requires ≥ 2 lens from distinct classes. Flagged for Track D pilot.
```

**Loose:**
```
The 22.90% F011 residual is what we measure through one projection.
Until we add a second lens (Sage/lcalc external, independent
implementation, or non-LMFDB source), we cannot call it durable —
per SHADOWS_ON_WALL@v1 it is a surviving_candidate, not a fire.
```

**In a conductor decision:**
```
BEFORE: promote F046 to +2. (BLOCK — shadows-on-wall operational
check: only one lens applied.)
AFTER: promote F046 to surviving_candidate; queue second-lens task
on Agora; re-evaluate when lens count reaches 2.
```

## Version history

- **v1** 2026-04-21T00:10:00Z — first canonicalization after James
  articulated the foundational form of the principle ("We see
  shadows on the wall not the reality of the fire projecting it")
  and asked for it to be drilled, not just philosophically
  acknowledged. Absorbs Pattern 6 (verdicts as coordinate systems)
  and Pattern 14 (verdict vs shape); extends both with operational
  lens-count tiers. Third type-`pattern` symbol after PATTERN_30
  and MULTI_PERSPECTIVE_ATTACK. Becomes the load-bearing frame
  beneath every other pattern, verdict, and finding in the substrate.
