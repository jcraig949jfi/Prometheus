"""Corpus analysis of W1 competent genomes and first donors (Nestor P2 delegate, 2026-09-27).

Read-only over W1 results; writes only into this directory. No world runs: every measurement is the
fresh-start P-11 assay (run_dd.assay_one logic) or the world copy criterion (run_nc.copies) on stored genomes.

    python corpus_analysis.py corpus   -> corpus.json        (dedup of all 51,007 competent genomes; static features)
    python corpus_analysis.py sample   -> sample.json        (stratified sample, coordinator directive; see build_sample)
    python corpus_analysis.py q1       -> q1_partial.jsonl   (20-seed assay, full mask vs mask without OP_SELF)
    python corpus_analysis.py q2       -> q2_regs.json       (single-register perturbation of the donor's start state)
    python corpus_analysis.py q2d      -> q2_donors.json     (same perturbation on the 43 x_dd_nocopy_context donors)
    python corpus_analysis.py q3       -> q3_reset.json      (single-register reset of the self-carried state)
    python corpus_analysis.py q4       -> q4_trace_all.json  (block-copy register values, SELF-free copiers)
    python q4_provenance.py            -> q4_provenance.json (last setter of each register; per-side pass counts)
    python q4_reps.py                  -> q4_reps.json/.txt  (executed listings of 8 representatives)
    python summarize.py                -> SUMMARY.json

At most 2 worker processes.
"""
from __future__ import annotations

import collections
import glob
import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parents[2] / "npe-w1-donor-discovery-2026-09-26"
CAMP = HERE.parents[2]
for p in (W1 / "x_dd_nocopy_context", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          CAMP / "c9x-explore-2026-09-24" / "x_donor_swap", CAMP / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
NPROC = 2
K = 20
FRESH = (None, 0, 0)
# register indices in z8: 0=B 1=C 2=D 3=E 4=H 5=L 6=(unused) 7=A
REGS1 = {"B": [0], "C": [1], "D": [2], "E": [3], "H": [4], "L": [5], "A": [7]}
PAIRS = {"BC": [0, 1], "DE": [2, 3], "HL": [4, 5]}

_W = {}


def env(vm, cell):
    """(world, runner) with world.z8 set explicitly for the genome's VM (as the W1 scripts do)."""
    import world
    import z8 as z8_plain
    import run_dc
    import run_dd
    import run_ds
    if "dense" not in _W:
        _W["dense"] = run_dc.dense_z8()
    world.z8 = _W["dense"] if vm == "DENSE" else z8_plain
    key = ("r", cell)
    if key not in _W:
        a = run_ds.cells()[run_dd.CELLS[cell]]
        _W[key] = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    r = _W[key]
    r.__dict__.pop("_ops_mask", None)          # undo any instance monkeypatch
    return world, r


# ------------------------------------------------------------------ corpus
def static(g, vm):
    pats = {"ED_B0": bytes((0xED, 0xB0)), "ED_B8": bytes((0xED, 0xB8))}
    pos = {k: g.find(p) for k, p in pats.items()}
    if vm == "DENSE":
        pos["E5"] = g.find(b"\xe5")
        pos["E7"] = g.find(b"\xe7")
    present = {k: v for k, v in pos.items() if v >= 0}
    first = min(present.items(), key=lambda kv: kv[1]) if present else None
    return {"has_self": bytes((0xED, 0x32)) in g, "blockcopy_encodings": sorted(present),
            "has_blockcopy": bool(present), "first_blockcopy": first[0] if first else None,
            "first_blockcopy_pos": first[1] if first else None,
            "first_is_alias": bool(first) and first[0] in ("E5", "E7"),
            "only_alias": bool(present) and all(k in ("E5", "E7") for k in present)}


def build_corpus():
    G = {}
    srcs = [("x_dd_dense_copy", p) for p in glob.glob(str(W1 / "x_dd_dense_copy/results/*.json"))]
    srcs += [("c_dense_copy", p) for p in glob.glob(str(W1 / "c_dense_copy/results/*.json"))]
    srcs += [("x_donor_discovery", p) for p in glob.glob(str(W1 / "x_donor_discovery/results/RANDOM_*.json"))]
    for exp, p in srcs:
        r = json.loads(pathlib.Path(p).read_text())
        arm = r.get("arm", "PLAIN")               # x_donor_discovery ran the stock VM
        vm = "DENSE" if arm == "DENSE_COPY" else "PLAIN"
        for c in r["checkpoints"]:
            for g in c["competent_genomes"]:
                k = (vm, r["cell"], g["hex"])
                e = G.setdefault(k, {"vm": vm, "cell": r["cell"], "hex": g["hex"], "origins": [],
                                     "stored_rates": []})
                o = "%s/%s/%d" % (exp, arm, r["seed"])
                if o not in e["origins"]:
                    e["origins"].append(o)
                e["stored_rates"].append(g["rate"])
                e.setdefault("first_epoch", c["epoch"])
    out = []
    for k, e in sorted(G.items()):
        e["origin_exp"] = e["origins"][0].split("/")[0]
        e["origin_run"] = e["origins"][0]
        e["n_runs"] = len({o for o in e["origins"]})
        e["stored_rate_max"] = max(e["stored_rates"])
        del e["stored_rates"]
        e.update(static(bytes.fromhex(e["hex"]), e["vm"]))
        out.append(e)
    (HERE / "corpus.json").write_text(json.dumps(out))
    print(len(out), collections.Counter((e["vm"], e["cell"], e["origin_exp"]) for e in out))


# ------------------------------------------------------------------ assays
def assay_state(world, r, g, st_donor, tag, k, mask=None):
    """run_dd.assay_one with an arbitrary donor start state (partner fresh); per seed, pass on either side."""
    n = r.L
    tl = world._pow2(2 * n)
    om = r._ops_mask() if mask is None else mask
    hits = 0
    sides = [0, 0]
    for i in range(k):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            sa, sb = (st_donor, FRESH) if side == 0 else (FRESH, st_donor)
            res = world.p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=sa, st_b=sb,
                                  budget=r.t["slice"], ops_mask=om, cmr=r.copy_mut,
                                  victim_side=1 - side, seed=("X-DONOR-DISCOVERY", tag, i, side))
            sides[side] += res["pass"]
            ok = ok or res["pass"]
        hits += ok
    return hits, sides


