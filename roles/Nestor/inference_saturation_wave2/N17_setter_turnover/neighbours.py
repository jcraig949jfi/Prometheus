"""N17c: mutational target size for a supercritical BASE copier one byte from 7ae3.
Every single-byte variant (64 x 255) of the 7ae3 founder: m_base against random partners, random side,
RAND contexts (carried-register world), copy errors off, NS interactions on a FIXED shared panel
(common random numbers, so variant differences are not panel noise). Hits with m_base >= founder+0.15 are
re-assayed on a fresh panel of NC. Static single interactions only."""
import json, random, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C

NS, NC = 60, 400


def panel(seed, n, L):
    rng = random.Random(seed)
    return [(C.rand_genome(rng, L), rng.randrange(2), C.rand_ctx(rng), C.rand_ctx(rng)) for _ in range(n)]


def mrate(r, x, pan):
    m = k = 0
    for y, s, sx, sy in pan:
        o = C.outcome(r, x, y, s, sx, sy, 0.0, None)
        m += o["m_base"]; k += o["keep"]
    return m / len(pan), k / len(pan)


def work(p):
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    pan = panel("N17c-screen", NS, r.L)
    rows = []
    for v in range(256):
        if v == F[p]:
            continue
        g = bytearray(F); g[p] = v
        m, k = mrate(r, bytes(g), pan)
        rows.append((p, v, m, k))
    return rows


if __name__ == "__main__":
    t0 = time.time()
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    f_s, _ = mrate(r, F, panel("N17c-screen", NS, r.L))
    with mp.Pool(6) as pool:
        rows = [x for part in pool.map(work, range(64)) for x in part]
    hits = [x for x in rows if x[2] >= f_s + 0.15]
    cpan = panel("N17c-confirm", NC, r.L)
    f_c, fk_c = mrate(r, F, cpan)
    conf = []
    for p, v, m, k in sorted(hits, key=lambda t: -t[2])[:40]:
        g = bytearray(F); g[p] = v
        mc, kc = mrate(r, bytes(g), cpan)
        conf.append({"pos": p, "val": "%02x" % v, "m_screen": m, "m_confirm": mc, "keep_confirm": kc})
    by_pos = {}
    for p, v, m, k in rows:
        by_pos.setdefault(p, []).append(m)
    out = {"founder_m_screen": f_s, "founder_m_confirm": f_c, "founder_keep_confirm": fk_c,
           "n_variants": len(rows), "n_screen_hits": len(hits),
           "n_confirmed_ge_founder+0.15": sum(1 for c in conf if c["m_confirm"] >= f_c + 0.15),
           "n_confirmed_m_gt_1.1": sum(1 for c in conf if c["m_confirm"] > 1.1),
           "confirmed": conf,
           "per_pos_mean_m": {p: round(sum(v) / len(v), 3) for p, v in by_pos.items()},
           "frac_variants_m_lt_0.5": sum(1 for x in rows if x[2] < 0.5) / len(rows),
           "wall_s": round(time.time() - t0, 1)}
    (HERE / "neighbours.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_pos_mean_m",)}, indent=1))
