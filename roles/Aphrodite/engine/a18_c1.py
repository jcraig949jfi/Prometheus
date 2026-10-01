"""AMENDMENT 18 -- C1 stages (foundry, donors, transfer, report). Uses a18.py.
Usage: python a18_c1.py <foundry|donors|transfer|report> [workers]
"""
import hashlib
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a18                    # noqa: E402
from a18 import a17, G, FR, I, T3D, log   # noqa: E402

DATE = "2026-09-27"
R_VAL_C1 = 4                        # validation cells per VALIDATE family (declared)
N_CELLS_T = 4                       # transfer cells per TRANSFER family
LADDER_CAP = 40 * a17.ESCROW        # capability-test budget (10M)
ARMS = ["G1", "G1_NC", "SHAM_0", "SHAM_1", "OFF_0", "P"]
COMPOSE = {"G1": True, "G1_NC": False, "SHAM_0": True, "SHAM_1": True, "OFF_0": True, "P": True}
HELD = {"G1": "G1", "G1_NC": "G1", "SHAM_0": "SHAM_0", "SHAM_1": "SHAM_1", "OFF_0": "OFF_0", "P": "P"}
ON_PATH = ["G1", "SHAM_0", "SHAM_1"]
NREP = {"CON": 8, "NAT": 4}
LET = "abcdefghijklmnopqrstuvwxyz"


def sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, default=str).encode()).hexdigest()


