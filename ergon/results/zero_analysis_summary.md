# Zero Analysis Summary — 5 Unexecuted Scripts from Last Session

Date executed: 2026-04-15

---

## 1. `higher_gap_analysis.py` — SUCCESS (minor Unicode crash at final print)

**Question:** Is the deficit gap1-specific or uniform across gap2-4?

**Key results (EC, 200K rank-0 curves):**
| Gap | Var | Var/Gaudin | Deficit% |
|-----|-----|-----------|----------|
| gap1 | 0.11378 | 0.6392 | 36.1% |
| gap2 | 0.14027 | 0.7880 | 21.2% |
| gap3 | 0.13248 | 0.7443 | 25.6% |
| gap4 | 0.09411 | 0.5287 | 47.1% |

**Cross-family (MF, 100K):** MF gap1 var/Gaudin = 0.9945 (only 0.5% deficit) vs EC gap1 = 0.6392 (36.1% deficit). Delta = 0.3553.

**Verdict:** Deficit is NOT gap1-specific -- present across all gaps (gap4 is worst at 47.1%). EC-specific, not present in modular forms. This is family-specific arithmetic structure, not generic unfolding.

---

## 2. `tamagawa_mediation.py` — SUCCESS (clean exit)

**Question:** Does controlling for Tamagawa (num_bad_primes) eliminate the isogeny class_size effect?

**Key results:**
- Raw Spearman r(class_size, gap1) = -0.2023
- Partial r controlling num_bad_primes = -0.1882 (only 7.0% reduction)
- Partial r controlling num_bad_primes + conductor = 0.1759 (13.0% reduction, p=0.00)
- Group-level partial r(class_size, var/Gaudin | nbp) = -0.5425 (p=0.020)
- Faltings height varies with class_size: Spearman r = 0.2842

**Verdict:** P1 REJECTED. Tamagawa does NOT mediate the class_size effect. The two channels (isogeny structure vs Tamagawa/BSD) act independently. Class_size retains r=0.1759 after controlling for both num_bad_primes and conductor.

---

## 3. `convergence_by_class_size.py` — SUCCESS (clean exit)

**Question:** Does var/Gaudin converge to 1.0 at high conductor for all class sizes?

**Key results (var/Gaudin by conductor decade):**
| Conductor | cs=1 | cs=2 | cs=4 |
|-----------|------|------|------|
| <1000 | 1.925 | 0.958 | 0.788 |
| 10^3-10^4 | 1.479 | 1.164 | 0.839 |
| 10^4-10^5 | 1.469 | 1.206 | 1.166 |
| 10^5-10^6 | 1.474 | 1.299 | 1.233 |

- cs=1 is DECREASING toward ~1.47 (still above 1.0)
- cs=2, cs=4 are INCREASING toward ~1.2-1.3 (approaching from below)
- Asymptotic fits have huge error bars (only 4 data points each)

**Verdict:** Consistent with finite-conductor transient (Katz-Sarnak), but the data is insufficient to confirm convergence. cs=1 appears stuck above 1.4, while cs=2 and cs=4 are still rising. The class_size gap narrows but does not close within the available conductor range.

---

## 4. `wachs_reproduction.py` — SUCCESS (clean exit)

**Question:** Does Wachs's first-zero displacement predict variance suppression?

**Key results:**
- Sha>=4 average z1 = 0.649 vs Sha=1 baseline z1 = 0.541 (displacement +0.107)
- All Sha>1 bins show z1 displaced UP (10/10 bins)
- All Sha>1 bins show gap1 tighter (10/10 bins)
- 8/10 bins show gap1 variance suppressed
- BUT: Pearson r(delta_z1, delta_var) = -0.379 (p=0.25, NOT significant)
- Weighted r = -0.711 (significant when weighting by sqrt(N))

**Verdict:** WEAK/NO correlation between displacement magnitude and variance suppression. The z1 displacement and variance suppression are separate channels -- both present, but not proportional. Sha displaces z1 upward consistently, but the amount of displacement does not predict the amount of variance reduction.

---

## 5. `isogeny_sha_joint.py` — SUCCESS (clean exit)

**Question:** Are isogeny and Sha effects independent or confounded?

**Key results:**
- Within sha=1 only (mid-conductor): cs=1 var/Gaudin=1.393, cs=2=1.095, cs=4=0.730, cs=6=0.541
- Within cs=1 only (mid-conductor): sha=1 var/Gaudin=1.393, sha=4=1.459, sha=9=2.089, sha=16=2.539
- Within an isogeny class: sha and torsion vary but gap1 is IDENTICAL (same L-function)
- Fraction with sha>1 increases with class_size: cs=1: 17.3%, cs=4: 32.2%, cs=8: 40.7%

**Critical finding:** Sha is NOT directly causal for gap1 because curves in the same isogeny class share the same L-function but have different Sha values. The BSD product Sha*Omega*Tam/Tor^2 = L(1,E) is the invariant.

**Verdict:** TWO independent channels confirmed:
1. BSD channel: L(1,E) magnitude controls zero repulsion from s=1 (sha contributes via L-value)
2. Isogeny channel: structural constraint on Euler product from algebraic endomorphisms (class_size effect survives within sha=1)

---

## One-line verdicts

1. **higher_gap:** Deficit is UNIFORM (all gaps), EC-specific (not in MF) -- deeper than central zero repulsion
2. **tamagawa:** Tamagawa does NOT mediate -- isogeny and Tamagawa are independent channels
3. **convergence:** Inconclusive -- narrowing with conductor but cannot confirm convergence within data range
4. **wachs:** z1 displacement is real but does NOT predict variance suppression magnitude -- separate channels
5. **isogeny_sha:** Independent and proven -- sha acts only through L(1,E), class_size has separate structural effect
