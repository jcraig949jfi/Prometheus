"""W2-2 a1: X-TICKET per-epoch precursors (read-only). python -B a1_ticket.py -> a1_ticket.json
traj rows: [causal_members_alive N, anc0_alive A, cumulative_causal_births B] for epochs 1..300.
Outcomes: world depth (ruler R_D), founder-lineage births B(300) (ruler R_B), anc0 occupancy A(300) (ruler R_A).
"""
import json, glob, pathlib, statistics as st
HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[1] / "campaigns" / "c9x-explore-2026-09-24"
R = [json.load(open(f)) for f in sorted(glob.glob(str(CAMP / "x_ticket" / "results" / "*.json")))]
out = {}

def cls(r):
    return "RUN" if r["depth"] >= 20 else "WIN" if r["depth"] >= 5 else "LOSE"

def g(r, e, i):  # value at end of epoch e (1-based); traj has 300 rows
    t = r["traj"]
    return t[min(e, len(t)) - 1][i] if t else 0

def dB(r, e):   # births during epoch e
    return g(r, e, 2) - (g(r, e - 1, 2) if e > 1 else 0)

rows = []
for r in R:
    t = r["traj"]
    B300, A300, N300 = g(r, 300, 2), g(r, 300, 1), g(r, 300, 0)
    last = max([e for e in range(1, 301) if dB(r, e) > 0], default=0)
    maxdb = max([dB(r, e) for e in range(1, 301)], default=0)
    first_multi = next((e for e in range(1, 301) if dB(r, e) >= 2), None)
    row = dict(s=r["s"], depth=r["depth"], cls=cls(r), B300=B300, A300=A300, N300=N300, last_birth=last,
               maxdB=maxdb, first_multi=first_multi, B1=g(r, 1, 2), N1=g(r, 1, 0))
    for e in (3, 5, 8, 10, 12, 15, 20, 30):
        row[f"B{e}"] = g(r, e, 2); row[f"N{e}"] = g(r, e, 0); row[f"A{e}"] = g(r, e, 1)
    # per-capita birth rate in windows (births / member-epochs, members at start of each epoch)
    for a, b in ((1, 5), (6, 10), (11, 15), (16, 20), (21, 30)):
        me = sum(g(r, e - 1, 0) if e > 1 else 1 for e in range(a, b + 1))
        bb = g(r, b, 2) - g(r, a - 1, 2) if a > 1 else g(r, b, 2)
        row[f"pc_{a}_{b}"] = round(bb / me, 3) if me else None
        row[f"bw_{a}_{b}"] = bb
    # concurrency: fraction of births in epochs with >=2 births (lower bound on >1 active copier)
    row["max_dB_1_10"] = max(dB(r, e) for e in range(1, 11))
    row["max_dB_11_20"] = max(dB(r, e) for e in range(11, 21))
    rows.append(row)

out["n"] = len(rows)
out["class_counts"] = {c: sum(r["cls"] == c for r in rows) for c in ("LOSE", "WIN", "RUN")}
out["deep_rows"] = [r for r in rows if r["depth"] >= 3 or r["B300"] >= 5]
# ruler disagreement: depth > founder-lineage births => depth came from outside the founder's certified lineage
out["depth_exceeds_founder_births"] = [(r["s"], r["depth"], r["B300"]) for r in rows if r["depth"] > r["B300"]]
# distribution of B300 and A300
out["B300_hist"] = sorted([r["B300"] for r in rows if r["B300"] > 0])
out["A300_by_cls"] = {c: sorted(r["A300"] for r in rows if r["cls"] == c) for c in ("LOSE", "WIN", "RUN")}
# per-class medians of features
feats = ["B5", "B10", "B15", "B20", "N5", "N10", "N15", "N20", "A10", "A20", "pc_1_5", "pc_6_10", "pc_11_15",
         "pc_16_20", "max_dB_1_10", "max_dB_11_20", "first_multi", "last_birth"]
out["by_class"] = {}
for c in ("LOSE", "WIN", "RUN"):
    sub = [r for r in rows if r["cls"] == c]
    out["by_class"][c] = {f: [r[f] for r in sub] for f in feats}

# early-warning screens: predict RUN (depth>=20) among all 128 and among copiers (B5>=1)
def screen(name, pred, pool, target):
    tp = sum(1 for r in pool if pred(r) and target(r)); fn = sum(1 for r in pool if not pred(r) and target(r))
    fp = sum(1 for r in pool if pred(r) and not target(r)); tn = sum(1 for r in pool if not pred(r) and not target(r))
    return dict(name=name, tp=tp, fn=fn, fp=fp, tn=tn, hit=round(tp / (tp + fn), 3) if tp + fn else None,
                false_alarm=round(fp / (fp + tn), 3) if fp + tn else None, ppv=round(tp / (tp + fp), 3) if tp + fp else None)

isrun = lambda r: r["depth"] >= 20
def win5(r, e):  # births in the 5 epochs ending at e
    return r["_t"][min(e, 300) - 1][2] - r["_t"][e - 6][2]
for r, rr in zip(rows, R):
    r["_t"] = rr["traj"]
scr = []
for e in (5, 10, 15, 20):
    for k in (4, 8, 16, 24, 32):
        scr.append(screen(f"B{e}>={k} -> RUN", lambda r, e=e, k=k: r[f"B{e}"] >= k, rows, isrun))
for e in (10, 12, 15, 20):
    scr.append(screen(f"births in ({e-5},{e}] >=1 -> RUN", lambda r, e=e: win5(r, e) >= 1, rows, isrun))
    scr.append(screen(f"births in ({e-5},{e}] >=3 -> RUN", lambda r, e=e: win5(r, e) >= 3, rows, isrun))
for e in (10, 15, 20):
    scr.append(screen(f"A{e}>=2*N{e} & N{e}>=4 (label leakage) -> RUN", lambda r, e=e: r[f"N{e}"] >= 4 and r[f"A{e}"] >= 2 * r[f"N{e}"], rows, isrun))
scr.append(screen("max_dB_11_20>=2 (>=2 concurrent copiers in 11-20) -> RUN", lambda r: r["max_dB_11_20"] >= 2, rows, isrun))
# conditional on being a WIN-or-RUN by depth>=5 (the burst-vs-runaway discrimination)
pool5 = [r for r in rows if r["depth"] >= 5]
for e in (10, 12, 15, 20):
    scr.append(screen(f"[depth>=5 pool] births in ({e-5},{e}] >=1 -> RUN", lambda r, e=e: win5(r, e) >= 1, pool5, isrun))
    scr.append(screen(f"[depth>=5 pool] B{e if e in (10,15,20) else 10}>=16 -> RUN", lambda r, e=e: r[f"B{e if e in (10,15,20) else 10}"] >= 16, pool5, isrun))
out["screens"] = scr
for r in rows:
    r.pop("_t", None)
out["rows"] = rows
json.dump(out, open(HERE / "a1_ticket.json", "w"), indent=1)
for x in scr: print(x)
print("depth>founder births:", out["depth_exceeds_founder_births"])
print("A300 by cls:", out["A300_by_cls"]["WIN"], out["A300_by_cls"]["RUN"], "LOSE max", max(out["A300_by_cls"]["LOSE"]))
for c, d in out["by_class"].items():
    print(c, {k: (st.median([v for v in vs if v is not None]) if [v for v in vs if v is not None] else None) for k, vs in d.items()})
