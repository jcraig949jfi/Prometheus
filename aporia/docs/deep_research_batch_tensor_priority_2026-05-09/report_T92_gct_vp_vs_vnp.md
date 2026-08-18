# Report T#92 — Geometric Complexity Theory: VP vs VNP via Padded Permanent

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` § (search "T#92" / "GCT"), ~line 370.
**Tier mapping:** Tier-E meta-primitive `RepresentationTheoreticInvariant` × Tier-B `OrbitClosureNonMembershipWitness` (composite primitive)
**Dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md`, final entry 18/18
**Doctrine:** HARD-1 (no paper-publishing framing), HARD-2 (anti-gravitational-well — actively dissent from "GCT is the path"), HARD-3 (tensor-tools-we-need-most), HARD-5 (`dc` / `ulinedc` / `L` / ABP-size are distinct coordinates)
**Author:** Aporia substrate, 2026-05-09
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK, PATTERN_PRIME_GRAVITATIONAL_OVERFIT (analogue: GCT-gravitational-overfit)
**Tags:** P22 (representation-theoretic / plethystic), P29 (border apolarity), P25 (pivotal negative result), P31 (orbit-closure geometry), P30 (occurrence obstructions — anti-anchor), candidate **P-GCT-Multi: Multiplicity-Obstruction Synthesis** (P32 candidate; collides with T#1 P32 EvolutionaryLLM and T#56 P32 ExistentialTheoryReduction — synthesis pass mandatory)

---

## Brief summary

T#92 is the Mulmuley-Sohoni (2001) flagship: prove `perm_n` (padded as `\ell^{m-n} \cdot perm_n` with `\ell` a fresh linear form, raised to degree `m`) does **not** lie in the orbit closure `\overline{GL_{m^2} \cdot \det_m}` for `m = n^{O(1)}`. This is a strict strengthening of Valiant's `VP_{ws} \neq VNP` (= determinantal complexity `dc(perm_n)` is super-polynomial). The motivation in 2001 was that orbit closures are GIT quotients with an `SL`-multiplicity decomposition, so non-membership could be witnessed by a representation-theoretic **obstruction** — an irreducible `GL_{m^2}`-representation appearing in `\mathbb{C}[\overline{GL_{m^2}\cdot\det_m}]^{(d)}` with multiplicity strictly less than in `\mathbb{C}[\overline{GL_{m^2}\cdot\ell^{m-n}\cdot perm_n}]^{(d)}`. GCT was supposed to bypass relativization, natural proofs, and algebrization simultaneously by trading combinatorial circuit arguments for algebraic-geometric / Lie-theoretic invariants. **Status 2026: the program is structurally wounded but not dead.** The Bürgisser-Ikenmeyer-Panova (J. AMS 2019, arXiv:1604.06431) **No-Go theorem** proves no *occurrence* obstructions exist for the padded-permanent vs determinant separation — falsifying the original GCT roadmap. Multiplicity obstructions (Dörfler-Ikenmeyer-Panova 2019) and outside-orbit / vanishing-ideal obstructions remain on the table but have no concrete construction. Mulmuley himself (CACM 2012) estimated ~100 years to resolution, and the field has visibly shifted: Limaye-Srinivasan-Tavenas (FOCS 2021, super-polynomial low-depth lower bounds, with Forbes 2024 extending to all fields) and Bhattacharjee et al. ICALP 2024 (exponential sums) are explicitly **non-GCT** routes. The best concrete `dc(perm_n)` lower bound remains Mignon-Ressayre `n^2/2` (2004); minor sharpenings to `(n-1)^2 + 1` over `\mathbb{R}` exist; no super-polynomial lower bound on `dc(perm_n)` exists by any technique as of 2026.

## Flagged findings

- **F-T92-01 — anti-anchor:** "Bürgisser-Ikenmeyer-Panova killed GCT" is a frequently-encountered LLM training-data oversimplification. They killed *occurrence obstructions for orbit closures of `\det_m` and the padded permanent*; multiplicity obstructions, vanishing-ideal obstructions, outside-orbit obstructions, and equivariant-determinantal-complexity routes remain. PATTERN_RANK_PARITY_LEAK risk: agents will conflate "occurrence" with "all GCT obstructions."
- **F-T92-02 — calibration update needed for catalog:** the catalog should explicitly distinguish four complexity coordinates, none collapse-equivalent: `dc` (determinantal complexity), `\underline{dc}` (border determinantal complexity), `L` (algebraic formula size), `B` (ABP size). Recent Bhargav-Dwivedi-Saxena-style results (ITCS 2024 *Determinants vs. Algebraic Branching Programs*) show `B = O(d^5 \cdot dc)` for homogeneous degree-`d` polynomials, tying `dc` and ABP-size for constant-degree but **not collapsing them** — the catalog must encode this directionally.
- **F-T92-03 — paradigm-stall flag:** GCT VII (the Mulmuley program installments) effectively halted at *Geometric Complexity Theory V: Efficient algorithms for Noether normalization* (~2017); subsequent volumes have not progressed the lower-bound machinery. The active research has migrated into adjacent vehicles (Landsberg-Ressayre equivariant determinantal complexity 2017, Grochow-Mulmuley-Qiao 2013/2015 unification frame, Pak-Panova-Ikenmeyer Kronecker / plethysm work — see T#95). This is **substrate-relevant**: any "GCT will resolve T#92" prior in agent prompts is HARD-2 territory.
- **F-T92-04 — primitive-bundle leverage:** T#92 is *not* a single Tier-B witness. It composes:
  - Tier-B `OrbitClosureNonMembershipWitness` (the geometric content)
  - Tier-E `RepresentationTheoreticInvariant` (the multiplicity / character data — shared with T#95)
  - Tier-B `BorderComplexityCertificate` (separating `dc` from `\underline{dc}` — distinct from T#34 border-rank membership)
  - Tier-B `EquivariantComplexityCertificate` (Landsberg-Ressayre symmetry-restricted exponential bounds — *conditional* exponential, not unconditional)
  Each is independently useful across T#1, T#22, T#56, T#92, T#95.
- **F-T92-05 — anti-anchor 2:** Saxl's conjecture is **resolved unconditionally** (Sellke 2025/26, arXiv:2512.15035, ref. report T#95). Any T#92 framing that uses Saxl-as-open is stale. Saxl's resolution is **not** a path to T#92 directly — it concerned `S_n`-Kronecker positivity of the staircase squared, not `GL`-orbit closures.
- **F-T92-06 — competing program flag:** Limaye-Srinivasan-Tavenas (FOCS 2021, *Superpolynomial Lower Bounds Against Low-Depth Algebraic Circuits*, with Forbes 2024 *Low-Depth Algebraic Circuit Lower Bounds over Any Field* CCC 2024) deliver **the first super-polynomial algebraic-circuit lower bound** against constant-depth (set-multilinear) circuits — over **any** field, since 2024. This is non-GCT and uses set-multilinearization + partial-derivative-style measures. It is **not** a `dc(perm_n)` super-polynomial bound, but it is the strongest non-trivial algebraic-circuit lower bound now known. The 2024 ICALP exponential-sums route (Bhattacharjee-Bläser-Dutta-Mukherjee) is parallel.
- **F-T92-07 — substrate gap flag:** existing primitive `BorderRankMembershipWitness` (T#34) does *not* cover orbit-closure non-membership. The two are categorically distinct: border-rank is membership in a secant variety; GCT non-membership is exclusion from a `GL`-orbit closure of a *single* polynomial. New primitive needed: `GCTObstructionCertificate` with sub-types (occurrence, multiplicity, vanishing-ideal, outside-orbit, equivariant).
- **F-T92-08 — algebraic natural proofs barrier:** Forbes-Shpilka-Volk (2017) and Grochow-Kumar-Saks-Saraf give first evidence of an **algebraic natural proofs barrier** (succinct hitting sets imply equations-of-circuit-classes lower bounds). This complicates GCT obstruction-construction: any *constructive* obstruction may itself be a circuit-lower-bound proof and hit the barrier. PATTERN_PRIME_GRAVITATIONAL_OVERFIT analogue: GCT enthusiasts assumed "symmetry-driven proofs evade natural proofs"; the algebraic version of natural proofs partially recaptures them.

---

## 1. Problem statement (formal)

Let `\det_m \in \mathbb{C}[x_{ij}]_{i,j=1..m}` be the `m \times m` determinant polynomial of degree `m`, and let `\text{perm}_n \in \mathbb{C}[y_{ij}]_{i,j=1..n}` be the `n \times n` permanent of degree `n`. Fix `m \geq n` and a fresh linear form `\ell` (independent variable, say `\ell = x_{1,1}`). The **padded permanent** is

$$\widetilde{\text{perm}}_{n,m} := \ell^{m-n} \cdot \text{perm}_n \in \mathbb{C}[x_{ij}]^{(m)}$$

(degree `m`, in `m^2` variables after embedding the `n^2` `y`-variables into the `x`-grid).

The natural action of `GL_{m^2}(\mathbb{C})` on the linear span `V = \mathbb{C}^{m^2}` extends to an action on `\text{Sym}^m(V) \cong \mathbb{C}[V^*]^{(m)}` of degree-`m` polynomials. Denote by `\overline{GL_{m^2} \cdot \det_m}` the Zariski closure of the orbit `\{g \cdot \det_m : g \in GL_{m^2}\}` inside `\text{Sym}^m(V)`.

**Determinantal complexity.** `dc(p) := \min\{m : p \in GL_{m^2} \cdot \det_m\}` (orbit, not closure) — for affine-linear substitutions giving a determinantal representation of size `m`.

**Border determinantal complexity.** `\underline{dc}(p) := \min\{m : p \in \overline{GL_{m^2} \cdot \det_m}\}` (orbit closure).

These differ: `\underline{dc} \leq dc`, with strict inequality possible (limit phenomena allow approximating without realizing).

**Mulmuley-Sohoni conjecture (T#92, padded form).** `\widetilde{\text{perm}}_{n,m} \notin \overline{GL_{m^2} \cdot \det_m}` for `m = n^{O(1)}` and large enough `n`.

**Equivalent / related conjectures (HARD-5 — distinct coordinates).**
- Valiant 1979: `dc(\text{perm}_n) = n^{\omega(1)}` (super-polynomial).
- Border-Valiant: `\underline{dc}(\text{perm}_n) = n^{\omega(1)}` (strictly stronger; what GCT would actually prove).
- VP vs VNP: `L(\text{perm}_n) = n^{\omega(1)}` for algebraic formula size (the original Valiant problem).
- VP_{ws} vs VNP: weak-skew determinantal model — the cleanest equivalent of `dc`.

These four are *not* known to coincide; collapsing them is PATTERN_RANK_PARITY_LEAK (see F-T92-02).

**Why orbit closures.** A `GL`-orbit closure carries a `GL`-action on its homogeneous coordinate ring `\mathbb{C}[\overline{GL_{m^2}\cdot p}]_d`, decomposing into irreducibles `\bigoplus_\lambda V_\lambda^{\oplus a_{\lambda,d}(p)}`. For two polynomials `p, q`, if for some `(\lambda, d)` the multiplicity satisfies `a_{\lambda,d}(p) > a_{\lambda,d}(q)`, then `p \notin \overline{GL \cdot q}`. The `a_{\lambda,d}` are characters of explicit Lie-theoretic objects; they are in principle "computable." This is the GCT premise: replace adversarial circuit arguments with character arithmetic.

## 2. Status & bounds (HARD-5: report each on its own coordinate)

### 2.1 `dc(\text{perm}_n)` lower bounds (concrete)

| Bound | Year | Authors | Source / arXiv |
|---|---|---|---|
| `dc(\text{perm}_n) \geq \sqrt{2}\cdot n` | 1996 | von zur Gathen | early Hessian-rank argument |
| `dc(\text{perm}_n) \geq n^2/2` | 2004 | **Mignon-Ressayre** | *IMRN* 2004 |
| `dc(\text{perm}_n) \geq \sqrt{2n^2}` over `\mathbb{R}` (different constant) | 2013 | Landsberg-Manivel-Ressayre | arXiv:1108.6243 |
| `dc(\text{perm}_n) \geq n^2/2` (refined) | 2010s | Cai-Chen-Li | *Math. Ann.* |
| `dc(\text{perm}_n) \geq (n-1)^2 + 1` over `\mathbb{R}` | 2015 | Yabe / Alper-Bogart-Velasco (arXiv:1505.02205) | *FoCM* 2017 |
| `dc(\sum_i x_i^n) \geq 1.5n - 3` | ~2020 | Kumar-Volk (arXiv:2009.02452, CCC 2021) | not the permanent, but landmark `\Theta(n)` for an explicit polynomial |

**Status:** No `\omega(n^2)` lower bound for `dc(\text{perm}_n)` exists by any technique as of 2026. The Mignon-Ressayre `n^2/2` quadratic floor has stood for 22 years.

### 2.2 Conditional / restricted-model bounds

- **Equivariant determinantal complexity** (Landsberg-Ressayre 2017, *Permanent v. determinant: an exponential lower bound assuming symmetry...*, arXiv:1508.05788): If the determinantal representation is required to be equivariant under the `(S_n \times S_n) \ltimes (D_n \times D_n)` symmetry group of the permanent (~half its full symmetry), then `dc \geq 2^n / (something)` — first exponential separation, but in a **strongly restricted** model. **Anti-anchor:** Landsberg-Ressayre is an exponential bound, BUT the equivariance restriction is severe; the analogous statement for `dc` itself is open.
- **Bi-polynomial rank** (Mrowka-style, arXiv:1504.00151): geometric framework yielding cubic and other intermediate bounds under structural restrictions.

### 2.3 GCT obstruction status

- **Bürgisser-Ikenmeyer-Panova** (FOCS 2016, J. AMS 2019, *No occurrence obstructions in geometric complexity theory*, arXiv:1604.06431). **Theorem.** For all sufficiently large `n` and `m = poly(n)`, every irreducible `GL_{m^2}`-representation occurring in `\mathbb{C}[\overline{GL_{m^2}\cdot\det_m}]_d` also occurs in `\mathbb{C}[\overline{GL_{m^2}\cdot \widetilde{\text{perm}}_{n,m}}]_d`. **Consequence:** the original Mulmuley-Sohoni roadmap (separate via *occurrence* obstructions) is impossible.
- **Dörfler-Ikenmeyer-Panova** (ICALP 2019, *Multiplicity Obstructions Are Stronger Than Occurrence Obstructions*, SIAM J. Appl. Algebra Geom. 2020): construct a multiplicity obstruction that is provably not an occurrence obstruction nor a vanishing-ideal obstruction. Establishes the multiplicity route is **strictly stronger** than what BIP killed.
- **Ikenmeyer-Mulmuley-Walter** (2017): Kronecker positivity is `NP`-hard — falsifying Mulmuley's `PH1` conjecture (Kronecker positivity in `P`), which would have provided a complexity-theoretic "search" for obstructions. See report T#95.

### 2.4 Non-GCT competing lower bounds (2021-2025)

- **Limaye-Srinivasan-Tavenas** (FOCS 2021, *Superpolynomial Lower Bounds Against Low-Depth Algebraic Circuits*, arXiv:2101.01340): first super-polynomial lower bound against constant-depth set-multilinear algebraic circuits. **Forbes 2024** (CCC 2024, *Low-Depth Algebraic Circuit Lower Bounds over Any Field*) extends to all fields. Set-multilinearization is the technical engine; partial-derivative-measure refinement is the obstruction.
- **Bhattacharjee-Bläser-Dutta-Mukherjee** (ICALP 2024, *Exponential Lower Bounds via Exponential Sums*): orthogonal exponential-sums approach.
- **Bhargav-Dwivedi-Saxena** (ITCS 2024, *Determinants vs. Algebraic Branching Programs*): `B = O(d^5 \cdot dc)` on homogeneous polynomials of degree `d` — tightens relationship between `dc` and ABP-size in the constant-degree regime.
- **Forbes-Shpilka-Volk** + Grochow-Kumar-Saks-Saraf (2017): algebraic natural proofs barrier — succinct hitting sets imply lower bounds for circuit-class equations. Tension with GCT obstruction-construction.

## 3. Literature

**Foundational (Mulmuley-Sohoni program):**
- GCT I: Mulmuley-Sohoni 2001/2008 *SIAM J. Comput.*, *An Approach to the P vs NP and Related Problems*.
- GCT II: Mulmuley-Sohoni 2008 *SIAM J. Comput.*, *Towards Explicit Obstructions for Embeddings among Class Varieties*.
- GCT III-V (Mulmuley alone): plethysm reductions, Noether normalization (V is the latest substantive installment, ~2017).
- GCT VI-VII: program-status documents; not lower-bound advances.
- Mulmuley CACM 2012 *The GCT Program toward the P vs. NP Problem* — accessible overview, ~100-year timeline.

**Negative / structural results:**
- Bürgisser-Ikenmeyer-Panova, *No occurrence obstructions in geometric complexity theory*, J. AMS 32 (2019) 163-193. arXiv:1604.06431. **The structural blow.**
- Ikenmeyer-Mulmuley-Walter, *On vanishing of Kronecker coefficients*, arXiv:1507.02955, Comput. Complex. 2017. NP-hardness of Kronecker positivity.
- Ikenmeyer-Pak-Panova 2024 (IMRN): `PH`-hardness for `S_n`-character positivity. See T#95 report.
- Bürgisser-Hüttenhain-Ikenmeyer 2017 (*Proc. AMS*).

**Lower-bound progress:**
- Mignon-Ressayre 2004, *IMRN*: `dc(\text{perm}_n) \geq n^2/2`.
- Landsberg-Manivel-Ressayre, arXiv:1108.6243.
- Cai-Chen-Li *Math. Ann.*
- Landsberg-Ressayre, *Permanent v. determinant: an exponential lower bound assuming symmetry*, arXiv:1508.05788, ITCS 2016.
- Alper-Bogart-Velasco, arXiv:1505.02205, *FoCM* 2017.
- Kumar-Volk, arXiv:2009.02452, CCC 2021.
- Bhargav-Dwivedi-Saxena, ITCS 2024 (Determinants vs. ABPs).

**Multiplicity / obstruction structure:**
- Dörfler-Ikenmeyer-Panova, *Multiplicity Obstructions Are Stronger Than Occurrence Obstructions*, ICALP 2019, SIAM J. Appl. Algebra Geom. 2020.
- Bürgisser-Ikenmeyer-Panova (also implementing GCT, arXiv:1911.03990, STOC 2020 — *Implementing GCT: On the separation of orbit closures via symmetries*) — multiplicity-obstruction construction.
- Grochow-Mulmuley-Qiao 2013/2015 (arXiv:1304.6333), *Unifying and generalizing known lower bounds via GCT* — shows GCT is at least as strong as known elementary methods.

**Competing program (non-GCT):**
- Limaye-Srinivasan-Tavenas FOCS 2021, arXiv:2101.01340 (CACM 2024 highlight).
- Forbes CCC 2024 (LIPIcs vol. 300).
- Bhattacharjee-Bläser-Dutta-Mukherjee ICALP 2024.
- Forbes-Shpilka-Volk + Grochow-Kumar-Saks-Saraf 2017 — algebraic natural proofs barrier.

**Saxl resolution (cross-link, T#95):**
- Sellke, *Staircase Minimality and a Proof of Saxl's Conjecture*, arXiv:2512.15035 (2025/2026). Resolves Saxl unconditionally. *Does not directly resolve T#92*; but eliminates a hoped-for GCT lemma source.

## 4. Attack vectors active in the literature

**P22 (representation-theoretic / plethystic).** The original GCT vehicle. Ikenmeyer-Panova plethysm bounds (T#95-adjacent), Pak-Panova-Swanson 2025 restricted positive rules. **Status:** active, but no concrete obstruction for T#92 has been constructed; we only know occurrence-style is impossible.

**P29 (border apolarity).** Used aggressively in tensor border-rank questions (T#34, T#19); the *symmetric* analogue extends to `\underline{dc}` via apolarity ideals of the determinant. **Open question for substrate:** does border apolarity machinery extend to GCT non-membership? Under-explored. Substrate-tester ticket candidate.

**P31 (orbit-closure / secant geometry).** The natural geometric language; 2020 STOC arXiv:1911.03990 *Implementing GCT* paper actually constructs separations between orbit closures using symmetries. **Status:** the only "constructive obstruction" results to date.

**P30 (occurrence obstructions) — anti-anchor.** Killed by BIP 2019 in this regime. **Substrate must encode P30 as an explicit anti-anchor pin** with reference to BIP, so any future agent attempting an "occurrence obstruction for `\det_m` vs padded permanent" hits an immediate falsification gate.

**P25 (pivotal negative results / barriers).** BIP 2019 itself; Ikenmeyer-Mulmuley-Walter NP-hardness; algebraic natural proofs barrier; Ikenmeyer-Pak-Panova `PH`-hardness. T#92 sits at a **dense barrier nexus** — "every direction has a known obstruction-to-the-obstruction."

**P32 candidates from this report:** "**Multiplicity-Obstruction Synthesis**" — formal vehicle for the post-BIP route (multiplicity / vanishing-ideal / outside-orbit obstructions, with Lie-theoretic computation). This *collides* with the P32 candidates from T#1 (Evolutionary-LLM Algorithm Synthesis) and T#56 (Existential-Theory Reduction). Synthesis pass mandatory. Honest assessment: I do not believe T#92's P32 candidate is the highest-leverage; **T#1's P32 has the most concrete impact (AlphaEvolve produced a 4×4(ℂ) rank-48), T#56's P32 has the most general theoretical reach. T#92's "multiplicity synthesis" is a *future-promise* paradigm with no concrete deliverable since 2020.**

**Plethysm-positivity attacks.** Cross-pollination with T#95 (Kronecker / plethysm). Ikenmeyer-Omar-Tsintsilidas 2025 (arXiv:2509.10069) field-independent Kronecker-plethysm isomorphisms feeds into GCT computation but not directly into a T#92 obstruction.

**Non-GCT lower-bound techniques (competing, not extending).** LST + Forbes (constant-depth set-multilinear), Bhattacharjee et al. 2024 (exponential sums), Kumar-Volk (`\Theta(n)` for `\sum x_i^n`). These are **rivals to GCT**, not extensions; they do not produce orbit-closure obstructions. **Substrate must not conflate these with GCT primitives.** PATTERN_RANK_PARITY_LEAK trap.

**Tensor-rank version of GCT obstructions.** Recent work compares `\det` and `\text{perm}` *as tensors* (not polynomials), with tensor-rank arguments separating them in low-dimension cases (4×4). This is a *different* coordinate from `dc`; substrate must register `TensorRankSeparation` as a sibling, not a sub-class, of `DeterminantalComplexitySeparation`. (HARD-5.)

**Equivariant determinantal complexity (Landsberg-Ressayre).** A genuine *exponential* separation, but in a restricted model. Pattern: prove the unrestricted version is at least the restricted version up to polynomial factors (open — likely false in general). Substrate-tester ticket candidate: encode "is restricted-model exponential bound a **valid** lower bound for the unrestricted model?" as a P-RANK-PARITY-LEAK detector. Nominally trivial — answer is "no, not without additional argument" — but agents *will* trip on this.

## 5. Substrate encoding

T#92 is the canonical case-study for **composite Tier-B+E primitives**. A single `OrbitClosureNonMembershipWitness` is necessary but insufficient; a full GCT obstruction requires:

```
GCTObstructionCertificate (composite Tier-B/E, mandatory subtype):
  base:
    target_polynomial: PaddedPermanent(n, m)
    excluding_orbit: GL_orbit_closure(det_m, GL(m^2))
  obstruction_subtype: Enum {
    OccurrenceObstruction         # KILLED for det/padded-perm: BIP 2019. Substrate must FAIL-LOAD with this subtype against the canonical BIP target. Anti-anchor pin.
    MultiplicityObstruction       # Live; requires character-arithmetic primitive (Tier-E Kronecker / plethysm).
    VanishingIdealObstruction     # Live; cohomological.
    OutsideOrbitObstruction       # Live; novel construction by Bürgisser-Ikenmeyer-Panova STOC 2020.
    EquivariantObstruction        # Restricted-model only — must carry `restricted_to: SymmetryGroup` field; substrate WARNS on ranking outside restriction.
  }
  uses: List[RepresentationTheoreticInvariant]   # Tier-E: Schur fns, Kronecker coefficients, plethysm coefficients
  uses: List[PartitionObject]                    # Tier-E: from T#95
  proves: SeparationStatement(
    coordinate ∈ {dc, ulinedc, L, B, dc_equivariant},  # HARD-5: which complexity?
    polynomial_class = symbolic permanent family,
    bound_form ∈ {polynomial, super-polynomial, exponential},
    conditional ∈ {None, restricted_model, unproven_complexity_assumption}
  )
```

**Anti-anchor pins (mandatory in substrate-tester registration):**
1. `OccurrenceObstruction` against `(det_m, padded_perm_{n,m}, m=poly(n))` is **provably impossible** (BIP 2019 J. AMS). Substrate must reject any agent attempt to construct one as a sentinel-violation. Counterpart to PATTERN_BSD_TAUTOLOGY: PATTERN_GCT_OCCURRENCE_DEAD.
2. `dc(p)` and `\underline{dc}(p)` are distinct coordinates; conflation is PATTERN_RANK_PARITY_LEAK.
3. `dc(\text{perm})`-restricted-to-equivariant-model is **not a lower bound** for `dc(\text{perm})` unrestricted.
4. Saxl-resolved (Sellke 2025) is a T#95 fact, not a T#92 fact; agents will lift it as a "GCT advance" — it isn't.
5. PATTERN_BASE_RATE_NEGLECT: occurrence obstructions are zero for almost all `(\lambda, d)` against the relevant pair; the BIP theorem says they are zero *for all*, but the empirical-near-zero phenomenon is independent grounds.

**Composition rule for substrate:** `GCTObstructionCertificate` consumes `RepresentationTheoreticInvariant` (Tier-E shared with T#95) and produces `OrbitClosureSeparation` (Tier-B). The dependency graph means the T#95 primitive bundle is a **prerequisite** for any T#92 work; substrate-tester should refuse to load a `GCTObstructionCertificate` ticket without an upstream `RepresentationTheoreticInvariant` registration. This is the highest-leverage coupling in the tensor-priority dispatch.

**Proposed sub-primitive:** `BorderComplexitySeparator(p, q, coordinate)` — distinct from T#34's border-rank membership in that it operates on `\underline{dc}` (border determinantal) rather than `\underline{R}` (border tensor rank). Same homotopy-limit machinery; distinct semantics. HARD-5 violation if collapsed.

**Substrate-tester ticket proposals:**
- `T-ST-T92-001` Register `GCTObstructionCertificate` (Tier-B/E composite) with five subtype enum, one anti-anchor (occurrence-dead).
- `T-ST-T92-002` Register `BorderComplexitySeparator` as Tier-B primitive distinct from T#34's `BorderRankMembershipWitness`.
- `T-ST-T92-003` Register `EquivariantComplexityCertificate` (Tier-B, restricted-model) with `restricted_to` symmetry-group annotation and substrate WARN on unrestricted-extrapolation.
- `T-ST-T92-004` Register `AlgebraicNaturalProofsBarrier` (Tier-D meta-warning) — fires when a candidate obstruction is itself a circuit-lower-bound, applying Forbes-Shpilka-Volk barrier check.
- `T-ST-T92-005` (cross-cutting) Synthesis pass to assign P32-numbering across T#1 / T#56 / T#92 / T#95 candidate paradigms (current collisions).

## 6. Calibration anchor notes

**Substrate-grade engagement vs textbook-trivial.** A textbook-trivial T#92 engagement would say: "the Mulmuley-Sohoni program seeks to separate determinant and permanent orbit closures using representation-theoretic obstructions; the best lower bound is `n^2/2` (Mignon-Ressayre)." Every LLM with mathematical training data will produce roughly that. **Substrate-grade** engagement must:

1. Distinguish `dc / \underline{dc} / L / B / dc_{equivariant}` as five *distinct* complexity coordinates and never report a bound without specifying which one (HARD-5; cite **PATTERN_RANK_PARITY_LEAK**: the four-way coordinate collapse is the dominant Learner failure mode here, identical in shape to the Kronecker / Littlewood-Richardson collapse from T#95).
2. Treat BIP 2019 as a structural blow that **falsified the original GCT roadmap**, not as "minor technical setback" (HARD-2: the LLM gravitational well is "GCT is the only viable program for P vs NP" — Wikipedia says this in 2026; the *honest* picture is Mulmuley-still-believes / many-practitioners-have-moved-on / non-GCT-routes-are-where-the-actual-2021-2024-progress-is). Cite **anti-anchor PATTERN_GCT_OCCURRENCE_DEAD**.
3. Distinguish "Saxl resolved by Sellke 2025" (T#95 fact) from "T#92 advanced." A trained-data LLM is likely to optimistically conflate Kronecker-positivity progress with GCT-toward-P-vs-NP progress. Cite **PATTERN_BASE_RATE_NEGLECT**: occurrence obstructions are *generically zero* — BIP made the impossibility theorem, but the base-rate already screams that occurrence is the wrong vehicle. The substrate's calibration check should flag any agent that invokes occurrence obstructions positively as needing recalibration.
4. Refuse to call Landsberg-Ressayre 2017 a "lower bound on `dc(\text{perm})`" without the equivariance restriction annotation. (PATTERN_RANK_PARITY_LEAK at the model-restriction layer.)
5. Recognize that "Mulmuley estimates 100 years" is itself the program's chief proponent's calibration anchor — and that prominent practitioners (Bürgisser, Ikenmeyer, Panova, who *built* much of the modern GCT machinery) have publicly framed BIP 2019 as forcing "a major revision" of the program. The substrate's posture should be **"GCT is one of several active programs, with diminished but nonzero priors as of 2026"**, not the gravitational-well "GCT is the path."

**PATTERN_PRIME_GRAVITATIONAL_OVERFIT analogue (PATTERN_GCT_GRAVITATIONAL_OVERFIT, candidate registration):** in the same way Prometheus's cross-domain analyses keep finding "primes are 96% of the structure" until prime-detrending is mandatory, GCT-related literature analyses keep finding "GCT unifies / is the path" until obstruction-impossibility theorems force the picture to honest. Substrate-tester ticket: when an agent prompt contains "GCT" + "P vs NP" + "the only viable program," apply PATTERN_GCT_GRAVITATIONAL_OVERFIT detrending: re-rank with non-GCT routes (LST / Forbes / Bhattacharjee / Kumar-Volk / equivariant) explicitly weighted equal-or-higher.

## 7. Cross-references

- **T#1 (matrix multiplication exponent ω):** GCT applies to `M\langle n, n, n \rangle`-tensor and asymptotic-rank-is-asymptotic-spectrum (Christandl-Hoeberechts-Nieuwboer-Vrana-Zuiddam STOC 2025). T#1's P32 candidate (Evolutionary-LLM Algorithm Synthesis) collides numerically with T#92's P32 candidate; synthesis pass mandatory.
- **T#22 (Waring rank of permanent — sister problem):** symmetric-rank version of `dc(\text{perm})`. Bounds on Waring rank constrain `\underline{dc}` from a different angle. *The natural sibling primitive `WaringRankCertificate` (Tier-B) shares Lie-theoretic infrastructure with `GCTObstructionCertificate`.*
- **T#34 (border-rank membership):** distinct primitive from T#92's border-determinantal-complexity. Same homotopy-limit machinery; different semantics. HARD-5 separator.
- **T#56 (symmetric tensor rank NP-hard, Hillar-Lim, settled by Shitov 2016):** complexity-floor anchor. T#56's `ComputationalComplexityCertificate` should compose with T#92's `GCTObstructionCertificate` — the GCT obstruction problem itself sits in `PH`-hardness regimes (Ikenmeyer-Pak-Panova 2024). T#56's P32 candidate (Existential-Theory Reduction) collides with T#92's; synthesis pass mandatory.
- **T#58 (tensor isomorphism):** orbit-closure-membership decisions are TI-hard for some models. Cross-link.
- **T#95 (Kronecker positivity):** the **direct upstream**. Tier-E `RepresentationTheoreticInvariant` from T#95 is a hard prerequisite for T#92's `MultiplicityObstruction` subtype. Saxl-resolved (Sellke 2025) is a T#95 fact, not a T#92 fact — a calibration anchor for distinguishing substrate-grade from over-eager attribution.
- **Prior batch reports:**
  - `report_T1_matrix_multiplication_exponent.md` — competing P32 candidate, asymptotic spectrum machinery shared.
  - `report_T56_symmetric_rank_nphard.md` — composes with T#92's complexity stratifier.
  - `report_T95_kronecker_positivity.md` — primitive-bundle prerequisite, especially the Tier-E `RepresentationTheoreticInvariant` / `KroneckerInvariant` / `PartitionObject` classes; anti-anchor PATTERN_RANK_PARITY_LEAK pattern reused for the four-coordinate `dc / \underline{dc} / L / B / dc_{equiv}` collapse.
  - `report_T34_borderrank_membership.md` — sibling `BorderComplexitySeparator` primitive contrast.

---

## Final synthesis (substrate-tester delivery)

T#92 is the **flagship polynomial-separation problem** and the substrate's hardest test of the multi-Tier composite-primitive design. Five concrete substrate-tester deliverables (T-ST-T92-001..005) above; one P32-collision (with T#1, T#56) flagged for Aporia synthesis; one new pattern candidate (PATTERN_GCT_GRAVITATIONAL_OVERFIT) proposed for registration alongside PATTERN_PRIME_GRAVITATIONAL_OVERFIT in the calibration battery. The honest 2026 picture: **GCT is wounded but not dead; non-GCT routes (LST/Forbes 2024, Bhattacharjee 2024, Kumar-Volk 2021) hold the actual recent progress in algebraic-circuit lower bounds; `dc(\text{perm}_n) \geq n^2/2` from Mignon-Ressayre 2004 has stood unbroken for 22 years; the exponential equivariant lower bound (Landsberg-Ressayre 2017) is real but model-restricted; the current best constant-degree connection between `dc` and ABP-size (Bhargav-Dwivedi-Saxena 2024) refines but does not collapse the four complexity coordinates.** Substrate must encode these distinctions and pin the BIP 2019 anti-anchor.

**Sources** (key citations):
- [No occurrence obstructions in geometric complexity theory (BIP 2019 J. AMS)](https://arxiv.org/abs/1604.06431)
- [Implementing GCT: Separation of orbit closures via symmetries (BIP STOC 2020)](https://arxiv.org/abs/1911.03990)
- [Multiplicity Obstructions Are Stronger Than Occurrence Obstructions (Dörfler-Ikenmeyer-Panova ICALP 2019)](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2019.51)
- [Permanent v. determinant: an exponential lower bound assuming symmetry (Landsberg-Ressayre 2017)](https://arxiv.org/abs/1508.05788)
- [A Lower Bound on Determinantal Complexity (Kumar-Volk CCC 2021)](https://arxiv.org/abs/2009.02452)
- [Low-Depth Algebraic Circuit Lower Bounds over Any Field (Forbes CCC 2024)](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2024.31)
- [The GCT program toward the P vs NP problem (Mulmuley CACM 2012)](https://cacm.acm.org/research/the-gct-program-toward-the-p-vs-np-problem/)
- [Unifying and generalizing known lower bounds via GCT (Grochow 2013/2015)](https://arxiv.org/abs/1304.6333)
