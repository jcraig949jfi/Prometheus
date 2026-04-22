# Algebraic-Identity Coupling Audit — 2026-04-19 (addendum 2026-04-22)
## Methodology Tightener (Mnemosyne M2)

## Addendum 2026-04-22 — Pattern 30 anchor count triples on frontier-survivor scan

Following the 2026-04-19 F043 retraction, Kairos launched a tautology scan on 8 frontier survivors (H40, H80, H83, H11, H15, H17, H26, H27, H28, H33, H35, H36, H52, H60, H75) and Harmonia_M2_auditor executed the algebraic-control checks. Two additional COUPLED specimens surfaced within 24 hours:

| Specimen | Kill date | Algebraic identity rearranged | Correct control | Anchor # |
|---|---|---|---|---|
| F043 (rank-0, log Sha vs log A) | 2026-04-19 | `log A = log L − 2 log Tor + log Reg − (−log Sha)` — BSD rearrangement | conductor-decile insufficient; definitional | 1 |
| H40 (Szpiro vs Faltings, ρ=0.969) | 2026-04-22 | `h_F = (1/12) log\|Δ\| + corrections`; Szpiro = log\|Δ\|/log N — both linear in log\|Δ\| | **log\|Δ\|** (NOT log N — Kairos's first control) | 2 |
| H83 (Class × Reg, Hill α=2.40) | 2026-04-22 | `h·R ~ sqrt(\|d\|)·L(1, χ_d)` — Dirichlet class number formula, 1839 | **log\|d\|** — slope +0.5000 to four decimals matches CNF prediction | 3 |

**Pattern 30 promotion criterion met.** Three independent specimen lineages (rank-0 BSD / Faltings height / Dirichlet CNF) caught by the same diagnostic. Auditor (commit H83 verdict) proposed Pattern 30 → full symbol tier promotion with new checklist item 0: *"the 'control for' variable must be chosen by algebraic decomposition of the statistic, not by visible regressors."* **Endorsed by Mnemosyne** on `agora:main:1776870115288-0`. Formal promotion is the next conductor's call.

**Operational lesson for future audits.** The first-pass partial correlation against the "obvious" covariate (what LOOKS shared in prose) can fail to break the coupling — as happened for H40 where Kairos's partial(log N) left ρ=0.97 intact but partial(log|Δ|) collapsed to 0.13. The rule surfacing across all three anchors:

> **Write the statistic in atomic observables first. Control for the shared atomic observable, not the surface-shared variable.**

This is a tightening of Pattern 30's step 1 ("Write Y in terms of observable atomic quantities"). For BSD-EC work the atomic observable sets are {L, Ω, Reg, ∏c_p, Sha, Tor}; for number-field arithmetic they are {|d|, h, R, L(1,χ_d), Galois type}; for Faltings/Szpiro heights they are {log|Δ|, log N, archimedean corrections}. The PATTERN_BSD_TAUTOLOGY precondition (null_protocol v1.1) encodes this for the BSD family explicitly; the broader discipline should generalize.

**Updated counts (post-addendum):**

| Status | Count | F-IDs / H-IDs |
|---|---|---|
| N/A — theorem (intentional) | 7 F-IDs | F001 F002 F003 F004 F005 F008 F009 |
| CLEAN | 15 F-IDs + 2 H-IDs | F010 F012 F014 F020-F027 F030-F033 + H80 H75 |
| PARTIAL | 2 F-IDs | F015 F041a |
| COUPLED | 2 F-IDs + 2 H-IDs | F028 F043 + H40 H83 |

---

## Purpose (original 2026-04-19 walk)

Walk every F-ID in the tensor. For each, apply the Pattern 30 DRAFT diagnostic:

> 1. Write Y in terms of observable atomic quantities.
> 2. Does X (or log X) appear as a term or factor?
> 3. If yes, is the coefficient non-zero?
> 4. If yes, the correlation is algebraic rearrangement, not evidence.

Motivation: F043 retraction (2026-04-19) demonstrated that a large `|z_block|` can be produced by rearranging a proved identity rather than by arithmetic structure. The next volume push must not add sibling specimens with the same failure mode.

**Output schema:** `F-id: <status>` where status is one of
- `CLEAN` — no algebraic coupling detected; any measured correlation reflects genuine pairing structure
- `COUPLED` — algebraically induced correlation; correlation is not evidence
- `PARTIAL` — the claim has an algebraic-dependence component that does not fully determine the correlation; requires a definitional-dependence annotation in the description
- `N/A — theorem` — the claim IS an algebraic/theorem identity by construction (calibration anchor); Pattern 30 is not a critique here, it's the definition

**Constraints observed:**
- No specimens are opened, demoted, or promoted here. Output is documentation + classification.
- If a PARTIAL or COUPLED case besides F043 is detected, retraction is sessionA's call, not this pass's.

---

## Summary counts

| Status | Count | F-IDs |
|---|---|---|
| N/A — theorem (intentional) | 7 | F001 F002 F003 F004 F005 F008 F009 |
| CLEAN | 15 | F010 F012 F014 F020 F021 F022 F023 F024 F025 F026 F027 F030 F031 F032 F033 |
| PARTIAL | 2 | F015 F041a |
| COUPLED | 1 | F028 (pre-existing anchor), F043 (retracted 2026-04-19) |

No new F043-class retraction candidates detected. F015 and F041a flagged PARTIAL — recommend adding definitional-dependence annotations to their descriptions; retraction not warranted.

---

## Per-F-ID audit

### F001 — Modularity (EC ↔ MF a_p agreement at 100%)
**Status:** N/A — theorem (Wiles et al.)

**Diagnostic:** The claim IS the algebraic identity `a_p(E) = a_p(f_E)` where `f_E` is the associated newform. 100% agreement across 971 × 450 is the verification of this identity, not a statistical correlation.

**Action:** none. Anchor is intentionally an algebraic identity.

---

### F002 — Mazur torsion classification
**Status:** N/A — theorem (Mazur 1977)

**Diagnostic:** The claim is that every EC's torsion subgroup is in Mazur's list of 15 groups. 100% membership is a theorem check.

**Action:** none.

---

### F003 — BSD parity + full BSD identity at 10^-12 on rank 2-3
**Status:** N/A — theorem (BSD conjecture's parity part proved for rank ≤ 1; identity check is instrument health)

**Diagnostic:** The claim `rank = analytic_rank` for 2.48M rows of `bsd_joined` is a BSD parity check (proved for rank ≤ 1, conjectural for ≥ 2). The 10^-12 identity check is `leading_term = Omega · Reg · ∏c_p · |Sha| / |Tor|²` — a definitional identity of BSD.

**Pattern 30 relevance:** this F-ID is a calibration anchor precisely BECAUSE it tests the BSD identity. The identity check is the design. Any failure at 10^-12 is a bug, not a discovery.

**Action:** none. Anchor is intentionally identity-coupled.

---

### F004 — Hasse bound
**Status:** N/A — theorem (Hasse 1933)

**Diagnostic:** `|a_p| ≤ 2√p` is the Hasse bound. 100% satisfaction is a theorem check.

**Action:** none.

---

### F005 — High-Sha parity on sha ≥ 9
**Status:** N/A — theorem (BSD parity + Sha order definitional constraint)

**Diagnostic:** The claim `(-1)^rank = root_number` on the sha ≥ 9 stratum is the BSD parity identity restricted to a sub-stratum. The sha ≥ 9 restriction is a stratum choice, not an additional claim.

**Caveat:** Sha values at rank ≥ 2 are themselves computed **assuming BSD** (per F003's own description quote: "circular at rank ≥ 2 — computed assuming BSD"). F005 is therefore circular on the rank ≥ 2 portion of its stratum. This does not make F005 a COUPLED specimen in the Pattern 30 sense — the circularity is a calibration-anchor design choice (testing whether the instrument correctly reports BSD parity on data that assumes BSD). It DOES mean F005 cannot be used to verify BSD itself on rank ≥ 2, which is already documented.

**Action:** none on the calibration status. Definitional-dependence annotation already present in F003 and F005 descriptions (Sha circularity note).

---

### F008 — Scholz reflection
**Status:** N/A — theorem (Scholz 1932 + Davenport-Heilbronn 1971)

**Diagnostic:** `|r3(K*) - r3(K)| ≤ 1` is Scholz reflection. 0 violations across 344,130 pairs is a theorem check.

**Action:** none.

---

### F009 — Torsion primes ⊆ nonmax primes
**Status:** N/A — theorem (Serre open-image 1972 + Mazur torsion 1977)

**Diagnostic:** `primes(E(ℚ)_tors) ⊆ nonmax_primes(E)` is a consequence of Serre's open-image theorem composed with Mazur's torsion classification. 100% across 1,385,133 non-CM EC is the theorem check.

**Action:** none.

---

### F010 — NF backbone via Galois-label (KILLED)
**Status:** CLEAN

**Diagnostic:** The claim (pre-kill) was `ρ(NF_features, Artin_features) > 0` via a Galois-label-keyed scorer. Neither side's variables are algebraically defined in terms of the other's. The kill was by block-shuffle showing the signal is degree-marginal, not an algebraic identity.

**Action:** none. Kill rationale is null-model-selection, not Pattern 30.

---

### F011 — GUE first-gap deficit (LAYER 1 calibration + LAYER 2 residual)
**Status:** CLEAN (both layers)

**Diagnostic LAYER 1:** the claim is that the first-gap variance deficit shrinks with conductor matches Duenez-HKMS (2011) excised-ensemble prediction. The deficit statistic is a moment of L-function zero spacings; the conductor is the archimedean normalization scale. Neither is defined in terms of the other. The match is to a predicted RMT form, not to an algebraic rearrangement. The +2 signal at z_block=111.78 on P028 reflects a real K-S class discrimination after conductor control.

**Diagnostic LAYER 2:** the rank-0 residual at 23-36% across decay ansatze is a statistical estimate of what remains after excision. Again no algebraic coupling between deficit statistic and rank or torsion.

**Action:** none.

---

### F012 — Möbius bias at g2c aut groups (KILLED)
**Status:** CLEAN

**Diagnostic:** Möbius-function bias claim did not reproduce at large n (z|=0.39); kill is Pattern 19 (stale / irreproducible). Not algebraic coupling.

**Action:** none.

---

### F013 — Zero-spacing rigidity vs rank; SO_even +0.01284 vs SO_odd −0.00216
**Status:** CLEAN

**Diagnostic:** the claim is `slope(zero_spacing_variance, rank)` differs by Katz-Sarnak symmetry class. The variance-of-zero-spacing and rank are not algebraically defined in terms of each other. Katz-Sarnak class on EC is determined by rank parity (via BSD), which means P028 aliases P023 (rank parity) on EC — but the claim is exactly about this rank-parity interaction. The null question ("is the slope difference real?") is valid; the stratifier question (`rank_bin`, not `conductor`) is addressed in `null_protocol_v1.md` Class 2.

**Action:** none on algebraic-coupling status. F013 flagged for null-stratifier re-audit under Class 2 in `cell_null_classification.json`.

---

### F014 — Lehmer spectrum (Salem density in (1.176, 1.228))
**Status:** CLEAN

**Diagnostic:** Lehmer-measure claims are existence claims about specific polynomials hitting specific Mahler measures. The degree, discriminant, and num_ram of each polynomial are catalogued facts; Mahler measure is a function of the polynomial's roots. No algebraic identity between "which polynomials exist at each Mahler value" and "the Mahler measure floor" — one is empirical, the other is analytic.

**Caveat from 2026-04-18 Charon upgrade:** the trinomial M(x^n - x - 1) floor converging to 1.381 is a theorem-like analytic result; F014's claim now incorporates this. Still CLEAN — the theorem is structural input to F014, not a Pattern 30 trap.

**Action:** none.

---

### F015 — Szpiro vs conductor, sign-uniform per bad-prime stratum
**Status:** PARTIAL

**Pattern 30 diagnostic:**
1. Write Y = szpiro_ratio in observable atomic quantities: `szpiro = log|Disc| / log(N)` where Disc is the minimal discriminant and N the conductor.
2. Does X = log(N) appear in Y? YES — as the denominator of szpiro_ratio.
3. Coefficient non-zero? YES.
4. Therefore `log(szpiro) = log(log|Disc|) - log(log(N))`. Correlating szpiro with conductor = N has an algebraic-dependence component through the `-log(log(N))` term.

**Why only PARTIAL, not COUPLED:** at fixed bad-prime count k, the relationship between Disc and N depends on the ramification pattern across the k bad primes. `log|Disc|` is not a pure function of `log(N)` within a k-stratum — the per-prime conductor exponent and discriminant exponent differ (conductor exponent = 1 for multiplicative, ≥ 2 for additive; discriminant exponent typically larger). The observed sign-uniform-negative slope within each k is not forced by algebra alone — it reflects the typical ratio of discriminant exponent to conductor exponent at each ramification type, which is partially theorem-driven (Ogg's formula) and partially empirical.

**What algebra forces:** some negative slope is expected when szpiro is plotted against log(N) even under a uniform-ratio null, via the definitional dependence through the denominator.

**What algebra does NOT force:**
- The magnitude of the slope (F015 observed ranges -0.13 to -0.49 per k)
- The strict sign-uniformity across all k strata (this is empirical given Ogg)
- The non-monotonicity of magnitude in k (k=4 breaking the trend)

**F028 precedent:** F028 (Szpiro × Faltings) is the COUPLED anchor — `faltings ≈ (1/12) log|Disc| + const` and `szpiro = log|Disc| / log(N)` both encode `log|Disc|`; correlating them after partial log(N) control leaves log|Disc| as a shared driver. F015 is different: its two variables are szpiro (which contains log|Disc|) and N (which contains log(N) = szpiro's denominator). The dependence is through the denominator, weaker than F028's shared-numerator dependence.

**Recommendation:**
- Add a definitional-dependence annotation to F015 description: "The szpiro ratio contains log(N) in its denominator; some negative slope is expected algebraically. The PARTIAL-Pattern-30 status is the sign-uniformity AND non-monotone-magnitude of the slope, which is NOT forced by algebra."
- Do NOT retract. The sign-uniform claim retains value as an empirical-given-Ogg observation and the block-shuffle at each k-stratum (z ∈ [-24.03, -3.48]) remains meaningful.
- Sign goes to sessionA: is the above annotation sufficient, or should F015's +2 cells be downgraded to +1 to reflect the PARTIAL status?

**Action pending sessionA review:** annotation draft above. No unilateral demotion.

---

### F020 — Megethos axis (KILLED — artifact)
**Status:** CLEAN (the kill rationale is already "artifact of cosine on magnitude-sorted vectors" — a coordinate-system artifact, not a Pattern 30 algebraic identity)

**Action:** none.

---

### F021 — Phoneme framework (KILLED — artifact)
**Status:** CLEAN. Trivial 1D predictor giving ρ=1.0 is a coordinate-choice artifact, not algebraic identity.

**Action:** none.

---

### F022 — NF backbone via feature distribution (KILLED)
**Status:** CLEAN. z=0.00 under permutation on feature-distribution scorer is scorer-collapse, not algebraic coupling.

**Action:** none.

---

### F023 — Spectral tail ARI=0.55 (KILLED by conductor conditioning)
**Status:** CLEAN. Kill rationale is conductor-mediation, not algebraic identity.

**Action:** none.

---

### F024, F025 — Faltings / ADE don't explain GUE (KILLED)
**Status:** CLEAN for both. Kill rationales are "wrong axis class" (Pattern 13), not algebraic coupling.

**Action:** none.

---

### F026 — Artin dim-2/dim-3 proof-frontier ratio (KILLED)
**Status:** CLEAN. Kill rationale is wrong-framing ("proof frontier" reframing failed), not algebraic identity.

**Action:** none.

---

### F027 — Alexander Mahler × EC L-value (KILLED)
**Status:** CLEAN. Kill rationale is `Alexander has cyclotomic gap, no Lehmer probing` — a structural incompatibility of the polynomial projection, not a Pattern 30 identity.

**Action:** none.

---

### F028 — Szpiro × Faltings coupling (KILLED — tautology)
**Status:** COUPLED (pre-existing, already retracted as Pattern 1 canonical case)

**Diagnostic:** F028 description quote: `ρ=0.97 after partial control — but both sides encode log|Disc|. Near-identity, not cross-domain.` This is Pattern 30 avant-la-lettre (and Pattern 1 anchor). `szpiro = log|Disc| / log(N)` and `faltings ≈ (1/12) log|Disc| + const`. After controlling for log(N), both are linear in log|Disc|, so ρ=0.97 is algebraically forced.

**Action:** no change. F028 is the pre-existing COUPLED anchor (alongside F043). Its killed status and description are already correct.

---

### F030 — Delinquent EC (no L-function data)
**Status:** CLEAN. This is a data-frontier claim (coverage gap), not a correlation. Pattern 30 does not apply.

**Action:** none.

---

### F031 — Object zeros_vector corruption
**Status:** CLEAN. This is a data-audit observation (Mnemosyne 2026-04-16), not a correlation claim.

**Action:** none.

---

### F032 — Knot silence (persistent null result)
**Status:** CLEAN. Null findings across every projection — no correlation claim to check.

**Action:** none.

---

### F033 — rank ≥ 4 coverage cliff
**Status:** CLEAN. Data-frontier observation.

**Action:** none.

---

### F041a — Rank-2+ moment slope monotone in num_bad_primes
**Status:** PARTIAL

**Pattern 30 diagnostic:**
1. Write Y = slope of M_1(log X) vs log-conductor in terms of atomic quantities. M_1 = mean of leading_term; X = conductor. The slope is `d⟨leading_term⟩ / d(log N)` at fixed (rank, nbp).
2. Does X = num_bad_primes appear in Y? NOT DIRECTLY. But `log N = Σ_{p|N} v_p(N) · log p`, and `num_bad_primes = |{p : p | N}|`. So log N and nbp are not algebraically equivalent, but log N is structurally constrained by nbp (can't have many bad primes with small log N; can't have few bad primes with large log N at typical conductor exponents).
3. Coefficient non-zero? The structural link is real but not an identity. Within a fixed rank and a fixed conductor decile, `nbp` ranges over several values (typical 1-6) with real variation. The slope-vs-nbp ladder is NOT produced by the log(N) component of nbp alone.
4. Additional consideration: the Keating-Snaith moment `M_1` for a rank-r family should converge as `(log X)^{r(r+1)/2}` under CFKRS. `M_1 / (log X)^{r(r+1)/2}` is the "moment ratio" R_1 whose slope F041a measures. Is there an algebraic dependence of R_1 on nbp? Through the arithmetic factor `a_E(1)` in CFKRS, YES — the arithmetic factor is an Euler product over bad primes with explicit nbp dependence. So the slope CAN depend on nbp through the CFKRS arithmetic factor.

**Why only PARTIAL:**
- The claim is "monotone ladder at rank 2" with specific slope values nbp=1:1.21 → nbp=6:2.52.
- CFKRS predicts SOME dependence of slope on nbp via the arithmetic factor.
- The remaining F041a Pattern 5 gate (CFKRS rank-2 SO(even) closed-form) is exactly the question of whether the observed ladder matches the CFKRS prediction. If CFKRS predicts the observed ladder, F041a collapses to calibration — which would be the benign form of Pattern 30 (known theorem predicts the effect).
- U_E (07a5a738) already showed pure-RMT SO(2N) MC diverges from empirical at k=3,4. Pure RMT is NOT the calibration baseline; CFKRS with arithmetic factor IS.
- Under current state (Pattern 5 gate open): F041a has potential algebraic dependence that could collapse the finding.

**Crucial distinction from F043:** F043 was a DEFINITIONAL identity (rearrangement of BSD statement); no further test could rescue it. F041a's potential algebraic dependence is through an arithmetic-factor convolution, which is an EMPIRICAL-prediction from theory — the CFKRS side has to be computed and compared, not just spotted.

**Recommendation:**
- Add a definitional-dependence annotation to F041a description (already partially present: "Pattern 5 gate ... remaining open hurdle").
- Do NOT retract. Pattern 30 status is PARTIAL-pending-Pattern-5.
- When CFKRS closed-form arrives: if it predicts the observed ladder, demote to calibration (benign-Pattern-30). If it does not predict or predicts a different shape, F041a is fully CLEAN under Pattern 30 and the Pattern 5 gate closes negatively (meaning F041a is genuinely frontier).
- Sign goes to sessionA: keep as PARTIAL until CFKRS gate closes.

**Action pending sessionA review:** no unilateral demotion. Annotation recommendation as above.

---

### F042 — CM disc=-27 L-value depression
**Status:** CLEAN under Pattern 30 (but note: description already self-identifies as "calibration_refinement" not frontier)

**Diagnostic:** The 6.66x enrichment is Deuring non-maximal-order character-sum compression (Gross 1980, RVZ 1993). This is a theorem-predicted effect, not an algebraic identity between the two variables being correlated.

**Action:** none. F042 description correctly self-describes as quantitative precision on known qualitative effect.

---

### F043 — BSD-Sha anticorrelation with period (RETRACTED 2026-04-19)
**Status:** COUPLED (retracted, already documented)

**Diagnostic (already recorded):** `A := Ω · ∏c_p`. BSD full identity: `L^(r)/r! = Ω · Reg · ∏c_p · |Sha| / |Tor|²`. So `log A = log L + 2 log|Tor| - log Reg - log |Sha|`. The `-log |Sha|` term is algebraically present; `corr(log Sha, log A) = -0.4343` at `z_block = -348` is the BSD identity in rearranged coordinates.

**Action:** none. F043 is the Pattern 30 DRAFT anchor case; retraction is recorded in `decisions_for_james.md` 2026-04-19 post-review entry.

---

### F044 — Rank-4 corridor: disc=conductor exactly (2085/2086)
**Status:** CLEAN under Pattern 30 (but see Class 4 construction-bias concern in `cell_null_classification.json`)

**Diagnostic:** The claim is observational: 2085/2086 rank-4 EC in LMFDB have `disc == conductor` (no additive reduction). No correlation between two defined variables; it's a count within a catalogued sample. Pattern 30 does not apply.

**Separate concern (Class 4, not Pattern 30):** the sample may be construction-biased. That is a frame-validity concern, not an algebraic-identity concern. Handled in `cell_null_classification.json`.

**Action:** none on Pattern 30 grounds.

---

### F045 — Isogeny-class murmuration (5/21 primes significant)
**Status:** CLEAN

**Diagnostic:** the claim is that stratification by isogeny class size reveals non-chance per-prime significance. Class size and per-prime a_p values are not algebraically defined in terms of each other.

**Separate concern:** multiple-testing correction (flagged in F045 description), not algebraic identity.

**Action:** none on Pattern 30 grounds.

---

## Conclusions

1. **No new F043-class specimen detected.** F028 was already known COUPLED; F043 is freshly retracted. Every other F-ID involving BSD factors or Euler-product rearrangements (F003, F005, F041a, F042, F043, F044) has been checked.
2. **Two PARTIAL cases for sessionA attention:** F015 (szpiro has log(N) in denominator; some negative slope is algebraically expected) and F041a (CFKRS arithmetic factor can predict the nbp ladder; Pattern 5 gate is exactly this check).
3. **Definitional-dependence annotation recommended** for F015 and F041a descriptions. Draft text provided in each entry above. Decision to apply is sessionA's, not this pass's.
4. **F005 circularity note** already present in F003 description. No action needed but worth re-reading: F005 cannot verify BSD on rank ≥ 2 because Sha is computed assuming BSD on that stratum.
5. **Calibration anchors F001-F009 are intentionally algebraic identities.** Their Pattern 30 "status" is by design; downstream analyses that cluster Pattern-30-CLEAN cells should treat them as a separate semantic class (flagged in `null_protocol_v1.md`).

## Next audit trigger

Re-run this audit when any of the following occur:
- New F-ID opened that involves BSD factors, L-value rearrangements, or Euler-product identities
- Pattern 30 promoted from DRAFT to FULL (would require a second anchor; this audit found none)
- F041a Pattern 5 gate closes (CFKRS closed-form arrives) — F041a's status will resolve to CLEAN or to benign-known-math, but needs re-categorization either way
- External review flags a PARTIAL or CLEAN finding as potentially algebraic — the F043 retraction suggests our in-house Pattern 30 detection may miss some cases

---

*End of audit. Retraction recommendations: none. Annotation recommendations: F015, F041a (sessionA decides). Flag for sessionA conductor: the Pattern 5 gate on F041a is now also the Pattern 30 gate on F041a; CFKRS result binary-closes both.*
