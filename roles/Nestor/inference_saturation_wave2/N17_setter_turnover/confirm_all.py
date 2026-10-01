"""N17d: re-assay ALL N17c screen hits (not only the top 40) on a fresh 400-interaction panel to count true
supercritical one-byte neighbours of 7ae3 (RAND contexts, random side, copy errors off), plus a ZERO-context
column. Converts the count into a per-birth production rate under the world's copy-error rule.
Static single interactions only."""
import json, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C
from neighbours import panel, mrate, NS

NC = 400


def zero_panel(pan):
    return [(y, s, C.ZERO, C.ZERO) for y, s, _a, _b in pan]


def work(chunk):
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    cp = panel("N17d-confirm", NC, r.L)
    zp = zero_panel(cp)
    out = []
    for p, v in chunk:
        g = bytearray(F); g[p] = v; g = bytes(g)
        m, k = mrate(r, g, cp)
        mz, _ = mrate(r, g, zp)
        out.append((p, v, m, mz))
    return out


if __name__ == "__main__":
    t0 = time.time()
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    span = panel("N17c-screen", NS, r.L)
    f_s, _ = mrate(r, F, span)
    # rebuild the screen (cheap enough to recompute rather than trust a cap)
    from neighbours import work as screen_work
    with mp.Pool(6) as pool:
        rows = [x for part in pool.map(screen_work, range(64)) for x in part]
        hits = [(p, v) for p, v, m, k in rows if m >= f_s + 0.15]
        chunks = [hits[i::6] for i in range(6)]
        res = [x for part in pool.map(work, chunks) for x in part]
    cp = panel("N17d-confirm", NC, r.L)
    f_c, _ = mrate(r, F, cp)
    f_z, _ = mrate(r, F, zero_panel(cp))
    se = 0.035  # approx SE of m over 400 interactions (m in {0,1,2})
    sc = [x for x in res if x[2] >= f_c + 0.15]
    sc_gt1 = [x for x in res if x[2] > 1.1]
    by_pos = {}
    for p, v, m, mz in sc:
        by_pos.setdefault(p, []).append("%02x" % v)
    copy_mut = r.copy_mut
    out = {"founder_m_RAND": f_c, "founder_m_ZERO": f_z, "n_screen_hits": len(hits),
           "n_supercrit_ge_founder+0.15": len(sc), "n_m_gt_1.1": len(sc_gt1),
           "positions": {str(p): vs for p, vs in sorted(by_pos.items())},
           "mean_m_supercrit_RAND": sum(x[2] for x in sc) / max(1, len(sc)),
           "mean_m_supercrit_ZERO": sum(x[3] for x in sc) / max(1, len(sc)),
           "copy_mut": copy_mut,
           "onebit_supercrit": [{"pos": p, "val": "%02x" % v, "m_RAND": m} for p, v, m, mz in sc if bin(v ^ F[p]).count("1") == 1],
           "per_copied_byte_flip_rate": copy_mut,
           "per_birth_rate_to_supercrit_via_copy_error": copy_mut * sum(1 for p, v, m, mz in sc if bin(v ^ F[p]).count("1") == 1) / 8.0,
           "note": "z8.py:413-417: a copy error is a SINGLE BIT FLIP (v ^= 1<<randrange(8)), so only one-bit neighbours are reachable by copy error; rate = copy_mut x n_onebit_sc / 8 per copy of the genome. In-place _mutate reaches only W2-3's mutable positions.",
           "rows": [{"pos": p, "val": "%02x" % v, "m_RAND": m, "m_ZERO": mz} for p, v, m, mz in res],
           "wall_s": round(time.time() - t0, 1)}
    (HERE / "confirm_all.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
