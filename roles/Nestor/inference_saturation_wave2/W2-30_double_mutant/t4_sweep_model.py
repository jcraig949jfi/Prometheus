"""W2-30 T4: in-silico sweep timescales (no world run, no VM calls). Inputs: t1_exact_m.json (N=1000 exact m),
t2_neighbourhood.json (class/FID m, per-side conv on 400 calls), W2-24 q3_invasion.json (exact-contact placement table).
Types {F, C3, AC, C3AC, other}. Named one-bit transitions (each 0.002/8 = 2.5e-4 per birth by copy error):
F<->C3 (43 bit1), F<->AC (44 bit6), C3<->C3AC (44 bit6), AC<->C3AC (43 bit1). In-place OPERAND mutation
(per interaction, every half): only C3<->C3AC via byte 44, which is a JP operand in both (0.002*(0.45/8+0.1/256)).
'other' = all remaining copy-error / in-place leakage, sink, m_other = expected m of a one-bit copy-error child.
REGIME A (background partners; density-independent BASE branching): per-epoch mean matrix M, relative growth,
  appearance + establishment + sweep times for N=256 (pop cap of the 7ae3 cell).
REGIME B (lineage-resident; partners are lineage members, exact contact, winner-takes-both table from W2-24 q3,
  BASE write-back): stochastic N=256 random-pairing model, one interaction per organism per epoch, 2000 epochs,
  200 replicates, start all-F. Leakage to 'other' ignored in B (equal across types to first order)."""
import json, pathlib, math
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
t1 = json.load(open(HERE / "t1_exact_m.json"))
t3 = json.load(open(HERE / "t3_analysis.json"))
t2 = {x["parent"]: x for x in json.load(open(HERE / "t2_neighbourhood.json"))["rows"] if x["kind"] == "parent"}
q3 = json.load(open(HERE.parent / "W2-24_keep_variant" / "q3_invasion.json"))
TY = ["F", "C3", "AC", "C3AC", "other"]
KEY = {"F": "F", "C3": "C3", "AC": "AC", "C3AC": "C3+AC"}
u = 0.002 / 8
v_in = 0.002 * (0.45 / 8 + 0.10 / 256)
NB = {("F", "C3"), ("C3", "F"), ("F", "AC"), ("AC", "F"), ("C3", "C3AC"), ("C3AC", "C3"), ("AC", "C3AC"), ("C3AC", "AC")}
p_err = 1 - (1 - 0.002) ** 64
N = 256
out = {"u_named_per_birth": u, "v_inplace_44": v_in, "p_any_copy_error_per_birth": p_err}


def build(mkind):
    m, conv = {}, {}
    for t in TY[:4]:
        k = KEY[t]
        if mkind == "exact":
            m[t] = t1[k]["ZERO"]["m_base_exact"]; conv[t] = t1[k]["ZERO"]["conv_exact"]
        else:
            m[t] = t2[k]["m_class"]; conv[t] = (t2[k]["convF0"] + t2[k]["convF1"]) / 2
    mo = {"exact": t3["F"]["expected_m_copyerror_child"]["m_exact"], "class": t3["F"]["expected_m_copyerror_child"]["m_class"]}[mkind]
    M = np.zeros((5, 5))
    for i, a in enumerate(TY[:4]):
        keep = m[a] - conv[a]
        named_birth = {b: (u if (a, b) in NB else 0.0) for b in TY[:4]}
        named_in = {b: (v_in if {a, b} == {"C3", "C3AC"} else 0.0) for b in TY[:4]}
        leak_birth = p_err - sum(named_birth.values())
        for j, b in enumerate(TY[:4]):
            M[i, j] += conv[a] * named_birth[b] + m[a] * named_in[b]
        M[i, 4] += conv[a] * leak_birth
        M[i, i] += conv[a] * (1 - p_err) + keep - m[a] * sum(named_in.values())
    M[4, 4] = mo
    return m, conv, M


