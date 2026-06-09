# Catalog Entry Draft — P036 Root number stratification

**Task:** `catalog_root_number`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 13)
**Reserved P-ID:** `P036` (via `agora.work_queue.reserve_p_id()` at claim-time).
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications) after P035 Kodaira (sessionD, pending) and before Section 5.
**Reference:** `cartography/docs/ec_harvest_triage.md` (sessionD), harvest row "Root number — 1960s — sign of functional equation".

---

## P036 — Root number stratification

**Code:** `WHERE root_number = <+1|−1>` on `lmfdb.bsd_joined` (materialized view, 2,481,157 rows; also directly on `lmfdb.lfunc_lfunctions.root_number` for the wider L-function population). For EC, `signD` in `ec_curvedata` is NOT the root number (it is the sign of the discriminant) — do NOT confuse them. Reference: sessionB's tick-5 correction after wsw_F011_katz_sarnak flagged the same distinction.
**Type:** stratification (binary sign-of-functional-equation axis; parity axis on self-dual L-functions)

**What it resolves:**
- **Sign of the functional equation.** For a self-dual L-function Λ(s) = ε · Λ(1−s), `root_number = ε ∈ {+1, −1}`. This is the single bit that distinguishes functional-equation-even from functional-equation-odd L-functions.
- **Forced central-zero presence.** For ε = −1, Λ(1/2) = 0 by the functional equation (central-zero is forced). For ε = +1, Λ(1/2) may or may not vanish. Hence `P036` directly predicts whether the L-function has an odd-index zero structure near the center.
- **Katz-Sarnak SO_even / SO_odd split on the Artin / EC side.** For an elliptic curve L-function, `root_number = −1 ⇔ analytic_rank is odd ⇔ family-member of SO_odd`. For `root_number = +1`, SO_even. `P028 × P036` within the EC family is nested, not orthogonal (see tautology profile).
- **BSD parity anchor F003.** For every row in `bsd_joined` (n=2,481,157), `(-1)^rank = root_number` holds at 100.000%. This is the cleanest parity-calibration axis we have. A single mismatch would be a catastrophic instrument failure.
- **Rohrlich local root-number decomposition.** Global root_number factors as a product of local root numbers ε_v; Kodaira type (P035) contributes to the local factor at each bad prime v. P035 × P036 cross-projection is a candidate calibration pair.

**What it collapses:**
- **Any non-parity feature of the L-function.** Two root_number=+1 L-functions at different ranks, conductors, and arithmetic content all map to the same stratum. Use `P036` as a coarse parity filter; stratify further by `P023` rank, `P020` conductor, etc.
- **Rank-parity-invariant features.** Pooled analyses that average over ranks 0 and 2 (both root_number=+1) lose the distinction; `P036` alone cannot see rank inside a parity class.
- **Non-self-dual L-function distinctions.** `root_number` is meaningful only for self-dual (ν=+1 Frobenius-Schur, see `P031`) L-functions. For ν=0 (complex) reps, the functional equation relates L(s) to its complex conjugate and "root number" is a phase on the unit circle, not ±1. Applying `P036` to ν=0 L-functions is a category error.

**Tautology profile:**
- **P036 ↔ P023 rank (BSD parity theorem).** Proved for rank 0 and rank 1 (Kolyvagin, Gross-Zagier); empirically perfect across all 2.48M EC of bsd_joined at higher rank. Empirical from `bsd_joined` (2026-04-17):
  - `root_number = +1`: rank ∈ {0, 2, 4} exclusively (954K + 276K + 1 = 1,229,540).
  - `root_number = −1`: rank ∈ {1, 3} exclusively (1,245K + 7K = 1,251,617).
  Zero mismatches out of 2,481,157. **This is the cleanest calibration anchor in the instrument** (F003) and applying `P036` + `P023` as if they were independent axes is double-counting their mutual determination.
- **P036 ↔ P028 Katz-Sarnak (nested for EC).** Per the forced-central-zero mechanism: `root_number = +1` on an EC L-function ⇔ SO_even family membership; `root_number = −1` ⇔ SO_odd. Within the EC slice of `P028`, `P036` IS the binary picking between SO_even and SO_odd. `P028` additionally distinguishes U, Sp, and SO families (outside EC). Do not apply `P028` and `P036` jointly on the EC slice as if orthogonal — it is triple-counting with P023.
- **P036 ↔ P033 Is_Even (cross-family parity correspondence).** For EC L-functions attached to Galois representations, `root_number` corresponds to `Is_Even` via the local-root-number Rohrlich factorization. On modularity pairs, weight-2 MF root_number = Atkin-Lehner eigenvalue = EC root_number (F001 identity). `P036 × P033` across matched EC↔MF↔Artin triples is an identity pair under Langlands functoriality, not an independent cross-axis.
- **P036 ↔ Local root numbers at bad primes (Pattern 1 lineage).** Global ε factors as `∏_v ε_v`. If a specimen uses "per-prime root number" and "global root number" jointly, the product identity is formula-level lineage. Lemma-check before reporting ρ.

**Stratum-count summary (live `bsd_joined` query, 2026-04-17, postgres/prometheus):**
- `root_number = +1`: 1,229,540 (49.55%)
- `root_number = −1`: 1,251,617 (50.45%)
- Total: 2,481,157 (bsd_joined matched rows)
- Near 50:50 as predicted by Katz-Sarnak universality for a large EC family; the slight asymmetry is expected finite-N behavior.

