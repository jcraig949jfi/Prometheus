# Report #81 — Proper Maass GL3 Test Design for Axis 3b Dimension-Hypothesis Discrimination

**Batch 5 | Aporia Void Detector | 2026-04-23 | Target agent: Ergon**

## 1. Problem Statement

Ergon's 2026-04-22 Maass GL3 capstone (n=1546 from LMFDB) returned a split signal: edge ρ ≈ +0.8, bulk ρ ≈ −0.8, p ≈ 0.2 — suggestive but not decisive. The arithmetic driver in Axis 3b is nbp = ω(cond), but *every* Maass GL3 form in LMFDB is level 1 (nbp = 0). The stratification used |sp₁|+|sp₂| (spectral-parameter radius) as a surrogate, which is not the Axis 3b observable. To discriminate the dimension-hypothesis (ρ ≈ +0.5) from pure Orthogonal (ρ ≈ +1.0) and pure Symplectic (ρ ≈ −0.9) at degree 3, we need a *true* degree-3 family with genuine nbp variation.

## 2. Data Options Reviewed

**(a) LMFDB Maass GL3 at level > 1.** The canonical self-dual Maass cusp forms on GL(3,ℤ) tabulated by Bian, and by Booker–Lee–Strömbergsson, and mirrored in LMFDB are almost exclusively level 1; higher-level GL3 Maass spectra are not systematically populated. Ergon should run:

    SELECT level, COUNT(*) FROM lfunc_lfunctions
    WHERE origin LIKE 'ModularForm/GL3/%' AND degree = 3
    GROUP BY level ORDER BY level;

If level > 1 count is < 100, this path is blocked.

**(b) Symmetric square of elliptic curves.** sym²(L(E,s)) is a genuine degree-3 L-function (Shimura 1975; Gelbart–Jacquet 1978 established it as a GL(3) automorphic L-function). It exists for every non-CM E/ℚ, nbp(sym²(E)) = nbp(E), and LMFDB stores a subset under `SymmetricPower/2/EllipticCurve/Q/…`. Obstruction: the Katz–Sarnak symmetry type of {sym²(E) : E/ℚ non-CM, cond ≤ X} is **Symplectic** (Katz–Sarnak 1999 §3; Dueñez–Miller 2009). Under Sp the Axis 3b prediction is ρ ≈ −0.9, identical to genus-2, so sym²(E) **cannot** separate dim-hypothesis from Sp.

**(c) Rankin–Selberg GL(2)×GL(2).** Degree 4. G2C already occupies that slot.

**(d) Twists L(E, χ, s).** Degree 2.

**(e) Self-dual Maass GL3 in computable ranges.** Predicted symmetry type for self-dual Maass cusp forms on GL(n) in archimedean families is Orthogonal (Goldfeld, *Automorphic Forms and L-functions for GL(n,R)*, 2006, §7; Goldfeld–Hundley 2011). For n=3 in the level aspect this would give desired O-type family — but data do not exist at scale.

## 3. Recommended Path for Ergon

**Primary: exhaust LMFDB level-aspect GL3 cohort.**
1. Level-distribution query.
2. If any level > 1 bin has n ≥ 100, factor conductor for nbp and run Spearman ρ(nbp, δ) stratified by (level, spectral-parameter quartile).
3. Expected: pure O → +1.0. Dim-hypothesis → +0.5. Sp → −0.9. Gap between +1.0 and +0.5 is the decisive signal.

**Secondary: sym²(E) as Sp-at-degree-3 control.** Doesn't discriminate O from dim-hypothesis, but gives the **first independent Sp test at degree 3** outside genus-2. Confirming ρ ≈ −0.9 for sym²(E) while G2C also gives ρ ≈ −0.9 shows Axis 3b sign is a function of symmetry class, not GL(2) origin. Tightens Report #78's Sp-uniqueness claim.

**Tertiary (if primary blocked): request targeted Maass GL3 level-aspect compute.** Bian's algorithm (PhD Bristol 2013) extends to squarefree levels. Cohort of 500–1000 Maass GL3 at levels {2,3,5,6,7,10,…} is minimum. Multi-month effort; scope separately.

## 4. Specific Computations

For Ergon, in priority order:
- **Step 1:** Run the level-distribution query. Record counts.
- **Step 2:** Pull all LMFDB symmetric-square L-functions at degree 3 (`origin LIKE 'SymmetricPower/2/EllipticCurve/%'`), compute δ per curve, compute ρ(nbp, δ). This is the Sp-at-deg-3 control.
- **Step 3:** If level > 1 Maass GL3 exists at n ≥ 100, run ρ(nbp, δ) with edge/bulk split identical to the 2026-04-22 capstone.
- **Step 4:** Report all three ρ values alongside F011 Axis 3b's existing EC/Dirichlet/G2C. If sym²(E) gives ≈ −0.9 and Maass GL3 level > 1 gives either +0.5 or +1.0, Report #78's discriminator is decided.

## 5. Connection to F011 Axis 3b and Report #78

Report #78 pins Sp uniqueness at degree 4 (G2C). Report #81 operationalizes the degree-3 probe: sym²(E) tests whether Sp uniqueness holds at degree 3 (falsifier for a "genus-2 artifact" objection), while level > 1 Maass GL3 (if data permit) is the only clean O-vs-dim-hypothesis discriminator at degree 3.

**Word count: ~720**