for mkind in ("class", "exact"):
    m, conv, M = build(mkind)
    lam = {t: M[i, i] for i, t in enumerate(TY)}
    res = {"m": m, "conv": conv, "M": M.round(6).tolist(), "lambda_diag": lam}
    # regime A timescales
    rF = lam["F"]
    A = {}
    for t in ("C3", "AC", "C3AC"):
        r = lam[t] / rF
        A[t] = {"rel_growth_vs_F": r,
                "sweep_epochs_1_to_N-1": (2 * math.log(N - 1) / math.log(r)) if r > 1 else None,
                "P_est_moran_approx": (1 - 1 / r) if r > 1 else 0.0}
    # appearance from an F-resident lineage of size N (births/epoch = N*conv_F)
    A["C3_mutants_per_epoch_from_F"] = N * conv["F"] * u
    A["AC_mutants_per_epoch_from_F"] = N * conv["F"] * u
    A["C3AC_mutants_per_epoch_from_C3_resident"] = N * (conv["C3"] * u + v_in)
    for t, rate in (("C3", A["C3_mutants_per_epoch_from_F"]), ("AC", A["AC_mutants_per_epoch_from_F"])):
        pe = A[t]["P_est_moran_approx"]
        A[t]["mean_epochs_to_established_mutant"] = 1 / (rate * pe) if pe > 0 else None
    r_c3ac_c3 = lam["C3AC"] / lam["C3"]
    A["C3AC_vs_C3_rel"] = r_c3ac_c3
    A["C3AC_from_C3_resident_mean_epochs_to_established"] = 1 / (A["C3AC_mutants_per_epoch_from_C3_resident"] * (1 - 1 / r_c3ac_c3)) if r_c3ac_c3 > 1 else None
    A["C3AC_sweep_over_C3_epochs"] = 2 * math.log(N - 1) / math.log(r_c3ac_c3) if r_c3ac_c3 > 1 else None
    res["regimeA"] = A
    out[mkind] = res

# REGIME B: lineage-resident stochastic model with the exact-contact placement table
idx = {"F": 0, "C3": 1, "AC": 2, "C3AC": 3}
W = np.zeros((4, 4), dtype=np.int64)   # winner when row type sits at side 0, column at side 1
lab = {"F": "F", "C3": "C3", "AC": "AC", "C3+AC": "C3AC"}
for k, v in q3["ZERO_placements"].items():
    a, b = k.split(" vs ")
    a, b = a[:-2], b[:-2]
    if a in lab and b in lab:
        assert v["BASE"][0] == v["BASE"][1]
        W[idx[lab[a]], idx[lab[b]]] = idx[lab[v["BASE"][0]]]
out["regimeB_winner_table_side0_row"] = W.tolist()
# mutation targets
bit_to = {0: [1, 2], 1: [0, 3], 2: [0, 3], 3: [1, 2]}
in_to = {1: 3, 3: 1}
rng = np.random.default_rng(20261001)
R, E = 200, 2000
first_c3ac = []
t50 = []
final = np.zeros(4)
for rep in range(R):
    pop = np.zeros(N, dtype=np.int64)
    fa = None; h = None
    for ep in range(E):
        rng.shuffle(pop)
        a, b = pop[0::2].copy(), pop[1::2].copy()
        win = W[a, b]
        # both halves -> winner; one half per pair is the converter's written copy (birth): copy errors
        new = np.concatenate([win, win])
        births = np.arange(N // 2)       # first half-array index = written copy
        e = rng.random(N // 2) < 2 * u
        if e.any():
            for k in np.nonzero(e)[0]:
                new[k] = bit_to[int(new[k])][rng.integers(2)]
        f = rng.random(N) < v_in
        if f.any():
            for k in np.nonzero(f)[0]:
                if int(new[k]) in in_to:
                    new[k] = in_to[int(new[k])]
        pop = new
        nc = int((pop == 3).sum())
        if fa is None and nc > 0:
            fa = ep
        if h is None and nc > N // 2:
            h = ep
            break
    first_c3ac.append(fa)
    t50.append(h)
fin = [x for x in t50 if x is not None]
out["regimeB"] = {"R": R, "epochs": E, "N": N,
                  "frac_reps_C3AC_majority_by_2000": len(fin) / R,
                  "median_epoch_C3AC_majority": float(np.median(fin)) if fin else None,
                  "p10_p90_epoch_C3AC_majority": [float(np.percentile(fin, 10)), float(np.percentile(fin, 90))] if fin else None,
                  "median_first_C3AC_appearance": float(np.median([x for x in first_c3ac if x is not None])) if any(x is not None for x in first_c3ac) else None}
(HERE / "t4_sweep_model.json").write_text(json.dumps(out, indent=1, default=float))
for mk in ("class", "exact"):
    print(mk, {k: round(v, 4) for k, v in out[mk]["lambda_diag"].items()})
    print(json.dumps(out[mk]["regimeA"], indent=1, default=float))
print(out["regimeB_winner_table_side0_row"], out["regimeB"])