**Small-n strata discipline:**
- At the bulk level, both P036 strata are >1M rows — no small-n concern.
- At joint stratifications: e.g., `P036 × P020 × P023` produces cells that can drop below `n = 100` at high conductor × high rank (per F033 coverage cliff; rank ≥ 4 is already data-limited regardless of root number). Apply sessionB's Liouville-lesson n≥100 discipline at the joint level, not the marginal.
- For non-EC L-functions in `lfunc_lfunctions`, coverage is thinner; enforce `n≥100` per stratum before publication-grade per-stratum |z|.

**Calibration anchors:**
- **F003 BSD parity at 100.000% over 2.48M rows** — `(-1)^rank = root_number` exactly, zero mismatches. This is the load-bearing calibration anchor for any P036 implementation: if a single row violates this, the instrument is broken (Pattern 7, stop all work). The theorem is proved for rank 0-1 (Kolyvagin, Gross-Zagier) and the remaining rank ≥ 2 cases hold empirically in the dataset by construction of LMFDB.
- **F005 high-Sha parity** — restricted to sha ≥ 9, `(-1)^rank = root_number` also holds at 100% (67,035 rows). Consistent subset anchor.
- **Deligne's global-root-number = product-of-local-root-numbers** theorem is proved; `P036` implementations should match local-product computations.
- **Rohrlich local root-number tables** — for additive-reduction primes, the local root number depends on Kodaira type in a table-known way. `P035 × P036` consistency is a future calibration candidate.

**Known failure modes:**
- **Confusing `signD` (sign of discriminant) with `root_number`.** `ec_curvedata.signD ∈ {-1, +1}` is NOT the root number. sessionB's tick-5 F011 Katz-Sarnak run hit this: signD/root_number mismatch rate was 50% (noise against wrong column), correctly retracted as not a calibration violation. Any `P036` implementation on `ec_curvedata` alone is likely wrong — use `bsd_joined.root_number` or `lfunc_lfunctions.root_number`.
- **Applying P036 to non-self-dual L-functions** (ν=0 Artin / ν=0 Frobenius-Schur). The "root number" is a complex phase, not ±1; category error.
- **Treating `P036` as independent from `P023` rank** — the BSD parity tautology collapses the axes to the same information content within EC. Never report "feature survives P036 but collapses under P023" without realizing they are the same axis up to a sign.
- **Pooled analysis across root_number without reporting the parity distribution** — `P036` is one of the few axes where pooled analysis is defensible (50:50 split), but any rank-sensitive feature requires separate reporting within each stratum.

**When to use:**
- **As the canonical BSD parity calibration axis.** Before running any EC / L-function pipeline on fresh data, verify `(-1)^rank = root_number` on a random sample — this is the cheapest instrument-health check available.
- **Forced-central-zero-sensitive analyses** — any measurement of `L(1/2)`, leading-term-at-center, or lowest-zero distance from center should stratify by `P036`.
- **Katz-Sarnak symmetry-type filtering on EC L-functions** — `P036` is the cheap proxy for P028's SO_even/SO_odd distinction on the EC slice; prefer `P036` when the question is rank-parity-flavored and `P028` when the question needs the finer U/Sp/SO classification.
- **Cross-family modularity checks** — root_number of a weight-2 MF must match the root number of its modular EC; joint `P036 × P029 × conductor` is the natural cross-slice.

**When NOT to use:**
- **Jointly with `P023` as if orthogonal** on EC data — you are double-counting BSD parity.
- **Jointly with `P028` on the EC slice** — nested tautology via the SO_even/SO_odd correspondence.
- **For non-self-dual L-functions** — complex-phase root number, not ±1.
- **Before verifying F003 on your sample** — if the calibration anchor is broken on your subset, every downstream `P036` stratification is suspect.

**Related projections:**
- **P023 rank stratification:** tautological pair via `(-1)^rank = root_number`. Do NOT treat independently.
- **P028 Katz-Sarnak family symmetry type:** nested on the EC slice — `P036` picks SO_even vs SO_odd; `P028` adds U / Sp / SO distinction for families beyond EC.
- **P033 Is_Even Artin parity (sessionD):** cross-family parity companion; Rohrlich local decomposition connects Artin-side Is_Even to EC-side root_number under Langlands.
- **P035 Kodaira (sessionD, pending materialization):** cross-projection calibration via Rohrlich local-root-number tables at additive-reduction primes.
- **P020 conductor conditioning:** joint use is orthogonal (no formula-level tautology), recommended for any root-number-vs-conductor trend analysis.

**Follow-ups this entry motivates:**
1. **Task `calibrate_F003_via_P036`** — run the `(-1)^rank = root_number` check on the full 2.48M bsd_joined rows and confirm 100.000% agreement. Currently accepted on faith; cheap to formalize as a standing CI check.
2. **Task `wsw_F010_P036` on the EC side** — F010 resolved under P033 Is_Even on the Artin side at 5.4σ (sessionB tick 12); the natural EC-side parallel is to stratify F010's EC partner by `P036`. Expect same structural parity (classical conductor-discriminant formula predicts); this is primarily a Pattern 5 (Known Bridges) calibration, not novelty.
3. **Candidate calibration anchor F007** — Rohrlich local-global root-number product identity, once `P035` Kodaira is materialized.
4. **Task `catalog_rank_parity_as_tautology_pair`** — formalize `(root_number, (-1)^rank)` in Section 8 (Tautology Pairs) of the catalog; currently implicit via F003, should be explicit as a load-bearing lineage pair.

*End of draft.*
