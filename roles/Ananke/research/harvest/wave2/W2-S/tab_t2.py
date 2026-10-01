"""Tabulate Task 2 -> out/t2_table.md. Classification per PLAN A1/A2 (competent = 32-pair overall lo99>.55 AND chg lo99>.55)."""
import json, glob, pathlib, gzip, collections
O = pathlib.Path(__file__).parent / "out"
ROOT = pathlib.Path(__file__).resolve().parents[6]
rows = {json.loads(l)["cell_id"]: json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")}
und = open(O / "undecided.txt").read().split(",")
res = collections.defaultdict(list)
for f in glob.glob(str(O / "t2_*.json")):
    if "RC" in f: continue
    for r in json.load(open(f))["rows"]:
        res[r["cell"]].append(r)
ALLR = {r["cell"]: r for f in ("t2_ALL_a.json", "t2_ALL_b.json") for r in json.load(open(O / f))["rows"]}
ALLXR = {r["cell"]: r for f in ("t2_ALLX_a.json", "t2_ALLX_b.json") for r in json.load(open(O / f))["rows"]}
def acts(cid):
    p = rows[cid]["physics"]; a = []
    if p["decay_shift"] > 0: a.append("D")
    if p["loss"] > 0: a.append("L")
    if p["cap"] > 0: a.append("C")
    if p["update_mode"] != "sync" or p["update_period"] != 1: a.append("U")
    if p["lat_jitter"] > 0: a.append("J")
    x = list(a)
    if any(p[k] for k in ("e_income", "c_emit", "c_op", "c_mem")): x.append("E")
    if p["noise"] > 0 or p["dup"] > 0: x.append("N")
    return a, x
def comp(r): return r["M"] == 64 and r["lo99"] > .55 and r["chg_lo99"] > .55
def scr(r): return r["lo99"] > .52 and r["chg"] > .55
def find(cid, dials, M):
    for r in res[cid]:
        if r["dials"] == dials and r["M"] == M: return r
CLASS = {}
for cid in und:
    rr = res[cid]; act, ax = acts(cid)
    all_ = ALLR[cid]; allx = ALLXR.get(cid)
    conf = [r for r in rr if comp(r)]
    singles = [r for r in conf if "+" not in r["dials"]]
    if singles:
        b = "/".join(sorted(r["dials"] for r in singles)); CLASS[cid] = ("single", b)
    elif conf:
        b = min(conf, key=lambda r: len(r["dials"]))["dials"]; CLASS[cid] = ("joint", b)
    elif all_ and scr(all_):
        CLASS[cid] = ("joint-screen", "ALL5")
    elif allx and scr(allx):
        CLASS[cid] = ("joint-screen", "ALL5+E/N")
    else:
        CLASS[cid] = ("inadequate", "-")
def placement(kind, b):
    if kind == "inadequate": return "UNDECIDED (plant inadequate even fully lossless)"
    ds = set(b.replace("/", "+").replace("ALL5+E/N", "E").replace("ALL5", "").split("+")) - {""}
    if kind == "single" and ("E" in b.split("/")): return "PLANT-DESIGN (econ: 22-line plant out-spends income)"
    if kind == "single" and set(b.split("/")) <= {"U", "J"}: return "P-candidate (transport timing)"
    if kind == "joint-screen" and b == "ALL5+E/N": return "PLANT-DESIGN/P joint incl. econ (screen only)"
    if kind == "joint-screen": return "joint (screen only; unconfirmed at 32 pairs)"
    return "joint " + b + (" (timing+loss: P-or-PLANT-DESIGN)" if "L" in b else "")
L = ["| cell | topo/update | env d/dl/b | active (+ext) | ALL5 screen acc [lo99] chg | ALLX screen | competent configs (32 pairs) | binding | placement |", "|---|---|---|---|---|---|---|---|---|"]
cnt = collections.Counter()
for cid in sorted(und, key=lambda c: (CLASS[c][0], c)):
    rr = res[cid]; act, ax = acts(cid); p = rows[cid]["physics"]; e = rows[cid]["env"]
    all_ = ALLR[cid]; allx = ALLXR.get(cid)
    conf = "; ".join(f"{r['dials']} {r['acc']:.3f}/{r['chg']:.3f}[{r['chg_lo99']:.3f}]" for r in rr if comp(r)) or "-"
    k, b = CLASS[cid]; pl = placement(k, b); cnt[pl] += 1
    ax_s = f"{allx['acc']:.3f} [{allx['lo99']:.3f}] {allx['chg']:.3f}" if allx else "n/a"
    L.append(f"| {cid[:8]} | {p['topology']} {p['update_mode']}{'' if p['update_period'] == 1 else ' p' + str(p['update_period'])} | {e['d']}/{e['delta']}/{e['block']} | {''.join(act)}{('+' + ''.join(d for d in ax if d not in act)) if ax != act else ''} | {all_['acc']:.3f} [{all_['lo99']:.3f}] {all_['chg']:.3f} | {ax_s} | {conf} | {k}: {b} | {pl} |")
(O / "t2_table.md").write_text("\n".join(L) + "\n\nCounts: " + json.dumps(cnt, indent=1) + "\n")
print("\n".join(L)); print(json.dumps(cnt, indent=1))
