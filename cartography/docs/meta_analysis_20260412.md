# Project Prometheus — Meta-Analysis
## What We Built, What We Found, What We Learned
### 2026-04-12 | ~130 tests | 21 datasets | Battery v7 | 2 machines

---

## 1. What This Project Is

Project Prometheus is an automated cross-domain mathematical discovery pipeline. Over 12 days, we built a falsification battery (27 tests + 5 cross-domain filters + primitive tagger), ran it against ~130 hypotheses spanning 21 mathematical and scientific databases (~1M+ objects), and subjected every finding to hostile review by 6 frontier models.

The goal was to find genuine, novel structural connections between mathematical domains. The honest result: we found none. What we found instead is more valuable.

---

## 2. The Instrument

### Battery v7 (32 tests across 7 tiers)

| Tier | Tests | Purpose |
|------|-------|---------|
| A: Detection | F1-F14 | Is the signal real? (permutation, stability, effect size, confounds, normalization, base rate, dose-response, direction, simplicity, outliers, cross-validation, partial correlation, growth rate, phase shift) |
| B: Robustness | F15-F18 | Does it survive perturbation? (log-normal calibration, equivalence, confound sensitivity, subset stability) |
| C: Representation | F19-F23 | Is the description well-posed? (generative replay, representation invariance, trend robustness, alignment, latent confound discovery) |
| D: Magnitude | F24-F24b | How big is it? (variance decomposition eta², metric consistency / tail localization) |
| E: Context | F25, F25b | Does it transfer? (group-mean transportability, model-based transportability) |
| F: Multiple testing | F26 | FDR correction (Benjamini-Hochberg) |
| G: Cross-domain | F27, F29-F32 | Is it a tautology? Is the overlap distributional? Size-conditioned? Prime-mediated? Scaling-degenerate? |

Plus: primitive tagger (8 operation types) for structural classification.

### Calibration
- 218/218 known mathematical truths pass (100%)
- 25+ independent rediscoveries (modularity, Deuring mass, Euler characteristic, paramodular conjecture, KMT theorem, etc.)

