# T#19 — Cactus rank

## Brief summary

T#19 is the rank-zoo gap problem for the scheme-theoretic invariant cactus rank `cr(T)`. The clean inequality chain is `cr(T) ≤ R̲(T) ≤ R(T)` with each inequality strict on explicit witnesses. Cactus rank is the minimal length of a 0-dim apolar (Gorenstein) scheme — the same invariant Iarrobino–Kanev (1999) called *scheme length* before Buczyńska–Buczyński renamed it after the *cactus variety* `κ_r`. The defining problem: classify when each inequality is strict, characterize the geometric obstruction, and bound the gap. T#19 is the scheme-theoretic substrate of the entire P29 border-apolarity paradigm and the structural reason for the **cactus barrier** of `6m − 4` on determinantal lower bounds for border rank of `m × m × m` tensors (Buczyński, Feb 2026, arXiv:2602.11309). Cactus rank fits the substrate as a clean Tier-B subtype `CactusRankWitness` extending T#34's `BorderRankWitness` with an explicit `apolar_witness` that does NOT require a degeneration sequence.

## Flagged findings

1. **PATTERN_RANK_PARITY_LEAK is the textbook leakage test for this entry.** Five-to-six distinct rank notions (`R, R̲, sr, cr̲, cr, differential_length`) share the lexical "rank." Cactus rank is most-confused with border rank because both involve "limits/closures." They are NOT equal: `cr` is scheme-theoretic (any 0-dim apolar scheme), `R̲` is topological-closure, `sr` (smoothable rank) sits between. The chain `cr ≤ R̲ ≤ sr ≤ R` is strict on explicit cubics (Buczyński–Jelisiejew–Mella wild forms).

2. **The "cactus barrier" finding (Buczyński, Feb 2026, arXiv:2602.11309) makes T#19 a PRIMARY tensor-frontier obstruction, not a rank-zoo curiosity.** All determinantal (rank-method) equations vanish on the *cactus* variety `κ_r` — strictly larger than `σ_r`. For `m × m × m`, `κ_r` fills the ambient space once `r ≥ 6m − 4`, so determinantal methods CANNOT prove a border-rank lower bound exceeding `6m − 4`. T#19 is the scheme-theoretic ceiling on the entire flattening-based attack on `ω` (T#1).

3. **Border cactus rank `cr̲` is a fifth rank invariant, freshly formalized in Buczyńska–Buczyński Jan 2026 (arXiv:2601.19558).** "Border cactus decomposition" extends border apolarity from secant to cactus varieties via Cox-ring multihomogeneous ideals on toric ambients. The substrate must track at least five rank coordinates per symmetric tensor: `R, R̲, sr, cr, cr̲`. Charts collapsing them into one "rank" field violate HARD-5.

