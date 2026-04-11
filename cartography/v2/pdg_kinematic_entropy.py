"""
PDG Kinematic Phase Space Entropy (List2 #3)

Calculate Shannon entropy of decay product mass distributions,
normalized by total available kinematic phase space (Q-value),
averaged over all primary hadronic decay channels.

Approach:
  1. Load PDG particle masses from particles.json
  2. Use curated hadronic decay channels with branching ratios (PDG 2024)
  3. For each decay channel: Q-value = M_parent - sum(M_daughters)
  4. Shannon entropy: H = -sum(BR_i * log2(BR_i))
  5. Normalized entropy: H_norm = H / log2(n_channels)
  6. Average across all particles with known decays
  7. Correlations: H vs mass, H vs lifetime
"""

import json
import math
import numpy as np
from pathlib import Path
from scipy import stats

# ---------------------------------------------------------------------------
# 1. Load PDG masses
# ---------------------------------------------------------------------------
PDG_PATH = Path(__file__).parent.parent / "physics" / "data" / "pdg" / "particles.json"
with open(PDG_PATH) as f:
    pdg_raw = json.load(f)

# Build mass lookup by MC ID
mass_by_id = {}
width_by_id = {}
name_by_id = {}
for p in pdg_raw:
    for mid in p["mc_ids"]:
        mass_by_id[mid] = p["mass_GeV"]
        width_by_id[mid] = p.get("width_GeV", 0.0)
        name_by_id[mid] = p["name"].strip()

# Convenience mass constants (GeV) - from PDG 2024
M = {
    "pi+": 0.13957,
    "pi-": 0.13957,
    "pi0": 0.13498,
    "K+": 0.49368,
    "K-": 0.49368,
    "K0": 0.49761,
    "Kbar0": 0.49761,
    "KS0": 0.49761,
    "KL0": 0.49761,
    "eta": 0.54786,
    "eta'": 0.95778,
    "rho0": 0.77526,
    "rho+": 0.77526,
    "rho-": 0.77526,
    "omega": 0.78266,
    "phi": 1.01946,
    "K*+": 0.89167,
    "K*-": 0.89167,
    "K*0": 0.89555,
    "K*bar0": 0.89555,
    "p": 0.93827,
    "pbar": 0.93827,
    "n": 0.93957,
    "nbar": 0.93957,
    "e+": 0.000511,
    "e-": 0.000511,
    "mu+": 0.10566,
    "mu-": 0.10566,
    "nu": 0.0,
    "nubar": 0.0,
    "gamma": 0.0,
    "D+": 1.86966,
    "D-": 1.86966,
    "D0": 1.86484,
    "Dbar0": 1.86484,
    "Ds+": 1.96835,
    "Ds-": 1.96835,
    "D*+": 2.01026,
    "D*-": 2.01026,
    "D*0": 2.00685,
    "B+": 5.27934,
    "B-": 5.27934,
    "B0": 5.27965,
    "Bbar0": 5.27965,
    "Bs0": 5.36688,
    "J/psi": 3.09690,
    "psi(2S)": 3.68610,
    "Upsilon(1S)": 9.46040,
    "Upsilon(2S)": 10.02326,
    "Upsilon(3S)": 10.3552,
    "Upsilon(4S)": 10.5794,
    "Lambda": 1.11568,
    "Sigma+": 1.18937,
    "Sigma0": 1.19264,
    "Sigma-": 1.19745,
    "Xi0": 1.31486,
    "Xi-": 1.32171,
    "Omega-": 1.67245,
    "Lambda_c+": 2.28646,
    "a1+": 1.230,
    "a1-": 1.230,
    "f0(500)": 0.475,
    "f0(980)": 0.990,
    "f2(1270)": 1.2754,
    "a0(980)+": 0.980,
    "a0(980)-": 0.980,
    "a2(1320)+": 1.3182,
    "a2(1320)-": 1.3182,
    "b1(1235)+": 1.2295,
    "b1(1235)-": 1.2295,
}

