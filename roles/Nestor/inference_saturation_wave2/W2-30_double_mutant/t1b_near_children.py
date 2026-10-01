"""W2-30 T1b: what are the FID>=0.9 but non-exact halves? For each focal type x on the N1000 panel (ZERO donor ctx,
copy errors off, in-place mutation off): classify every x-like half (own=keep, partner=conv) after one interaction
as exactly one of the named types {F,C3,AC,5C,C3+AC} or 'near' (FID>=0.9, not named). Per-interaction expected
counts = realized VM-damage transition matrix (BASE and ATOMIC write-back). Diff-position histogram of near halves.
Then: exact and FID m of up to 60 distinct near halves per focal type (panel[:200], both sides each = 400 calls),
weighted by how often each near genome arises."""
import json, sys, pathlib, time, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C  # noqa: E402
from t1_exact_m import G, r, n  # noqa: E402

NAMES = list(G)
INV = {g: k for k, g in G.items()}


def lab(x, h):
    if h in INV:
        return INV[h]
    return "near" if C.FID(x, h) >= 0.9 else None


def halves(x, y, s, sx, sy):
    ga, gb, sa, sb = (x, y, sx, sy) if s == 0 else (y, x, sy, sx)
    o = C.pair(r, ga, gb, sa, sb, 0.0)
    na, nb, wa, wb = o["na"], o["nb"], o["wo"][0], o["wo"][1]
    fa = na if C.promoted(ga, na, gb, wb, n) else ga
    fb = nb if C.promoted(gb, nb, ga, wa, n) else gb
    return ((na, nb), (fa, fb)) if s == 0 else ((nb, na), (fb, fa))


def m_both_sides(v, pan):
    eb = fb = 0
    k = 0
    for y, cy, cx, _s in pan:
        for s in (0, 1):
            (nx, ny), _ = halves(v, y, s, C.ZERO, cy)
            eb += (nx == v) + (ny == v)
            fb += (C.FID(v, nx) >= 0.9) + (C.FID(v, ny) >= 0.9)
            k += 1
    return eb / k, fb / k


if __name__ == "__main__":
    t0 = time.time()
    pan = panel()
    pan200 = pan[:200]
    out = {}
    for nm, x in G.items():
        T = {"BASE": collections.Counter(), "ATOMIC": collections.Counter()}
        pos = collections.Counter()
        nears = collections.Counter()
        nearpos_role = collections.Counter()
        for y, cy, cx, s in pan:
            hb, ha = halves(x, y, s, C.ZERO, cy)
            for wb, hs in (("BASE", hb), ("ATOMIC", ha)):
                for role, h in zip(("keep", "conv"), hs):
                    L = lab(x, h)
                    if L is not None:
                        T[wb][L] += 1
                        T[wb][role + ":" + L] += 1
                        if L == "near" and wb == "BASE":
                            nears[h] += 1
                            d = tuple(i for i in range(n) if h[i] != x[i])
                            for i in d:
                                pos[i] += 1
                            nearpos_role["%s_s%d" % (role, s)] += 1
        near_list = nears.most_common(60)
        cov = sum(c for _, c in near_list) / max(1, sum(nears.values()))
        ms = []
        for h, c in near_list:
            me, mf = m_both_sides(h, pan200)
            d = [i for i in range(n) if h[i] != x[i]]
            ms.append({"count": c, "ndiff": len(d), "diff_pos_head": d[:8], "has_43_45": any(i in (43, 44, 45) for i in d),
                       "m_exact": me, "m_FID": mf})
        w = sum(e["count"] for e in ms)
        out[nm] = {"per_interaction_BASE": {k: v / len(pan) for k, v in T["BASE"].items()},
                   "per_interaction_ATOMIC": {k: v / len(pan) for k, v in T["ATOMIC"].items()},
                   "near_distinct": len(nears), "near_total": sum(nears.values()), "near_role_side": dict(nearpos_role),
                   "near_diff_pos_top": pos.most_common(15), "near_sample_coverage": cov,
                   "near_m_exact_wmean": sum(e["count"] * e["m_exact"] for e in ms) / max(1, w),
                   "near_m_FID_wmean": sum(e["count"] * e["m_FID"] for e in ms) / max(1, w),
                   "near_frac_touch_43_45": sum(e["count"] for e in ms if e["has_43_45"]) / max(1, w),
                   "near_sample": ms[:15]}
        o = out[nm]
        print(nm, {k: round(v, 3) for k, v in sorted(o["per_interaction_BASE"].items())}, "distinct", o["near_distinct"],
              "cov %.2f" % cov, "near m_ex %.3f m_FID %.3f touch43-45 %.3f" % (o["near_m_exact_wmean"], o["near_m_FID_wmean"], o["near_frac_touch_43_45"]),
              "pos", o["near_diff_pos_top"][:8], o["near_role_side"], flush=True)
    out["wall_s"] = round(time.time() - t0, 1)
    (HERE / "t1b_near_children.json").write_text(json.dumps(out, indent=1))
    print("wall", out["wall_s"])
