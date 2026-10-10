"""Foundry driver: world generation, per-family qualification (null ladder + known positive), admission gate,
planted controls, task export, manifest and report.

    python qualify.py world    --seed S [--out DIR]
    python qualify.py qualify  --seed S [--out DIR] [--cpu-min 13]     (resumable; each run stays under the cap)
    python qualify.py controls [--out DIR] [--oracle-seed S]
    python qualify.py report   --seeds S1,S2,... [--out DIR]

Admission (family at rung R >= 2):
    ADMITTED  iff  every null-ladder baseline is not SOLVED on test (closed-form baselines in HINDSIGHT mode;
                   small search = first dev-consistent within B_small)
              and  the KNOWN POSITIVE passes: the witness is verified by interpreter A, AND the oracle-library
                   search (base grammar + the world's true level-1 mechanisms as primitives) finds a dev-consistent
                   program within B_oracle that is SOLVED on test
              and  (R3/R4) every mechanism used has >= 1 R1 family in the world whose known positive passes.
    Otherwise REJECTED with the first class that applies, in this order:
    FAIL_PRONE | DEGENERATE | DUPLICATE (generation screens) | TRIVIAL_BY_<baseline> | WITNESS_INVALID |
    KNOWN_POSITIVE_FAIL:NOT_FOUND | KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED | PREREQ_MISSING.
R0 / R1 families are CONTROLS. They get the same measurements and the same class, but are never "admitted".
No treatment arm is consulted anywhere in this file.
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.setrecursionlimit(10000)

import interp_a as A
import generator as G
import nulls as N
import tenum

QCONFIG = {
    "version": "b04-foundry-qual-v0.1",
    "B_small": 100_000,
    "B_oracle": 1_000_000,
    "closed_form_mode": "hindsight",
    "small_search_mode": "hindsight (any dev-consistent program within B_small solving test); the contract-protocol "
                         "first-dev-consistent verdict is recorded as selected_solved",
    "ladder": ["constant", "lookup", "reactive", "history2", "library", "small_search"],
    "goldilocks_band": [0.2, 0.8],
    "base_memo_max": 7, "oracle_memo_max": 6,          # memory only; enumeration order is unchanged
    "base_at_oracle_budget": "R>=2 families that pass every null and the known positive",
}
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "pilot")


def qconfig_sha():
    return hashlib.sha256(json.dumps(QCONFIG, sort_keys=True).encode()).hexdigest()


def sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def wpath(out, seed, name):
    d = os.path.join(out, "W%s" % seed)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)


# ---------------------------------------------------------------- world
def cmd_world(seed, out):
    w = G.build_world(seed)
    p = wpath(out, seed, "WORLD_SEALED.json")
    with open(p, "wb") as f:
        f.write(G.world_bytes(w))
    print("wrote", p, sha_file(p))
    return w


def load_world(out, seed):
    with open(wpath(out, seed, "WORLD_SEALED.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- per-family qualification
_BASE_G = None
_ORACLE_G = {}


def base_grammar():
    global _BASE_G
    if _BASE_G is None:
        _BASE_G = tenum.Grammar(memo_max=QCONFIG["base_memo_max"])
    return _BASE_G


def oracle_grammar(world):
    key = world["world_id"]
    if key not in _ORACLE_G:
        mechs = G.mechanisms_of(world)
        _ORACLE_G.clear()                                 # one world per process at a time (memory)
        _ORACLE_G[key] = tenum.Grammar({m.name: (m.sig, m.ret, m.term) for m in mechs.values()},
                                       memo_max=QCONFIG["oracle_memo_max"])
    return _ORACLE_G[key]


def _units(term, xs, promoted=None):
    v, u = A.run(term, xs, promoted=promoted, with_units=True)
    return v, u.promoted, u.expanded


def witness_check(rec, mechs):
    base = A.parse(rec["witness"])
    prom = A.parse(rec["witness_promoted"])
    pmap = {m.name: m.promoted() for m in mechs.values()}
    out = {}
    try:
        A.typecheck(base)
        A.typecheck(prom, promoted=pmap)
        out["typed"] = True
    except A.TypeErr as e:
        out["typed"] = False
        out["error"] = str(e)
        out["ok"] = False
        return out
    ok = True
    up, ue = [], []
    for xs, y in rec["dev"] + rec["test"]:
        if A.run(base, xs) != y:
            ok = False
        v, a, b = _units(prom, xs, pmap)
        if v != y:
            ok = False
        up.append(a)
        ue.append(b)
    out["ok"] = ok
    out["units_promoted_mean"] = round(sum(up) / len(up), 2)
    out["units_expanded_mean"] = round(sum(ue) / len(ue), 2)
    return out


def oracle_search(world, rec, mechs, budget):
    g = oracle_grammar(world)
    T = {"I": "I", "L": "L", "B": "B"}[rec["output_type"]]
    t0 = time.process_time()
    r = tenum.search(g, T, rec["dev"], budget)
    out = {"budget": budget, "charge": r["charge"], "size_reached": r["size_reached"],
           "complete_size": r["complete_size"], "cpu_s": round(time.process_time() - t0, 2)}
    if r["found"] is None:
        out["found"] = None
        out["status"] = "NOT_FOUND"
        return out
    prog = r["found"]
    pmap = {m.name: m.promoted() for m in mechs.values()}
    out["found"] = A.show(prog)
    out["found_esize"] = A.esize(prog)
    exp = G.expand(prog, mechs)
    out["found_expanded"] = A.show(exp)
    out["found_expanded_esize"] = A.esize(exp)
    out["mechanisms_in_found"] = sorted({n for n in mechs if ("(%s " % n) in out["found"]})
    test_ok = sum(1 for xs, y in rec["test"] if A.run(prog, xs, promoted=pmap) == y)
    out["test_acc"] = round(test_ok / len(rec["test"]), 4)
    out["status"] = "SOLVED" if test_ok == len(rec["test"]) else "DEV_UNDERDETERMINED"
    trib = rec["tribunal"]
    out["tribunal_agree"] = round(sum(1 for xs, y in trib if A.run(prog, xs, promoted=pmap) == y) / len(trib), 4)
    # expanded program must agree with the promoted one (promotion semantics check)
    out["expansion_consistent"] = all(A.run(exp, xs) == A.run(prog, xs, promoted=pmap)
                                      for xs, _y in rec["dev"] + rec["test"] + trib)
    return out


def qualify_family(world, rec, mechs):
    t0 = time.process_time()
    q = {"family_id": rec["family_id"], "rung": rec["rung"], "gen_class": rec["gen_class"]}
    if rec["gen_class"] != "OK":
        q["class"] = rec["gen_class"]
        return q
    dev, test, trib = rec["dev"], rec["test"], rec["tribunal"]
    q["witness"] = witness_check(rec, mechs)
    q["nulls"] = N.run_closed_form(dev, test, trib)
    q["small"] = N.run_small_search(base_grammar(), rec["output_type"], dev, test, QCONFIG["B_small"], trib)
    q["oracle"] = oracle_search(world, rec, mechs, QCONFIG["B_oracle"])
    solved_by = [n for n in QCONFIG["ladder"][:-1] if q["nulls"][n]["solved"]]
    if q["small"]["solved"]:
        solved_by.append("small_search")
    q["solved_by"] = solved_by
    kp = q["witness"]["ok"] and q["oracle"]["status"] == "SOLVED"
    q["known_positive"] = kp
    if int(rec["rung"][1]) >= 2 and not solved_by and kp:
        q["base_at_oracle_budget"] = N.run_small_search(base_grammar(), rec["output_type"], dev, test,
                                                        QCONFIG["B_oracle"], trib)
    q["cpu_s"] = round(time.process_time() - t0, 2)
    return q


def cmd_qualify(seed, out, cpu_min=13.0):
    world = load_world(out, seed)
    mechs = G.mechanisms_of(world)
    qp = wpath(out, seed, "QUALIFICATION.jsonl")
    done = set()
    if os.path.exists(qp):
        with open(qp) as f:
            for line in f:
                done.add(json.loads(line)["family_id"])
    t0 = time.process_time()
    n = 0
    with open(qp, "a") as f:
        for rec in world["families"]:
            if rec["family_id"] in done:
                continue
            if time.process_time() - t0 > cpu_min * 60:
                print("cpu cap reached; resumable", flush=True)
                return False
            q = qualify_family(world, rec, mechs)
            f.write(json.dumps(q, sort_keys=True) + "\n")
            f.flush()
            n += 1
            print(rec["family_id"], q.get("class") or ("solved_by=%s kp=%s orank=%s cpu=%s" % (
                q["solved_by"], q["known_positive"], q["oracle"]["charge"], q["cpu_s"])), flush=True)
    print("done", n, "families, cpu_s", round(time.process_time() - t0, 1))
    return True


# ---------------------------------------------------------------- classification
def finalize(world, quals):
    """Apply the admission gate. Needs every family's raw qualification (for R3/R4 prerequisites)."""
    byid = {q["family_id"]: q for q in quals}
    recs = {r["family_id"]: r for r in world["families"]}
    r1_kp = {}
    for fid, q in byid.items():
        r = recs[fid]
        if r["rung"] == "R1" and q.get("known_positive"):
            for m in r["mechanisms_used"]:
                r1_kp[m] = r1_kp.get(m, 0) + 1
    out = []
    for r in world["families"]:
        q = dict(byid[r["family_id"]])
        if r["gen_class"] != "OK":
            cls = r["gen_class"]
        elif q["solved_by"]:
            cls = "TRIVIAL_BY_" + q["solved_by"][0].upper()
        elif not q["witness"]["ok"]:
            cls = "WITNESS_INVALID"
        elif q["oracle"]["status"] != "SOLVED":
            cls = "KNOWN_POSITIVE_FAIL:" + q["oracle"]["status"]
        elif r["rung"] in ("R3", "R4") and any(r1_kp.get(m, 0) == 0 for m in r["mechanisms_used"]):
            cls = "PREREQ_MISSING"
        else:
            cls = "QUALIFIED"
        q["class"] = cls
        rn = int(r["rung"][1])
        q["status"] = ("ADMITTED" if cls == "QUALIFIED" else "REJECTED") if rn >= 2 else "CONTROL"
        if r["gen_class"] == "OK":
            # WTP-05 Goldilocks label (reported, NOT part of the gate): the best dev-consistent null's test accuracy
            caps = [q["nulls"][n].get("best_consistent_test_acc", 0.0) for n in QCONFIG["ladder"][:-1]]
            caps.append(q["small"].get("test_acc", 0.0) if q["small"].get("found") else 0.0)
            cap = max(caps)
            lo, hi = QCONFIG["goldilocks_band"]
            q["null_capture"] = cap
            q["goldilocks"] = "DESERT_HARSH" if cap < lo else ("GOLDILOCKS" if cap <= hi else "NEAR_TRIVIAL")
            # headroom proof (coordinator addendum 1)
            if q["oracle"]["status"] == "SOLVED":
                q["headroom"] = {"oracle_rank": q["oracle"]["charge"], "B_small": QCONFIG["B_small"],
                                 "B_oracle": QCONFIG["B_oracle"],
                                 "kp_within_B_small": q["oracle"]["charge"] <= QCONFIG["B_small"],
                                 "nulls_all_fail": not q["solved_by"]}
            simplest = r["witness_esize"]
            if q["oracle"].get("status") == "SOLVED":
                simplest = min(simplest, q["oracle"]["found_expanded_esize"])
            if q["small"].get("solved"):
                simplest = min(simplest, q["small"]["hindsight_esize"])
            q["simplest_known_esize"] = simplest
            q["small_reach_complete_size"] = q["small"]["complete_size"]
            q["gap_simplest_minus_reach"] = simplest - q["small"]["complete_size"]
        out.append(q)
    return out


