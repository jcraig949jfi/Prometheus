# Catalog Entry Draft — P039 Galois ℓ-adic image stratification

**Task:** `catalog_galois_l_image`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 17)
**Reserved P-ID:** `P039` (via `agora.work_queue.reserve_p_id()` at claim-time).
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications) after P037 Sato-Tate group and before Section 5.
**Reference:** `cartography/docs/ec_harvest_triage.md` (sessionD), harvest row "Galois representation image (mod ℓ) — 1972 — Serre openness and exceptional primes".

---

## P039 — Galois ℓ-adic image stratification

**Code:** Several LMFDB columns on `ec_curvedata` encode aspects of the Galois image:
- `nonmax_primes` (text, list of ℓ where image is non-maximal),
- `nonmax_rad` (radical of the nonmax-prime list),
- `elladic_images` (per-ℓ subgroup labels in `GL_2(Z_ℓ)`),
- `modell_images` (per-ℓ mod-ℓ subgroup labels),
- `adelic_level`, `adelic_index`, `adelic_genus` (adelic-image invariants).

Use `nonmax_primes = '[]'` as the boolean-level filter for "fully surjective image at every prime"; use `elladic_images`/`modell_images` for per-prime fine classification; use `adelic_index` for the global adelic refinement.
**Type:** stratification (Galois-representation image axis; carries Serre-openness and exceptional-prime structure)

**What it resolves:**
- **Serre's Open Image Theorem** (Serre 1972): for a non-CM elliptic curve over Q, the image of `ρ_ℓ: Gal(Q̄/Q) → GL_2(Z_ℓ)` is open for every ℓ, and **surjective** for all but finitely many ℓ (the *exceptional primes*, listed in `nonmax_primes`). `P039` is the direct stratification of that classification.
- **Exceptional-prime structure.** The finite set of primes where the image drops below full `GL_2(Z_ℓ)` encodes the arithmetic of the specific curve (existence of rational torsion, isogenies of prescribed degree, rational cyclic subgroups). The union `nonmax_primes ∪ {primes dividing torsion order}` is bounded in terms of the conductor (Masser-Wustholz-type bounds).
- **CM vs non-CM Galois-image signature.** For CM elliptic curves, the image of `ρ_ℓ` lies in the normalizer of a (non-split) Cartan — it is *never* the full `GL_2(Z_ℓ)`. The interpretation of `nonmax_primes` for CM rows requires care: LMFDB flags "max" relative to the *expected* image (Cartan for CM, `GL_2` for non-CM), so empirical CM rows can appear with `nonmax_primes = '[]'` despite being strictly below full `GL_2`. Verify the per-CM convention before using as a CM indicator.
- **Congruence-subgroup structure.** `adelic_level` is the level of the congruence subgroup `Γ ≤ GL_2(Ẑ)` capturing the adelic image; `adelic_index` is the `[GL_2(Ẑ) : Γ]` index; `adelic_genus` is the genus of the modular curve corresponding to `Γ`. Joint `adelic_level × adelic_index × adelic_genus` is a finer projection than `nonmax_primes` alone.
- **Isogeny-class signature.** Curves sharing an isogeny class typically share `adelic_index` up to the specific isogeny structure; `P039` cross-references with isogeny structure and torsion via shared lattice constraints.

**What it collapses:**
- **Within-image fine structure.** Two curves with identical `elladic_images` but different conductors, ranks, or torsion-structures collapse in `P039`. Stratify jointly with `P020` conductor, `P023` rank, or `P024` torsion for finer resolution.
- **Per-prime-independent information.** If the question is whether the image at *every* prime is full `GL_2(Z_ℓ)`, the `nonmax_primes = '[]'` boolean collapses the per-prime detail. Use `elladic_images` per-ℓ entries when the specific exceptional-prime identity matters.
- **CM-specific versus non-CM cells.** Interpretation of `nonmax_primes` differs between the two regimes; pooling without stratifying by `P025 cm` first can silently mix two distinct "maximal" conventions (see warning above).

