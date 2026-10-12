"""C-018-T020 demand gate runner (PREREG.md). One process, harry1 CPU. Writes a JSON result.

    python -m rso.aether.demand.demand_gate rso/aether/demand/demand_result.json

Stages: ancestry (P2, 5 fixtures x 4 seeds), decode (P3, 5 fixtures x 4 seeds), locality (P1: counterfeit + native),
P4 (Aether express01 tables, new surroundings seeds). Decision rules are applied by `verdicts` exactly as frozen.
"""
import itertools
import json
import sys
import time

import numpy as np

from rso.aether.demand import fixtures as F

SEEDS = (0, 1, 2, 3)


def verdict_ancestry(rows):
    if all(r["div"] < 3 for r in rows):
        return "INSUFFICIENT"
    if all(r["div"] >= 3 and r["removed_cut"] >= 0.8 and r["removed_nonanc"] <= 0.2 for r in rows):
        return "ANCESTRY_QUALIFIED"
    return "ANCESTRY_ABSENT"


def verdict_content(d, extent):
    ds = list(d["Dstat"].values())
    if all(abs(v) < 0.03 for v in ds):
        return "CONTENT_ABSENT"
    ok = all(d["min_seed_acc_by_radius"][r] >= 0.5 for r in range(1, extent)) and all(v >= 0.2 for v in ds)
    return "CONTENT_TRANSMITTED" if ok else "CONTENT_PARTIAL"


def native_locality():
    """P1 on native worlds (new seeds): max divergent Chebyshev radius vs tick for a one-bit payload impulse."""
    from observatory import aeth01_run as R
    rows = []
    for law in ("V1", "RX"):
        for k in SEEDS:
            n = 64
            f, _ = R.build_initial(R.SPARSE_SOUP, n, n, F.RNG + k, write_density=0.5, energy_mode=R.ENERGY_UNIFORM)
            s = [x.copy() for x in f]
            phys = F.PHYS + k
            for t in range(100):
                s, _ = F.T.law_step(np, F._K, law, n, phys, t + 1, s)
            act = np.argwhere((s[0] == F._K.WRITE_OPCODE) & (s[4].astype(int) >= 1))
            rng = np.random.default_rng(0xC18E0000 + k)
            y, x = (int(v) for v in act[rng.integers(0, len(act))])
            b = [q.copy() for q in s]
            p = [q.copy() for q in s]
            p[3][y, x] ^= np.uint8(1)
            dist = F.cheb_to_set(n, [(y, x)])
            ok, ratio, ever, rmax, alive = True, 0.0, 0, 0, 0
            for t in range(100, 180):
                b, _ = F.T.law_step(np, F._K, law, n, phys, t + 1, b)
                p, _ = F.T.law_step(np, F._K, law, n, phys, t + 1, p)
                dm = F.diff_mask(p, b)
                if dm.any():
                    r = int(dist[dm].max())
                    rmax = max(rmax, r)
                    ever = max(ever, int(dm.sum()))
                    ratio = max(ratio, r / (t - 99))
                    ok &= r <= (t - 99)
                    alive = t - 99
            rows.append({"law": law, "seed": k, "origin": [y, x], "light_cone_ok": bool(ok), "max_radius": rmax,
                         "peak_divergent_sites": ever, "last_divergent_tick": alive, "max_radius_over_tick": round(ratio, 3)})
    return rows


def p4_tables():
    import express01 as E
    out = {}
    for op in ("REPLACE", "XOR", "ADD"):
        for g in ("C3", "C4"):
            names = E.INPUT_NAMES[g]
            tab = E.table(g, op)
            row = {"strict_dep": {v: bool(E.depends_on(tab, names, v)) for v in names}}
            row["any_dep"] = {v: bool(E.depends_any(tab, names, v)) for v in names}
            # single-source alternatives: is the output a function of ONE input alone? is it a copy of an input?
            single = {}
            for i, v in enumerate(names):
                m = {}
                ok = True
                for k, o in tab.items():
                    if m.setdefault(k[i], o) != o:
                        ok = False
                        break
                single[v] = ok
            row["output_is_function_of_single_input"] = single
            row["output_equals_some_input"] = any(all(o == k[i] for k, o in tab.items()) for i in range(len(names)))
            row["distinct_outputs"] = len(set(tab.values()))
            row["surroundings_invariant_new_seeds"] = all(
                E.table(g, op, surround_seed=F.SURR + q) == tab for q in (0, 1))
            row["ablate_A_removes_dep_a"] = not E.depends_any(E.table(g, op, ablate=("A",)), names, "a") \
                if g == "C3" else None
            out["%s/%s" % (g, op)] = row
    return out


def main(argv):
    out_path = argv[1]
    t0 = time.time()
    res = {"schema": "prometheus.rso.aether.demand.v1", "seeds": list(SEEDS),
           "phys_base": hex(F.PHYS), "noise_base": hex(F.NOISE), "surr_base": hex(F.SURR), "rng_base": hex(F.RNG)}
    anc = {k: [F.ancestry_run(k, s) for s in SEEDS] for k in F.KINDS}
    res["ancestry"] = anc
    print("ancestry done %.0fs" % (time.time() - t0), file=sys.stderr, flush=True)
    dec = {}
    for k in F.KINDS:
        dec[k] = F.decode_kind(k, SEEDS)
        print("decode", k, dec[k]["Dstat"], dec[k]["acc_by_radius"], "%.0fs" % (time.time() - t0), file=sys.stderr, flush=True)
    res["decode"] = dec
    extent = {"A": 6, "B": 6, "E": 6, "G": 3, "N": 6}
    res["verdicts"] = {k: {"ancestry": verdict_ancestry(anc[k]), "content": verdict_content(dec[k], extent[k]),
                           "t0_sites": sorted({r["t0_sites"] for r in anc[k]})} for k in F.KINDS}
    tele = [F.ancestry_run("A", s, law="TELEPORT") for s in SEEDS]
    res["locality_counterfeit_teleport"] = [{"seed": r["seed"], "light_cone_ok": r["light_cone_ok"],
                                              "max_radius_over_tick": r["max_radius_over_tick"]} for r in tele]
    res["locality_native"] = native_locality()
    print("locality done %.0fs" % (time.time() - t0), file=sys.stderr, flush=True)
    res["p4_express01_tables"] = p4_tables()
    res["wall_seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(out_path, "w"), indent=1)
    print(json.dumps(res["verdicts"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
