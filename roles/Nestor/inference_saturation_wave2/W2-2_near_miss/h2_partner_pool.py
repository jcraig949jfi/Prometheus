"""W2-2 h2: environmental feedback test. Does a partner pool that has already been written on by the lineage
(non-converted partners left with 7ae3 fragments by BASE write-back) change the individual law of 7ae3 under BASE?
Arms (same h1 machinery, H=60, CAP=80, G=3, 3 seeds):
  RANDOM   - partners are fresh background genomes (h1 baseline);
  TOUCHED  - partners drawn from halves that met a 7ae3-lineage individual, were NOT converted, but were changed
             (they carry lineage-written bytes) - the population a burst leaves behind;
  MIX25    - 75% RANDOM, 25% TOUCHED (a lineage ~10-30 members deep into a burst touches tens of partners).
Single interactions only (world._pair_interact). python -B h2_partner_pool.py -> h2_partner_pool.json
"""
import json, random, sys, time, statistics as st
import h1_lineage_tree as h

h.H, h.CAP, h.G = 60, 80, 3
SP = "7ae3f9c1437c8000-s54765-tL-a0"


def touched_pool(r, d, p, g0, pool, rng, n=400):
    out = []
    ctr = [500_000]
    g, stt = g0, (None, 0, 0)
    tries = 0
    while len(out) < n and tries < 20000:
        tries += 1
        pg = r._seed_genome()
        h.set_org(r, d, g0, (None, 0, 0) if rng.random() < 0.5 else stt)
        h.set_org(r, p, pg, pool[rng.randrange(len(pool))])
        d.anc, p.anc = 0, 1
        doid, poid = d.oid, p.oid
        del r.births[:]
        r.epoch = ctr[0]; ctr[0] += 1
        a, b = (d, p) if rng.randrange(2) == 0 else (p, d)
        r._pair_interact(0, a, b)
        conv = any(par == doid for par, c in r.births)
        if not conv and r._genome(p) != pg:
            out.append((r._genome(p), h.state(p)))
        stt = h.state(d)
    return out


def life_law(r, g0, rng, pool, d, p):
    ctr = [10_000]
    gen = [(g0, (None, 0, 0))] * h.CAP
    rows = []
    for k in range(h.G):
        nxt = []
        for g, st0 in gen[:h.CAP]:
            b, died = h.live(r, d, p, g, st0, pool, rng, ctr)
            rows.append(dict(gen=k, births=len(b), causal=sum(c for _, c, _, _ in b), died=died))
            nxt += [(cg, cs) for _, c, cg, cs in b]
        rng.shuffle(nxt)
        gen = nxt
        if not gen:
            break
    return rows


def main():
    t0 = time.process_time()
    out = {}
    for arm in ("RANDOM", "TOUCHED", "MIX25"):
        allrows = []
        npool = []
        for seed in (1, 2, 3):
            r, g0 = h.make(SP, "BASE", 90_000 + seed)
            rng = random.Random(repr(("W2-2-h2", arm, seed)))
            pool = h.partner_pool(r, rng)
            d = r._place(bytes(r.L), 0); p = r._place(bytes(r.L), 1)
            tp = touched_pool(r, d, p, g0, pool, rng) if arm != "RANDOM" else []
            npool.append(len(tp))
            frac = {"RANDOM": 0.0, "TOUCHED": 1.0, "MIX25": 0.25}[arm]
            orig = r._seed_genome
            r._seed_genome = (lambda orig=orig, tp=tp, frac=frac, rng=rng:
                              tp[rng.randrange(len(tp))][0] if tp and rng.random() < frac else orig())
            allrows += life_law(r, g0, rng, pool, d, p)
        m = st.mean(x["births"] for x in allrows); mc = st.mean(x["causal"] for x in allrows)
        out[arm] = dict(n=len(allrows), touched_pool_sizes=npool, mean_births=round(m, 3), mean_causal=round(mc, 3),
                        gen_means={g: round(st.mean(x["births"] for x in allrows if x["gen"] == g), 3) for g in range(h.G) if any(x["gen"] == g for x in allrows)},
                        zero_share=round(sum(x["births"] == 0 for x in allrows) / len(allrows), 3),
                        survive=round(sum(x["died"] is None for x in allrows) / len(allrows), 3))
        print(arm, out[arm], round(time.process_time() - t0), flush=True)
    out["cpu_s"] = round(time.process_time() - t0, 1)
    json.dump(out, open(h.HERE / "h2_partner_pool.json", "w"), indent=1)


if __name__ == "__main__":
    main()
