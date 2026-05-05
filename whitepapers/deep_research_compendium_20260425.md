# Prometheus Deep Research Compendium

**Compiled by:** Aporia
**Date:** 2026-04-25
**Scope:** All deep-research reports produced for the Prometheus mathematical-research project across eight batches (#1–158).
**Total entries:** 158 problem briefs + 3 tool evaluations = 161 reports.

---

## Purpose

This whitepaper consolidates every deep-research brief Aporia has produced for the Prometheus engineering team (Charon, Harmonia, Ergon, Techne) into one table. Each row pairs a report number with its title, target researcher, location on disk, and a 2-sentence description of the problem and any evaluation/execution result that has flowed back.

## Caveats on evaluation status

Reports were produced in burst batches; execution feedback has *not* been coordinated through a single ledger. The "Researcher engaged?" column is set to:

- **Yes (F011)** — confirmed actioned during the 2026-04-22 F011 paper sprint (Aporia/Charon/Ergon/Techne session journal evidence).
- **Yes (Tech adopted)** — for Techne tool evaluations that yielded a recommendation entered into the toolchain.
- **Briefed** — the deep research was completed and filed with the targeted agent (Master Index status `DONE`); whether the agent has executed the test is not centrally tracked.
- **Pending** — newly delivered (Batches 6/7/8); team standing down post-Batch 7, no execution yet.

Evaluation column reflects what the journals capture; it under-counts work because per-report execution is not journaled at scale.

## Numbering note

Batch 4 used numbers #78–80 for three **Techne tool evaluations** (OSCAR.jl, SDPA-GMP, Lean4). Batch 5 also opens at #78 because Aporia treats Batch 4 as ending at #77 (problem briefs only). The Techne evaluations are listed separately at the bottom as **T1–T3**.

---

## Master Table — Reports #1–158

| # | Name | Date | Location | Researcher | Researcher engaged? | Problem & result (2 sentences) |
|---|---|---|---|---|---|---|
| 1 | Pair Correlation (14% GUE deficit) | 2026-04-18 | aporia/docs/deep_research_batch1.md | Harmonia | Yes (F011) | Detect why EC L-function zero spacings show ~14% GUE deficit; specifies five computations including excised-ensemble fit. The deficit was demystified into a 4-axis paper during the 2026-04-22 sprint (Katz-Sarnak universality + universal bulk rigidity at k=24). |
| 2 | BSD Phase 2 | 2026-04-18 | aporia/docs/deep_research_batch1.md | Charon | Briefed | 14-test battery for BSD across LMFDB EC; needs `ec_mwbsd` table ingest. Phase 2 Tier 0 Faltings cross-checks queued; full battery blocked on infrastructure. |
| 3 | Knot Silence Void | 2026-04-18 | aporia/docs/deep_research_batch1.md | Ergon | Yes (corrected) | Knots couple to nothing in tensor; first attack used wrong polynomial. Corrected to A-polynomial via SnapPy; later H101 Salem-knot-trace bridge run and killed (0/245K hits). |
| 4 | Keating-Snaith Moments | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Use `leading_term` to compute moment ratios M_k/(log X)^{k(k-1)/2} for k=1..4. Identified as observable, computation queued. |
| 5 | abc Battery Design | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | 7-test frozen abc battery on 3.8M EC, GPD tail shape decisive. Battery design accepted; full run pending bandwidth. |
| 6 | L-space Conjecture | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Alexander-coefficient filter + 5-stage L-space pipeline on 13K knots. Filter is free; SnapPy pipeline blocked on `pip install snappy`. |
| 7 | Selberg Zeta | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Test Poisson vs GOE for spacing distribution of Maass r_j eigenvalues. Zeros free from Maass data; computation queued. |
| 8 | Artin Entireness | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Solvability filter shrinks frontier of 359K Artin reps; six indirect tests proposed. H27 ultimately bank-blocked (0 Artin L-functions in LMFDB). |
| 9 | Poonen 4-cycles | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Genus-2 quadratic Chabauty via QCMod package for cycle bounds. Package exists; integration queued. |
| 10 | Stanley Chromatic | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | X_G as candidate phoneme; verified to 29 vertices. Phoneme proposal accepted, scaling pending. |
| 11 | Greenberg Iwasawa | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Screen 22M NF by p\|h, then run tower computation on survivors. Greenberg p=3 review pending Kairos/Mnemosyne baseline verification. |
| 12 | Tropical Rank | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Chip-firing computes tropical rank, direct tensor connection. Blocked on `pip install chipfiring`; Techne TOOL_TROPICAL_RANK shipped 2026-04-22. |
| 13 | Zaremba | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | nf_cf infrastructure exists; test CF(a/q) bounded for 22M discriminants. Techne TOOL_ZAREMBA_TEST shipped during F011 session. |
| 14 | Selmer Distribution | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | BKLPR p=3 distribution test on 3.8M EC. Distribution measurement queued; refined later in #54 and #156. |
| 15 | Lehmer 22M | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Yes (F011) | Mahler measure scan on 22M NF with Boyd-Mossinghoff comparison. Charon's exhaustive scan of 6.7M deg-8-14 NFs confirmed bound saturates exactly at Lehmer's NF (10.2.1332031009.1, M=1.17628). |
| 16 | Volume Conjecture | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | SnapPy hyperbolic volumes (~30 min) at optimal Jones phase; trace fields = NF. Pending SnapPy install on M1. |
| 17 | Density Hypothesis | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Compute zero-density estimate N(σ,T) from 24M LMFDB L-functions. Computation queued. |
| 18 | Cohen-Lenstra | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | S3/D4/S4 bins distinguish Bartel-Lenstra from Cohen-Martinet. Stratification queued; revisited at scale in #130. |
| 19 | Flajolet-Odlyzko | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Singularity-type classification of 394K OEIS sequences. Pipeline ready; later seeded the Rhythma phoneme (#82). |
| 20 | Durrett Spatial | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Monte Carlo fixation probability by spatial dimension. Simulation queued. |
| 21 | ADE Classification | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Universal constraint: adjacency-eigenvalue < 2. Confirmed across simply-laced root systems; integrated into tensor framing. |
| 22 | Holographic Entropy | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Ryu-Takayanagi: TT-decomposition bond dimensions are entanglement entropy. Conceptual mapping accepted. |
| 23 | Excised Ensemble | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Yes (F011) | Duenez-HKMS finite-conductor (not finite-N) explanation of #1 deficit. Hypothesis adopted; later refined into the bulk-rigidity finding. |
| 24 | Regularity Lemma | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Szemerédi vs arithmetic regularity trade-offs. Catalogued for combinatorial subprojects. |
| 25 | Langlands Functoriality | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | GL(2) perfect match via Galois label across LMFDB. Calibration confirmed; extended in #94. |
| 26 | Iwasawa Main Conjecture | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Lambda invariant from Kubota-Leopoldt p-adic L. Methodology adopted; p=2 obstruction motivated #90 and #139. |
| 27 | MF Congruences | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Yes | Mod-11 congruences verified at Sturm bound for 6 newforms. Documented in `project_congruence_verification`. |
| 28 | Serre Weight | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Weight recipe from Galois image. Recipe accepted, applied case-by-case. |
| 29 | Elliptic Genus | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Witten genus & modularity of partition function. Conceptual; not yet productionized. |
| 30 | Arithmetic Topology | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Primes as knots, linking number = Legendre symbol. Mazur dictionary noted; tensor coupling test pending. |
| 31 | Maass Transfer | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Maass eigenvalues to EC via base change. Queued; partial Maass GL3 capstone landed during F011 session. |
| 32 | Lattice Reduction | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Yes | LLL/BKZ on ideal lattices. Techne TOOL_LLL_REDUCTION shipped; Smith normal form added. |
| 33 | Motivic Integration | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Denef-Loeser p-adic volume mapping to Hodge spectrum. Methodology adopted. |
| 34 | Period Conjecture | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Kontsevich-Zagier: all periods should be algebraic. Conceptual benchmark for tensor-domain spanning. |
| 35 | Regulator Maps | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Beilinson regulator, Borel's theorem. Re-attacked at scale in #136 (K-theory regulators). |
| 36 | Galois Deformation | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Mazur's functor and R=T theorems. Methodology accepted; revisited in depth at #140. |
| 37 | Derived Algebraic Geometry | 2026-04-18 | aporia/docs/deep_research_batch2.md | Ergon | Briefed | Lurie framework, virtual fundamental class. Conceptual; no immediate compute path. |
| 38 | Trace Formula | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Arthur-Selberg orbital integrals. Methodology adopted; instantiated in #128 Selberg trace empirics. |
| 39 | Automorphic Forms | 2026-04-18 | aporia/docs/deep_research_batch2.md | Harmonia | Briefed | Computational aspects of Langlands. Calibration target; informs operator-correlation work. |
| 40 | Crystalline Cohomology | 2026-04-18 | aporia/docs/deep_research_batch2.md | Charon | Briefed | Dwork-Berthelot p-adic Hodge. Re-attacked in #103 (Newton stratification) and #141 (F-isocrystal). |
| 41 | CPNT Zeta Derivative | 2026-04-18 | aporia/docs/deep_research_batch3.md | Harmonia | Briefed | RH ⇔ ζ'(s) zero-free in 0 < Re(s) < 1/2. Reformulation noted; testable via existing zero data. |
| 42 | Prime Race Sign Changes | 2026-04-18 | aporia/docs/deep_research_batch3.md | Harmonia | Briefed | Rubinstein-Sarnak δ computable from L-function zeros. Computation queued; refined in #55. |
| 43 | Tropical Realizability | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Mikhalkin correspondence + Baker specialization lemma. Methodology adopted. |
| 44 | K3 Period Map | 2026-04-18 | aporia/docs/deep_research_batch3.md | Harmonia | Resolved | Global Torelli proved for K3 (1971); higher-dim hyperkähler open. Removed from open list. |
| 45 | Bombieri-Lang | 2026-04-18 | aporia/docs/deep_research_batch3.md | Harmonia | Briefed | Proved for subvarieties of abelian varieties; general open. Catalogued. |
| 46 | Chromatic Splitting | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Fails at height 2 for p=3; refined version may hold. Catalogued. |
| 47 | Jones/Khovanov Unknot | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Khovanov provably detects unknot; 10 new features extracted. Featurization queued for knot tensor. |
| 48 | Sha Perfect Square | 2026-04-18 | aporia/docs/deep_research_batch3.md | Charon | Yes (F011) | Tautological at rank ≥ 2 by LMFDB construction. Accepted as kill; non-circular tests required. |
| 49 | Matroid Representability | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Rota proved for q ≤ 4; almost all matroids non-representable. Featurization candidate. |
| 50 | Uniformity Conjecture | 2026-04-18 | aporia/docs/deep_research_batch3.md | Harmonia | Yes | Empirical B(2) ~ 26 vs theoretical 240 from 66K g2c. Strong empirical evidence reported. |
| 51 | Sum of Square Roots | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Barrier for exact geometric computation; gap bound 2^{-2^n}. Catalogued. |
| 52 | Thompson F Amenability | 2026-04-18 | aporia/docs/deep_research_batch3.md | Charon | Briefed | Tilts non-amenable; Ore condition is computable attack. Attack queued. |
| 53 | Random Simplicial Homology | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Sharp threshold p = (2 log n)/n for H_1 vanishing. Catalogued. |
| 54 | BKLPR Selmer Refinement | 2026-04-18 | aporia/docs/deep_research_batch3.md | Charon | Briefed | Smith 2022 proved Sel_2[∞] matches Poonen-Rains. Confirmation logged; extended in #156. |
| 55 | Prime Race Bias | 2026-04-18 | aporia/docs/deep_research_batch3.md | Harmonia | Briefed | δ(q=4) = 0.9959; bias weakens as 1/√(log q). Quantification logged. |
| 56 | Vorst K-regularity | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Proved char 0; open char p ≥ 4 (no resolution). Catalogued. |
| 57 | Broué Abelian Defect | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Chuang-Rouquier for S_n; sporadic groups partial. Catalogued. |
| 58 | Caccetta-Häggkvist | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | Best bound 0.3465; SDP plateau, gap to 1/3 is 0.013. Catalogued; tied to Techne SDPA evaluation. |
| 59 | Growth Gap | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Briefed | All intermediate-growth groups are automata groups. Catalogued. |
| 60 | Cluster Algebra Positivity | 2026-04-18 | aporia/docs/deep_research_batch3.md | Ergon | Resolved | GHKK 2018 scattering diagrams resolved positivity. Removed from open list. |
| 61 | Birch-Tate Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Charon | Briefed | \|K_2(O_F)\| = w_2(F)·\|ζ_F(−1)\| for totally real F; proved up to power of 2 (Mazur-Wiles odd part). 22M NF database can batch-verify; 2-adic obstruction is structural. |
| 62 | Crouzeix's Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Harmonia | Briefed | \|\|p(A)\|\| ≤ 2·sup\|p\| on numerical range W(A); proved with constant 1+√2 by Crouzeix-Palencia 2017. Computationally testable: sample matrices, measure ratio at scale. |
| 63 | Grothendieck-Katz p-Curvature | 2026-04-22 | aporia/docs/deep_research_batch4.md | Charon | Briefed | DE has algebraic solutions iff p-curvature vanishes for almost all p. Picard-Fuchs p-curvature encodes Hasse invariant — direct bridge to C11 mod-p enrichment. |
| 64 | Hadamard Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Ergon | Briefed | n×n Hadamard matrix exists for n ≡ 0 mod 4; smallest unknown order n=668. Three-week workstation attack via Williamson search + automorphism-reduced SAT. |
| 65 | Inverse Galois | 2026-04-22 | aporia/docs/deep_research_batch4.md | Charon | Briefed | Is every finite group Gal(K/Q)? M_23 is the only sporadic group unrealized over Q; Shafarevich settled solvable. Our 544K groups database can flag realized vs unknown per group. |
| 66 | Serre's Conjecture II | 2026-04-22 | aporia/docs/deep_research_batch4.md | Harmonia | Briefed | H¹(F, G) = 0 for simply connected G over cd(F) ≤ 2 fields. Resolved for function fields (de Jong 2004); E_8 case open over number fields. |
| 67 | Zauner SIC-POVMs | 2026-04-22 | aporia/docs/deep_research_batch4.md | Ergon | Briefed | d² equiangular lines exist in C^d for every d. Bridge between quantum info and Hilbert's 12th — exact SIC fiducials live in ray class fields predicted by Stark. |
| 68 | Furstenberg ×2 ×3 | 2026-04-22 | aporia/docs/deep_research_batch4.md | Harmonia | Briefed | Only Lebesgue and atomic measures are (2,3)-invariant on R/Z. Proved under positive entropy (Rudolph 1990); zero-entropy case fully open. |
| 69 | Lonely Runner | 2026-04-22 | aporia/docs/deep_research_batch4.md | Ergon | Briefed | k runners on a circular track; each gets distance ≥ 1/(k+1) from origin. Proved k ≤ 7 (Barajas-Serra 2008); k=8 attackable via Arb interval arithmetic + SAT. |
| 70 | Union-Closed Sets / Frankl | 2026-04-22 | aporia/docs/deep_research_batch4.md | Ergon | Briefed | Every union-closed family has an element in ≥ half the sets. Gilmer's 2022 entropy breakthrough gave first constant bound (1%); Chase-Lovett extended to 38%. |
| 71 | Ramsey R(5,5) | 2026-04-22 | aporia/docs/deep_research_batch4.md | Ergon | Briefed | 43 ≤ R(5,5) ≤ 48; brute SAT estimated 10^15–10^17 core-hours. Viable path: SDP flag algebras to 45–46 then focused SAT; 5 Techne tools proposed. |
| 72 | Collatz (Ergodic View) | 2026-04-22 | aporia/docs/deep_research_batch4.md | Harmonia | Briefed | All orbits reach 1; Tao 2019 proved almost-bounded for almost all orbits. Four novel measurements proposed (spectral, tensor, 2-adic Lyapunov, entropy by residue). |
| 73 | MLC Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Harmonia | Briefed | Mandelbrot set is locally connected. Proved at non-renormalizable parameters (Yoccoz) and bounded-type infinitely renormalizable (Lyubich); unbounded combinatorics open. |
| 74 | Riemann Hypothesis | 2026-04-22 | aporia/docs/deep_research_batch4.md | Charon | Briefed | All non-trivial zeros at Re(s)=1/2; verified to 2×10^13 zeros (Platt-Trudgian 2021). Gap is "missing geometric object" not missing calculation; Prometheus contributes anomaly detection. |
| 75 | Hodge Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Harmonia | Briefed | Every Hodge class is algebraic; only proved for (1,1)-classes (Lefschetz). Our 66K g2c data can test Tate proxy via CM curves' extra Hodge classes. |
| 76 | Goldbach's Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Charon | Briefed | Every even n>2 is sum of two primes; ternary proved (Helfgott 2013), binary best is Chen 1+2. Goldbach comet's strand structure matches singular series — testable. |
| 77 | Twin Prime Conjecture | 2026-04-22 | aporia/docs/deep_research_batch4.md | Charon | Briefed | Infinitely many p with p+2 prime; gap 246 (Maynard-Polymath8b). Three Prometheus tests proposed: gap distribution spectroscopy, twin density in conductors, parity signal. |
| 78 | Why Sp uniquely negative in per-curve nbp? | 2026-04-23 | aporia/docs/deep_research_batch5/report_78_sp_uniqueness.md | Harmonia | Yes (F011) | Theoretical mechanism for Symplectic-only nbp sign-flip; connect to USp(4) 2-point correction sign. Confirmed empirically in F011 paper (Axis 3b matches Katz-Sarnak 1999 §3.3 sign). |
| 79 | Unitary beyond-KS signal | 2026-04-23 | aporia/docs/deep_research_batch5/report_79_unitary_beyond_ks.md | Harmonia | Yes (F011) | Why Dirichlet shows +ρ despite zero family-averaged 2-point correction. Refuted my pre-reg; Ergon's simpler Sp-unique model accepted (Seed 13). |
| 80 | Universal bulk rigidity as new constant | 2026-04-23 | aporia/docs/deep_research_batch5/report_80_universal_bulk_constant.md | Harmonia | Yes (F011) | Is +46-51% deficit at k=24 a new universal RMT constant beyond compact-group universality? Cross-family universality confirmed (EC non-CM, CM, G2C all within 5pp). |
| 81 | Maass GL3 degree-3 test design | 2026-04-23 | aporia/docs/deep_research_batch5/report_81_maass_gl3_design.md | Ergon | Yes (F011) | Sample size, pre-reg, run protocol on Maass GL3 corpus. Capstone executed: edge ρ=+0.8, bulk ρ=−0.8, n=1546 (gradient inversion within family). |
| 82 | Rhythma — OEIS/Belyi growth+singularity phoneme | 2026-04-23 | aporia/docs/deep_research_batch5/report_82_rhythma.md | Harmonia | Briefed | Phoneme based on Flajolet-Odlyzko singularity classification + growth-rate exponent. Proposal filed; instantiation pending. |
| 83 | Taxis — finite groups character phoneme | 2026-04-23 | aporia/docs/deep_research_batch5/report_83_taxis.md | Harmonia | Briefed | Character-degree distribution + conjugacy-class size as phoneme observable for groups domain. Proposal filed. |
| 84 | Schema — Bianchi hyperbolic phoneme | 2026-04-23 | aporia/docs/deep_research_batch5/report_84_schema.md | Harmonia | Briefed | Hyperbolic volume + trace-field label as phoneme; hooks to identity-join strategy. Proposal filed. |
| 85 | Topos — Belyi dessins monodromy phoneme | 2026-04-23 | aporia/docs/deep_research_batch5/report_85_topos.md | Harmonia | Briefed | Monodromy representation of Belyi covering as phoneme observable. Proposal filed. |
| 86 | H85 Chowla at genus-2 — proper test design | 2026-04-23 | aporia/docs/deep_research_batch5/report_86_h85_chowla_g2.md | Charon | Yes (F011) | Stratify by aut group; detect arithmetic modulation of Liouville sums at g2c discriminants. Design accepted; execution pending bandwidth scaling to 66K curves. |
| 87 | H15 NF tower termination via Golod-Shafarevich | 2026-04-23 | aporia/docs/deep_research_batch5/report_87_h15_nf_tower.md | Charon | Yes (F011) | Per-sample subprocess isolation architecture; cn ≥ 4 regime; specific LMFDB candidates. Multiple H15 attempts during F011 session — all stuck at depth=1 trivial closure. |
| 88 | CM classification via n ≥ 20K ingest design | 2026-04-23 | aporia/docs/deep_research_batch5/report_88_cm_ingest_design.md | Charon | Yes (F011) | What Mnemosyne ingest of CM curves enables decisive O/Sp/U classification. CM nbp inconclusive at current scale; ingest still pending. |
| 89 | Scholz conjecture | 2026-04-23 | aporia/docs/deep_research_batch5/report_89_scholz.md | Charon | Briefed | Reflection principles for 3-class groups; testable at LMFDB scale. Proposal filed. |
| 90 | Iwasawa main conjecture at p=2 | 2026-04-23 | aporia/docs/deep_research_batch5/report_90_iwasawa_p2.md | Charon | Briefed | 2-adic obstruction of Batch 1 #26; targeted test for totally-real NFs. Proposal filed; later expanded by #139 over real quadratic. |
| 91 | Mertens conjecture refinement | 2026-04-23 | aporia/docs/deep_research_batch5/report_91_mertens.md | Ergon | Briefed | Post-Odlyzko-te-Riele kill; search for sign changes at larger scale via Liouville partial sums. Proposal filed. |
| 92 | abc at genus-2 radical extension | 2026-04-23 | aporia/docs/deep_research_batch5/report_92_abc_g2.md | Charon | Briefed | Radical of discriminant vs Szpiro ratio for g2c; test abc generalization. Proposal filed. |
| 93 | Brumer-Stark at LMFDB scale | 2026-04-23 | aporia/docs/deep_research_batch5/report_93_brumer_stark.md | Charon | Briefed | Test analytic class-number formula for totally-real abelian extensions. Proposal filed; paired with #107 Stark units. |
| 94 | Langlands transfer GL(2,NF) → GL(2h,Q) | 2026-04-23 | aporia/docs/deep_research_batch5/report_94_langlands_gl2_nf.md | Harmonia | Briefed | Base-change tests for real-quadratic NF; coefficient compatibility. Proposal filed; extended to operator transport in #119. |
| 95 | Hilbert's 17th empirical on low-degree forms | 2026-04-23 | aporia/docs/deep_research_batch5/report_95_hilbert_17.md | Ergon | Briefed | Sum-of-squares decompositions; count expressibility at degree 2n-2. Proposal filed. |
| 96 | Jacobian of genus-3 hyperelliptic | 2026-04-23 | aporia/docs/deep_research_batch5/report_96_genus3_jacobian.md | Ergon | Briefed | Rank-distribution + Sha-parity tests on LMFDB g3 corpus (if ingested). Proposal filed; awaits g3 ingest. |
| 97 | Ulam spiral prime clustering at 10^10 scale | 2026-04-23 | aporia/docs/deep_research_batch5/report_97_ulam_spiral.md | Ergon | Briefed | Test Hardy-Littlewood via direct prime counts on spiral diagonals. Proposal filed. |
| 98 | Hecke orbit equidistribution on HMF over real-quadratic | 2026-04-23 | aporia/docs/deep_research_batch6/report_98_hecke_orbit_equidistribution.md | Harmonia | Pending | Empirical test of Zhang-Venkatesh on HMF Hecke orbits. Briefed; not yet executed (team stand-down). |
| 99 | Congruence prime distribution in HMF | 2026-04-23 | aporia/docs/deep_research_batch6/report_99_hmf_congruence_primes.md | Charon | Pending | Ribet-style congruence prime distribution; degree-2 extension. Briefed. |
| 100 | Isogeny graph diameter on EC/Q at fixed conductor | 2026-04-23 | aporia/docs/deep_research_batch6/report_100_isogeny_graph_diameter.md | Ergon | Pending | Mestre-Oesterlé style diameter on EC isogeny graphs at fixed conductor. Briefed. |
| 101 | p-adic uniformization rank for Shimura curves | 2026-04-23 | aporia/docs/deep_research_batch6/report_101_shimura_p_adic_uniformization.md | Harmonia | Pending | Drinfeld level structures and uniformization rank distribution. Briefed. |
| 102 | Mod-p Galois image statistics for g=2 Jacobians | 2026-04-23 | aporia/docs/deep_research_batch6/report_102_mod_p_galois_g2.md | Charon | Pending | Serre open-image conjecture at scale on g2c. Briefed. |
| 103 | Newton stratification on moduli of abelian varieties mod p | 2026-04-23 | aporia/docs/deep_research_batch6/report_103_newton_stratification.md | Harmonia | Pending | Empirical density of Newton strata on moduli mod p. Briefed; companion to #141 (crystalline) and #146 (prismatic). |
| 104 | Bianchi modular form base change to GL(2)/Q(√d) | 2026-04-23 | aporia/docs/deep_research_batch6/report_104_bianchi_hmf_base_change.md | Harmonia | Pending | CM-tower base-change check Bianchi → HMF. Briefed. |
| 105 | Heegner-point height distribution at rank-0 CM | 2026-04-23 | aporia/docs/deep_research_batch6/report_105_heegner_heights.md | Charon | Pending | Gross-Zagier empirical on rank-0 CM Heegner points. Briefed; extended by #158 (YZZ over real-quadratic). |
| 106 | Ceresa cycle non-triviality count for g=3 curves | 2026-04-23 | aporia/docs/deep_research_batch6/report_106_ceresa_cycle.md | Ergon | Pending | Beilinson height pairing on g=3 Ceresa cycles. Briefed. |
| 107 | Stark unit recovery at LMFDB scale | 2026-04-23 | aporia/docs/deep_research_batch6/report_107_stark_units.md | Charon | Pending | Regulator factorization paired with Brumer-Stark. Briefed. |
| 108 | Cuspidal cohomology of GL(n,Z) for n=5,6 | 2026-04-23 | aporia/docs/deep_research_batch6/report_108_cuspidal_cohomology_gln.md | Harmonia | Pending | Harder-type empirics on arithmetic-group cohomology. Briefed (multi-day budget). |
| 109 | Rogers-Ramanujan-type identities beyond level 5 | 2026-04-23 | aporia/docs/deep_research_batch6/report_109_rogers_ramanujan.md | Ergon | Pending | Bressoud-Andrews catalog scan beyond level 5. Briefed. |
| 110 | Mahler measure of K3 surfaces | 2026-04-23 | aporia/docs/deep_research_batch6/report_110_k3_mahler_measure.md | Charon | Pending | Deninger-Boyd K3 Mahler empirics extending Lehmer. Briefed. |
| 111 | Farey fraction statistics on Hecke triangle groups | 2026-04-23 | aporia/docs/deep_research_batch6/report_111_farey_hecke_triangle.md | Ergon | Pending | Sarnak spectral statistics on Farey fractions. Briefed. |
| 112 | Random Belyi map genus distribution | 2026-04-23 | aporia/docs/deep_research_batch6/report_112_random_belyi_genus.md | Harmonia | Pending | Eskin-Okounkov vs Hurwitz heuristic for Belyi-genus distribution. Briefed. |
| 113 | Euler product defect at small bad primes for g=2 L-functions | 2026-04-23 | aporia/docs/deep_research_batch6/report_113_g2_euler_defect.md | Charon | Pending | Extends F011 mechanism (c) Euler-product investigation to g2c. Briefed. |
| 114 | Sato-Tate refinement for rank-2 EC over Q | 2026-04-23 | aporia/docs/deep_research_batch6/report_114_sato_tate_rank2.md | Charon | Pending | Conditional-on-BSD Sato-Tate refinement for rank-2 EC. Briefed. |
| 115 | Rational cusps in noncongruence subgroups of PSL(2,Z) | 2026-04-23 | aporia/docs/deep_research_batch6/report_115_noncongruence_cusps.md | Harmonia | Pending | Atkin-Swinnerton-Dyer noncongruence-cusps test. Briefed. |
| 116 | Empirical distribution of regulator-to-torsion ratios | 2026-04-23 | aporia/docs/deep_research_batch6/report_116_bsd_tamagawa_calibration.md | Ergon | Pending | BSD Tamagawa calibration on regulator/torsion ratios. Briefed. |
| 117 | Twist family collisions at high conductor | 2026-04-23 | aporia/docs/deep_research_batch6/report_117_twist_collisions.md | Charon | Pending | Discriminant-matched EC twist families; finite-size selection-bias audit. Briefed. |
| 118 | Operator-correlation matrix on the 5-domain tensor | 2026-04-23 | aporia/docs/deep_research_batch6/report_118_operator_correlation.md | Harmonia | Pending | Direct test of operator-correlation across 5 tensor domains. Briefed; predecessor to Batch 7 transport tests. |
| 119 | Hecke ↔ Frobenius transport at LMFDB scale | 2026-04-23 | aporia/docs/deep_research_batch7/report_119_hecke_frobenius_transport.md | Harmonia | Pending | Recover Hecke eigenvalues on HMF from Frobenius data on associated EC/g2c. Briefed; canonical operator-transport probe. |
| 120 | p-adic L-function at LMFDB scale | 2026-04-23 | aporia/docs/deep_research_batch7/report_120_padic_l_function.md | Charon | Pending | Mazur-Tate-Teitelbaum zeros across 10⁴ ordinary EC. Briefed. |
| 121 | Motivic height × Faltings height correlation | 2026-04-23 | aporia/docs/deep_research_batch7/report_121_motivic_faltings.md | Harmonia | Pending | Beilinson-Bloch pairing vs Faltings height across g=2,3 Jacobians. Briefed. |
| 122 | Mock modular completion statistics | 2026-04-23 | aporia/docs/deep_research_batch7/report_122_mock_modular_completion.md | Harmonia | Pending | Zagier error-term growth across LMFDB harmonic-Maass forms. Briefed. |
| 123 | Knot concordance rank empirics | 2026-04-23 | aporia/docs/deep_research_batch7/report_123_knot_concordance.md | Ergon | Pending | Smooth vs topological slice genus across 10⁴ knots. Briefed. |
| 124 | Ray class group structure at LMFDB scale | 2026-04-23 | aporia/docs/deep_research_batch7/report_124_ray_class_groups.md | Charon | Pending | Genus-theoretic decomposition across ~10⁶ NF. Briefed. |
| 125 | Arithmetic dynamics preperiodic density | 2026-04-23 | aporia/docs/deep_research_batch7/report_125_arithmetic_dynamics_preperiodic.md | Ergon | Pending | Morton-Silverman bounds at scale across rational-function iterates. Briefed. |
| 126 | Ш analytic order distribution | 2026-04-23 | aporia/docs/deep_research_batch7/report_126_sha_analytic_order.md | Charon | Pending | Tate-Shafarevich order histogram across rank-0 EC at log cond > 8. Briefed. |
| 127 | Higher L-function moments | 2026-04-23 | aporia/docs/deep_research_batch7/report_127_higher_l_moments.md | Charon | Pending | Conrey-Keating-Snaith beyond M_4 to M_6, M_8 for rank-0 EC. Briefed. |
| 128 | Selberg trace formula empirics | 2026-04-23 | aporia/docs/deep_research_batch7/report_128_selberg_trace.md | Ergon | Pending | PSL(2,Z) Laplace spectrum low-lying zero statistics. Briefed. |
| 129 | Twisted L-function root-number distribution | 2026-04-23 | aporia/docs/deep_research_batch7/report_129_twisted_root_numbers.md | Charon | Pending | ε(E, χ) for χ quadratic Dirichlet across 10⁵ twists. Briefed. |
| 130 | Cohen-Lenstra across class-group strata | 2026-04-23 | aporia/docs/deep_research_batch7/report_130_cohen_lenstra_strata.md | Harmonia | Pending | Stratified p-part density for p ∈ {3,5,7,11}. Briefed. |
| 131 | Siegel modular forms genus 3 | 2026-04-23 | aporia/docs/deep_research_batch7/report_131_siegel_g3.md | Harmonia | Pending | First-pass cataloging from Bergström-Faber-van der Geer tables. Briefed. |
| 132 | Local Langlands depth-zero census | 2026-04-23 | aporia/docs/deep_research_batch7/report_132_local_langlands_depth_zero.md | Harmonia | Pending | Supercuspidal representations across GL(2)/Q_p, p ≤ 19. Briefed. |
| 133 | Hypergeometric motives L-function empirics | 2026-04-23 | aporia/docs/deep_research_batch7/report_133_hypergeometric_motives.md | Charon | Pending | Rodriguez-Villegas HGM family Sato-Tate scan. Briefed. |
| 134 | Hilbert scheme Göttsche generating function | 2026-04-23 | aporia/docs/deep_research_batch7/report_134_hilbert_scheme_gottsche.md | Ergon | Pending | Euler-characteristic sequences for Hilb^n(K3). Briefed. |
| 135 | Dedekind η-quotient rationality at level > 100 | 2026-04-23 | aporia/docs/deep_research_batch7/report_135_eta_quotient_high_level.md | Ergon | Pending | Complement to #109 at extended range. Briefed. |
| 136 | Algebraic K-theory regulators | 2026-04-23 | aporia/docs/deep_research_batch7/report_136_k_theory_regulators.md | Charon | Pending | Beilinson regulator at scale for number fields, matched to ζ_F'(0). Briefed. |
| 137 | Arithmetic progressions in OEIS prime sequences | 2026-04-23 | aporia/docs/deep_research_batch7/report_137_oeis_arithmetic_progressions.md | Ergon | Pending | Green-Tao-style empirics across OEIS-indexed prime families. Briefed. |
| 138 | Minkowski constant sharpness across NF | 2026-04-23 | aporia/docs/deep_research_batch7/report_138_minkowski_sharpness.md | Ergon | Pending | How close disc lower bound comes to Minkowski bound, stratified by degree/signature. Briefed. |
| 139 | Iwasawa main conjecture for HMF over real quadratic | 2026-04-25 | aporia/docs/deep_research_batch8/report_139_iwasawa_hmf_real_quadratic.md | Charon | Pending | Extend Skinner-Urban beyond GL(2)/Q via Λ-truncation comparison of Selmer characteristic ideal vs Hida p-adic L. Pending — newly delivered. |
| 140 | Mazur-Galois deformation ring local components | 2026-04-25 | aporia/docs/deep_research_batch8/report_140_mazur_galois_deformation_local.md | Harmonia | Pending | Empirical structure of universal deformation rings at small primes via Böckle presentations vs Hecke ring T_{ρ̄}. Pending. |
| 141 | F-isocrystal Newton stratification | 2026-04-25 | aporia/docs/deep_research_batch8/report_141_f_isocrystal_newton_stratification.md | Harmonia | Pending | Crystalline-channel Newton-stratum density vs Rapoport-Richartz prediction; Voloch-style "Newton-above-Hodge" detector. Pending. |
| 142 | Manin conjecture for Fano threefolds | 2026-04-25 | aporia/docs/deep_research_batch8/report_142_manin_fano_threefolds.md | Charon | Pending | Empirical (a, b, c) measurement on ~10 Mori-Mukai families against Batyrev-Manin-Peyre prediction. Pending. |
| 143 | Heath-Brown circle method for cubic forms | 2026-04-25 | aporia/docs/deep_research_batch8/report_143_heath_brown_cubic.md | Ergon | Pending | Hardy-Littlewood constant measurement for ~200 cubic forms in n ∈ {4,5}; flag Brauer-Manin candidates. Pending. |
| 144 | Vinogradov mean value at LMFDB scale | 2026-04-25 | aporia/docs/deep_research_batch8/report_144_vinogradov_mean_value.md | Charon | Pending | Empirical exponent for J_{s,k}(N) vs Bourgain-Demeter-Guth sharp bound. Pending. |
| 145 | Anabelian section conjecture for elliptic curves | 2026-04-25 | aporia/docs/deep_research_batch8/report_145_anabelian_section.md | Harmonia | Pending | Section/Point ratio measurement for E/K (K imaginary quadratic) via Selmer-style H¹ counting. Pending. |
| 146 | Perfectoid / prismatic site empirical cohomology | 2026-04-25 | aporia/docs/deep_research_batch8/report_146_perfectoid_prismatic.md | Harmonia | Pending | Bhatt-Scholze prismatic dimension test for Hodge-Tate decomposition on small varieties. Pending; third leg of p-adic Hodge testbed (#103, #141, #146). |
| 147 | Theta correspondence Howe-Kim duality | 2026-04-25 | aporia/docs/deep_research_batch8/report_147_theta_correspondence_howe_kim.md | Harmonia | Pending | Howe-Rallis L-function identity test for theta lifts of GL(2)/Q forms to Sp(4). Pending. |
| 148 | Drinfeld modular forms over F_q(T) | 2026-04-25 | aporia/docs/deep_research_batch8/report_148_drinfeld_modular_forms.md | Harmonia | Pending | Cross-characteristic test of F011 bulk rigidity via Drinfeld L-functions. Pending. |
| 149 | Coleman p-adic family rank-jump distribution | 2026-04-25 | aporia/docs/deep_research_batch8/report_149_coleman_padic_family_rank.md | Charon | Pending | Mazur-Tilouine rank-jump density along Coleman families at p ∈ {3,5,7}. Pending. |
| 150 | Kloosterman sum distribution at large modulus | 2026-04-25 | aporia/docs/deep_research_batch8/report_150_kloosterman_distribution.md | Ergon | Pending | Katz vertical Sato-Tate for Kloosterman angles + Heath-Brown-Patterson cubic-symmetry probe. Pending. |
| 151 | Sum of three squares — Linnik equidistribution | 2026-04-25 | aporia/docs/deep_research_batch8/report_151_linnik_3_squares.md | Ergon | Pending | Measure spherical equidistribution rate exponent vs Iwaniec-Kowalski 1/28 and Duke 1/8. Pending. |
| 152 | Roth-Schmidt subspace theorem empirics | 2026-04-25 | aporia/docs/deep_research_batch8/report_152_roth_schmidt_subspace.md | Ergon | Pending | Irrationality measures μ(α) for ~500 algebraic α; Schmidt subspace count test. Pending. |
| 153 | GUE pair correlation for Maass forms | 2026-04-25 | aporia/docs/deep_research_batch8/report_153_gue_maass_pair_correlation.md | Ergon | Pending | Rudnick-Sarnak R_2 convergence + F011 transfer test on `maass_form` table. Pending. |
| 154 | Iwahori-Hecke algebra Kazhdan-Lusztig cells | 2026-04-25 | aporia/docs/deep_research_batch8/report_154_iwahori_hecke_kazhdan_lusztig.md | Harmonia | Pending | Cell-statistic verification for S_6..S_9, B_4, D_4 via Sage `KazhdanLusztigPolynomial`. Pending. |
| 155 | Tamagawa numbers for unitary groups | 2026-04-25 | aporia/docs/deep_research_batch8/report_155_tamagawa_unitary_groups.md | Charon | Pending | tau(U(n)) = 2 calibration on 50 imaginary-quadratic K via Sansuc + Bhargava-Gross. Pending. |
| 156 | Selmer scheme rank distribution | 2026-04-25 | aporia/docs/deep_research_batch8/report_156_selmer_scheme_rank.md | Charon | Pending | BKLPR distribution test for Sel_n, n ∈ {2,3,4,5,7}, conductor-stratified. Pending; extends #14, #54. |
| 157 | Weil bound and Burgess refinement empirics | 2026-04-25 | aporia/docs/deep_research_batch8/report_157_weil_burgess_character_sums.md | Ergon | Pending | Burgess exponent saturation measurement across primitive Dirichlet χ at p ∈ {1009, 10007, 100003}. Pending. |
| 158 | Heegner cycles on Shimura sets — YZZ heights | 2026-04-25 | aporia/docs/deep_research_batch8/report_158_heegner_shimura_yzz.md | Harmonia | Pending | Yuan-Zhang-Zhang formula validation on 50 (E, F) with F real quadratic. Pending. |

---

## Techne Tool Evaluations (separate numbering — Batch 4 used #78, 79, 80 for these)

| ID | Name | Date | Location | Researcher | Adopted? | Recommendation |
|---|---|---|---|---|---|---|
| T1 | OSCAR.jl Evaluation | 2026-04-22 | aporia/docs/deep_research_batch4.md (#78) | Techne | Yes (Tech adopted) | Phased adoption: Hecke/Nemo NOW for NF/class groups (Windows-native, 2-5x Sage); evaluate full OSCAR via WSL2; skip Windows-native OSCAR until polymake support improves. |
| T2 | SDPA-GMP + SoS Tools | 2026-04-22 | aporia/docs/deep_research_batch4.md (#79) | Techne | Yes (Tech adopted) | Reproduce Razborov's Caccetta-Häggkvist certificate via flagmatic in WSL2 as validation; use CSDP/SCS for exploration, SDPA-GMP for certificate promotion; defer Ramsey R(5,5) SDP. |
| T3 | Lean4 Ecosystem 2025-2026 | 2026-04-22 | aporia/docs/deep_research_batch4.md (#80) | Techne | Yes (Tech adopted) | Install Lean4 + LeanDojo immediately; deploy DeepSeek-Prover-V2-7B (fits 17GB VRAM in bf16); use Herald + ProofBridge for autoformalization with 50% manual fallback. |

---

## Aggregate Statistics

| Metric | Count |
|---|---|
| Total problem briefs (#1–158) | 158 |
| Techne tool evaluations (T1–T3) | 3 |
| **Grand total reports** | **161** |
| Targeted Charon | 53 |
| Targeted Harmonia | 60 |
| Targeted Ergon | 45 |
| Targeted Techne | 3 |
| Marked **Yes (F011)** — actioned in 2026-04-22 sprint | 13 |
| Marked **Yes / Resolved** — confirmed engagement or removed from open list | 9 |
| Marked **Briefed** — research delivered, execution not centrally tracked | 78 |
| Marked **Pending** — Batches 6–8, no execution yet | 61 |

## Cross-batch threads (for navigation)

- **F011 universality (2026-04-22 paper):** #1, #4, #14, #15, #23, #50, #54, #78, #79, #80, #81, #86, #87, #88, #113, #148, #153.
- **p-adic Hodge testbed:** #40, #103, #141, #146.
- **Operator transport / correlation:** #38, #39, #94, #118, #119, #140, #145, #147.
- **Selmer / BKLPR:** #14, #54, #156.
- **Iwasawa:** #11, #26, #90, #139.
- **Diophantine / silent islands:** #142, #143, #151, #152, #157.
- **Lehmer / Mahler:** #15, #110.
- **Heegner / Shimura:** #105, #158.
- **Knot theory / silent island:** #3, #6, #16, #47, #123.
- **Function-field / Drinfeld:** #148.
- **Galois deformation:** #36, #140.
- **Cohen-Lenstra / class groups:** #18, #54, #124, #130, #138.

## Status snapshot at 2026-04-25

The compendium captures all deep-research output. The main gap is *not* in research production but in **execution feedback**: Batches 6–8 (61 reports, ~38% of the corpus) are "Pending" because the engineering team stood down after the F011 sprint and Batch 7 close-out. Recommended next coordination: stand up an `execution_status.jsonl` ledger keyed on report ID so per-report execution can be tracked centrally rather than reconstructed from session journals.

---

*Compiled by Aporia from the master index (`aporia/docs/deep_research_master_index.md`), batch documents 1-4, batch INDEX/seed files for 5-8, and session journals for the 2026-04-22 F011 sprint.*
