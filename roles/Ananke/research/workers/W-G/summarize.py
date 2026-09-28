"""Apply PLAN.md rules to out/<ns>/*.json -> out/<ns>_summary.json + table."""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ALPHA = 0.01
PROBES = ["BLANK", "PING", "CLEAR_S0", "CLEAR_FAST", "RELOC"]


def holm(pv: dict) -> dict:
    items = sorted(pv.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        adj[k] = run
    return adj


def main(ns):
    d = HERE / "out" / ns
    rs = {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json"))}
    spec = {k: v for k, v in rs.items() if not k.startswith("C-")}
    ctrl = {k: v for k, v in rs.items() if k.startswith("C-")}
    fam2 = holm({(n, dd): r["decoders"][dd]["p"] for n, r in spec.items() for dd in ("D1", "D2")})
    famP = holm({n: r["decoders"]["PAIR"]["p"] for n, r in spec.items()})
    fam3 = holm({n: r["L3"]["p"] for n, r in spec.items()})
    fam4 = holm({(n, p): r["probes"][p]["p"] for n, r in spec.items() for p in PROBES})
    out = {}

    def verdict(n, r, adj2, adjP, adj3, adj4):
        L2 = any(adj2(dd) < ALPHA for dd in ("D1", "D2"))
        L15 = adjP < ALPHA
        L3 = adj3 < ALPHA
        dyn = [p for p in PROBES[:4] if adj4(p) < ALPHA]
        rel = adj4("RELOC") < ALPHA
        if not r["L1"]:
            cls = "NONE (no L1)"
        elif not L15:
            cls = "CHAOTIC DIVERGENCE" + ("" if not (L2 or L3 or dyn) else " (NOTE: a signed level fires; inspect)")
        elif r["sufficient_stores"]:
            hr = r["hist_ratio"]
            cls = ("ACCUMULATION" if hr and hr["ratio"] >= 0.5 else "STATIC STORAGE") + " in " + "/".join(r["sufficient_stores"])
        else:
            cls = "REGENERATION/DISTRIBUTED"
        return {"L1": r["L1"], "L1_persistent": r["L1_persistent"], "L1.5": L15, "L2": L2, "L3": L3,
                "L4_dyn": dyn, "L4_readout": rel, "class": cls,
                "nontrivial_candidate": bool((L3 or dyn) and not cls.startswith("CHAOTIC"))}

    for n, r in spec.items():
        v = verdict(n, r, lambda dd: fam2[(n, dd)], famP[n], fam3[n], lambda p: fam4[(n, p)])
        v["adj"] = {"D1": fam2[(n, "D1")], "D2": fam2[(n, "D2")], "PAIR": famP[n], "L3": fam3[n],
                    **{p: fam4[(n, p)] for p in PROBES}}
        out[n] = v
    for n, r in ctrl.items():   # unadjusted alpha
        v = verdict(n, r, lambda dd: r["decoders"][dd]["p"], r["decoders"]["PAIR"]["p"], r["L3"]["p"],
                    lambda p: r["probes"][p]["p"])
        v["raw"] = {"D1": r["decoders"]["D1"]["p"], "D2": r["decoders"]["D2"]["p"],
                    "PAIR": r["decoders"]["PAIR"]["p"], "L3": r["L3"]["p"],
                    **{p: r["probes"][p]["p"] for p in PROBES}}
        out[n] = v
    (HERE / "out" / f"{ns}_summary.json").write_text(json.dumps(out, indent=1))
    for n, v in out.items():
        r = rs[n]
        print(f"{n:14s} L1={int(v['L1'])}{'p' if v['L1_persistent'] else ' '} ndiff={list(r['ndiff_pairs_end_trial_k+j'].values())}"
              f" L1.5={int(v['L1.5'])} L2={int(v['L2'])} L3={int(v['L3'])} L4dyn={v['L4_dyn']} L4rd={int(v['L4_readout'])}"
              f" | {v['class']} | cand={v['nontrivial_candidate']} guards={all(r['guards'].values())}")
    print("ANY nontrivial candidate:", [n for n, v in out.items() if v["nontrivial_candidate"] and not n.startswith("C-")])


if __name__ == "__main__":
    main(sys.argv[1])