def q1_chunk(items):
    import run_dd
    out = []
    for e in items:
        world, r = env(e["vm"], e["cell"])
        g = bytes.fromhex(e["hex"])
        full = r._ops_mask()
        tag = ("CORPUS-Q1", e["hex"])
        # run_dd.assay_one itself, with the runner's _ops_mask monkeypatched for the no-SELF arm
        h_full, _ = run_dd.assay_one(world, r, g, tag, K)
        r._ops_mask = lambda m=full & ~0x02: m
        h_ns, _ = run_dd.assay_one(world, r, g, tag, K)
        r.__dict__.pop("_ops_mask", None)
        out.append({"vm": e["vm"], "cell": e["cell"], "hex": e["hex"], "rate_full": h_full / K,
                    "rate_noself": h_ns / K, "origin_run": e["origin_run"], "nocopy_donor": e.get("nocopy_donor")})
    return out


SAMPLE_SEED = 20260927
STRATUM_CAP = 300
TOTAL_CAP = 1500


def build_sample():
    """Coordinator directive (2026-09-27): stratified random sample instead of the full corpus.
    Stratum = (cell, VM/arm, origin run). Per-stratum quota q = the largest q <= STRATUM_CAP such that
    sum_s min(|s|, q) <= TOTAL_CAP (water-filling, so small strata are taken whole). Fixed seed.
    Plus every first-donor genome of x_dd_nocopy_context (dense VM), flagged nocopy_donor."""
    corpus = json.loads((HERE / "corpus.json").read_text())
    strata = collections.defaultdict(list)
    for e in corpus:
        strata[(e["cell"], e["vm"], e["origin_run"])].append(e)
    q = 0
    while q < STRATUM_CAP and sum(min(len(v), q + 1) for v in strata.values()) <= TOTAL_CAP:
        q += 1
    rng = random.Random(SAMPLE_SEED)
    out = []
    for k in sorted(strata):
        v = sorted(strata[k], key=lambda e: e["hex"])
        out += [dict(e, nocopy_donor=None) for e in (v if len(v) <= q else rng.sample(v, q))]
    idx = {(e["vm"], e["cell"], e["hex"]): e for e in out}
    allc = {(e["vm"], e["cell"], e["hex"]): e for e in corpus}
    for p in sorted(glob.glob(str(W1 / "x_dd_nocopy_context/results/*.json"))):
        x = json.loads(pathlib.Path(p).read_text())
        if not x["donor_hex"]:
            continue
        k = ("DENSE", x["cell"], x["donor_hex"])
        if k in idx:
            idx[k]["nocopy_donor"] = x["status"]
        else:
            base = allc.get(k) or dict({"vm": "DENSE", "cell": x["cell"], "hex": x["donor_hex"],
                                        "origins": ["x_dd_establish/DENSE_COPY/%d" % x["seed"]],
                                        "origin_exp": "x_dd_establish",
                                        "origin_run": "x_dd_establish/DENSE_COPY/%d" % x["seed"]},
                                       **static(bytes.fromhex(x["donor_hex"]), "DENSE"))
            e = dict(base, nocopy_donor=x["status"], in_corpus=k in allc)
            out.append(e)
            idx[k] = e
    meta = {"seed": SAMPLE_SEED, "stratum_cap": STRATUM_CAP, "total_cap": TOTAL_CAP, "quota_q": q,
            "n_strata": len(strata), "corpus_size": len(corpus), "sample_size": len(out),
            "nocopy_donors_included": sum(e["nocopy_donor"] is not None for e in out),
            "stratum_sizes": {"%s|%s|%s" % k: [len(v), min(len(v), q)] for k, v in sorted(strata.items())}}
    (HERE / "sample.json").write_text(json.dumps({"meta": meta, "genomes": out}))
    print(json.dumps({k: v for k, v in meta.items() if k != "stratum_sizes"}))