# ---------------------------------------------------------------------------
# 2. Curated hadronic decay channels with branching ratios (PDG 2024)
#    Focus: primary hadronic decay modes for unstable hadrons and mesons
# ---------------------------------------------------------------------------
# Format: { "particle": { mass_GeV, width_GeV, mc_id,
#            channels: [ {products: [...], BR: float}, ... ] } }

DECAY_DATA = {
    # ---- Light unflavored mesons ----
    "pi0": {
        "mass": 0.13498, "width": 7.81e-9, "mc_id": 111,
        "channels": [
            {"products": ["gamma", "gamma"], "BR": 0.98823},
            {"products": ["e+", "e-", "gamma"], "BR": 0.01174},
        ]
    },
    "eta": {
        "mass": 0.54786, "width": 1.31e-6, "mc_id": 221,
        "channels": [
            {"products": ["gamma", "gamma"], "BR": 0.3941},
            {"products": ["pi0", "pi0", "pi0"], "BR": 0.3268},
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.2292},
            {"products": ["pi+", "pi-", "gamma"], "BR": 0.0422},
            {"products": ["e+", "e-", "gamma"], "BR": 0.0069},
        ]
    },
    "rho0": {
        "mass": 0.77526, "width": 0.1474, "mc_id": 113,
        "channels": [
            {"products": ["pi+", "pi-"], "BR": 1.0},
        ]
    },
    "omega": {
        "mass": 0.78266, "width": 0.00868, "mc_id": 223,
        "channels": [
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.893},
            {"products": ["pi0", "gamma"], "BR": 0.0828},
            {"products": ["pi+", "pi-"], "BR": 0.0153},
        ]
    },
    "eta'": {
        "mass": 0.95778, "width": 0.000188, "mc_id": 331,
        "channels": [
            {"products": ["pi+", "pi-", "eta"], "BR": 0.426},
            {"products": ["rho0", "gamma"], "BR": 0.291},
            {"products": ["pi0", "pi0", "eta"], "BR": 0.228},
            {"products": ["omega", "gamma"], "BR": 0.0275},
            {"products": ["gamma", "gamma"], "BR": 0.0220},
        ]
    },
    "phi": {
        "mass": 1.01946, "width": 0.004249, "mc_id": 333,
        "channels": [
            {"products": ["K+", "K-"], "BR": 0.491},
            {"products": ["KS0", "KL0"], "BR": 0.340},
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.153},
            {"products": ["eta", "gamma"], "BR": 0.01303},
        ]
    },
    "f0(500)": {
        "mass": 0.475, "width": 0.550, "mc_id": 9000221,
        "channels": [
            {"products": ["pi+", "pi-"], "BR": 0.667},
            {"products": ["pi0", "pi0"], "BR": 0.333},
        ]
    },
    "f0(980)": {
        "mass": 0.990, "width": 0.055, "mc_id": 9010221,
        "channels": [
            {"products": ["pi+", "pi-"], "BR": 0.52},
            {"products": ["pi0", "pi0"], "BR": 0.26},
            {"products": ["K+", "K-"], "BR": 0.11},
            {"products": ["K0", "Kbar0"], "BR": 0.11},
        ]
    },
    "f2(1270)": {
        "mass": 1.2754, "width": 0.1867, "mc_id": 225,
        "channels": [
            {"products": ["pi+", "pi-"], "BR": 0.564},
            {"products": ["pi0", "pi0"], "BR": 0.282},
            {"products": ["K+", "K-"], "BR": 0.023},
            {"products": ["K0", "Kbar0"], "BR": 0.023},
            {"products": ["eta", "eta"], "BR": 0.004},
            {"products": ["pi+", "pi-", "pi+", "pi-"], "BR": 0.028},
            {"products": ["pi0", "pi0", "pi+", "pi-"], "BR": 0.070},
            {"products": ["gamma", "gamma"], "BR": 0.0014},
        ]
    },

    # ---- Strange mesons ----
    "K+": {
        "mass": 0.49368, "width": 5.317e-17, "mc_id": 321,
        "channels": [
            {"products": ["mu+", "nu"], "BR": 0.6356},
            {"products": ["pi+", "pi0"], "BR": 0.2067},
            {"products": ["pi+", "pi+", "pi-"], "BR": 0.05583},
            {"products": ["pi0", "e+", "nu"], "BR": 0.0507},
            {"products": ["pi0", "mu+", "nu"], "BR": 0.03352},
            {"products": ["pi+", "pi0", "pi0"], "BR": 0.01760},
        ]
    },
    "KS0": {
        "mass": 0.49761, "width": 7.3508e-15, "mc_id": 310,
        "channels": [
            {"products": ["pi+", "pi-"], "BR": 0.6920},
            {"products": ["pi0", "pi0"], "BR": 0.3069},
        ]
    },
    "KL0": {
        "mass": 0.49761, "width": 1.287e-17, "mc_id": 130,
        "channels": [
            {"products": ["pi0", "pi0", "pi0"], "BR": 0.1952},
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.1254},
            {"products": ["pi-", "e+", "nu"], "BR": 0.2027},
            {"products": ["pi+", "e-", "nubar"], "BR": 0.2027},
            {"products": ["pi-", "mu+", "nu"], "BR": 0.1352},
            {"products": ["pi+", "mu-", "nubar"], "BR": 0.1352},
        ]
    },
    "K*0": {
        "mass": 0.89555, "width": 0.0473, "mc_id": 313,
        "channels": [
            {"products": ["K+", "pi-"], "BR": 0.667},
            {"products": ["K0", "pi0"], "BR": 0.333},
        ]
    },
    "K*+": {
        "mass": 0.89167, "width": 0.0514, "mc_id": 323,
        "channels": [
            {"products": ["K0", "pi+"], "BR": 0.667},
            {"products": ["K+", "pi0"], "BR": 0.333},
        ]
    },

    # ---- Charm mesons ----
    "D+": {
        "mass": 1.86966, "width": 6.33e-13, "mc_id": 411,
        "channels": [
            {"products": ["Kbar0", "pi+"], "BR": 0.0289},
            {"products": ["K-", "pi+", "pi+"], "BR": 0.0946},
            {"products": ["Kbar0", "pi+", "pi0"], "BR": 0.143},
            {"products": ["Kbar0", "pi+", "pi+", "pi-"], "BR": 0.0812},
            {"products": ["K-", "pi+", "pi+", "pi0"], "BR": 0.0620},
            {"products": ["KS0", "pi+"], "BR": 0.0155},
            {"products": ["K-", "e+", "nu"], "BR": 0.0350},  # semileptonic
            {"products": ["K-", "mu+", "nu"], "BR": 0.0332},  # semileptonic
            {"products": ["Kbar0", "mu+", "nu"], "BR": 0.0967},
            {"products": ["pi+", "pi+", "pi-"], "BR": 0.00317},
            {"products": ["Kbar0", "K+"], "BR": 0.00603},
        ]
    },
    "D0": {
        "mass": 1.86484, "width": 1.605e-12, "mc_id": 421,
        "channels": [
            {"products": ["K-", "pi+"], "BR": 0.03947},
            {"products": ["K-", "pi+", "pi0"], "BR": 0.144},
            {"products": ["K-", "pi+", "pi+", "pi-"], "BR": 0.0824},
            {"products": ["Kbar0", "pi+", "pi-"], "BR": 0.0288},
            {"products": ["Kbar0", "pi0"], "BR": 0.0236},
            {"products": ["K-", "e+", "nu"], "BR": 0.0355},
            {"products": ["K-", "mu+", "nu"], "BR": 0.0342},
            {"products": ["pi+", "pi-"], "BR": 0.001455},
            {"products": ["K+", "K-"], "BR": 0.00407},
            {"products": ["Kbar0", "pi+", "pi-", "pi0"], "BR": 0.0957},
        ]
    },
    "Ds+": {
        "mass": 1.96835, "width": 1.305e-12, "mc_id": 431,
        "channels": [
            {"products": ["K+", "Kbar0"], "BR": 0.0297},
            {"products": ["K+", "K-", "pi+"], "BR": 0.0534},
            {"products": ["K+", "KS0", "pi+", "pi-"], "BR": 0.0172},
            {"products": ["eta", "pi+"], "BR": 0.0179},
            {"products": ["eta'", "pi+"], "BR": 0.0384},
            {"products": ["phi", "pi+"], "BR": 0.0245},
            {"products": ["pi+", "pi+", "pi-"], "BR": 0.01090},
            {"products": ["mu+", "nu"], "BR": 0.00528},
            {"products": ["eta", "rho+"], "BR": 0.0890},
        ]
    },

    # ---- Bottom mesons (selected major modes) ----
    "B+": {
        "mass": 5.27934, "width": 4.018e-13, "mc_id": 521,
        "channels": [
            {"products": ["Dbar0", "pi+"], "BR": 0.00484},
            {"products": ["D-", "pi+", "pi+"], "BR": 0.00107},
            {"products": ["Dbar0", "rho+"], "BR": 0.0134},
            {"products": ["D*-", "pi+", "pi+"], "BR": 0.00128},
            {"products": ["J/psi", "K+"], "BR": 0.00101},
            {"products": ["Dbar0", "e+", "nu"], "BR": 0.0233},
            {"products": ["Dbar0", "mu+", "nu"], "BR": 0.0233},
            {"products": ["D*bar0", "e+", "nu"], "BR": 0.0570},  # D*0bar
            {"products": ["Dbar0", "pi+", "pi0"], "BR": 0.0108},
            {"products": ["Dbar0", "K+"], "BR": 0.000386},
        ]
    },
    "B0": {
        "mass": 5.27965, "width": 4.294e-13, "mc_id": 511,
        "channels": [
            {"products": ["D-", "pi+"], "BR": 0.00252},
            {"products": ["D-", "rho+"], "BR": 0.0078},
            {"products": ["D*-", "pi+"], "BR": 0.00276},
            {"products": ["D*-", "rho+"], "BR": 0.0068},
            {"products": ["J/psi", "K0"], "BR": 0.000874},
            {"products": ["D-", "e+", "nu"], "BR": 0.0218},
            {"products": ["D*-", "e+", "nu"], "BR": 0.0505},
            {"products": ["D-", "pi+", "pi+", "pi-"], "BR": 0.0082},
            {"products": ["D-", "K+"], "BR": 0.000199},
            {"products": ["pi+", "pi-"], "BR": 0.00000526},
        ]
    },

    # ---- Charmonium ----
    "J/psi": {
        "mass": 3.09690, "width": 9.26e-5, "mc_id": 443,
        "channels": [
            {"products": ["e+", "e-"], "BR": 0.05971},
            {"products": ["mu+", "mu-"], "BR": 0.05961},
            # hadrons ~88% split among many channels
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.0218},
            {"products": ["rho0", "pi0"], "BR": 0.0056},
            {"products": ["omega", "pi+", "pi-"], "BR": 0.0080},
            {"products": ["K+", "K-", "pi0"], "BR": 0.0052},
            {"products": ["pi+", "pi-", "pi+", "pi-", "pi0"], "BR": 0.056},
            {"products": ["K+", "K-"], "BR": 0.000286},
            {"products": ["p", "pbar"], "BR": 0.00217},
            {"products": ["eta", "pi+", "pi-"], "BR": 0.0179},
        ]
    },
    "psi(2S)": {
        "mass": 3.68610, "width": 2.94e-4, "mc_id": 100443,
        "channels": [
            {"products": ["J/psi", "pi+", "pi-"], "BR": 0.347},
            {"products": ["J/psi", "pi0", "pi0"], "BR": 0.184},
            {"products": ["J/psi", "eta"], "BR": 0.0340},
            {"products": ["e+", "e-"], "BR": 0.00793},
            {"products": ["mu+", "mu-"], "BR": 0.00793},
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.00188},
            {"products": ["gamma", "eta"], "BR": 0.00130},
        ]
    },

    # ---- Bottomonium ----
    "Upsilon(1S)": {
        "mass": 9.46040, "width": 5.402e-5, "mc_id": 553,
        "channels": [
            {"products": ["e+", "e-"], "BR": 0.0238},
            {"products": ["mu+", "mu-"], "BR": 0.0248},
            # ~95% hadronic, very fragmented — use effective grouped modes
            {"products": ["gamma", "pi+", "pi-"], "BR": 0.0037},
            {"products": ["pi+", "pi-", "pi0"], "BR": 0.0003},
        ]
    },
    "Upsilon(4S)": {
        "mass": 10.5794, "width": 0.0205, "mc_id": 300553,
        "channels": [
            {"products": ["B+", "B-"], "BR": 0.514},
            {"products": ["B0", "Bbar0"], "BR": 0.486},
        ]
    },

    # ---- Light baryons ----
    "n": {
        "mass": 0.93957, "width": 7.485e-28, "mc_id": 2112,
        "channels": [
            {"products": ["p", "e-", "nubar"], "BR": 1.0},
        ]
    },
    "Lambda": {
        "mass": 1.11568, "width": 2.501e-15, "mc_id": 3122,
        "channels": [
            {"products": ["p", "pi-"], "BR": 0.6394},
            {"products": ["n", "pi0"], "BR": 0.3586},
        ]
    },
    "Sigma+": {
        "mass": 1.18937, "width": 8.209e-15, "mc_id": 3222,
        "channels": [
            {"products": ["p", "pi0"], "BR": 0.5157},
            {"products": ["n", "pi+"], "BR": 0.4843},
        ]
    },
    "Sigma-": {
        "mass": 1.19745, "width": 4.45e-15, "mc_id": 3112,
        "channels": [
            {"products": ["n", "pi-"], "BR": 0.99848},
        ]
    },
    "Sigma0": {
        "mass": 1.19264, "width": 8.9e-6, "mc_id": 3212,
        "channels": [
            {"products": ["Lambda", "gamma"], "BR": 1.0},
        ]
    },
    "Xi0": {
        "mass": 1.31486, "width": 2.27e-15, "mc_id": 3322,
        "channels": [
            {"products": ["Lambda", "pi0"], "BR": 0.99524},
        ]
    },
    "Xi-": {
        "mass": 1.32171, "width": 4.02e-15, "mc_id": 3312,
        "channels": [
            {"products": ["Lambda", "pi-"], "BR": 0.99887},
        ]
    },
    "Omega-": {
        "mass": 1.67245, "width": 8.02e-15, "mc_id": 3334,
        "channels": [
            {"products": ["Lambda", "K-"], "BR": 0.6780},
            {"products": ["Xi0", "pi-"], "BR": 0.2360},
            {"products": ["Xi-", "pi0"], "BR": 0.0860},
        ]
    },

    # ---- Charm baryons ----
    "Lambda_c+": {
        "mass": 2.28646, "width": 3.30e-12, "mc_id": 4122,
        "channels": [
            {"products": ["p", "K-", "pi+"], "BR": 0.0651},
            {"products": ["p", "Kbar0"], "BR": 0.0323},
            {"products": ["Lambda", "pi+"], "BR": 0.0130},
            {"products": ["Lambda", "pi+", "pi0"], "BR": 0.071},
            {"products": ["Lambda", "pi+", "pi+", "pi-"], "BR": 0.0266},
            {"products": ["Sigma+", "pi+", "pi-"], "BR": 0.0450},
            {"products": ["p", "K-", "pi+", "pi0"], "BR": 0.041},
        ]
    },

    # ---- Light resonances ----
    "rho+": {
        "mass": 0.77526, "width": 0.1474, "mc_id": 213,
        "channels": [
            {"products": ["pi+", "pi0"], "BR": 1.0},
        ]
    },
    "a1+": {  # a1(1260)
        "mass": 1.230, "width": 0.420, "mc_id": 20213,
        "channels": [
            {"products": ["rho0", "pi+"], "BR": 0.50},
            {"products": ["rho+", "pi0"], "BR": 0.50},
        ]
    },

    # ---- Delta baryons ----
    "Delta++": {
        "mass": 1.232, "width": 0.117, "mc_id": 2224,
        "channels": [
            {"products": ["p", "pi+"], "BR": 1.0},
        ]
    },
    "Delta+": {
        "mass": 1.232, "width": 0.117, "mc_id": 2214,
        "channels": [
            {"products": ["p", "pi0"], "BR": 0.667},
            {"products": ["n", "pi+"], "BR": 0.333},
        ]
    },
    "Delta0": {
        "mass": 1.232, "width": 0.117, "mc_id": 2114,
        "channels": [
            {"products": ["n", "pi0"], "BR": 0.667},
            {"products": ["p", "pi-"], "BR": 0.333},
        ]
    },

    # ---- W and Z (include for completeness) ----
    "W+": {
        "mass": 80.369, "width": 2.08, "mc_id": 24,
        "channels": [
            {"products": ["e+", "nu"], "BR": 0.1071},
            {"products": ["mu+", "nu"], "BR": 0.1063},
            {"products": ["pi+", "pi-"], "BR": 0.0},  # placeholder
            # hadronic: ~67.4%
            # ud, cs dominate
        ]
    },

    # ---- tau lepton (important for hadronic decays) ----
    "tau-": {
        "mass": 1.77693, "width": 2.267e-12, "mc_id": 15,
        "channels": [
            {"products": ["pi-", "nu"], "BR": 0.1082},
            {"products": ["pi-", "pi0", "nu"], "BR": 0.2549},
            {"products": ["pi-", "pi0", "pi0", "nu"], "BR": 0.0926},
            {"products": ["pi-", "pi+", "pi-", "nu"], "BR": 0.0904},
            {"products": ["K-", "nu"], "BR": 0.00697},
            {"products": ["K-", "pi0", "nu"], "BR": 0.00433},
            {"products": ["e-", "nubar", "nu"], "BR": 0.1782},
            {"products": ["mu-", "nubar", "nu"], "BR": 0.1739},
        ]
    },
}

