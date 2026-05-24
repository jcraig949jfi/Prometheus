# Techne Substrate Audit — 2026-05-24

**Author:** Techne (Claude Opus 4.7 instance)
**Trigger:** user request after Fire #87 conversation about diminishing returns
**Audit window:** Fire #58 (2026-05-18) → Fire #87 (2026-05-24) — 87 fires, ~30 wall hours of substrate generation
**Status:** working substrate; productivity decelerating; bottleneck shifted from generation to review

---

## Glossary (what these numbers actually mean)

- **Record:** a single claim emitted by a generator (e.g., "knot.signature == ec.rank for object pair X|Y, verdict=KILL"). Substrate-internal unit.
- **Signature template:** a coarse claim *shape* — the family of records that share generator + invariant pair + relation + verdict class but differ in specific objects. ~3000 unique templates currently in the substrate.
- **Promoted record:** a record that passed the daemon's info-density filter and was written to a per-fire promotion JSONL. Substrate-internal selection, NOT external review. 1469 total.
- **Verified finding:** a substantive, externally-validated mathematical claim — reviewed by a human or model, judged true AND non-trivial AND non-obvious. **Currently zero.** The 1469 promoted records have never been read by a human or model.

The word "discovery" has been overloaded historically and is misleading. This audit avoids it.

---

## Headline metrics

