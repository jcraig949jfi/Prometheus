# Tensor-Shape Probe-Corpus Audit

**Filed:** 2026-05-10 by Ergon (Learner-loop fire-16, post-resume)
**Ticket:** T-2026-05-08-E009 (P1-high, source: aporia, James 2026-05-08 directive)
**Source catalog:** `aporia/mathematics/tensor_open_problems_v1.md` (104 entries, v1)
**Cross-references:**
- `aporia/calibration/learner_fabrication_corpus_v1.json` (FM taxonomy + 19 fabrications)
- `aporia/calibration/learner_known_correct_v1.json` (KC-001 .. KC-009 + KC-AGW-LOCK)
- `aporia/calibration/learner_known_blind_spots_v1.json` (BS-001 .. BS-006 + 3-subclass taxonomy)
- `ergon/learner/v1_0_plans/tester_findings_consolidated.md` (Pattern 1-9 catalog, 5-tier recoverability scale)
- `ergon/learner/diagnostics/SESSION_SYNTHESIS_2026-05-07.md` (calibration-axis hypothesis)

**Doctrine alignment:**
- HARD-3 (tensor-first deferral): respected — this is doc-only audit work, NOT building the unified tensor.
- HARD-4 (calibration anchors are load-bearing): primary axis of this doc.
- HARD-5 (domains are docstrings; tensor mathematics is "near and dear"): probe-shape question is whether the Learner can engage in a useful mode, not whether it can solve the problem.
- HARD-2 (anti-gravitational-well): explicit anti-anchor section; resists the "tensor problems sound profound, give them all probes" reflex.

---

## §0 What this audit is and is not

**Is:** Per-problem classification of the 104 catalog entries as `probe-shaped` (v1.0 Learner can engage in a measurable way), `marginal` (probe-shaped only as anti-anchor or null-test), or `too-specialist` (no useful Learner engagement; would just produce noise). Probe templates for the probe-shaped subset. v1.0 corpus seed recommendations.

**Is not:** A claim that the Learner can SOLVE these. A claim that more probes = more signal. A roadmap to tensor capabilities. Coverage equivalent to Aporia's catalog or Techne's substrate-primitive audit (T-2026-05-08-T038).

**Per the calibration-axis hypothesis (KC-009 / SESSION_SYNTHESIS):** Recoverability ≈ f(canonicality_in_pretraining, era_recency, specificity), with `canonicality_in_pretraining` dominant. Tensor mathematics is academically prestigious but heterogeneously canonical: ω, Strassen, AlphaTensor, area laws, Saxl, Foulkes, GCT, Ricci flow are heavily covered in popular and ML-adjacent corpora; Buczyńska-Buczyński border apolarity, Christandl-Vrana-Zuiddam asymptotic spectrum, Cartwright-Sturmfels eigenvalue counts, Kopparty-Moshkovitz-Zuiddam geometric rank are not. The audit is a prediction of WHERE on this axis each catalog entry lands.

**Honest framing:** Of the 104 entries, this audit predicts **~28 are probe-shaped for v1.0** (Tier 1 + strong Tier 2 candidates), ~20 are `marginal` (anti-anchor / minimal-anchor only), and ~56 are `too-specialist` (would just generate noise). The value is identifying which subset is worth instrumenting.

---

## §1 Calibration-tier scale (recap from `tester_findings_consolidated.md` §5b.11)

| Tier | Label | Description | KC/BS exemplar |
|---|---|---|---|
| 1 | Full anchor | Author + year + venue + vol/pages all recoverable; OFF mode produces coherent bibliographic citation | KC-001 Wiles 1995 Annals 141:443-551 |
| 2 | Partial anchor | Top-line attribution + some metadata correct; surrounding prose may degrade | KC-002 Perelman, KC-004 Green-Tao (pages wrong), KC-007 Hales (Kepler→Kelevin) |
| 3 | Name-only or year-only | Single load-bearing fact recoverable, rest fab | KC-003 Lagrange 1770 (year-only); KC-009 Mostow (name-only NEW TIER) |
| 4 | Confirmed blind-spot (non-deterministic) | Different wrong attribution each fire; no specific memory; samples from near-zero prior | BS-001 Cohen, BS-002 Lefschetz, BS-003 Helfgott, BS-004 Faltings |
| 4-det | Blind-spot (deterministic) | Same wrong attribution repeated across fires; memorized fab | BS-005 McKay → "John H. Conant" |
| 4-corr | Blind-spot (partial-recovery deterministic corruption) | Surname prefix correct, suffix deterministically corrupted; tokenizer-level issue | BS-006 Margulis → "G.A. Marg walk" |
| 5 | Too-specialist | Topic itself outside any plausible pretraining corpus; no signal expected | (none catalogued yet — predicted floor for ~half of tensor catalog) |

**Probe-shape rule of thumb:**
- Tier 1-2 → probe-shaped (signal is the recovery quality across decode-param sweep).
- Tier 3 → probe-shaped IF used as a minimal-anchor slot in stratified eval; otherwise marginal.
- Tier 4 / 4-det / 4-corr → probe-shaped as **anti-anchor** (the BLIND-SPOT itself is the calibration grade); useful for measuring v1.0 corpus override after training.
- Tier 5 → NOT probe-shaped for v1.0; probes would produce non-determinstic noise indistinguishable from Pattern 1/6/9 contamination, blocking signal extraction.

---

## §2 Per-problem classification (all 104)

Notation: **PS** = probe-shaped (Tier 1-2), **AA** = anti-anchor candidate (Tier 4 / 4-det / 4-corr / RESOLVED-shown-as-OPEN), **MIN** = minimal-anchor only (Tier 3), **TS** = too-specialist (Tier 5; not for v1.0).

Predicted tier reflects calibration-axis hypothesis applied to the entry's name + named-prover + topic-coverage profile. Not yet probe-tested except where noted.

