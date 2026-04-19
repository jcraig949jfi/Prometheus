"""
Landscape Tensor Builder — Harmonia's serialized state

Compresses the session's acquired understanding into a structure a cold-start
Harmonia can restore from efficiently. The core insight: tensor structure
carries invariance information that prose would flatten.

Output artifacts:
  - landscape_tensor.npz    : (feature × projection) tensor of resolution status
  - landscape_manifest.json : typed metadata for every feature and projection
  - feature_graph.json      : directed edges between features (supersedes / supports / contradicts)
  - projection_graph.json   : edges between projections (refines / tautology_of / dual_to)
  - pattern_library.md      : hard-to-verbalize recognition patterns

Schema for the main tensor:
  T[i, j] ∈ {-2, -1, 0, +1, +2}
    -2: this projection provably collapses the feature (known artifact)
    -1: projection tested, feature not resolved (collapses or unclear)
     0: projection not tested against this feature (unknown)
    +1: projection resolves the feature (visible through it)
    +2: projection strongly resolves AND validates under permutation-break null

Adjacent rows (similar invariance profile) = structurally similar features.
Adjacent columns (resolve similar features) = redundant coordinate systems.
Dense +1/+2 rows = landscape structure (real terrain).
Sparse rows = artifact or weak signal worth walking.

Author: Harmonia, session of 2026-04-17
"""
import json
import numpy as np
import os
import sys, io
from pathlib import Path

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# FEATURES (rows of the tensor)
# ============================================================================

