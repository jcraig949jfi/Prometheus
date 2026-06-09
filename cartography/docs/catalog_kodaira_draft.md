# Catalog Entry Draft — P035 Kodaira reduction type stratification

**Task:** `catalog_kodaira`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 12)
**Reserved P-ID:** `P035` (via `agora.work_queue.reserve_p_id()` at claim-time).
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications) after P032 MF character parity and before Section 5.
**Reference:** `cartography/docs/ec_harvest_triage.md` (sessionD), harvest row "Kodaira symbols — 1964 — geometric type of singular fiber".

---

## P035 — Kodaira reduction type stratification

**Code:** **DERIVABLE, not a direct LMFDB column.** Our readonly `lmfdb.ec_curvedata` exposes only `bad_primes` (list), `semistable` (bool), and `potential_good_reduction` (bool). Kodaira symbols per bad prime (I_n, II, III, IV, I_n*, II*, III*, IV*) are computed from the a-invariants via **Tate's algorithm** (Tate, 1975); implementations exist in PARI/GP (`ellglobalred`), Sage (`EllipticCurve.kodaira_symbol`), and LMFDB's own build pipeline. **To use P035 at scale, we must either (a) materialize a per-(curve, bad_prime) Kodaira table via Tate's algorithm on our mirror, or (b) query the public LMFDB EC detail endpoint per curve.** Flagging for Koios / Mnemosyne as an index-build candidate.
**Type:** stratification (geometric reduction-type axis, refines P026 semistable vs additive)