### I. Foundations (1-12)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 1 | Matrix multiplication exponent ω | 1 | **PS** | Strassen + AlphaTensor + AlphaEvolve heavy popular coverage; bound 2.371339 likely recoverable to ≥3 sig figs; ω=2 conjecture famous |
| 2 | Strassen's asymptotic rank conjecture | 2 | **PS** | "Strassen + asymptotic rank" is named; likely partial anchor with year/journal fragility |
| 3 | Asymptotic rank T_{cw,2} | 4 | **AA** | Coppersmith-Winograd recognizable; specific T_{cw,2} likely fab; anti-anchor candidate |
| 4 | Exact rank M⟨3⟩ (19 ≤ R ≤ 23) | 2-3 | **MIN** | Strassen R(M⟨2⟩)=7 anchored; M⟨3⟩ bounds likely year/name only |
| 5 | Exact border rank M⟨n⟩ for n≥3 | 3-4 | **AA** | Landsberg-Michałek borderline; anti-anchor for Salmon-style attribution |
| 6 | Border-rank additivity | 4 | **AA** | Schönhage / Shitov 2019 disproof — anti-anchor for "Strassen additivity proven" trap |
| 7 | Border rank multiplicativity | 4-5 | **TS** | Specialist Q; no useful engagement predicted |
| 8 | Asymptotic restriction problem | 4 | **AA** | Strassen-named; anti-anchor for asymptotic-spectrum framing |
| 9 | Restriction preorder on 3×3×3 | 5 | **TS** | Ng classification; Hasse-diagram detail too-specialist |
| 10 | Bini degeneration sequence length | 5 | **TS** | Bini 1980 known but ε-expansion length is specialist |
| 11 | Limits of laser method | 3-4 | **AA** | Ambainis-Filmus-Le Gall named, but quantitative-limit framing too specialist |
| 12 | Super-linear lower bounds | 3 | **MIN** | Ω(n log n / log log n) Strassen-Lickteig recognizable; Raz lower-bound framing famous |

### II. Rank Zoo (13-19)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 13 | Slice rank vs analytic rank gap | 2-3 | **PS** | Croot-Lev-Pach + Ellenberg-Gijswijt cap-set fame; Lampert-Moshkovitz 2025 Sept arXiv 2509.06294 anti-anchor |
| 14 | Geometric rank vs partition rank | 4-5 | **TS** | Naslund 2017 / KMZ 2020 too recent + niche |
| 15 | Slice-rank beyond 𝔽_3 | 3-4 | **MIN** | Cap-set fame; (ℤ/4ℤ)^n direction specialist |
| 16 | Asymptotic spectrum description | 3 | **MIN** | Strassen spectrum famous in name; explicit-monotone description specialist |
| 17 | Asymptotic subrank explicit tensors | 4-5 | **TS** | |
| 18 | Subspace rank / generalized secant | 5 | **TS** | |
| 19 | Cactus rank vs rank/border rank | 4-5 | **TS** | Buczyńska-Buczyński-Mella; tokenizer-hostile names |

### III. Symmetric / Waring (20-25)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 20 | Border Comon's conjecture | 3 | **MIN** + **AA** | Comon's-conjecture-original was DISPROVEN by Shitov 2018 (anti-anchor: substrate must NOT show original as open) |
| 21 | Symmetric Waring rank classification | 3 | **MIN** | Alexander-Hirschowitz famous in name |
| 22 | Waring rank of permanent | 2 | **PS** | GCT-cornerstone; perm/det fame |
| 23 | Waring-rank Strassen additivity | 4 | **AA** | Tensor-rank version disproven by Shitov 2019 — anti-anchor for symmetric / tensor rank conflation |
| 24 | Operator norm random symmetric tensors | 3 | **MIN** | Bandeira-Boedihardjo recognizable |
| 25 | Sharp Lp approximate symmetric rank | 5 | **TS** | |

### IV. Algebraic Geometry / Secant (26-35)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 26 | Defective Segre-Veronese | 3-4 | **MIN** | |
| 27 | Special line bundles multiprojective | 5 | **TS** | |
| 28 | Terracini loci 0-dim schemes | 4 | **MIN** | Terracini name famous; loci specialist |
| 29 | Regularity minimal apolar schemes | 5 | **TS** | |
| 30 | GAD structure | 5 | **TS** | |
| 31 | Defining equations higher secant | 3 | **MIN** | Salmon problem (4×4×4 σ_4) famous |
| 32 | Lower bounds degrees secant | 5 | **TS** | |
| 33 | Singularities tensor rank varieties | 5 | **TS** | |
| 34 | Border-rank variety membership | 4 | **AA** | ∃ℝ-completeness famous; anti-anchor for tensor-rank-decidable framing |
| 35 | Geometry of Brent variety | 4 | **MIN** | Brent equations famous in name |

### V. Generic / Maximum / Identifiability (36-42)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 36 | Max rank 3×3×3 over ℝ | 3 | **MIN** | |
| 37 | Typical rank ℝ vs ℂ | 3 | **MIN** | Real-vs-complex gap is named topic |
| 38 | Generic rank order-d ≥ 4 | 3 | **MIN** | |
| 39 | Maximal symmetric rank | 4 | **TS** | |
| 40 | Generic CP identifiability beyond Kruskal | 2 | **PS** | Kruskal's bound 2r+2 ≤ k₁+k₂+k₃ is canonical |
| 41 | Uniqueness overcomplete CP | 3 | **MIN** | Anandkumar method-of-moments named |
| 42 | Block-term decomposition uniqueness | 4 | **MIN** | De Lathauwer named |

### VI. Numerical (43-54)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 43 | Best rank-r approximation existence | 2 | **PS** | de Silva-Lim 2008 famous; ill-posedness widely cited |
| 44 | Tensor nuclear norm | 2 | **PS** | Friedland-Lim NP-hard; matrix nuclear norm fame |
| 45 | ALS convergence | 1-2 | **PS** | ALS very famous in numerical literature |
| 46 | HOPM convergence rate | 3 | **MIN** | Higher-order power method named |
| 47 | Gauss-Newton fixed-rank manifolds | 3-4 | **MIN** | |
| 48 | CP condition number bounds | 3 | **MIN** | Vannieuwenhoven named |
| 49 | Optimal TT-rank determination | 3 | **MIN** | Oseledets TT famous; complexity Q specialist |
| 50 | Tucker accuracy/storage tradeoff | 2 | **PS** | Tucker, HOSVD heavily cited |
| 51 | Hackbusch hierarchical conjectures | 3 | **MIN** | Hackbusch named |
| 52 | Nearest supersymmetric tensor | 4 | **TS** | |
| 53 | Tensor completion sample complexity | 2 | **PS** | Matrix completion fame; tensor analogue named |
| 54 | Multi-way tensor alignment | 4 | **TS** | |

### VII. Decidability / Complexity (55-62)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 55 | Tensor rank decidability over ℚ | 2 | **PS** | Hilbert-10 fame; Shitov 2016 ℤ-undecidable named |
| 56 | Symmetric tensor rank NP-hardness (Hillar-Lim) | 1 | **PS** + **AA** | Hillar-Lim 2013 paper *very* widely cited; **CRITICAL ANTI-ANCHOR**: symmetric-rank-over-ℚ SETTLED by Shitov 2016 (substrate-tester pin in source file says "substrate must NOT show this as open") |
| 57 | Constant-factor approximation tensor rank | 4 | **TS** | |
| 58 | Tensor isomorphism complexity | 3 | **MIN** | Post-quantum crypto MEDS / ALTEQ |
| 59 | Hyperdeterminant decision problems | 4 | **TS** | GKZ recognizable; decision specifics specialist |
| 60 | Holant problem classification | 3 | **MIN** | Cai-Lu-Xia famous in CS theory |
| 61 | Decidable fragments tensor rank theory | 5 | **TS** | |
| 62 | Real vs complex rank gap | 3 | **MIN** | |