# Each feature = specimen we've measured or anomaly we've encountered.
# Order matters — grouped by topological kinship where possible.
FEATURES = [
    # ----- CALIBRATION ANCHORS (known landscape; must always resolve) -----
    {"id": "F001", "label": "Modularity (a_p agreement)",
     "tier": "calibration", "n_objects": 971 * 450,
     "description": "EC ↔ MF a_p coefficients agree at 100.000%. Known theorem (Wiles et al.)."},
    {"id": "F002", "label": "Mazur torsion",
     "tier": "calibration", "n_objects": 3824372,
     "description": "EC torsion subgroup structure ∈ Mazur's 15. 100.000% of 3.8M."},
    {"id": "F003", "label": "BSD parity (rank = analytic_rank) + FULL BSD identity at 10⁻¹² (rank 2-3)",
     "tier": "calibration", "n_objects": 2481157,
     "description": "rank = ov for all of bsd_joined. 100.000%. 2026-04-18 UPGRADE via Charon eb6d31df: full BSD identity (leading_term = Omega · Reg · prod(c_p) · |Sha| / |Tor|²) verified at 10⁻¹² precision across 218/218 conditional rank 2-3 curves via devmirror.lmfdb.xyz (ec_mwbsd unblocked). Zero failures. Instrument-health check: any row failing at 10⁻¹² is a bug."},
    {"id": "F004", "label": "Hasse bound on a_p",
     "tier": "calibration", "n_objects": 150000,
     "description": "|a_p| ≤ 2√p. 100% of 150K coefficients."},
    {"id": "F005", "label": "High-Sha parity (H43)",
     "tier": "calibration", "n_objects": 67035,
     "description": "Among sha≥9: (-1)^rank = root_number perfect."},
    {"id": "F008", "label": "Scholz reflection |r3(K*) - r3(K)| ≤ 1 for quadratic fields",
     "tier": "calibration", "n_objects": 344130,
     "description": "Zero violations of Scholz 1932 reflection across 344,130 imaginary-real quadratic pairs (Ergon scholz_reflection.py in 2572d7dd; sessionD independent verification in 12e93a0f). 71.5% equality (r3 matches), 28.5% differ by 1 — never >1. Explains the p=3 BST convergence anomaly (alpha_3 ≈ 0.16 vs alpha_{p>=5} ≈ 0.23-0.28) observed in Cohen-Lenstra Reports 18b/c. Theorem lineage: Scholz reflection (1932) + Davenport-Heilbronn (1971). Load-bearing calibration anchor for NF class-group work. Any tool that predicts |r3(K*) - r3(K)| > 1 has a bug."},
    {"id": "F009", "label": "Torsion primes ⊆ nonmax primes (Serre open-image lineage)",
     "tier": "calibration", "n_objects": 1385133,
     "description": "For every non-CM EC over Q: primes(rational torsion) ⊆ nonmax_primes (mod-ℓ image is non-maximal at every torsion prime). 100.000% across 1,385,133 non-CM EC rows with torsion>1; zero violations (sessionD audit_nonmax_vs_torsion, 2026-04-17). All 15 Mazur torsion cells pass at 100%. Theorem lineage: Serre open-image + Mazur torsion classification. Load-bearing calibration anchor; joins F001-F005."},

    # ----- LIVE SPECIMENS (weak-but-survives) -----
    {"id": "F010", "label": "NF backbone via Galois-label — KILLED, joins F022 under block-shuffle null",
     "tier": "killed", "n_objects": 75,
     "description": "KILLED under block-shuffle-within-degree null (sessionC wsw_F010_alternative_null 2026-04-17). The 0.27 decontaminated ρ was degree-mediated between-strata leakage — block null z=-0.86 (observed ρ=0.173 BELOW null mean 0.205 at n=51). Progression: pooled ρ=0.40 (n=71) → bigsample pooled 0.109 (n=75) → decon ρ=0.27 via P052 (z=2.38 weak-null) → block-null z=-0.86 (dead). The plain label-permute null over-rejected because it didn't preserve per-degree structure; block-shuffle preserves per-degree marginal AND destroys within-degree structure, revealing no within-degree coupling. F010 joins F022 as same-data-no-durable-signal. Triple-layer artifact: Pattern 20 (pooled) + Pattern 19 (stale original) + F022 twin (NF-Artin coupling is degree-marginal only)."},
    {"id": "F011", "label": "GUE first-gap deficit — EXCISED (calibration) + RANK-0 RESIDUAL (frontier)",
     "tier": "live_specimen", "n_objects": 2009089,
     "description": "REOPENED to live_specimen 2026-04-18. Pooled ~38% deficit decomposes into two layers. "
                    "LAYER 1 (calibration): bulk deficit IS Duenez-HKMS (2011) excised ensemble. sessionB Aporia Report 1: "
                    "deficit shrinks monotonically with conductor (slope -7.17/log-decade z=-54.2; 45.37% -> 35.34%); "
                    "gap1 38.17% vs gap2 29.07% (z=96.97). The instrument correctly detected known central-zero-forcing. "
                    "LAYER 2 (frontier): RANK-0 ~31% RESIDUAL IS GENUINE. sessionB fitted three decay ansatze: power-law "
                    "eps_0=31.08±6.19 (chi²=19.6); 1/log(N) eps_0=22.90±0.78 (z=29sigma from 0); 1/log(N)² eps_0=35.83±0.36. "
                    "Robust 23-36% across ansatze. Self-audit P104 block-shuffle (Pattern 24) — CITATION CORRECTED "
                    "2026-04-18 per sessionB recursion-3 audit (71ff1d47): the prior z_block=10.46 used class_size "
                    "as stratifier but class_size is DEGENERATE (null_std=0, dominant value covers 59%). Honest "
                    "z_block = 4.19 under torsion_bin (Mazur 15 balanced). Still DURABLE but meaningfully lower "
                    "than the degenerate-null overclaim. cm_binary gives z=0.63 noisy (only 0.9% CM). "
                    "Joint alpha-free decay fit is UNDER-CONSTRAINED (alpha=0.49±0.52, eps_0=-4.07±56.08): data "
                    "cannot distinguish classical 1/log from power-law; eps_0 point estimate depends on fixed form. "
                    "Ergon DHKMS closed-form test (2572d7dd): ruled out as finite-N correction — DHKMS predicts the WRONG "
                    "DIRECTION; 25% mean unfolding bias would be needed, implausible. Ergon zero-projections (37158e4f): "
                    "deficit varies with arithmetic complexity (isogeny class 1->8 var/Gaudin 1.37->0.97; sha 1->36 1.30->1.00) "
                    "— NOT uniform, rules out generic unfolding error. P028 Katz-Sarnak z=7.63 spread (block z=111.78) is "
                    "downstream of LAYER 1 central-zero-forcing, still durable. T4 sub-family (cbe7b623): rank-0 low-tail "
                    "Pr[L/M_1<0.25] enriched for CM (1.73x, cm=-27: 6.66x), class_size=3 (1.78x); sha>1 depleted — residual "
                    "concentrated in arithmetically structured sub-populations. Frontier probes queued: DHKMS closed-form "
                    "magnitude match; independent-unfolding via non-LMFDB zeros; cross-family vs Dirichlet L-functions; "
                    "Miller 2009 NLO prediction (P106 draft)."},
    {"id": "F012", "label": "Möbius bias at g2c aut groups (H85) — KILLED",
     "tier": "killed", "n_objects": 66158,
     "description": "KILLED across Möbius AND Liouville definitions (sessionB wsw_F012 + liouville_side_check_F012, 2026-04-17). Clean measurement on full n=66158 g2c: max|z| over adequate strata = 0.39 (μ) / 0.52 (λ), permutation p = 0.68 (μ) / 0.60 (λ). The prior |z|=6.15 DID NOT REPRODUCE under either Möbius or Liouville. Definitional drift hypothesis excluded. Canonical Pattern 19 case: stale or never-reproducible tensor entry. Likely causes: different subset, different scorer, or original measurement was noise. 63% non-squarefree g2c discriminants reduce effective S/N but don't account for the 16x discrepancy."},
    {"id": "F013", "label": "Zero spacing rigidity vs rank (H06) — P028 resolves BUT downstream of F011 excised ensemble",
     "tier": "live_specimen", "n_objects": 2009088,
     "description": "Original pooled slope=-0.0019 was a Pattern-20 MIXTURE ARTIFACT (sessionB tick 18 wsw_F013_P028, n=2M). Stratified by Katz-Sarnak: SO_even slope=+0.01284 (variance INCREASES with rank); SO_odd slope=-0.00216. Slope diff z=13.68, p=1.3e-42. BLOCK-SHUFFLE VERIFIED at z_block=15.31 (sessionB audit tick 20). "
                    "**RETROSPECTIVE CAVEAT 2026-04-18**: Per Aporia Report 1 finding that F011 is the Duenez-HKMS excised ensemble, F013's P028 split is a DOWNSTREAM consequence of the same central-zero-forcing at finite conductor. The signal is real and durable but calibration-level, not independent novelty. Pattern 5 gate closed retrospectively on both F011 and F013 P028 findings. Tier retained as live_specimen because the rank-slope sign flip is structurally informative beyond F011's first-gap story, but interest downgraded. Specimens 21, 40, 44 (prior registrations) revised to lower interest."},
    {"id": "F014", "label": "Lehmer spectrum (refined) — Salem density in (1.176, 1.228)",
     "tier": "live_specimen", "n_objects": 22178569,
     "description": "Lehmer bound TOUCHED at degrees 10 and 20 (Lehmer polynomial and splitting field). "
                    "Original '4.4% gap between bound and next Mahler measure (1.228 at deg 12)' FALSIFIED "
                    "by sessionB wsw_F014 (81K polynomials, Pattern-4-biased ORDER BY disc_abs ASC per degree). "
                    "Observed gap = 3.41%; 3 polynomials strictly in (1.17628, 1.228), minimum a Salem "
                    "polynomial at 1.216392 (deg 10, num_ram=1, disc_abs=1.49e9). The region above Lehmer's "
                    "polynomial is a Salem-number density, not a clean gap. Strong per-num_ram monotone: "
                    "bound touched only at num_ram=1,2; minimum jumps to 1.267 at num_ram=3, 1.800 at num_ram=5. "
                    "Bad-prime count shows real shape (echoes F011 P021 monotone, sessionC). "
                    "Source: cartography/docs/wsw_F014_results.json. Anti-pattern note: Mahler-measure gap "
                    "claims without degree-AND-num_ram stratification are suspect. "
                    "2026-04-18 STRUCTURAL UPGRADE (Charon eb6d31df): the gap (1.176, 1.241) is not just a density "
                    "question — it is STRUCTURAL. The trinomial M(x^n - x - 1) Mahler-measure sequence sets a lower "
                    "floor for degrees >= 22, converging to 1.381 as n→∞. The gap WIDENS with degree rather than "
                    "shrinking. The 3.41% 'gap' observed at our sample is a finite-degree artifact of the full "
                    "asymptotic structure. F014 stays live_specimen; the frontier shifts from 'how small can "
                    "minimum Mahler get' to 'what is the exact asymptotic form of the floor above Lehmer'."},
    {"id": "F041a", "label": "Rank-2+ moment slope monotone in num_bad_primes (supersedes F041)",
     "tier": "live_specimen", "n_objects": 222288,
     "description": "PROMOTED 2026-04-18 after 5 independent kill-test survivals. Original F041 (session's Keating-Snaith rank-dependent convergence) demoted to first-moment drift; the REAL signal is the rank-2+ interaction. "
                    "At rank=2 (n=222,288): slope of M_1(log X) is strictly monotone in num_bad_primes: nbp=1:1.21, nbp=2:1.52, nbp=3:1.70, nbp=4:1.86, nbp=5:1.95, nbp=6:2.52. At rank 0 and 1: slope flat in nbp. The interaction is rank-specific. "
                    "Kill tests survived: "
                    "(W2 2a3f6c37) cross-nbp block-shuffle-within-(rank,decade): amp 27.6x, corr(nbp,slope)=0.97, null slopes collapse to ~1.9 with spread 0.046 vs observed 1.32 (27.6x). "
                    "(U_A 4a046a81) conductor-control joint OLS: b_nbp z=3.37 (>=3 threshold); narrow 0.1-decade sub-bins give corr 0.965 slopes 2.02-4.19. Within-decade conductor drift is real but does NOT explain the ladder. "
                    "(W3 e3f67b94) P039 Galois-image alternative: P021 range 1.316 vs best P039 marginal 0.305 — nbp is NOT a Galois-image proxy. "
                    "(T3 68225787) P026 semistable-vs-additive split: ladder lives in SEMISTABLE half (slope_range_semi=0.570 vs slope_range_add=0.279; ratio 0.489 well under 0.8). Counterintuitive — points toward conductor-only / multiplicative-ramification effect, not Kodaira. "
                    "(T5 d9c646d9) Specific-prime joint: no single Mazur-Kenku prime dominates (max |slope_diff|=0.56 for has_2, below 1.0 ladder threshold). Effect is carried by COUNT of bad primes plus modest {2,3} lift. "
                    "Pattern 5 gate (CFKRS rank-2 SO(even) closed-form) is the remaining open hurdle; if CFKRS predicts monotone-in-nbp at rank 2: demote to calibration. If not: fully frontier."},
    {"id": "F042", "label": "CM disc=-27 L-value depression — novel quantitative precision on KNOWN qualitative effect",
     "tier": "calibration_refinement", "n_objects": 14,
     "description": "DOWNGRADED 2026-04-18 (from live_specimen) per sessionC literature scan (c9a7543a). The 6.66x enrichment is the Deuring non-maximal-order character-sum compression described qualitatively in Gross LNM 776 (1980) and Rodriguez-Villegas & Zagier (1993). Our contribution is NOT a frontier finding — it is quantitative precision (6.66x enrichment factor, 2.5x leading_term depression between cm=-3 and cm=-27, 71.4% low-L tail participation) on a well-established qualitative structure. Useful as a Pattern 5 calibration instance and for non-maximal-order test sets; not a promotion candidate. Discovered U_C 322ff272, n=14 at rank-0 decade [1e5,1e6). Frontier reopens only if a broader test across Q(sqrt(-d)) non-maximal orders at other d values shows precision deviating from the Gross/RVZ qualitative predictions by more than factor 2."},
    {"id": "F043", "label": "BSD-Sha anticorrelation with period (new empirical law candidate)",
     "tier": "live_specimen", "n_objects": 60003,
     "description": "U_D 2026-04-18 (111d6288): corr(log Sha, log A) = -0.520 at rank 0 decade [1e5,1e6), where A := Omega_real * prod_p c_p. Large-Sha curves have systematically small period*Tamagawa product. Weighted regression: mean_logA = 1.393 - 0.691 * log(sha). NOT a conditioning tautology — independent-sha null over-depletes large sha 12.2x mean ratio. Secondary: corr(2 log tors, log A) = +0.612 (large-torsion -> larger A, neutralizing torsion denominator on L). Mechanistically EXPLAINS T4 (cbe7b623) low-L-tail sha depletion: the period drops faster than Sha rises, so large-Sha curves are BUFFERED out of the low-L tail relative to sha-independent baseline. Frontier: no known BSD formula predicts corr(Sha, A) = -0.52. Candidate new empirical law. Kill/confirm test: Iwasawa main conjecture or Cassels-Tate bounds; replication at rank 1 and rank 2."},
    {"id": "F044", "label": "Rank-4 corridor: disc=conductor EXACTLY — additive reduction forbidden at rank ≥ 4?",
     "tier": "live_specimen", "n_objects": 2086,
     "description": "Charon 2026-04-18 (eb6d31df): across 2086 rank-4 EC in LMFDB, 2085 have disc=conductor (prime conductor, no additive bad reduction — only multiplicative). ONLY 1 exception. Connects abc conjecture to BSD via measurable arithmetic narrowing at high rank. Open frontier questions: "
                    "(a) theorem hiding in plain sight (some constraint forbids additive reduction at rank >= 4)? "
                    "(b) LMFDB selection artifact (the method of finding rank-4 curves favors prime conductor via isogeny-class or searchable-range restrictions)? "
                    "(c) Pattern 4 sampling frame (LMFDB's rank-4 set is not a random sample of rank-4 curves over Q)? "
                    "Kill/confirm tests needed: (1) verify the 1 exception's existence and its conductor structure; "
                    "(2) replicate at rank 5 where disc=conductor would extend the pattern; "
                    "(3) literature scan — Stein, Elkies, or Dujella rank-record constructions may have selection bias. "
                    "If (a) holds: candidate new calibration anchor. If (b) or (c): Pattern 4 story."},
    {"id": "F045", "label": "Isogeny-class murmuration (5/21 primes) — novel axis, weaker than rank",
     "tier": "live_specimen", "n_objects": None,
     "description": "Ergon 2026-04-18 (7e68116c): murmuration-style stratification by isogeny class size shows 5 of 21 tested primes significant (vs ~1 expected under chance). Headline: p=79 F=6.6. Effect magnitude 5-10x weaker than classical rank-based murmurations. Wachs 2026 literature confirms Sha-direction structure but NOT the isogeny axis — isogeny-class stratification is novel. PRECISION CAVEATS (adversarial review): "
                    "(1) '5/21 significant vs ~1 expected' needs explicit multiple-testing correction. At α=0.05 uncorrected, 5 FPs out of 21 tests has p~0.0001 under null, but raw per-prime p-values should be reported. "
                    "(2) Are the 5 significant primes clustered at small primes (which could be multiplicative-reduction artifact piggybacking on F041a) or distributed? p=79 being the headline suggests non-clustering, but all 5 should be named. "
                    "(3) 5-10x weaker than rank murmurations — the sign of the effect matters. If same-sign-as-rank, the isogeny axis may be a weak proxy. If independent-sign, it is a genuinely new axis. "
                    "Kill/confirm task: compute per-prime uncorrected p-values + correlation with F041a nbp ladder to test whether isogeny-class-size and num_bad_primes are independent axes. If correlated, F045 may collapse into F041a."},
    {"id": "F015", "label": "Szpiro vs conductor — sign-uniform, magnitude non-monotone in k — BLOCK-SHUFFLE VERIFIED",
     "tier": "live_specimen", "n_objects": 30000,
     "description": "Szpiro-vs-conductor slope is sign-uniformly-negative within every bad-prime stratum (P042 z=-6.9..-22.7). **Block-shuffle-within-k null (sessionC audit_F014_F015_block_shuffle, 2026-04-17) VERIFIED the sign-uniform-negative claim at ALL k:** k=1 z=-24.03, k=2 z=-19.70, k=3 z=-12.69, k=4 z=-7.48, k=5 z=-4.06, k=6 z=-3.48. Every stratum z<=-3 under the rigorous null. Magnitude is NOT monotone in k (k=4 breaks the smooth trend; this remains a Pattern-20 anchor on the magnitude side). 88% of pooled -0.597 slope is k-mediated confound; 12% residual survives decontamination (P052 kill). Within-conductor bins show opposite-sign trend (szpiro increases with k). Pattern 19 variant: Ergon monotone claim partially reproduces (sign, yes; magnitude, no). F015 is the first specimen verified under the F010-methodology block-shuffle protocol — **sign claim is durable**."},

    # ----- KILLED but structurally informative -----
    {"id": "F020", "label": "Megethos axis (sorted log-normals)",
     "tier": "killed", "n_objects": None,
     "description": "ρ=1.0 for sorted log-normals. Not structure — artifact of cosine on magnitude-sorted vectors."},
    {"id": "F021", "label": "Phoneme framework (5-axis)",
     "tier": "killed", "n_objects": 789000,
     "description": "Trivial 1D predictor gave ρ=1.0. Unvalidated; the framework was a coordinate choice, not landscape."},
    {"id": "F022", "label": "NF backbone via feature distribution",
     "tier": "killed", "n_objects": 9116,
     "description": "z=0.00 under permutation null when coupling = cosine of feature vectors. Same data as F010. "
                    "Kill tells us: this coordinate system collapses the feature."},
    {"id": "F023", "label": "Spectral tail ARI=0.55 (2026-04-15 version)",
     "tier": "killed", "n_objects": 4000,
     "description": "Conductor conditioning kills: all 4 bins p>0.05. Signal was mediated by conductor, not structural."},
    {"id": "F024", "label": "Faltings explains GUE (H08)",
     "tier": "killed", "n_objects": 10000,
     "description": "y-intercept 0.164 outside GUE 99% CI. Faltings is NOT the axis that resolves the 14% curvature."},
    {"id": "F025", "label": "ADE splits GUE (H10)",
     "tier": "killed", "n_objects": 20000,
     "description": "|Δvar|=0.006 < 0.025. ADE (multiplicative/additive reduction) is NOT the resolver either."},
    {"id": "F026", "label": "Artin dim-2/dim-3 proof-frontier ratio (H61)",
     "tier": "killed", "n_objects": 798000,
     "description": "Ratio 1.8:1, not 50:1 as predicted. The 'proof frontier' framing was wrong."},
    {"id": "F027", "label": "Alexander Mahler × EC L-value (Charon)",
     "tier": "killed", "n_objects": None,
     "description": "z=0 under permutation. Wrong polynomial projection — Alexander has cyclotomic gap, no Lehmer probing."},
    {"id": "F028", "label": "Szpiro × Faltings coupling (H40)",
     "tier": "killed_tautology", "n_objects": 200000,
     "description": "ρ=0.97 after partial control — but both sides encode log|Disc|. Near-identity, not cross-domain."},

    # ----- FRONTIER / DATA GAPS (not features but operational terrain) -----
    {"id": "F030", "label": "Delinquent EC (no L-function data)",
     "tier": "data_frontier", "n_objects": 1508097,
     "description": "51.7% of iso classes lack lfunc data. All 19 rank-5 curves in this gap (conductor 19M-289M)."},
    {"id": "F031", "label": "Object zeros_vector corruption",
     "tier": "data_artifact", "n_objects": 120649,
     "description": "Positions 21-24 are metadata, not zeros. Mnemosyne's audit: pos 21 = root_number (100% match). "
                    "Use lfunc.positive_zeros (authoritative) or truncate to [0:20]."},
    {"id": "F032", "label": "Knot silence (persistent)",
     "tier": "null_confirmed", "n_objects": 12965,
     "description": "Every coordinate system tested shows knot-side coupling at noise level to every other domain. "
                    "Knot projection reveals features other projections don't share."},
    {"id": "F033", "label": "rank ≥ 4 coverage cliff",
     "tier": "data_frontier", "n_objects": 2105,
     "description": "2,086 rank-4 + 19 rank-5 curves. Only 1 has lfunc data. Frontier for BSD verification."},
]


