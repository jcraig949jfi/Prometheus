# Congruence Enrichment Linearity — Finding Report
## 2026-04-12 | M1 (Skullport)

---

## The Observation

When pairs of automorphic forms are compared mod p, the fraction of coefficients
that agree exceeds the random baseline (1/p) by a factor that grows linearly with p.

| Prime p | EC enrichment | Maass enrichment | Ramanujan prediction |
|---------|---------------|------------------|---------------------|
| 2 | 1.29x | 1.04x | ~1.0x |
| 5 | 1.58x | 1.42x | 1.0x |
| 11 | 2.69x | 3.03x | 1.1x |
| 23 | 5.46x | 6.34x | 1.2x |
| 47 | 11.10x | 12.95x | 1.7x |

Best fit: E(p) = slope * p + intercept

| Family | Slope | R² | Intercept |
|--------|-------|----|-----------|
| EC (weight-2, dim-1) | 0.220 | 0.997 | 0.450 |
| Maass (rounded coefficients) | 0.269 | 0.999 | 0.168 |
| Moonshine (McKay-Thompson) | 0.038 | 0.812 | 1.16 |

## The Mechanism

The Ramanujan bound constrains |a_p| <= 2*sqrt(p). For large p, this means
the coefficients live in a range of size ~4*sqrt(p) while there are p possible
residues mod p. The collision probability for two independently sampled
coefficients is:

P(match) = sum_r P(a mod p = r)^2 = HHI of the mod-p residue distribution

For coefficients uniform on [-2sqrt(p), 2sqrt(p)]:
  - ~4sqrt(p) integers in range, p residues
  - HHI ~ 1/(4sqrt(p))^2 * p = 1/16
  - E(p) = P(match) / (1/p) = p * HHI = p/16

This predicts slope = 1/16 = 0.0625. Measured slopes are 3.5-4.3x larger.

**The excess is Sato-Tate concentration.** Real coefficients follow a semicircular
(or variant) distribution, concentrating near 0 more than uniform would.
This increases HHI by a factor of ~3.5-4.3, explaining the measured slopes.

Maass slope (0.269) > EC slope (0.220) because Maass coefficients are real
numbers rounded to integers, creating additional concentration near 0.

## Controls

| Control | Result | Interpretation |
|---------|--------|----------------|
| Level dependence | Slope varies 0.20-0.23 across quartiles | WEAK — not a level artifact |
| Anti-matched magnitudes | 70% of enrichment survives | NOT just size matching |
| Quadratic term | ~0.001*p² | Slight super-linearity, consistent with ST |
| F24 family->enrichment | eta²=0.012 | EC and Maass are similar |
| F25 across families | OOS R²=-0.05 | Mappings are family-specific at the margin |

## Classification

**KNOWN CONSEQUENCE** — the linearity follows from Ramanujan bound + Sato-Tate.
Not a novel discovery. However:

- The slope (0.22 for EC, 0.27 for Maass) is a **measurable invariant** of
  the coefficient distribution's concentration relative to the Ramanujan bound
- The 70% anti-matched survival shows genuine residue-class structure beyond
  simple magnitude matching
- The slope ratio (Maass/EC = 1.22) quantifies the relative tail heaviness

## What This Taught Us

1. Linear-in-p growth from Ramanujan is inevitable — don't claim it as a finding
2. The SLOPE is the invariant, not the linearity
3. Anti-magnitude-matching is a useful control for any mod-p analysis
4. The pipeline correctly identified the pattern but needed the theoretical model
   to classify it as known rather than novel

---

*Documented: 2026-04-12, M1 (Skullport)*
