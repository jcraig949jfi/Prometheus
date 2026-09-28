import gzip, json, pathlib, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[5]
rows = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
rng = np.random.default_rng(0x5EF)
def cls(ph):
    if ph["collision"] == "none" or ph["cap"] == 0: return "SUM"
    return "ALOHA" if ph["collision"] == "aloha" else "SAT"
def boot(x):
    x = np.asarray(x, float); m = rng.choice(x, (4000, len(x))).mean(1)
    return (float(x.mean()), float(np.quantile(m, .005)), float(np.quantile(m, .995)), len(x))
def bdiff(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = rng.choice(a, (4000, len(a))).mean(1) - rng.choice(b, (4000, len(b))).mean(1)
    return (float(a.mean() - b.mean()), float(np.quantile(d, .005)), float(np.quantile(d, .995)))
A0 = [r for r in rows if r["wave"] == "A0"]
out = {}
for fam in ["RELAY", "MAJ", "XOR", "FLIP", "HOLD", "ALL"]:
    for stat in ["frac_contrast_pos", "acc_max", "frac_sensitive_any", "frac_emitting"]:
        d = {s: [r["result"]["gen0"][stat] for r in A0 if cls(r["physics"]) == s and (fam == "ALL" or r["env"]["family"] == fam)] for s in ("SUM", "SAT", "ALOHA")}
        out[f"{fam}/{stat}"] = {s: boot(v) for s, v in d.items()}
        out[f"{fam}/{stat}"]["SAT-SUM"] = bdiff(d["SAT"], d["SUM"])
        out[f"{fam}/{stat}"]["ALOHA-SUM"] = bdiff(d["ALOHA"], d["SUM"])
        if stat in ("frac_contrast_pos", "acc_max"):
            o = out[f"{fam}/{stat}"]
            print(f"{fam:5s} {stat:18s} SUM {o['SUM'][0]:.4f} n{o['SUM'][3]} SAT {o['SAT'][0]:.4f} ALOHA {o['ALOHA'][0]:.4f} | SAT-SUM {o['SAT-SUM'][0]:+.4f}[{o['SAT-SUM'][1]:+.4f},{o['SAT-SUM'][2]:+.4f}] ALOHA-SUM {o['ALOHA-SUM'][0]:+.4f}[{o['ALOHA-SUM'][1]:+.4f},{o['ALOHA-SUM'][2]:+.4f}]")
(pathlib.Path(__file__).parent / "out/e4.json").write_text(json.dumps(out, indent=1))
