"""Foundry v2 driver (E1_V2_RULES.md, frozen before the v2 pilot). v1 (qualify.py) is kept as the v1 record.

Pipeline per world (each step is resumable; each run stays under --cpu-min):
    world   --secrets F --set pilot_v2 --index i   build the world + its YOKED sibling (the seed is read from the
                                                    secret file, checked against the sha256 commitment, never written)
    qualify --world WID      stage 1 per family: null ladder (constant, lookup(+nearest), reactive, history2, library:
                             hindsight; REGRESSION: dev-fit, dev-selected), small search 1e5 (hindsight), witness check;
                             for R>=2 that survive: base search 1e6 from scratch (hindsight; rule 3b), then the
                             sealed-mechanism known positive (R2 gate; R3+ label KP_CAPACITY). R1: chain step (c).
    chain   --world WID      rule 3d: promote the FOUND R1 programs (not the sealed truth) and search each R3/R4/R5
                             family with that acquired library (contract protocol, 1e6, qualified = test + tribunal).
    ablate  --world WID      SYNTHETIC_DEPTH: R3+ = acquired library minus each constituent; R2 = sealed library minus
                             its mechanism (v1 rule, kept). Hindsight, 1e6.
    export  --secrets F --set pilot_v2   final classes (motif cap), evaluator view, redacted arm view, orders,
                             manifest, report. Wipes and rewrites evaluator/ and arm_view/ (rule 5).
    controls                 planted controls (run first).
No treatment arm is consulted anywhere.
"""
import argparse
import hashlib
import json
import os
import random
import shutil
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.setrecursionlimit(10000)

import interp_a as A
import generator as G
import nulls as N
import regress
import tenum

QCONFIG = {
    "version": "b04-foundry-qual-v2.0",
    "rules": "roles/Aphrodite/beta04/windows/E1_V2_RULES.md",
    "B_small": 100_000, "B_base": 1_000_000, "B_oracle": 1_000_000, "B_chain": 1_000_000,
    "ladder": ["constant", "lookup", "reactive", "history2", "library", "regression", "small_search"],
    "closed_form_mode": "hindsight (any dev-consistent model of the class solves test)",
    "regression_mode": "dev-fit, dev-selected per class (fewest parameters); no hindsight",
    "small_search_mode": "hindsight within B_small",
    "base_1e6_mode": "hindsight within B_base (rule 3b)",
    "kp_mode": "contract protocol (first dev-consistent) with the SEALED mechanisms; SOLVED on test",
    "chain_c_mode": "contract protocol base search within B_chain on the mechanism's R1 families; the found program "
                    "must be correct on test AND tribunal; the mechanism primitive is the first closed lambda of the "
                    "mechanism's type in the found program (f/p fallback: abstract a single repeated readout s(xs))",
    "chain_d_mode": "contract protocol within B_chain, base grammar + ALL acquired primitives of the world; qualified "
                    "= correct on test AND tribunal",
    "near_trivial_capture": 0.8,
    "goldilocks_band": [0.2, 0.8],
    "motif_cap": 1,
    "kind_pairs_required": 3,
    "base_memo_max": 7, "oracle_memo_max": 6,
    "shuffles_uniform": 5, "shuffles_anti": 3,
}
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "pilot_v2")
COMMITMENTS = os.path.join(os.path.dirname(HERE), "WORLD_SEED_COMMITMENTS.json")


def qconfig_sha():
    return hashlib.sha256(json.dumps(QCONFIG, sort_keys=True).encode()).hexdigest()


def sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def wdir(out, wid):
    d = os.path.join(out, wid)
    os.makedirs(d, exist_ok=True)
    return d


def wpath(out, wid, name):
    return os.path.join(wdir(out, wid), name)


def read_jsonl(p):
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ---------------------------------------------------------------- secrets
def load_secret(path, set_name, index):
    with open(path) as f:
        seeds = json.load(f)[set_name]
    seed = seeds[index]
    with open(COMMITMENTS) as f:
        com = json.load(f)["commitments"][set_name]
    ssha = G.seed_sha256(seed)
    if ssha != com[index]:
        raise SystemExit("seed does not match its commitment")
    return seed