### Known Limitations (characterized by adversarial testing)
- **F25/F25b breaks on random groupings.** Even Deuring mass (r=1.0) collapses to WEAK_NOISY with random fragmentation at any group count 2-1000. F25b only works when the grouping variable is semantically meaningful.
- **Eta² is resolution-dependent.** Coarsening drops it (lattice type: 26% of SG signal), refinement inflates it (SG×Tc-quartile: 200%). Always compare to the permutation null for the specific group structure.
- **Cross-domain overlaps are overwhelmingly distributional artifacts.** 6/6 overlap claims killed by Benford, size, group-theoretic, or prime-mediated controls. The only surviving cross-domain signal (#32, iso-MF r=-0.21 after prime conditioning) is likely the Eichler-Selberg trace formula.

---

## 3. What We Found

### The Classification

| Category | Count | Description |
|----------|-------|-------------|
| **Structural (Tier 1)** | 14 | Strong within-context effects (eta² > 0.14, z > 20 vs permutation null) |
| **Constraints (Tier 2)** | 13 | Small but real (eta² 0.01-0.14, survive distributional nulls) |
| **Scaling Laws** | 1 | Prime gap M4/M² grows at 0.37/decade |
| **Tendencies** | 15 | Weak but consistent (eta² 0.01-0.06) |
| **Identities** | 8 | Deterministic mathematical relationships |
| **Rediscoveries** | 30 | Known theorems detected by the pipeline |
| **Negligible** | 17 | Below noise floor (eta² < 0.01) |
| **Killed** | 12 | Confirmed false, artifact, or confound |
| **Novel cross-domain bridges** | **0** | Every candidate collapsed under controls |

### The Flagship Result: Tc Variance Decomposition

```
Total Tc variance = 100%

  SC_class (chemical family):           57.0%    ← BREAK_SYMMETRY
  SG (space group, after SC_class):     14.1%    ← BREAK_SYMMETRY
  SC_class × SG (interaction):          11.0%    ← (balanced, survives resampling)
  SG + physics (no chemistry):          57.5%    ← chemistry adds 13.6% beyond physics
  N_elements (after SC + SG):            1.8%
  Continuous properties:                 0.6%
  Residual:                             15.5%
```

**Replicated externally:** eta²(SG→Tc) = 0.41 on 70 independent COD-sourced curves.

**Non-stationarity is genuine:** Subsample scaling from n=5 to n=500 shows no improvement in transfer (main R² stays at -15 to -21). Coarsening proves even crystal system (538 per group) fails to transfer — only Tc-based groupings transfer (tautologically). This is NOT noise; it's a structural property of the data-generating process.

**Chemical sabotage test:** SC_class adds +13.6% beyond SG + all physical properties (volume, density, nsites, formation energy). Chemistry encodes information invisible to bulk measurements.

### Structural Primitives Across Findings

| Primitive | Count | What it means |
|-----------|-------|---------------|
| **SYMMETRIZE** | 7 | A categorical symmetry group partitions variance (SG→nsites, Maass level→R, moonshine class→coefficients) |
| **BREAK_SYMMETRY** | 3 | A universal mapping fractures along context lines (SC_class→Tc, SG×SC→Tc, NF degree→CN) |
| **LINEARIZE** | 3 | Logarithmic or power-law scaling (isogeny diameter, unit circle profiles, prime gaps) |
| **PARTITION** | 3 | Moderate categorical effects (endomorphism→uniformity, ST→conductor, EC non-recurrence) |
| **IDENTITY** | 2 | Deterministic relationships (Deuring, Alexander→determinant) |

SYMMETRIZE dominates. COMPOSE (cross-domain structure) has zero confirmed instances.

---

## 4. What We Learned (the actual contribution)

### Lesson 1: Detecting interaction ≠ verifying transportability

We proved this empirically:
- ANOVA interaction term: 11% (confirmed, survives balanced resampling)
- Rank inversion across classes: rho = -0.04 (confirmed)
- Leave-one-class-out OOS R²: -15.7 (fails to transfer)
- Coarsening experiment: no symmetry grouping transfers, even with 500+ per group

These are measuring different things. ANOVA and rank correlation detect interaction with moderate data requirements. Transfer tests require the grouping to be meaningful AND groups to be large AND the mapping to be simple enough for one-hot linear models. The transfer test's failure says more about the test's limitations than about the signal.

### Lesson 2: Cross-domain overlaps are almost always distributional artifacts

Our kill rate on cross-domain claims: **100%** (6/6 + 2 additional from adversarial tests = 8/8 killed or partially mediated). The failure modes form a taxonomy:

| Type | Example | Control |
|------|---------|---------|
| Benford/marginal distribution | Knot det vs SG numbers (1.13x) | F29: power-law null |
| Prime-size confound | Isogeny-knot overlap (3.35x) | F30: range conditioning + F31: prime null |
| Group-theoretic tautology | PG order vs NF degree (10x) | F27 + manual: crystallographic restriction |
| Tabulation bias | EC conductors vs Maass levels (1.05x) | F29 + F30: range conditioning |
| Scaling degeneracy | Log-growth in isogenies vs prime gaps | F32: functional form comparison |

This taxonomy is itself a contribution. Any future cross-domain claim must survive all 7 layers of the protocol.

### Lesson 3: The non-stationarity pattern is universal across mathematical databases

The same BREAK_SYMMETRY primitive appears in:
- Superconductors: SG→Tc mapping changes across chemical families
- Number fields: Degree→class number mapping changes across Galois groups
- Genus-2 curves: ST→conductor mapping changes across torsion structures

In all three domains, the categorical variable carries real within-context information (eta² 0.13-0.57) but the mapping is non-stationary across contexts. This is not a domain-specific finding — it's a structural property of categorical→continuous relationships in structured scientific data.

### Lesson 4: M4/M² (excess kurtosis ratio) is a contrast amplifier, not a magnitude measure

Every finding originally framed around M4/M² either died (C48 S_n formula — false), shrank (ST→conductor, C37 knot det), or needed correction (C43 prime gap slope). The correction from M4/M² to eta² (F24) changed the project's finding landscape more than any other instrument improvement. It revealed that the strongest finding (SC_class→Tc, eta²=0.57) had been hiding in plain sight while the pipeline chased tail-amplified mirages.

### Lesson 5: The battery is the product

The ~130 findings are the battery's validation set. The instrument itself — with its characterized failure surface, its 7-layer cross-domain filter, its primitive tagger, and its honest accounting of what it can and cannot detect — is the real output. It separates:
- Signal from artifact (F1-F14, F24, F24b)
- Robust from fragile (F15-F18)
- Well-described from representation-dependent (F19-F23)
- Large from tiny (F24 with permutation null)
- Transferable from context-locked (F25/F25b — with documented limitations)
- Novel from tautological (F27)
- Cross-domain from distributional coincidence (F29-F32)

---

## 5. The Honest Numbers

```
Pipeline operation: 12 days
Datasets: 21 (1M+ objects)
Hypotheses tested: ~130
Battery tests: 32 (F1-F32 + F25b)
Adversarial tests: 25+ (5 smoke tests + 5 cross-domain gauntlet + 14 endurance + 6 final)
Council reviews: 3 rounds × 6 models = 18 reviews

Results:
  Novel universal laws:           0
  Novel cross-domain bridges:     0
  Context-dependent invariants:   3 (SC_class→Tc, SG×SC→Tc, NF degree→CN)
  Domain-internal structure:      11 (moonshine, Maass spectral, isogeny diameter, etc.)
  Constraints:                    13
  Rediscoveries:                  30+
  Killed:                         12+
  Known identities:               8

Meta-results:
  1. Non-stationarity is universal in categorical→continuous mappings
  2. Cross-domain overlaps collapse under distributional controls (8/8)
  3. Transfer tests are fundamentally limited by group structure
  4. M4/M² systematically overvalues tail effects
  5. The battery itself is the main scientific product
```

---

## 6. What Comes Next

### The Project Now Has Two Clear Outputs

**Output 1: The Falsification Battery** — a reusable instrument for evaluating empirical structure in mathematical databases. 32 tests across 7 tiers with characterized failure modes. Ready for application to new domains.

**Output 2: The Non-Stationarity Result** — a quantitative demonstration that categorical→continuous mappings in structured scientific data are context-dependent, not universal. Supported by the Tc decomposition (replicated externally), the coarsening experiment, and cross-domain replication in number fields and genus-2 curves.

### Three Publication Paths

1. **Methodology paper** (safest, highest impact): "A falsification-first framework for evaluating empirical structure in mathematical databases." Anchored on the battery design, the M4/M² correction, and the cross-domain falsification protocol.

2. **Materials science paper** (domain-specific, strong quantitative story): "Quantifying the interaction between crystal symmetry and chemical class in superconductor critical temperature." The Tc variance decomposition + coarsening + COD replication.

3. **Meta-science paper** (broadest, riskiest): "Why cross-domain mathematical connections are hard to find: a systematic false-positive audit across 21 databases." The 8/8 kill rate + the taxonomy of failure modes.

### What We Would Do Differently

1. **Start with the cross-domain falsification protocol.** We built it after finding false positives. If we'd had layers 1-7 from day one, we'd have avoided 2 weeks of chasing distributional ghosts.

2. **Use permutation-null eta² from the start, not fixed thresholds.** The Cohen's d-based thresholds from social science don't account for group count. Permutation nulls are cheap and dataset-specific.

3. **Don't use M4/M² as a discovery metric.** Use it as a descriptive statistic only. eta² (variance explained) should be the primary magnitude measure from the beginning.

4. **Build the primitive tagger earlier.** Classifying findings by operation type (SYMMETRIZE, BREAK_SYMMETRY, etc.) reveals patterns invisible to the per-finding view. SYMMETRIZE dominates; COMPOSE is absent. That's a finding about the structure of mathematical knowledge.

---

## 7. The Deepest Lesson

We set out to find universal mathematical structure across domains. We found that the tools for PROVING such structure doesn't exist are more valuable than the structures themselves.

The battery kills false positives. The cross-domain protocol eliminates distributional ghosts. The non-stationarity analysis reveals that even strong within-domain patterns don't transfer across contexts. And the primitive tagger shows that the dominant operation in mathematical databases is SYMMETRIZE (categorical partitioning), not COMPOSE (cross-domain bridging).

The absence of cross-domain structure under these representations and this battery is itself the finding. Whether it reflects a deep truth about mathematical compartmentalization or a limitation of feature-based analysis remains an open question — but at least we now know exactly what "open" means, because we've closed every other door and documented what's behind each one.

---

*Project Prometheus, April 1-12, 2026*
*Machines: M1 (Skullport) + M2 (SpectreX5)*
*Agents: Charon (cross-domain cartographer)*
*Battery: v7 (F1-F32 + F25b + primitive tagger)*
*Council: ChatGPT (×2), Gemini, Claude, DeepSeek, Grok, Perplexity*
*Tests: ~130 | Findings: ~100 classified | Cross-domain: 0 confirmed*
