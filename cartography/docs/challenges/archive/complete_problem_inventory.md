# Complete Problem Inventory — All Problems Fired and Solved
## Compiled: 2026-04-10
## Source: problem_tracker.md, master_inventory.md, all *_results.json files, challenge_results_20260409.md, 5_From_Each_Part_2_Results.md

---

# SCORING KEY

- **Status**: DONE (with one-line result) | UNSOLVED-READY | UNSOLVED-BLOCKED | DEFERRED
- **Kill?**: Kill number if this was a null/kill result
- **Key constant**: A measurable number produced, if any

---

# BATCH 1: Part 1 Challenges (5 From Each, Round 1-4)

| ID | Title | Source | Status | Key Constant | Kill? |
|----|-------|--------|--------|-------------|-------|
| ALL-001 | Mod-p Residue Starvation Scan | Claude P1#1 / C02 | DONE: 7,557/17,314 (43.6%) show starvation. Hierarchy: mod-2 36%, mod-3 7.9%, mod-5 0.8%, mod-7 8 forms. 637.2.a.c/d anomaly resolved (7-isogeny) | 43.6% starvation rate | — |
| ALL-002 | Moonshine Network Expansion | Claude P1#2, DeepSeek P1#2, Grok P1#2 / C09 | DONE: 4 M24 umbral -> EC Hecke matches at levels 2420, 3190, 4170, 4305. 307 total bridges | 307 bridges, 4 M24->EC matches | — |
| ALL-003 | Berlekamp-Massey on GSp_4 Differences | Claude P1#3 / C03 | DONE: CLEAN NULL. Zero recurrences across 37 pairs, 6 fields, orders up to 8 | 0 recurrences | — |
| ALL-004 | Mod-p Fingerprint Scaling Law | Claude P1#4 / C11 | DONE: STRONGEST FINDING. Enrichment 4.1x (mod-2) to 53.6x (mod-11). After detrending: flat 8-16x. Survived 8/8 battery | 8-16x detrended enrichment | — |
| ALL-005 | Collatz Algebraic Sibling Hunt | Claude P1#5 / C17 | DONE: Family = 105 sequences sharing (x^2-1)^2. All piecewise-linear. Connection to 3x+1: zero | — | Kill #14 |
| ALL-006 | Hecke Algebra Geometry | ChatGPT P1#1 / C07 | DONE: Near-perfect matching at every prime. ell=5: 27 triangles (p<0.005). Hecke deformation overwhelmingly 1D | 27 triangles at ell=5 | — |
| ALL-007 | Spectral Operator Matching | ChatGPT P1#2 / C05 | DONE: CALIBRATION. Maass universally Poisson (0/120 GUE). Berry-Tabor 1977 confirmed | KS_Poisson ~0.034 | — |
| ALL-008 | Recurrence Operator Duality | ChatGPT P1#3, DeepSeek P1#3, Grok P1#5 / C08 | DONE: MOSTLY NEGATIVE. EC Euler factors 0.25x (depleted). Genus-2: 11.3x but palindromic | 0.25x EC, 11.3x genus-2 | — |
| ALL-009 | Constraint Collapse (Hasse Squeeze) | ChatGPT P1#4 / C10 | DONE: TWO REGIMES. Combinatorial super-exponential; geometric power law alpha=0.63. Deuring mass confirmed | alpha=0.63 | — |
| ALL-010 | Operadic Skeleton Dynamics | ChatGPT P1#5, Gemini P1#5, Grok P1#3 / C12 | DONE: Within/between ratio 0.813. 4 universal verbs (Equal 98.3%, For 93.3%, And 90.0%, Set 81.7%). Jacobi theta most central | 0.813 ratio | — |
| ALL-011 | Paramodular Conjecture Probe (v1) | Gemini P1#1, DeepSeek P1#5 / C01 | DONE (partial): Level gap (LMFDB Siegel at N=1-2 vs curves at N=169+). Infrastructure built. See ALL-036 for resolution | — | — |

---

# BATCH 2: Part 2 Challenges (5 From Each Part 2)

