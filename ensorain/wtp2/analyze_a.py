"""Wave A analysis: per-world (prereg) and per-founder-lineage (A7) fractions,
detector fire rates against their named null twins. Writes runs/wtp02/waveA_summary.json."""
import collections
import json
import os

import numpy as np

from ensorain.wtp.genome import ghash
from .detect2 import DETS, NULL, fires, null_fires, refs_from

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp02")


def _f(x):
    return x if x is not None and np.isfinite(x) else float("nan")


def lineage_roots(rows):
    """Map each admitted genome hash -> root founder hash via meta.parents."""
    par = {}
    for r in rows:
        m = r["genome"].get("meta", {})
        ps = m.get("parents") or []
        par[r["genome_hash"]] = ps[0] if (m.get("strategy", "").startswith("mutate") and ps) else None
    adm = json.load(open(os.path.join(OUT, "waveA_admission.json")))["admitted"]
    for a in adm:  # admitted-but-unsampled parents still carry lineage
        h = ghash(a["g"])
        if h not in par:
            m = a["g"].get("meta", {})
            ps = m.get("parents") or []
            par[h] = ps[0] if (m.get("strategy", "").startswith("mutate") and ps) else None

    def root(h, depth=0):
        p = par.get(h)
        return h if p is None or depth > 200 else root(p, depth + 1)
    return {r["genome_hash"]: root(r["genome_hash"]) for r in rows}


def main():
    rows = json.load(open(os.path.join(OUT, "waveA.json")))
    units = [r["unit"] for r in rows]
    refs = refs_from(units)
    roots = lineage_roots(rows)
    st = collections.Counter(u["real"].get("status") for u in units)

    def pos(u, tw="real"):
        r, s = u[tw], u["shuffled"]
        c, cs = _f(r.get("CGu")), _f(s.get("CGu"))
        ok = r.get("status") == "OK"
        return ok and np.isfinite(c) and c >= 0.10, ok and np.isfinite(c) and np.isfinite(cs) and c - cs >= 0.10

    per = []
    for r, u in zip(rows, units):
        cg, sd = pos(u)
        per.append(dict(h=r["genome_hash"], root=roots[r["genome_hash"]], cgu=cg, sd=sd, both=cg and sd,
                        CGu=_f(u["real"].get("CGu")), CGu_sh=_f(u["shuffled"].get("CGu")),
                        sub=r["genome"]["substrate"]["gen"], band=r["genome"]["memory"]["band"],
                        strat=r["genome"]["meta"]["strategy"].split(":")[0]))
    n = len(per)
    ok = [p for p in per if np.isfinite(p["CGu"])]
    sh_pos = sum(1 for u in units if u["shuffled"].get("status") == "OK" and _f(u["shuffled"].get("CGu")) >= 0.10)
    lin = collections.defaultdict(list)
    for p in per:
        lin[p["root"]].append(p)
    lin_pos = {k: any(p["both"] for p in v) for k, v in lin.items()}
    lin_cgu = {k: any(p["cgu"] for p in v) for k, v in lin.items()}
    det = {}
    for d in DETS:
        rf = sum(fires(d, u, refs)[1] for u in units)
        nf = sum(null_fires(d, u, refs)[1] for u in units)
        linf = len({roots[r["genome_hash"]] for r, u in zip(rows, units) if fires(d, u, refs)[1]})
        det[d] = dict(real=rf, null=nf, null_twin=NULL[d], lineages=linf)
    by = lambda key: {k: dict(n=len(v), both=sum(p["both"] for p in v), cgu=sum(p["cgu"] for p in v))
                      for k, v in sorted(collections.defaultdict(list, {kk: [p for p in per if p[key] == kk]
                                                                         for kk in {p[key] for p in per}}).items(),
                                         key=lambda kv: str(kv[0]))}
    cg = np.array([p["CGu"] for p in ok])
    summ = dict(
        n_worlds=n, real_status=dict(st), refs=refs,
        per_world=dict(cgu_ge_01=sum(p["cgu"] for p in per), sd_ge_01=sum(p["sd"] for p in per),
                       both=sum(p["both"] for p in per), frac_both=sum(p["both"] for p in per) / n,
                       shuffled_cgu_ge_01=sh_pos),
        per_lineage=dict(n_lineages=len(lin), both=sum(lin_pos.values()), cgu=sum(lin_cgu.values()),
                         frac_both=sum(lin_pos.values()) / len(lin),
                         median_within_lineage_frac=float(np.median([np.mean([p["both"] for p in v]) for v in lin.values()])),
                         largest=max(len(v) for v in lin.values())),
        CGu_quantiles={q: float(np.quantile(cg, q)) for q in (0.01, 0.1, 0.5, 0.9, 0.99, 1.0)} if len(cg) else {},
        detectors=det, by_substrate=by("sub"), by_band=by("band"), by_strategy=by("strat"),
        positives=sorted([p for p in per if p["both"]], key=lambda p: -p["CGu"])[:40])
    json.dump(summ, open(os.path.join(OUT, "waveA_summary.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in summ.items() if k != "positives"}, indent=1, default=float))
    for p in summ["positives"][:15]:
        print(p)


if __name__ == "__main__":
    main()