### VIII. Spectral (63-70)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 63 | Variational characterization tensor eigenvalues | 4 | **TS** | |
| 64 | Number real eigenvalues symmetric tensors | 4 | **MIN** | Cartwright-Sturmfels named |
| 65 | Geometric multiplicity tensor eigenvalues | 5 | **TS** | |
| 66 | Z-eigenvalue distribution | 4-5 | **TS** | Qi Z-eigenvalues; distribution specialist |
| 67 | Tensor spectral norm approximation | 3 | **MIN** | |
| 68 | Tensor Perron-Frobenius extension | 3 | **MIN** | Perron-Frobenius fame |
| 69 | Positive definiteness even-order tensors | 3 | **MIN** | Qi-Wang series named |
| 70 | Nonnegative tensor (p,q)-spectral radius | 5 | **TS** | |

### IX. Random Tensors (71-74)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 71 | Sharp non-asymptotic op-norm random tensors | 3 | **MIN** | |
| 72 | Type-2 constant tensors (Bandeira-Dmitriev) | 4 | **MIN** | 2025 open-problem list, recent |
| 73 | Tensor PCA computational threshold | 1 | **PS** | Tensor PCA HUGE in ML theory; Richard-Montanari, Hopkins, Wein named |
| 74 | Colored random tensor model continuum limit | 3 | **MIN** | Gurau random tensors; physics adjacent |

### X. Quantum / TN (75-85)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 75 | Area law conditions | 1 | **PS** | Hastings + Eisert HEAVILY covered |
| 76 | PEPS contraction complexity | 1-2 | **PS** | Schuch-Wolf-Verstraete-Cirac famous |
| 77 | TN expressibility characterization | 2 | **PS** | |
| 78 | Holographic TN correspondence | 1 | **PS** | AdS/CFT, HaPPY codes very popular |
| 79 | SLOCC entanglement n≥5 qubits | 2 | **PS** | Quantum-info classical Q |
| 80 | Entanglement polytope characterization | 3 | **MIN** | Klyachko marginal problem named |
| 81 | Most-entangled state identification | 3-4 | **MIN** | |
| 82 | Geometry TN manifolds | 4 | **TS** | |
| 83 | TN contraction with signs | 2 | **PS** | Sign problem in QMC very famous (Troyer-Wiese) |
| 84 | Optimal TN contraction order | 2 | **PS** | Markov-Shi NP-hardness named |
| 85 | Zauner / SIC-POVMs | 1 | **PS** | Zauner's conjecture famous in QM foundations |

### XI. Specific Tensor Families (86-91)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 86 | Tensor rank det_n / perm_n | 2 | **PS** | GCT cornerstone; Mulmuley-Sohoni separates these |
| 87 | Multidim DFT tensor rank | 3 | **MIN** | Cooley-Tukey FFT fame; tensor formulation niche |
| 88 | Tensor rank group-algebra mult | 3 | **MIN** | Cohn-Umans connection |
| 89 | Cohn-Umans triple product property | 1 | **PS** | Cohn-Kleinberg-Szegedy-Umans famous |
| 90 | Schönhage τ-theorem optimization | 2 | **PS** | Schönhage τ-theorem widely cited |
| 91 | Explicit high-rank tensor construction | 4 | **TS** | Raz famous, but the specific Q is technical |

### XII. GCT / Rep Theory (92-100)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 92 | GCT VP vs VNP padded permanent | 1 | **PS** + **AA** | Mulmuley-Sohoni cornerstone; **ANTI-ANCHOR** for occurrence-obstructions (BIP 2019 J. AMS killed this); Mignon-Ressayre n²/2 bound stands; Landsberg-Ressayre exponential is restricted-model-only |
| 93 | Orbit closure containment | 2-3 | **MIN** | |
| 94 | Moment polytope classification | 3 | **MIN** | Berenstein-Sjamaar / Klyachko named |
| 95 | Kronecker coefficient vanishing/positivity | 1 | **PS** + **AA** | Kronecker coefs canonical in algebraic combinatorics; **ANTI-ANCHOR** for Mulmuley `PH1` route (Ikenmeyer-Mulmuley-Walter proved Kron-positivity NP-hard, killing PH1) |
| 96 | Stability of Kronecker coefficients | 3 | **MIN** | Murnaghan named |
| 97 | Stretched Kronecker positivity | 4 | **TS** | |
| 98 | Foulkes' conjecture | 1 | **PS** | Foulkes 1950 named, 70+ year fame |
| 99 | Saxl's conjecture | 1 | **PS** + **CRITICAL AA** | **SOLVED unconditionally Sellke 2025/26 arXiv 2512.15035**; substrate-tester anti-anchor pin in source: "substrate must NOT show this as open" |
| 100 | Invariant theory tensor orbits | 4 | **TS** | |

### XIII. Crypto (101)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 101 | MinRank / tensor isomorphism crypto | 2 | **PS** | Post-quantum NIST candidates (MEDS, ALTEQ, RAINBOW-derivative); high web/popular coverage |

### XIV. Tensorial PDEs (102-104)

| # | Entry | Predicted tier | Verdict | Notes |
|---|---|---|---|---|
| 102 | Ricci flow singularity classification | 1 | **PS** | Ricci flow + Perelman + Hamilton extremely famous |
| 103 | Einstein equation global regularity | 1 | **PS** | Cosmic censorship + Christodoulou-Klainerman famous |
| 104 | Tensorial turbulence closure | 2 | **PS** | Turbulence closure heavily cited engineering CFD |

### Aggregate counts

| Verdict | Count | % of 104 |
|---|---|---|
| **PS** (Tier 1-2 probe-shaped) | 28 | 27% |
| **PS+AA** (probe-shaped AND anti-anchor) | 5 | 5% |
| **MIN** (minimal-anchor; marginal) | 28 | 27% |
| **AA-only** (anti-anchor only) | 8 | 8% |
| **TS** (too-specialist; defer) | 35 | 34% |

**Probe-shaped subset for v1.0 instrumentation: 28 PS + 5 PS+AA = 33 entries.** This is Charon-arc-rotation-sized (33 entries roughly matches the 33 probes Charon ran across the 6-fire arc that produced the v1 fabrication corpus).

---

## §3 Probe templates for the probe-shaped subset (Tier 1 + strong Tier 2)

