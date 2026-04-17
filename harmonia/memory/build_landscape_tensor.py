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
    {"id": "F003", "label": "BSD parity (rank = analytic_rank)",
     "tier": "calibration", "n_objects": 2481157,
     "description": "rank = ov for all of bsd_joined. 100.000%. Not a finding — projection calibration."},
    {"id": "F004", "label": "Hasse bound on a_p",
     "tier": "calibration", "n_objects": 150000,
     "description": "|a_p| ≤ 2√p. 100% of 150K coefficients."},
    {"id": "F005", "label": "High-Sha parity (H43)",
     "tier": "calibration", "n_objects": 67035,
     "description": "Among sha≥9: (-1)^rank = root_number perfect."},

    # ----- LIVE SPECIMENS (weak-but-survives) -----
    {"id": "F010", "label": "NF backbone via Galois-label",
     "tier": "live_specimen", "n_objects": 114,
     "description": "ρ(NF log_disc, Artin log_cond) = 0.40 over 114 shared labels. z=3.64. "
                    "Survives object-keyed permutation. Reads as Langlands functoriality through categorical projection."},
    {"id": "F011", "label": "GUE first-gap deficit (~38% unfolded, n=2M)",
     "tier": "live_specimen", "n_objects": 2009089,
     "description": "Unfolded first-gap variance ~0.110 vs GUE 0.178 = ~38% deficit at n=2,009,089 "
                    "(sessionC wsw_F011, 2026-04-17; validated by sessionA). Raw P050: ~59% z=-595. "
                    "Unfolded P051: ~38% z=-383. Uniform across 7 projections (P050-P051-P021-P023-P024-P025-P026 "
                    "all verdict +1). 14% was a smaller-sample pre-unfolding artifact; Mnemosyne's first-gap "
                    "reduction from 40% pooled held directionally but the clean n=2M number is ~38%. "
                    "Faltings (H08) killed; ADE (H10) killed. Pattern 13: conductor-family axes do not resolve. "
                    "Next probes: P028 Katz-Sarnak, H09 conductor-window finite-N, representation-theoretic axes."},
    {"id": "F012", "label": "Möbius bias at g2c aut groups (H85) — KILLED",
     "tier": "killed", "n_objects": 66158,
     "description": "KILLED across Möbius AND Liouville definitions (sessionB wsw_F012 + liouville_side_check_F012, 2026-04-17). Clean measurement on full n=66158 g2c: max|z| over adequate strata = 0.39 (μ) / 0.52 (λ), permutation p = 0.68 (μ) / 0.60 (λ). The prior |z|=6.15 DID NOT REPRODUCE under either Möbius or Liouville. Definitional drift hypothesis excluded. Canonical Pattern 19 case: stale or never-reproducible tensor entry. Likely causes: different subset, different scorer, or original measurement was noise. 63% non-squarefree g2c discriminants reduce effective S/N but don't account for the 16x discrepancy."},
    {"id": "F013", "label": "Zero spacing rigidity vs rank (H06)",
     "tier": "live_specimen", "n_objects": 50000,
     "description": "Spacing variance decreases linearly with rank. slope=-0.0019, R²=0.399. Weak."},
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
                    "claims without degree-AND-num_ram stratification are suspect — Salem polynomials cluster "
                    "in the sub-1.228 region at specific degree × low-num_ram combinations."},
    {"id": "F015", "label": "Szpiro monotone decrease at fixed bad-prime count (Ergon)",
     "tier": "live_specimen", "n_objects": None,
     "description": "abc Szpiro ratio decreases monotonically with conductor when stratified by num_bad_primes. "
                    "Coordinate system revelation: bad_primes is the axis that resolves this."},

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
    "F003": {"P020": +2, "P023": +2, "P041": +2},             # BSD parity
    "F004": {"P043": +2},                                      # Hasse
    "F005": {"P023": +2, "P024": +1},                          # high-Sha parity

    # Live specimens — sparse +1s, many -1s in wrong projections
    "F010": {"P001": -1, "P010": +2, "P040": -1, "P042": +1},  # NF backbone: dies distributional, survives object-keyed
    "F011": {"P050": +1, "P051": +1, "P021": +1, "P023": +1, "P024": +1, "P025": +1, "P026": +1, "P027": -1},  # GUE deficit: uniform +1 across 7 projections (sessionC n=2M); P027 ADE killed per H10. Resolving axis still unknown.
    "F012": {"P022": -1, "P040": -2, "P043": -1},               # H85 KILLED (μ+λ, sessionB 2026-04-17). Pattern 19 canonical case.
    "F013": {"P023": +1, "P041": +1},                           # spacing rigidity
    "F014": {"P053": +2, "P040": +1, "P023": +2, "P021": +2},   # Lehmer spectrum (refined, sessionB 2026-04-17): P053 Mahler + P023 degree (bound touched at deg 10, 20) + P021 num_ram monotone (touched only at num_ram=1,2; jumps at 3+)
    "F015": {"P021": +2, "P001": -1},                           # abc rescue: bad_primes is the axis

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