def run_q1():
    corpus = json.loads((HERE / "sample.json").read_text())["genomes"]
    done = {}
    part = HERE / "q1_partial.jsonl"
    if part.exists():
        for line in part.read_text().splitlines():
            d = json.loads(line)
            done[(d["vm"], d["cell"], d["hex"])] = d
    todo = [e for e in corpus if (e["vm"], e["cell"], e["hex"]) not in done]
    chunks = [todo[i:i + 20] for i in range(0, len(todo), 20)]
    with mp.Pool(NPROC) as pool, open(part, "a") as fh:
        for j, res in enumerate(pool.imap_unordered(q1_chunk, chunks)):
            for d in res:
                fh.write(json.dumps(d) + "\n")
            fh.flush()
            print("q1 chunk", j + 1, "/", len(chunks), flush=True)


# ------------------------------------------------------------------ Q2
def perturbed(name, rng):
    regs = [0] * 8
    fz = fc = 0
    if name in REGS1:
        regs[REGS1[name][0]] = rng.randrange(1, 256)
    elif name in PAIRS:
        v = rng.randrange(1, 65536)
        regs[PAIRS[name][0]], regs[PAIRS[name][1]] = v >> 8, v & 0xFF
    elif name == "fz":
        fz = 1
    elif name == "fc":
        fc = 1
    return (regs, fz, fc)


Q2_CONDS = ["B", "C", "D", "E", "H", "L", "A", "BC", "DE", "HL", "fz", "fc"]
Q2_DRAWS = 10
Q2_SEEDS = 2


def q2_one(e):
    world, r = env(e["vm"], e["cell"])
    g = bytes.fromhex(e["hex"])
    out = {"vm": e["vm"], "cell": e["cell"], "hex": e["hex"], "self_dep": e["self_dep"]}
    # baseline: the same assay seeds, fresh state (regs None == zeros)
    base = 0
    for d in range(Q2_DRAWS):
        base += assay_state(world, r, g, FRESH, ("CORPUS-Q2", e["hex"], d), Q2_SEEDS)[0]
    out["base"] = base / (Q2_DRAWS * Q2_SEEDS)
    for c in Q2_CONDS:
        rng = random.Random(("CORPUS-Q2", e["hex"], c).__repr__())
        h = 0
        for d in range(Q2_DRAWS):
            h += assay_state(world, r, g, perturbed(c, rng), ("CORPUS-Q2", e["hex"], d), Q2_SEEDS)[0]
        out[c] = h / (Q2_DRAWS * Q2_SEEDS)
    return out


def run_q2():
    q1 = {(d["vm"], d["cell"], d["hex"]): d for d in load_q1()}
    rng = random.Random(20260927)
    sample = []
    for cell in ("7ae3", "ffa6"):
        comp = [d for d in q1.values() if d["cell"] == cell and d["rate_full"] >= 0.5]
        dep = sorted([d for d in comp if d["rate_noself"] < 0.5], key=lambda d: d["hex"])
        ind = sorted([d for d in comp if d["rate_noself"] >= 0.5], key=lambda d: d["hex"])
        nd = min(len(dep), 15)
        ni = min(len(ind), 30 - nd)
        nd = min(len(dep), 30 - ni)
        for d in rng.sample(dep, nd):
            sample.append(dict(d, self_dep=True))
        for d in rng.sample(ind, ni):
            sample.append(dict(d, self_dep=False))
    with mp.Pool(NPROC) as pool:
        res = pool.map(q2_one, sample)
    (HERE / "q2_regs.json").write_text(json.dumps(res))
    print(len(res))