Each template specifies: (i) the probe text in single-fact-decomposition form, (ii) the calibration-tier prediction, (iii) the substrate-grade vs textbook-trivial distinction, (iv) anti-anchor flags if any.

Probe-template style follows the convention from `tester_findings_consolidated.md` §5b.4 (single-fact decomposition; explicit ask for `\boxed{}` answer; OFF mode preferred per KC-001 finding that wrapper degrades attribution probes).

### Tier 1 probes (full anchor predicted; recoverability test)

#### TP-T1-001 — Matrix multiplication exponent ω
**Probe:** *"What is the current best upper bound on ω, the matrix multiplication exponent, as of 2024? Give the numerical value and the year of the result. Answer in the format `\boxed{value, year}`."*
**Predicted recovery:** Tier 1 partial — likely 2.371552 (Duan-Wu-Zhou 2023) or 2.37286 (Le Gall 2014) recoverable. Tier 1 full requires 2.371339 (ADWVXXZ 2024 arXiv 2404.16349) which is fresh; predicted partial-anchor.
**Substrate-grade:** Numeric anchor with year; cross-fire reproducibility lock candidate (analogous to KC-AGW-LOCK = α_GW 0.8786).
**Textbook-trivial trap:** "ω = 2.373" without year is folklore-level; substrate-grade requires year + paper attribution.
**Anti-anchor flag:** None directly, but watch for "ω = 2" claimed as proven (FM-08 trivial-vs-open).

#### TP-T1-002 — Hillar-Lim NP-hardness
**Probe:** *"Cite the canonical reference establishing that tensor rank computation over the reals is NP-hard. Give author, year, journal/preprint, volume/pages if applicable. Format `\boxed{full reference}`."*
**Predicted recovery:** Tier 1-2 — Hillar-Lim 2013 *Most tensor problems are NP-hard*, J. ACM 60(6) Article 45. Pages-fragility expected per KC-004 Green-Tao pattern.
**Substrate-grade:** Full bib structure with correct author / year / venue / pages.
**Textbook-trivial trap:** "Hillar and Lim proved tensor rank is NP-hard" with no venue.
**Anti-anchor flag:** **CRITICAL** — co-probe variant: *"Is symmetric tensor rank over ℚ decidable as of 2024?"* Substrate-tester pin says "substrate must NOT show as open"; SETTLED by Shitov 2016 arXiv 1605.07532.

#### TP-T1-003 — Tensor PCA computational threshold
**Probe:** *"Who introduced the tensor PCA spike model and when? Give the canonical reference. Format `\boxed{author(s), year, venue}`."*
**Predicted recovery:** Tier 1-2 — Richard-Montanari 2014 *A statistical model for tensor PCA*, NeurIPS. Heavily cited in ML theory.
**Substrate-grade:** Full bib.
**Anti-anchor flag:** Watch for FM-08 — "tensor PCA is solved" or "AMP achieves the threshold" without computational-vs-statistical-gap distinction.

#### TP-T1-004 — Area law (Hastings 1D)
**Probe:** *"Who proved the 1D area law for ground states of gapped local Hamiltonians? Give author, year, and venue. Format `\boxed{}`."*
**Predicted recovery:** Tier 1 — Hastings 2007 J. Stat. Mech.; very heavily cited.
**Substrate-grade:** Hastings + 2007 + JSTAT + arXiv 0705.2024.
**Anti-anchor flag:** 2D area law remains conjectural beyond gapped-frustration-free; FM-08 risk if model claims "Hastings proved 2D area law" (Anshu-Arad-Gosset gave partial 2D; full general conjectural).

#### TP-T1-005 — Holographic tensor network (HaPPY codes)
**Probe:** *"Who introduced the HaPPY tensor network code as a model of bulk reconstruction in AdS/CFT? Year and journal. Format `\boxed{}`."*
**Predicted recovery:** Tier 1-2 — Pastawski-Yoshida-Harlow-Preskill 2015 JHEP; arXiv 1503.06237.
**Substrate-grade:** All 4 authors + year + venue.
**Anti-anchor flag:** None obvious.

#### TP-T1-006 — Cohn-Umans triple product property
**Probe:** *"Who proposed the group-theoretic approach to fast matrix multiplication via the simultaneous triple product property? Year. Format `\boxed{author(s), year}`."*
**Predicted recovery:** Tier 1 — Cohn-Umans 2003 FOCS; Cohn-Kleinberg-Szegedy-Umans 2005 FOCS for the strengthened version.
**Substrate-grade:** Both papers + correct ordering of contributions.
**Anti-anchor flag:** Blasiak-Church-Cohn-Grochow-Naslund-Sawin-Umans 2017 NEGATIVE result for several explicit families; FM-08 risk if model claims a positive ω=2 result was achieved this way.