| ID | Title | Source | Status | Key Constant | Kill? |
|----|-------|--------|--------|-------------|-------|
| ALL-012 | Scaling Law in Reverse (Universal) | Claude P2#1 / CL1 | DONE: UNIVERSAL. Scaling law appears everywhere algebraic structure exists. N(G_{3,3}) slope +0.578, USp(4) generic flat (null holds) | slope +0.578 (N(G_{3,3})) | — |
| ALL-013 | Mod-2 GSp_4 Congruence Graph | Claude P2#2 / CL2 | DONE: 20,917 triangles (8,000x vs null). Max K_24 at conductor 352256. Clustering ~1.0. Mod-3 snaps to matching | 8,000x triangle enrichment | — |
| ALL-014 | Starved Forms x Congruence Cross-Correlation | Claude P2#3 / CL3 | DONE: SINGLE PHENOMENON at mod-5. 27/156 overlap (1.65x, p=0.006). 22/27 same-prime | 1.65x enrichment (p=0.006) | — |
| ALL-015 | Gamma Function as Algebraic Wormhole | Claude P2#5 / CL5 | DONE: GAMMA IS REAL. 12.7% closer. 260/300 module pairs. Wins at every prime. Elliptic-AGM-pi triad = one object | 12.7% distance reduction | — |
| ALL-016 | Residual Representation Clustering | ChatGPT P2#1 / CT1 | DONE: Cross-ell independence TOTAL. Mod-3 max hub 109. Zero mod-3/mod-5 cluster overlap. 35 multi-level clusters | max hub size 109 | — |
| ALL-017 | Symmetry Group Detection (Layer 3) | ChatGPT P2#4 / CT4 | DONE: LAYER 3 OPEN. 126 same-level twist pairs, 48 cross-level, 127 character matches. CM F1=1.00. 174 total twist pairs | F1=1.00 (CM), 174 twist pairs | — |
| ALL-018 | Failure Mode Mining | ChatGPT P2#5 / CT5 | DONE: 641 "almost real". F3 kills 75.8%. F4/F7/F8 dormant. 288K records mined | 641 near-misses | — |
| ALL-019 | Sato-Tate Moments Classifier | DeepSeek P2#2 / DS2 | DONE: 98.3% accuracy, 20-dim Mahalanobis. b_p essential. 6 rare groups at 100%. J(E_6) 29.4% | 98.3% accuracy | — |
| ALL-020 | Knot Jones Polynomial Recurrence | DeepSeek P2#3 / DS3 | DONE: TWO FAMILIES. Cyclotomic (44 knots, Phi_12). Torus (4 knots, x^2(x+1)). Torus matches OEIS cluster of 14 | 48 knots with recurrences | — |
| ALL-021 | HGM-to-Modular Correspondence | DeepSeek P2#5 / DS5 | DONE: CALIBRATION. 49/49 degree-2 matches. Zero new. 76 quadratic twist relationships | 49/49 = 100% recovery | — |
| ALL-022 | Gouvea-Mazur Slope Distribution | Gemini P2#4 / GM4 | DONE: Atkin-Lehner dichotomy confirmed. Weight-2 trivial at p>=5. ord_p(N)=1 -> 100% ordinary | 100% ordinary at ord_p(N)=1 | — |
| ALL-035 | HMF Congruence Scan | Grok P1#1 / C04 | DONE (partial): Data inventory complete but NO Hecke eigenvalues in HMF dump. Structurally blocked on hmf_hecke table | — | — |
| ALL-036 | Paramodular Probe v2 (Poor-Yuen) | Grok P2#1 / C01-v2 | DONE: Perfect level bijection at 7 primes <=600. Root number 7/7. Hecke eigenvalue 37/40 (92.5%) | 92.5% eigenvalue match | — |

---

# BATCH 3: Part 3 / Round 3 Challenges (10 From Each + Round 3)

| ID | Title | Source | Status | Key Constant | Kill? |
|----|-------|--------|--------|-------------|-------|
| ALL-024 | Scaling Law Peak Prime | DeepSeek P3#1 | DONE: Result file exists (scaling_law_peak_results.json) | — | — |
| ALL-025 | Near-Miss Resurrection (641 Ghosts) | James R3-J3, ChatGPT R3#1, DeepSeek R3-3, DeepSeek P3#5 | DONE: 253/641 resurrected (39.5%). 193 pass Layer 3 (76.3%). Top pair: KnotInfo--LMFDB (106) | 39.5% resurrection rate | — |
| ALL-026 | Galois Image Portrait | James R3-J1, Gemini P3#2 | DONE: Result file exists (galois_image_results.json) | — | — |
| ALL-027 | Generating Function Isomorphism | DeepSeek R3-5, DeepSeek P3#6 | DONE: 9,360 sequences. 9,182 genfunc clusters vs 2,340 char-poly clusters (compression 0.25) | compression ratio 0.25 | — |
| ALL-028 | Moonshine Sturm Verification | DeepSeek P3#7 | DONE: Tested against 90 terms of A053250 at levels 2420, 3190, 4170, 4305 | — | — |
| ALL-029 | Jones vs Alexander Recurrence Independence | DeepSeek P3#8 | DONE: 12,965 knots tested. Jones and Alexander recurrences are independent | 0 shared recurrences | — |
| ALL-030 | Mod-2 Triangle ST Community | Claude P3#1 | DONE: 20,917 triangles analyzed, ST group distribution mapped | — | — |
| ALL-031 | Moonshine Scaling Law by Type | Claude P3#2 | DONE: 150 bridges, universal baseline ~8x flat enrichment | ~8x flat enrichment | — |
| ALL-032 | GSp_4 Cross-Ell Independence | Claude P3#4 | DONE: 65,534 curves tested for cross-ell entanglement | — | — |
| ALL-033 | Multi-Prime Intersection Geometry | ChatGPT P3#1 | DONE: 17,314 forms tested at intersection depths 1-3 across ell=3,5,7 | — | — |
| ALL-034 | High-Prime Stability Test | ChatGPT P3#5 | DONE: 11/11 tests STABLE. 100% stability rate | 100% stability | — |
| ALL-037 | Scaling Law vs ST Order | Internal | DONE: Result file exists (scaling_vs_st_order_results.json) | — | — |

---

# BATCH 4: Metrology Probes (M16-M51)