# ============================================================================
# PROJECTIONS (columns of the tensor)
# ============================================================================
# A projection = a coordinate system / scorer / stratification / normalization.
# Documented with what it resolves and what it collapses.

PROJECTIONS = [
    # ----- Feature-distribution projections (mostly collapse object structure) -----
    {"id": "P001", "label": "CouplingScorer (cosine feature similarity)",
     "type": "feature_distribution",
     "description": "Cosine of normalized feature vectors. Sees distributional alignment. "
                    "Collapses under permutation of object labels (distributional, not object-level)."},
    {"id": "P002", "label": "DistributionalCoupling (M4/M2² kurtosis)",
     "type": "feature_distribution",
     "description": "Kurtosis-sensitive coupling. Resolves tail structure. Magnitude-confounded (Megethos)."},
    {"id": "P003", "label": "Megethos / log|magnitude| axis",
     "type": "magnitude_axis",
     "description": "PC of log-magnitude features (log disc, log conductor). Confounds everything. "
                    "Sorted log-normals give ρ=1.0. Anti-projection: explicitly remove before other analysis."},

    # ----- Object-level projections (survive permutation) -----
    {"id": "P010", "label": "Galois-label object-keyed scorer",
     "type": "categorical_object_level",
     "description": "Match by Galois label (e.g. '7T7'). Breaks under permutation of labels. "
                    "Resolves Langlands-style coupling (F010). Introduced 2026-04-17."},
    {"id": "P011", "label": "Lhash exact match",
     "type": "categorical_object_level",
     "description": "LMFDB isospectral grouping hash. Index built 2026-04-17. Should resolve EC↔MF modularity pairs. "
                    "Not yet fully tested (Koios running cross-family join)."},
    {"id": "P012", "label": "trace_hash",
     "type": "categorical_object_level",
     "description": "Alternative to Lhash — hashes Hecke eigenvalues. More strict. Useful when Lhash is too coarse."},

    # ----- Stratification projections -----
    {"id": "P020", "label": "Conductor conditioning",
     "type": "stratification",
     "description": "Condition on conductor before testing. Removes the biggest single confound in EC data. "
                    "Killed spectral tail (F023). Standard discipline."},
    {"id": "P021", "label": "Bad-prime count stratification",
     "type": "stratification",
     "description": "Split by num_bad_primes. Ergon used this to rescue abc/Szpiro (F015). "
                    "Axis revealed real structure that pooled analysis missed."},
    {"id": "P022", "label": "aut_grp stratification (genus-2)",
     "type": "stratification",
     "description": "Split by automorphism group. H85 lives here. The axis that resolves Möbius bias."},
    {"id": "P023", "label": "Rank stratification",
     "type": "stratification",
     "description": "Split by EC rank 0/1/2/3/4/5. Resolves F013 (spacing rigidity)."},
    {"id": "P024", "label": "Torsion stratification",
     "type": "stratification",
     "description": "Split by torsion order. Tested in H38 — z1 not predicted by torsion. Collapses for this feature."},
    {"id": "P025", "label": "CM vs non-CM",
     "type": "stratification",
     "description": "Binary CM flag. Tested 2026-04-16: zero spacings indistinguishable (KS p=0.38). Clean null."},
    {"id": "P026", "label": "Semistable vs additive",
     "type": "stratification",
     "description": "Multiplicative vs additive reduction. Tested H10 — does NOT split GUE deficit."},
    {"id": "P027", "label": "ADE type stratification",
     "type": "stratification",
     "description": "Classify via Dynkin type (rough proxy via Galois label). H11 found WRONG direction at d=4.96."},

    # ----- Battery tests (each is a null-model projection) -----
    {"id": "P040", "label": "F1 permutation null (label shuffle)",
     "type": "null_model",
     "description": "Shuffle all labels, recompute. Kills distributional artifacts. Catches noise."},
    {"id": "P041", "label": "F24 variance decomposition",
     "type": "null_model",
     "description": "Partition variance among axes. Kills effects that don't decompose cleanly."},
    {"id": "P042", "label": "F39 feature permutation (proposed)",
     "type": "null_model",
     "description": "Shuffle features, keep objects. Catches representation artifacts. The F40 proposal."},
    {"id": "P043", "label": "Bootstrap stability",
     "type": "null_model",
     "description": "1000-sample bootstrap. Catches unstable effects."},

    # ----- Preprocessing projections -----
    {"id": "P050", "label": "First-gap analysis (first zero spacing only)",
     "type": "preprocessing",
     "description": "Use only γ₂ - γ₁. Mnemosyne's tool that shrank GUE deficit from 40% to 14%. "
                    "Coordinate choice removed pooling artifact."},
    {"id": "P051", "label": "N(T) unfolding (density normalization)",
     "type": "preprocessing",
     "description": "Divide zero spacings by local density log(N·T²/(4π²)). Turns raw zeros into unfolded ones. "
                    "Correct preprocessing before any RMT comparison."},
    {"id": "P052", "label": "Prime decontamination (3-layer microscope)",
     "type": "preprocessing",
     "description": "Detrend + filter + normalize to remove shared prime factorization. "
                    "96% of scalar cross-dataset structure was shared primes. Use before any numerical coupling."},
    {"id": "P053", "label": "Mahler measure projection",
     "type": "feature_extraction",
     "description": "M(P) = |leading|·∏ max(1, |root|). Maps any polynomial to its growth rate. "
                    "Domain-agnostic — flattens distinction between different domain polynomials."},

    # ----- Feature-distribution scorer added tick 13 (sessionB) -----
    {"id": "P034", "label": "AlignmentCoupling (rank-based extremity coupling)",
     "type": "feature_distribution",
     "description": "Rank-based (quantile) coupling scorer with extremity weighting and sign-agreement term. "
                    "Megethos-robust BY CONSTRUCTION (quantile transform kills magnitude). Learns an interaction "
                    "matrix per domain pair at init via 5-shuffle 2σ filter. Sigmoid-normalized output. Complements "
                    "P001 (raw cosine) and P002 (kurtosis-extended cosine); does NOT replace either. Code: "
                    "harmonia/src/coupling.py:AlignmentCoupling (lines 182-298)."},

    # ----- Stratifications added tick 16 (sessionB merge of sessionC draft; P100 per NAMESPACE_V2) -----
    {"id": "P100", "label": "Isogeny class size stratification",
     "type": "stratification",
     "description": "WHERE class_size = k on ec_curvedata. 100% coverage across 3,824,372 EC. Mazur-bounded "
                    "values {1,2,3,4,6,8}. Resolves Q-rational cyclic-isogeny structure; collapses "
                    "per-curve variation within class and L-function-derived features (invariant within class). "
                    "Partial tautologies vs isogeny_degrees (class_size = len of), P024 torsion, and P039 "
                    "Galois ℓ-adic image (class_size≥2 ⇔ nonmax_primes≠[]). Code: "
                    "cartography/docs/catalog_isogeny_class_size_draft.md (sessionC)."},
    {"id": "P102", "label": "Artin representation dimension stratification",
     "type": "stratification",
     "description": "WHERE \"Dim\" = d on artin_reps. 100% coverage across 798,140 irreducible reps. "
                    "Resolves fixed-degree L-function cohort structure and the Deligne-Serre stratum at "
                    "(Dim=2, Is_Even=False). Collapses per-Galois-group, parity, and Frobenius-Schur "
                    "structure within a dimension. Partial tautologies: Dim | |G| (Maschke), Dim × "
                    "Is_Even (non-uniform — dim-2 odd-dominated, dim-4 even-dominated), symplectic reps "
                    "only at even Dim. H61 and H63 killed at this axis (Pattern 19 anchors). Code: "
                    "cartography/docs/catalog_artin_dim_draft.md (sessionC)."},

    # ----- Catalogued stratifications missing from the tensor (gap-filler 2026-04-18) -----
    {"id": "P028", "label": "Katz-Sarnak family symmetry type",
     "type": "stratification",
     "description": "Family classification {U, Sp, SO_even, SO_odd} from Katz-Sarnak (1999). For EC L-"
                    "functions, SO_even iff rank even and SO_odd iff rank odd (by BSD parity). Resolves "
                    "low-lying zero statistics via one-level density divergence between symmetry types. "
                    "Calibration: function-field Katz-Sarnak theorem. Load-bearing: F011 resolves at "
                    "z=5.38 spread (sessionB tick 8); F013 at z=13.68 slope flip (sessionB tick 18). "
                    "Both survive NULL_BSWCD@v1 at z_block=111.78 and 15.31 respectively."},
    {"id": "P031", "label": "Frobenius-Schur Indicator stratification",
     "type": "stratification",
     "description": "WHERE \"Indicator\" = ν on artin_reps. ν ∈ {−1, 0, +1} for symplectic / complex / "
                    "orthogonal reps. Forbidden-cell partial tautology: ν=−1 only at even dimension. "
                    "Small-n cells below 100 at several (Dim, ν) joints; adequacy check required."},
    {"id": "P032", "label": "MF / Dirichlet character parity stratification",
     "type": "stratification",
     "description": "Split by χ(−1) parity. Resolves Γ-factor archimedean split and Rubinstein-Sarnak "
                    "chebyshev biases. On MF: aliased with weight mod 2. Tautology vs P028 when families "
                    "align with parity."},
    {"id": "P033", "label": "Artin Is_Even parity stratification",
     "type": "stratification",
     "description": "Split Artin reps by Is_Even (image of complex conjugation = +1 iff even). Deligne-"
                    "Serre stratum at (Dim=2, Is_Even=False). Strong non-uniform distribution across Dim "
                    "(dim-2 77% odd; dim-4 74% even). Tautology with P028 on rank-parity for EC families."},
    {"id": "P035", "label": "Kodaira reduction type stratification",
     "type": "stratification",
     "description": "Split EC by Kodaira symbol at each bad prime (I_n, II, III, ..., I_n*, II*, etc.). "
                    "Finer than P026 semistable vs additive. Tautology-adjacent to P021 (Kodaira type "
                    "constrains bad-prime Tamagawa contribution)."},
    {"id": "P036", "label": "Root number stratification",
     "type": "stratification",
     "description": "Split EC by root_number = ±1 (sign of functional equation). Equivalent to (−1)^rank "
                    "under BSD parity; so on EC families this aliases P023 rank parity and P028 Katz-Sarnak "
                    "SO_even/SO_odd. Independent projection only for non-EC L-function families."},
    {"id": "P037", "label": "Sato-Tate group stratification",
     "type": "stratification",
     "description": "Split by Sato-Tate group (SU(2), N(U(1)), U(1), ...). For EC: non-CM gives SU(2); "
                    "CM gives N(U(1)). Tautology with P025 CM flag on EC. Richer on g2c / higher-genus "
                    "where more ST groups appear."},
    {"id": "P038", "label": "Sha (Tate-Shafarevich order) stratification",
     "type": "stratification",
     "description": "Split EC by sha (conjectural Sha order from BSD or proven for small rank). Mazur-Rubin "
                    "stratification. Tautology with F005 high-Sha parity anchor; independence requires sha "
                    "treated as continuous axis rather than parity bin."},
    {"id": "P039", "label": "Galois ℓ-adic image stratification",
     "type": "stratification",
     "description": "Split EC by nonmax_primes list / adelic_index / adelic_level (mod-ℓ Galois image). "
                    "Serre open-image theorem: for non-CM EC, image is almost surely surjective; "
                    "nonmax_primes is finite. Partial tautology with P100 isogeny class size "
                    "(class_size ≥ 2 ⇔ nonmax_primes ≠ [])."},
    {"id": "P101", "label": "EC regulator stratification",
     "type": "stratification",
     "description": "Split EC by regulator (positive for rank ≥ 1; trivially 1 for rank 0). Useful only "
                    "at rank ≥ 1 as a separating axis; rank-0 regulator is degenerate."},
    {"id": "P103", "label": "EC modular degree stratification",
     "type": "stratification",
     "description": "Split EC by modular_degree. Manin-Stevens constant-related. Edixhoven-Jong and "
                    "congruence-number connections. NOT directly stored in current ec_curvedata mirror — "
                    "derivable via lfunc_lfunctions or sessionC's Report 10 approach. Data gap noted."},
    {"id": "P104", "label": "NULL_BSWCD@v1 — Block-shuffle-within-primary-confound null",
     "type": "null_model",
     "description": "Stratified permutation null: within each bin of the chosen primary confound, shuffle "
                    "labels of the test-axis variable. Preserves per-bin marginal distribution; destroys "
                    "within-bin test-axis pairing. Stricter than P040 when test axis correlates with "
                    "confound. Canonical kill: F010 at z=-0.86. Canonical survivals: F011 at z_block=111.78, "
                    "F013 at z_block=15.31, F015 at z_block ∈ [-24.03, -3.48] every k-stratum. "
                    "Pattern 26 (DRAFT): stratifier must have 5-20 balanced strata. See symbols/NULL_BSWCD.md."},
]