# ---------------------------------------------------------------------------
# 3. Compute entropy metrics for each particle
# ---------------------------------------------------------------------------
results = []

for name, info in DECAY_DATA.items():
    channels = info["channels"]
    mass_parent = info["mass"]
    width = info["width"]

    # Filter channels with BR > 0
    valid_channels = [ch for ch in channels if ch["BR"] > 0]
    n_ch = len(valid_channels)

    if n_ch < 1:
        continue

    # Normalize BRs to sum to 1 (they may not due to unlisted modes)
    br_sum = sum(ch["BR"] for ch in valid_channels)
    brs_norm = [ch["BR"] / br_sum for ch in valid_channels]

    # Q-values
    q_values = []
    for ch in valid_channels:
        daughter_mass = sum(M.get(p, 0.0) for p in ch["products"])
        q = mass_parent - daughter_mass
        q_values.append(q)

    # Shannon entropy
    H = 0.0
    for br in brs_norm:
        if br > 0:
            H -= br * math.log2(br)

    # Normalized entropy
    H_norm = H / math.log2(n_ch) if n_ch > 1 else 0.0

    # Lifetime from width: tau = hbar / Gamma
    hbar_GeV_s = 6.582119569e-25  # GeV*s
    lifetime_s = hbar_GeV_s / width if width > 0 else float("inf")

    # Q-value weighted entropy: weight each channel's contribution by Q/Q_max
    q_max = max(q_values) if q_values else 1.0
    H_q_weighted = 0.0
    if q_max > 0 and n_ch > 1:
        for br, q in zip(brs_norm, q_values):
            w = q / q_max if q_max > 0 else 1.0
            if br > 0 and w > 0:
                H_q_weighted -= br * w * math.log2(br)

    avg_q = np.mean(q_values) if q_values else 0.0

    entry = {
        "particle": name,
        "mass_GeV": mass_parent,
        "width_GeV": width,
        "lifetime_s": lifetime_s if lifetime_s != float("inf") else None,
        "n_channels": n_ch,
        "BR_sum_raw": round(br_sum, 6),
        "Q_values_GeV": [round(q, 6) for q in q_values],
        "avg_Q_GeV": round(float(avg_q), 6),
        "shannon_entropy_bits": round(H, 6),
        "normalized_entropy": round(H_norm, 6),
        "Q_weighted_entropy": round(H_q_weighted, 6),
    }
    results.append(entry)