**Tautology profile:**
- **P039 ↔ P024 torsion.** Rational ℓ-torsion forces the mod-ℓ image to stabilize a line, which makes the image non-surjective on `GL_2(F_ℓ)`. Concretely: any curve with rational 2-torsion has `2 ∈ nonmax_primes`; any curve with rational 3-torsion has `3 ∈ nonmax_primes`. These are theorems, not findings. Joint `P039 × P024` analyses must factor out the torsion-induced non-maximality before claiming structural signal.
- **P039 ↔ P025 CM.** CM curves' Galois image is contained in the normalizer of a Cartan (abelian up to index 2), never full `GL_2(Z_ℓ)`. The LMFDB "max relative to expected image" convention makes the `P039 × P025` joint have forbidden-cell-like structure (CM rows with "fully surjective" label mean "fully fills Cartan," not "fills GL_2"). Similar to `P033 Is_Even × P031 Frobenius-Schur` asymmetric tautology.
- **P039 ↔ Isogeny degrees.** The image is non-maximal at ℓ exactly when the curve has a rational cyclic subgroup of order divisible by ℓ (modulo subtleties). So `nonmax_primes` is nearly equivalent to the set of primes dividing `isogeny_degrees`. Joint `P039 × isogeny_degrees` double-counts this identity.
- **Adelic-invariant bundle (`adelic_level, adelic_index, adelic_genus`).** These three are not independent — for a specific congruence subgroup `Γ`, they are joint invariants computable from `Γ` alone. Using all three independently is triple-counting the same underlying subgroup.

**Stratum-count summary (live `ec_curvedata` queries, 2026-04-17):**
- **Fully surjective at every prime (`nonmax_primes = '[]'`):** 2,217,470 rows (58.0%)
- **Has at least one exceptional prime:** 1,606,902 rows (42.0%)
- Total: 3,824,372 rows.
- Top `adelic_level` values: 6 (n=26,853), 120 (n=16,615), 840 (n=16,466), 24 (n=14,270), 168 (n=12,862), 8 (n=12,541). The heavy populations at `adelic_level ∈ {6, 24, 120}` reflect rational 2-, 3-, and 2×3-torsion populations (the torsion-forced non-maximality at small primes).
- Top `adelic_index` values: 2 (n=2,223,342 — dominant!), 12 (n=836,392), 48 (n=411,166), 16 (n=195,058), 192 (n=48,164). The `adelic_index = 2` cluster is the "almost-surjective with a single global twist" cohort — this is 58% of all EC and correlates heavily with `nonmax_primes = '[]'`.
- CM counts on surjective-image subset: 2,211,532 (non-CM) + ~5,938 (CM across various discriminants) have empty `nonmax_primes`. The ~6K CM rows in this count illustrate the LMFDB convention issue described above.

**Small-n strata discipline:**
- At the `adelic_index`-level: the top two values cover 80 %+ of the dataset; beyond `adelic_index = 192` counts drop rapidly. `n ≥ 100` is easy at the top and hard below; apply sessionB's Liouville discipline to any rare-index claim.
- At the `elladic_images` level: per-ℓ subgroup labels have long tails (many rare labels at small ℓ, e.g., 2Cs / 2B / 2Cn / 3B / etc.). For rare labels, explicit `n` reporting is mandatory.
- At the **exceptional-prime level**, the classical Mazur-Kenku-Momose-Parent list bounds which primes can be exceptional: the set of primes ℓ where some non-CM curve over Q has non-surjective mod-ℓ image is contained in `{2, 3, 5, 7, 11, 13, 17, 37}` (Mazur 1978 for ℓ ≤ 7, later extensions for ℓ ≤ 37). Any row with `ℓ ∈ nonmax_primes` for `ℓ > 37` and cm=0 is a data-integrity violation.

**Calibration anchors:**
- **Serre's Open Image Theorem** (1972): for non-CM EC over Q, the image is open in `GL_2(Z_ℓ)` for every ℓ and surjective for almost all ℓ. Proved. Any LMFDB row claiming non-CM + all primes non-maximal is a violation.
- **Mazur-Kenku-Momose-Parent exceptional-prime bound**: non-CM mod-ℓ image is surjective for ℓ > 37 (sharper for ℓ > 13 except known exceptional cases at ℓ = 17, 37). LMFDB rows with cm=0 and `nonmax_primes` containing any ℓ > 37 must be audited.
- **Rational torsion → mod-ℓ non-maximality for ℓ | torsion order**: proved / textbook. Cross-check: for every EC row, every prime dividing `torsion` should appear in `nonmax_primes`. Candidate data-quality anchor.
- **Adelic genus ≥ 0** (trivial but easy to test): the `adelic_genus` column must be a non-negative integer.

