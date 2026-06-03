# Techne Substrate Fire Log — 2026-06-03

## Calibration v3 — independent-null falsification of the v2 corpus sweep

**Context on entry.** Theseus bandit loop paused at Fire #236 (92 consecutive
0-promoted). GPT-5 2026-05-30 review forced the calibration pivot: prove the
substrate recovers known structure at better-than-null rates before resuming.
F2 content-aware filter calibrated on synthetic controls (v0 Murasugi, v1
EC-torsion) and shipped observation-only (`theseus/scoring/content_aware_promote.py`).
v2 corpus sweep then reported ~18.5% group-level contrast on real data while
flagging (caveats #2/#3) that most was probably selection bias. **The v2 claim
had not yet been falsified.** Per calibration-discipline mandate, the
independent null runs before the claim escapes upward.

**Probe built.** `theseus/scripts/calibration_v3_nonmutated.py`. A record is
mutation-derived iff it carries a `parent_record_id`; excluding them isolates
independently-sampled records. Added an optional `generator_id` filter to
isolate a1 (pure uniform `rng.choice`). Smoke at 200K before the 30M full scan
(smoke-before-full-scale rule). Matched v2's exact sorted-file / oldest-N window
for comparability.

**Result (30M-record window).**
- v2 analyzed 1,068 groups (≥50 all-record). Only **96** have ≥50 independently-
  sampled records → ~91% of v2's group diversity is mutation-generated K-variants.
- v2's named strongest residual (`knot/trace_field_class abs_diff_le_0 ec/torsion`)
  is **100% mutation-derived** — collapses to 0 non-mutated records.
- All-gen non-mutated: 61/96 promote, contrast up to 0.27 — but `sub_hold` 22–40%
  vs `null` often 0.00%, mechanically impossible under uniform sampling. Signal
  comes from non-a1 selection/transform generators.
- **a1-only (uniform, the unbiased baseline): 0/96 promote, max contrast 0.023,
  `sub_hold ≈ null` everywhere.** a1 has 0 records with a parent.

**Verdict.** No cross-catalog knot×EC coupling under unbiased sampling. v2's
apparent corpus signal was selection bias in two layers (mutation inheritance +
non-a1 generator construction), both stripped by v3. F2's calibration is
genuine: recovers planted (v0/v1), reports ~zero on the honest real null. The
92-consecutive-0-promoted streak is **correct refusal to promote artifacts**,
not a bounded-menu wall in this region.

Full verdict: `pivot/calibration_v3_VERDICT_2026-06-03.md`.

**Owed next probe (filed, not yet run).** Per-generator `sub_hold` vs null on the
96 groups — name which non-a1, non-mutation generators inject the Layer-2 bias
(targeting vs raw-vs-transformed value mismatch, v2 caveat #2), and decide
whether their SHADOW verdicts belong in the content-aware corpus at all.

**Doctrine:** calibration-discipline (independent null before claim) ✓;
counter-baseline discriminator (a1 uniform null) ✓; permutation/independent-null
mandatory ✓; assume-wrong / kills-are-the-output ✓; HARD-5 no-bridge-story ✓.