# ---------------------------------------------------------------------------
# 4. Aggregate statistics
# ---------------------------------------------------------------------------
# Filter particles with n_channels > 1 for meaningful entropy
multi_ch = [r for r in results if r["n_channels"] > 1]

H_norms = [r["normalized_entropy"] for r in multi_ch]
H_raw = [r["shannon_entropy_bits"] for r in multi_ch]
masses = [r["mass_GeV"] for r in multi_ch]
n_channels_list = [r["n_channels"] for r in multi_ch]

avg_H_norm = float(np.mean(H_norms))
std_H_norm = float(np.std(H_norms))
median_H_norm = float(np.median(H_norms))

# Separate hadronic-dominant particles (exclude W, tau, leptons, gauge bosons)
NON_HADRONIC = {"W+", "tau-", "n"}  # n is beta decay (weak), not hadronic
hadronic_particles = [r for r in multi_ch if r["particle"] not in NON_HADRONIC]
hadronic_H_norms = [r["normalized_entropy"] for r in hadronic_particles]
avg_H_norm_hadronic = float(np.mean(hadronic_H_norms))

# Channel-count weighted average (heavier weight to richer spectra)
total_ch = sum(r["n_channels"] for r in multi_ch)
weighted_H_norm = sum(r["normalized_entropy"] * r["n_channels"] for r in multi_ch) / total_ch