# ------------------------------------------------------------------ Q3
Q3_SEEDS = 10
Q3_RESETS = ["NONE", "B", "C", "D", "E", "H", "L", "A", "BC", "DE", "HL", "fz", "fc", "FLAGS", "ALL_REGS", "ALL"]


def carried_state(world, r, g, st, side, n, tl, tag):
    """One blank-partner execution in the world's order, exactly as x_dd_selfstate.run_ss does (k = 1)."""
    import p11
    blank = bytes(n)
    ga, gb = (g, blank) if side == 0 else (blank, g)
    mem = bytearray(tl)
    mem[0:len(ga)] = ga
    mem[n:n + len(gb)] = gb
    rng = random.Random(p11.event_seed(*tag))
    dctx = None
    for who, start, stw in ((0, 0, st if side == 0 else FRESH), (1, n, st if side == 1 else FRESH)):
        c = world.z8.Ctx(mem, start, n, policy=world.z8.ARENA, rng=rng, copy_mut_rate=r.copy_mut, sense=who)
        c.regs, c.fz, c.fc = (None if stw[0] is None else list(stw[0])), stw[1], stw[2]
        world.z8.run(c, start, r.t["slice"], ops_enabled=r._ops_mask())
        if who == side:
            dctx = c
    return (list(dctx.regs), dctx.fz, dctx.fc)


def reset(st, name):
    regs, fz, fc = list(st[0]), st[1], st[2]
    if name == "NONE":
        pass
    elif name in REGS1:
        regs[REGS1[name][0]] = 0
    elif name in PAIRS:
        for i in PAIRS[name]:
            regs[i] = 0
    elif name == "fz":
        fz = 0
    elif name == "fc":
        fc = 0
    elif name == "FLAGS":
        fz = fc = 0
    elif name == "ALL_REGS":
        regs = [0] * 8
    elif name == "ALL":
        return FRESH
    return (regs, fz, fc)


def q3_one(d):
    import run_nc
    world, r = env("DENSE", d["cell"])
    g = bytes.fromhex(d["donor_hex"])
    n = r.L
    tl = world._pow2(2 * n)
    hits = collections.Counter()
    tot = 0
    states = collections.Counter()
    for sd in range(Q3_SEEDS):
        for side in (0, 1):
            st = carried_state(world, r, g, FRESH, side, n, tl, ("CORPUS-Q3-pre", d["cell"], d["seed"], sd, side))
            states[json.dumps([side, st[0][:6] + st[0][7:], st[1], st[2]])] += 1
            tot += 1
            for nm in Q3_RESETS:
                hits[nm] += run_nc.copies(world, r, g, reset(st, nm), bytes(n), FRESH, side,
                                          ("CORPUS-Q3", d["cell"], d["seed"], nm, sd, side))
    return {"status": d["status"], "cell": d["cell"], "seed": d["seed"], "donor_hex": d["donor_hex"],
            "selfstate_rates_by_k": d.get("rates_by_k"),
            "rates": {nm: round(hits[nm] / tot, 4) for nm in Q3_RESETS},
            "carried_states": [{"side_regs_BCDEHLA_fz_fc": json.loads(k), "count": v}
                               for k, v in states.most_common()]}


def run_q3():
    rows = []
    ss = {}
    for p in glob.glob(str(W1 / "x_dd_selfstate/results/*.json")):
        x = json.loads(pathlib.Path(p).read_text())
        ss[(x["cell"], x["seed"])] = x["rates_by_k"]
    for p in sorted(glob.glob(str(W1 / "x_dd_nocopy_context/results/*.json"))):
        x = json.loads(pathlib.Path(p).read_text())
        if x["donor_hex"] and x["status"] in ("NO_COPY", "ESTABLISHED"):
            rows.append(dict(x, rates_by_k=ss.get((x["cell"], x["seed"]))))
    with mp.Pool(NPROC) as pool:
        res = pool.map(q3_one, rows)
    (HERE / "q3_reset.json").write_text(json.dumps(res))
    print(len(res))


# ------------------------------------------------------------------ Q4
def dis_dense(g, vm):
    import z8
    out = []
    for a, s in z8.dis(g):
        if vm == "DENSE" and s == "nop(E5)":
            s = "LDIR*  (E5 alias)"
        elif vm == "DENSE" and s == "nop(E7)":
            s = "LDDR*  (E7 alias)"
        out.append("%02X  %s" % (a, s))
    return out