# ---------------------------------------------------------------- planted controls
def planted_families(seed=777):
    rng = random.Random("planted|%s" % seed)
    dist = G.CONFIG["dist_base"]
    fams = []
    # (1) lookup-only: TEST INPUTS = DEV INPUTS (deliberate contract violation, calibration only), random outputs
    xs = []
    seen = set()
    while len(xs) < 40:
        x = G.sample_list(rng, dist)
        if tuple(x) not in seen:
            seen.add(tuple(x))
            xs.append(x)
    pairs = [[x, rng.randint(-1000, 1000)] for x in xs]
    fams.append({"family_id": "PLANTED-LOOKUP", "rung": "PLANTED", "output_type": "I", "dev": pairs,
                 "test": pairs, "expect": "lookup solves; constant/reactive/history2/library/small fail",
                 "note": "test inputs == dev inputs; NOT contract-conformant; calibration only"})
    # (2) structureless negative: random outputs, disjoint test -> nothing solves, the known positive must fail
    dev, test = [], []
    seen = set()
    while len(dev) < 10 or len(test) < 40:
        x = G.sample_list(rng, dist)
        if tuple(x) in seen:
            continue
        seen.add(tuple(x))
        (dev if len(dev) < 10 else test).append([x, rng.randint(-1000, 1000)])
    fams.append({"family_id": "PLANTED-RANDOM", "rung": "PLANTED", "output_type": "I", "dev": dev, "test": test,
                 "expect": "no baseline solves; oracle-library search fails -> KNOWN_POSITIVE_FAIL"})
    # (3) reactive-only: elementwise random table over the value range, test elements all seen in dev
    table = {v: rng.randint(-50, 50) for v in range(dist["val"][0], dist["val"][1] + 1)}
    dev, test = [], []
    dev_x = [list(range(dist["val"][0] + 6 * i, min(dist["val"][0] + 6 * i + 6, dist["val"][1] + 1)))
             for i in range(8)]
    for x in dev_x:
        dev.append([x, [table[v] for v in x]])
    while len(dev) < 10:
        x = G.sample_list(rng, dist)
        dev.append([x, [table[v] for v in x]])
    while len(test) < 40:
        x = G.sample_list(rng, dist)
        if any(x == d for d, _ in dev):
            continue
        test.append([x, [table[v] for v in x]])
    fams.append({"family_id": "PLANTED-REACTIVE", "rung": "PLANTED", "output_type": "L", "dev": dev, "test": test,
                 "expect": "reactive (elementwise table) solves; constant/lookup/small fail"})
    return fams


