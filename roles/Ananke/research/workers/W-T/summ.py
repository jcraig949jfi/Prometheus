"""W-T bookkeeping: per-unit P8 / P8any accuracy (W-S analyze.accuracy: 99% pair bootstrap, 2000 draws),
coverage, shuffled must-fail, frozen decision rule (PLAN s4), and cue-traffic descriptors.
python summ.py <tag> <census frozen|follow> <unit list o:q,o:q,...> [label]"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wt  # noqa: E402  (sets paths)
import analyze as WSA  # noqa: E402

DEC_LO, COV_MIN, ANY_LO = 0.90, 0.25, 0.80


def decide(dec, cov, anyr):
    """Frozen PLAN s4 rule. Returns (verdict, failing parts)."""
    fails = []
    if dec["acc"] is None or dec["ci99"][0] <= DEC_LO:
        fails.append("P8 decisive lo99 <= .90")
    if cov < COV_MIN:
        fails.append("coverage < .25")
    if anyr["acc"] is None or anyr["ci99"][0] <= ANY_LO:
        fails.append("P8any strict lo99 <= .80")
    return ("REACHES" if not fails else "DOES NOT REACH"), fails


def unit(arr, o, q, census, shuffle_seed=0):
    ok = arr[f"ok_{census}"].astype(bool)
    sel = ok & (arr["o"] == o) & (arr["q"] == q)
    pat = arr[f"pat_{census}"][sel]
    pair = arr["pair"][sel]
    p8 = arr["P8"][sel]
    p8a = wt.p8any_of(p8)
    sc = np.isin(pat, ("S", "C"))
    dec = np.isin(p8, ("S", "C"))
    r = {"n_eligible": int(sel.sum()), "census": dict(Counter(pat.tolist())),
         "P8_strict": WSA.accuracy(p8, pat, pair),
         "P8_decisive": WSA.accuracy(p8[dec], pat[dec], pair[dec]),
         "P8_coverage": float(np.mean(dec[sc])) if sc.any() else 0.0,
         "P8_decisive_shuffled": WSA.accuracy(WSA.shuffled(p8[dec], pat[dec], shuffle_seed), pat[dec], pair[dec]),
         "P8any": WSA.accuracy(p8a, pat, pair),
         "P8any_shuffled": WSA.accuracy(WSA.shuffled(p8a, pat, shuffle_seed), pat, pair),
         "P8all_decisive": None, "xtab": None}
    p8all = arr["P8all"][sel]
    da = np.isin(p8all, ("S", "C"))
    r["P8all_decisive"] = WSA.accuracy(p8all[da], pat[da], pair[da])
    r["P8all_coverage"] = float(np.mean(da[sc])) if sc.any() else 0.0
    r["xtab"] = {f"{a}>{b}": c for (a, b), c in sorted(Counter(zip(pat.tolist(), p8.tolist())).items())}
    r["verdict"], r["fails"] = decide(r["P8_decisive"], r["P8_coverage"], r["P8any"])
    # cue-bearing traffic descriptors over S/C pair-trials (and by pattern)
    desc = {}
    for lab, m in (("all_SC", sc), ("S", pat == "S"), ("C", pat == "C"), ("N", pat == "N")):
        if not m.any():
            continue
        g = lambda k: arr[k][sel][m]
        nsrc = g("n_src_a").astype(float)
        desc[lab] = {"n": int(m.sum()),
                     "cue_copies_to_readout_mean": float(g("n_cue_a").mean()),
                     "cue_copies_to_readout_median": float(np.median(g("n_cue_a"))),
                     "src_copies_mean": float(nsrc.mean()),
                     "first_emission_copies_mean": float(g("n_src_first").mean()),
                     "share_rebroadcast": float(g("n_src_later").sum() / max(nsrc.sum(), 1)),
                     "share_relay": float(g("n_relay_a").sum() / max(g("n_cue_a").sum(), 1)),
                     "relay_inflight_mean": float(g("n_relay_flight").mean()),
                     "src_emit_ticks_mean": float(g("n_emit_src").mean()),
                     "te1_rel_hist": dict(Counter(int(x) for x in g("te1_rel"))),
                     "P8_counts": dict(Counter(g("P8").tolist()))}
    r["traffic"] = desc
    return r


def fmt(r):
    f = lambda x: "n0" if not x or x.get("acc") is None else f"{x['acc']:.3f} [{x['ci99'][0]:.3f},{x['ci99'][1]:.3f}] n{x['n']}"
    return (f"  census {r['census']}\n  P8 decisive {f(r['P8_decisive'])} cov {r['P8_coverage']:.3f} | strict {f(r['P8_strict'])}"
            f" | dec-shuf {f(r['P8_decisive_shuffled'])}\n  P8any {f(r['P8any'])} | shuf {f(r['P8any_shuffled'])}"
            f" | P8all dec {f(r['P8all_decisive'])} cov {r['P8all_coverage']:.3f}\n  xtab {r['xtab']}\n"
            f"  VERDICT {r['verdict']} {r['fails']}")


def main():
    tag, census = sys.argv[1], sys.argv[2]
    units = [tuple(int(y) for y in x.split(":")) for x in sys.argv[3].split(",")]
    label = sys.argv[4] if len(sys.argv) > 4 else tag
    arr = dict(np.load(HERE / "out" / f"rows_{tag}.npz"))
    out, lines = {}, []
    for o, q in units:
        r = unit(arr, o, q, census)
        out[f"o{o}q{q}"] = r
        lines.append(f"{label} o{o} q{q} ({census})\n" + fmt(r))
    (HERE / "out" / f"summary_{label}.json").write_text(json.dumps(out, indent=1, default=float))
    (HERE / "out" / f"summary_{label}.txt").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
