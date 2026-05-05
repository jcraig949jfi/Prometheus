# P2 — Yang-Mills Mass Gap (4D)

**Author:** Harmonia C (instantiated 2026-05-05)
**Time spent:** ~70 min (within 3 hr budget)
**Verdict:** OPEN — no progress made; obstruction localized; calibration anchor produced
**Tags:** `constructive-QFT`, `renormalizability-marginal`, `lattice-gauge`,
`continuum-limit-missing`, `obstruction-located`, `2D-Abelian-control-trace-clean`

---

## 1. Statement (operational form)

Construct a 4D quantum Yang-Mills theory (gauge group $G$ a compact non-Abelian Lie
group, e.g. $SU(2)$ or $SU(3)$) satisfying the Wightman/Osterwalder-Schrader axioms,
and prove that the spectrum of the Hamiltonian on the physical Hilbert space has a
gap above the vacuum: $\inf \{\lambda > 0 : \lambda \in \sigma(H)\} > 0$.

The Clay statement (Jaffe-Witten) makes this precise. The two parts — *existence*
and *mass gap* — are both open and entangled: existence in 4D is not known
independently of any spectral statement.

## 2. What is known (anchor literature, no inventions)

- **Yang-Mills 1954 (Phys. Rev.).** Original proposal of non-Abelian gauge theory.
  Pure-gauge action $S = \frac{1}{4 g^2} \int F^a_{\mu\nu} F^{a\,\mu\nu}$.
- **Wilson 1974 (Phys. Rev. D).** Lattice formulation of gauge theory. Plaquette action
  $S_W = \beta \sum_{p} (1 - \frac{1}{N} \mathrm{Re}\,\mathrm{tr}\, U_p)$ with $\beta = 2N/g^2$.
  Wilson loops show area law in the strong-coupling expansion → confinement.
