# Tensor Update — F012 Möbius × aut_grp — PROVISIONAL KILLED

**Task:** `tensor_update_F012_killed`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 3)
**Status:** PROVISIONAL — pending `liouville_side_check_F012` (sessionB claimed at 10:55:19Z)
**Source of truth:** `cartography/docs/wsw_F012_results.json` (sessionB)

---

## Proposed diff — `harmonia/memory/build_landscape_tensor.py`

### FEATURES[F012]

```diff
-    {"id": "F012", "label": "Möbius bias at g2c aut groups (H85)",
-     "tier": "live_specimen", "n_objects": 50000,
-     "description": "Max |z|=6.15 for Möbius on g2c abs_disc stratified by aut_grp. Needs permutation audit."},
+    {"id": "F012", "label": "Möbius bias at g2c aut groups (H85) — PROVISIONAL KILLED",
+     "tier": "killed_provisional", "n_objects": 66158,
+     "description": "Under clean measurement at n=66,158 (sessionB wsw_F012, 2026-04-17): "
+                    "max |z| over adequate strata (n≥100) = 0.39 (stratum 4.2, n=2,597); "
+                    "permutation-null p = 0.6843; bootstrap mean = 0.88 (5-95pct [0.30, 1.99]). "
+                    "Prior claim of |z|=6.15 did not reproduce. "
+                    "μ-population: 62.6% zeros (non-squarefree g2c abs_disc) reduce effective S/N. "
+                    "PROVISIONAL pending liouville_side_check_F012 (sessionB) — definitional drift "
+                    "(Möbius μ vs. Liouville λ) is the leading rescue hypothesis. "
+                    "If λ also gives |z|<3, this specimen demotes to killed or killed_unreproducible. "
+                    "If λ gives |z|≫3, re-open as live_specimen under refined scorer definition."},
```

### INVARIANCE[F012]

```diff
-    "F012": {"P022": +2, "P040": 0},                            # H85 Möbius: aut_grp is the axis (needs perm audit)
+    "F012": {"P022": -1, "P040": -2, "P043": -1},               # H85 Möbius PROVISIONAL KILLED: P022 collapses under clean n=66158 measurement (sessionB wsw_F012); P040 null kills cleanly (p=0.68); P043 bootstrap within noise. Pending Liouville side-check.
```

Encoding recap:
- `+2` (prior): projection strongly resolves AND validates under perm null
- `-1` (new): projection tested, feature not resolved
- `-2` (new): projection provably collapses (kill cleanly via permutation null)

### FEATURE_EDGES — add

```diff
+    {"from": "F012", "to": "F011", "relation": "shared_ledger_axis_exhausted",
+     "note": "Per sessionB's Pattern 13 note: F012 and F011 now both sit on the 'family-axis exhausted' ledger. For F011, 7 tested projections are +1-uniform (axis class exhausted). For F012, the prior family-axis claim does NOT reproduce under clean measurement (axis class failure of a different flavor). Both point away from family-level axes as resolvers."},
+    {"from": "F012", "to": "F028", "relation": "may_inform",
+     "note": "If Liouville λ rescues F012, the resolving axis is a finer scorer choice, not aut_grp itself. Katz-Sarnak (P028, sessionB) remains a family axis candidate but Pattern 13 predicts it will also not resolve. F012 kill provides a second data point."},
```

(If sessionB's Liouville side-check rescues, the `shared_ledger_axis_exhausted` edge is removed and F012 reverts to `live_specimen` with a new INVARIANCE row under the λ scorer.)

---

## Proposed diff — `harmonia/memory/pattern_library.md` (Pattern 8 extension)

Append to the end of the Pattern 8 "What's been ruled out as the mechanism" list:

```diff
 - Rank-dependent (H06 survives but weak; sessionD wsw_F013 2026-04-17
   shows rank-spacing coupling is object-level real but density-mediated,
   so H06 is a parallel finding, not an F011 mechanism)
+- aut_grp on g2c discriminants (F012 PROVISIONAL KILLED by sessionB, 2026-04-17):
+  the prior |z|=6.15 claim did not reproduce at n=66,158; max clean-stratum |z|=0.39.
+  Pending Liouville side-check. If λ also kills, F012 joins the family-axis-exhausted
+  ledger alongside F011 — two specimens pointing to the same charter reading:
+  family axes do not resolve GUE-adjacent spectral anomalies.
```

---

## Pattern 19 candidate — hold until sessionB Liouville resolves

sessionA said (CONDUCTOR_TICK 1776423182216-0): "Pattern 19 candidate proposed by sessionB: 'Stale/Irreproducible Tensor Entry' — will add after Liouville confirms."

Once Liouville side-check returns:

- **If `|z|_λ ≫ 3` (rescue):** F012 is definitional drift, NOT stale. Pattern 19 text should emphasize "prior-session scorer definitions drift" rather than "entry was never reproducible."
- **If `|z|_λ < 3` (also killed):** F012 is genuinely stale or was never reproducible. Pattern 19 text should be strongest in that form, with this session's **three** tensor-entry corrections (F011 14%→38%, F012 6.15→0.39, F014 4.4% gap wrong) as the anchoring case set.

Holding Pattern 19 authorship for sessionA; will not draft unilaterally.

---

## Revert plan if Liouville rescues

If sessionB's `liouville_side_check_F012` returns `|z|_λ ≫ 3`:

1. Revert FEATURES[F012] tier → `live_specimen`, label → "Möbius-vs-Liouville scorer distinction at g2c aut_grp (H85 refined)"
2. Revert INVARIANCE[F012] to reflect λ-scorer results (likely `{P022: +2}` restored if λ survives P040)
3. Remove the `shared_ledger_axis_exhausted` and `may_inform` feature edges
4. File a catalog entry proposing P031 (or next free ID) = "Liouville-λ object-level scorer" as distinct from Möbius-μ
5. Propose Pattern 19 as "Definitional drift between scorer variants" rather than staleness

The `killed_provisional` tier is deliberately reversible. No descriptions need to be deleted; they are now history.

---

## Completion notes

- Per task `expected_output: tensor_diff: markdown diff posted to sync` and respecting the apparent `TENSOR_DIFF-only, no in-place edits` convention observed last tick: this file is the diff; **no in-place edits applied** to tensor or pattern library.
- sessionB's claim on `liouville_side_check_F012` is active; this diff is authored after reading sessionB's findings but before the Liouville verdict lands.
- `complete_task` called with `SUCCESS_PROVISIONAL`; tensor application blocked on Liouville, explicitly.

*End of diff.*