def opaque(seed, family_id):
    return hashlib.sha256(("opaque|%s|%s" % (seed, family_id)).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- world
def cmd_world(secrets, set_name, index, out):
    seed = load_secret(secrets, set_name, index)
    t0 = time.process_time()
    w = G.build_world(seed)
    sib = G.build_world(G.yoke_seed(seed))
    y = G.build_yoked(w, sib)
    cpu = round(time.process_time() - t0, 1)
    wid = w["world_id"]
    with open(wpath(out, wid, "WORLD_SEALED.json"), "wb") as f:
        f.write(G.world_bytes(w))
    with open(wpath(out, wid, "YOKED_SEALED.json"), "wb") as f:
        f.write(G.world_bytes(y))
    with open(wpath(out, wid, "GEN_RECEIPT.json"), "w") as f:
        json.dump({"world_id": wid, "set": set_name, "index": index, "world_seed_sha256": w["world_seed_sha256"],
                   "config_sha": G.config_sha(), "regression_bank": regress.bank_summary(G.CONFIG)["sha256"],
                   "cpu_s": cpu, "world_sha256": sha_file(wpath(out, wid, "WORLD_SEALED.json")),
                   "yoked_sha256": sha_file(wpath(out, wid, "YOKED_SEALED.json"))}, f, sort_keys=True, indent=1)
    print(wid, "generated in", cpu, "cpu-s")
    return wid


def load_world(out, wid):
    with open(wpath(out, wid, "WORLD_SEALED.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- grammars (cached per process)
_G = {}


def base_grammar():
    if "base" not in _G:
        _G["base"] = tenum.Grammar(memo_max=QCONFIG["base_memo_max"])
    return _G["base"]


def lib_grammar(key, extra):
    """One library grammar at a time besides the base grammar (memory)."""
    if _G.get("lib_key") != key:
        _G["lib"] = tenum.Grammar(extra, memo_max=QCONFIG["oracle_memo_max"])
        _G["lib_key"] = key
    return _G["lib"]


def sealed_extra(mechs, drop=None):
    return {m.name: (m.sig, m.ret, m.term) for m in mechs.values() if m.name != drop}


def _T(rec):
    return {"I": "I", "L": "L", "B": "B"}[rec["output_type"]]


def _count_est(T, k, extra, levels):
    """Estimate the size of level k of a pruned grammar from the measured level k-1 and the unpruned growth."""
    if k - 1 not in levels:
        return None
    sig = [(v[0], v[1]) for v in extra.values()] if extra else None
    a, b = tenum.count_space(T, k - 1, extra_sig=sig), tenum.count_space(T, k, extra_sig=sig)
    return levels[k - 1] * b / a if a else None


def search_record(r, prog_key, T, extra, budget):
    """Common fields for a search result: CRN rank, order-free expected rank (F7), HORIZON info (F8)."""
    out = {"budget": budget, "complete_size": r["complete_size"], "size_reached": r["size_reached"],
           "level_counts": {str(k): v for k, v in r["level_counts"].items()}}
    prog = r.get(prog_key)
    if prog is not None:
        k = A.esize(prog)
        est = _count_est(T, k, extra, r["level_counts"]) if k not in r["level_counts"] else None
        ofr, estimated = tenum.order_free_rank(r["level_counts"], k, est)
        out["order_free_rank"] = round(ofr) if ofr is not None else None
        out["order_free_rank_estimated"] = estimated
    return out


# ---------------------------------------------------------------- witness check
def witness_check(rec, mechs):
    base = A.parse(rec["witness"])
    prom = A.parse(rec["witness_promoted"])
    pmap = {m.name: m.promoted() for m in mechs.values()}
    try:
        A.typecheck(base)
        A.typecheck(prom, promoted=pmap)
    except A.TypeErr as e:
        return {"ok": False, "error": str(e)}
    ok, up, ue = True, [], []
    for xs, y in rec["dev"] + rec["test"]:
        if A.run(base, xs) != y:
            ok = False
        v, u = A.run(prom, xs, promoted=pmap, with_units=True)
        if v != y:
            ok = False
        up.append(u.promoted)
        ue.append(u.expanded)
    trib_ok = all(A.run(base, xs) == y for xs, y in rec["tribunal"])
    return {"ok": ok and trib_ok, "units_promoted_mean": round(sum(up) / len(up), 2),
            "units_expanded_mean": round(sum(ue) / len(ue), 2)}


def qualified_on(prog, rec, promoted=None):
    """(test_ok, tribunal_ok) under interpreter A."""
    t = all(A.run(prog, xs, promoted=promoted) == y for xs, y in rec["test"])
    tr = all(A.run(prog, xs, promoted=promoted) == y for xs, y in rec["tribunal"])
    return t, tr


# ---------------------------------------------------------------- chain step (c): lambda extraction
KIND_TYPE = {"f": A.SLOT_TYPES["F1"], "p": A.SLOT_TYPES["P"], "s": A.SLOT_TYPES["F2"]}


def _lams(t):
    if t[0] == "lam":
        yield t
        yield from _lams(t[2])
    elif t[0] == "app":
        yield from _lams(t[1])
        for a in t[2]:
            yield from _lams(a)
    elif t[0] == "prim":
        for a in t[2]:
            yield from _lams(a)


def _readout_sites(t, acc):
    if t[0] == "var":
        acc.append(None)                                   # a bare xs occurrence
        return
    if t[0] == "prim" and t[1] in G.CONFIG["readouts_int"] and t[2] == (("var", "xs"),):
        acc.append(t)
        return
    if t[0] == "lam":
        _readout_sites(t[2], acc)
    elif t[0] == "app":
        _readout_sites(t[1], acc)
        for a in t[2]:
            _readout_sites(a, acc)
    elif t[0] == "prim":
        for a in t[2]:
            _readout_sites(a, acc)


def _replace(t, old, new):
    if t == old:
        return new
    if t[0] in ("lit", "var"):
        return t
    if t[0] == "lam":
        return ("lam", t[1], _replace(t[2], old, new))
    if t[0] == "app":
        return ("app", _replace(t[1], old, new), tuple(_replace(a, old, new) for a in t[2]))
    return ("prim", t[1], tuple(_replace(a, old, new) for a in t[2]))


def extract_primitive(prog, kind):
    want = KIND_TYPE[kind]
    for lam in _lams(prog):
        if A.free_vars(lam):
            continue
        try:
            if A.typecheck(lam, env={}) == want:
                return lam, "lambda"
        except A.TypeErr:
            continue
    if kind in ("f", "p"):
        sites = []
        _readout_sites(prog, sites)        # every xs occurrence: its enclosing readout (r xs), or None if bare
        if sites and all(st is not None for st in sites) and len(set(sites)) == 1:
            body = _replace(prog, sites[0], ("var", "x"))
            lam = ("lam", "x", body)
            try:
                if not A.free_vars(lam) and A.typecheck(lam, env={}) == want:
                    return lam, "abstract_readout"
            except A.TypeErr:
                pass
    return None, None


def chain_c(rec, mechs):
    """Rule 3c on one R1 family: base search (contract protocol) at B_chain; qualified + extractable?"""
    m = mechs[rec["mechanisms_used"][0]]
    T = _T(rec)
    t0 = time.process_time()
    r = tenum.search(base_grammar(), T, rec["dev"], QCONFIG["B_chain"])
    out = {"mechanism": m.name, "charge": r["charge"]}
    out.update(search_record(r, "found", T, None, QCONFIG["B_chain"]))
    if r["found"] is None:
        out["status"] = "HORIZON" if rec["witness_esize"] > r["complete_size"] else "NOT_FOUND"
    else:
        prog = r["found"]
        out["found"] = A.show(prog)
        out["found_esize"] = A.esize(prog)
        t_ok, tr_ok = qualified_on(prog, rec)
        out["test_ok"], out["tribunal_ok"] = t_ok, tr_ok
        if not t_ok:
            out["status"] = "UNDERDETERMINED"
        elif not tr_ok:
            out["status"] = "TRIBUNAL"
        else:
            lam, how = extract_primitive(prog, m.kind)
            if lam is None:
                out["status"] = "NOT_EXTRACTABLE"
            else:
                out["status"] = "ACQUIRED"
                out["primitive"] = A.show(lam)
                out["extraction"] = how
                out["agree_with_sealed"] = agreement(lam, m)
    out["cpu_s"] = round(time.process_time() - t0, 2)
    return out


def agreement(lam, m):
    """Diagnostic: fraction of the probe grid where the acquired primitive equals the sealed mechanism
    (values in [-80, 80]; fold steps on the generator's (a, b) probe grid extended to |a| <= 8000)."""
    import fastc
    fa, fs = fastc.closed_fun(lam), fastc.closed_fun(m.term)
    pts, ok = 0, 0
    if m.kind in ("f", "p"):
        for v in range(-80, 81):
            pts += 1
            ok += _safe(lambda: fa(v)) == _safe(lambda: fs(v))
    else:
        for a in list(range(-30, 31)) + [-8000, -999, 999, 8000]:
            for b in range(-40, 41, 3):
                pts += 1
                ok += _safe(lambda: fa(a)(b)) == _safe(lambda: fs(a)(b))
    return round(ok / pts, 4)


def _safe(f):
    try:
        return f()
    except (A.Fail, ZeroDivisionError, TypeError):
        return "FAIL"


# ---------------------------------------------------------------- stage 1
def capture_of(q):
    caps = [q["nulls"][n].get("best_consistent_test_acc", 0.0) for n in QCONFIG["ladder"][:5]]
    caps.append(q["regression"].get("best_selected_test_acc", 0.0))
    caps.append(q["small"].get("test_acc", 0.0) if q["small"].get("found") else 0.0)
    return max(caps)


def qualify_family(world, rec, mechs):
    t0 = time.process_time()
    q = {"family_id": rec["family_id"], "rung": rec["rung"], "gen_class": rec["gen_class"]}
    if rec["gen_class"] != "OK":
        return q
    dev, test, trib = rec["dev"], rec["test"], rec["tribunal"]
    q["witness"] = witness_check(rec, mechs)
    q["nulls"] = N.run_closed_form(dev, test)
    q["regression"] = regress.run(dev, test, G.CONFIG)
    q["small"] = N.run_small_search(base_grammar(), rec["output_type"], dev, test, QCONFIG["B_small"], trib)
    solved_by = [n for n in QCONFIG["ladder"][:5] if q["nulls"][n]["solved"]]
    if q["regression"]["solved"]:
        solved_by.append("regression")
    if q["small"]["solved"]:
        solved_by.append("small_search")
    q["solved_by"] = solved_by
    q["capture"] = capture_of(q)
    rn = int(rec["rung"][1])
    if rec["rung"] == "R1":
        q["chain_c"] = chain_c(rec, mechs)
    if rn >= 2 and not solved_by and q["capture"] <= QCONFIG["near_trivial_capture"] and q["witness"]["ok"]:
        T = _T(rec)
        r = tenum.search(base_grammar(), T, dev, QCONFIG["B_base"], hindsight_test=test)
        b = {"walk_charge": r["walk_charge"], "n_dev_consistent": r["n_dev_consistent"],
             "first_dev_consistent": A.show(r["found"]) if r["found"] else None}
        b.update(search_record(r, "hindsight_found", T, None, QCONFIG["B_base"]))
        b["solved"] = False
        if r["hindsight_found"] is not None:
            b["solved"] = qualified_on(r["hindsight_found"], rec)[0]
            b["hindsight_found"] = A.show(r["hindsight_found"])
            b["hindsight_charge"] = r["hindsight_charge"]
        q["base1e6"] = b
        if not b["solved"]:
            q["kp"] = known_positive(world, rec, mechs)
    q["cpu_s"] = round(time.process_time() - t0, 2)
    return q


def known_positive(world, rec, mechs):
    extra = sealed_extra(mechs)
    g = lib_grammar(("sealed", world["world_id"]), extra)
    T = _T(rec)
    t0 = time.process_time()
    r = tenum.search(g, T, rec["dev"], QCONFIG["B_oracle"])
    out = {"charge": r["charge"]}
    out.update(search_record(r, "found", T, extra, QCONFIG["B_oracle"]))
    if r["found"] is None:
        out["status"] = "HORIZON" if rec["promoted_esize"] > r["complete_size"] else "NOT_FOUND"
    else:
        pmap = {m.name: m.promoted() for m in mechs.values()}
        out["found"] = A.show(r["found"])
        out["found_esize"] = A.esize(r["found"])
        t_ok, tr_ok = qualified_on(r["found"], rec, pmap)
        out["status"] = "SOLVED" if t_ok else "DEV_UNDERDETERMINED"
        out["tribunal_ok"] = tr_ok
    out["cpu_s"] = round(time.process_time() - t0, 2)
    return out


def _resumable(path, items, fn, cpu_min, label):
    done = {d["family_id"] + "|" + d.get("_key", "") for d in read_jsonl(path)}
    t0 = time.process_time()
    n = 0
    with open(path, "a") as f:
        for key, item in items:
            if key in done:
                continue
            if time.process_time() - t0 > cpu_min * 60:
                print("cpu cap reached; resumable", flush=True)
                return False
            d = fn(item)
            f.write(json.dumps(d, sort_keys=True) + "\n")
            f.flush()
            n += 1
            print(label, d["family_id"], d.get("_key", ""), d.get("solved_by", ""), d.get("status", ""),
                  d.get("cpu_s", ""), flush=True)
    print("done", label, n, "items, cpu_s", round(time.process_time() - t0, 1), flush=True)
    return True


def cmd_qualify(out, wid, cpu_min):
    world = load_world(out, wid)
    mechs = G.mechanisms_of(world)
    items = [(r["family_id"] + "|", r) for r in world["families"]]
    return _resumable(wpath(out, wid, "QUALIFICATION.jsonl"), items,
                      lambda r: qualify_family(world, r, mechs), cpu_min, "qualify")


# ---------------------------------------------------------------- chain step (d)
def acquired_library(world, quals):
    recs = {r["family_id"]: r for r in world["families"]}
    lib, status = {}, {}
    for q in sorted(quals, key=lambda q: recs[q["family_id"]]["index"]):
        if q["rung"] != "R1" or "chain_c" not in q:
            continue
        c = q["chain_c"]
        m = c["mechanism"]
        status.setdefault(m, []).append({"family_id": q["family_id"], "status": c["status"]})
        if c["status"] == "ACQUIRED" and m not in lib:
            lib[m] = {"from": q["family_id"], "term": c["primitive"], "agree_with_sealed": c["agree_with_sealed"]}
    names = {}
    for i, m in enumerate(sorted(lib)):
        names[m] = "q%d" % i
    return lib, names, status


def acquired_extra(world, lib, names, drop=None):
    mechs = G.mechanisms_of(world)
    ex = {}
    for m, d in lib.items():
        if m == drop:
            continue
        mk = mechs[m]
        ex[names[m]] = (mk.sig, mk.ret, A.parse(d["term"]))
    return ex


def passes_stage1(rec, q):
    return (rec["gen_class"] == "OK" and not q["solved_by"] and q["capture"] <= QCONFIG["near_trivial_capture"]
            and q["witness"]["ok"] and "base1e6" in q and not q["base1e6"]["solved"])


def chain_d(world, rec, lib, names):
    ex = acquired_extra(world, lib, names)
    g = lib_grammar(("acq", world["world_id"]), ex)
    T = _T(rec)
    t0 = time.process_time()
    r = tenum.search(g, T, rec["dev"], QCONFIG["B_chain"])
    out = {"family_id": rec["family_id"], "charge": r["charge"], "library": sorted(names.values())}
    out.update(search_record(r, "found", T, ex, QCONFIG["B_chain"]))
    if r["found"] is None:
        out["status"] = "HORIZON" if rec["promoted_esize"] > r["complete_size"] else "NOT_FOUND"
    else:
        pmap = {n: A.Promoted(n, t, s, rr) for n, (s, rr, t) in ex.items()}
        prog = r["found"]
        out["found"] = A.show(prog)
        out["found_esize"] = A.esize(prog)
        t_ok, tr_ok = qualified_on(prog, rec, pmap)
        out["status"] = "SOLVED" if (t_ok and tr_ok) else ("TRIBUNAL" if t_ok else "UNDERDETERMINED")
        inv = {v: k for k, v in names.items()}
        out["acquired_used"] = sorted(inv[n] for n in names.values() if ("(%s " % n) in out["found"])
    out["cpu_s"] = round(time.process_time() - t0, 2)
    return out


def cmd_chain(out, wid, cpu_min):
    world = load_world(out, wid)
    quals = {q["family_id"]: q for q in read_jsonl(wpath(out, wid, "QUALIFICATION.jsonl"))}
    if len(quals) != len(world["families"]):
        raise SystemExit("qualify first")
    lib, names, _st = acquired_library(world, list(quals.values()))
    items = []
    for r in world["families"]:
        if r["rung"] not in ("R3", "R4", "R5") or not passes_stage1(r, quals[r["family_id"]]):
            continue
        if not set(r["mechanisms_used"]) <= set(lib):
            continue                                   # CHAIN_C_FAIL; nothing to search
        items.append((r["family_id"] + "|", r))
    return _resumable(wpath(out, wid, "CHAIN.jsonl"), items, lambda r: chain_d(world, r, lib, names), cpu_min,
                      "chain")


# ---------------------------------------------------------------- ablation (SYNTHETIC_DEPTH)
def cmd_ablate(out, wid, cpu_min):
    world = load_world(out, wid)
    mechs = G.mechanisms_of(world)
    quals = {q["family_id"]: q for q in read_jsonl(wpath(out, wid, "QUALIFICATION.jsonl"))}
    chains = {c["family_id"]: c for c in read_jsonl(wpath(out, wid, "CHAIN.jsonl"))}
    lib, names, _st = acquired_library(world, list(quals.values()))
    jobs = []
    for r in world["families"]:
        q = quals[r["family_id"]]
        if r["rung"] == "R2" and passes_stage1(r, q) and q.get("kp", {}).get("status") == "SOLVED":
            jobs.append(("sealed", r["mechanisms_used"][0], r))
        if r["rung"] in ("R3", "R4", "R5") and chains.get(r["family_id"], {}).get("status") == "SOLVED":
            for m in r["mechanisms_used"]:
                jobs.append(("acquired", m, r))
    jobs.sort(key=lambda j: (j[0], j[1], j[2]["index"]))

    def run(job):
        lib_kind, m, r = job
        if lib_kind == "sealed":
            ex = sealed_extra(mechs, drop=m)
            pm = {k: mechs[k].promoted() for k in ex}
        else:
            ex = acquired_extra(world, lib, names, drop=m)
            pm = {n: A.Promoted(n, t, s, rr) for n, (s, rr, t) in ex.items()}
        g = lib_grammar((lib_kind, world["world_id"], "minus", m), ex)
        t0 = time.process_time()
        res = tenum.search(g, _T(r), r["dev"], QCONFIG["B_oracle"], hindsight_test=r["test"])
        d = {"family_id": r["family_id"], "_key": "%s:%s" % (lib_kind, m), "library": lib_kind, "ablated": m,
             "solved": False, "n_dev_consistent": res["n_dev_consistent"], "walk_charge": res["walk_charge"]}
        if res["hindsight_found"] is not None:
            d["solved"] = qualified_on(res["hindsight_found"], r, pm)[0]
            d["found"] = A.show(res["hindsight_found"])
        d["cpu_s"] = round(time.process_time() - t0, 2)
        return d
    items = [(j[2]["family_id"] + "|%s:%s" % (j[0], j[1]), j) for j in jobs]
    return _resumable(wpath(out, wid, "ABLATION.jsonl"), items, run, cpu_min, "ablate")


# ---------------------------------------------------------------- final classes
FUSE = {"fold_of_map": "ACC(s)o MAP(f)", "step_of_f": "ACC(s)o MAP(f)", "scan_of_map": "ACC(s)o MAP(f)",
        "fold_of_filter": "ACC(s)o FILTER(p)", "scan_of_filter": "ACC(s)o FILTER(p)",
        "fold_of_scan": "ACC(s)o ACC(s)", "compose": "MAP(f o f)", "two_maps": "MAP(f o f)",
        "post_map": "f o READ(MAP(f))", "filter_of_map": "FILTER(p) o MAP(f)", "map_of_filter": "MAP(f) o FILTER(p)",
        "pred_of_f": "FILTER(p o f)", "guard_p": "MAP(if p f)", "post_fold": "f o ACC(s)",
        "filter_filter": "FILTER(p o p)"}


def fused_key(rec):
    """Merged skeleton x mechanism set (rule 7): readout suffix dropped; fold and scan merged; init literal is not
    part of the skeleton; compose == two_maps; fold_of_map == step_of_f."""
    parts = rec["skeleton"].split(":")
    rung = parts[0]
    if rung in ("R3", "R4"):
        core = FUSE.get(parts[2].replace("+red", ""), parts[2].replace("+red", ""))
    elif rung == "R5":
        core = parts[1] + "|" + FUSE.get(parts[3].replace("+red", ""), parts[3].replace("+red", ""))
    else:
        core = ":".join(parts[1:]).replace("+red", "")
    return "%s|%s|%s" % (rung, core, "+".join(rec["mechanisms_used"]))


def kind_pair(rec):
    parts = rec["skeleton"].split(":")
    if parts[0] in ("R3", "R4"):
        return parts[1]
    if parts[0] == "R5":
        return parts[2]
    return None


def finalize(world, quals, chains, ablation):
    recs = world["families"]
    qmap = {q["family_id"]: q for q in quals}
    lib, names, cstat = acquired_library(world, quals)
    # rule 2 post-hoc: every R1 family of a mechanism must survive the regression rung
    mech_bad = set()
    for r in recs:
        q = qmap[r["family_id"]]
        if r["rung"] == "R1" and r["gen_class"] == "OK" and q["regression"]["solved"]:
            mech_bad |= set(r["mechanisms_used"])
    abl = {}
    for d in ablation:
        abl.setdefault(d["family_id"], []).append(d)
    out = []
    for r in recs:
        q = dict(qmap[r["family_id"]])
        rn = int(r["rung"][1])
        if r["gen_class"] != "OK":
            cls = r["gen_class"]
        elif q["solved_by"]:
            cls = "TRIVIAL_BY_" + q["solved_by"][0].upper()
        elif q["capture"] > QCONFIG["near_trivial_capture"]:
            cls = "NEAR_TRIVIAL"
        elif rn < 2:
            cls = "QUALIFIED"
        elif set(r["mechanisms_used"]) & mech_bad:
            cls = "MECH_R1_REGRESSION"
        elif not q["witness"]["ok"]:
            cls = "WITNESS_INVALID"
        elif q["base1e6"]["solved"]:
            cls = "TRIVIAL_BY_BASE_1E6"
        elif rn == 2:
            st = q["kp"]["status"]
            cls = "KNOWN_POSITIVE_FAIL:" + st if st != "SOLVED" else "QUALIFIED"
        else:
            missing = sorted(set(r["mechanisms_used"]) - set(lib))
            if missing:
                cls = "CHAIN_C_FAIL:" + "+".join(missing)
            else:
                c = chains.get(r["family_id"])
                q["chain_d"] = c
                cls = "QUALIFIED" if c and c["status"] == "SOLVED" else "CHAIN_D_FAIL:" + (c["status"] if c else "?")
        if cls == "QUALIFIED" and rn >= 2:
            ab = abl.get(r["family_id"], [])
            need = set(r["mechanisms_used"])
            if {d["ablated"] for d in ab} != need:
                cls = "ABLATION_PENDING"
            elif any(d["solved"] for d in ab):
                cls = "SYNTHETIC_DEPTH"
            q["ablation"] = {d["ablated"]: {"solved": d["solved"], "found": d.get("found")} for d in ab}
        if r["rung"] in ("R3", "R4", "R5") and r["family_id"] in chains:
            q["chain_d"] = chains[r["family_id"]]
        q["class"] = cls
        q["fused_key"] = fused_key(r)
        q["kind_pair"] = kind_pair(r)
        if rn < 2:
            q["status"] = "CONTROL"
        else:
            q["status"] = "ADMITTED" if cls == "QUALIFIED" else "REJECTED"
        if r["gen_class"] == "OK":
            lo, hi = QCONFIG["goldilocks_band"]
            c = q["capture"]
            q["band"] = "BELOW_BAND" if c < lo else ("IN_BAND" if c <= hi else "NEAR_TRIVIAL")
        out.append(q)
    # motif cap (rule 7): one admitted family per fused key (lowest index); the rest MOTIF_CAP
    seen = {}
    for q, r in zip(out, recs):
        if q["status"] != "ADMITTED":
            continue
        k = q["fused_key"]
        if k in seen:
            q["class"], q["status"], q["motif_cap_of"] = "MOTIF_CAP", "REJECTED", seen[k]
        else:
            seen[k] = q["family_id"]
    return out, {"acquired": lib, "names": names, "chain_c_by_mechanism": cstat, "mech_r1_regression": sorted(mech_bad)}


# ---------------------------------------------------------------- planted controls
def planted_families(seed=777):
    rng = random.Random("planted|%s" % seed)
    dist = G.CONFIG["dist_base"]
    fams = []
    xs, seen = [], set()
    while len(xs) < 40:
        x = G.sample_list(rng, dist)
        if tuple(x) not in seen:
            seen.add(tuple(x))
            xs.append(x)
    pairs = [[x, rng.randint(-1000, 1000)] for x in xs]
    fams.append({"family_id": "PLANTED-LOOKUP", "output_type": "I", "dev": pairs, "test": pairs,
                 "expect": "lookup solves (test inputs == dev inputs; not contract-conformant)"})
    dev, test = [], []
    while len(dev) < 12 or len(test) < 40:
        x = G.sample_list(rng, dist)
        if tuple(x) in seen:
            continue
        seen.add(tuple(x))
        (dev if len(dev) < 12 else test).append([x, rng.randint(-1000, 1000)])
    fams.append({"family_id": "PLANTED-RANDOM", "output_type": "I", "dev": dev, "test": test,
                 "expect": "nothing solves"})
    table = {v: rng.randint(-50, 50) for v in range(dist["val"][0], dist["val"][1] + 1)}
    dev = [[list(range(dist["val"][0] + 6 * i, min(dist["val"][0] + 6 * i + 6, dist["val"][1] + 1))), None]
           for i in range(8)]
    dev = [[x, [table[v] for v in x]] for x, _ in dev]
    while len(dev) < 12:
        x = G.sample_list(rng, dist)
        dev.append([x, [table[v] for v in x]])
    test = []
    while len(test) < 40:
        x = G.sample_list(rng, dist)
        test.append([x, [table[v] for v in x]])
    fams.append({"family_id": "PLANTED-REACTIVE", "output_type": "L", "dev": dev, "test": test,
                 "expect": "reactive (elementwise table) solves"})
    # regression positives: an alternating power sum (W) and a piecewise map (E), built from contract terms
    rr = random.Random("planted-reg")
    for fid, src, expect in [
            ("PLANTED-REGRESSION-W", "(foldl (lam a (lam b (add (sub 6 a) (mul b b)))) 0 xs)", "regression (W) solves"),
            ("PLANTED-REGRESSION-E", "(map (lam x (if (lt x 0) (mul x x) (add x 3))) xs)", "regression (E) solves"),
            ("PLANTED-NONLINEAR-FOLD", "(foldl (lam a (lam b (sub (mul a b) 1))) 1 xs)",
             "regression does NOT solve (multiplicative accumulator)")]:
        t = A.parse(src)
        allx = []
        while len(allx) < 52:
            x = G.sample_list(rr, dist)
            if A.run(t, x) != A.FAIL and x not in allx:
                allx.append(x)
        ex = [[x, A.run(t, x)] for x in allx]
        fams.append({"family_id": fid, "output_type": "I" if type(ex[0][1]) is int else "L",
                     "dev": ex[:12], "test": ex[12:], "expect": expect})
    return fams


def cmd_controls(out):
    res = []
    for f in planted_families():
        q = {"family_id": f["family_id"], "expect": f["expect"]}
        q["nulls"] = N.run_closed_form(f["dev"], f["test"])
        q["regression"] = regress.run(f["dev"], f["test"], G.CONFIG)
        q["small"] = N.run_small_search(base_grammar(), f["output_type"], f["dev"], f["test"], QCONFIG["B_small"])
        q["solved_by"] = [n for n in QCONFIG["ladder"][:5] if q["nulls"][n]["solved"]] + \
            (["regression"] if q["regression"]["solved"] else []) + (["small_search"] if q["small"]["solved"] else [])
        res.append(q)
        print(f["family_id"], q["solved_by"], flush=True)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "CONTROLS_PLANTED.json"), "w") as fh:
        json.dump(res, fh, sort_keys=True, indent=1)


# ---------------------------------------------------------------- export
def _prereq_frac(order, rung, uses):
    pos = {i: k for k, i in enumerate(order)}
    first = {}
    for i in order:
        if rung[i] == "R1":
            for m in uses[i]:
                first.setdefault(m, pos[i])
    hs = [i for i in order if rung[i] in ("R3", "R4", "R5")]
    if not hs:
        return None
    return round(sum(1 for i in hs if all(first.get(m, 10 ** 9) < pos[i] for m in uses[i])) / len(hs), 3)


def make_orders(seed, fams, ids, yfams=None, yids=None):
    """Orders over opaque ids (evaluator view only)."""
    ok = [r for r in fams if r["gen_class"] == "OK"]
    rung = {ids[r["family_id"]]: r["rung"] for r in ok}
    uses = {ids[r["family_id"]]: r["mechanisms_used"] for r in ok}
    cur = [ids[r["family_id"]] for r in sorted(ok, key=lambda r: (r["rung"], r["index"]))]
    orders = {"CURRICULUM": cur}
    for k in range(QCONFIG["shuffles_uniform"]):
        o = list(cur)
        random.Random("order|uniform|%d|%s" % (k, seed)).shuffle(o)
        orders["SHUFFLED_UNIFORM_%d" % (k + 1)] = o
    hi = [i for i in cur if rung[i] in ("R3", "R4", "R5")]
    lo = [i for i in cur if rung[i] not in ("R3", "R4", "R5")]
    for k in range(QCONFIG["shuffles_anti"]):
        rr = random.Random("order|anti|%d|%s" % (k, seed))
        h, l = list(hi), list(lo)
        rr.shuffle(h)
        rr.shuffle(l)
        orders["SHUFFLED_ANTI_%d" % (k + 1)] = h + l
    orders["DESERT"] = sorted(hi)
    res = {k: {"order": v, "r3plus_prereq_first_frac": _prereq_frac(v, rung, uses)} for k, v in orders.items()}
    if yfams is not None:
        yok = [r for r in yfams if r["gen_class"] == "OK"]
        yr = {yids[(r["yoked_source"], r["family_id"])]: r["rung"] for r in yok}
        yu = {yids[(r["yoked_source"], r["family_id"])]: r["mechanisms_used"] for r in yok}
        ycur = [yids[(r["yoked_source"], r["family_id"])] for r in
                sorted(yok, key=lambda r: (r["rung"], r["yoked_source"], r["index"]))]
        res["YOKED_CURRICULUM"] = {"order": ycur, "r3plus_prereq_first_frac": _prereq_frac(ycur, yr, yu),
                                   "world": "YOKED"}
    return res


def task_json_eval(world, r, q, oid):
    test_dist = G.CONFIG[r["dist_key"]]
    dev_dist = G.CONFIG[r["dev_dist_key"]]
    return {"family_id": r["family_id"], "opaque_id": oid, "rung": r["rung"],
            "generator_seed": {"sha256": world["world_seed_sha256"], "secret": True},
            "witness": r["witness"], "dev": r["dev"], "test": r["test"],
            "input_dist": {"dev": {"name": r["dev_dist_key"], **dev_dist},
                           "test": {"name": r["dist_key"], **test_dist},
                           "conditioned_on_witness_defined": True, "dev_test_disjoint": True},
            "output_type": {"I": "Int", "L": "List", "B": "Bool"}[r["output_type"]],
            "provenance": {"generator": G.CONFIG["version"], "config_sha": world["config_sha"],
                           "qual_config_sha": qconfig_sha(), "world_id": world["world_id"],
                           "status": q["status"] if q else "GEN_REJECTED",
                           "class": q["class"] if q else r["gen_class"]},
            "tribunal": r["tribunal"]}


def arm_json(oid, r):
    return {"id": oid, "dev": r["dev"]}


def _write(path, obj):
    b = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    with open(path, "wb") as f:
        f.write(b)
    return sha_bytes(b)


def cmd_export(secrets, set_name, out):
    with open(secrets) as f:
        nseeds = len(json.load(f)[set_name])
    ev_root, arm_root = os.path.join(out, "evaluator"), os.path.join(out, "arm_view")
    for d in (ev_root, arm_root):                       # rule 5: wipe and rewrite
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
    manifest = {"config_sha": G.config_sha(), "qual_config_sha": qconfig_sha(), "QCONFIG": QCONFIG,
                "regression_bank": regress.bank_summary(G.CONFIG), "generator_config": G.CONFIG, "worlds": {}}
    arm_manifest = {"note": "ARM VIEW: opaque id + dev examples only (E1 v2 rule 4). Load only via this manifest.",
                    "worlds": {}}
    report = {"config_sha": G.config_sha(), "qual_config_sha": qconfig_sha(), "worlds": {}}
    cp = os.path.join(out, "CONTROLS_PLANTED.json")
    if os.path.exists(cp):
        with open(cp) as f:
            report["planted_controls"] = [{"family_id": c["family_id"], "expect": c["expect"],
                                           "solved_by": c["solved_by"],
                                           "regression": c["regression"].get("solved_by")} for c in json.load(f)]
    for i in range(nseeds):
        seed = load_secret(secrets, set_name, i)
        wid = "W" + G.seed_sha256(seed)[:8]
        if not os.path.exists(wpath(out, wid, "WORLD_SEALED.json")):
            print(wid, "missing")
            continue
        world = load_world(out, wid)
        with open(wpath(out, wid, "YOKED_SEALED.json")) as f:
            yoked = json.load(f)
        quals = read_jsonl(wpath(out, wid, "QUALIFICATION.jsonl"))
        if len(quals) != len(world["families"]):
            print(wid, "qualification incomplete")
            continue
        chains = {c["family_id"]: c for c in read_jsonl(wpath(out, wid, "CHAIN.jsonl"))}
        ablation = read_jsonl(wpath(out, wid, "ABLATION.jsonl"))
        finals, lib_info = finalize(world, quals, chains, ablation)
        with open(wpath(out, wid, "FINAL.jsonl"), "w") as f:
            for q in finals:
                f.write(json.dumps(q, sort_keys=True) + "\n")
        fq = {q["family_id"]: q for q in finals}
        ids = {r["family_id"]: opaque(seed, r["family_id"]) for r in world["families"]}
        sib_seed = G.yoke_seed(seed)
        yids = {}
        for r in yoked["families"]:
            yids[(r["yoked_source"], r["family_id"])] = ids[r["family_id"]] if r["yoked_source"] == "target" \
                else opaque(sib_seed, r["family_id"])
        # evaluator view
        ev_files = {}
        evd = os.path.join(ev_root, wid)
        os.makedirs(evd)
        for r in world["families"]:
            if r["gen_class"] != "OK":
                continue
            p = os.path.join(evd, r["family_id"] + ".json")
            ev_files[os.path.relpath(p, out).replace("\\", "/")] = _write(p, task_json_eval(world, r, fq[r["family_id"]],
                                                                                            ids[r["family_id"]]))
        # arm views (world + yoked world), opaque world labels
        arm_tag = "A" + hashlib.sha256(("armworld|%s" % seed).encode()).hexdigest()[:10]
        yarm_tag = "A" + hashlib.sha256(("armworld-yoked|%s" % seed).encode()).hexdigest()[:10]
        arm_files, yarm_files = {}, {}
        for tag, fams, keyf, store in ((arm_tag, world["families"], lambda r: ids[r["family_id"]], arm_files),
                                       (yarm_tag, yoked["families"],
                                        lambda r: yids[(r["yoked_source"], r["family_id"])], yarm_files)):
            d = os.path.join(arm_root, tag)
            os.makedirs(d)
            for r in sorted((r for r in fams if r["gen_class"] == "OK"), key=lambda r: keyf(r)):
                oid = keyf(r)
                p = os.path.join(d, oid + ".json")
                store[os.path.relpath(p, out).replace("\\", "/")] = _write(p, arm_json(oid, r))
        arm_manifest["worlds"][arm_tag] = {"files": arm_files}
        arm_manifest["worlds"][yarm_tag] = {"files": yarm_files}
        ords = make_orders(seed, world["families"], ids, yoked["families"], yids)
        id_map = {ids[r["family_id"]]: {"family_id": r["family_id"], "rung": r["rung"],
                                        "status": fq[r["family_id"]]["status"], "class": fq[r["family_id"]]["class"]}
                  for r in world["families"] if r["gen_class"] == "OK"}
        manifest["worlds"][wid] = {
            "world_seed_sha256": world["world_seed_sha256"], "commitment_set": set_name, "commitment_index": i,
            "sealed_world_sha256": sha_file(wpath(out, wid, "WORLD_SEALED.json")),
            "yoked_sha256": sha_file(wpath(out, wid, "YOKED_SEALED.json")),
            "final_sha256": sha_file(wpath(out, wid, "FINAL.jsonl")),
            "arm_world": arm_tag, "arm_world_yoked": yarm_tag,
            "evaluator_files": ev_files, "id_map": id_map, "orders": ords,
            "yoked_counts": yoked["counts"], "acquired_library": lib_info}
        report["worlds"][wid] = world_report(world, finals, lib_info, quals, ords, yoked)
    with open(os.path.join(arm_root, "ARM_VIEW_MANIFEST.json"), "w") as f:
        json.dump(arm_manifest, f, sort_keys=True, indent=1)
    manifest["arm_view_manifest_sha256"] = sha_file(os.path.join(arm_root, "ARM_VIEW_MANIFEST.json"))
    report["pooled"] = pooled(report)
    with open(os.path.join(out, "WORLD_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=1)
    with open(os.path.join(out, "QUALIFICATION_REPORT.json"), "w") as f:
        json.dump(report, f, sort_keys=True, indent=1)
    with open(os.path.join(out, "QUALIFICATION_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(render_md(report))
    print("exported")
    return report


def world_report(world, finals, lib_info, quals, ords, yoked):
    recs = {r["family_id"]: r for r in world["families"]}
    by = {}
    for q in finals:
        r = recs[q["family_id"]]
        d = by.setdefault(r["rung"], {"generated": 0, "gen_ok": 0, "admitted": 0, "classes": {}, "bands": {},
                                      "admitted_ids": []})
        d["generated"] += 1
        d["gen_ok"] += r["gen_class"] == "OK"
        d["classes"][q["class"]] = d["classes"].get(q["class"], 0) + 1
        if "band" in q:
            d["bands"][q["band"]] = d["bands"].get(q["band"], 0) + 1
        if q["status"] == "ADMITTED":
            d["admitted"] += 1
            d["admitted_ids"].append(q["family_id"])
    for d in by.values():
        d["classes"] = dict(sorted(d["classes"].items()))
    admitted = []
    for q in finals:
        if q["status"] != "ADMITTED":
            continue
        r = recs[q["family_id"]]
        a = {"family_id": q["family_id"], "rung": r["rung"], "skeleton": r["skeleton"],
             "witness_promoted": r["witness_promoted"], "witness_esize": r["witness_esize"],
             "fused_key": q["fused_key"], "kind_pair": q["kind_pair"], "capture": q["capture"],
             "base1e6_n_dev_consistent": q["base1e6"]["n_dev_consistent"]}
        if r["rung"] == "R2":
            a["kp_found"] = q["kp"]["found"]
            a["kp_rank"] = q["kp"]["charge"]
            a["kp_order_free_rank"] = q["kp"].get("order_free_rank")
        else:
            a["chain_found"] = q["chain_d"]["found"]
            a["chain_rank"] = q["chain_d"]["charge"]
            a["chain_order_free_rank"] = q["chain_d"].get("order_free_rank")
            a["acquired_used"] = q["chain_d"].get("acquired_used")
            a["kp_capacity"] = q.get("kp", {}).get("status")
        admitted.append(a)
    r2 = by.get("R2", {}).get("admitted", 0)
    r3 = by.get("R3", {}).get("admitted", 0)
    controls = {
        "R0_trivial": sum(1 for q in finals if q["rung"] == "R0" and q.get("solved_by")),
        "R0_ok": sum(1 for q in finals if q["rung"] == "R0" and q["gen_class"] == "OK"),
        "R1_ok": sum(1 for q in finals if q["rung"] == "R1" and q["gen_class"] == "OK"),
        "R1_regression_solved": sum(1 for q in finals if q["rung"] == "R1" and q["gen_class"] == "OK"
                                    and q["regression"]["solved"]),
        "witness_ok": sum(1 for q in finals if q["gen_class"] == "OK" and q["witness"]["ok"]),
        "families_ok": sum(1 for q in finals if q["gen_class"] == "OK")}
    chain_c = {m: [s["status"] for s in v] for m, v in lib_info["chain_c_by_mechanism"].items()}
    cpu = round(sum(q.get("cpu_s", 0) for q in quals), 1)
    return {"mechanisms": world["mechanisms"], "unfilled_slots": world["mechanism_screen"]["unfilled_slots"],
            "mechanism_rejections": world["mechanism_screen"]["rejections"],
            "regression_rejected_candidates": len(world["mechanism_screen"]["regression_rejects"]),
            "r3_pairs": world["r3_pairs"], "r4_pairs": world["r4_pairs"], "fill": world["fill"],
            "controls": controls, "chain_c": chain_c,
            "acquired": {m: {"term": d["term"], "agree_with_sealed": d["agree_with_sealed"]}
                         for m, d in lib_info["acquired"].items()},
            "mech_r1_regression": lib_info["mech_r1_regression"],
            "by_rung": dict(sorted(by.items())), "admitted": admitted,
            "E1_gate": "PASS" if (r2 >= 1 and r3 >= 1) else "FAIL",
            "orders_prereq_first_frac": {k: v["r3plus_prereq_first_frac"] for k, v in ords.items()},
            "yoked_counts": yoked["counts"], "qualify_cpu_s": cpu}


def pooled(report):
    by, kp, admitted = {}, set(), 0
    for w in report["worlds"].values():
        for rung, d in w["by_rung"].items():
            p = by.setdefault(rung, {"generated": 0, "gen_ok": 0, "admitted": 0, "classes": {}})
            p["generated"] += d["generated"]
            p["gen_ok"] += d["gen_ok"]
            p["admitted"] += d["admitted"]
            for c, n in d["classes"].items():
                p["classes"][c] = p["classes"].get(c, 0) + n
        for a in w["admitted"]:
            if a["kind_pair"]:
                kp.add(a["kind_pair"])
    for p in by.values():
        p["classes"] = dict(sorted(p["classes"].items()))
    any_r3 = by.get("R3", {}).get("admitted", 0)
    gate_worlds = [w for w, d in report["worlds"].items() if d["E1_gate"] == "PASS"]
    if any_r3 == 0:
        e1 = "WORLD_DEMAND_NOT_QUALIFIED"
    elif len(kp) < QCONFIG["kind_pairs_required"]:
        e1 = "WORLD_DEMAND_NOT_QUALIFIED (motif coverage: %d kind-pairs < %d)" % (len(kp), QCONFIG["kind_pairs_required"])
    elif gate_worlds:
        e1 = "WORLD_DEMAND_QUALIFIED (%d/%d worlds pass the E1 gate)" % (len(gate_worlds), len(report["worlds"]))
    else:
        e1 = "WORLD_DEMAND_NOT_QUALIFIED"
    return {"by_rung": dict(sorted(by.items())), "kind_pairs_admitted": sorted(kp), "worlds_passing_gate": gate_worlds,
            "E1": e1}


def render_md(rep):
    L = ["# Beta-04 E1 foundry v2 pilot: qualification report", "",
         "generator config_sha `%s`; qualification config_sha `%s`." % (rep["config_sha"], rep["qual_config_sha"]),
         "", "## 1. Controls (run first)", "", "| planted family | expectation | solved by |", "|---|---|---|"]
    for c in rep.get("planted_controls", []):
        L.append("| %s | %s | %s |" % (c["family_id"], c["expect"], ", ".join(c["solved_by"]) or "none"))
    L += ["", "| world | R0 solved by a trivial rung | R1 solved by regression (must be 0) | witnesses verified |",
          "|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        c = w["controls"]
        L.append("| %s | %d/%d | %d/%d | %d/%d |" % (wid, c["R0_trivial"], c["R0_ok"], c["R1_regression_solved"],
                                                      c["R1_ok"], c["witness_ok"], c["families_ok"]))
    L += ["", "## 2. Admission by world and rung", "",
          "| world | rung | generated | gen OK | admitted | class histogram |", "|---|---|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        for rung, d in w["by_rung"].items():
            L.append("| %s | %s | %d | %d | %s | %s |" % (wid, rung, d["generated"], d["gen_ok"],
                                                          d["admitted"] if rung not in ("R0", "R1") else "(control)",
                                                          "; ".join("%s %d" % kv for kv in d["classes"].items())))
    L += ["", "| world | mechanisms (unfilled) | chain (c) by mechanism | E1 gate |", "|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        L.append("| %s | %s (%s) | %s | **%s** |" % (
            wid, ", ".join(m["name"] for m in w["mechanisms"]), ", ".join(w["unfilled_slots"]) or "-",
            "; ".join("%s: %s" % (m, "/".join(v)) for m, v in sorted(w["chain_c"].items())), w["E1_gate"]))
    L += ["", "## 3. Pooled", "", "| rung | generated | gen OK | admitted | class histogram |", "|---|---|---|---|---|"]
    for rung, d in rep["pooled"]["by_rung"].items():
        L.append("| %s | %d | %d | %s | %s |" % (rung, d["generated"], d["gen_ok"],
                                                 d["admitted"] if rung not in ("R0", "R1") else "(control)",
                                                 "; ".join("%s %d" % kv for kv in d["classes"].items())))
    L += ["", "Kind-pairs among admitted R3/R4/R5: %s. **E1: %s**" % (
        ", ".join(rep["pooled"]["kind_pairs_admitted"]) or "none", rep["pooled"]["E1"]), "",
        "## 4. Admitted families", "", "| family | skeleton | promoted witness | solution found | rank (order-free) |",
        "|---|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        for a in w["admitted"]:
            found = a.get("kp_found") or a.get("chain_found")
            rank = a.get("kp_rank") or a.get("chain_rank")
            ofr = a.get("kp_order_free_rank") or a.get("chain_order_free_rank")
            L.append("| %s | %s | `%s` | `%s` | %s (%s) |" % (a["family_id"], a["skeleton"], a["witness_promoted"],
                                                            found, rank, ofr))
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--secrets")
    ap.add_argument("--set", default="pilot_v2")
    ap.add_argument("--index", type=int)
    ap.add_argument("--world")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--cpu-min", type=float, default=13.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.cmd == "world":
        cmd_world(a.secrets, a.set, a.index, a.out)
    elif a.cmd == "qualify":
        cmd_qualify(a.out, a.world, a.cpu_min)
    elif a.cmd == "chain":
        cmd_chain(a.out, a.world, a.cpu_min)
    elif a.cmd == "ablate":
        cmd_ablate(a.out, a.world, a.cpu_min)
    elif a.cmd == "controls":
        cmd_controls(a.out)
    elif a.cmd == "export":
        cmd_export(a.secrets, a.set, a.out)
    elif a.cmd == "config":
        print("generator config_sha256", G.config_sha())
        print("qualification config_sha256", qconfig_sha())
        print("regression bank sha256", regress.bank_summary(G.CONFIG)["sha256"])
    else:
        raise SystemExit("unknown command")


if __name__ == "__main__":
    main()