def cmd_controls(out, oracle_seed):
    world = load_world(out, oracle_seed)
    mechs = G.mechanisms_of(world)
    res = []
    for f in planted_families():
        q = {"family_id": f["family_id"], "expect": f["expect"], "note": f.get("note")}
        q["nulls"] = N.run_closed_form(f["dev"], f["test"])
        q["small"] = N.run_small_search(base_grammar(), f["output_type"], f["dev"], f["test"], QCONFIG["B_small"])
        rec = dict(f, tribunal=[[x, y] for x, y in f["test"][:4]])
        q["oracle"] = oracle_search(world, rec, mechs, QCONFIG["B_oracle"])
        q["solved_by"] = [n for n in QCONFIG["ladder"][:-1] if q["nulls"][n]["solved"]] + \
            (["small_search"] if q["small"]["solved"] else [])
        res.append(q)
        print(f["family_id"], q["solved_by"], q["oracle"]["status"], flush=True)
    p = os.path.join(out, "CONTROLS_PLANTED.json")
    with open(p, "w") as fh:
        json.dump(res, fh, sort_keys=True, indent=1)
    print("wrote", p)


# ---------------------------------------------------------------- export + report
TASK_KEYS = ["family_id", "rung", "generator_seed", "witness", "dev", "test", "input_dist", "output_type",
             "provenance", "tribunal"]


