"""K1 (frame B, channel): is 'core conservation' purifying selection on ESSENTIAL positions, or the
transparency profile of the per-interaction channel (which positions the pair map transmits verbatim,
and which the in-place noise can reach)?

Channel frame prediction: final founder-material retention at position p in the 27 C-CORE runaways
tracks (a) T(p) = P(product[p] == x[p] | x converted a partner) and (b) whether p is reachable by the
in-place OPERAND mutation (_mutate skips instruction-start bytes only), NOT essentiality E(p).
Selection frame: retention tracks E(p) (measured in the realized field).
Everything here is single interactions in 7ae3's own C-CORE cell (stock VM, atlas_axis NONE) plus
reading c_core/results/*.json. Copy errors ON at the cell's rate for T (they are part of the channel).
"""
import json
import random
import statistics as st
import time

import common as C
spearman = C.spearman

N = 300          # partners per context for T
NKO = 40         # partners per knockout value for E
KOV = 3          # random replacement values per position


def main():
    t0 = time.time()
    r = C.runner_for_spec(C.run_ds.DONOR)
    x = C.run_ds.donor_genome()
    n = r.L
    # 1. which positions can in-place mutation reach? (empirical, the world's own _mutate)
    hits = [0] * n
    for _ in range(20000):
        g = r._mutate(x)
        for p in range(n):
            hits[p] += g[p] != x[p]
    mutable = [h > 0 for h in hits]
    # 2. channel transparency T(p) from 7ae3's source side (side 1) against random partners
    T = {}
    rng = random.Random("K1-T")
    for cm in ("ZERO", "RAND"):
        same, k = [0] * n, 0
        for _ in range(N):
            y = C.rand_genome(rng, n)
            sx = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
            sy = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
            o = C.outcome(r, x, y, 1, sx, sy, r.copy_mut, rng)
            if o["conv"]:
                k += 1
                for p in range(n):
                    same[p] += o["ny"][p] == x[p]
        T[cm] = {"n_conv": k, "T": [s / max(k, 1) for s in same]}
    # 3. essentiality E(p): drop in side-1 conversion rate when byte p is replaced (copy errors off)
    E = {}
    rng = random.Random("K1-E")
    for cm in ("ZERO", "RAND"):
        ys = [(C.rand_genome(rng, n), C.rand_ctx(rng), C.rand_ctx(rng)) for _ in range(NKO)]

        def rate(g):
            c = 0
            for y, sx, sy in ys:
                if cm == "ZERO":
                    sx = sy = C.ZERO
                c += C.outcome(r, g, y, 1, sx, sy, 0.0, rng)["conv"]
            return c / len(ys)
        base = rate(x)
        e = []
        for p in range(n):
            drops = []
            for v in random.Random("KOV%d" % p).sample([b for b in range(256) if b != x[p]], KOV):
                g = bytearray(x)
                g[p] = v
                drops.append(base - rate(bytes(g)))
            e.append(max(0.0, st.mean(drops)) / max(base, 1e-9))
        E[cm] = {"base": base, "E": e}
    # 4. retention from the frozen C-CORE records
    rs = [json.loads(f.read_text()) for f in (C.CAMP / "c9x-explore-2026-09-24" / "c_core" / "results").glob("*.json")]
    run = [q for q in rs if q["depth"] >= 20 and q["anc0_share"] >= 0.9]
    ret = [st.mean(q["freq"][p] for q in run) for p in range(n)]
    adv2_ess = {2, 22, 23, 24, 34, 43, 45, 46, 52, 53}
    res = {"n_runaways": len(run), "mutable_positions": [p for p in range(n) if mutable[p]],
           "mutate_hits": hits, "retention": [round(v, 4) for v in ret], "T": T, "E": E}
    corr = {}
    for cm in ("ZERO", "RAND"):
        corr["rho_ret_T_" + cm] = spearman(ret, T[cm]["T"])
        corr["rho_ret_E_" + cm] = spearman(ret, E[cm]["E"])
    corr["rho_ret_adv2_ess"] = spearman(ret, [float(p in adv2_ess) for p in range(n)])
    corr["rho_ret_immune"] = spearman(ret, [float(not m) for m in mutable])
    # 2x2: essential (E_ZERO >= 0.5) x immune
    tab = {}
    for e in (True, False):
        for im in (True, False):
            ps = [p for p in range(n) if (E["ZERO"]["E"][p] >= 0.5) == e and (not mutable[p]) == im]
            tab["ess=%s,immune=%s" % (e, im)] = {"n": len(ps), "mean_ret": round(st.mean(ret[p] for p in ps), 3) if ps else None,
                                                  "pos": [(p, round(ret[p], 2), round(T["RAND"]["T"][p], 2)) for p in ps]}
    res["corr"] = corr
    res["table"] = tab
    res["cpu_s"] = round(time.time() - t0, 1)
    (C.HERE / "k1_channel_retention.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({"corr": corr, "table": tab, "mutable": res["mutable_positions"],
                      "nconv": {k: v["n_conv"] for k, v in T.items()}, "Ebase": {k: v["base"] for k, v in E.items()},
                      "cpu": res["cpu_s"]}, indent=1))
    print("T<0.9 (RAND):", [(p, round(T["RAND"]["T"][p], 2), round(ret[p], 2)) for p in range(n) if T["RAND"]["T"][p] < 0.9])
    print("E>=0.5 (ZERO):", [(p, round(E["ZERO"]["E"][p], 2), round(ret[p], 2)) for p in range(n) if E["ZERO"]["E"][p] >= 0.5])
    print("E>=0.5 (RAND):", [(p, round(E["RAND"]["E"][p], 2), round(ret[p], 2)) for p in range(n) if E["RAND"]["E"][p] >= 0.5])


if __name__ == "__main__":
    main()
