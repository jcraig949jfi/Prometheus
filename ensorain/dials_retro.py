"""EXPLORATORY (hypothesis generation, no gate, no verdict): do two dials
act separately or through their coupling? Uses rows Ensorain already has:
full grids over stability (proximal lam: higher = more stable, less
plastic) x consolidation depth (sweeps), per world family and per memory
cap. Measures, per grid, the share of explained variance of held-out R^2
that is INTERACTION (non-additive) rather than main effects, with a
permutation null over the grid cells for the interaction share."""
import collections
import json
import numpy as np

RNG = np.random.default_rng(924)


def interaction_share(table):
    """table: dict (lam, sweeps) -> list of per-instance R^2. Two-way
    decomposition on cell medians; returns (share, null_p95, cells)."""
    lams = sorted({k[0] for k in table})
    sws = sorted({k[1] for k in table})
    M = np.array([[np.median(table[(l, s)]) for s in sws] for l in lams])
    M = np.clip(M, -1.0, 1.0)  # a diverged cell is "fails", not -1e6

    def share(A):
        g = A.mean()
        r = A.mean(1, keepdims=True) - g
        c = A.mean(0, keepdims=True) - g
        inter = A - g - r - c
        tot = ((A - g) ** 2).sum()
        return float((inter ** 2).sum() / tot) if tot > 0 else 0.0
    s = share(M)
    null = [share(RNG.permutation(M.reshape(-1)).reshape(M.shape)) for _ in range(2000)]
    return s, float(np.quantile(null, 0.95)), lams, sws, M


def load(path):
    return [json.loads(l) for l in open(path)]


def main():
    out = {}
    grids = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in load("ensorain/runs/e1p5_calibrate.jsonl"):
        if r.get("status") == "OK":
            c = r["cfg"]
            grids[f"E1.5 TT latent-order cap {r['cap']}"][(c["lam"], c["sweeps"])].append(r["r2_ho"])
    for r in load("ensorain/runs/e2_calibrate.jsonl"):
        if r.get("status") == "OK":
            g = r["gi"]
            lam = (3, 10, 30, 100)[g // 3]
            sw = (5, 10, 20)[g % 3]
            grids[f"E2 {r['family']} world, correct family"][(lam, sw)].append(r["r2_ho"])
    for name in sorted(grids):
        s, p95, lams, sws, M = interaction_share(grids[name])
        best = np.unravel_index(np.argmax(M), M.shape)
        best_lam_by_sweeps = {sw: lams[int(np.argmax(M[:, j]))] for j, sw in enumerate(sws)}
        out[name] = dict(interaction_share=round(s, 3), null_p95=round(p95, 3), coupled=s > p95,
                         best=(lams[best[0]], sws[best[1]]), best_lam_by_sweeps=best_lam_by_sweeps,
                         grid_median_r2=np.round(M, 2).tolist(), lams=lams, sweeps=sws)
        print(f"{name:40s} interaction {s:.3f} (null95 {p95:.3f}) {'COUPLED' if s > p95 else 'additive'}"
              f"  best lam|sweeps {best_lam_by_sweeps}")
    json.dump(out, open("ensorain/runs/dials_retro.json", "w"), indent=1, default=str)



def anova_interaction(table):
    """Two-way ANOVA with replication (instances within a cell): F test for
    the lam x sweeps interaction. R^2 clipped to [-1, 1] (divergence = fail).
    Also a positive control: the same test on a synthetic grid with a known
    interaction, and a negative control on a synthetic additive grid."""
    from scipy.stats import f as fdist
    lams = sorted({k[0] for k in table})
    sws = sorted({k[1] for k in table})
    n = min(len(v) for v in table.values())
    Y = np.array([[np.clip(np.array(table[(l, s)][:n]), -1, 1) for s in sws] for l in lams])  # a x b x n
    a, b = len(lams), len(sws)
    g = Y.mean()
    cell = Y.mean(2)
    ra = cell.mean(1, keepdims=True) - g
    cb = cell.mean(0, keepdims=True) - g
    ss_int = n * ((cell - g - ra - cb) ** 2).sum()
    ss_err = ((Y - cell[:, :, None]) ** 2).sum()
    df_int, df_err = (a - 1) * (b - 1), a * b * (n - 1)
    F = (ss_int / df_int) / (ss_err / df_err)
    ss_tot = ((Y - g) ** 2).sum()
    return float(F), float(1 - fdist.cdf(F, df_int, df_err)), float(ss_int / ss_tot)


def controls():
    r = np.random.default_rng(5)
    add = {(l, s): list(0.1 * i + 0.2 * j + r.normal(0, 0.2, 6)) for i, l in enumerate((3, 10, 30, 100)) for j, s in enumerate((5, 10, 20))}
    cou = {(l, s): list(0.3 * (i == j + 1) + r.normal(0, 0.2, 6)) for i, l in enumerate((3, 10, 30, 100)) for j, s in enumerate((5, 10, 20))}
    return anova_interaction(add)[1], anova_interaction(cou)[1]


def main2():
    grids = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in load("ensorain/runs/e1p5_calibrate.jsonl"):
        if r.get("status") == "OK":
            c = r["cfg"]
            grids[f"E1.5 TT latent cap {r['cap']}"][(c["lam"], c["sweeps"])].append(r["r2_ho"])
    for r in load("ensorain/runs/e2_calibrate.jsonl"):
        if r.get("status") == "OK":
            grids[f"E2 {r['family']} correct family"][((3, 10, 30, 100)[r["gi"] // 3], (5, 10, 20)[r["gi"] % 3])].append(r["r2_ho"])
    p_add, p_cou = controls()
    print(f"controls: additive grid p={p_add:.3f} (should be > .05); coupled grid p={p_cou:.2e} (should be < .05)")
    out = {"controls": dict(additive_p=p_add, coupled_p=p_cou)}
    for name in sorted(grids):
        F, p, share = anova_interaction(grids[name])
        out[name] = dict(F=round(F, 2), p=p, interaction_share_of_total=round(share, 3))
        print(f"{name:32s} F={F:6.2f} p={p:.2e} interaction share of total variance {share:.2f}")
    json.dump(out, open("ensorain/runs/dials_retro_anova.json", "w"), indent=1)


if __name__ == "__main__":
    main2()