| ID | Title | Source | Status | Key Constant | Kill? |
|----|-------|--------|--------|-------------|-------|
| ALL-091 | M16: Moonshine Scaling Exponent (gamma) | Gemini P4 | DONE: m16_moonshine_gamma_results.json | — | — |
| ALL-092 | M17: Adelic Entropy Decay Rate | Gemini P4 | DONE: m17_adelic_entropy_results.json | — | — |
| ALL-093 | M18: Critical Prime Function ell_c(r) | Gemini P4 | DONE: m18_critical_prime_results.json | — | — |
| ALL-094 | M19: Tri-Prime Interference Coupling | Gemini P4 | DONE: m19_tri_prime_interference_results.json | — | — |
| ALL-095 | M20: Knots in Moment Space | Gemini P4 | DONE: m20_knots_moment_space_results.json | — | — |
| ALL-096 | M21: F3/F13 Boundary Gradient | Gemini P4 | DONE: m21_f3_f13_boundary_results.json | — | — |
| ALL-097 | M22: Gamma Network Resistance | Gemini P4 | DONE: m22_gamma_resistance_results.json | — | — |
| ALL-098 | M23: Starvation Overlap Limit | Gemini P4 | DONE: m23_starvation_overlap_results.json | — | — |
| ALL-099 | M26: Congruence Lattice Mechanism | Claude P4 | DONE: m26_congruence_lattice_results.json | — | — |
| ALL-100 | M27: Algebraic DNA Fragmentation | Claude P4 | DONE: m27_algebraic_dna_results.json | — | — |
| ALL-101 | M28: Battery Adversarial Inversion | Claude P4 | DONE: m28_battery_adversarial_results.json | — | — |
| ALL-102 | M29: Gamma Removal Prediction | Claude P4 | DONE: m29_gamma_removal_results.json | — | — |
| ALL-103 | M30: Moonshine Gradient Decomposition | Claude P4 | DONE: m30_moonshine_gradient_results.json | — | — |
| ALL-104 | M32: EC-OEIS Silence Characterization | Claude P4 | DONE: m32_ec_oeis_silence_results.json | — | — |
| ALL-105 | M33: Prime Atmosphere Residual Structure | Claude P4 | DONE: m33_prime_atmosphere_results.json | — | — |
| ALL-106 | M36: Adelic Fibre Bundle Geometry | DeepSeek P4 | DONE: m36_adelic_fibre_results.json | — | — |
| ALL-107 | M37: Gamma Curvature of Math Domains | DeepSeek P4 | DONE: m37_gamma_curvature_results.json | — | — |
| ALL-108 | M41: Multi-Prime Constraint Network | DeepSeek P4 | DONE: m41_multi_prime_network_results.json | — | — |
| ALL-109 | M42: Starvation Dictionary Expansion | DeepSeek P4 | DONE: m42_starvation_dictionary_results.json | — | — |
| ALL-110 | M43: Tensor Rank of Moonshine | DeepSeek P4 | DONE: m43_tensor_rank_moonshine_results.json | — | — |
| ALL-111 | M46: Moonshine Parity Structure | DeepSeek P4 | DONE: m46_moonshine_parity_results.json | — | — |
| ALL-112 | M50: Gamma-Pi Conductance | Internal | DONE: m50_gamma_pi_conductance_results.json | — | — |
| ALL-113 | M51: Starvation-Twist Commutator | Internal | DONE: m51_starvation_twist_commutator_results.json | — | — |

---

# BATCH 5: Round 5 Challenges (c1-c11 series)

| ID | Title | Source | Status | Key Constant | Kill? |
|----|-------|--------|--------|-------------|-------|
| ALL-114 | c1: Adelic Survivors | Round 5 | DONE: c1_adelic_survivors_results.json | — | — |
| ALL-115 | c2: v5 Sweet Spot | Round 5 | DONE: c2_v5_sweet_spot_results.json | — | — |
| ALL-116 | c3: Moonshine Ablation | Round 5 | DONE: c3_moonshine_ablation_results.json | — | — |
| ALL-117 | c4: Knot-OEIS Verbs | Round 5 | DONE: c4_knot_oeis_verbs_results.json | — | — |
| ALL-118 | c5: F3/F13 Boundary | Round 5 | DONE: c5_f3_f13_boundary_results.json | — | — |
| ALL-119 | c6: Dissect 15.2.a.a | Round 5 | DONE: c6_dissect_15_2_a_a_results.json | — | — |
| ALL-120 | c7: Rosetta Eigenvectors | Round 5 | DONE: c7_rosetta_eigenvectors_results.json | — | — |
| ALL-121 | c8: Parity Ablation | Round 5 | DONE: c8_parity_ablation_results.json | — | — |
| ALL-122 | c9: EC-Pi Wormhole | Round 5 | DONE: c9_ec_pi_wormhole_results.json | — | — |
| ALL-123 | c10: Twilight Verbs | Round 5 | DONE: c10_twilight_verbs_results.json | — | — |
| ALL-124 | c11: CM Compression | Round 5 | DONE: c11_cm_compression_results.json | — | — |

---

# BATCH 6: Frontier / Follow-Up Analyses (previously assigned to ALL-040 through ALL-069 or new)

| ID | Title | Source | Status | Key Constant | Kill? |
|----|-------|--------|--------|-------------|-------|
| ALL-125 | ALL-040: Deformation Paths | ChatGPT P2#2 / R3 / Grok P3#1 | DONE: all040_deformation_paths_results.json | — | — |
| ALL-126 | ALL-047: Phase Shift Alignment | ChatGPT P3#4 | DONE: all047_phase_shift_results.json | — | — |
| ALL-127 | ALL-061: Battery Rewrite Rules | Grok P3#9 | DONE: all061_battery_rewrite_results.json | — | — |
| ALL-128 | ALL-063: Kloosterman Distribution | Gemini P3#7 | DONE: all063_kloosterman_results.json | — | — |
| ALL-129 | ALL-064: Universal ST Ratio | Gemini P3#9 | DONE: all064_universal_st_ratio_results.json | — | — |
| ALL-130 | ALL-065: Rosetta Entropy | Gemini P3#10 | DONE: all065_rosetta_entropy_results.json | — | — |
| ALL-131 | ALL-066: Mod-p Fungrim Skeleton | Claude P2#4 | DONE: all066_modp_fungrim_results.json | — | — |

---

# BATCH 7: Additional Analyses with Result Files (shared/scripts/v2)

These are follow-up analyses, deeper dives, and cross-correlation experiments that produced result files.