# Particles with >= 3 channels (well-measured spectra)
rich_ch = [r for r in multi_ch if r["n_channels"] >= 3]
rich_H_norms = [r["normalized_entropy"] for r in rich_ch]
avg_H_norm_rich = float(np.mean(rich_H_norms)) if rich_H_norms else 0.0

# Q-value weighted entropy average
q_weighted_entropies = [r["Q_weighted_entropy"] for r in multi_ch if r["Q_weighted_entropy"] > 0]
avg_q_weighted = float(np.mean(q_weighted_entropies)) if q_weighted_entropies else 0.0

# Lifetime correlation (exclude infinite lifetime)
finite_lt = [(r["mass_GeV"], r["normalized_entropy"],
              r["lifetime_s"], r["n_channels"])
             for r in multi_ch if r.get("lifetime_s") is not None]

if len(finite_lt) > 2:
    log_lifetimes = [math.log10(lt) for _, _, lt, _ in finite_lt]
    h_norms_lt = [h for _, h, _, _ in finite_lt]
    masses_lt = [m for m, _, _, _ in finite_lt]

    # H_norm vs log(lifetime)
    r_lt, p_lt = stats.pearsonr(log_lifetimes, h_norms_lt)
    # H_norm vs mass
    r_mass, p_mass = stats.pearsonr(masses_lt, h_norms_lt)
