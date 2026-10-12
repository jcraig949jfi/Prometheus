"""RESULT tables (Argus C-018-T050): read-only use of the frozen adapter/evaluate on the committed unit metas.
Writes rso/aether/runs/meta/result_tables.json. Changes no pinned file."""
import json, glob, os, sys
sys.path.insert(0, os.getcwd())
from rso.aether import adapter as A, evaluate as E
TR = E.TR
an = json.load(open("rso/aether/runs/meta/analyse_full.out"))
rows = {r["seed"]: r for r in an["laws"]["RX"]["rows"]}
out = []
def cheb(a, b, n):
    ya, xa = divmod(a, n); yb, xb = divmod(b, n)
    dy = min((ya - yb) % n, (yb - ya) % n); dx = min((xa - xb) % n, (xb - xa) % n)
    return max(dy, dx), dy + dx
for p in sorted(glob.glob("rso/aether/runs/CONFIRM/RX.*/native_RX_*.json")):
    m = json.load(open(p)); r = rows[m["seed"]]
    if r["cls"] == "NO_CUT": continue
    tree, n, O = m["tree"], m["n"], m["origin"]
    B, _ = TR.choose_cut({"tree": tree})
    ft = dict(zip(tree["site"], tree["ftick"]))
    tg = sorted(TR.descendants(tree, B))
    N = A.choose_nonancestor(tree, B, O, n)
    cands = A.nonancestor_candidates(tree, B, O, n)
    v10 = cands[0][2] if cands else None
    d = {"seed": m["seed"], "cls": r["cls"], "r_int": r["r_int"], "B": B, "ftick_B": ft[B], "N": N,
         "ftick_N": ft[N] if N is not None else None, "n_tree_targets": len(tg), "v100_N": v10,
         "v100_N_ftick": ft[v10] if v10 is not None else None}
    d["v100_N_before_B"] = (ft[v10] < ft[B]) if v10 is not None else None
    d["N_is_v100_N"] = (N == v10)
    if N is not None and tg:
        c = [cheb(N, t, n) for t in tg]
        d["N_dist_cheb_nearest_target"] = min(x[0] for x in c)
        d["N_4adjacent_to_target"] = any(x[1] == 1 for x in c)
    assert (r["ftick_B"], r["ftick_N"]) == (d["ftick_B"], d["ftick_N"]), (r, d)
    out.append(d)
conf = [x for x in out if x["cls"] == "CONFIRMED"]
summ = {"p2_v110": {"confirmed_r_ge2": sum(1 for x in conf if x["r_int"] >= 2), "need": an["laws"]["RX"]["need"], "evaluable": an["laws"]["RX"]["evaluable"]},
        "p2_v100": {"confirmed_r_ge2": sum(1 for x in conf if x["r_int"] >= 2), "need": 5, "of_units": 48}}
summ["p2_v100"]["reading"] = "HELD" if summ["p2_v100"]["confirmed_r_ge2"] >= 5 else "NOT HELD"
summ["p2_v110"]["reading"] = "HELD" if summ["p2_v110"]["confirmed_r_ge2"] >= 3 else "NOT HELD"
ev = [x for x in out if x["cls"] in ("CONFIRMED", "NONSPECIFIC")]
summ["N_4adjacent_in_confirmed_or_nonspecific"] = sum(1 for x in ev if x.get("N_4adjacent_to_target")); summ["n_confirmed_or_nonspecific"] = len(ev)
summ["N_moved_off_v100_N"] = sum(1 for x in ev if not x["N_is_v100_N"])
summ["N_moved_off_pre_B_site"] = sum(1 for x in ev if x["v100_N_before_B"])
summ["any_unit_N_moved_off_pre_B"] = sum(1 for x in out if x["v100_N_before_B"])
json.dump({"units": out, "summary": summ}, open("rso/aether/runs/meta/result_tables.json", "w"), indent=1)
for x in out: print(x)
print(json.dumps(summ, indent=1))