# ============================================================================
# INVARIANCE MATRIX (the main tensor)
# ============================================================================
# T[feature_i][projection_j] ∈ {-2, -1, 0, +1, +2}
# Encoded as dict for legibility; converted to np array below.

INVARIANCE = {
    # Calibration anchors resolve everywhere they've been tested
    "F001": {"P010": +2, "P011": +2, "P012": +2, "P020": +1},  # modularity
    "F002": {"P024": +1, "P001": +1},                          # Mazur torsion
    "F003": {"P020": +2, "P023": +2, "P041": +2, "P036": -1},  # BSD parity; P036 root_number = (-1)^rank by BSD → tautological collapse
    "F004": {"P043": +2},                                      # Hasse
    "F005": {"P023": +2, "P024": +1, "P036": -1, "P038": -1},  # high-Sha parity; P036 root_number and P038 sha are both constitutive of F005 (defined by sha≥9 + root_number=(-1)^rank) → tautological collapse
    "F009": {"P024": +2, "P039": +2, "P100": +1},              # torsion primes subset of nonmax primes (Serre+Mazur lineage). P100 +1: class_size>=2 ⇒ nonmax_primes≠[] partial tautology with F009's claim; non-empty nonmax family partially overlaps the F009 anchor cohort.

    # Live specimens — sparse +1s, many -1s in wrong projections
    "F010": {"P001": -1, "P010": -1, "P040": -2, "P042": +1, "P052": -2, "P020": +1, "P021": +1, "P028": +1, "P104": -2},  # NF backbone KILLED: decon ρ=0.27 via P052 killed by block-shuffle-within-degree null (z=-0.86). P104 ANCHOR KILL CASE: NULL_BSWCD@v1 canonical kill (sessionC 711f8325). P052 demoted +1→-2 (the decon signal is degree-marginal leakage, not real). P010 demoted +2→-1 (the object-keyed coupling doesn't survive stricter nulls). F010 joins F022 — same data, no durable signal under the correct null model.
    "F011": {"P050": +1, "P051": +1, "P021": +1, "P023": +1, "P024": +1, "P025": +1, "P026": +1, "P027": -1, "P028": +2, "P020": +2, "P104": +2, "P036": +2},  # GUE deficit: tier downgraded to calibration_confirmed 2026-04-18 per Aporia Report 1. P028 resolves + block-shuffle verified. P036 root_number stratification = (-1)^rank by BSD, so information-identical to P028 on EC (+2 by formal equivalence; not independent measurement). P020 +2 (conductor IS the resolving axis, Duenez-HKMS excised ensemble). P104 DURABLE at z_block=111.78. Not novel anomaly; instrument correctly detected known RMT effect.
    "F012": {"P022": -1, "P040": -2, "P043": -1, "P104": -2},   # H85 KILLED (μ+λ, sessionB 2026-04-17). Pattern 19 canonical case. P104 −2 inferred: signal dead under plain null at n=66K; block-shuffle would also collapse.
    "F013": {"P023": +1, "P041": +1, "P028": +2, "P051": +1, "P104": +2},   # spacing rigidity; P028 resolves at z=13.68 (SO_even vs SO_odd opposite sign, sessionB 2026-04-17). P051 unfolding also matters (sessionD prior). P104 DURABLE at z_block=15.31 (sessionB audit_P028_findings_block_shuffle).
    "F014": {"P053": +2, "P040": +1, "P023": +2, "P021": +2},   # Lehmer spectrum (refined, sessionB 2026-04-17): P053 Mahler + P023 degree (bound touched at deg 10, 20) + P021 num_ram monotone (touched only at num_ram=1,2; jumps at 3+)
    "F015": {"P021": +2, "P020": +1, "P042": +2, "P051": 0, "P052": -1, "P001": -1, "P104": +2, "P023": -1},    # Szpiro sign-uniform / magnitude non-monotone in k; 88% k-mediated (sessionD wsw_F015 2026-04-17); P042 z=-6.9..-22.7; P104 DURABLE at every k-stratum, z∈[-24.03, -3.48]. P023 rank -1: Szpiro is defined on all ranks without rank-conditioning; the k-monotone structure is rank-uniform in sessionD's within-conductor tests. First specimen to pass block-shuffle protocol — durable sign.
    "F041a": {"P023": +2, "P020": +1, "P021": +2, "P026": +1, "P039": -1, "P104": +2, "P025": -1, "P036": -1},   # PROMOTED 2026-04-18. Rank-2+ monotone-in-nbp slope ladder survives: block-null W2 (amp 27.6x corr 0.97), conductor-control U_A (z=3.37), P026 semistable split T3, specific-prime joint T5. P039 Galois-image ruled out (W3). P025 CM -1: rank-2+ CM is rare (coverage cliff); P036 root_number -1: F041a is defined on rank-2+ which splits both root-number classes non-trivially; stratifying by root_number doesn't isolate the monotone slope (per the sessionB gamma_1 displacement result: SO_even and SO_odd have different slope signs but F041a is about amplitude ladder, orthogonal axis). CFKRS Pattern 5 gate pending.
    "F042": {"P025": +1, "P020": +1, "P037": -1, "P039": +1},                                                  # CM disc=-27 quantitative precision on known qualitative structure (Gross 1980, RVZ 1993). P037 Sato-Tate → N(U(1)) by CM hypothesis (tautological). P039 +1 via CM curves having characteristic nonmax_primes structure.
    "F044": {"P020": +2, "P023": +2, "P026": +2, "P035": +1, "P101": -1},                                       # Rank-4 corridor disc=conductor in 2085/2086. Semistable forced. P035 Kodaira +1: semistable implies I_n types only (tautology-adjacent with P026 +2). P101 EC regulator -1: rank-4 regulator axis collapses (only 2085 rows, regulator stratification under-powered / F033 coverage cliff). Open: theorem vs LMFDB artifact.
    "F045": {"P023": +1, "P100": -1},                                                                           # Isogeny-class murmuration 5/21 primes significant. Novel axis per Wachs 2026. Effect 5-10x weaker than rank. P100 -1: isogeny class size IS the F045 test-axis (definitional tautology). Pattern 5 gate + multiple-testing rigor pending.
    "F043": {"P020": +1, "P023": +1, "P038": +1, "P036": -1},                                                  # U_D corr(log Sha, log A)=-0.520 at rank 0; candidate new empirical BSD relation. NOT conditioning tautology. P036 -1: F043 is on rank-0 subset where root_number = +1 constant, no stratification possible.
    "F008": {"P024": +2},                                                                                      # Scholz reflection calibration: 100% pass across 344K quadratic pairs (Ergon + sessionD 2026-04-18).

    # Killed — structurally informative
    "F020": {"P001": -2, "P003": -2, "P040": -2},              # Megethos: not landscape
    "F021": {"P002": -2, "P040": -2},                           # phoneme
    "F022": {"P001": -1, "P040": -2, "P010": +2},              # NF backbone feature-dist: same as F010 but kills via P001
    "F023": {"P020": -2, "P040": +1},                           # spectral tail: kills under conductor
    "F024": {"P027": -1, "P020": -1},                           # Faltings doesn't explain GUE
    "F025": {"P026": -1, "P027": -1},                           # ADE doesn't split GUE
    "F026": {"P040": -1},                                       # Artin ratio
    "F027": {"P053": -1, "P040": -1},                           # Alexander Mahler bridge
    "F028": {"P020": -2, "P041": -2, "P001": +1},              # Szpiro-Faltings: identity not coupling

    # Data operational
    "F030": {"P020": 0},                                        # delinquent — missing data
    "F031": {"P020": -2},                                       # zeros corruption — data artifact
    "F032": {"P001": -2, "P010": -2, "P011": -2, "P053": -2},  # knot silence — persistent across all projections
    "F033": {"P023": 0},                                        # rank ≥ 4 coverage cliff
}