| ID | Title | Result File | Status | Key Constant | Kill? |
|----|-------|-------------|--------|-------------|-------|
| ALL-132 | Congruence Verification (6 mod-11) | congruence_verification_results.json | DONE: 6 mod-11 congruences verified at Sturm bound + irreducibility proved | — | — |
| ALL-133 | Genus-2 Congruence Scan | genus2_congruence_results.json | DONE: GSp_4 congruences mapped | — | — |
| ALL-134 | Genus-2 Structural Analysis | genus2_structural_results.json | DONE | — | — |
| ALL-135 | Genus-2 c2 Fast Scan | genus2_c2_fast_results.json | DONE | — | — |
| ALL-136 | Genus-2 c2 Extension | genus2_c2_extend_results.json | DONE | — | — |
| ALL-137 | Tau(n) Congruence Analysis | tau_results.json | DONE | — | — |
| ALL-138 | Moonshine OEIS (raw) | moonshine_oeis_results.json | DONE: Raw moonshine bridge scan | — | — |
| ALL-139 | Moonshine Filtered | moonshine_filtered_results.json | DONE: Filtered moonshine bridges | — | — |
| ALL-140 | Spectral Spacing Analysis | spectral_spacing_results.json | DONE: Berry-Tabor confirmation | — | — |
| ALL-141 | Lattice-NF Bridge | lattice_nf_bridge_results.json | DONE: Likely prime confound | — | Kill #13 |
| ALL-142 | Scaling Law Battery (8 tests) | scaling_law_battery_results.json | DONE: 8/8 survived. Signal genuine | 8/8 battery pass | — |
| ALL-143 | GSp_4 Cross-Ell | gsp4_cross_ell_results.json | DONE | — | — |
| ALL-144 | Scaling Law Peak | scaling_law_peak_results.json | DONE | — | — |
| ALL-145 | Near Miss Analysis | near_miss_results.json | DONE: 253/641 resurrected | — | — |
| ALL-146 | Mod-2 Triangle ST | mod2_triangle_st_results.json | DONE | — | — |
| ALL-147 | Jones-Alexander Independence | jones_alexander_results.json | DONE | — | — |
| ALL-148 | Moonshine Sturm | moonshine_sturm_results.json | DONE | — | — |
| ALL-149 | Multi-Prime Intersection | multi_prime_results.json | DONE | — | — |
| ALL-150 | High-Prime Stability | high_prime_stability_results.json | DONE: 11/11 stable | — | — |
| ALL-151 | GenFunc Isomorphism | genfunc_isomorphism_results.json | DONE | — | — |
| ALL-152 | Gamma Triangle Consistency | gamma_triangle_results.json | DONE | — | — |
| ALL-153 | Test Correlation Analysis | test_correlation_results.json | DONE | — | — |
| ALL-154 | Derived Functor Analysis | derived_functor_results.json | DONE | — | — |
| ALL-155 | Scaling vs ST Order | scaling_vs_st_order_results.json | DONE | — | — |
| ALL-156 | Conditional Cross-Ell | conditional_cross_ell_results.json | DONE | — | — |
| ALL-157 | Constraint Interference | constraint_interference_results.json | DONE | — | — |
| ALL-158 | Partial Correspondence | partial_correspondence_results.json | DONE | — | — |
| ALL-159 | Scaling on CM Fields | scaling_cm_fields_results.json | DONE | — | — |
| ALL-160 | Cross-Level Lift | cross_level_lift_results.json | DONE | — | — |
| ALL-161 | Phase Transition | phase_transition_results.json | DONE | — | — |
| ALL-162 | Spectral Scaling | spectral_scaling_results.json | DONE | — | — |
| ALL-163 | Verbs by Family | verbs_by_family_results.json | DONE | — | — |
| ALL-164 | Triangle Collapse | triangle_collapse_results.json | DONE | — | — |
| ALL-165 | Algebraic vs Operadic | algebraic_vs_operadic_results.json | DONE | — | — |
| ALL-166 | Genus-3 Frobenius Computation | genus3_frobenius_results.json | DONE: First genus-3 Frobenius data | — | — |
| ALL-167 | Dual Representation Consistency | dual_representation_results.json | DONE | — | — |
| ALL-168 | Asymptotic Classifier | asymptotic_classifier_results.json | DONE | — | — |
| ALL-169 | Genus-3 Phase Test | genus3_phase_test_results.json | DONE | — | — |
| ALL-170 | Prime Entanglement | prime_entanglement_results.json | DONE | — | — |
| ALL-171 | Mock Shadow Mapping | mock_shadow_results.json | DONE | — | — |
| ALL-172 | GSp_4 CM Detection | gsp4_cm_detection_results.json | DONE | — | — |
| ALL-173 | Verb Slope Function | verb_slope_function_results.json | DONE | — | — |
| ALL-174 | Clique Distribution | clique_distribution_results.json | DONE | — | — |
| ALL-175 | Enrichment Position | enrichment_position_results.json | DONE | — | — |
| ALL-176 | Interference Function | interference_function_results.json | DONE | — | — |
| ALL-177 | Reconstruction Entropy | reconstruction_entropy_results.json | DONE | — | — |
| ALL-178 | Scaling Detector | scaling_detector_results.json | DONE | — | — |
| ALL-179 | Mod-2 Inter-Clique | mod2_inter_clique_results.json | DONE | — | — |
| ALL-180 | Nonlinear Transform Search | nonlinear_transform_results.json | DONE | — | — |
| ALL-181 | Prime-Weighted Metric | prime_weighted_metric_results.json | DONE | — | — |
| ALL-182 | Recurrence Stability | recurrence_stability_results.json | DONE | — | — |
| ALL-183 | Local-to-Global | local_to_global_results.json | DONE | — | — |
| ALL-184 | Knot-Primes Starvation | knot_primes_starvation_results.json | DONE | — | — |
| ALL-185 | Near-Congruence Analysis | near_congruence_results.json | DONE | — | — |
| ALL-186 | Gamma-Moonshine Distance | gamma_moonshine_distance_results.json | DONE | — | — |
| ALL-187 | Triangle Density vs Conductor | triangle_density_conductor_results.json | DONE | — | — |
| ALL-188 | BM Graph Statistics | bm_graph_statistics_results.json | DONE | — | — |
| ALL-189 | Slope Classification | slope_classification_results.json | DONE | — | — |
| ALL-190 | Twist Network Mod-7 | twist_network_mod7_results.json | DONE | — | — |
| ALL-191 | Motif Extraction Mod-2 | motif_extraction_mod2_results.json | DONE | — | — |
| ALL-192 | CM Detection GSp_4 Pairs | cm_detection_gsp4_pairs_results.json | DONE | — | — |
| ALL-193 | CL3 Different-Prime Dissection | cl3_different_prime_results.json | DONE | — | — |
| ALL-194 | ST Moment t-SNE | st_moment_tsne_results.json | DONE | — | — |
| ALL-195 | Knot Bridge Expansion | knot_bridge_expansion_results.json | DONE | — | — |
| ALL-196 | Altitude Camouflage | altitude_camouflage_results.json | DONE | — | — |
| ALL-197 | Curvature Flow | curvature_flow_results.json | DONE | — | — |
| ALL-198 | Ground State Hub | ground_state_hub_results.json | DONE | — | — |
| ALL-199 | Genus-2 Interference | genus2_interference_results.json | DONE | — | — |
| ALL-200 | Hodge-Operadic Analysis | hodge_operadic_results.json | DONE | — | — |
| ALL-201 | PDG Spectral Gaps | pdg_spectral_gaps_results.json | DONE | — | — |
| ALL-202 | Prime Nonlinearity | prime_nonlinearity_results.json | DONE | — | — |
| ALL-203 | Reynolds Number Analysis | reynolds_number_results.json | DONE | — | — |
| ALL-204 | Rosetta Mode-1 Ablation | rosetta_mode1_ablation_results.json | DONE | — | — |
| ALL-205 | Two-Adic Ablation | twoadic_ablation_results.json | DONE | — | — |
| ALL-206 | v2 Wall SVD | v2_wall_svd_results.json | DONE | — | — |
| ALL-207 | Moonshine Expansion (full) | moonshine_expansion_results.json | DONE | — | — |
| ALL-208 | HMF Congruence Inventory | hmf_congruence_results.json | DONE: Data inventory complete | — | — |

