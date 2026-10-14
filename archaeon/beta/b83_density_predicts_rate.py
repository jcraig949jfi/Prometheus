"""B83 -- does one-step neighbourhood density PREDICT the conversion rate? (extends B82 from n=3 to n=10; evaluation only)

B82: H_6913 has 15/1000 improving one-step mutants, all RESET-like, and converts 5/6. H_6923 has 0 and converts 1/6.
L_6916 has 0 RESET-like and converts 0/6.
Here the one-step census (1000 mutants, B82 procedure) is run for every latch whose conversion rate is known. Pooled
observed rates (populations with >= 5 RESET-like genomes / runs):
  HAND_LATCH (B76)          6/6
  H_6913 (B80+B81)          5/6      H_6923 1/6      H_6911 0/3      H_6929 (B79 6/6 + B80 1/3) 7/9
  L_6932 1/3                L_6916 0/6      L_S6913 0/6      L_6931 0/4
  LONG_LOW B69d SOLO 6924 (B79) 0/6
Caveat: B76 seeded 100 x latch_1 + 100 x latch_2; HAND_LATCH here measures latch_1 only.
PREDICTION (committed before running):
- Spearman rank correlation between the RESET-like one-step density and the observed conversion rate >= .6 over the 10
  latches;
- every latch with density 0 has an observed rate <= 1/6 (except at most one).
"""
import copy
import json
import sys
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b68_pulse_state_controls import latch, man
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
from archaeon.beta.b79_evolved_latch_start import evolved_latch
from archaeon.beta.b80_latch_quality import latch_genome

OUT = Path(__file__).resolve().parent / "results" / "B83_density"
RATES = {"HAND_LATCH": (6, 6), "H_6913": (5, 6), "H_6923": (1, 6), "H_6911": (0, 3), "H_6929": (7, 9), "L_6932": (1, 3),
         "L_6916": (0, 6), "L_S6913": (0, 6), "L_6931": (0, 4), "LONG_LOW": (0, 6)}


def genome(key):
    if key == "HAND_LATCH":
        return man(latch(1), "regs")
    if key == "LONG_LOW":
        return evolved_latch("LONG_LOW")
    return latch_genome(key)[0]


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y); n = len(x); mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** .5
    return num / den if den else 0.0


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    N = int(argv[0]) if argv else 1000
    world, s, _ = B75.load(); w = NoClock(world)
    screen = lambda m: sum(group_reloc([m], w, s + 2000 + k, 8, P=4, Q=16, mode="random")[0] for k in range(2)) / 2
    held = lambda m: sum(group_reloc([m], w, s + 1000 + k, 16, P=4, Q=16, mode="random")[0] for k in range(4)) / 4
    rows = []
    for key in RATES:
        m0 = genome(key); rec0 = G.organism_record(copy.deepcopy(m0), None, 0); ps, ph = screen(m0), held(m0)
        rng = SplitMix64(seed_from("b83", key)); improved = 0; reset_like = 0
        for i in range(N):
            child, _ = descend(rec0, rng.next_u64() & ((1 << 62) - 1)); m = child["manifest"]
            if screen(m) <= ps:
                continue
            r = held(m)
            if r <= ph:
                continue
            improved += 1
            lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
            if r - held(lk) >= .02:
                rf = B75.refind(m, w, s, world.R); reset_like += bool(rf is not None and rf >= .31)
        k_, n_ = RATES[key]
        rows.append({"latch": key, "len": len(m0["genome"]) // 4, "parent_held": round(ph, 4), "improved": improved, "reset_like": reset_like,
                     "density": reset_like / N, "rate": round(k_ / n_, 3), "runs": n_})
        print(json.dumps(rows[-1]), flush=True)
    rho = spearman([r["density"] for r in rows], [r["rate"] for r in rows])
    zero = [r for r in rows if r["reset_like"] == 0]
    summ = {"spearman": round(rho, 3), "zero_density_latches": len(zero), "zero_density_with_rate_gt_1of6": sum(r["rate"] > 1 / 6 + 1e-9 for r in zero)}
    summ["pred_rho"] = summ["spearman"] >= .6; summ["pred_zero"] = summ["zero_density_with_rate_gt_1of6"] <= 1
    print(json.dumps(summ))
    (OUT / "B83_result.json").write_text(json.dumps({"probe": "B83", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