def task_json(world, r, q):
    dist = G.CONFIG[r["dist_key"]]
    return {
        "family_id": r["family_id"], "rung": r["rung"], "generator_seed": world["world_seed"],
        "witness": r["witness"], "dev": r["dev"], "test": r["test"],
        "input_dist": {"name": r["dist_key"], "len": dist["len"], "val": dist["val"],
                       "conditioned_on_witness_defined": True,
                       "dev_test_disjoint": True},
        "output_type": {"I": "Int", "L": "List", "B": "Bool"}[r["output_type"]],
        "provenance": {"generator": G.CONFIG["version"], "config_sha": world["config_sha"],
                       "qual_config_sha": qconfig_sha(), "world_id": world["world_id"], "index": r["index"],
                       "status": q["status"], "class": q["class"],
                       "truth": "sealed: W%s/WORLD_SEALED.json" % world["world_seed"]},
        "tribunal": r["tribunal"],
    }


def orders(world, finals, seed):
    fams = [r for r in world["families"] if r["gen_class"] == "OK"]
    ids = [r["family_id"] for r in fams]
    rung = {r["family_id"]: r["rung"] for r in fams}
    uses = {r["family_id"]: r["mechanisms_used"] for r in fams}
    curriculum = sorted(ids, key=lambda i: (rung[i], i))
    rr = random.Random("shuffle|%s" % seed)
    uniform = list(ids)
    rr.shuffle(uniform)
    hi = [i for i in ids if rung[i] in ("R3", "R4")]
    lo = [i for i in ids if rung[i] not in ("R3", "R4")]
    rr.shuffle(hi)
    rr.shuffle(lo)
    anti = hi + lo
    desert = sorted(hi)

    def precedence(order):
        pos = {i: k for k, i in enumerate(order)}
        r1_first = {}
        for i in order:
            if rung[i] == "R1":
                for m in uses[i]:
                    r1_first.setdefault(m, pos[i])
        hs = [i for i in order if rung[i] in ("R3", "R4")]
        if not hs:
            return None
        ok = sum(1 for i in hs if all(r1_first.get(m, 10 ** 9) < pos[i] for m in uses[i]))
        return round(ok / len(hs), 3)

    return {
        "CURRICULUM": {"order": curriculum, "r3r4_prereq_first_frac": precedence(curriculum),
                       "meaning": "rung order; each R3/R4 family's mechanisms appear alone (R1) earlier"},
        "SHUFFLED_UNIFORM": {"order": uniform, "r3r4_prereq_first_frac": precedence(uniform),
                             "meaning": "seeded uniform permutation of the same families"},
        "SHUFFLED_ANTI": {"order": anti, "r3r4_prereq_first_frac": precedence(anti),
                          "meaning": "same families; every R3/R4 family before any R0-R2 family (mechanisms NOT "
                                     "presented first) -- the history-contingency contrast"},
        "DESERT": {"order": desert, "r3r4_prereq_first_frac": precedence(desert),
                   "meaning": "R3/R4 only, no stepping stones (WTP-05 DESERT condition)"},
    }