# ============================================================================
# FEATURE GRAPH (directed edges between features)
# ============================================================================
# Relation types: 'supersedes', 'contradicts', 'supports', 'same_object_different_projection',
#                 'reveals_mechanism_of', 'artifact_of'

FEATURE_EDGES = [
    # F013 density-regime parallel to F011 (sessionD wsw_F013)
    {"from": "F013", "to": "F011", "relation": "parallel_density_regime",
     "note": "Both mostly collapse under N(T) unfolding (P051). F013: raw slope -0.00467 -> unfolded -0.00121 (~74% reduction). F011: pooled ~40% -> first-gap raw ~59% -> unfolded ~38%. Both are density-regime features. Proper N(T) unfolding is the next natural probe for the resolving coordinate system."},
    # F010 (NF backbone alive) supersedes F022 (NF backbone killed via feature-dist)
    {"from": "F010", "to": "F022", "relation": "supersedes",
     "note": "Same data, different projection. Feature-dist projection kills; Galois-label resolves."},
    {"from": "F022", "to": "F010", "relation": "same_object_different_projection",
     "note": "Reverse link for navigation."},

    # Calibration anchors
    {"from": "F001", "to": "F003", "relation": "supports",
     "note": "Both are EC↔MF or EC↔L-function identities; both must hold or instrument is broken."},
    {"from": "F003", "to": "F005", "relation": "supports",
     "note": "High-Sha parity is consistent subset of BSD parity."},

    # GUE deficit mechanism search
    {"from": "F024", "to": "F011", "relation": "reveals_mechanism_of",
     "note": "H08 kill tells us Faltings is not the axis that resolves the 14% curvature."},
    {"from": "F025", "to": "F011", "relation": "reveals_mechanism_of",
     "note": "H10 kill tells us ADE reduction type is not the axis either."},

    # Tautology pair
    {"from": "F028", "to": "F014", "relation": "contradicts",
     "note": "Szpiro-Faltings correlation is the formula-level leak; Lehmer shows real disc structure."},

    # Data frontier
    {"from": "F033", "to": "F030", "relation": "subset_of",
     "note": "Rank≥4 coverage cliff is specific instance of delinquent EC problem."},

    # abc trajectory
    {"from": "F015", "to": "F023", "relation": "contrasts",
     "note": "abc survived at fixed bad-primes (coord axis found); spectral tail died at fixed conductor."},

    # Pattern 20 anchor triad — stratification reveals pooled artifact
    {"from": "F015", "to": "F011", "relation": "stratification_reveals_pooled_artifact",
     "note": "Both F015 and F011 show: the POOLED view hides or distorts structure; STRATIFIED views reveal it. "
             "F011: pooled 40% deficit → first-gap unfolded 38% with uniform visibility across 7 projections, "
             "then P028 Katz-Sarnak RESOLVES at SO_even 42% vs SO_odd 35% (sessionB wsw_F011_katz_sarnak). "
             "F015: pooled slope -0.597 → only 12% residual after k-decontamination (88% k-mediated). "
             "Shape: single-axis pooled summaries understate the axis-class enumeration."},
    {"from": "F015", "to": "F013", "relation": "stratification_reveals_pooled_artifact",
     "note": "Parallel to F015→F011 edge. F013: raw slope -0.00467 → ~74% collapse under N(T) unfolding. "
             "F015: pooled slope -0.597 → ~88% collapse under k-decontamination. "
             "Both: naive pooled magnitude reported a larger effect than the stratified/decontaminated residual. "
             "Pattern 20 anchor set: F011 + F013 + F015 (sessionC Pattern 20 merge 2026-04-17)."},

    # ===== edge-weaver batch 1 (Mnemosyne, 2026-04-18) =====
    {"from": "F013", "to": "F011", "relation": "downstream_of",
     "note": "F013 description quote: 'Per Aporia Report 1 finding that F011 is the Duenez-HKMS excised ensemble, "
             "F013’s P028 split is a DOWNSTREAM consequence of the same central-zero-forcing at finite conductor.' "
             "The F013 rank-slope sign flip through P028 Katz-Sarnak is mechanistically driven by the F011 "
             "excised-ensemble bulk deficit."},
    {"from": "F009", "to": "F001", "relation": "calibration_peer",
     "note": "F009 description quote: 'Load-bearing calibration anchor; joins F001-F005.' "
             "Theorem lineage: Serre open-image + Mazur torsion classification."},
    {"from": "F009", "to": "F002", "relation": "calibration_peer",
     "note": "F009 description quote: 'Load-bearing calibration anchor; joins F001-F005.' "
             "F002 Mazur torsion classification is explicitly cited in F009’s theorem lineage."},
    {"from": "F009", "to": "F003", "relation": "calibration_peer",
     "note": "F009 description quote: 'Load-bearing calibration anchor; joins F001-F005.' "
             "F003 BSD parity is part of the calibration family F009 joins."},
    {"from": "F009", "to": "F005", "relation": "calibration_peer",
     "note": "F009 description quote: 'Load-bearing calibration anchor; joins F001-F005.' "
             "F005 high-Sha parity is part of the calibration family F009 joins."},
]