4. **Substrate primitive: `CactusRankWitness` as a clean Tier-B subtype of `BorderRankWitness` (T#34).** No degeneration sequence required — only a saturated apolar 0-dim scheme. Strictly *easier* to construct than the full `BorderRankWitness` and strictly *less* informative (lower bound on `R̲`, not exact decision). Useful implication: `cr(T) > r ⇒ R̲(T) > r` is a one-line entailment once both witnesses register; converse fails — encoded as `closure_status` flag.

5. **PATTERN_BASE_RATE_NEGLECT trap (Bernardi–Ranestad cubic-form bound):** for *general* forms, `R = R̲ = sr = cr` — the rank-zoo collapses on the generic full-measure stratum. Strict inequalities live entirely on the lower-dimensional defective stratum (T#26). A generic-point spot-check would falsely report no gap. Substrate must require a non-generic / wild-form / minimal-border-rank witness for any gap claim.

6. **PATTERN_VRAM_TRUNCATION_ARTIFACT for Macaulay2-based apolar enumeration.** B-invariant-ideal enumeration (Buczyńska–Buczyński Duke 2021 Algorithm) blows up combinatorially with multigraded Hilbert function. Implementations truncate to small `r` and small format; substrate must record truncation depth on every `apolar_witness` to avoid silent false-NO. Bernardi–Reig Fité (Aug 2025, arXiv:2508.15062) gives the current best refinement.

7. **Two proposed new tickets:**
   - `T-ST-T19-001` `CactusRankWitness` probe with PATTERN_RANK_PARITY_LEAK calibration (must distinguish all five rank coordinates).
   - `T-ST-T19-002` Cactus-barrier audit: any determinantal `BorderRankWitness` claiming a lower bound `> 6m − 4` for `m × m × m` is auto-flagged for re-verification via P29 apolarity (NOT P31 flattenings).

## 1. Problem statement

For homogeneous degree-`d` form `F ∈ S^d V`, with apolar ideal `F^⊥ = {θ : θ · F = 0}` under the contraction action:

```
cr(F) := min { length(X) : X ⊂ ℙ(V) a 0-dim subscheme with I(X) ⊆ F^⊥ }
```

Equivalently, `cr(F)` is the minimum length of a 0-dim Gorenstein subscheme apolar to `F`. (Iarrobino–Kanev 1999 = *scheme length*; Buczyńska–Buczyński 2010 renamed.)

Inequality chain:

```
differential_length(F) ≤ cr(F) ≤ sr(F) ≤ R(F)
                        cr(F) ≤ R̲(F) ≤ sr(F) ≤ R(F)
```

T#19 problem: classify schemes that achieve cactus rank but not border rank; characterize when `R̲(F) = cr(F)`; bound `R̲ − cr` on tensors and on symmetric forms. Equivalent: when does `κ_r ⊋ σ_r`? When is the strict containment detectable by determinantal equations?

## 2. Status & bounds

| Result | Authors | Year |
|---|---|---|
| Cactus rank as "scheme length" | Iarrobino, Kanev | 1999 |
| Cactus rank renamed; cactus variety formalized | Buczyńska, Buczyński | 2010 |
| `cr ≤ 2n+2` for general cubic in `n+1` vars (`n ≥ 8`) | Bernardi, Ranestad | 2011/2013 |
| `cr` of reducible cubic = `n+2` while `R ≥ 2n` | Bernardi, Ranestad | 2013 |
| Smoothable vs border rank gap; wild forms | Buczyński, Jelisiejew, Mella | 2018 |
| Vector bundles give equations of cactus varieties | Galązka | 2017 |
| Border apolarity + multigraded Hilbert scheme | Buczyńska, Buczyński | 2021 (Duke 170, arXiv:1910.01944) |
| Distinguishing secant from cactus (`κ_14` for Veronese) | Galązka, Mańdziuk, Rupniewski | 2023 (FoCM, arXiv:2007.16203) |
| Cactus scheme = catalecticant minor zero scheme (open subset) | Buczyński, Keneshlou | 2024 (arXiv:2410.21908) |
| Symmetric powers smoothability + rank-chain collapse | Flavi, Jelisiejew, Michałek | 2025 (IMRN) |
| Border cactus decompositions (apolarity for cactus) | Buczyńska, Buczyński | Jan 2026 (arXiv:2601.19558) |
| Cactus barrier = `6m − 4` for `m³` border-rank determinantal LBs | Buczyński | Feb 2026 (arXiv:2602.11309) |
| Local cactus rank algorithm refinement | Bernardi, Reig Fité | Aug 2025 (arXiv:2508.15062) |

**Open frontier (substrate-relevant):**
1. Tight gap `R̲(T) − cr(T)` for matrix-mult tensor `M⟨n⟩` and `det_n` — no known nontrivial separation.
2. Whether `cr(T) = R̲(T)` for *minimal* border rank (T#20-adjacent).
3. Defining equations of cactus varieties beyond Veronese (Segre / Segre-Veronese / Grassmannian). Galązka–Mańdziuk–Rupniewski 2023 handled Veronese `κ_14`; non-Veronese mostly open.
4. Sharp classification of `κ_r ∖ σ_r`. For Veronese, the extra component consists of polynomials divisible by `(d-3)`-rd power of a linear form (Galązka–Mańdziuk–Rupniewski).
5. Cactus rank of `M⟨n⟩` — open even at `n = 3`. The `R̲(M⟨3⟩) ≥ 17` lower bound (Conner–Harper–Landsberg 2023) goes via P29 apolarity; implied cactus-rank lower bound is automatic but not sharp.
6. Computational complexity of deciding `T ∈ κ_r` — sister to T#34 with distinct algorithmic profile (apolar-scheme search vs degeneration sequence).

## 3. Literature

**Founding (1999–2013):** Iarrobino–Kanev, *Power Sums, Gorenstein Algebras, and Determinantal Loci*, LNM 1721 (1999) — Lemma 5.17 introduces *scheme length*. Buczyńska–Buczyński 2010 — cactus variety formalism. Bernardi–Ranestad, J. Symbolic Comput. 50 (2013), arXiv:1110.2197 — `cr ≤ 2n+2` for general cubic.

**Apolarity machinery (2017–2021):** Galązka, Adv. Math. 320 (2017) — vector bundle equations. Buczyński–Jelisiejew–Mella 2018 — wild forms; explicit cubic in 5 variables with `R̲=5, sr=6`. Buczyńska–Buczyński, Duke Math. J. 170 (2021), arXiv:1910.01944 — THE foundational P29 paper.

**Distinguishing secant from cactus (2020–2024):** Galązka–Mańdziuk–Rupniewski, FoCM (2023), arXiv:2007.16203 — `κ_14 ∖ σ_14` for Veronese; algorithmic decision for `d ≥ 6, n ≥ 6`. Buczyński–Keneshlou, arXiv:2410.21908 (Oct 2024) — cactus scheme equals catalecticant-minor zero scheme on dense open complement of `κ_{r-1}`.

**Recent 2025–2026:** Bernardi–Reig Fité, arXiv:2508.15062 (Aug 2025) — Hankel-operator local minimal apolar scheme; GAD socle-degree analysis. Flavi–Jelisiejew–Michałek, IMRN 2025(18) — encompassing polynomials; `tw(F^d)` collapses all five rank coordinates to `⌊(n+d)/d⌋`. Buczyńska–Buczyński, arXiv:2601.19558 (Jan 2026) — border apolarity for cactus varieties of toric ambients via Cox ring. Buczyński, arXiv:2602.11309 (Feb 2026) — cactus barrier `6m − 4`.

**Survey/textbook anchors:** Landsberg, *Tensors: Geometry and Applications*, AMS GSM 128 (2012). Iarrobino–Kanev op. cit.

**Software:** Macaulay2 — `Apolarity`, `MultigradedHilbert`, `SecantVarieties`, `QuaternaryQuartics`, `CoincidentRootLoci`. Border-apolarity B-invariant-ideal enumeration: kashbari/BorderApolarity GitHub. Bernardi–Reig Fité divided-power-formalism algorithm.

## 4. Attack vectors active in the literature

**4.1 P29 apolarity (PRIMARY).** Classify saturated 0-dim Gorenstein apolar schemes of length `r` for given `F`. Substrate-grade: the witness is CONSTRUCTIVE — finite combinatorial data auditable by substrate. Border-cactus extension (Buczyńska–Buczyński 2026) brings multigraded Hilbert scheme machinery to toric ambients via Cox ring.

**4.2 P31 catalecticant attack.** Catalecticant minors give equations vanishing on `κ_r`. Buczyński–Keneshlou (2024) prove these *cut out* `κ_r` set-theoretically on the complement of `κ_{r-1}` for high-degree Veronese — catalecticant minors are EXACTLY the cactus-variety equations on a dense open subset. **Critical caveat (cactus barrier):** since these equations vanish on `κ_r ⊋ σ_r`, they cannot prove border-rank lower bounds exceeding `dim(κ_r)`.

**4.3 P31 secondary: Kronecker-Koszul / Kronecker-Young flattenings (beyond cactus).** Galązka–Mańdziuk et al. construct equations vanishing on `σ_r` but NOT on `κ_r` — non-determinantal, breaks the cactus barrier in principle.

**4.4 Multigraded Hilbert scheme analysis.** `κ_r` parameterized by length-`r` 0-dim subschemes; multigraded Hilbert scheme stratifies by multigraded Hilbert function. B-invariant ideal enumeration (Buczyńska–Buczyński Algorithm 5.1) implements exhaustive search. Substrate hook: each Hilbert function = a CoordinateChart on the witness space.

**4.5 GAD machinery.** Bernardi–Iarrobino–Marques classify minimal-length GADs. Apolar scheme `X` of `F` corresponds to a GAD; *socle-degree* of `X` determines whether GAD is "of `F`" or "of an extension." Bernardi–Reig Fité 2025 — current best constructive algorithm.

**4.6 Smoothability & wild forms (strict-inequality witness path).** Buczyński–Jelisiejew–Mella 2018: explicit cubic in 5 variables with `R̲=5, sr=6`. Flavi–Jelisiejew–Michałek 2025 flips direction: encompassing polynomials with smoothable apolar algebra COLLAPSE all five rank coordinates. Substrate calibration: `CactusRankWitness` claiming gap detection must produce smoothability obstruction.

**4.7 New attack pattern (substrate architecture, NOT a paradigm): closure-stratification audit.** The five rank coordinates `(R, sr, R̲, cr̲, cr)` form a stratification of polynomial complexity. A `CactusRankWitness` recording all five with explicit witnesses for each strict inequality is a stronger primitive than any single-rank witness. Refines `closure_status` field of `BorderRankWitness` from T#34.

## 5. Substrate encoding

**Position in primitive hierarchy.** T#19 is a Tier-B subtype of T#34's `BorderRankWitness`:

```
ConstructiveExistenceWitness (Tier-B abstract)
└── BorderRankWitness (T#34; substrate-grade, registered)
    ├── DecompositionCertificate (T#43 subtype)
    ├── DegenerationWitness (T#43 / T#34 subtype)
    └── CactusRankWitness (T#19 subtype, NEW)
        └── BorderCactusWitness (Buczyńska-Buczyński 2026, sub-subtype)
```

**Required primitive:**

```
CactusRankWitness {
  form_or_tensor:    {SymmetricForm, GeneralTensor}
  ambient_field:     {ℚ, ℝ, ℂ, k_alg_closed}
  cactus_rank_r:     Integer

  apolar_witness: {
    apolar_scheme:     ZeroDimensionalSubscheme
    length:            Integer (= r)
    is_gorenstein:     bool
    is_smoothable:     {YES, NO, UNKNOWN}        # discriminator vs sr
    is_reduced:        {YES, NO}                  # discriminator vs R
    saturation:        bool
    multigraded_hilbert_function: List<Integer>
    socle_degree:      Integer
    gad_relation:      {OF_F, OF_EXTENSION, NA}   # Bernardi-Reig Fité 2025
  }

  catalecticant_witness: optional<{                # Buczynski-Keneshlou 2024
    catalecticant_matrix: Matrix
    minor_size:        Integer
    rank_at_F:         Integer
    is_dense_open:     bool                        # complement of kappa_{r-1}
  }>

  rank_coordinates: {                              # full rank-zoo entry
    R:                 optional<Integer>
    sr:                optional<Integer>
    R_underline:       optional<Integer>
    cr_underline:      optional<Integer>           # border cactus rank
    cr:                Integer (= cactus_rank_r)
    differential_length: optional<Integer>
  }

  closure_status: {
    achieves_strict_gap_vs_R_underline:   {YES, NO, UNKNOWN}
    achieves_strict_gap_vs_sr:            {YES, NO, UNKNOWN}
    is_general_form:                       bool        # base-rate flag
    is_wild_form:                          bool        # Buczynski-Jelisiejew-Mella
  }

  attack_paradigm:    {P29_APOLARITY, P31_CATALECTICANT, GAD, MIXED}
  certificate_grade:  {EXACT, NUMERICAL_CERTIFIED, NUMERICAL_HEURISTIC}
}
```

**Composition rules:**
- `CactusRankWitness(F, r)` + `BorderRankWitness.apolar_witness = SAME scheme` ⇒ scheme proves `cr(F) ≤ r ≤ R̲(F)`.
- `CactusRankWitness(F, r)` ∧ `R̲(F) > r` (separately certified) ⇒ STRICT GAP `cr < R̲` (substrate-grade gap-witness).
- `is_general_form = true` triggers PATTERN_BASE_RATE_NEGLECT calibration warning.

**CoordinateChart hint (HARD-5).** The five rank coordinates `(R, sr, R̲, cr̲, cr)` are five DISTINCT charts on the same `tensor_node`. A coordinate-aware substrate must register them separately, NEVER collapse into a single "rank" attribute. Any chart asserting "rank decreased from X to Y" without specifying WHICH rank is HARD-5-noncompliant.

**Capability-gap tickets:**
- Inherits `T-ST-fire41-001` from T#34.
- Proposed new `T-ST-T19-001` `CactusRankWitness` probe with PATTERN_RANK_PARITY_LEAK calibration.
- Proposed new `T-ST-T19-002` cactus-barrier audit hook for any P31 BorderRankWitness with claimed `r > 6m − 4`.

## 6. Calibration anchor notes

**Substrate-grade response:**
- States `cr ≤ R̲ ≤ R` strict on explicit witnesses (Bernardi–Ranestad cubic; Buczyński–Jelisiejew–Mella wild form).
- Names cactus rank as Iarrobino–Kanev's *scheme length* renamed by Buczyńska–Buczyński (attribution restoration).
- Identifies P29 (border apolarity) as primary paradigm; catalecticant minors as sharp equations on dense open subsets (Buczyński–Keneshlou 2024).
- Names cactus barrier `6m − 4` (Buczyński 2026) as the structural reason determinantal lower bounds on `R̲(M⟨n⟩)` plateau.
- Distinguishes `cr` from smoothable rank `sr` and from border cactus rank `cr̲` — five rank coordinates, not one.
- Acknowledges PATTERN_RANK_PARITY_LEAK as the textbook leakage trap.

**Textbook-trivial (FAIL):**
- "Cactus rank is just border rank for schemes." — wrong; border rank is the closure of the rank-`r` locus, cactus rank is the minimum length of any 0-dim apolar scheme.
- "Cactus rank ≤ rank, end of story." — direction-loss; the structural finding is `cr ≤ R̲`, not just `cr ≤ R`.
- "Use catalecticant minors and you get the border-rank lower bound." — false because of the cactus barrier; minors give cactus-variety equations, not secant.
- "For general forms there's no gap, problem solved." — PATTERN_BASE_RATE_NEGLECT trigger.
- "Border apolarity is the same as Macaulay's apolarity." — confuses classical (rank) apolarity with border apolarity (Buczyńska–Buczyński 2021 multigraded Hilbert scheme machinery).

**Trivial-vs-open within rank-zoo (FM-08 + PATTERN_RANK_PARITY_LEAK):**
- `R(F)` Waring rank — NP-hard decision (T#56).
- `R̲(F)` border rank — `∃ℝ` decision (T#34).
- `sr(F)` smoothable rank — equals `R̲` for non-wild forms; strictly between for wild forms.
- **`cr(F)` cactus rank — THIS REPORT. Strictly `≤ R̲`; gap detectable on defective stratum.**
- `cr̲(F)` border cactus rank — Buczyńska–Buczyński 2026; closure of cactus-rank-`r` locus.
- `differential_length(F)` — max catalecticant rank; lower bound on all of the above.

**Attribution canonicality:** Buczyńska, Buczyński (founders); Iarrobino, Kanev (scheme-length pre-discovery 1999); Bernardi, Ranestad (cubic-form bound); Mella (VSP / cactus geometry); Galązka, Mańdziuk, Rupniewski (secant-vs-cactus distinguishing); Jelisiejew, Michałek (smoothability); Landsberg (textbook). Watch-1 fabrication risk: a Learner could conflate Bernardi (apolarity) with another Bernardi or attribute Iarrobino's *scheme length* to Buczyńska–Buczyński's *cactus rank* without noting the renaming.

**Pattern citations:**
- **PATTERN_RANK_PARITY_LEAK (primary).** Five-to-six distinct rank notions sharing the lexical "rank." T#19 is the *defining* leakage-test problem.
- **PATTERN_BASE_RATE_NEGLECT.** General-form stratum has all ranks coincide; defective stratum carries the gap.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT.** Macaulay2 B-invariant-ideal enumeration in border apolarity blows up combinatorially; truncation must be recorded to avoid silent false-NO.

## 7. Cross-references

**Within `tensor_open_problems_v1.md`:**
- **#5** (border rank `M⟨n⟩`) — cactus barrier directly constrains determinantal P31 attack on T#5.
- **#6** (border-rank additivity) — cactus version open; submultiplicativity holds.
- **#20** (border Comon's) — cactus version asks `cr = cr_S` for symmetric forms.
- **#26** (defective Segre-Veronese) — defective stratum = where `cr ≠ R̲` lives.
- **#29** (regularity of minimal apolar schemes) — direct sister: minimal apolar schemes ARE the cactus-rank witnesses.
- **#30** (GADs structure) — cactus rank = minimal-length GAD invariant; Bernardi–Reig Fité 2025 makes constructive.
- **#34** (border-rank variety membership) — PARENT primitive; T#19 is Tier-B subtype.

**Within `attack_angle_taxonomy.md`:**
- **P29 (Border Apolarity)** — primary; T#19 is the scheme-theoretic substrate of the entire P29 framework. P29 catalog already lists T#19 explicitly.
- **P31 (Secant Variety Geometry)** — dual; catalecticant minors (cactus equations) and Young flattenings (secant equations beyond cactus) live here.
- **P25 (Pivotal Negative Result)** — the cactus barrier IS a P25 finding.
- **P15** (parent paradigm), **P09** (exhaustive computation in B-invariant enumeration).

**Prior reports in batch:**
- `report_T1_matrix_multiplication_exponent.md` — cactus barrier constrains P31 attacks on `ω`.
- `report_T28_asymptotic_spectrum.md` — cactus rank is monotone but does NOT obviously lift to asymptotic spectrum element.
- `report_T34_borderrank_membership.md` — direct PARENT report.
- `report_T43_best_rank_r_existence.md` — sister Tier-B; smoothable rank / wild forms territory.
- `report_T56_symmetric_rank_nphard.md` — sister Tier-B; complexity baseline.

**Forward dependency for Techne T038:** `CactusRankWitness` belongs in the same Tier-B contract-change-window as T#34/T#43/T#56 sister primitives. It is the cleanest of the four to specify (purely combinatorial witness — no degeneration sequences, no NP-hardness reductions) — recommend implementing FIRST as pilot for the larger contract change.