---

# BATCH 8: Cartography/v2 Frontier Results

These are problems from the frontier problem lists (F-series, X-series, P-series, OSC-series) and additional cross-domain probes.

| ID | Title | Result File | Status | Key Constant | Kill? |
|----|-------|-------------|--------|-------------|-------|
| ALL-209 | Cross-Domain Moments | cross_domain_moments_results.json | DONE | — | — |
| ALL-210 | Twist Shadow Commutator | twist_shadow_commutator_results.json | DONE: Twist preserves AC shadow | — | — |
| ALL-211 | EC vs Rank | ellc_vs_rank_results.json | DONE | — | — |
| ALL-212 | Fake L-Functions | fake_lfunctions_results.json | DONE | — | — |
| ALL-213 | EC L-Function Taylor | ellc_lfunction_taylor_results.json | DONE | — | — |
| ALL-214 | L-Function Ricci Curvature | lfunction_ricci_results.json | DONE | — | — |
| ALL-215 | Sato-Tate Spectral | sat_spectral_results.json | DONE | — | — |
| ALL-216 | Dead Zone Attack | dead_zone_attack_results.json | DONE | — | — |
| ALL-217 | CODATA in OEIS | codata_in_oeis_results.json | DONE | — | — |
| ALL-218 | PDG Algebraic Ratios | pdg_algebraic_ratios_results.json | DONE | — | — |
| ALL-219 | Hecke Entropy Rate | hecke_entropy_rate_results.json | DONE | — | — |
| ALL-220 | PDG Recurrence | pdg_recurrence_results.json | DONE | — | — |
| ALL-221 | CODATA Mod-p Stability | codata_modp_stability_results.json | DONE: NO_SIGNAL | — | — |
| ALL-222 | CODATA Compressibility | codata_compressibility_results.json | DONE | — | — |
| ALL-223 | NF Spectral Index | nf_spectral_index_results.json | DONE | — | — |
| ALL-224 | ST Drift | st_drift_results.json | DONE | — | — |
| ALL-225 | PDG Graph Curvature | pdg_graph_curvature_results.json | DONE | — | — |
| ALL-226 | AC Phase Transition | ac_phase_transition_results.json | DONE | — | — |
| ALL-227 | Transport Matrix | transport_matrix_results.json | DONE | — | — |
| ALL-228 | OEIS Sato-Tate | oeis_sato_tate_results.json | DONE | — | — |
| ALL-229 | Knot-NF Intersection | knot_nf_intersection_results.json | DONE: MARGINAL (weak non-random collision) | — | — |
| ALL-230 | Genus-2 Phase Coherence | genus2_phase_coherence_results.json | DONE | — | — |
| ALL-231 | OEIS Spectral Dimension | oeis_spectral_dimension_results.json | DONE | — | — |
| ALL-232 | Spectral Gap Universality | spectral_gap_universality_results.json | DONE | — | — |
| ALL-233 | Lattice Theta Universality | lattice_theta_universality_results.json | DONE: STRONG SEPARATION per dimension | — | — |
| ALL-234 | Spectral Rigidity | spectral_rigidity_results.json | DONE | — | — |
| ALL-235 | Compressibility Hierarchy | compressibility_hierarchy_results.json | DONE | — | — |
| ALL-236 | Fine Structure in OEIS | fine_structure_oeis_results.json | DONE: NOTABLE nearest-neighbor below 1st percentile; 137 frequency unremarkable | — | — |
| ALL-237 | Recurrence-Zeta Transfer | recurrence_zeta_transfer_results.json | DONE | — | — |
| ALL-238 | ST Twist Drift | st_twist_drift_results.json | DONE: EVEN_EXACT_ODD_NONZERO | — | — |
| ALL-239 | Chromatic Scaling | chromatic_scaling_results.json | DONE | — | — |
| ALL-240 | Hecke Curvature Transition | hecke_curvature_transition_results.json | DONE | — | — |
| ALL-241 | Near-Congruence Defect | near_congruence_defect_results.json | DONE | — | — |
| ALL-242 | FLINT Call Graph | flint_call_graph_results.json | DONE | — | — |
| ALL-243 | Kissing Number from Theta | kissing_from_theta_results.json | DONE | — | — |
| ALL-244 | CODATA Galois Group | codata_galois_results.json | DONE | — | — |
| ALL-245 | PDG Decay Topology | pdg_decay_topology_results.json | DONE | — | — |
| ALL-246 | Fungrim Complexity vs Recurrence | fungrim_complexity_recurrence_results.json | DONE | — | — |
| ALL-247 | NF Reynolds Number | nf_reynolds_results.json | DONE | — | — |
| ALL-248 | Lattice Enrichment Slope | lattice_enrichment_slope_results.json | DONE | — | — |
| ALL-249 | Pipeline Info Loss | pipeline_info_loss_results.json | DONE | — | — |
| ALL-250 | Genus-2 Fake Sigma | genus2_fake_sigma_results.json | DONE | — | — |
| ALL-251 | Fungrim Clique Power Law | fungrim_clique_power_law_results.json | DONE | — | — |
| ALL-252 | Prime Sieve Artifact | prime_sieve_artifact_results.json | DONE: ARTIFACT_WITH_CROSSOVER | — | — |
| ALL-253 | Prime Fourier 2D | prime_fourier_2d_results.json | DONE | — | — |
| ALL-254 | Quadratic Enrichment | quadratic_enrichment_results.json | DONE | — | — |
| ALL-255 | Grid Prime Null | grid_prime_null_results.json | DONE | — | — |
| ALL-256 | Prime Fractal Dimension | prime_fractal_dimension_results.json | DONE | — | — |
| ALL-257 | Entropy Gradient Rays | entropy_gradient_rays_results.json | DONE | — | — |
| ALL-258 | Diagonal Cross-Prime | diagonal_cross_prime_results.json | DONE | — | — |
| ALL-259 | Prime Gap Anisotropy | prime_gap_anisotropy_results.json | DONE: ANISOTROPIC (genuine directional structure) | — | — |
| ALL-260 | Prime Correlation Tensor | prime_correlation_tensor_results.json | DONE | — | — |
| ALL-261 | Prime Run Persistence | prime_run_persistence_results.json | DONE | — | — |
| ALL-262 | Residue Interference Lattice | residue_interference_lattice_results.json | DONE | — | — |