else:
    r_lt, p_lt = 0.0, 1.0
    r_mass, p_mass = 0.0, 1.0

# ---------------------------------------------------------------------------
# 5. Print results
# ---------------------------------------------------------------------------
print("=" * 72)
print("PDG Kinematic Phase Space Entropy Analysis")
print("=" * 72)
print(f"\nTotal particles analyzed: {len(results)}")
print(f"Particles with >1 channel: {len(multi_ch)}")
print(f"Hadronic-dominant particles: {len(hadronic_particles)}")
print()

print("Per-particle results (multi-channel only):")
print(f"{'Particle':<18} {'Mass':>8} {'n_ch':>5} {'H(bits)':>8} {'H_norm':>7} {'avg_Q':>8}")
print("-" * 60)
for r in sorted(multi_ch, key=lambda x: x["mass_GeV"]):
    print(f"{r['particle']:<18} {r['mass_GeV']:>8.4f} {r['n_channels']:>5d} "
          f"{r['shannon_entropy_bits']:>8.4f} {r['normalized_entropy']:>7.4f} "
          f"{r['avg_Q_GeV']:>8.4f}")

print()
print("Aggregate Statistics:")
print(f"  Mean H_norm (all multi-ch):       {avg_H_norm:.6f}")
print(f"  Std  H_norm:                      {std_H_norm:.6f}")
print(f"  Median H_norm:                    {median_H_norm:.6f}")
print(f"  Mean H_norm (hadronic-dominant):   {avg_H_norm_hadronic:.6f}")
print(f"  Channel-weighted H_norm:           {weighted_H_norm:.6f}")
print(f"  Mean H_norm (>=3 channels):        {avg_H_norm_rich:.6f}")
print(f"  Mean Q-weighted entropy:           {avg_q_weighted:.6f}")
print(f"  N particles (>=3 ch):              {len(rich_ch)}")
print()
print("Correlations:")
print(f"  H_norm vs log10(lifetime):  r = {r_lt:.4f}, p = {p_lt:.4e}")
print(f"  H_norm vs mass:             r = {r_mass:.4f}, p = {p_mass:.4e}")

