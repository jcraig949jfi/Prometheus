# Tensor Update — F015 sign-uniform, magnitude non-monotone

**Task:** `tensor_update_F015_sign_not_magnitude`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 7)
**Source of truth:** `cartography/docs/wsw_F015_results.json` (sessionD, tick 5)
**Tier:** `live_specimen` (unchanged — real object-level coupling)
**Convention:** TENSOR_DIFF only (no in-place edits).

---

## Proposed diff — `harmonia/memory/build_landscape_tensor.py`

### FEATURES[F015]

```diff
-    {"id": "F015", "label": "Szpiro monotone decrease at fixed bad-prime count (Ergon)",
-     "tier": "live_specimen", "n_objects": None,
-     "description": "abc Szpiro ratio decreases monotonically with conductor when stratified by num_bad_primes. "
-                    "Coordinate system revelation: bad_primes is the axis that resolves this."},
+    {"id": "F015", "label": "Szpiro vs conductor — sign-uniform, magnitude non-monotone in k",
+     "tier": "live_specimen", "n_objects": 30000,
+     "description": "Under clean measurement (sessionD wsw_F015, 2026-04-17): szpiro-vs-log(conductor) slope "
+                    "is sign-uniformly-negative within every bad-prime stratum k ∈ {1..6} "
+                    "(P042 permutation-null z-scores -6.9 to -22.7, p=0 all). Object-level real. "
+                    "BUT the monotone-in-k claim (Ergon 2026-04-16) does NOT hold: per-k slopes are "
+                    "-0.128 / -0.448 / -0.488 / -0.356 / -0.476 / -0.459, with k=4 breaking the smooth trend. "
+                    "P052 decontamination: 88% of pooled slope -0.597 is k-mediated confound; only ~12% residual. "
+                    "Within-conductor bins (P020), szpiro slope vs k is POSITIVE (+0.44 to +0.61) — the two "
+                    "stratified views are self-consistent but opposite-direction. "
+                    "Pattern 19 variant: the Ergon 'monotone' claim partially reproduces (sign yes, magnitude no)."},
```

### INVARIANCE[F015]

```diff
-    "F015": {"P021": +2, "P001": -1},                           # abc rescue: bad_primes is the axis
+    "F015": {"P021": +2, "P020": +1, "P042": +2, "P051": 0, "P052": -1, "P001": -1},   # sign-uniform within k (P042 z=-6.9..-22.7); P051 N/A (scalar); P052 shows 88% k-mediated
```

Encoding recap for the new cells:
- `P020: +1` — within-conductor-bin, szpiro-vs-k slope is positive and consistent (+0.44 to +0.61 at adequate bins).
- `P042: +2` — within-stratum feature permutation null gives z=-6.9 to -22.7 in every adequate k-stratum.
- `P051: 0` — N(T) unfolding is a zero-spacing concept, NOT_APPLICABLE to scalar Szpiro; flagged 0 rather than forcing a mismatched test.
- `P052: -1` — prime decontamination shows 88% of pooled slope is k-confound; the residual 12% is the real structural content.

### FEATURE_EDGES — add

```diff
+    {"from": "F015", "to": "F011", "relation": "stratification_reveals_pooled_artifact",
+     "note": "Both F015 and F011 show: the POOLED view hides or distorts structure; STRATIFIED views reveal it. F011: pooled 40% deficit → post-unfolding 38% with uniform visibility across 7 projections. F015: pooled slope -0.597 → only 12% residual after k-decontamination. Common shape: single-axis pooled summaries understate the axis-class enumeration."},
+    {"from": "F015", "to": "F013", "relation": "stratification_reveals_pooled_artifact",
+     "note": "Parallel to F011 edge. F013: raw slope -0.00467 → ~74% collapse under N(T) unfolding. F015: pooled slope -0.597 → ~88% collapse under k-decontamination. Both cases: naive pooled magnitude reported a larger effect than the stratified/decontaminated residual. Candidate Pattern 20 anchor set: F011 + F013 + F015."},
```

---

## Proposed diff — `harmonia/memory/pattern_library.md` (Pattern 8 side-note + Pattern 20 seed)

### Pattern 8 side-observation (extend the bad-prime trend note)

The existing Pattern 8 already flags the P021 per-stratum variance monotone
(0.166 at k=1 → 0.088 at k=6) as a candidate separate specimen. Extend:

```diff
+**Cross-specimen note (added 2026-04-17 via F015 tick 7):** F015's per-k
+szpiro-vs-logN slopes (k=1..6 at -0.128/-0.448/-0.488/-0.356/-0.476/-0.459)
+and F011's P021 per-stratum variance trend (0.166 → 0.088) both show
+bad-prime count carrying coherent within-stratum structure. The axis itself
+is *not* the resolver of F011's uniform deficit (which is invariant under
+P021 pooling), but it IS a coordinate the residuals organize around. Worth
+its own catalog entry as a coordinate *class* (bad-prime-count-as-axis)
+distinct from the P021 stratification projection.
```

### Pattern 20 seed (brief; full draft deferred to `pattern_20_stratification_reveals` task)

This update motivates but does not author Pattern 20. Proposed skeleton for
the Pattern 20 task claimer:

> **Pattern 20 — Stratification Reveals Pooled Artifact.** When a pooled summary
> of an effect has a larger magnitude than the effect surviving a disciplined
> stratification or decontamination, the pool was reporting confounder-mediation
> in the guise of signal. The right number is the within-stratum residual, not
> the pooled slope. Canonical cases: F011 pooled→uniform 38%, F013 raw→unfolded
> 74% collapse, F015 pooled→decontaminated 88% collapse. Discipline: always
> report pooled-and-residual side-by-side; flag the confound-mediation fraction
> explicitly.

Do NOT merge this skeleton directly — the Pattern 20 task has authorship
responsibility for the canonical phrasing.

---

## signals.specimens insert (per TRACKING MANDATE)

This TENSOR_DIFF's specimen row will be written alongside the task
`complete_task` call. Key fields:

- `claim`: "F015 tensor update — sign-uniform magnitude-nonmonotone"
- `status`: `refined`
- `interest`: 0.55
- `data_provenance.source_task`: `tensor_update_F015_sign_not_magnitude`
- `data_provenance.feature_id`: `F015`
- `data_provenance.proposed_invariance`: `{P021:+2, P020:+1, P042:+2, P051:0, P052:-1, P001:-1}`
- `data_provenance.edges_added`: 2 (F015→F011, F015→F013)
- `data_provenance.applied_by_sessionA`: pending

---

## Completion notes

- No in-place edits to `build_landscape_tensor.py` or `pattern_library.md`.
- Pattern 20 authorship held for the `pattern_20_stratification_reveals` task claimer.
- `complete_task` called with `SUCCESS`; journal entry logged; specimen row inserted.

*End of diff.*