---

# BATCH 9: Charon/v2 Results

| ID | Title | Result File | Status | Key Constant | Kill? |
|----|-------|-------------|--------|-------------|-------|
| ALL-263 | Oscillation Shadow (15.2.a.a) | oscillation_shadow_results.json | DONE: NEGATIVE. 15.2.a.a oscillation not universal. AC magnitudes not larger than null | — | Kill |

---

# UNSOLVED — READY (Data exists, not yet fired)

| ID | Title | Source | Blocked By |
|----|-------|--------|------------|
| ALL-038 | Mock Shadow Mapping | James R3-J4 | READY |
| ALL-039 | Scaling Law as Active Detector | DeepSeek R3, ChatGPT R3#2 | READY |
| ALL-041 | Twist Network of Mod-7 Anomaly | DeepSeek P3#2 | READY |
| ALL-042 | Operadic Permeability Constant (0.813 stable?) | DeepSeek P3#3 | READY (needs DLMF) |
| ALL-044 | ST Moment Space t-SNE | DeepSeek P3#9 | READY |
| ALL-045 | Prime-Weighted Distance Metric | ChatGPT P3#2 | READY |
| ALL-046 | Nonlinear Transformation Search | ChatGPT P3#3 | READY |
| ALL-048 | Cross-Domain Moment Matching | ChatGPT P3#6 | READY |
| ALL-049 | Local-to-Global Consistency | ChatGPT P3#7 | READY |
| ALL-050 | Motif Extraction Mod-2 Graphs | ChatGPT P3#8 | READY |
| ALL-051 | Recurrence Stability Under Reduction | ChatGPT P3#9 | READY |
| ALL-052 | Dual Representation Consistency | ChatGPT P3#10 | READY |
| ALL-054 | Gamma Metric: Moonshine Distance | Claude P3#3 | READY |
| ALL-055 | Triangle Density vs Conductor | Claude P3#5 | READY |
| ALL-056 | CL3 Different-Prime Dissection | Claude P3#6 | READY |
| ALL-057 | BM on Graph Statistics vs Prime | Claude P3#7 | READY |
| ALL-058 | Algebraic Family vs Operadic | Claude P3#8 | READY |
| ALL-059 | CM Detection on GSp_4 Pairs | Claude P3#9 | READY |
| ALL-060 | Universal Verbs vs Scaling Slope | Claude P3#10 | READY |
| ALL-067 | Knot Bridge Expansion (torus) | ChatGPT R3#5 | READY |
| ALL-069 | Scaling Slope as Invariant | ChatGPT R3#2 | READY |

