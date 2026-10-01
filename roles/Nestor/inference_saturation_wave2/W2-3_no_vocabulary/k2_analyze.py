"""Summarize k2_side_symmetry.json."""
import json
import statistics as st

import common as C

d = json.loads((C.HERE / "k2_side_symmetry.json").read_text())
rows = d["rows"]


spearman = C.spearman


res = {}
for cm in ("ZERO", "RAND"):
    c_star, i_wrong, mb, ma, pred_ma, sstar, surv = [], [], [], [], [], [], {True: [], False: []}
    two_sided = 0
    for x in rows[:-1]:
        s = x[cm]
        c0, c1 = s["0"]["conv"], s["1"]["conv"]
        if max(c0, c1) < 0.05:
            continue
        if min(c0, c1) >= 0.05:
            two_sided += 1
        ss = 0 if c0 >= c1 else 1
        sstar.append(ss)
        c_star.append(s[str(ss)]["conv"])
        i_wrong.append(s[str(1 - ss)]["imp"])
        mb.append((s["0"]["m_base"] + s["1"]["m_base"]) / 2)
        ma.append((s["0"]["m_atomic"] + s["1"]["m_atomic"]) / 2)
        pred_ma.append(1 + s[str(ss)]["conv_prom"] / 2)
        if ss == 0 and s["0"]["pre"] > 0:
            surv[bool(x["state_free"])].append(s["0"]["post_given_pre"] / s["0"]["pre"])
    n = len(c_star)
    diff = [a - b for a, b in zip(i_wrong, c_star)]
    res[cm] = {
        "n_converting_copiers": n, "two_sided": two_sided, "side0_source": sstar.count(0), "side1_source": sstar.count(1),
        "c_star_median": st.median(c_star), "i_wrong_median": st.median(i_wrong),
        "i_minus_c_median": st.median(diff), "i_minus_c_IQR": [sorted(diff)[n // 4], sorted(diff)[3 * n // 4]],
        "spearman_i_c": spearman(i_wrong, c_star),
        "m_base_median": st.median(mb), "m_base_IQR": [sorted(mb)[n // 4], sorted(mb)[3 * n // 4]],
        "m_base_share_in_0.9_1.1": sum(0.9 <= v <= 1.1 for v in mb) / n,
        "m_base_max": max(mb), "m_base_min": min(mb),
        "m_atomic_median": st.median(ma), "m_atomic_minus_pred_median": st.median([a - b for a, b in zip(ma, pred_ma)]),
        "side0_product_survival_statefree": (st.mean(surv[True]) if surv[True] else None, len(surv[True])),
        "side0_product_survival_notfree": (st.mean(surv[False]) if surv[False] else None, len(surv[False])),
    }
x7 = rows[-1]
res["7ae3_own_cell"] = {cm: {s: {k: round(v, 3) for k, v in x7[cm][s].items()} for s in ("0", "1")} for cm in ("ZERO", "RAND")}
(C.HERE / "k2_summary.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