def _median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def world_metrics(world, finals):
    recs = {r["family_id"]: r for r in world["families"]}
    by = {}
    for q in finals:
        r = recs[q["family_id"]]
        d = by.setdefault(r["rung"], {"generated": 0, "classes": {}, "statuses": {}, "witness_esize": [],
                                      "admitted_witness_esize": [], "simplest_known": [], "gap": [],
                                      "oracle_rank_solved": [], "oracle_not_found": 0, "solved_by_counts": {},
                                      "goldilocks": {}, "kp_pass": 0, "kp_within_B_small": 0,
                                      "base_at_B_oracle_found_solved": 0, "base_at_B_oracle_run": 0,
                                      "out_types": {}, "len_mean": [], "val_absmax": [], "skeletons": {}})
        d["generated"] += 1
        d["classes"][q["class"]] = d["classes"].get(q["class"], 0) + 1
        d["statuses"][q["status"]] = d["statuses"].get(q["status"], 0) + 1
        d["skeletons"][r["skeleton"]] = d["skeletons"].get(r["skeleton"], 0) + 1
        if r["gen_class"] != "OK":
            continue
        d["witness_esize"].append(r["witness_esize"])
        d["out_types"][r["output_type"]] = d["out_types"].get(r["output_type"], 0) + 1
        xs = [x for x, _y in r["dev"] + r["test"]]
        d["len_mean"].append(sum(len(x) for x in xs) / len(xs))
        d["val_absmax"].append(max(abs(v) for x in xs for v in x))
        for n in q["solved_by"]:
            d["solved_by_counts"][n] = d["solved_by_counts"].get(n, 0) + 1
        d["goldilocks"][q["goldilocks"]] = d["goldilocks"].get(q["goldilocks"], 0) + 1
        if q["known_positive"]:
            d["kp_pass"] += 1
            if set(r["mechanisms_used"]) <= set(q["oracle"].get("mechanisms_in_found", [])):
                d["kp_uses_all_mechs"] = d.get("kp_uses_all_mechs", 0) + 1
            if q["status"] == "ADMITTED" and set(r["mechanisms_used"]) <= set(q["oracle"].get("mechanisms_in_found", [])):
                d["admitted_kp_uses_all_mechs"] = d.get("admitted_kp_uses_all_mechs", 0) + 1
            d["oracle_rank_solved"].append(q["oracle"]["charge"])
            if q["oracle"]["charge"] <= QCONFIG["B_small"]:
                d["kp_within_B_small"] += 1
        if q["oracle"]["status"] == "NOT_FOUND":
            d["oracle_not_found"] += 1
        d["simplest_known"].append(q["simplest_known_esize"])
        d["gap"].append(q["gap_simplest_minus_reach"])
        if q["status"] == "ADMITTED":
            d["admitted_witness_esize"].append(r["witness_esize"])
        if "base_at_oracle_budget" in q:
            d["base_at_B_oracle_run"] += 1
            if q["base_at_oracle_budget"]["solved"]:
                d["base_at_B_oracle_found_solved"] += 1
    out = {}
    for rung, d in sorted(by.items()):
        adm = d["statuses"].get("ADMITTED", 0)
        ok = sum(v for k, v in d["out_types"].items())
        out[rung] = {
            "generated": d["generated"], "passed_generation_screens": ok,
            "admitted": adm if int(rung[1]) >= 2 else None,
            "admission_yield_of_generated": round(adm / d["generated"], 3) if int(rung[1]) >= 2 else None,
            "qualified_controls": d["classes"].get("QUALIFIED", 0) if int(rung[1]) < 2 else None,
            "class_histogram": dict(sorted(d["classes"].items())),
            "solved_by_counts": dict(sorted(d["solved_by_counts"].items())),
            "known_positive_pass": d["kp_pass"], "kp_within_B_small": d["kp_within_B_small"],
            "kp_solution_uses_all_witness_mechanisms": d.get("kp_uses_all_mechs", 0),
            "admitted_kp_solution_uses_all_witness_mechanisms": d.get("admitted_kp_uses_all_mechs", 0),
            "oracle_not_found": d["oracle_not_found"],
            "oracle_rank_median": _median(d["oracle_rank_solved"]),
            "oracle_rank_max": max(d["oracle_rank_solved"]) if d["oracle_rank_solved"] else None,
            "witness_esize_min_median_max": [min(d["witness_esize"] or [0]), _median(d["witness_esize"]),
                                             max(d["witness_esize"] or [0])],
            "admitted_witness_esize_min": min(d["admitted_witness_esize"]) if d["admitted_witness_esize"] else None,
            "simplest_known_esize_median": _median(d["simplest_known"]),
            "gap_simplest_minus_small_reach_median": _median(d["gap"]),
            "base_search_at_B_oracle": {"run": d["base_at_B_oracle_run"],
                                        "solved": d["base_at_B_oracle_found_solved"]},
            "goldilocks": dict(sorted(d["goldilocks"].items())),
            "output_types": d["out_types"], "skeletons": dict(sorted(d["skeletons"].items())),
            "input_len_mean": round(sum(d["len_mean"]) / len(d["len_mean"]), 2) if d["len_mean"] else None,
            "input_val_absmax": max(d["val_absmax"]) if d["val_absmax"] else None,
        }
    return out


