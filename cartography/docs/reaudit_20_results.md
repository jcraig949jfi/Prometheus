# Re-Audit of 20 Findings with F24
## 2026-04-12 — The samples re-examined with the upgraded microscope

---

## The Instrument Upgrade

Before F24: all "PROBABLE" findings looked the same.
After F24: findings are classified by **effect geometry** — LAW / CONSTRAINT / TENDENCY / NEGLIGIBLE.

---

## Results

| ID | Claim | eta² | Type | F24b | Tail% |
|----|-------|------|------|------|-------|
| **C85** | SC class → Tc | **0.570** | **LAW** | CONSISTENT | 77% |
| **C32** | Space group → Tc | **0.457** | **LAW** | CONSISTENT | 76% |
| **C38v** | Space group → Cell volume | **0.394** | **LAW** | CONSISTENT | 82% |
| **C4** | N_elements → Tc | **0.329** | **LAW** | CONSISTENT | 77% |
| **C38f** | Space group → Formation energy | **0.328** | **LAW** | CONSISTENT | 13% |
| **C35** | Crossing number → determinant | **0.219** | **LAW** | CONSISTENT | 38% |
| **C38d** | Space group → Density | **0.190** | **LAW** | CONSISTENT | 59% |
| C36 | Galois group → class number | 0.138 | TENDENCY | CONSISTENT | 76% |
| C36c | NF degree → class number | 0.138 | TENDENCY | CONSISTENT | 76% |
| C59 | Crystal system → Tc | 0.128 | TENDENCY | CONSISTENT | 77% |
| C32b | Space group → Band gap | 0.096 | TENDENCY | CONSISTENT | 100% |
| G2to | ST group → torsion order | 0.084 | TENDENCY | CONSISTENT | 86% |
| C50 | ST group → conductor | 0.013 | CONSTRAINT | TAIL_DRIVEN | 42% |
| EC_to | Torsion → conductor | 0.013 | CONSTRAINT | TAIL_DRIVEN | 24% |
| EC_rk | Rank → conductor | 0.011 | TENDENCY | CONSISTENT | 24% |
| C50d | ST group → |discriminant| | 0.005 | CONSTRAINT | TAIL_DRIVEN | 28% |
| NFdd | NF degree → |discriminant| | 0.004 | NEGLIGIBLE | CONSISTENT | 24% |
| EC_cm | CM → conductor | 0.003 | NEGLIGIBLE | CONSISTENT | 24% |
| EC_ss | Semistable → conductor | 0.003 | NEGLIGIBLE | CONSISTENT | 24% |

---

## Meta-Analysis: What does our discovery process produce?

| Type | Count | Fraction |
|------|-------|----------|
| **LAW** | 7 | 35% |
| **CONSTRAINT** | 3 | 15% |
| **TENDENCY** | 6 | 30% |
| **NEGLIGIBLE** | 4 | 20% |

### The 7 LAWS (eta² > 0.14, not tail-driven)

These are **dominant organizing principles** — remove them and understanding collapses:

1. **SC class → Tc (eta² = 0.570):** Chemical family is the STRONGEST predictor of Tc. Stronger than space group.
2. **SG → Tc (eta² = 0.457):** Crystal symmetry explains 46% of Tc variance.
3. **SG → Cell volume (eta² = 0.394):** Space group strongly constrains lattice geometry.
4. **N_elements → Tc (eta² = 0.329):** Compositional complexity predicts Tc. Independent pathway.
5. **SG → Formation energy (eta² = 0.328):** Space group constrains thermodynamic stability.
6. **Crossing number → determinant (eta² = 0.219):** Knot complexity organizes determinants.
7. **SG → Density (eta² = 0.190):** Space group constrains mass packing.

### Key finding: Space group is a LAW-level predictor for 5 properties

SG explains >14% of variance for Tc, cell volume, formation energy, density, AND (borderline) crystal system → Tc. Band gap is the outlier (eta² = 0.096, TENDENCY).

**The original claim "SG predicts Tc but nothing else" is definitively wrong.** SG is a strong predictor of multiple material properties. The correct statement: SG is a **general organizing principle** for crystalline materials, not specific to superconductivity.

### What's actually specific to superconductivity?

**SC class (chemical family) → Tc is the strongest effect (eta² = 0.570).** Cuprates, iron-based, heavy fermions, etc. are the primary organizer. SG is secondary.

### The Galois enrichment surprise

C36 (Galois group → class number) was **KILLED by F17** in the earlier session (degree confound). But F24 shows eta² = 0.138 — borderline TENDENCY. And C36c (degree → class number) has the SAME eta² = 0.138. **This confirms the kill**: Galois and degree explain the same variance. They're not independent.

### The collapsed discoveries (Pattern A from the council)

- **C50 (ST → conductor):** Looked like a 3.63× M4/M2² ratio. Actually eta² = 0.013. **CONSTRAINT.**
- **C50d (ST → discriminant):** Looked significant. Actually eta² = 0.005. **CONSTRAINT.**
- **EC_cm (CM → conductor):** Looked like a finding. Actually eta² = 0.003. **NEGLIGIBLE.**

These are the amplification artifacts the council warned about.

---

## What Changed vs Previous Understanding

| Finding | Before F24 | After F24 | Shift |
|---------|-----------|-----------|-------|
| SG → Tc | PROBABLE | **LAW** (eta²=0.457) | Upgraded — dominant effect |
| SG → Band gap | "null" | TENDENCY (eta²=0.096) | Upgraded — weak but real |
| SG → Volume | Not tested | **LAW** (eta²=0.394) | New finding |
| SG → Formation E | Not tested | **LAW** (eta²=0.328) | New finding |
| SG → Density | Not tested | **LAW** (eta²=0.190) | New finding |
| SC class → Tc | Conjecture | **LAW** (eta²=0.570) | Major upgrade — strongest effect |
| N_elements → Tc | r=0.37 non-cuprate | **LAW** (eta²=0.329) | Major upgrade |
| ST → conductor | PROBABLE | CONSTRAINT (eta²=0.013) | **Downgraded** — tail artifact |
| ST → discriminant | Fiber ratio finding | CONSTRAINT (eta²=0.005) | **Downgraded** — tiny effect |
| Galois → class number | KILLED | TENDENCY (eta²=0.138) | Correctly killed — same as degree |
| CM → conductor | Finding | NEGLIGIBLE (eta²=0.003) | **Collapsed** |

---

## The Systematic Bias We Found

The pipeline was seeded by M4/M2², which is a tail-sensitive contrast amplifier. This produced:

- **Overrepresentation of CONSTRAINT-type findings** (tail effects amplified into "discoveries")
- **Underrepresentation of LAW-type findings** (strong bulk effects not highlighted because they looked "obvious")

The 7 LAWS found here include 4 that were never prominently featured (SG → volume, SG → formation energy, SG → density, SC class → Tc) because the pipeline wasn't looking for high-eta² bulk effects.

**The council was right: we had a detection bias.**

---

*20 findings re-audited. 7 LAWS, 3 CONSTRAINTS, 6 TENDENCIES, 4 NEGLIGIBLE.*
*The strongest finding (SC class → Tc, eta²=0.570) was barely mentioned before.*
*The most-discussed finding (ST → conductor ratio) is a CONSTRAINT (eta²=0.013).*
*The instrument correction revealed what the pipeline's geometry of attention had hidden.*
*2026-04-12*