def trace_blockcopy(world, r, g, side, victim, st=FRESH, mask=None):
    """Execute the pair interaction (victim bytes in the partner half) step by step and record, for every
    block-copy the DONOR context executes, its pc and HL/DE/BC. Re-runs from scratch with budget b to read the
    state before step b (the budget cap would truncate LDIR if we single-stepped)."""
    n = r.L
    tl = world._pow2(2 * n)
    om = r._ops_mask() if mask is None else mask
    z = world.z8
    dense = vm_is_dense(z)
    budget = r.t["slice"]

    def setup():
        tape = bytearray(tl)
        tape[0:n] = (g + bytes(n))[:n] if side == 0 else victim
        tape[n:2 * n] = victim if side == 0 else (g + bytes(n))[:n]
        return tape

    tape = setup()
    # partner runs first if donor is side 1
    if side == 1:
        c0 = z.Ctx(tape, 0, n, policy=z.ARENA, rng=random.Random(1), copy_mut_rate=0.0, sense=0)
        z.run(c0, 0, budget, ops_enabled=om)
    pre = bytes(tape)
    start = side * n
    events = []
    prev_pc = start
    for b in range(0, budget + 1):
        t2 = bytearray(pre)
        c = z.Ctx(t2, start, n, policy=z.ARENA, rng=random.Random(1), copy_mut_rate=0.0, sense=side)
        c.regs, c.fz, c.fc = (None if st[0] is None else list(st[0])), st[1], st[2]
        pc = z.run(c, start, b, ops_enabled=om) if b else start
        if c.halted and b:
            break
        regs = c.regs if (b and c.regs is not None) else ([0] * 8 if st[0] is None else list(st[0]))
        op = t2[pc % tl]
        op2 = t2[(pc + 1) % tl]
        is_bc = (op == 0xED and op2 in (0xB0, 0xB8)) or (dense and op in (0xE5, 0xE7))
        if is_bc:
            kind = "LDIR" if (op == 0xE5 or (op == 0xED and op2 == 0xB0)) else "LDDR"
            events.append({"step": b, "pc": pc, "pc_rel_own": (pc - start) % tl, "kind": kind,
                           "enc": "alias" if op != 0xED else "ED",
                           "HL": (regs[4] << 8) | regs[5], "DE": (regs[2] << 8) | regs[3],
                           "BC": (regs[0] << 8) | regs[1], "A": regs[7]})
            if len(events) >= 4:
                break
    return events


def vm_is_dense(z):
    return z.__name__ == "z8_dense_copy"


def run_q4():
    q1 = load_q1()
    corpus = {(e["vm"], e["cell"], e["hex"]): e for e in json.loads((HERE / "corpus.json").read_text())}
    ind = [d for d in q1 if d["rate_full"] >= 0.5 and d["rate_noself"] >= 0.5]
    # traces for ALL self-independent competent genomes (cheap), then motif tallies
    res = []
    for d in ind:
        world, r = env(d["vm"], d["cell"])
        g = bytes.fromhex(d["hex"])
        vr = random.Random(("CORPUS-Q4", d["hex"]).__repr__())
        victim = bytes(vr.randrange(256) for _ in range(r.L))
        ev = {s: trace_blockcopy(world, r, g, s, victim, mask=r._ops_mask() & ~0x02) for s in (0, 1)}
        res.append({"vm": d["vm"], "cell": d["cell"], "hex": d["hex"], "rate_full": d["rate_full"],
                    "rate_noself": d["rate_noself"], "origin_run": d["origin_run"], "nocopy_donor": d.get("nocopy_donor"),
                    "trace": ev})
    (HERE / "q4_trace_all.json").write_text(json.dumps(res))
    print(len(res))


def load_q1():
    return [json.loads(l) for l in (HERE / "q1_partial.jsonl").read_text().splitlines()]


def run_q2d():
    """Q2 perturbation applied to the x_dd_nocopy_context first donors (NO_COPY / ESTABLISHED)."""
    q1 = [d for d in load_q1() if d.get("nocopy_donor")]
    with mp.Pool(NPROC) as pool:
        res = pool.map(q2_one, [dict(d, self_dep=d["rate_noself"] < 0.5 <= d["rate_full"]) for d in q1])
    for x, d in zip(res, q1):
        x["nocopy_donor"] = d["nocopy_donor"]
    (HERE / "q2_donors.json").write_text(json.dumps(res))
    print(len(res))


if __name__ == "__main__":
    {"corpus": build_corpus, "sample": build_sample, "q1": run_q1, "q2": run_q2, "q2d": run_q2d, "q3": run_q3,
     "q4": run_q4}[sys.argv[1]]()