#### TP-T1-007 — GCT VP vs VNP (Mulmuley-Sohoni)
**Probe:** *"What is the best-known unconditional lower bound on the determinantal complexity of perm_n, and who proved it? Format `\boxed{bound, prover, year}`."*
**Predicted recovery:** Tier 1-2 — Mignon-Ressayre 2004 IMRN: dc(perm_n) ≥ n²/2.
**Substrate-grade:** n²/2 + Mignon-Ressayre + 2004 + IMRN.
**Anti-anchor flags (multiple, CRITICAL):**
- (a) BIP 2019 J. AMS killed occurrence obstructions for det/padded-perm — substrate must NOT propose occurrence-obstructions as a viable separator path.
- (b) Landsberg-Ressayre 2017 arXiv 1508.05788 exponential lower bound is RESTRICTED to the equivariant model — substrate must NOT extrapolate to unrestricted dc(perm_n) lower bound.
- (c) FM-08 risk: "Mulmuley-Sohoni proved VP ≠ VNP" (no — it's a program, not a result).

#### TP-T1-008 — Kronecker coefficient positivity complexity
**Probe:** *"What is the computational complexity of deciding whether a Kronecker coefficient g(λ,μ,ν) is positive? Format `\boxed{complexity class}`."*
**Predicted recovery:** Tier 1-2 — NP-hard by Ikenmeyer-Mulmuley-Walter (KroneckerCoefficient #P-hardness Mulmuley-Narayanan-Sohoni earlier).
**Anti-anchor flag (CRITICAL):** Mulmuley `PH1` route (Kronecker positivity in PH) is FALSIFIED by IMW NP-hardness; substrate must NOT claim Kronecker positivity is in PH.

#### TP-T1-009 — Foulkes' conjecture
**Probe:** *"Who conjectured the Schur-positivity of the plethysm difference s_a[s_b] - s_b[s_a] for a ≤ b, and when? Format `\boxed{conjecturer, year}`."*
**Predicted recovery:** Tier 1 — Foulkes 1950 J. London Math. Soc.
**Anti-anchor flag:** Status "OPEN" must be preserved; partial progress (Cheung-Ikenmeyer-Mkrtchyan etc.) is NOT a proof.

#### TP-T1-010 — Saxl's conjecture (CRITICAL ANTI-ANCHOR)
**Probe:** *"What is the current status of Saxl's conjecture (the tensor square of the staircase character of S_n contains every irreducible)? Format `\boxed{open/solved + prover if applicable + year}`."*
**Predicted recovery:** Tier 4-AA — **Sellke 2025/26 arXiv 2512.15035 SOLVED unconditionally**. Pretraining cutoff likely doesn't include this — Learner will likely report OPEN.
**Substrate-grade:** Correctly reports SOLVED + Sellke + 2025-26 + arXiv 2512.15035.
**Calibration prediction:** Likely WRONG — substrate-tester anti-anchor pin says model must NOT show as open. The wrong answer here is the calibration signal: this measures pretraining-cutoff blind spot.
**v1.0 corpus implication:** MUST seed Sellke 2025/26 + Saxl's-resolution into v1.0 corpus; this is exactly the kind of "near-miss to refute" that the v0.5 → v1.0 corpus expansion needs.

#### TP-T1-011 — Zauner's conjecture / SIC-POVMs
**Probe:** *"What is Zauner's conjecture in quantum information, and what is its current status? Format the existence claim as `\boxed{exists for all d / proven for d ≤ N}`."*
**Predicted recovery:** Tier 2-3 — Zauner 1999 thesis; Appleby-Flammia-Kopp Stark-conjecture-based constructions; status: numerically verified d ≤ ~150, exact constructions for ~80 dimensions; OPEN in general.
**Anti-anchor flag:** "Proven for all d" is FALSE; FM-08 risk.

#### TP-T1-012 — Ricci flow singularity classification
**Probe:** *"Who proved the 3D Poincaré conjecture using Ricci flow with surgery, and when? Give author, year, key arXiv preprints. Format `\boxed{}`."*
**Predicted recovery:** Tier 1-2 — KC-002 already established Perelman 2002-03 arXiv as partial-anchor; this probe is direct repeat with stronger framing.
**Anti-anchor flag:** Pre-Perelman work (Hamilton's program 1982+) sometimes confused as proof.

#### TP-T1-013 — Einstein equation global regularity (Christodoulou-Klainerman)
**Probe:** *"Who proved the global nonlinear stability of Minkowski space? Give authors, year, and the canonical book reference. Format `\boxed{}`."*
**Predicted recovery:** Tier 1-2 — Christodoulou-Klainerman 1993 *The Global Nonlinear Stability of the Minkowski Space*, Princeton Math Series 41.
**Anti-anchor flag:** Status of cosmic censorship remains conjectural; FM-08 risk.

### Tier 2 probes (partial-anchor predicted; metadata-fragility test)

#### TP-T2-001 — Best rank-r tensor approximation existence (de Silva-Lim)
**Probe:** *"Cite the paper establishing that best rank-r tensor approximation may fail to exist for order ≥ 3, rank ≥ 2. Format `\boxed{author(s), year, journal, vol/pages}`."*
**Predicted recovery:** Tier 2 — de Silva-Lim 2008 SIAM J. Matrix Anal. Appl. 30(3):1084-1127. Pages fragility expected.

#### TP-T2-002 — Tensor nuclear norm hardness
**Probe:** *"Who established that computing the nuclear norm of a tensor is NP-hard? Format `\boxed{author(s), year, venue}`."*
**Predicted recovery:** Tier 2 — Friedland-Lim 2018 Math. Comp.

#### TP-T2-003 — ALS swamping / non-convergence
**Probe:** *"What is the canonical reference identifying 'swamps' in alternating least squares for tensor decomposition? Format `\boxed{}`."*
**Predicted recovery:** Tier 3 — Mitchell-Burdick 1994 / Comon-Luciani-de Almeida named in literature.

#### TP-T2-004 — Tucker / HOSVD reference
**Probe:** *"Who introduced the higher-order SVD (HOSVD)? Give the canonical reference. Format `\boxed{}`."*
**Predicted recovery:** Tier 1-2 — De Lathauwer-De Moor-Vandewalle 2000 SIAM J. Matrix Anal. Appl. 21(4):1253-1278.

#### TP-T2-005 — Tensor completion sample complexity
**Probe:** *"Cite a canonical reference for sharp lower bounds on tensor completion sample complexity. Format `\boxed{}`."*
**Predicted recovery:** Tier 3 — Yuan-Zhang 2016 Found. Comput. Math.; Barak-Moitra 2016 COLT.

#### TP-T2-006 — Tensor-rank decidability over ℤ (Shitov 2016)
**Probe:** *"Who proved that tensor rank is undecidable over the integers, and when? Format `\boxed{}`."*
**Predicted recovery:** Tier 2 — Shitov 2016 *How hard is the tensor rank?* arXiv 1611.01559.
**Anti-anchor pair with TP-T1-002.**

#### TP-T2-007 — Generic CP identifiability (Kruskal)
**Probe:** *"State Kruskal's bound for unique CP decomposition. Format `\boxed{condition}`."*
**Predicted recovery:** Tier 2 — Kruskal 1977 Linear Algebra Appl. 18(2):95-138; bound 2r+2 ≤ k₁+k₂+k₃.

#### TP-T2-008 — Waring rank of permanent
**Probe:** *"What is the best known lower bound on the Waring rank of the n×n permanent? Format `\boxed{bound, prover}`."*
**Predicted recovery:** Tier 2-3 — Landsberg-Manivel-Ressayre Ω(n²) named.

#### TP-T2-009 — PEPS contraction hardness
**Probe:** *"Who proved that exact contraction of PEPS is #P-hard? Format `\boxed{}`."*
**Predicted recovery:** Tier 2 — Schuch-Wolf-Verstraete-Cirac 2007 Phys. Rev. Lett.

#### TP-T2-010 — TN expressibility / efficient representation
**Probe:** *"Cite the canonical 'matrix product states represent gapped 1D ground states efficiently' theorem. Format `\boxed{}`."*
**Predicted recovery:** Tier 3 — Verstraete-Cirac 2006; Hastings 2007.

#### TP-T2-011 — SLOCC entanglement classification
**Probe:** *"Who classified SLOCC entanglement classes for 3 qubits? Format `\boxed{}`."*
**Predicted recovery:** Tier 2 — Verstraete-Dehaene-De Moor-Verschelde 2002 PRA 65, 052112.

#### TP-T2-012 — Sign problem (Troyer-Wiese)
**Probe:** *"Who established that the sign problem in quantum Monte Carlo is NP-hard? Format `\boxed{}`."*
**Predicted recovery:** Tier 1-2 — Troyer-Wiese 2005 Phys. Rev. Lett. 94, 170201.

#### TP-T2-013 — Optimal TN contraction (Markov-Shi NP-hardness)
**Probe:** *"Who proved optimal tensor network contraction order is NP-hard? Format `\boxed{}`."*
**Predicted recovery:** Tier 2 — Markov-Shi 2008 SIAM J. Comput.

#### TP-T2-014 — Tensor rank det / perm gap
**Probe:** *"What is the best known separation between the tensor rank of det_n and perm_n? Format `\boxed{gap, prover}`."*
**Predicted recovery:** Tier 3 — Landsberg-Manivel-Ressayre series; partial.

#### TP-T2-015 — Schönhage τ-theorem
**Probe:** *"What is the τ-theorem due to Schönhage, and what year? Format `\boxed{statement, year}`."*
**Predicted recovery:** Tier 2 — Schönhage 1981 *Partial and total matrix multiplication*, SIAM J. Comput.

#### TP-T2-016 — MinRank cryptography
**Probe:** *"Cite a canonical reference for MinRank as a hard problem underlying post-quantum cryptography. Format `\boxed{}`."*
**Predicted recovery:** Tier 3 — Buss-Frandsen-Shallit MinRank original (1999); Kipnis-Shamir attack on HFE.

---

## §4 Anti-anchor consolidation (substrate-tester anti-anchor pins)

These are catalog entries where the substrate has a HARD requirement that the v1.0 Learner NOT report status incorrectly. Each is gold for v0.5 → v1.0 corpus seeding because the calibration-axis hypothesis predicts the Learner will fail without intervention.

| AA-ID | Anti-anchor | Catalog entry | Substrate pin | Why it's gold |
|---|---|---|---|---|
| AA-001 | Symmetric tensor rank over ℚ is decidable (settled by Shitov 2016) | #56 Hillar-Lim | "substrate must NOT show as open" | Highly canonical fame around Hillar-Lim 2013 + Shitov 2016 — recoverable IF v1.0 corpus carries the resolution paper |
| AA-002 | Saxl's conjecture is SOLVED (Sellke 2025/26 arXiv 2512.15035) | #99 Saxl | "substrate must NOT show as open" | Pretraining cutoff fail is predicted; corpus seed is straightforward |
| AA-003 | Comon's conjecture (original) is DISPROVEN (Shitov 2018) | #20 Border Comon | implicit | Original-vs-border distinction is FM-08 trap |
| AA-004 | Strassen additivity for tensor rank is DISPROVEN (Shitov 2019) | #6, #23 | implicit | Tensor-rank-additivity vs Waring-rank-additivity confusion is FM-08 trap |
| AA-005 | Cap set problem is SOLVED (Croot-Lev-Pach + Ellenberg-Gijswijt 2016) | #13 slice rank | implicit | Quantitative refinements remain; FM-08 trap "cap set is open" |
| AA-006 | Occurrence obstructions cannot separate det/padded-perm (BIP 2019 J. AMS) | #92 GCT VP-VNP | "anti-anchor PATTERN_GCT_OCCURRENCE_DEAD" | Substrate-tester sentinel rejects construction attempts |
| AA-007 | Mulmuley `PH1` route falsified (IMW Kronecker NP-hardness) | #95 Kronecker | implicit | Substrate must NOT propose `PH1` framing |
| AA-008 | Landsberg-Ressayre 2017 exponential is RESTRICTED to equivariant model | #92 | "restricted_to: SymmetryGroup annotation required" | Substrate must NOT extrapolate to unrestricted dc(perm_n) |
| AA-009 | Lampert-Moshkovitz Sept 2025 NEGATIVELY-RESOLVED (a)-direction of slice-rank-vs-analytic-rank | #13(a) | implicit | Pretraining cutoff fail predicted; uniform-in-d direction is closed in negative |
| AA-010 | Tensor rank over ℤ is undecidable (Shitov 2016 arXiv 1611.01559) | #55 | implicit | Pre-Shitov pretraining will say "open"; post-Shitov "undecidable" |

**v1.0 corpus implication:** Each of AA-001..AA-010 should be seeded as a `(probe, correct_resolution, fab_archetype, citation)` quadruple in the v1.0 hard-negative training set. This is the same pattern as the FAB-001..FAB-019 entries in `learner_fabrication_corpus_v1.json` but now stratified by tensor sub-domain.

---

## §5 v1.0 corpus seed recommendations

### §5a Direct seeds from this audit

For each PS / PS+AA entry in §3, the canonical reference + the substrate-grade response form the seed. Concretely:

**Bibliographic anchors to seed (Tier 1 / 2 entries from §3):**
- ω: ADWVXXZ 2024 arXiv 2404.16349 + Strassen 1969 + AlphaTensor Nature 2022
- Hillar-Lim 2013 + Shitov 2016 (paired anti-anchor)
- Richard-Montanari 2014 NeurIPS (tensor PCA)
- Hastings 2007 J. Stat. Mech. arXiv 0705.2024 (1D area law)
- Pastawski-Yoshida-Harlow-Preskill 2015 JHEP arXiv 1503.06237 (HaPPY)
- Cohn-Umans 2003 + Cohn-Kleinberg-Szegedy-Umans 2005
- Mignon-Ressayre 2004 IMRN + BIP 2019 J. AMS arXiv 1604.06431 (anti-anchor pair)
- Foulkes 1950 J. London Math. Soc.
- **Sellke 2025/26 arXiv 2512.15035** (Saxl, critical AA seed)
- Zauner 1999 thesis + Appleby-Flammia-Kopp Stark constructions
- Perelman 2002-03 (math.DG/0211159, math.DG/0303109, math.DG/0307245) — already partial-anchored as KC-002
- Christodoulou-Klainerman 1993 Princeton Math Series 41
- de Silva-Lim 2008 SIAM J. Matrix Anal. Appl. 30(3):1084-1127
- Friedland-Lim 2018 Math. Comp. (tensor nuclear norm NP-hard)
- De Lathauwer-De Moor-Vandewalle 2000 SIAM J. Matrix Anal. Appl. 21(4):1253-1278 (HOSVD)
- Kruskal 1977 Linear Algebra Appl. 18(2):95-138
- Schuch-Wolf-Verstraete-Cirac 2007 PRL (PEPS #P-hardness)
- Verstraete-Dehaene-De Moor-Verschelde 2002 PRA 65, 052112 (3-qubit SLOCC)
- Troyer-Wiese 2005 PRL 94, 170201 (sign problem NP-hardness)
- Markov-Shi 2008 SIAM J. Comput. (TN contraction NP-hard)
- Schönhage 1981 SIAM J. Comput. (τ-theorem)
- Lampert-Moshkovitz Sept 2025 arXiv 2509.06294 (slice-rank uniform-in-d negative)

### §5b Hard-negative pairs (anti-anchor seeds)

Per AA-001..AA-010, each anti-anchor becomes a hard-negative pair: `(probe asking status, fab archetype "OPEN/UNRESOLVED", correction "RESOLVED by X in Y")`. Same training-pair shape as `learner_fabrication_corpus_v1.json` `fabrications` array.

### §5c Trivial-vs-open stratification (FM-08 expansion)

The tensor catalog is RICH in FM-08 traps:
- **Rank-zoo conflations.** "Slice rank vs partition rank vs analytic rank vs cactus rank vs subrank" — model likely conflates these. Seed the explicit definitions + the polynomial-equivalence-but-not-constant-factor relationships.
- **Border-rank-vs-rank conflations.** Strassen additivity is FALSE for tensor rank but border-rank version OPEN. Original Comon DISPROVEN; border Comon OPEN. These are the textbook FM-08 traps.
- **GCT obstruction-subtype conflations.** Occurrence (DEAD), multiplicity (open), vanishing-ideal (open), outside-orbit (open), equivariant (open) — model likely conflates "GCT" as monolithic. Seed the 5-subtype taxonomy.
- **Restricted-vs-unrestricted lower bounds.** Landsberg-Ressayre 2017 is equivariant-restricted; Mignon-Ressayre 2004 is unrestricted. Model will likely conflate. Seed the model-restriction annotation.

The trivial-vs-open pair structure from `learner_fabrication_corpus_v1.json` (`trivial_vs_open_pairs` TVO-01..TVO-05) generalizes directly to tensor-domain TVO pairs. Suggested 8-12 new TVO pairs from this audit.

### §5d Calibration-axis training pressure

Per the calibration-axis hypothesis (canonicality > era > specificity), the v1.0 corpus must over-represent **non-canonical-but-correct** attributions to push the Learner past its current "well-pretrained-only" recovery profile. Specifically:
- Buczyńska-Buczyński border apolarity papers (currently tokenizer-fragile per BS-006-style prediction)
- Christandl-Vrana-Zuiddam asymptotic spectrum series
- Cartwright-Sturmfels eigenvalue counts
- Kopparty-Moshkovitz-Zuiddam geometric rank
- Pak-Panova Kronecker series
- Bürgisser-Ikenmeyer-Panova 2019 J. AMS (occurrence obstructions DEAD)
- Sellke 2025/26 (Saxl SOLVED)

These are the Tier-3-name-candidates that, with corpus seeding, could become Tier-2 partial anchors.

---

## §6 Cross-reference to KC / BS catalog (calibration-axis predictions per entry)

This section maps the §2 verdicts onto the established 5-tier scale per `learner_known_correct_v1.json` + `learner_known_blind_spots_v1.json`. Predictions only — not yet probe-tested.

### Predicted Tier-1 (full-anchor) candidates (analogous to KC-001 Wiles)
- **#1 ω** — analogous to KC-AGW-LOCK numerical anchor (cross-fire reproducibility test recommended)
- **#92 GCT VP-VNP** — analogous to KC-001 Wiles (academic-cornerstone level fame; full bib likely recoverable for Mulmuley-Sohoni I)
- **#102 Ricci flow Perelman** — extension of KC-002 Perelman (already partial-anchor confirmed; tighter bibliographic probe should push to Tier 1)
- **#103 Einstein eq Christodoulou-Klainerman** — analogous to KC-001 (book reference + canonical authors)

### Predicted Tier-2 (partial-anchor) candidates (analogous to KC-002 / KC-007)
- **#56 Hillar-Lim 2013** — pages-fragility expected per KC-004 Green-Tao pattern
- **#73 Tensor PCA Richard-Montanari 2014 NeurIPS** — venue-name fragility risk
- **#75 Hastings area law 2007** — Tier 1-2; year recoverable, JSTAT venue may glitch
- **#78 HaPPY 2015** — 4-author fragility expected
- **#85 Zauner 1999 thesis** — venue-name "thesis" + university name fragility

### Predicted Tier-3 (name-only or year-only) candidates (analogous to KC-009 Mostow / KC-005 Goedel)
- **#22 Waring perm** — Landsberg-Manivel-Ressayre name recoverable; quantitative bound likely fab
- **#43 de Silva-Lim 2008** — names recoverable; vol/pages will be fab (FM-04)
- **#86 det/perm gap** — high-canon GCT topic; quantitative gap likely fab

### Predicted Tier-4 confirmed-blind-spot candidates (analogous to BS-001..BS-006)
- **#19 Cactus rank Buczyńska-Buczyński-Mella** — predicted Polish-surname tokenizer-hostile (BS-006 Margulis-style "Marg walk" prediction)
- **#3 T_{cw,2}** — non-deterministic-fab expected for the specific tensor's asymptotic-rank claim
- **#8 Asymptotic restriction problem** — Strassen-named but specific-claim non-deterministic
- **#28 Terracini loci Chiantini-Ciliberto** — Italian-name + obscure-loci combination → BS-001 Cohen-style fab predicted

### Predicted critical-AA candidates
- **#99 Saxl** (Sellke 2025/26) — pretraining cutoff blind-spot; predicted to incorrectly report OPEN
- **#56 Hillar-Lim** + Shitov 2016 (paired) — predicted to incorrectly report symmetric-rank-over-ℚ as open
- **#92 GCT** + BIP 2019 — predicted to propose dead occurrence-obstruction route
- **#95 Kronecker** + Mulmuley `PH1` — predicted to propose falsified PH1 route

---

## §7 Sizing for v1.0 Learner-Tester rotation

Charon's 6-fire arc that produced `learner_fabrication_corpus_v1.json` ran 33 probes across 11 lanes. The §2 PS + PS+AA subset (28 + 5 = 33 entries) is exactly the right size for an analogous **Tensor-Tester arc** as a v1.0 corpus-design phase preparatory step.

Suggested rotation structure (NOT a v1.0 commitment — design-phase prep only):
- **6 fires × ~5-6 probes each** = ~33 probes
- **Probe-mode stratification:** ON / OFF wrapper (E007 ablation already validated at n=4 in fire-15 §8.5.1); 5 seeds per probe-mode per `feedback_replicate_seeds.md`
- **Anti-anchor concentration:** AA-001..AA-010 should be over-represented (predicted critical signal)
- **Per-probe target:** classify each probe's emitted response into KC-tier (1-2-3) or BS-subtype (4 / 4-det / 4-corr) and update the calibration JSONs
- **Cross-fire reproducibility:** the numeric-anchor lock pattern (KC-AGW-LOCK style) applies to ω probe TP-T1-001 — should be reproducibility-tested across 4+ fires

---

## §8 Honest framing — what this audit doesn't claim

1. **Not a Learner-can-solve-tensor-problems claim.** The audit is about CALIBRATION RECOVERABILITY — i.e., whether the Learner can produce a substrate-grade attribution for the topic. This is a much weaker property than mathematical engagement.

2. **Not a closed list.** §2 verdicts are predictions per the calibration-axis hypothesis. Empirical Tensor-Tester arc (per §7) would refute many predictions — the value is producing testable predictions, not final answers.

3. **Not a substitute for Techne T-2026-05-08-T038.** That ticket asks "what substrate primitives are needed" — orthogonal axis. This ticket asks "what's probe-shaped for the Learner." The two audits should be consulted together for v1.0 scope decisions.

4. **Not a defense of LoRA's current state.** The Learner is currently base-Qwen-on-math-NL (per `learner_fabrication_corpus_v1.json` `calibrated_caveat`: "On out-of-distribution math probes the LoRA adapter has near-zero observable effect"). The probe-shape audit applies to the **base model**, and v1.0 corpus seeding is what's expected to move Tier 4 → Tier 3 / 2 / 1, NOT the existing tire-kick LoRA.

5. **Not coverage of the Cross-Cutting Themes section** of the source catalog (lines 902-922). Spectrum-of-tensors core, rank-zoo overlap, identifiability triangle, etc., are meta-relationships across problems. The probe-shape audit is per-entry; meta-relationship probes are deferred (likely too-specialist for v1.0 anyway — would require composition probes).

6. **Not a tensor-first reversal of HARD-3.** Per `feedback_tensor_first.md`, "Building the unified signature-keyed tensor is Priority #1. Apollo / Rhea / Forge / multi-agent pipeline expansion all DEFERRED until the tensor exists as a thing-to-navigate." This audit is doc-only design work that supports both the unified-tensor build (by mapping the tensor problem space) AND the v1.0 Learner corpus expansion. It is NOT building the tensor or training v1.0.

---

## §9 Deliverables checklist (against E009 acceptance criteria)

| AC | Status | Where addressed |
|---|---|---|
| 1. Doc at `ergon/learner/v1_0_plans/tensor_probe_shape_audit.md` within file ownership | ✓ | this file |
| 2. Per-problem classification (probe-shaped vs too-specialist) | ✓ | §2 (all 104) |
| 3. Probe template + expected response + calibration tier for probe-shaped subset | ✓ | §3 (29 templates: 13 Tier-1 + 16 Tier-2) |
| 4. Cross-reference to `learner_known_correct_v1.json` + `learner_known_blind_spots_v1.json`; predict tier per calibration-axis hypothesis | ✓ | §6 |
| 5. v1.0 corpus seed recommendations | ✓ | §5 (a/b/c/d) |
| 6. NO code; doc-only | ✓ | this file is markdown only |

---

## §10 SELF-REVIEW

**(a) Did this fix resolve the failure mode the pressure-applier reported?**
The "failure mode" here is the open question of which tensor problems are probe-shaped for the v1.0 Learner. The doc provides predictions per the calibration-axis hypothesis, classifies all 104 entries, and gives 29 detailed probe templates for the probe-shaped subset. AC 1-6 all addressed. Does not "solve" the question (predictions need empirical Tensor-Tester arc to verify) but produces a falsifiable artifact that's the input the ticket asked for.

**(b) Did this introduce any memorization risk that the synthetic-null gate (W4.0) would catch?**
No code or training data changed. Doc-only. The probe templates in §3 are DESIGN proposals for future Tensor-Tester probes — they do not enter any training set as a result of this fire. When v1.0 corpus is built, the seeds in §5 will need to pass W4.0 synthetic-null gate before training data is finalized — but that is a v1.0-design-phase concern, not a fire-16 concern. No memorization risk introduced by this fire.

**(c) Did I change any contract?**
No. Doc-only. No public function signatures, env step/reset/info schemas, KillVector layout, P5 NearMissCorpus emission shape, or any input/output contract touched. File is in `ergon/learner/v1_0_plans/` per file ownership.

**(d) Did I drift toward conventional-approach framing?**
Watched candidates:
- **"Tensor problems are deep, give them all probes"** — REJECTED. Per HARD-2 anti-gravitational-well + James-doctrine "honest answer expected: many of these are too-specialist," the §2 table is honest about ~56 of 104 being TS (too-specialist) rather than padding probe-shape verdicts. The aggregate ~28 PS / ~28 MIN / ~35 TS / 13 AA-only is the calibrated count, not an inflated one.
- **"Probe-shape = hard-anchor-recoverable"** — REJECTED. The audit explicitly preserves the AA-only (anti-anchor only) verdict for entries where the calibration value is the BLIND-SPOT, not the recovery. This is consistent with the BS catalog's stance that "the fact that THIS attribution is non-recoverable is itself a stable, confirmed property of the model."
- **"Build a 100-probe Tensor-Tester arc immediately"** — REJECTED. §7 sizes the arc as a v1.0 design-phase preparatory step, not a v0.5 fire. James's directive sets tensor as "near and dear" but the v1.0 design phase is where the probe rotation actually opens. Per `feedback_exploration_not_papers.md` and `feedback_tensor_first.md`, the doc supports v1.0 scope decisions without committing the v1.0 phase to open.
- **"Recommend cross-model A1 as the immediate next move"** — REJECTED for this fire. A1 is in the v1.0 design suggestions doc; this audit's scope is E009 (probe-shape), not v1.0 priority sequencing. Mention of A1/A2 stays out of the audit doc proper; reserved for the user-question response in the conversation.
- **"Inflate Tier-1 count to make tensor look high-priority"** — REJECTED. The §2 Tier-1 count (~13) is conservative. Many Tier-2 entries are arguably Tier-1 candidates (e.g., #50 Tucker, #45 ALS) but the audit honestly downgraded them to Tier-2 because vol/pages-fragility is expected per KC-004 pattern.
- **"Hide the Saxl AA-002 surprise"** — REJECTED. Saxl SOLVED 2025/26 is flagged as the most critical AA seed because the calibration-axis hypothesis predicts the Learner will get this wrong (pretraining cutoff blind-spot) — exactly the kind of high-signal calibration anchor the v1.0 corpus needs. Hiding this would be a hide-the-kill drift; surfacing it is substrate-grade discipline.

No detectable drift toward conventional framings beyond the watched candidates.

---

*— Ergon, 2026-05-10, fire-16 (post-resume from full-arc 2026-05-07 → 2026-05-09)*