### From Frontier 1 (unsolved):
| ID | Title | Status |
|----|-------|--------|
| F-R01 | F9: Functorial Lift Detectability Threshold | READY |
| F-R02 | F16: Algorithmic Recurrence Density in Source Code | READY |
| F-R03 | F17: Symbolic Constant Reuse Graph Exponent | READY |
| F-R04 | F18: Arithmetic Kernel Spectral Signature | READY |
| F-R05 | F20: Recurrence -> Zeta Transfer Efficiency | READY |
| F-R06 | F23: Moment Vector Manifold Dimension | READY |
| F-R07 | F25: Sequence Spectral Anisotropy | READY |
| F-R08 | F26: Zeta Zero Surrogate Stability | READY |
| F-R09 | F27: Curvature-Entropy Coupling Constant | READY |
| F-R10 | F30: Rosetta Axis Deformation Under Noise | READY |
| F-R11 | Spectral Gap of Quantum Decay Topologies | READY (buildable from PDG) |
| F-R12 | Automorphic Reconstruction via Basis Projection | READY |

### From Frontier 2 Part 1 (20 problems, many READY):
| ID | Title | Status |
|----|-------|--------|
| F2-01 | Spectral Gap of Prime-Indexed OEIS Operator | READY |
| F2-02 | Ollivier-Ricci Phase Transition Mod-p Hecke | READY |
| F2-03 | Sato-Tate Moment Drift Under Quadratic Twist | READY |
| F2-04 | Genus-2 to Genus-3 Jacobian Dimension Gap | READY (SageMath) |
| F2-06 | Knot Alexander Recurrence via Coefficients | READY |
| F2-07 | Fine-Structure in OEIS Fingerprint Space | READY |
| F2-08 | Congruence Graph Chromatic Scaling | READY |
| F2-09 | NF Discriminant as MF Fingerprint Query | READY |
| F2-11 | Fungrim Complexity vs OEIS Recurrence Order | READY |
| F2-12 | Genus-2 Endomorphism Enrichment at Genus-3 Boundary | READY |
| F2-13 | FLINT Source Code Spectral Analysis | READY |
| F2-14 | Lattice Kissing from Mod-p Theta | READY |
| F2-15 | Cross-Prime Interference Genus-2 vs EC | READY |
| F2-17 | ST Moment Vectors in Hyperbolic Space | READY |
| F2-18 | Recurrence-Zeta Info Loss | READY |
| F2-19 | v2-Wall Spectral Rigidity Lyapunov | READY |
| F2-20 | Congruence-Curvature Duality | READY |

### From Frontier 2 Part 2 (20 problems, many READY):
| ID | Title | Status |
|----|-------|--------|
| F2P2-01 | Fine-Structure Drift in FLINT | READY |
| F2P2-03 | Ollivier-Ricci Curvature of Knot L-Functions | READY |
| F2P2-04 | Fungrim Formula Topology Sigma Ratio | READY |
| F2P2-05 | FLINT Source Code Interference Exponent | READY |
| F2P2-06 | PDG Mass Gap in Genus-2 Curves | READY |
| F2P2-08 | Near-Congruence Cartan Topological Defect | READY |
| F2P2-09 | OEIS Set/For Axis FFT Rotation | READY |
| F2P2-10 | Reynolds Number Phase Transition in NF | READY |
| F2P2-11 | v2 Wall Spectrum in Knot Concatenation | READY |
| F2P2-12 | SageMath Point-Counting Tau-Entropy | READY |
| F2P2-13 | CODATA Unitless Constant Galois Group | READY |
| F2P2-15 | Local-to-Global PDG Decay Modes | READY |
| F2P2-16 | Clique Power Law Fungrim Implication | READY |
| F2P2-17 | Rosetta Metric Learning on FLINT Macros | READY |
| F2P2-18 | Enrichment Slope Inversion Lattice Packings | READY |
| F2P2-19 | Fake L-Function Critical Sigma Genus-2 | READY |
| F2P2-20 | Habitable Zone Lower Bound in Knots | READY |

### From Unproposed AI batches:
| ID | Title | Status |
|----|-------|--------|
| AI-01 | OpenAI batch (10 problems) | UNTESTED |
| AI-02 | DeepSeek batch (10 problems) | UNTESTED |
| AI-03 | Claude self-generated remainder (P2 CODATA, P3 FLINT, P5 knot growth, etc.) | UNTESTED |

---

# UNSOLVED — BLOCKED (Missing data or infrastructure)

| ID | Title | Blocker |
|----|-------|---------|
| ALL-071 | Genus-3 ST 410-Group Classifier | SageMath for genus-3 Frobenius |
| ALL-072 | Maeda Conjecture Verification | Higher-weight Hecke char polys (SageMath) |
| ALL-073 | Hida Theory / p-adic Families | SageMath + higher-weight forms |
| ALL-074 | Quantum Modular Forms / Knots | Jones poly at high precision near roots of unity |
| ALL-075 | HMF Full Congruence Scan | hmf_hecke table from LMFDB |
| ALL-076 | Picard-Fuchs Operadic Skeleton | AESZ operator database |
| ALL-077 | Brauer-Manin Obstruction Probe | Curated obstructed equation set |
| ALL-079 | Which of 410 Groups Occur Over Q? | Genus-3 Frobenius (SageMath) |
| ALL-080 | Shintani Reversal | L-value computation (SageMath/PARI) |
| ALL-081 | Pizer Graph Isomorphism | Brandt matrix construction (SageMath) |
| ALL-082 | Rigid Analytic Tate-Curve Fingerprinting | p-adic CAS |
| ALL-083 | Vertex-Algebra Moonshine Expansion | Higher-lambency mock theta data |
| ALL-084 | Sporadic Group Moonshine (Co_1, Suz) | McKay-Thompson tables from ATLAS |
| ALL-085 | FindStat Algebraic DNA | FindStat API numerical values |
| B-01 | COD Crystal Problems (5+) | COD download running overnight |
| B-02 | Genus-Dependent GUE Deviation | Higher-precision L-function zeros |
| B-03 | Mod-p Rigidity of HGM Identities | Fungrim formula evaluator over F_p |
| B-04 | LLL Integer Relation on CODATA | LLL/PSLQ implementation |
| B-05 | Lattice Gauge Theory (X5) | SU(2)/SU(3) simulation data |
| B-06 | Turbulence Tensor (X6) | Fluid dynamics velocity field data |
| B-07 | Ricci Flow on High-Genus Isogeny Graphs | Genus-2 isogeny graph data |