**Known failure modes:**
- **CM convention ambiguity.** As noted above, `nonmax_primes` for CM rows uses a CM-specific "max" convention. Any claim about "Galois image maximality" on CM rows without distinguishing CM-max (full Cartan) from absolute-max (full `GL_2`) is ambiguous.
- **Torsion-induced non-maximality reported as signal.** Any non-CM + non-trivial-torsion curve has predictably non-surjective mod-ℓ images at primes dividing the torsion order. A "signal" claim of the form "curves with non-empty `nonmax_primes` have property X" is vulnerable to this tautology with `P024 torsion`.
- **Isogeny class vs individual curve.** Curves in the same isogeny class share most Galois-image data but not all — specifically, rational cyclic subgroups can be created/destroyed under isogeny. Using `P039` at the isogeny-class level vs the individual-curve level gives different partitions; don't conflate.
- **Pooled analysis of `adelic_index`.** The dominant `adelic_index = 2` cluster (58%) will carry any pooled signal unless explicitly stratified; this is a textbook Pattern 4 sampling-frame trap with `P039` hidden inside the pool.

**When to use:**
- **Sanity-check isogeny-adjacent claims** — the `nonmax_primes` list is the cleanest "is this curve Galois-generic or not" flag we have.
- **Refinement of CM stratification** — `P039` distinguishes different CM discriminants' Galois-image signatures; `P025` alone only gives the CM discriminant.
- **Selmer-group / p-descent calibration** — for primes in `nonmax_primes`, the mod-p Selmer analysis is non-standard (image is non-surjective); P039 filters out the generic cases where Selmer-rank bounds apply unconditionally.
- **Galois-representation-feature cross-specimen tests** — any cross-specimen involving `elladic_images` labels should stratify by P039.

**When NOT to use:**
- **For CM rows without disambiguating the "max" convention** — report ambiguous.
- **Jointly with P024 without accounting for the torsion-induced-non-maximality tautology** — you'll double-count the torsion axis.
- **Pooled across `adelic_index` classes without reporting the dominant `index = 2` share** — Pattern 4 trap.
- **For ℓ > 37 on non-CM rows without data-integrity audit** — Mazur-Kenku bound says this shouldn't happen; treat as data-quality alarm before feature claim.

**Related projections:**
- **P024 torsion:** partial tautology via rational-torsion → mod-ℓ non-maximality.
- **P025 CM:** interpretation-conflating aliasing (CM convention vs non-CM convention).
- **P031 Frobenius-Schur / P033 Is_Even:** Galois-image-determines-Sato-Tate on Artin reps, which cross-references to `P037`. `P039` is the direct LMFDB-column companion to these derived axes.
- **P037 Sato-Tate group:** for EC, `P039` determines `P037` (image type determines the Lie group the Frobenius traces live in). Joint use is nested.
- **Isogeny-class projections (future P045 sister):** `P039` and isogeny structure share the cyclic-subgroup information; design carefully.

**Follow-ups this entry motivates:**
1. `audit_nonmax_primes_vs_torsion` — verify every prime dividing `torsion` appears in `nonmax_primes` across all 3.82M EC. Candidate calibration anchor (F009 or next free).
2. `audit_mazur_kenku_bound` — flag any non-CM row with `ℓ > 37` in `nonmax_primes` as a data-quality alarm.
3. `clarify_cm_max_convention` — write a short doc on LMFDB's "max" convention for CM rows and add it to the catalog or to the Section 8 tautology table.
4. `wsw_F010_P039` — F010 NF backbone resolved under Artin `Is_Even` (P033); does the EC partner resolve under `P039` Galois image? If CM curves (image in Cartan) dominate the coupling, this is a trivial aliasing — if non-CM with specific `adelic_index` drive it, that would be structural.
5. `catalog_adelic_invariants` — if `adelic_level × adelic_index × adelic_genus` is worth its own sister entry, file it; otherwise note the triple as a sub-projection of `P039`.

*End of draft.*