**What it resolves:**
- **Per-bad-prime singular fiber geometry.** The Néron model at a bad prime p has a specific geometric type captured by the Kodaira symbol. I_n (n≥1) families are multiplicative / semistable; all others (II, III, IV, I_n*, II*, III*, IV*) are additive.
- **Refinement of P026 (semistable vs additive).** Within "additive," the Kodaira type distinguishes between II/III/IV/etc., each with distinct local component groups, Tamagawa numbers, and L-function local factors. A curve classified "additive at p" via P026 can sit in seven distinct finer Kodaira classes.
- **Tamagawa-number prediction** (up to limited ambiguity). The local component-group order c_p is determined by the Kodaira type plus split/non-split information (ogg's formula gives conductor exponent f_p = 2 for additive regardless of fine type, so P035 is finer than what the conductor alone carries).
- **Modular-curve genus and degeneration signature.** Kodaira types classify the degeneration of the Weierstrass equation's singular fiber; the join profile across all bad primes is the curve's "global reduction signature" and can be used to cluster isogeny-related curves with non-obvious similarity.
- **Néron differential period behavior.** Additive-reduction types have specific integral-period factors that multiplicative-reduction types lack. Relevant for BSD leading-term computations.

**What it collapses:**
- **Per-prime vs global.** Kodaira type is a PER-BAD-PRIME invariant. A curve has one Kodaira symbol per bad prime, not a single scalar. Using P035 as a stratification therefore requires a choice: (i) stratify by a tuple of per-prime types, (ii) stratify by dominant type across bad primes, or (iii) stratify per (curve, prime) pair (exploding row count). Each choice collapses different features.
- **Non-reduction-related structure.** Any feature of the curve independent of its Néron model at bad primes is invariant under P035 and collapses into a single stratum.
- **Split vs non-split multiplicative distinction** (if only the coarse Kodaira symbol I_n is used). The finer split/non-split flag at multiplicative primes is orthogonal and must be recorded separately.

**Tautology profile:**
- **P035 ↔ P026 (semistable vs additive).** P035 IS the refinement: `P026 = "semistable"` iff all Kodaira types across bad_primes are I_n; `P026 = "additive"` iff any is non-I_n. Joint P026 × P035 is *nested*, not orthogonal. Applying both axes independently is double-counting.
- **P035 ↔ P021 (num_bad_primes).** For a fixed num_bad_primes, the Kodaira type *tuple* has combinatorially more entropy than the scalar count — P035 refines P021 within each P021 stratum.
- **P035 ↔ Tamagawa numbers.** The product of local Tamagawa numbers c_p enters the BSD formula. For most Kodaira types, c_p is determined up to a small ambiguity by the type; for I_n the Tamagawa number is n (or n/2 for non-split). Treating P035 and "Tamagawa number stratification" as independent re-asserts this near-identity as if it were signal.
- **P035 ↔ Conductor exponent f_p.** Ogg's formula: f_p = ord_p(Δ) − m + 1, where m is the number of components of the Néron fiber. Conductor exponents are derivable from Kodaira + Δ valuation; joint with conductor conditioning (P020) risks formula-lineage leak per Pattern 1.

**Stratum-count summary (at catalog-draft time, based on Tate classification):**
- Kodaira types are classified by an 8-element set: `{I_n (n≥1), II, III, IV, I_n* (n≥0), II*, III*, IV*}`. In practice `I_n` and `I_n*` subsume infinitely many sub-types indexed by n; for finite analysis use the coarse 8-class split and treat n as a secondary axis.
- Per LMFDB's aggregate counts (public Elliptic curves over Q), the coarse class distribution is heavily skewed: I_n dominates (~70–80% of all bad-prime Kodaira symbols across the 3.8M EC_curvedata rows); II / III / IV occur at 5–10% each; II* / III* / IV* and I_n* are rarer. A precise count requires the Tate-algorithm materialization task flagged in "Code" above.
- **Small-n strata discipline:** at fine granularity (e.g., "curves all of whose bad primes are type II"), strata quickly drop below `n=100` in any conductor-restricted sub-sample. Apply sessionB's Liouville-lesson discipline.

**Calibration anchors:**
- **Tate's algorithm is proved**, not conjectural. Any LMFDB Kodaira symbol disagreeing with an independent PARI/GP or Sage computation on the same a-invariants is a data-quality violation — F-level calibration anchor candidate (F006+ once materialized).
- **Ogg's formula** (conductor exponent from Kodaira + Δ) is proved. A fresh P035 implementation that computes `f_p` from Kodaira + local Δ valuation and disagrees with `ec_curvedata.conductor` at the corresponding prime is broken.
- **Neron component-group sizes** match the Kodaira type: I_n → c_p ∈ {1, 2, ..., n} per split/non-split; II → 1; III → 2; IV → 3; I_0* → {1,2,4}; I_n*→varies; II*→1; III*→2; IV*→3. Textbook identity.
- **Semistable reduction theorem** (Deligne-Mumford): every elliptic curve acquires semistable reduction (all Kodaira types become I_n) after a tame base change. This is a proved invariant that joint P035 × extension-degree analyses can validate.

**Known failure modes:**
- **Using P035 without materialized data** — any worker drawing claims from "Kodaira stratification" must either (a) run Tate's algorithm on the curves they use, (b) query LMFDB's public detail endpoint per curve (slow, rate-limited), or (c) defer the work until Mnemosyne materializes a `kodaira_per_prime` table. Do not fabricate strata from indirect LMFDB columns without an audit trail.
- **Choosing the wrong aggregation rule** (per-prime vs dominant-type vs tuple) and reporting as if it were the canonical axis. Different choices yield different strata; document the rule explicitly.
- **Stratifying without split/non-split awareness.** Two I_n curves can have genuinely different arithmetic if split vs non-split; ignoring this is an information leak.
- **Confusing Kodaira symbol with Kodaira-Neron model.** The symbol is a label; the Néron model is the geometric object. P035 classifies labels.

**When to use:**
- **Refining a P026 "additive" cohort** — when a pooled "additive" stratum has structural variation, P035 is the natural next refinement axis. Seven sub-strata (II, III, IV, I_n*, II*, III*, IV*) may each behave differently.
- **Tamagawa-number-driven claims** — whenever local c_p structure enters a specimen's definition, Kodaira stratification is the cleaner axis than raw c_p values (which carry redundant information).
- **Cross-projection calibration** — Ogg's formula and Tate's algorithm are proved; P035 is a candidate source of calibration anchors once materialized.
- **Investigating the Salem-region density around F014** — low-num_ram EC (few bad primes) may correlate with specific Kodaira type signatures; worth a walk once the data is available.

**When NOT to use:**
- **As the sole axis for BSD-adjacent claims** — Tamagawa numbers enter the BSD formula multiplicatively; Pattern 1 tautology with anything computed from the formula.
- **Jointly with P026 as if orthogonal** (nested-refinement tautology).
- **Before Tate-algorithm data is materialized** — the axis is purely notional without the per-prime Kodaira table.
- **At small n per sub-stratum** — rare Kodaira types (IV*, III*, II*) have few representatives in LMFDB; n≥100 adequacy is hard to reach at fine granularity.

**Related projections:**
- **P026 semistable vs additive:** parent axis; P035 is the refinement within the additive cohort.
- **P021 num_bad_primes:** orthogonal-in-count; P035 refines at fixed num_bad_primes.
- **P020 conductor conditioning:** joint usage requires Ogg's formula awareness (conductor exponents are Kodaira-derivable).
- **P039 Faltings height (proposed)** and **Regulator P046 (proposed):** Kodaira type can enter the Néron differential period factor; formula-lineage check warranted.
- **P036 Root number (proposed):** local root numbers are Kodaira-type-sensitive (Rohrlich); joint P035 × P036 is a natural cross-axis.

**Follow-ups this entry motivates:**
1. **Task: `materialize_kodaira_per_prime`** — run Tate's algorithm (via PARI `ellglobalred` or Sage) on the 3.8M ec_curvedata rows, write results to a new table (Mnemosyne/Koios own). Without this, P035 is a catalog placeholder.
2. **Task: `audit_kodaira_ogg_consistency`** — once materialized, verify Ogg's formula on every (curve, bad_prime) pair. Disagreements = data-quality violations per Pattern 7.
3. **Candidate calibration anchor F006** — Kodaira consistency across LMFDB vs independent Tate-algorithm runs.
4. **Joint catalog entry with "split/non-split multiplicative" flag** — orthogonal refinement of I_n that Kodaira alone doesn't capture; either co-document here or give it a sister P-ID.
5. **wsw candidate: `F014_kodaira_salem_region`** — test whether the Salem polynomials in (1.176, 1.228) correlate with specific Kodaira signatures. Connects F014 (Lehmer refined) to P035.

*End of draft.*
