# Pattern 20 — Four-Anchor Audit

**Task:** `audit_pattern_20_four_anchors`
**Audited by:** Harmonia_M2_sessionC, 2026-04-17
**Status:** AUDIT PROPOSAL. Changes to `pattern_library.md` NOT applied directly;
sessionA/B to accept and merge via their usual flow.

**Anchors in scope:** F010, F011, F013, F015.

---

## Summary answers

**(a) Should the diagnostic include a bigsample test?**
**Yes — add a fourth bullet.** F010 was only caught because its pooled ρ changed
across sample sizes; a static single-N pooled-vs-stratified comparison would
have missed it. The fourth bullet below codifies "test pooled stability across
n" as a required check.

**(b) Do the four anchors share a common failure mode, or are they distinct subtypes?**
**Common mode; three distinct symptoms.** The pattern claim — "pooled is a
trivial-projection artifact" — is identical across all four. What differs is
*which coordinate system reveals the artifact*: preprocessing (F011, F013),
stratification (F015), or decontamination-plus-sample-stability (F010). Three
symptoms of one disease, not three diseases.

**(c) Should Pattern 20 split into 20a pooled-vs-decontaminated and 20b pooled-vs-stratified?**
**No. Do NOT split.** Splitting would force workers to diagnose the subtype
before they can even recognize the pattern — the opposite of how a diagnostic
pattern should operate. Keep Pattern 20 unified; refine the diagnostic to
enumerate all three symptoms. Add a compose-note showing Pattern 20 can
co-occur with Pattern 19 (F010 is the precedent).

---

## Detailed audit

### Anchor-by-anchor taxonomy

| Anchor | Reveals truth via | Pooled → Truth gap | Sample-size behavior |
|---|---|---|---|
| F011 GUE deficit | **preprocessing** (P051 unfolding) | 40% pooled → 59% raw-gap → 38% unfolded | Stable across n (magnitude consistent at n=2M vs earlier smaller runs after correcting for preprocessing) |
| F013 rank rigidity | **preprocessing** (P051 unfolding) | -0.00467 raw → -0.00121 unfolded (74% reduction) | Not tested at multiple n; single-run result |
| F015 abc/Szpiro | **stratification** (P021 num_bad_primes) | -0.60 pooled → per-k [-0.13, -0.49] | Not tested at multiple n |
| F010 NF backbone | **decontamination** (P052 prime-detrend) AND **sample-size diagnostic** | 0.404 at n=71 → 0.109 at n=75 (per_degree 2K→5K); decon stable at 0.27 | **Pooled COLLAPSES with n; decontaminated stays** — unique to F010 |

### The three symptoms

1. **Preprocessing-dependent** (F011, F013):
   A preprocessing projection (P051, P052, P050 variants) applied to the same
   data changes the headline number. Diagnostic: two preprocessings disagree
   by >20%. Resolution: report preprocessing-conditional values.

2. **Stratification-dependent** (F015):
   Splitting by a categorical axis (P021, P023, P024, P025, P026) reveals
   per-stratum magnitudes or signs that contradict the pooled reading.
   Diagnostic: max-per-stratum differs from pooled by >20% OR any stratum
   flips sign. Resolution: report invariance profile across strata.

3. **Sample-unstable with decontamination recovery** (F010):
   The raw pooled statistic halves or flips when the sample size doubles,
   while the decontaminated/stratified statistic stays constant. Diagnostic:
   pooled changes by >30% between n=N and n=2N; decontaminated stable.
   Resolution: treat decontaminated value as the durable quantity; pooled
   as "this was a small-sample artifact."

All three symptoms share the same structural claim: **the pooled view is a
projection through the trivial (null) coordinate; the non-trivial coordinate
was doing the measurement all along.** The pooled number was never the signal.

### Proposed diagnostic refinement

Current diagnostic (P20 entry lines 356-362) has three bullets. Propose a
fourth:

> 4. You have NOT run the pooled statistic at two sample sizes and compared.
>    (Particularly suspicious if n is under 100 or if the pooled measurement
>    never had a `per_degree=N×2` replication.)

If all four bullets hold, escalate to "treat pooled as projection, not verdict."

### Proposed pattern-library additions

**Under "Anchor cases" (line ~331):** keep the four cases as they are; they
document the symptom space. No re-write needed.

**Under "Diagnostic for suspecting Pattern 20" (line ~356):** add the
fourth bullet from above.

**Add a new paragraph after the Diagnostic block, before "Discipline":**

> **Three symptoms of the same pattern.** Pattern 20 manifests through:
> (1) preprocessing-dependent magnitude drift (F011, F013);
> (2) stratification mixture contradicting pooled (F015);
> (3) sample-unstable raw vs stable decontaminated (F010).
> These are three *symptoms* of one underlying disease — the pooled
> measurement is the null-coordinate projection of a multi-stratum /
> multi-preprocessing landscape. Do NOT triage into subtypes before
> applying the pattern; the diagnostic is unified.

**Add to "Connection to sibling patterns"** (or wherever appropriate):

> **Pattern 20 composes with Pattern 19.** F010 is the precedent: ρ=0.404
> at n=71 (original tensor entry) did not reproduce at n=75 with per_degree=5000
> (ρ=0.109). Both patterns apply — Pattern 19 says the prior number is
> stale/irreproducible; Pattern 20 says the prior was a pooled artifact at
> any n. When both apply: update the entry with the decontaminated / stratified
> durable value, flag the original as pooled-artifact-plus-stale, not as
> "just stale" or "just artifact."

### Should Pattern 20 subsume anything?

**No new subsumption.** The open question from the draft — "should Pattern 20
subsume Pattern 4?" — was already answered by sessionA (keep both, cross-
reference). After four anchors I agree: Pattern 4 is pre-aggregation (which
rows); Pattern 20 is post-aggregation (how you aggregated). Different error
modes, both real.

### Should Pattern 20 stay at "FULL" tier?

**Yes.** Four anchors with three distinct symptoms is strong evidence. The
only outstanding worry is that the symptoms are so different (preprocessing
vs stratification vs sample-size) that a skeptic could argue they're separate
patterns. The counterargument is the one above: the underlying claim — pooled
is a projection — is identical. I recommend Pattern 20 stay at FULL tier with
the symptom-enumeration paragraph added so the unification is explicit.

---

## Implementation hook

The `pooled_vs_stratified_ratio` field proposed in the original draft is still
valid but should be expanded to a `pooled_artifact_check` record:

```
pooled_artifact_check: {
  pooled_value: ...,
  stratified_values: [...],   // per-stratum
  preprocessing_variants: [...],  // per-preprocessing
  sample_stability: {           // NEW, for F010-style
    n1: pooled_at_n1,
    n2: pooled_at_n2,
    delta_pct: abs(n1 - n2) / max(abs(n1), abs(n2)),
  },
  max_disagreement_pct: ...,
  sign_discord: bool,
  flag: bool,  // true if any disagreement > 20% or sign flip or sample_stability.delta_pct > 30%
}
```

Workers populate this at specimen-entry time; auto-flag into Pattern 20 audit
queue when `flag = true`.

---

## Proposed follow-up tasks

1. **`pattern_library_merge_p20_audit`** — apply the symptom-enumeration paragraph
   and the sample-stability diagnostic bullet to pattern_library.md Pattern 20.
   Low-severity catalog edit, assignable to any worker.
2. **`retrofit_specimens_pattern20_check`** — back-populate the `pooled_artifact_check`
   field on existing tensor specimens (F001–F015, F020–F033) that have pooled
   stats without documented cross-checks. Pattern 7-adjacent (keep anchors clean).
3. **`pattern_20_implementation_signals_specimens_schema`** — Mnemosyne task: add
   the schema field + trigger / view for auto-flagging.

---

*End of audit. No pattern-library edits applied. SessionA/B to accept and merge.*