def cmd_report(seeds, out):
    report = {"config_sha": G.config_sha(), "qual_config_sha": qconfig_sha(), "QCONFIG": QCONFIG,
              "worlds": {}}
    manifest = {"config_sha": G.config_sha(), "qual_config_sha": qconfig_sha(), "generator_config": G.CONFIG,
                "worlds": {}}
    cp = os.path.join(out, "CONTROLS_PLANTED.json")
    if os.path.exists(cp):
        with open(cp) as f:
            report["planted_controls"] = [{k: v for k, v in c.items() if k in
                                           ("family_id", "expect", "note", "solved_by")} |
                                          {"oracle_status": c["oracle"]["status"]} for c in json.load(f)]
    for seed in seeds:
        world = load_world(out, seed)
        with open(wpath(out, seed, "QUALIFICATION.jsonl")) as f:
            quals = [json.loads(l) for l in f]
        if len(quals) != len(world["families"]):
            print("W%s incomplete: %d/%d" % (seed, len(quals), len(world["families"])))
            continue
        finals = finalize(world, quals)
        fp = wpath(out, seed, "FINAL.jsonl")
        with open(fp, "w") as f:
            for q in finals:
                f.write(json.dumps(q, sort_keys=True) + "\n")
        recs = {r["family_id"]: r for r in world["families"]}
        files = {}
        for q in finals:
            r = recs[q["family_id"]]
            if r["gen_class"] != "OK":
                continue
            sub = {"ADMITTED": "admitted", "CONTROL": "controls", "REJECTED": "rejected"}[q["status"]]
            d = os.path.join(out, "W%s" % seed, "tasks", sub)
            os.makedirs(d, exist_ok=True)
            p = os.path.join(d, r["family_id"] + ".json")
            with open(p, "w") as f:
                json.dump(task_json(world, r, q), f, sort_keys=True)
            files[os.path.relpath(p, out).replace("\\", "/")] = sha_file(p)
        ords = orders(world, finals, seed)
        manifest["worlds"][world["world_id"]] = {
            "world_seed": seed, "sealed_world_file": "W%s/WORLD_SEALED.json" % seed,
            "sealed_world_sha256": sha_file(wpath(out, seed, "WORLD_SEALED.json")),
            "qualification_sha256": sha_file(wpath(out, seed, "QUALIFICATION.jsonl")),
            "final_sha256": sha_file(fp), "task_files": files, "orders": ords,
            "mechanisms_sealed": True,
        }
        controls = {
            "R0_solved_by_trivial": sum(1 for q in finals if q["rung"] == "R0" and q["gen_class"] == "OK"
                                        and q["solved_by"]),
            "R0_total_ok": sum(1 for q in finals if q["rung"] == "R0" and q["gen_class"] == "OK"),
            "R1_kp_pass": sum(1 for q in finals if q["rung"] == "R1" and q.get("known_positive")),
            "R1_total_ok": sum(1 for q in finals if q["rung"] == "R1" and q["gen_class"] == "OK"),
            "admitted_kp_pass": sum(1 for q in finals if q["status"] == "ADMITTED" and q["known_positive"]),
            "admitted": sum(1 for q in finals if q["status"] == "ADMITTED"),
            "witness_ok": sum(1 for q in finals if q["gen_class"] == "OK" and q["witness"]["ok"]),
            "expansion_consistent": sum(1 for q in finals if q["gen_class"] == "OK"
                                        and q["oracle"].get("expansion_consistent", True)),
            "families_ok": sum(1 for q in finals if q["gen_class"] == "OK"),
        }
        report["worlds"][world["world_id"]] = {
            "mechanisms": world["mechanisms"], "mechanism_screen": world["mechanism_screen"],
            "r3_pairs": world["r3_pairs"], "r4_pairs": world["r4_pairs"], "fill": world["fill"],
            "controls": controls, "by_rung": world_metrics(world, finals),
            "orders_prereq_first_frac": {k: v["r3r4_prereq_first_frac"] for k, v in ords.items()},
            "admitted": [{"family_id": q["family_id"], "rung": q["rung"], "skeleton": recs[q["family_id"]]["skeleton"],
                          "witness_promoted": recs[q["family_id"]]["witness_promoted"],
                          "witness_esize": recs[q["family_id"]]["witness_esize"],
                          "oracle_found": q["oracle"]["found"], "oracle_rank": q["oracle"]["charge"],
                          "oracle_uses_all_witness_mechanisms": set(recs[q["family_id"]]["mechanisms_used"]) <=
                          set(q["oracle"].get("mechanisms_in_found", [])),
                          "headroom": q.get("headroom"), "goldilocks": q.get("goldilocks"),
                          "null_capture": q.get("null_capture"),
                          "base_at_B_oracle": (q.get("base_at_oracle_budget") or {}).get("solved")}
                         for q in finals if q["status"] == "ADMITTED"],
            "cpu_s_total": round(sum(q.get("cpu_s", 0) for q in quals), 1),
        }
    with open(os.path.join(out, "WORLD_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=1)
    with open(os.path.join(out, "QUALIFICATION_REPORT.json"), "w") as f:
        json.dump(report, f, sort_keys=True, indent=1)
    with open(os.path.join(out, "QUALIFICATION_REPORT.md"), "w") as f:
        f.write(render_md(report))
    print("wrote manifest + report")
    return report


def render_md(rep):
    L = ["# Beta-04 E1 foundry pilot: qualification report", "",
         "generator config_sha `%s`; qualification config_sha `%s`; B_small=%d, B_oracle=%d. Closed-form nulls in "
         "HINDSIGHT mode." % (rep["config_sha"], rep["qual_config_sha"], QCONFIG["B_small"], QCONFIG["B_oracle"]),
         "", "## 1. Controls (run first)", "", "### 1a. Planted controls", "",
         "| family | expectation | solved by | oracle-library KP |", "|---|---|---|---|"]
    for c in rep.get("planted_controls", []):
        L.append("| %s | %s | %s | %s |" % (c["family_id"], c["expect"], ", ".join(c["solved_by"]) or "none",
                                            c["oracle_status"]))
    L += ["", "### 1b. Per-world controls", "",
          "| world | R0 solved by a trivial baseline | R1 KP pass | admitted with KP pass | witness verified (A) | "
          "promoted==expanded |", "|---|---|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        c = w["controls"]
        L.append("| %s | %d/%d | %d/%d | %d/%d | %d/%d | %d/%d |" % (
            wid, c["R0_solved_by_trivial"], c["R0_total_ok"], c["R1_kp_pass"], c["R1_total_ok"],
            c["admitted_kp_pass"], c["admitted"], c["witness_ok"], c["families_ok"], c["expansion_consistent"],
            c["families_ok"]))
    L += ["", "## 2. Admission by world and rung", "",
          "| world | rung | generated | passed gen screens | admitted (R>=2) / qualified controls (R0-R1) | KP pass "
          "| KP rank <= B_small | oracle median rank | class histogram |", "|---|---|---|---|---|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        for rung, m in w["by_rung"].items():
            adm = m["admitted"] if m["admitted"] is not None else m["qualified_controls"]
            L.append("| %s | %s | %d | %d | %s | %d | %d | %s | %s |" % (
                wid, rung, m["generated"], m["passed_generation_screens"], adm, m["known_positive_pass"],
                m["kp_within_B_small"], m["oracle_rank_median"],
                "; ".join("%s %d" % kv for kv in m["class_histogram"].items())))
    L += ["", "## 3. Admitted families (headroom proof)", "",
          "| family | skeleton | promoted witness | witness esize | oracle solution | oracle rank | KP <= B_small | "
          "oracle uses all witness mechanisms | base search solves at B_oracle | null capture (band) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for wid, w in rep["worlds"].items():
        for a in w["admitted"]:
            h = a["headroom"] or {}
            L.append("| %s | %s | `%s` | %d | `%s` | %s | %s | %s | %s | %.3f (%s) |" % (
                a["family_id"], a["skeleton"], a["witness_promoted"], a["witness_esize"], a["oracle_found"],
                a["oracle_rank"], h.get("kp_within_B_small"), a["oracle_uses_all_witness_mechanisms"],
                a["base_at_B_oracle"], a["null_capture"] or 0, a["goldilocks"]))
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--seeds")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--cpu-min", type=float, default=13.0)
    ap.add_argument("--oracle-seed", type=int)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.cmd == "world":
        cmd_world(a.seed, a.out)
    elif a.cmd == "qualify":
        cmd_qualify(a.seed, a.out, a.cpu_min)
    elif a.cmd == "controls":
        cmd_controls(a.out, a.oracle_seed)
    elif a.cmd == "report":
        cmd_report([int(s) for s in a.seeds.split(",")], a.out)
    elif a.cmd == "config":
        print("generator config_sha256", G.config_sha())
        print("qualification config_sha256", qconfig_sha())
    else:
        raise SystemExit("unknown command")


if __name__ == "__main__":
    main()
