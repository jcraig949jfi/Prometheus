# Aporia Session Journal — 2026-04-22

## Session: The Mechanism (c) Characterization + H101 Kill

### Mode
Continuous 6-min polling loop with team (Agora, M1/Skullport). Charon + Ergon + Techne active for most of session; Kairos/Harmonia/Mnemosyne offline. James semi-autonomous.

---

## Major Outcomes

### 1. F011 "14% GUE deficit" void — DEMYSTIFIED to quantitative law

My April-16 void list entry ("EC zeros more regular than RMT predicts; hidden operator suppresses randomness") went through a full characterization cycle today:

- **Initial framing (tick 8):** Ergon's finite-N matched-simulation argument suggested the deficit was a sample-depth artifact. I moved it to RESOLVED.
- **Reversal (tick 13):** Ergon ran against properly MATCHED GUE null (local-4-gap normalization). EC sits 20–33% below matched baseline at n=200K with z = −48 to −103. Deficit deepens gap1 → gap4. I RE-OPENED the void.
- **Mechanism investigation (ticks 18–24):**
  - Conductor-memory rejected (Ergon 40-cell study, confirmed by Charon at BSD-1646 via Katz-Sarnak slope). Compression attenuates at −2%/log(N).
  - Isogeny-invariance kills direct Sha→gap causality.
  - CM/non-CM split at n=2134 shows CM ~2x deeper compression.
  - Torsion split shows rare torsion (5, 6, 8) ~2.5x deeper than trivial — second mechanism-(c) channel.
  - V-CM-scaling (my proposal): Charon finds r = +0.71 at n=11, r = +0.79 at n=12, **r = +0.82 on Heegner-only (h=1 fixed)**. Prediction function `gap1_deficit = 19.15·log|D| + 6.0`, R²=0.68.
  - h(K) disambiguation: |D| IS the driving variable; h(K) is a proxy for non-Heegner.
  - CM × torsion cross-stratification (Charon): **gap1 SATURATES** (sub-additive by 8pp), **gap4 ADDITIVE** (predicted = observed to within 1pp). CM-alone has FLAT gap-index gradient; the gradient is a torsion-channel signature.

**Current characterization:**
```
gap1_deficit ≈ max(CM_log|D|_channel, torsion_rarity_channel) − conductor_atten + noise   [SATURATING]
gap4_deficit ≈ CM_log|D|_channel + torsion_rarity_channel − conductor_atten + noise       [ADDITIVE]
```

Awaiting Ergon's closure regression (per-curve joint fit on 200K) as the verdict-grade confirmation.

### 2. Lehmer bound — CLASSICAL STATEMENT CONFIRMED ON LMFDB NF CORPUS

Charon's exhaustive scan of 6.7M deg-8-14 NF defining polynomials: min non-cyclotomic Mahler measure saturates at **1.17628 exactly** at `10.2.1332031009.1` (Lehmer's own NF). Smyth bound saturated at deg 9 (x^15-x^10+1). Below-Lehmer count = cyclotomic noise only.

Scope: NF-defining-polynomial subfamily (not all integer polys). Classical Lehmer not proved, but not refuted and now empirically hit.

F014:P040 tensor cell promotable to +2.

### 3. H101 Salem-NF-as-knot-trace-field — KILLED

My void prediction (small-Salem NFs should appear as knot trace fields via McMullen K3 bridge) was tested by Ergon via reverse-substitution: evaluate each of the 5 Salem polynomials at each of the 12,963 hyperbolic knot shape field roots. **245,280 evaluations, 0 hits at 10^-40 tolerance.**

Scope: shape-field not iTrF, 3-13 crossing census. Extension possible but H101 as stated is CLEANLY KILLED. The K3-Salem-to-3-manifold bridge does not populate this corpus.

### 4. LMFDB deg-14 Mossinghoff Gap — CONFIRMED REAL

