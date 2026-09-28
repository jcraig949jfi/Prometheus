"""R2 SELECTION OBJECTIVE (Crius) + W1-E1 efficiency/capability split.
Re-creates each C2 donor's frozen VALIDATE cells exactly as a18.donor did
(a17.R_VAL = 4, label A19-<cat>-val/r<r>, index r*4+j, Prov over the
replicate's families) and prices libraries with the exact fast cost used in C2.
Reproduction check: recomputed mean paired saving of the chosen candidate must
equal the frozen selection_table value.
E1: for every donor that selected something other than INHERITED, split the
validation saving into cells START solved at escrow (efficiency) vs cells START
failed at escrow (capability).
R2: for every composing arm with a held schema (G1, SHAM_0, SHAM_1, OFF_0), the
compositions of the held schema covering the MOST of the replicate's 8
TRANSFER families (extensional, any group); each is priced on the frozen
VALIDATE cells as a17.select prices it, and (on the families it covers) on the
frozen TRANSFER cells (A19-<cat>-rx, 4 cells) with T4 qualification."""
import sys
import time
from w6_common import a18, a17, FR, Fam, c2_data, wr, HERE as HERE_W6

sys.path.insert(0, str(a18.HERE))
import a18_c1 as C   # noqa: E402

a17.R_VAL = 4
ESC = a17.ESCROW
t0 = time.time()
roles, panel, donors, trans = c2_data()
HELD = C.HELD
_start_cost = {}


def val_cells(d, fams):
    r, cat = d["replicate"], d["catalog"]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
    prov = a17.Prov(specs)
    val_f = [f["name"] for f in fams if f["role"] == "VALIDATE"]
    size = {f["name"]: f["Q2_size"] for f in fams}
    return [FR.Cell(prov, f, r * a17.R_VAL + j, size[f], label="%s-%s-val/r%d" % (a18.TAG, cat, r))
            for f in val_f for j in range(a17.R_VAL)], val_f


def costs(entries, cells):
    lib = FR.KLib(entries)
    return [c.cost(lib)[0] for c in cells]


def fams_of(d):
    return roles["%s/%s" % (d["catalog"][:3], d["catalog"][3:])]["families"]


def start_costs(d, cells):
    k = (d["catalog"], HELD[d["arm"]])
    if k not in _start_cost:
        _start_cost[k] = costs(a18.start_library(HELD[d["arm"]], panel)[0], cells)
    return _start_cost[k]


def transfer_price(d, fam, entries):
    name = fam["name"]
    spec = (fam["body"], fam["final"], fam["init"])
    prov = a17.Prov({name: spec})
    a17.M.use_provider(prov)
    lib = FR.KLib(entries)
    out = []
    for i in range(C.N_CELLS_T):
        c = FR.Cell(prov, name, i, fam["Q2_size"], label="%s-%s-rx" % (a18.TAG, d["catalog"]))
        ch, prog = c.cost(lib)
        q = bool(prog is not None and C.t4_qualified(prov, name, prog)[0])
        out.append({"charge": ch, "qualified": q, "program": prog})
    return out


import json as _j
try:
    _prev = {(e["catalog"], e["arm"]): e for e in _j.load(open(HERE_W6 / "W6_R2_E1_run1_partial.json"))["E1"]}
except Exception:  # noqa: BLE001
    _prev = {}
