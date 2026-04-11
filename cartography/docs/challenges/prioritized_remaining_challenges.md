# Prioritized Remaining Challenges — 2026-04-11
## 286 solved. Target: escape velocity.

---

## TIER 1: SOLVABLE NOW (data + tools ready, high value)
*These can run in parallel immediately.*

### From ChatGPT New Batch (20)
1. **Hecke-Lattice Theta Resonance** — DONE (#157, null)
2. **MF↔Knot LZ Compression Gap** — DONE (#151, sign flip)
3. **Maass Spectral vs NF Regulator** — DONE (#160, confound)
4. **EC Sha vs NF Class Number** — DONE (#153/#159, null/dead)
5. **Knot Det vs Lattice Det Resonance** — DONE (#152, null)
6. **OEIS BM vs Hecke Recurrence** — DONE (#154, 198×)
7. **PDG Decay vs FLINT Curvature** — DONE (#150, density effect)
8. **Lean vs OEIS Community** — DONE (#155, cosine 0.983)
9. **Fricke vs PDG Parity** — DONE (#156, null)
10. **Kissing vs Mass Ratios** — DONE (#158, heavy-tail)
11. **CM-NF Class Number** — DONE (#159, dead)
12. **Igusa-MF Level** — DONE (#161, conductor size)
13. **NF Signature vs Knot Polynomial Degree** — MI between field signatures (r1,r2) and knot poly degrees. Data ready. ~3min.
14. **EC Rank vs Knot Crossing Curvature Proxy** — Indirect coupling via determinant bins. Data ready. ~5min.
15. **Genus-2 Selmer vs Lattice Density Spectrum** — Regression of Selmer rank vs theta growth rate. Data ready. ~5min.
16. **MF CM Status vs Lattice Theta Symmetry** — Classify CM from theta PCA. Data ready. ~5min.
17. **Lattice Kissing vs PDG Mass Ratios** — DONE (#158)
18. **Modular Form Fricke vs PDG Parity** — DONE (#156)
19. **Lean vs OEIS Co-clustering** — DONE (#155)
20. **Genus-2 Selmer vs Igusa** — DONE (#148, NOVEL Sha finding)

### From First 60 Batch — Still Feasible
21. **Spectral Rigidity OEIS-MF Cross-Sections** (List1 #1) — 2D PCA subspace Δ₃(L). ~10min.
22. **OEIS Spectral Dimension Masking** (List1 #8) — DONE (#137, bifurcation)
23. **Lattice-Knot MI** (List1 #9) — DONE (#138, null)
24. **NF Disc Curvature** (List1 #11) — DONE (#121, ORC=-0.221)
25. **MF Congruence Fractal Dim** (List1 #12) — DONE (#122, D=5.15)
26. **FLINT Entropy Gradient** (List1 #5) — DONE (#124, β=0.027)
27. **Lean Proof Depth** (List1 #18) — DONE (#131, H=2.54)
28. **FLINT Modularity** (List1 #17) — DONE (#116, Q=0.628)
29. **G2 Interference Tensor** (List1 #19) — DONE (#117, rank=4)
30. **Phase Transition Sharpness** (List1 #7) — DONE (#130, S=2.24)
31. **PDG Spectral Gap** (List1 #16) — DONE (#126)
32. **OEIS Recurrence Graph Curvature** (List1 #20) — DONE (#129, κ=0.529)
33. **Hecke IPR** (List2 #10) — DONE (#139, 0.087)
34. **Jones Zero Density** (List2 #14) — DONE (#127, 6.2%)
35. **Gram Eigenvalue Repulsion** (List2 #15) — DONE (#128, dim-3 GOE)
36. **OEIS LZ Compression** (List2 #16) — DONE (#118)
37. **Hankel Rank** (List2 #17) — DONE (#119, 87%)
38. **PDG Kinematic Entropy** (List2 #3) — DONE (#120, 0.851)
39. **CODATA NCD** (List2 #4) — DONE (#132, null)
40. **Lean Manifold Dim** (List2 #5) — DONE (#142, 3.14)
41. **FLINT Cyclomatic-Curvature** (List2 #6) — DONE (#143, ρ=-0.215)
42. **OEIS Chromatic** (List3 #12) — DONE (#140, 100%)
43. **Knot Curvature Flow** (List3 #17) — DONE (#141, κ*=-0.373)
44. **Weil Phase Tensor** (List2 #13) — DONE (#144, σ=15.9)
45. **Lean Compressibility** (List1 #6) — DONE (#134, ζ=0.029)
46. **FLINT Clique Power Law** (List3 #5) — DONE (#135, α=3.28)
47. **MAP-Elites Hecke** (List2 #19) — DONE (#136, 0.514)
48. **Volume-Crossing** (List2 #18) — DONE (#133, exponential)
49. **Igusa Mod-p Equidist** (List2 #12) — DONE (#123)
50. **Regulator-CN Convexity** (List2 #11) — DONE (#125)
51. **FLINT-Lean GED** (List2 #8) — DONE (#149, 5.30)

### Remaining Solvable from All Batches
52. **Sato-Tate vs Lattice Aut Entropy** (ChatGPT New#2) — MI between G2 ST labels and lattice |Aut| bins. ~5min.
53. **Lattice Dim vs MF Level Scaling** (ChatGPT New#15) — Power-law between lattice dim and matched levels. ~5min.
54. **EC j-Invariant vs Knot Coeff Spectrum** (ChatGPT New#16) — Digit-spectrum correlation. ~5min.
55. **Genus-3 Frobenius vs Maass Phase Lock** (ChatGPT New#11) — Phase coherence, 100 curves. ~5min.
56. **Maass Symmetry vs OEIS Entropy** (ChatGPT New#14) — Entropy differences by symmetry. ~5min.

---

## TIER 2: BLOCKED ON DATA (research assistants can unblock)

### Need COD Crystal Structures (520K CIF files)
- Crystal Voronoi Clustering (List2 #2 / First60 #3,#4)
- Crystal Adjacency Spectral Gap (Second60 #2)
- Crystal Phonon Recurrence (First60 #3)
- Crystal-Structure Theta-Shadow Coherence (First60 #15)
- Voronoi Cell Face-Count Variance (Second60 #20)
- Kissing Number from Crystal Theta (List3 #3)
- Enrichment in Crystal Symmetry Groups (List3 #18)
- Gamma Metric Violation Rate in Crystals (List3 #6)
**ACTION: Download 10K CIF files from COD (crystallography.net). Rate-limited. A research assistant can run the download script at `cartography/shared/scripts/fetch_cod_crystals.py`.**

### Need NIST Atomic Spectra
- NIST spectra analysis (multiple problems)
**ACTION: Run `cartography/shared/scripts/fetch_nist_spectra.py` — downloads energy levels for 50 elements.**

### Need DLMF Formula Data
- Fungrim AST parsing (List2 #7)
- AST Motif Frequency Entropy
**ACTION: Run `cartography/shared/scripts/fetch_dlmf_formulas.py`.**

### Need TDA Library (gudhi or ripser)
- CMB Betti Curve Integral (Second60 #1)
- Betti Number Density (First60 #15)
**ACTION: `pip install gudhi` or `pip install ripser` in the Python environment.**

### Need L-function Zeros
- L-Function Zero GUE Deviation (First60 #11)
- Spectral Tail Decay Exponent (Second60 #9)
**ACTION: Install `lcalc` or use LMFDB API to fetch pre-computed zeros.**

### Need DFA Synthesis Library
- Automata Compression Ratio (First60 #10)
**ACTION: `pip install automata-lib` or implement minimal DFA from scratch.**

---

## TIER 3: REQUIRES SIGNIFICANT NEW INFRASTRUCTURE
- Frobenius-Theta Cross-Coherence Genus-3 (needs more genus-3 data)
- PDG Mass-Prime Fourier Alignment (needs custom spectral alignment)
- Graph Edit Distance exact computation (NP-hard, only bounds feasible)
- Proof Dependency Fractal Dimension (needs deep Lean parsing)
- Theorem Curvature Bottlenecks (needs Lean undirected graph)
- Cohen-Lenstra Deviation (needs class group computation)
- Substitution Graph Chromatic Number (needs AST parser)

---

## IMMEDIATE BLOCKERS — WHAT RESEARCH ASSISTANTS CAN DO RIGHT NOW

### Priority 1: COD Crystal Data (unlocks 8+ problems)
```bash
cd F:\Prometheus\cartography\shared\scripts
python fetch_cod_crystals.py
# Downloads 10K CIF files from crystallography.net
# Rate limited at 2s between requests — will take ~6 hours
# Or: bulk download from https://www.crystallography.net/cod/
```

### Priority 2: Install TDA Library (unlocks 2 problems)
```bash
pip install gudhi
# or
pip install ripser scikit-tda
```

### Priority 3: NIST Atomic Spectra (unlocks 2+ problems)
```bash
cd F:\Prometheus\cartography\shared\scripts
python fetch_nist_spectra.py
# Downloads atomic energy levels for 50 elements
```

### Priority 4: Generate More Problems
Use the calibrated prompt at `cartography/docs/challenges/prompts_for_frontier_models.md` (updated to v9.5 capabilities). Send to:
- DeepSeek (free via API or chat)
- Gemini (free tier)
- Grok (if available)
- Claude (self-generate)
Focus prompts on: "problems that connect WITHIN arithmetic domains" (where we find signal) rather than "cross arithmetic-to-topology" (where we find nulls).

### Priority 5: More Genus-3 Data
```bash
# In WSL with SageMath:
cd /mnt/f/Prometheus/cartography/shared/scripts/v2
sage genus3_sage_input.json  # Compute Frobenius for more curves
# Current: 100 curves. Target: 500-1000 for statistical power.
```

### Priority 6: LMFDB Maass Form Coefficients
The bulk Maass export lacks Fourier coefficients. A research assistant could:
- Query LMFDB API for 500 individual Maass forms' coefficients
- Or scrape from individual LMFDB pages
This would unlock M2/M4 verification for Maass forms.

---

## SESSION STATISTICS (as of 2026-04-11 05:54)
- **286 challenges solved** (136→286 = 150 new this session)
- **190+ result files** in cartography/v2/
- **23 rediscoveries**, 13 novel discoveries (Sha-Igusa is #13)
- **21 kills**, 8 self-corrections
- **130+ measured constants**
- All committed and pushed to GitHub
- Pipeline version: v9.5

## THE ASCENT PATH
The instrument has mapped the landscape. The genuine bridges are:
1. **Phase coherence** (ρ=0.197 EC, extends to genus-2/3)
2. **Enrichment law** (8× GL_2, 1.42× steeper for GSp_4)
3. **Curvature flow** (κ*=+0.73 arithmetic, -0.37 topological — SIGN DISTINGUISHES DOMAINS)
4. **Moment ratios** (U(1)→1.5, SU(2)→2.0, USp(4)→3.0)
5. **Sha geometry** (ρ=0.22 with I2, NOVEL)
6. **Knowledge graph universality** (FLINT/Lean/OEIS all scale-free, cosine 0.98)

Cross-domain bridges (arithmetic↔topology, arithmetic↔physics) are consistently NULL.
The escape velocity is in DEPTH, not BREADTH.