Charon grepped his exhaustive deg-14 scan for any Mahler measure in [1.20, 1.23]. **Zero entries.** Mossinghoff's published small-Salem deg-14 specimens (1.20002, 1.20261, 1.20515) are OUTSIDE LMFDB's |disc|-cutoff. Queued to Mnemosyne for targeted catalog ingestion.

### 5. Lehmer's NF polredabs canonical form — SELF-CORRECTION

My polredabs caveat (polredabs destroys Mahler measure) was PARTIALLY WRONG. Verified empirically: Lehmer's NF is at label `10.2.1332031009.1`; LMFDB stores `Lehmer(-x)` (x → -x substitution), which preserves M(f) exactly. Sample size (10K out of 2.8M deg-10 NFs = 0.35% coverage) was the real issue in Charon's first scan, not polredabs.

Retained: polredabs CAN change Mahler measure in general (α → α+k shifts); specific transformations (sign flip, cyclotomic permutations) preserve it. Case-by-case.

---

## Retractions / Kills (mine or re-framed)

| Claim | Verdict | Why |
|-------|---------|-----|
| "14% GUE deficit is finite-N resolved" (tick 7) | RETRACTED (tick 13) | Matched null shows real deficit; finite-N was wrong normalization |
| "Polredabs always destroys Mahler measure" (tick 10) | PARTIAL RETRACT (tick 11) | x→-x preserves M; other polredabs-equivalent polys may differ |
| "Ergon two-channel 40.7% residual" (tick 5) | RETRACTED (tick 6) | Misread — 40.7% is Sha>1 fraction, not residual |
| "Gradient reversal for CM" (tick 21, built on n=18) | RETRACTED (tick 22) | Ergon n=2134 shows CM gradient is positive, not inverted |
| "|D|-scaling adds via log_lp" | NULL (tick 28) | F-test F=2.17, not significant at n=12 |
| H101 Salem-NF-trace-field bridge | KILLED (tick 26) | 0/245K hits |

---

## Methodological Lessons

1. **Null-choice is everything.** Three reframings of F011 gap-deficit in one session, all due to null/normalization mismatch. Proposed PATTERN_NULL_CONSTRAINT_MISMATCH precondition for Kairos catalog.

2. **Small-n direction claims are traps.** My "|D|-scaling + Heegner deepest" on n=18 was wrong. Required resolution: flag n<50 findings with "pending n≥200 confirmation" before building downstream hypotheses.

3. **PATTERN_KILL_UNDER_CONSTRAINED proposed:** require 2/3 independent tests (alt-null, cross-dataset, gradient-AND-absolute-level) before any F-cell is flipped negative. Two kill-then-unkill cycles in one session justify the precondition.

4. **Scope specification matters.** "Lehmer holds on LMFDB NF subfamily" ≠ "Lehmer holds on all integer polys". "H101 killed at 3-13 crossing shape-field scope" ≠ "K3-topology bridge is empty everywhere". Every result carries its scope.

---

## Void List Updates

Added:
- V-CM-scaling (confirmed): CM compression ~ 19·log|D|, Heegner-only fit R²=0.68.
- Two-regime compression (confirmed): saturation at gap1, additive at gap4.
- LMFDB deg-14 Mossinghoff coverage gap: confirmed, awaiting targeted ingestion.

Demystified (not killed — refined to quantitative law):
- 14% GUE deficit (April-16 void) → "rank-0 EC local-gap-variance compression, Euler-product-simplification driven, multi-channel (CM + torsion), Katz-Sarnak attenuated".

Killed:
- H101 Salem-NF-as-knot-trace-field (scope: shape-field, 3-13 crossings).

Still open:
- Mechanism (c) closure test (Ergon running joint regression).
- H15 NF tower termination (H15 partial at cn≤5 trivial; requires per-sample subprocess isolation for proper run at cn≥4).
- H27 Yakaboylu Artin root-number bias (DATA-BLOCKED; no Artin L-funcs in LMFDB).

---

## By The Numbers

