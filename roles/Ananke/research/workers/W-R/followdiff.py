"""W-R SECONDARY (not in PLAN s2 wording; LOG A14): the PLAN s2 phase-effect rule applied to the
follow census (lens_swap.census_follow patterns) for the abstainers 78f3b0ec, e06701a5, whose frozen
census is UNDEFINED. Same bootstrap as fork.phase_diff_boot (2000 pair draws, 99%).
python followdiff.py <spec> [...] -> out/followdiff_<spec>.json"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import fork
from posthoc import load_raw

NOT_RUN = fork.NOT_RUN


def follow_table(n_s0, site_s0, chan_s0, scored, trials):
    """Pattern table exactly as lens_swap.census_follow (sign-based)."""
    Mw, nt = n_s0.shape
    tr = np.zeros(nt, bool); tr[list(trials)] = True
    sg = np.sign
    A, B = slice(0, None, 2), slice(1, None, 2)
    nA, nB = sg(n_s0[A]), sg(n_s0[B])
    ran = (site_s0 != NOT_RUN) & (chan_s0 != NOT_RUN)
    ok = (nA != nB) & tr[None] & scored[A] & ran[A] & ran[B]
    sA, sB, cA, cB = sg(site_s0[A]), sg(site_s0[B]), sg(chan_s0[A]), sg(chan_s0[B])
    code = lambda v, own, par: np.where(v == par, "P", np.where(v == own, "O", "?"))
    key = np.char.add(np.char.add(code(sA, nA, nB), code(sB, nB, nA)), np.char.add(code(cA, nA, nB), code(cB, nB, nA)))
    pat = np.full(ok.shape, "X", dtype="<U3")
    pat[key == "PPOO"] = "S"; pat[key == "OOPP"] = "C"; pat[(key == "OPOP") | (key == "POPO")] = "N"
    return {"ok": ok, "pat": pat}


def diff_boot(t0, t1, P, n_boot=2000, seed=1, alpha=0.01):
    def fr(tab, pairs):
        ok = tab["ok"][pairs]
        if ok.sum() == 0:
            return None
        pat = tab["pat"][pairs][ok]
        return {x: float(np.mean(pat == x)) for x in "SCN"}
    a, b = fr(t0, np.arange(P)), fr(t1, np.arange(P))
    res = {f"d{x}": b[x] - a[x] for x in "SCN"}
    rng = np.random.default_rng(seed)
    bs = {x: [] for x in "SCN"}
    for _ in range(n_boot):
        pr = rng.integers(P, size=P)
        a2, b2 = fr(t0, pr), fr(t1, pr)
        if a2 is None or b2 is None:
            continue
        for x in bs:
            bs[x].append(b2[x] - a2[x])
    res["ci99"] = {f"d{x}": (float(np.quantile(v, alpha / 2)), float(np.quantile(v, 1 - alpha / 2))) for x, v in bs.items()}
    return res, int(t0["ok"].sum()), int(t1["ok"].sum())


def run(name):
    d, normal, ns0, scored, site, chan, s0s, s0c = load_raw(name)
    P = normal.shape[0] // 2
    out = {}
    for o in d["offsets"]:
        st = fork.strata(d["trials"], o, d["Pd"], d["strat_period"])
        t0 = follow_table(ns0, s0s[o], s0c[o], scored, st[0])
        t1 = follow_table(ns0, s0s[o], s0c[o], scored, st[1])
        diff, n0, n1 = diff_boot(t0, t1, P)
        m = d["offsets_res"][str(o)]
        out[str(o)] = {"diff": diff, "n0": n0, "n1": n1, "phase_effect": fork.phase_effect(diff, n0, n1),
                       "classes_follow": [m[q]["follow"]["class"] for q in ("pooled", "q0", "q1")],
                       "n_check": [m["q0"]["follow"]["eligible"], m["q1"]["follow"]["eligible"]]}
        dd = diff
        print(name, o, out[str(o)]["classes_follow"], "eff" if out[str(o)]["phase_effect"] else "",
              " ".join(f"d{x}{dd[f'd{x}']:+.2f}[{dd['ci99'][f'd{x}'][0]:+.2f},{dd['ci99'][f'd{x}'][1]:+.2f}]" for x in "SCN"),
              "n", n0, n1, out[str(o)]["n_check"], flush=True)
    (HERE / f"out/followdiff_{name}.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        run(n)