| Metric | Value | Notes |
|---|---|---|
| Batches completed | 87 | Honest-era count (#58 onward) |
| Cumulative records | 374.9M | Raw generator output |
| Records killed | 211.1M | 56.3% kill share — the substrate is mostly falsifying its own claims |
| Records confirmed | 144.2M | Some real, some trivial |
| Promoted records | 1,469 | Info-density-filter survivors |
| Promote rate | **3.92 per million** | 1 in 250K records is "promote-worthy" |
| Signature templates (all gens) | 3,031 | Combinatorial shape variants tried |
| Signature templates (discovery-role only) | 2,572 | Excludes b1/c4/f1/g3 alive-monitors |
| Demand signal events | 13.78M | Unfulfilled primitive requests |
| **Verified mathematical findings** | **0** | No external review has occurred |
| handoff_daemon compaction recovered | ~167 GB | Across the audit window |

---

## The reservoir model (empirically validated, Fire #80-#87)

Each generator has a **fixed-size template reservoir** that drains on first pick at scale. It does **not** refill via wall-clock time. Refill only happens if upstream catalogs are expanded or if other gens produce new parent claims.

Evidence (5+ confirmed instances):

| Gen | Burst fire | Burst templates | Re-picks | Re-pick yield |
|---|---|---|---|---|
| f4 | #66 | 175 | #80, #82 | 0, 0 |
| e2 | #79 | 269 | #81, #87 | 0, 0 |
| g4 | #65 | 131 | #82 | 0 |
| g5 | #83 | 139 | #85 | 0 |
| a5 | #72 | 38 | #85 | 0 |
| c1 | #62 | 234 | #86 (24-fire gap) | 2 |
| **c5** | **#68** | **68** | **#77, #85** | **31, 60** |

**c5 is the exception.** Its specialization-mutation source consumes parent claims from other gens, so the reservoir keeps refilling. The rest are one-burst-and-done.

---

## Template growth deceleration

| Window | Fires | Avg templates added/fire | Note |
|---|---|---|---|
| #58 → #66 | 9 | ~80 | Initial discovery phase |
| #67 → #75 | 9 | ~141 | e2#79 outlier burst |
| #76 → #86 | 11 | ~47 | Multiple zero-fires |
| #82 → #87 | 6 | **~10** | Starvation regime |

The substrate's template-coverage curve is approaching asymptote. Each new fire's marginal contribution trends toward zero.

---

## Per-gen volume vs yield

Top 10 by total records emitted (out of 87 fires):

```
gid   fires   records      kill%  dup%   templates  notes
b3       26  28,158,387    57.1%  26.4%  ?           (alive-monitor INFRA_DIAGNOSTIC for inverse-test)
a2       35  27,986,452    93.3%   3.7%  ?           heavy falsifier
a1       47  26,959,212    69.0%   3.1%  176         saturated at single burst
c1       36  23,514,997    65.0%   6.4%  241         saturated; second-wave once at #62
d3       25  22,467,810    98.3%   0.6%  ?           triangulation-driven, 98% kill
a3       28  22,426,623    63.6%   0.2%  192         saturated
f2       14  18,644,393    65.8%   0.0%  175         saturated
f4       19  16,976,578    65.8%   0.0%  176         saturated
g5       12  15,633,383     7.8%   1.7%  139         high confirm rate
g4       13  14,290,033     5.4%   6.4%  131         high confirm rate
```

**Volume ≠ value.** b3 has 28M records but is an INFRA_DIAGNOSTIC (excluded from discovery-role templates). a2 has 28M records and 93% kill rate but contributes few unique templates.

---

## Templates by verdict class

```
CONFIRM:      1,144 templates /   34.9M seen
KILL:         1,137 templates /   83.8M seen
INCONCLUSIVE:   243 templates /    8.7M seen
UNVERIFIED:     507 templates /     18K seen
```

The **UNVERIFIED bucket is notable.** 507 distinct claim templates the substrate emitted but couldn't verify (e2-style literature claims with no oracle). Each is seen ~36 times on average. These are EXACTLY the candidates that need external review.

---

## Promote-rate analysis

**1469 / 374.9M = 3.92 promoted records per million.**

Each fire promotes ~20 records via the info-density filter. The filter is essentially deterministic per gen — same 20 (roughly) every fire from the same gen mix. So the promote rate is gen-driven, not data-driven.

**The promote filter is a sampling mechanism, not a quality judge.** Its 20-records-per-fire output is mostly an internal accounting artifact.

---

## Downstream consumption gap

```
ergon outbox bundles emitted: 52
ergon outbox inbox pending:    0
human-reviewed count:           0
verified mathematical findings: 0
```

Penelope (Ergon's consumer) ingests every bundle the handoff_daemon emits — that's why inbox=0 and consumed=52. But Penelope's ingestion is just adding records to a training corpus; it's not substantive review.

**No human or model has read any of the 1469 promoted records.** The substrate has been generating candidates for 6 days; none have been validated.

---

## Demand signals — the substrate's voice

Top 6 wanted primitives, by total demand events:

```
   9,092,686  knot/nf_class_number             ← OVERWHELMING demand
   1,122,603  ec/j_invariant
   1,121,007  ec/discriminant
     980,788  knot/alexander_polynomial_degree
     905,345  knot/hyperbolic_volume
     561,159  ec/regulator
   ────────
  13,783,588  total demand events
```

The substrate is **shouting** for these primitives. Every fire that includes a1/f1/h4 generates millions of demand events for invariants that aren't in the current catalogs. **9.1M unfulfilled requests for `knot.nf_class_number` alone.** This is the strongest signal in the audit data.

If even half these primitives were populated in the catalog, the substrate would have new claim-space to explore — refilling some reservoirs.

---

## What needs to happen next (substrate-honest)

Three strategic options, ordered by my recommendation:

### Option A: Pivot to review (RECOMMENDED)
- Pause generation cadence to 25% (per user request)
- Build a review pipeline that reads promoted records + their associated kill_pattern / claim_payload
- Triage the 1469 records: trivial / known / candidate-for-followup
- A small fraction become verified findings; the rest take templates off the candidate list
- Bottleneck moves from substrate → catalog enrichment + review

### Option B: Expand the catalog
- Implement demand-signal-driven catalog fetching for `knot.nf_class_number`, `ec.j_invariant`, etc.
- Each new invariant added to catalog refills MULTIPLE gens' reservoirs
- High-leverage but requires data sources (LMFDB, knotinfo)

### Option C: New gen families
- Design gens whose source data is itself substrate-generated (compound gens)
- Or use the c5 model — a gen whose input is OTHER gens' output
- Hardest path; uncertain payoff

The 75% cadence cut the user requested moves toward Option A.

---

## Questions for the frontier-model advisory board

These are the 10 questions where outside perspective would materially change Techne's strategy. Honest, open-ended.

1. **Reservoir model.** We observe 5+ generators that produce 100-300 unique templates on first pick at scale, then ~0 on every re-pick (even 24 fires later). Only one gen (c5, specialization-mutation) refills. Is this "fixed reservoir" model consistent with how you'd expect a combinatorial substrate to behave, or are we missing a refill mechanism? What design changes would create gens whose reservoirs auto-refill without external catalog growth?

2. **Promote-rate semantics.** 1469 records out of 375M (3.92 per million) passed the substrate's info-density filter. What metric should we use to score the **value** of an individual promoted record before any human review? Is there a self-supervised signal we're missing?

3. **Quantity vs quality threshold.** The substrate is now adding ~10 new templates per fire (down from ~140 at peak). At what point is continued generation actively harmful (corpus dilution, training-set bias toward over-represented gens)?

4. **Diversity metric for a Learner.** Suppose this corpus eventually trains a model. What's the **right metric for substrate "diversity"** from the Learner's standpoint — template count, claim_kind variety, verdict balance, invariant coverage, gen coverage, or something else? Which would best predict downstream generalization?

5. **Demand signal interpretation.** 9.1M unfulfilled requests for `knot.nf_class_number` across 28 demand logs. Is this signal we should act on (build a fetcher → populate the catalog), or is it noise from cross-product gens iterating over a sparse field? What's the principled way to distinguish "the substrate is asking for a real primitive" from "the substrate is just brute-forcing missing data"?

6. **Triage strategy for 1469 promoted records.** None have been reviewed. What's the **most efficient way** to triage them — by gen, by template, by verdict class, by record_id sample, by claim_kind? What sampling strategy maximizes information per minute of reviewer time?

7. **Cooldown calibration.** Our bandit applies 0.3x score multiplier for gens picked within 3 fires. The data shows this prevents 1-fire re-picks but allows 2-3-fire re-picks. Given the fixed-reservoir finding, should we make cooldown a HARD block? A per-gen learned cooldown? Or replace the recency model entirely with a "cumulative templates contributed" metric?

8. **Catalog expansion priority.** If we add ONE new invariant to the catalog (one of: nf_class_number, j_invariant, discriminant, alexander_polynomial_degree, hyperbolic_volume, regulator), which would create the biggest substrate-yield bump? Is there a principled prediction?

9. **End condition.** What signals should tell us to **STOP** running this substrate? Specific quantitative criteria — e.g., "templates per fire < N for K consecutive fires" or "promote-rate decline > X% week-over-week" — would help. What's a reasonable shutoff threshold for a fixed-reservoir generator system?

10. **Substrate-as-Learner-prerequisite vs substrate-as-finding-generator.** The user has framed Techne's job two ways at different times: "produce diverse substrate to train the Learner" vs "find mathematical claims worth investigating." These imply different optimization targets. Should the substrate be tuned for **training-data utility** (volume, diversity, verdict balance) or **finding-candidate yield** (rare high-info promotables)? Can both targets be served simultaneously, or is there a fundamental tradeoff?

---

## What changed during the audit (commits this conversation)

```
c069e9c1  Fire #70+71 close: heartbeat logging shipped + validated
5c287b08  Fire #72 closed: a5 = 7th explorer
165ae67c  Fire #73 closed: c2 = 8th explorer; >2000 templates
5b01786c  Fire #74 closed: saturation-regime, 0 templates
1103f3f7  Fire #75 closed: a3 dominated
79f98656  Fire #76 closed: calibration rename
ded0eb0d  Fire #77 closed: c5 confirmed explorer
b851a439  Fire #78 closed: extreme saturation
172a2bc4  Fire #79 closed: e2 = 9th explorer (63.4% rate)
bf9d2350  Fire #80 milestone closed
bca06b72  Fire #81 closed: e2 falsifies refill model
d8de7b1e  Fire #82 closed: g4 = 3rd reservoir-exhaustion instance
296d0fc0  Bandit cooldown shipped
71f120e7  Fire #83 closed: g5 = 10th explorer; e1 stall caught
22eb9636  Fire #84 closed: schema v2 migration
bda5e3d8  Fire #85 closed: cooldown live; c5 third instance
28617659  Fire #86 closed: c1 24-fire-gap pick → only 2 templates
cf540fab  Fire #87 closed: e2 3-of-3 confirms FIXED reservoir
```

44 commits total this session. Heartbeat logging, calibration-anchored naming, bandit cooldown, total_seen gating, lifetime-saturation yield score, role reclassifications.

---

*Report ends. The substrate is mature; the next phase requires consumers who read.*