- 16+ Agora main-stream posts
- 3 reframing-then-refinement cycles on F011
- 1 clean H101 kill
- 1 Lehmer exhaustive confirmation (6.7M polys)
- 3 new Techne tools requested + delivered (HCF, faltings_height guard, knot_shape_field_batch)
- 5 Techne tools shipped this session total (HCF, class_number, regulator, faltings_height, selmer_rank, tropical_rank + BSD chain hardening)

---

## Artifacts

| File | Purpose |
|------|---------|
| `aporia/docs/identity_join_strategy_spec.md` | V4 spectral-gap fill proposal (knot silence interpretation) |
| `aporia/docs/h15_partial_summary.md` | H15 partial run summary + Golod-Shafarevich candidate |
| `aporia/mathematics/paradigm_gap_v2.json` | Differentiated EIG ranking (v2 over broken v1) |
| `aporia/mathematics/v1_triangle_deficits.json` | V1 constraint-triangle results |
| `aporia/mathematics/h15_first_look.json` | H15 first-look at cn=2 (trivial closure) |
| `aporia/mathematics/h15_results.json` | H15 partial at cn≤5 (5 specimens, incl. 2.0.2296.1 candidate long-tower) |
| `roles/Aporia/loop_state.json` | Continuous loop state (last_read_ids, tick notes, open items) |

---

## Late-Session Addendum (ticks 29–33)

### Closure regression cascade
- Ergon's cell-level closure regression: gap1 R²=0.67, gap4 R²=0.55 (PARTIAL).
- Per-CM-disc dummies: +11.6pp / +14.0pp to 0.79 / 0.69 (F=4.59, p=0.005 significant).
- Charon's shape taxonomy (FLAT/GROWING/SHRINKING/MILD) on 12 CM discs.
- **V-GAMMA-SIXTH-ROOTS sub-void discovered** (mine): Q(√-3) non-maximal orders (-12, -27) UNIQUELY invert the gap-index gradient. Pre-registered prediction.
- Ergon's RCF decomposition: `cm_disc = order_conductor² × fund_disc`. Two principled CM invariants replace per-disc dummies at same R² with fewer params: gap1 R²=0.78, gap4 R²=0.68.
- **V-GAMMA-SIXTH-ROOTS CONFIRMED by cross-check.** Within-D_K, order conductor matters ONLY in Q(√-3) — the sixth-roots family. Non-maximality in Q(i) or Q(√-7) doesn't flip shape.
- Techne TOOL_CM_ORDER_DATA shipped (REQ-023 closed) as post-session infrastructure.

### Final F011 state
```
Start of session : R² = 0.15 (conductor only, wrong null)
After (cm, |D|, tor, logN)           : 0.67 / 0.55
After per-disc dummies               : 0.79 / 0.69  (over-parameterized)
After RCF decomp (D_K, c)            : 0.78 / 0.68  (principled, parsimonious)
Residual                             : 22% / 32%
```

### Sub-voids CHARACTERIZED (not killed, not open — structurally explained)
- Per-disc gap profile: STRUCTURED by (D_K, order_conductor) per Ergon's decomposition.
- V-GAMMA-SIXTH-ROOTS: CONFIRMED as Q(√-3)-family specificity.

### Paper-track
F011 is publishable as-is. Charon's 30-45 min methods/tables draft-ready on James signal.
Working title: "Sato-Tate saturation of L-function zero statistics in CM and rare-torsion subfamilies"

### Final-state artifact count
- `roles/Aporia/SESSION_JOURNAL_20260422.md` — this file
- `charon/CHARON_SESSION_2026-04-22.md` — Charon session
- `roles/Ergon/SESSION_JOURNAL_20260422.md` — Ergon session
- `charon/data/cm_disc_gap_profile.md` — shape taxonomy catalog
- `ergon/results/closure_test_combined.json` + `closure_test_rcf.json` — regression outputs

---

*Aporia — semi-autonomous void detector. Three-agent loop (Charon execute, Ergon regress, Aporia void-frame) produced publishable-grade characterization in ~3 hours continuous work. Prometheus science-team model at target.*
*2026-04-22, Aporia. Session final state captured.*

---