# ============================================================================
# PROJECTION GRAPH (relationships among coordinate systems)
# ============================================================================

PROJECTION_EDGES = [
    {"from": "P002", "to": "P001", "relation": "refines",
     "note": "DistributionalCoupling extends CouplingScorer with kurtosis sensitivity."},
    {"from": "P003", "to": "P001", "relation": "confound_of",
     "note": "CouplingScorer is susceptible to Megethos unless normalized."},
    {"from": "P003", "to": "P002", "relation": "confound_of",
     "note": "Same Megethos issue for distributional scorer."},
    {"from": "P010", "to": "P001", "relation": "orthogonal_to",
     "note": "Categorical object-keyed scorer breaks where distributional scorer fails, and vice versa."},
    {"from": "P050", "to": "P051", "relation": "precedes_in_pipeline",
     "note": "First-gap analysis often does the job without full unfolding."},
    {"from": "P052", "to": "P001", "relation": "preprocessing_for",
     "note": "Prime decontamination must run before any numerical coupling on scalar features."},
    {"from": "P020", "to": "P023", "relation": "independent_of",
     "note": "Conductor and rank stratifications can be applied jointly."},
    {"from": "P040", "to": "P042", "relation": "weaker_than",
     "note": "F1 label shuffle catches less than F39 feature permutation for representation artifacts."},
    {"from": "P027", "to": "P010", "relation": "heuristic_proxy_for",
     "note": "ADE-type via Galois label is a coarse proxy for the actual object-keyed Galois scorer."},
]