# ---------------------------------------------------------------------------
# 6. Save results
# ---------------------------------------------------------------------------
output = {
    "metadata": {
        "description": "PDG Kinematic Phase Space Entropy (List2 #3)",
        "date": "2026-04-10",
        "source": "PDG 2024 Review of Particle Physics",
        "n_particles_total": len(results),
        "n_particles_multi_channel": len(multi_ch),
        "n_hadronic_dominant": len(hadronic_particles),
    },
    "aggregate": {
        "mean_normalized_entropy_all": round(avg_H_norm, 6),
        "std_normalized_entropy_all": round(std_H_norm, 6),
        "median_normalized_entropy_all": round(median_H_norm, 6),
        "mean_normalized_entropy_hadronic": round(avg_H_norm_hadronic, 6),
        "channel_weighted_normalized_entropy": round(weighted_H_norm, 6),
        "mean_normalized_entropy_rich_ge3ch": round(avg_H_norm_rich, 6),
        "mean_Q_weighted_entropy": round(avg_q_weighted, 6),
        "n_particles_rich_ge3ch": len(rich_ch),
        "correlation_H_vs_log_lifetime": {
            "pearson_r": round(r_lt, 6),
            "p_value": float(f"{p_lt:.6e}"),
        },
        "correlation_H_vs_mass": {
            "pearson_r": round(r_mass, 6),
            "p_value": float(f"{p_mass:.6e}"),
        },
    },
    "per_particle": sorted(results, key=lambda x: x["mass_GeV"]),
}

OUT_PATH = Path(__file__).parent / "pdg_kinematic_entropy_results.json"
with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2, default=str)
print(f"\nResults saved to {OUT_PATH}")