## Far-Late-Session Addendum (ticks 34–60)

After the "final state" addendum above at tick ~33, James extended the loop and the team continued. What followed was a SECOND major arc that reframed F011 FIVE MORE TIMES (tick 34 through tick 60), ending with a 4-axis paper-ready manuscript.

### The second arc: from mechanism characterization to Katz-Sarnak-grounded universality paper

**Tick 40 — Ergon rank-stratification (Seed 4):** gap-index gradient is RANK-INVARIANT for ranks 0, 1, 2 (near-identical); rank 3+ shows different pattern. Gap4 is the RANK-INVARIANT STRUCTURAL CONSTANT (~33% across ranks). Gap1 at ranks 0-2 is edge-artifact prone.

**Tick 41 — Ergon nbp mega-finding:** Spearman(nbp, deficit) = 1.000 across non-CM 150K. num_bad_primes is the clean non-CM analog of |D|. Closure gap1 R² jumps from 0.50 to 0.73 with nbp added. But gap4 R² barely moves (0.48). **Gap1 = EULER-ARITHMETIC regime, gap4 = SPECTRAL-ASYMPTOTIC regime.**

**Tick 42 — Charon selection-bias cross-check:** nbp Spearman ≈ 0 at BSD-1646 (vs +1.0 at 150K random). PATTERN_SELECTION_BIAS emerges. Scope matrix drafted.

**Tick 45 — Ergon Seed 2 (gap-k scan) lands MAJOR REFRAME:** 24-gap normalization on 49K rank-0 EC shows k=1-3 as EXCESS variance (+5 to +9%), not deficit; k=4-24 monotone DEFICIT deepening to +51% at k=24. Under 4-gap norm the "gap1 compression" we characterized was NORMALIZATION ARTIFACT. New meta-pattern: PATTERN_NORMALIZATION_SIGN_FLIP.

**Tick 46 — Charon cross-checks bulk robust:** k=24 random +50.9% vs curated +52.1% (within 1.2pp). Edge excess amplified by BSD selection. Bulk is TRULY STRUCTURAL.

**Tick 47 — My Katz-Sarnak theory prompt (Seed 11):** Proposed F011 may be Katz-Sarnak O(even) universality artifact rather than GUE anomaly. EC rank-0 even family IS O+(2N).

**Tick 48 — Charon literature check on Seed 11:** CONFIRMS EC rank-0 even = O+(even) = SO(2N) per ILS 2000, Young 2005, Katz-Sarnak 1999. Edge statistics DIFFER; bulk is asymptotically universal.

**Tick 49 — CM 24-gap landed (first CM data point):** CM FLIPS EDGE SIGN vs non-CM under GUE null. Bulk converges within 3pp at k=24. Universality-class diagnostic at edge, universal bulk.

**Tick 50 — Two decisive tests:**
  (1) Ergon nbp-bulk-k survival test: rho=1.000 at k=8, 20 (deep bulk). Mechanism (c) IS real at bulk, not edge artifact.
  (2) Charon O+(2N=80) sim REFUTES Seed 11: EC has MORE variance than O+ at edge (-48.6% vs O+, vs -7% vs GUE). BOTH edge AND bulk are beyond-both-GUE-AND-O+ deviations. My Seed 11 "edge = universality" claim RETRACTED.

**Tick 51 — CM sign flip reframed:** under GUE null, yes; under O+ null, BOTH CM and non-CM show EXCESS (magnitudes differ). Only GUE as midpoint makes "flip" appear.

**Tick 52 — Axis 1 Katz-Sarnak 1-level density CONFIRMED:** rank-0 unfolded z_1 = 1.586 (O+), rank-1 = 2.730 (O-), ratio 1.72, z=+249. TEXTBOOK signature. Paper now has 3 axes.

**Tick 53 — Universality triangle completes:** Ergon G2C (USp(4)) 24-gap: edge k=1 -77.6% (10x deeper than O+), bulk k=24 +46.4%. THREE families: non-CM EC O+ (+51%), CM EC U(1)-ish (+48%), G2C USp(4) (+46%). **Bulk deficit is CROSS-FAMILY UNIVERSAL within 5pp.** Paper lead result identified.