- **Glimm-Jaffe constructive program** (multiple papers, monograph "Quantum Physics:
  A Functional Integral Point of View", 1987 ed.). Constructive QFT for super-renormalizable
  theories ($\phi^4_2, \phi^4_3$, Yukawa, etc.).
- **Magnen-Rivasseau, Balaban** (1980s). Constructive treatment of $\phi^4_3$,
  partial results toward 4D gauge theory; Balaban's program builds the lattice
  continuum limit step by step.
- **Numerical lattice QCD** (Wilson, Creutz, then a vast literature). Glueball masses
  in pure $SU(3)$ in 4D measured at multiple lattice spacings, extrapolated to
  continuum: lightest scalar glueball $\sim 1.7$ GeV, tensor $\sim 2.4$ GeV, with
  uncertainty bands ~5–10%. *Numerically* the mass gap is overwhelming.

I have hazy memory on whether **3D pure non-Abelian YM** has a fully rigorous
existence-with-gap result; my prior is that 3D is super-renormalizable so existence
is on firmer ground than 4D, but I did not retrieve a definitive citation.

I am **NOT** inventing specific theorem statements I can't attribute.

## 3. Locating the obstruction

The gap between "we can simulate it" and "we have constructed it" reduces to:

1. **UV continuum limit.** Lattice cutoff $a$ → 0 limit must exist with all expected
   properties. In 4D, $g(a)$ runs logarithmically (asymptotic freedom). Block-spin
   RG arguments (Balaban) give partial control but not a complete construction
   matching all OS axioms.
2. **Reflection positivity.** Wilson lattice action is reflection-positive on its
   own, but proving the property survives the continuum limit and relates to a
   physical Hilbert space is non-trivial. Especially under gauge fixing.
3. **Gribov ambiguity.** Coulomb / Landau / axial gauge fixing in non-Abelian
   theories is not unique globally on the configuration space. Different
   resolutions (Gribov-Zwanziger, BRST quantization, stochastic quantization) all
   have technical issues that have not been bundled into a complete proof.
4. **Mass gap separately.** Even granting existence, a quantitative gap requires
   a transfer-matrix bound or a cluster expansion that survives all scales.
   Strong-coupling lattice expansion produces a gap easily (it's the trivial regime);
   weak-coupling matched to that strong-coupling region without losing the gap is
   the open piece.

In my reading the **structurally hardest** of the four is (1)+(3) combined: every
construction route either gives up gauge invariance and adds Gribov-handling
machinery or keeps gauge invariance and confronts a non-locally-defined integration
measure.

**Why 2D abelian is rigorous and 4D non-abelian isn't:** in 2D, the lattice gauge
plaquettes are *independent* (because the underlying Haar measure on $U(1)$ links
factorizes through the 2D combinatorics), so the partition function is a product
of single-plaquette integrals. Continuum limit is tractable analytically. In 4D
non-abelian, plaquettes are *strongly coupled* (each link enters six plaquettes),
the partition function is genuinely multi-dimensional, and the renormalization
flow is marginal, not relevant.

## 4. Computational experiment (2D U(1) lattice as calibration anchor)

I cannot run a 4D non-abelian lattice gauge simulation in this harness's time
budget. Even small-lattice $SU(2)$ in 4D needs ~10⁵ Metropolis sweeps on $L^4$
with $L \geq 8$ to get clean glueball signals. Instead, I run **2D U(1) Wilson
gauge theory** on a $16 \times 16$ lattice and verify the simulation matches
**exact analytic predictions** in a regime where rigorous QFT exists. This
calibrates the toolchain.

- Lattice: $16 \times 16$, periodic boundary conditions.
- Gauge group: $U(1)$ (link variables $\theta_\mu(x) \in [0, 2\pi)$).
- Action: Wilson plaquette, $\beta = 2.0$.
- Algorithm: standard Metropolis, single-link random-walk proposals on $[-1, 1]$.
- Thermalization: 2000 sweeps. Measurement: 4000 sweeps, sampled every 5.
- Total effective samples: 800.

**Analytic predictions** (Migdal recursion / character-expansion exact for 2D):
- $\langle \cos\theta_p \rangle_{\rm exact} = I_1(\beta)/I_0(\beta) = 0.69777$.
- $\langle W(R, T) \rangle_{\rm exact} = (I_1/I_0)^{R \cdot T}$.
- string tension $\sigma_{\rm exact} = -\log(I_1/I_0) = 0.35986$.

**Run output (script `_p2_ym_experiment.py`):**

| observable | simulation | exact | absolute Δ | relative Δ |
|---|---|---|---|---|
| plaquette $\langle \cos\theta_p \rangle$ | $0.69991 \pm 0.00087$ | $0.69777$ | $+0.00214$ | $+0.31\%$ |
| Wilson loop $W(1,1)$ | $0.70275 \pm 0.00349$ | $0.69777$ | $+0.00498$ | $+0.71\%$ |
| Wilson loop $W(2,2)$ | $0.24015 \pm 0.00589$ | $0.23706$ | $+0.00309$ | $+1.30\%$ |
| Wilson loop $W(1,3)$ | $0.34898 \pm 0.00580$ | $0.33974$ | $+0.00924$ | $+2.72\%$ |
| string tension (via $W(2,2)$) | $0.35663$ | $0.35986$ | $-0.00323$ | $-0.90\%$ |

All match to within 1–3 sigma of statistical error. **The toolchain is calibrated.**

**What this calibration buys:** confidence that a Metropolis sweep, a Wilson-loop
estimator, and an area-law extraction are all working as expected. It does NOT
buy any progress on the 4D non-abelian gap — that requires a different machinery
(continuum-limit construction with rigorous error bounds), not just better statistics.

## 5. Where I would push if I had more time

1. **Run lattice $SU(2)$ in 2D, 3D, 4D at matched $\beta$**, observe how
   confinement signals (Wilson area law, glueball spectrum from Polyakov loop
   correlators) scale with dimension. The expected scaling is the textbook
   answer; what I would actually look for is *deviation from textbook* on small
   lattices that might surface a structural feature. (Almost certainly null.)
2. **Examine the Balaban block-spin RG output** as a coordinate system. Plot the
   effective action coefficients across scales. If the coefficient flow has a
   structural feature (a fixed-point pinch, a degeneracy locus) it would be a
   candidate symbol for the methodology toolkit. This is "novelty-budget" work.
3. **Map the Gribov region geometrically** in low-volume lattice. Visualize the
   ambiguity. Probably also textbook but I haven't seen it visualized cleanly.

I did not start (1)–(3).

## 6. Per-attack metadata

| field | value |
|---|---|
| problem_id | `MILLENNIUM_YM_4D_MASS_GAP` |
| attack_class | survey + 2D abelian control-trace + obstruction localization |
| anchor_invoked | `Wilson-1974-lattice`, `Glimm-Jaffe-constructive-program` |
| failure_mode | `marginal-renormalizability + Gribov + reflection-positivity-of-continuum-limit` |
| computational_scope | 2D U(1), $L=16$, $\beta=2.0$, ~6000 sweeps total |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | Yang-Mills 1954, Wilson 1974, Glimm-Jaffe (book) |
| hazy_citations | 3D pure non-abelian existence-with-gap status (not invoked) |
| 4D-experiment-attempted | NO (compute budget) |
| reward_signal_capture_check | passed — calibration matched exact answer before any structural claim |
| pattern_30_relevance | low |
| cross-problem-cluster | shares "marginal-scaling" obstruction theme with NS (P1) |

## 7. Honest read

The 2D U(1) Metropolis run reproduces $I_1(\beta)/I_0(\beta)$ to within a percent at
$\beta = 2.0$ in a few seconds. That's a clean toolchain check. No structural
discovery. The 4D non-abelian gap obstruction is well-localized in the
constructive-QFT literature; I do not know of any leverage point a single-session
attack could meaningfully push against. If the substrate's bet is on
*coordinate-invention*, the "Balaban RG flow as coordinate system" idea is the most
promising follow-up but is multi-month work.

— Harmonia C, 2026-05-05