def wr(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")


def rd(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def rd_jsonl(name):
    p = HERE / name
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def _pname(i):
    return "q" + "".join(LET[(i // 26 ** k) % 26] for k in range(3))


def pool(fn, items, workers):
    with ProcessPoolExecutor(max_workers=workers, initializer=a18.worker_init) as ex:
        futs = [ex.submit(fn, it) for it in items]
        for f in as_completed(futs):
            yield f.result()


def t4_qualified(prov, name, prog):
    import tribunal_t4 as T4
    T4.use_provider(prov)
    art = a17.M.artifact_for(name, prog, a17.EMITTER)
    tr = T4.TribunalT4.after_freeze(art, name)
    sc = tr.score(art)
    return tr.qualified(sc), sc


# ---------------------------------------------------------------- foundry
def qualify_family(args):
    """Q2 (exact-fast) + T4 on the witness artifact + PRISTINE / L1 pilot
    solvability (4 cells each; hit must also be T4-qualified)."""
    a18.worker_init()
    name, body, init, final, src = args
    prov = a17.Prov({name: (body, final, init)})
    a17.M.use_provider(prov)
    row = {"name": name, "body": body, "init": init, "final": final, "source": src}
    size = a17.qualify(prov, name, a18.TAG + "-Q2")
    row["Q2_size"] = size
    if size is None:
        return row
    ok, sc = t4_qualified(prov, name, prov.witness(name))
    row["T4"], row["T4_qualified"] = sc, ok
    if not ok:
        return row
    for arm, ents in (("PRISTINE", FR.pristine().entries), ("L1", a17.L1_entries())):
        lib, solved = FR.KLib(ents), 0
        for i in range(4):
            c = FR.Cell(prov, name, i, size, label="%s-pilot-%s" % (a18.TAG, arm))
            _ch, prog = c.cost(lib)
            if prog is not None and t4_qualified(prov, name, prog)[0]:
                solved += 1
        row["p_" + arm] = solved / 4
    return row


def stage_foundry(workers=8, draws_per_source=48):
    import ruler_v2 as R
    a18.use_world("W5")
    panel = a18.build_panel()
    sb = a18.supply_bodies(panel, ON_PATH)
    own = {k: set(T3D.instantiate(s)) for k, s in panel.items()}
    comp = {k: set(b for w in a18.compositions(s) for b in T3D.instantiate(w)) for k, s in panel.items()}
    overlap = {a: {b: round(len(own[a] & comp[b]) / max(1, len(comp[b])), 5) for b in panel if b != a}
               for a in panel}
    rng = random.Random(I._seed("APHRODITE/A18/SUPPLY/v1"))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    draws, i = [], 0
    for k in ON_PATH:
        for _ in range(draws_per_source):
            draws.append((_pname(i), rng.choice(sb[k]), rng.choice(G.H1_SPACE), rng.choice(finals), "CON:" + k))
            i += 1
    for _ in range(draws_per_source * 3):          # NATURAL: uniform accumulating W5 bodies
        while True:
            b = rng.choice(G.BODY_SPACE)
            if R.accumulating(b):
                break
        draws.append((_pname(i), b, rng.choice(G.H1_SPACE), rng.choice(finals), "NAT"))
        i += 1
    wr("A18_PANEL_%s.json" % DATE, {"panel": panel, "panel_sha256": sha(panel), "overlap": overlap,
                                    "supply_sizes": {k: len(v) for k, v in sb.items()},
                                    "draws_sha256": sha(draws), "draws": draws})
    log("panel %s draws %d sha %s max-overlap %.4f" % (panel, len(draws), sha(draws)[:12],
                                                       max(v for d in overlap.values() for v in d.values())))
    done = {r["name"] for r in rd_jsonl("A18_FOUNDRY_ROWS_%s.jsonl" % DATE)}
    todo = [d for d in draws if d[0] not in done]
    with open(HERE / ("A18_FOUNDRY_ROWS_%s.jsonl" % DATE), "a", encoding="utf-8") as fh:
        for r in pool(qualify_family, todo, workers):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
    rows = rd_jsonl("A18_FOUNDRY_ROWS_%s.jsonl" % DATE)
    by = {}
    for r in rows:
        s = by.setdefault(r["source"], {"n": 0, "Q2": 0, "T4": 0, "p_P>0": 0, "p_L1>0": 0})
        s["n"] += 1
        s["Q2"] += r["Q2_size"] is not None
        s["T4"] += bool(r.get("T4_qualified"))
        s["p_P>0"] += r.get("p_PRISTINE", 0) > 0
        s["p_L1>0"] += r.get("p_L1", 0) > 0
    wr("A18_FOUNDRY_SUMMARY_%s.json" % DATE, by)
    log("foundry summary %s" % by)


# ---------------------------------------------------------------- roles + donors
def assign_roles(rows, supply, rep):
    rng = random.Random(I._seed("APHRODITE/A18/ROLES/%s/%d" % (supply, rep)))
    q = sorted([r for r in rows if r.get("T4_qualified")], key=lambda r: r["name"])
    head = [r for r in q if r.get("p_PRISTINE", 0) <= 0.75]        # window ceiling (RB-2)
    floor = [r for r in head if r.get("p_PRISTINE", 0) > 0]         # OBSERVE floor: PRISTINE only
    used, fams = set(), []

    def take(pool_, k, role):
        c = [r for r in pool_ if r["name"] not in used]
        rng.shuffle(c)
        for r in c[:k]:
            used.add(r["name"])
            fams.append(dict(r, role=role, qualified_dev_size=r["Q2_size"]))
        return len(c) >= k

    ok = True
    if supply == "CON":
        ok &= take(floor, 4, "OBSERVE")
        for k in ON_PATH:
            ok &= take([r for r in head if r["source"] == "CON:" + k], 1, "VALIDATE")
        ok &= take([r for r in head if r["source"] == "NAT"], 1, "VALIDATE")
        for k in ON_PATH:
            ok &= take([r for r in head if r["source"] == "CON:" + k], 2, "TRANSFER")
        ok &= take([r for r in head if r["source"] == "NAT"], 2, "TRANSFER")
    else:
        ok &= take([r for r in floor if r["source"] == "NAT"], 4, "OBSERVE")
        ok &= take([r for r in head if r["source"] == "NAT"], 4, "VALIDATE")
        ok &= take([r for r in head if r["source"] == "NAT"], 8, "TRANSFER")
    return fams, ok


def _donor_job(args):
    cat, kind, rep, fams, specs, panel, compose, arm = args
    a17.R_VAL = R_VAL_C1
    r = a18.donor((cat, kind, rep, fams, specs, panel, compose))
    r["arm"] = arm
    return r


def stage_donors(workers=8):
    a18.use_world("W5")
    panel = rd("A18_PANEL_%s.json" % DATE)["panel"]
    rows = rd_jsonl("A18_FOUNDRY_ROWS_%s.jsonl" % DATE)
    jobs, roles = [], {}
    for supply, n in NREP.items():
        for rep in range(n):
            fams, ok = assign_roles(rows, supply, rep)
            roles["%s/%d" % (supply, rep)] = {"ok": ok, "families": [
                {k: f[k] for k in ("name", "role", "source", "body", "init", "final", "Q2_size")} for f in fams]}
            if not ok:
                continue
            specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
            for arm in ARMS:
                jobs.append(("%s%d" % (supply, rep), HELD[arm], rep, fams, specs, panel, COMPOSE[arm], arm))
    wr("A18_ROLES_%s.json" % DATE, roles)
    done = {(r["catalog"], r["arm"]) for r in rd_jsonl("A18_DONORS_%s.jsonl" % DATE)}
    jobs = [j for j in jobs if (j[0], j[7]) not in done]
    log("donor jobs to run: %d" % len(jobs))
    with open(HERE / ("A18_DONORS_%s.jsonl" % DATE), "a", encoding="utf-8") as fh:
        for r in pool(_donor_job, jobs, workers):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("donor %s %-6s sel=%s origin=%s COMP=%s NOV=%s %ss" % (
                r["catalog"], r["arm"], r["selected_schema"], r["selected_origin"], r["COMPOSES_held"],
                r["NOVELTY_vs_G1"], r["seconds"]))


# ---------------------------------------------------------------- transfer + ladder
def _transfer_job(args):
    """One (replicate, arm, TRANSFER family): selected library vs the donor's
    start library vs PRISTINE, N_CELLS_T cells at escrow; the capability ladder
    re-runs start/PRISTINE at LADDER_CAP on cells where the selected library
    qualified and they did not."""
    cat, arm, fam, spec, size, sel_entries, start_entries, sel_schema = args
    a18.worker_init()
    name = fam
    prov = a17.Prov({name: spec})
    a17.M.use_provider(prov)
    libs = {"SELECTED": FR.KLib(sel_entries), "START": FR.KLib(start_entries),
            "PRISTINE": FR.KLib(FR.pristine().entries)}
    out = {"catalog": cat, "arm": arm, "family": fam, "cells": []}
    for i in range(N_CELLS_T):
        c = FR.Cell(prov, name, i, size, label="%s-%s-rx" % (a18.TAG, cat))
        row = {}
        for k, lib in libs.items():
            ch, prog = c.cost(lib)
            q = bool(prog is not None and t4_qualified(prov, name, prog)[0])
            coord = None
            if prog is not None and sel_schema and k == "SELECTED":
                coord = "g2_new" if prog[2] in set(T3D.instantiate(sel_schema)) else "other"
            row[k] = {"charge": ch, "qualified": q, "coord": coord}
        if row["SELECTED"]["qualified"]:
            for k in ("START", "PRISTINE"):
                if not row[k]["qualified"]:
                    ch, prog = c.cost(libs[k], LADDER_CAP)
                    row[k]["ladder_charge"] = ch
                    row[k]["ladder_qualified"] = bool(prog is not None and t4_qualified(prov, name, prog)[0])
        out["cells"].append(row)
    return out


def stage_transfer(workers=8):
    a18.use_world("W5")
    panel = rd("A18_PANEL_%s.json" % DATE)["panel"]
    roles = rd("A18_ROLES_%s.json" % DATE)
    donors = rd_jsonl("A18_DONORS_%s.jsonl" % DATE)
    done = {(r["catalog"], r["arm"], r["family"]) for r in rd_jsonl("A18_TRANSFER_%s.jsonl" % DATE)}
    jobs = []
    for d in donors:
        key = "%s/%s" % (d["catalog"][:3], d["catalog"][3:])
        fams = [f for f in roles[key]["families"] if f["role"] == "TRANSFER"]
        start = a18.start_library(HELD[d["arm"]], panel)[0]
        for f in fams:
            if (d["catalog"], d["arm"], f["name"]) in done:
                continue
            jobs.append((d["catalog"], d["arm"], f["name"], (f["body"], f["final"], f["init"]), f["Q2_size"],
                         d["selected_entries"], start, d["selected_schema"]))
    log("transfer jobs %d" % len(jobs))
    with open(HERE / ("A18_TRANSFER_%s.jsonl" % DATE), "a", encoding="utf-8") as fh:
        for r in pool(_transfer_job, jobs, workers):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


# ---------------------------------------------------------------- report (verdict rules, frozen)
def _sign_p(a, b):
    import math
    n = a + b
    return sum(math.comb(n, k) for k in range(a, n + 1)) / 2 ** n if n else 1.0


def ladder_for(d, trows, panel):
    """Per (replicate, arm) ladder. SOLVED/REUSABLE/CAPABILITY use the transfer
    rows of this donor; REACHABLE/SELECTED/NOVELTY/COMPOUNDING the donor trace."""
    held = HELD[d["arm"]]
    grp = "CON:" + held if held in ON_PATH else None
    own = [t for t in trows if (grp is None or t.get("source") == grp)]
    sel_q_fams = sorted({t["family"] for t in own for c in t["cells"]
                         if c["SELECTED"]["qualified"] and c["SELECTED"]["coord"] == "g2_new"})
    cap_fams = sorted({t["family"] for t in own for c in t["cells"]
                       if c["SELECTED"]["qualified"] and c["SELECTED"]["charge"] <= a17.ESCROW
                       and not c["START"].get("ladder_qualified", c["START"]["qualified"])
                       and not c["PRISTINE"].get("ladder_qualified", c["PRISTINE"]["qualified"])
                       and "ladder_charge" in c["START"] and "ladder_charge" in c["PRISTINE"]})
    return {"REACHABLE": d["n_composed_candidates"] > 0,
            "SELECTED": bool(d["COMPOSES_held"]),
            "SOLVED": any(c["SELECTED"]["qualified"] and not c["START"]["qualified"]
                          for t in own for c in t["cells"]),
            "REUSABLE": d["COMPOSES_held"] and len(sel_q_fams) >= 2,
            "CAPABILITY_EXPANDING": d["COMPOSES_held"] and len(cap_fams) >= 2,
            "NOVELTY": bool(d["NOVELTY_vs_G1"]), "COMPOUNDING": bool(d["COMPOSES_held"] or d["REFINES_held"]),
            "reuse_families": sel_q_fams, "capability_families": cap_fams}


def stage_report(_w=0):
    panel = rd("A18_PANEL_%s.json" % DATE)["panel"]
    roles = rd("A18_ROLES_%s.json" % DATE)
    donors = rd_jsonl("A18_DONORS_%s.jsonl" % DATE)
    trans = rd_jsonl("A18_TRANSFER_%s.jsonl" % DATE)
    src = {f["name"]: f["source"] for v in roles.values() for f in v["families"]}
    for t in trans:
        t["source"] = src.get(t["family"])
    out = {"panel": panel, "per_supply": {}}
    for supply in NREP:
        lad = {}
        for d in donors:
            if not d["catalog"].startswith(supply):
                continue
            tr = [t for t in trans if t["catalog"] == d["catalog"] and t["arm"] == d["arm"]]
            lad.setdefault(d["arm"], {})[d["catalog"]] = ladder_for(d, tr, panel)
        counts = {a: {k: sum(1 for v in lad.get(a, {}).values() if v[k]) for k in
                      ("REACHABLE", "SELECTED", "SOLVED", "REUSABLE", "CAPABILITY_EXPANDING", "NOVELTY", "COMPOUNDING")}
                  for a in ARMS}
        n = {a: len(lad.get(a, {})) for a in ARMS}

        def stepping(arm, controls):
            sel = counts[arm]["SELECTED"]
            ps = {c: _sign_p(sum(1 for r in lad.get(arm, {}) if lad[arm][r]["SELECTED"]
                                 and not lad.get(c, {}).get(r, {}).get("SELECTED")),
                             sum(1 for r in lad.get(c, {}) if lad[c][r]["SELECTED"]
                                 and not lad.get(arm, {}).get(r, {}).get("SELECTED"))) for c in controls}
            yes = (all(p < 0.05 for p in ps.values()) and counts[arm]["REUSABLE"] >= 5
                   and counts[arm]["CAPABILITY_EXPANDING"] >= 5)
            return {"sign_p_vs": ps, "YES": yes, "n": n.get(arm, 0), "selected": sel}
        res = {"n": n, "ladder_counts": counts, "ladders": lad}
        if supply == "CON":
            h1 = stepping("G1", ["G1_NC", "P", "OFF_0"])
            res["G1_STEPPING_STONE"] = ("UNTESTABLE" if n.get("G1", 0) < 8 else ("YES" if h1["YES"] else "NO"))
            res["H1"] = h1
            res["GENERIC_STEPPING_STONE"] = sum(stepping(s, ["P", "OFF_0"])["YES"] for s in ("SHAM_0", "SHAM_1"))
        out["per_supply"][supply] = res
    wr("A18_C1_RESULT_%s.json" % DATE, out)
    for supply, res in out["per_supply"].items():
        log("%s counts %s" % (supply, json.dumps(res["ladder_counts"])))
        if supply == "CON":
            log("G1_STEPPING_STONE=%s GENERIC=%s/2 H1=%s" % (res["G1_STEPPING_STONE"],
                                                           res["GENERIC_STEPPING_STONE"], res["H1"]))


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    log("stage %s workers %d fasteval=%s fastcost=%s" % (st, w, os.environ.get("A17_FASTEVAL"),
                                                         os.environ.get("A18_FASTCOST")))
    {"foundry": stage_foundry, "donors": stage_donors, "transfer": stage_transfer,
     "report": stage_report}[st](w)
    log("stage %s done" % st)