# ============================================================================
# BUILD TENSOR AND WRITE ARTIFACTS
# ============================================================================

def build_tensor():
    feature_ids = [f["id"] for f in FEATURES]
    proj_ids = [p["id"] for p in PROJECTIONS]
    f_idx = {fid: i for i, fid in enumerate(feature_ids)}
    p_idx = {pid: j for j, pid in enumerate(proj_ids)}

    T = np.zeros((len(feature_ids), len(proj_ids)), dtype=np.int8)
    for fid, row in INVARIANCE.items():
        if fid not in f_idx:
            continue
        for pid, val in row.items():
            if pid not in p_idx:
                continue
            T[f_idx[fid], p_idx[pid]] = val
    return T, feature_ids, proj_ids


def write_all(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    T, fids, pids = build_tensor()

    np.savez(outdir / "landscape_tensor.npz",
             T=T, feature_ids=np.array(fids), projection_ids=np.array(pids))

    with open(outdir / "landscape_manifest.json", "w") as f:
        json.dump({
            "version": "1.0",
            "date": "2026-04-17",
            "charter_ref": "docs/landscape_charter.md",
            "harmonia_charter": "roles/Harmonia/CHARTER.md",
            "tensor_shape": list(T.shape),
            "tensor_encoding": {
                "-2": "projection provably collapses the feature (known artifact)",
                "-1": "projection tested, feature not resolved",
                "0": "projection not tested against this feature",
                "+1": "projection resolves the feature",
                "+2": "projection strongly resolves AND validates under permutation-break null"
            },
            "features": FEATURES,
            "projections": PROJECTIONS,
            "invariance_matrix_dict": INVARIANCE,  # same as tensor but human-readable
            "calibration_anchors": [f["id"] for f in FEATURES if f["tier"] == "calibration"],
            "live_specimens": [f["id"] for f in FEATURES if f["tier"] == "live_specimen"],
        }, f, indent=2, default=str)

    with open(outdir / "feature_graph.json", "w") as f:
        json.dump({"edges": FEATURE_EDGES}, f, indent=2)

    with open(outdir / "projection_graph.json", "w") as f:
        json.dump({"edges": PROJECTION_EDGES}, f, indent=2)

    # Diagnostic summary
    print(f"Tensor shape: {T.shape}")
    print(f"  features: {len(FEATURES)}")
    print(f"  projections: {len(PROJECTIONS)}")
    print(f"  non-zero cells: {int((T != 0).sum())} of {T.size}")
    print(f"  strong resolves (+2): {int((T == 2).sum())}")
    print(f"  resolves (+1): {int((T == 1).sum())}")
    print(f"  collapses (-1): {int((T == -1).sum())}")
    print(f"  hard collapses (-2): {int((T == -2).sum())}")

    # Per-feature invariance profile (how many projections resolve each)
    print("\nPer-feature resolution counts:")
    for i, fid in enumerate(fids):
        resolves = int((T[i] > 0).sum())
        collapses = int((T[i] < 0).sum())
        untested = int((T[i] == 0).sum())
        label = next(f["label"] for f in FEATURES if f["id"] == fid)
        print(f"  {fid} ({label[:50]:50s}): +{resolves} / -{collapses} / ?{untested}")


if __name__ == "__main__":
    outdir = os.path.dirname(os.path.abspath(__file__))
    write_all(outdir)
    print(f"\nArtifacts written to: {outdir}")