**Tick 54 — Axis 1 literature-locked:** Charon pins ILS 2000 / Young 2005 / KS 1999. Ratio 1.72 matches theory within 0.2%. Axis 1 is PUBLISHABLE CONFIRMATION. 4-family 1-level density ruler: CM 0.88x / EC non-CM 1.00x / EC rank-1 1.73x / G2C 4.67x. Clean ordinal hierarchy.

**Tick 55 — G2C nbp SIGN FLIPS:** Ergon finds Spearman(nbp, deficit) = -0.9 at G2C (opposite +1.0 at EC). Mechanism (c) is 2-LAYER: ORDINAL universal + DIRECTIONAL symmetry-class-specific.

**Tick 56 — Cross-family nbp panel:** O+ rank-0 +1.0, O- rank-1 +1.0 SAME SIGN, G2C USp(4) -0.9. CM inconclusive at n=2K. Sign pattern = Orthogonal(+) vs Symplectic(−). Ergon proposes theoretical connection to Katz-Sarnak 2-point correction signs.

**Tick 57 — Axis 3b LITERATURE-LOCKED:** Charon pins Katz-Sarnak 1999 Sec 3.3 — 2-point correction is positive for O+/O-, negative for USp. SIGN MATCH PERFECT. Axis 3b is "per-curve resolution of family-averaged Katz-Sarnak 2-point correction, nbp-ordinally manifested." Theoretically grounded.

**Tick 60 — Session-closing TL;DR filed** at `roles/Aporia/TLDR_20260422.md`.

### Final 4-axis paper structure

| Axis | Content | Status |
|------|---------|--------|
| 1 — 1-level density ratio 1.72 | Classical Katz-Sarnak confirm (ILS/Young/KS) | CONFIRMED |
| 2 — Edge k=1 magnitudes beyond family-correct null | NEW: non-CM -49%, CM -29%, G2C -220+% vs O+/Sp | NEW FINDING |
| 3a — Universal bulk deficit +46-51% at k=24 cross-family | NEW: beyond BOTH GUE and family-correct classical RMT | NEW FINDING |
| 3b — nbp sign Orthogonal(+)/Symplectic(−) matches KS 2-point correction sign | Classical KS 1999 Sec 3.3 confirm | CONFIRMED |

**Paper title:** "A Universal Bulk Rigidity in L-function Zero Spacings Beyond Katz-Sarnak Universality"

### Seven proposed Kairos meta-patterns (tick 58 deliverable)

Consolidated at `aporia/docs/kairos_proposed_patterns_20260422.md`:
- PATTERN_NULL_CONSTRAINT_MISMATCH (003)
- PATTERN_KILL_UNDER_CONSTRAINED (004)
- PATTERN_PREDICTION_LEVEL_MISMATCH (005)
- PATTERN_SELECTION_BIAS (006)
- PATTERN_NORMALIZATION_SIGN_FLIP (007)
- PATTERN_LITERATURE_REFRAME (008)
- PATTERN_MEASUREMENT_CHANNEL (009)

Each with canonical example from today's session.

### Session arc in one line

15 structural reframes + 2 theoretical lock-ins + 7 meta-patterns in ~7 hours continuous work, converted stale "14% GUE deficit" void-list entry into 4-axis paper-ready publication with cross-family universality finding.

### Wind-down options Ergon offered (deferred to next session if not yet run)

- CM nbp re-pool at coarser bins (completes Table 2 for CM; tests my pre-reg + Orthogonal prediction)
- Dim=1 MF proper Modularity check
- gap_k for k>25 (saturation check)
- CM n≥10K ingest (Mnemosyne) for decisive classification

### Session end state

Paper-ready. Team standing down. 5-artifact package delivered. Loop continues per James's 7-min instruction as idle watchdog.

---

*Aporia, 2026-04-22, session complete. 15 reframes. 4 axes. 1 paper.*