E1, R2 = [], []
for d in sorted(donors, key=lambda x: (x["catalog"], x["arm"])):
    fams = fams_of(d)
    cells, val_f = val_cells(d, fams)
    tab = d["selection_table"]
    base = None
    # ---- E1
    if (d["catalog"], d["arm"]) in _prev:
        E1.append(_prev[(d["catalog"], d["arm"])])
        _start_cost[(d["catalog"], HELD[d["arm"]])] = E1[-1]["start_costs"]
        print("E1 resumed", d["catalog"], d["arm"], flush=True)
    elif d["selected"] != "INHERITED":
        base = start_costs(d, cells)
        sc = costs(d["selected_entries"], cells)
        s = FR.paired_summary(base, sc)
        eff = [b - x for b, x in zip(base, sc) if b < ESC]
        cap = [b - x for b, x in zip(base, sc) if b >= ESC]
        cap_solved = sum(1 for b, x in zip(base, sc) if b >= ESC and x < ESC)
        E1.append({"catalog": d["catalog"], "arm": d["arm"], "selected": d["selected"],
                   "schema": d["selected_schema"], "origin": d["selected_origin"],
                   "repro_mean": s["mean_paired_saving"], "frozen_mean": tab[d["selected"]]["mean_paired_saving"],
                   "repro_ok": abs(s["mean_paired_saving"] - tab[d["selected"]]["mean_paired_saving"]) < 0.01,
                   "n_cells": len(cells), "start_solved_cells": len(eff), "start_failed_cells": len(cap),
                   "saving_total": sum(eff) + sum(cap), "saving_efficiency": sum(eff),
                   "saving_capability": sum(cap), "capability_cells_newly_solved": cap_solved,
                   "start_costs": base, "selected_costs": sc})
        print("E1", E1[-1]["catalog"], d["arm"], E1[-1]["repro_ok"], sum(eff), sum(cap), round(time.time() - t0), flush=True)
    # ---- R2
    held = HELD[d["arm"]]
    if not d["compose"] or held == "P" or d["arm"] == "G1_NC":
        continue
    base = start_costs(d, cells)
    if not d["compose"] or held == "P" or d["arm"] == "G1_NC":
        continue
    S = panel[held]
    tf = [f for f in fams if f["role"] == "TRANSFER"]
    TF = [Fam(f["name"], f["body"], f["final"], f["init"]) for f in tf]
    comps = a18.compositions(S)
    cov = {w: [F.name for F in TF if F.covered_by_bodies(a18.T3D.instantiate(w))] for w in comps}
    held_cov = [F.name for F in TF if F.covered_by_bodies(a18.T3D.instantiate(S))]
    sel_cov = ([F.name for F in TF if F.covered_by_bodies(a18.T3D.instantiate(d["selected_schema"]))]
               if d["selected_schema"] else None)
    # rank by MARGINAL cover (families the held schema itself does not cover),
    # then total cover: inert wraps ((S + 0), (S * 1), ...) equal S and add nothing.
    marg = {w: [n for n in v if n not in held_cov] for w, v in cov.items()}
    mx = max(len(v) for v in cov.values()) if cov else 0
    mm = max(len(v) for v in marg.values()) if marg else 0
    best = sorted([w for w in comps if len(marg[w]) == mm and mm > 0], key=lambda w: -len(cov[w]))[:6]
    start = a18.start_library(held, panel)[0]
    chosen_mean = tab[d["selected"]]["mean_paired_saving"] if d["selected"] != "INHERITED" else 0.0
    rows = []
    for w in best:
        ents = [a17.schema_entry("g2_new", w)] + start
        sc = costs(ents, cells)
        s = FR.paired_summary(base, sc)
        screened = a18.hits_any_cell(w, cells)
        elig = s["lower95_one_sided"] > 0
        tp = {}
        new_q = 0
        for f in tf:
            if f["name"] not in cov[w]:
                continue
            tr = transfer_price(d, f, ents)
            fro = next(t for t in trans if t["catalog"] == d["catalog"] and t["arm"] == d["arm"]
                       and t["family"] == f["name"])
            tp[f["name"]] = [{"best": x, "START_frozen": fc["START"], "SELECTED_frozen": fc["SELECTED"]}
                             for x, fc in zip(tr, fro["cells"])]
            new_q += sum(1 for x, fc in zip(tr, fro["cells"]) if x["qualified"] and not fc["START"]["qualified"])
        rows.append({"composition": w, "covers": cov[w], "marginal_covers": marg[w], "was_candidate_after_screen": screened,
                     "val_mean_saving": s["mean_paired_saving"], "val_lower95": s["lower95_one_sided"],
                     "eligible": elig, "in_table": any(False for _ in []),
                     "beats_chosen": elig and s["mean_paired_saving"] > chosen_mean,
                     "val_costs": sc, "transfer": tp, "transfer_cells_qualified_where_START_failed": new_q})
        print("R2", d["catalog"], d["arm"], w, len(cov[w]), s["mean_paired_saving"], s["lower95_one_sided"],
              screened, new_q, round(time.time() - t0), flush=True)
    R2.append({"catalog": d["catalog"], "arm": d["arm"], "held": S, "selected": d["selected"],
               "selected_schema": d["selected_schema"], "selected_cover": sel_cov, "held_cover": held_cov,
               "chosen_mean": chosen_mean, "n_compositions": len(comps), "max_cover": mx, "max_marginal_cover": mm,
               "n_at_max_marginal": sum(1 for v in marg.values() if len(v) == mm and mm > 0),
               "n_at_max": sum(1 for v in cov.values() if len(v) == mx and mx > 0),
               "cover_hist": {k: sum(1 for v in cov.values() if len(v) == k) for k in range(len(tf) + 1)},
               "cover_by_composition": {w: v for w, v in cov.items() if v},
               "best": rows})
    wr("W6_R2_E1.json", {"E1": E1, "R2": R2})
wr("W6_R2_E1.json", {"E1": E1, "R2": R2})
print("wrote", round(time.time() - t0), flush=True)
