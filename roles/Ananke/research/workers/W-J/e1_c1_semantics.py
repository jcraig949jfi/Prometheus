"""E1 (PLAN.md): C1 evolved champions by receiver semantics class."""
import gzip, json, pathlib, collections
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[5]
OUT = pathlib.Path(__file__).parent / "out"
rows = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]

def cls(ph):
    if ph["collision"] == "none" or ph["cap"] == 0:
        return "SUM"
    return "ALOHA" if ph["collision"] == "aloha" else "SAT"

rng = np.random.default_rng(0x5EF)
def boot(x, B=4000):
    x = np.asarray(x, float)
    if len(x) == 0: return (None, None, None)
    m = rng.choice(x, (B, len(x))).mean(1)
    return (float(x.mean()), float(np.quantile(m, .005)), float(np.quantile(m, .995)))

recs = []
for r in rows:
    h = r["result"].get("held")
    if not isinstance(h, dict) or "lo99" not in h:
        continue
    recs.append(dict(fam=r["env"]["family"], sem=cls(r["physics"]), cap=r["physics"]["cap"],
                     wave=r["wave"], kind=r["kind"], acc=h["acc"], lo=h["lo99"],
                     cd=h.get("comm_delta"), cdlo=h.get("comm_delta_lo99"),
                     emit=r["result"].get("held_tel", {}).get("emit_rate"),
                     coll=r["result"].get("held_tel", {}).get("collide_frac"),
                     fanout=r["physics"]["fanout"], dest=r["physics"]["dest_mode"],
                     topo=r["physics"]["topology"]))
out = {"n": len(recs), "table": {}}
for fam in ["ALL", "RELAY", "MAJ", "XOR", "FLIP", "HOLD"]:
    for sem in ["SUM", "SAT", "ALOHA"]:
        xs = [x for x in recs if (fam == "ALL" or x["fam"] == fam) and x["sem"] == sem]
        cc = [float(x["lo"] >= .6 and (x["cdlo"] or -1) > 0) for x in xs]
        out["table"][f"{fam}/{sem}"] = {"n": len(xs), "CC": boot(cc),
            "acc": boot([x["acc"] for x in xs]),
            "comm_delta": boot([x["cd"] for x in xs if x["cd"] is not None]),
            "emit": boot([x["emit"] for x in xs if x["emit"] is not None])}
for cap in (1, 2, 4):
    xs = [x for x in recs if x["sem"] == "ALOHA" and x["cap"] == cap]
    out["table"][f"ALOHA_cap{cap}"] = {"n": len(xs), "CC": boot([float(x["lo"] >= .6 and (x["cdlo"] or -1) > 0) for x in xs])}
out["waves"] = collections.Counter((x["wave"], x["kind"]) for x in recs)
out["waves"] = {f"{a}/{b}": c for (a, b), c in out["waves"].items()}
(OUT / "e1.json").write_text(json.dumps(out, indent=1))
for k, v in out["table"].items():
    f = lambda t: "NA" if t is None or t[0] is None else f"{t[0]:.3f}[{t[1]:.3f},{t[2]:.3f}]"
    print(f"{k:14s} n={v['n']:4d} CC={f(v['CC'])} " + (f"acc={f(v['acc'])} cd={f(v['comm_delta'])} emit={f(v['emit'])}" if 'acc' in v else ""))
print(out["waves"])