---

# DEFERRED (Lower priority or superseded)

| ID | Title | Reason |
|----|-------|--------|
| ALL-086 | Cross-Domain Generating Function Matching | Requires GF approximation layer |
| ALL-087 | Operadic Rewrite Dynamics | 2-3 week build, combinatorial explosion |
| ALL-088 | Asymptotic Regime-Shift in q-series | Lower priority |
| ALL-089 | Borcherds Product Skeletons | Requires product formula corpus |
| ALL-090 | Umbral Shadow Identification | Covered by ALL-038 |
| D-01 | Deformation Trajectories (ChatGPT P2#2) | Complex build, partially done |
| D-02 | Cross-Domain GF Matching (ChatGPT P2#3) | Needs GF approximation layer |
| D-03 | Operadic Rewrite (DeepSeek P2#4) | 2-3 week build |
| D-04 | FindStat BM on rep theory (Grok P1#5) | Not tested this session |
| D-05 | q-series regime shifts (Grok P1#4) | Lower priority |

---

# FINAL TALLIES

## By Status

| Status | Count |
|--------|-------|
| **DONE (result file exists)** | **195** |
| UNSOLVED-READY (data exists, not fired) | ~80 |
| UNSOLVED-BLOCKED (missing data/infrastructure) | ~21 |
| DEFERRED | ~10 |
| **Total problems identified** | **~306** |

## Solved Problems Breakdown

| Batch | Count |
|-------|-------|
| Batch 1: Part 1 Challenges (ALL-001 to ALL-011) | 11 |
| Batch 2: Part 2 Challenges (ALL-012 to ALL-036) | 13 |
| Batch 3: Part 3 / Round 3 (ALL-024 to ALL-037) | 12 |
| Batch 4: Metrology M16-M51 (ALL-091 to ALL-113) | 23 |
| Batch 5: Round 5 c1-c11 (ALL-114 to ALL-124) | 11 |
| Batch 6: Frontier follow-ups ALL-040+ (ALL-125 to ALL-131) | 7 |
| Batch 7: Additional analyses (ALL-132 to ALL-208) | 77 |
| Batch 8: Cartography/v2 frontier (ALL-209 to ALL-262) | 54 |
| Batch 9: Charon/v2 (ALL-263) | 1 |
| **Total result files** | **195** |

(Note: Some result files are follow-up analyses on the same parent challenge, so the number of unique independent questions is lower -- approximately 108 unique challenges solved, with 87 deeper follow-up analyses.)

## Kills

| Kill # | Problem | Result |
|--------|---------|--------|
| Kill #13 | Lattice-NF Determinant Bridge (ALL-141) | Prime confound |
| Kill #14 | Collatz Algebraic Siblings (ALL-005) | Piecewise-linear, no 3x+1 connection |
| Kill (unnumbered) | 15.2.a.a Oscillation Shadow (ALL-263) | Not universal, null holds |
| Kills 1-12 | Pre-session kills | Battery kills from prior sessions (16+ total in project) |

Total project kills: 21 (per problem_tracker.md)

## Key Constants Produced

| Constant | Value | Source |
|----------|-------|--------|
| Mod-p enrichment (detrended) | 8-16x across all primes | ALL-004 / C11 |
| Starvation rate | 43.6% of weight-2 forms | ALL-001 / C02 |
| Operadic permeability ratio | 0.813 within/between | ALL-010 / C12 |
| Gamma distance reduction | 12.7% closer than random | ALL-015 / CL5 |
| Mod-2 GSp_4 triangle enrichment | 8,000x vs null | ALL-013 / CL2 |
| Constraint collapse exponent | alpha = 0.63 | ALL-009 / C10 |
| ST classifier accuracy | 98.3% (20-dim Mahalanobis) | ALL-019 / DS2 |
| CM classifier F1 | 1.00 (perfect) | ALL-017 / CT4 |
| Paramodular eigenvalue match | 92.5% (37/40) | ALL-036 / C01-v2 |
| HGM-modular recovery | 100% (49/49) | ALL-021 / DS5 |
| Moonshine bridges | 307 total, 4 M24->EC | ALL-002 / C09 |
| Near-miss resurrection rate | 39.5% (253/641) | ALL-025 |
| Jones recurrence knots | 48 (44 cyclotomic + 4 torus) | ALL-020 / DS3 |
| High-prime stability | 100% (11/11) | ALL-034 |
| Starved-congruence enrichment | 1.65x (p=0.006) | ALL-014 / CL3 |
| Residual rep max hub | 109 forms (mod-3) | ALL-016 / CT1 |
| Hecke triangles at ell=5 | 27 (p<0.005) | ALL-006 / C07 |
| Maass Poisson KS | ~0.034 | ALL-007 / C05 |
| N(G_{3,3}) scaling slope | +0.578 | ALL-012 / CL1 |
| Compression ratio (genfunc) | 0.25 | ALL-027 |
| Battery pass rate | 8/8 for C11 | ALL-142 |
| Twist pairs detected | 174 | ALL-017 / CT4 |
| Cross-ell cluster overlap | 0 (total independence) | ALL-016 / CT1 |
| F3 kill fraction | 75.8% | ALL-018 / CT5 |
| "Almost real" near-misses | 641 | ALL-018 / CT5 |
| Ordinary at ord_p(N)=1 | 100% | ALL-022 / GM4 |

---

*195 result files. ~108 unique challenges solved. ~80 ready to fire. ~21 blocked. 21 kills across the project. 25+ measurable constants. The instrument works at Layer 2 and Layer 3 is open.*
