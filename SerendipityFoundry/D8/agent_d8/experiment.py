"""D-8 orchestrator: calibration, instrument validation, freeze, binding run,
frozen statistics and verdict mapping.

Subcommands:
  smoke                 quick sanity check (engineering only)
  calibrate <tag>       run M0 suite on CAL battery (disjoint seeds)
  validate              instrument validation suite V1..V8 (VAL seeds)
  freeze                hash substrate+code+prereg into frozen/MANIFEST.json
  dev                   binding: M1 developmental phase on DEV battery
  hrnd                  build cost-matched H-RANDOM hoard
  evalrun --arms A,B    binding: run arms on EV battery
  ablz                  binding: per-z ablation arms on EV F1..F4
  stats                 frozen statistics + verdict mapping -> results/
"""

import json
import os
import sys
import time
import hashlib
from collections import defaultdict
from math import comb

import svm
import tasks as T
import engine as E
from engine import CFG, Machinery, run_task

HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "ledgers")
RES = os.path.join(HERE, "results")
FRZ = os.path.join(HERE, "frozen")
for d in (LED, RES, FRZ):
    os.makedirs(d, exist_ok=True)


def save_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def load_jsonl(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def agg_meters(rows, extra=None):
    tot = defaultdict(int)
    for r in rows:
        for k, v in r.get("meters", {}).items():
            tot[k] += v
    if extra:
        for k, v in extra.items():
            tot[k] += v
    return dict(tot)


# ------------------------------------------------------------------ smoke

def cmd_smoke():
    t = T.make_task("F1", "SMOKE-F1-00")
    print("gen:", svm.disasm(t["gen"]))
    print("revealed:", t["revealed"])
    row, _ = run_task("M0c", t, budget=2000)
    print("M0c:", row["solved"], "evals", row["evals"], "best", row["best"])
    if row["solution"]:
        print("solution:", svm.disasm(row["solution"]))


# -------------------------------------------------------------- calibrate

def cmd_calibrate(tag):
    batt = T.make_battery(T.CAL_SPEC, "CAL%s" % tag)
    rows = []
    for arm in ("M0a", "M0b", "M0c"):
        t0 = time.time()
        for t in batt:
            row, _ = run_task(arm, t)
            row["family"] = t["family"]
            rows.append(row)
        print("%s done in %.1fs" % (arm, time.time() - t0))
    save_jsonl(os.path.join(LED, "cal_%s.jsonl" % tag), rows)
    fams = sorted(set(r["family"] for r in rows))
    print("%-5s" % "", "  ".join("%-6s" % f for f in fams), " all(F1-F3)")
    for arm in ("M0a", "M0b", "M0c"):
        vals = []
        for f in fams:
            sub = [r for r in rows if r["arm"] == arm and r["family"] == f]
            vals.append(sum(r["solved"] for r in sub) / max(1, len(sub)))
        core = [r for r in rows if r["arm"] == arm
                and r["family"] in ("F1", "F2", "F3")]
        cr = sum(r["solved"] for r in core) / max(1, len(core))
        print("%-5s" % arm, "  ".join("%-6.2f" % v for v in vals),
              "  %.2f" % cr)


# --------------------------------------------------------------- validate

def _mini_battery(prefix, spec):
    return T.make_battery(spec, prefix)


def _planted_motif_task(uid, motif):
    """ORACLE-SIDE validation helper: an F2-like task forced to contain a
    specific, load-bearing motif. Used ONLY for instrument validation (V8),
    VAL seeds. Requirements: >=4 distinct hidden outputs; passes the
    triviality screen; deleting the motif changes >= 12/24 hidden outputs
    (the motif actually carries the computation)."""
    r = svm.rng("v8gen-v2", uid)
    ri = T._revealed_inputs(uid)
    hi = T._hidden_inputs(uid, ri)
    g = None
    for attempt in range(80):
        pre = [r.choice((svm.LD0, svm.LD1, svm.LD2))
               for _ in range(r.randint(1, 2))]
        glue = [T._tok(r, T.MIX_POOL) for _ in range(r.randint(0, 1))]
        cand = (pre + list(motif) + glue)[:svm.MAXLEN]
        outs = [svm.run(cand, *x)[0] for x in hi]
        if len(set(outs)) < 4:
            continue
        holed = pre + glue
        changed = sum(1 for x, o in zip(hi, outs)
                      if svm.run(holed, *x)[0] != o)
        if changed < 12:
            continue
        if T._screen_trivial(uid, attempt, cand, ri):
            continue
        g = cand
        break
    if g is None:
        return None
    revealed = [(x, svm.run(g, *x)[0]) for x in ri]
    hidden = [(x, svm.run(g, *x)[0]) for x in hi]
    return dict(uid=uid, family="V8", gen=g, revealed=revealed,
                hidden=hidden, resamples=0)


def _v8_battery():
    """Pick the first pool-A motif (len<=MAC_MAXLEN) whose planted battery
    sits in the detectable regime for a sensitivity control: 12 valid tasks
    and M0c solve rate <= 0.25 at the binding budget. Choices logged."""
    tried = []
    for mi, motif in enumerate(T.motif_pool("A")):
        if len(motif) > CFG["MAC_MAXLEN"]:
            tried.append(dict(idx=mi, skip="too long"))
            continue
        batt = []
        for i in range(20):
            t = _planted_motif_task("VAL8m%d-%02d" % (mi, i), motif)
            if t is not None:
                batt.append(t)
            if len(batt) == 12:
                break
        if len(batt) < 12:
            tried.append(dict(idx=mi, skip="only %d valid tasks"
                              % len(batt)))
            continue
        r0 = _rate(_run_arm("M0c", batt))
        tried.append(dict(idx=mi, m0c=r0))
        if r0 <= 0.25:
            return motif, batt, r0, tried
    return None, None, None, tried


def _rate(rows):
    return sum(r["solved"] for r in rows) / max(1, len(rows))


def _run_arm(arm, batt, mach=None, budget=None):
    rows = []
    for t in batt:
        row, _ = run_task(arm, t, mach, budget=budget)
        row["family"] = t["family"]
        rows.append(row)
    return rows


def cmd_validate():
    B = CFG["BUDGET"]  # sensitivity must be checked at the binding budget
    report = dict(when=time.strftime("%Y-%m-%d %H:%M:%S"), budget=B,
                  checks=[])

    def check(name, passed, detail):
        report["checks"].append(dict(name=name, passed=bool(passed),
                                     detail=detail))
        print("[%s] %s  %s" % ("PASS" if passed else "FAIL", name, detail))

    batt = _mini_battery("VAL", T.VAL_SPEC)
    m0 = _run_arm("M0c", batt, budget=B)
    r_m0 = _rate(m0)

    # V1: pure artifact possession must register, and be attributed to
    # possession (H-BAG retains it).
    mt = defaultdict(int)
    m1v = Machinery()
    for t in batt:
        m1v.add_record(list(t["gen"]), 6, mt)          # ORACLE-SIDE plant
        m1v.solutions[t["uid"]] = list(t["gen"])
    m1v.build(mt)
    m1v.promote_macros(mt)
    v1 = _run_arm("V1M1", batt, m1v, budget=B)
    v1bag = _run_arm("V1BAG", batt, m1v.clone_flags(
        use_bigram=False, use_segw=False, use_macros=False,
        uniform_bag=True), budget=B)
    d1 = _rate(v1) - r_m0
    dbag = _rate(v1bag) - r_m0
    ret = dbag / d1 if d1 > 0 else None
    check("V1-artifact-reuse", d1 >= 0.3 and ret is not None and ret >= 0.7,
          "d=%.2f bag_retention=%s" % (d1, "%.2f" % ret if ret else "na"))

    # V2/V3: random-history machinery, shuffled and unshuffled, must not
    # produce a large spurious advantage.
    mt2 = defaultdict(int)
    mrnd = Machinery()
    r = svm.rng("val-rnd-v1")
    for _ in range(500):
        mrnd.add_record(E.random_prog(r), 1, mt2)
    mrnd.build(mt2)
    mrnd.promote_macros_mirror(mt2)
    v3 = _run_arm("V3RND", batt, mrnd, budget=B)
    v2 = _run_arm("V2SHUF", batt, E.shuffled_machinery(mrnd, mt2), budget=B)
    d2 = _rate(v2) - r_m0
    d3 = _rate(v3) - r_m0
    check("V2-shuffle-false-positive", d2 <= 0.151, "d=%.2f" % d2)
    check("V3-diversity-injection", d3 <= 0.151, "d=%.2f" % d3)

    # V4: endpoint memorization must be flaggable. Mini-dev on the battery,
    # then re-run the same battery; solutions byte-identical to stored dev
    # solutions must be flagged by the novelty checker.
    mt4 = defaultdict(int)
    mdev = Machinery()
    for t in batt:
        row, ctx = run_task("V4DEV", t, mdev, budget=B, collect=True)
        for (p, m) in ctx.collected:
            mdev.add_record(p, m, mt4)
        if ctx.solved:
            mdev.solutions[t["uid"]] = list(ctx.solution)
        mdev.build(mt4)
    mdev.promote_macros(mt4)
    v4 = _run_arm("V4M1", batt, mdev, budget=B)
    devsols = set(tuple(s) for s in mdev.solutions.values())
    flagged = sum(1 for r_ in v4 if r_["solved"]
                  and tuple(r_["solution"]) in devsols)
    solved4 = sum(1 for r_ in v4 if r_["solved"])
    check("V4-memorization-flagged", solved4 == 0 or flagged >= 1,
          "solved=%d flagged_identical=%d" % (solved4, flagged))

    # V5: a useless-but-complex object must NOT be admissible.
    mjunk = Machinery()
    rj = svm.rng("val-junk-v1")
    mjunk.macros = [tuple(E.rand_tok(rj) for _ in range(5))]
    mjunk.macro_meta = [dict(ntasks=0, length=5, tasks=[])]
    mjunk.macro_enabled = [True]
    v5 = _run_arm("V5JUNK", batt, mjunk, budget=B)
    v5a = _run_arm("V5ABL", batt, mjunk.clone_flags(use_macros=False),
                   budget=B)
    d5 = _rate(v5) - _rate(v5a)
    admit5 = d5 >= 0.30 * max(0.0001, _rate(v5) - r_m0) and d5 > 0.05
    check("V5-useless-object-rejected", not admit5,
          "ablation_delta=%.2f (must not qualify)" % d5)

    # V6: unmetered compute must be caught by the ledger validator.
    v6 = _run_arm("V6CHEAT", batt[:5], None, budget=2 * B)
    bad = [r_ for r_ in v6 if r_["evals"] > B]
    check("V6-budget-cheat-flagged", len(bad) > 0,
          "%d/%d rows exceed declared budget" % (len(bad), len(v6)))

    # V7: structureless world -> nothing solves.
    b5 = T.make_battery([("F5", 6)], "VALF5")
    v7a = _run_arm("M0c", b5, budget=B)
    v7b = _run_arm("V7RND", b5, mrnd, budget=B)
    check("V7-structureless-zero", _rate(v7a) == 0 and _rate(v7b) == 0,
          "rates %.2f/%.2f" % (_rate(v7a), _rate(v7b)))

    # V8: sensitivity — a genuinely useful planted object must be detected
    # and its ablation must register. ORACLE-SIDE plant; VAL seeds only.
    motif, b8, r80, tried = _v8_battery()
    report["v8_motif_selection"] = tried
    if motif is None:
        check("V8-sensitivity", False, "no motif battery in regime")
    else:
        m8 = Machinery()
        m8.macros = [tuple(motif)]
        m8.macro_meta = [dict(ntasks=0, length=len(motif), tasks=["V8"])]
        m8.macro_enabled = [True]
        v8m1 = _run_arm("V8M1", b8, m8, budget=B)
        v8ab = _run_arm("V8ABL", b8, m8.clone_flags(use_macros=False),
                        budget=B)
        d8_ = _rate(v8m1) - r80
        dab = _rate(v8m1) - _rate(v8ab)
        check("V8-sensitivity", d8_ >= 0.15 and dab >= 0.10,
              "m0c=%.2f gain=%.2f ablation_loss=%.2f" % (r80, d8_, dab))

    # preserve full generation (failures included)
    path = os.path.join(LED, "validation_%d.json" % int(time.time()))
    with open(path, "w") as f:
        json.dump(report, f, indent=1)
    print("saved", path)
    nfail = sum(1 for c in report["checks"] if not c["passed"])
    print("validation: %d/%d passed" % (len(report["checks"]) - nfail,
                                        len(report["checks"])))


# ----------------------------------------------------------------- freeze

FREEZE_FILES = ["svm.py", "tasks.py", "engine.py", "experiment.py",
                "PREREG.md"]


def cmd_freeze(m0_primary):
    man = dict(when=time.strftime("%Y-%m-%d %H:%M:%S"),
               python=sys.version,
               m0_primary=m0_primary,
               cfg=dict(CFG),
               hashes={})
    for fn in FREEZE_FILES:
        with open(os.path.join(HERE, fn), "rb") as f:
            man["hashes"][fn] = hashlib.sha256(f.read()).hexdigest()
    path = os.path.join(FRZ, "MANIFEST.json")
    with open(path, "w") as f:
        json.dump(man, f, indent=1)
    print(json.dumps(man["hashes"], indent=1))
    print("frozen ->", path)


# -------------------------------------------------------------- binding

def cmd_dev():
    batt = T.make_battery(T.DEV_SPEC, "DEV")
    mach = Machinery()
    bmeters = defaultdict(int)
    rows = []
    t0 = time.time()
    for t in batt:
        row, ctx = run_task("DEV", t, mach, collect=True)
        for (p, m) in ctx.collected:
            mach.add_record(p, m, bmeters)
        if ctx.solved:
            mach.solutions[t["uid"]] = list(ctx.solution)
        mach.build(bmeters)
        row["family"] = t["family"]
        row["hoard"] = len(mach.records)
        rows.append(row)
    mach.promote_macros(bmeters)
    with open(os.path.join(FRZ, "machinery.json"), "w") as f:
        json.dump(mach.to_json(), f)
    save_jsonl(os.path.join(LED, "dev.jsonl"), rows)
    summary = dict(
        solved=sum(r["solved"] for r in rows), n=len(rows),
        hoard=len(mach.records), n_solutions=len(mach.solutions),
        macros=[dict(tokens=list(z), disasm=svm.disasm(z), **meta)
                for z, meta in zip(mach.macros, mach.macro_meta)],
        search_meters=agg_meters(rows), build_meters=dict(bmeters),
        wall_s=round(time.time() - t0, 1))
    with open(os.path.join(RES, "dev_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


def cmd_hrnd():
    bmeters = defaultdict(int)
    mach = Machinery()
    r = svm.rng("hrnd-v1")
    for _ in range(CFG["HOARD_CAP"]):
        mach.add_record(E.random_prog(r), 1, bmeters)
    mach.build(bmeters)
    with open(os.path.join(FRZ, "machinery_hrnd.json"), "w") as f:
        json.dump(mach.to_json(), f)
    with open(os.path.join(RES, "hrnd_build_meters.json"), "w") as f:
        json.dump(dict(bmeters), f, indent=1)
    print("hrnd hoard", len(mach.records), dict(bmeters))


def _load_mach(kind, meters):
    if kind == "dev":
        with open(os.path.join(FRZ, "machinery.json")) as f:
            return Machinery.from_json(json.load(f), meters)
    if kind == "hrnd":
        with open(os.path.join(FRZ, "machinery_hrnd.json")) as f:
            return Machinery.from_json(json.load(f), meters,
                                       mirror_promotion=True)
    raise ValueError(kind)


def _arm_machinery(arm, meters):
    if arm in ("M0a", "M0b", "M0c"):
        return None, False
    if arm == "HRND":
        return _load_mach("hrnd", meters), False
    m = _load_mach("dev", meters)
    if arm == "M1F":
        return m, False
    if arm == "M1L":
        return m, True
    if arm == "HBAG":
        return m.clone_flags(use_bigram=False, use_segw=False,
                             use_macros=False, uniform_bag=True), False
    if arm == "HSHUF":
        return E.shuffled_machinery(m, meters), False
    if arm == "ABLMAC":
        return m.clone_flags(use_macros=False), False
    if arm == "ABLRET":
        return m.clone_flags(use_retrieval=False), False
    if arm == "ABLBIG":
        return m.clone_flags(use_bigram=False), False
    if arm.startswith("ABLZ"):
        i = int(arm[4:])
        if i < len(m.macro_enabled):
            m.macro_enabled[i] = False
        return m, False
    raise ValueError(arm)


def cmd_evalrun(arms, spec=None, prefix="EV"):
    batt = T.make_battery(spec or T.EV_SPEC, prefix)
    for arm in arms:
        t0 = time.time()
        lmeters = defaultdict(int)
        mach, live = _arm_machinery(arm, lmeters)
        rows = []
        for t in batt:
            row, ctx = run_task(arm, t, mach, collect=live)
            if live:
                for (p, m) in ctx.collected:
                    mach.add_record(p, m, lmeters)
                if ctx.solved:
                    mach.solutions[t["uid"]] = list(ctx.solution)
                mach.build(lmeters)
                if ctx.solved:
                    mach.promote_macros(lmeters)
            row["family"] = t["family"]
            rows.append(row)
        out = os.path.join(LED, "eval_%s.jsonl" % arm)
        save_jsonl(out, rows)
        with open(os.path.join(LED, "meters_%s.json" % arm), "w") as f:
            json.dump(dict(search=agg_meters(rows), load=dict(lmeters)),
                      f, indent=1)
        n = len(rows)
        s = sum(r["solved"] for r in rows)
        print("%s: %d/%d solved, %.1fs -> %s"
              % (arm, s, n, time.time() - t0, out))


def cmd_ablz():
    mt = defaultdict(int)
    m = _load_mach("dev", mt)
    arms = ["ABLZ%d" % i for i in range(len(m.macros))]
    if not arms:
        print("no promoted macros; ABLZ arms skipped (recorded)")
        with open(os.path.join(LED, "ablz_none.json"), "w") as f:
            json.dump(dict(note="no promoted macros"), f)
        return
    spec = [("F1", 20), ("F2", 20), ("F3", 20), ("F4", 16)]
    cmd_evalrun(arms, spec=spec, prefix="EV")


# ------------------------------------------------------------------ stats

def _solve_map(rows):
    return {r["uid"]: bool(r["solved"]) for r in rows}


def _rate_u(sm, uids):
    return sum(1 for u in uids if sm.get(u)) / max(1, len(uids))


def _mcnemar(sa, sb, uids):
    b = sum(1 for u in uids if sa.get(u) and not sb.get(u))
    c = sum(1 for u in uids if sb.get(u) and not sa.get(u))
    n = b + c
    if n == 0:
        return 1.0, b, c
    k = min(b, c)
    p = 2 * sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, p), b, c


def _boot(uids, fn, nres=2000):
    r = svm.rng("boot-v1")
    vals = []
    for _ in range(nres):
        samp = [uids[r.randrange(len(uids))] for _ in uids]
        v = fn(samp)
        if v is not None:
            vals.append(v)
    if not vals:
        return None, None, 0
    vals.sort()
    lo = vals[int(0.025 * len(vals))]
    hi = vals[min(len(vals) - 1, int(0.975 * len(vals)))]
    return lo, hi, len(vals) / nres


def _holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    adj = [None] * m
    prev = 0.0
    for rank, i in enumerate(idx):
        a = min(1.0, (m - rank) * pvals[i])
        a = max(a, prev)
        adj[i] = a
        prev = a
    return adj


def cmd_stats():
    with open(os.path.join(FRZ, "MANIFEST.json")) as f:
        man = json.load(f)
    m0p_name = man["m0_primary"]
    arms = {}
    for fn in os.listdir(LED):
        if fn.startswith("eval_") and fn.endswith(".jsonl"):
            arm = fn[5:-6]
            arms[arm] = load_jsonl(os.path.join(LED, fn))
    fam = {}
    for rows in arms.values():
        for r in rows:
            fam[r["uid"]] = r["family"]
    all_uids = sorted(fam.keys())
    P = [u for u in all_uids if fam[u] in ("F1", "F2", "F3")]
    F4 = [u for u in all_uids if fam[u] == "F4"]
    F5 = [u for u in all_uids if fam[u] == "F5"]
    F6 = [u for u in all_uids if fam[u] == "F6"]
    sm = {a: _solve_map(rows) for a, rows in arms.items()}

    # ledger validation: fail closed on budget violations
    violations = []
    for a, rows in arms.items():
        for r in rows:
            if r["evals"] > CFG["BUDGET"]:
                violations.append((a, r["uid"], r["evals"]))
    res = dict(when=time.strftime("%Y-%m-%d %H:%M:%S"),
               m0_primary=m0p_name, n_primary=len(P),
               budget_violations=violations)

    def rate(a, uids):
        return _rate_u(sm[a], uids)

    # per-family table
    table = {}
    for a in sorted(arms):
        table[a] = {f: round(_rate_u(sm[a], [u for u in all_uids
                                             if fam[u] == f]), 3)
                    for f in ("F1", "F2", "F3", "F4", "F5", "F6")
                    if any(fam[u] == f for u in all_uids)}
        table[a]["primary"] = round(rate(a, P), 3)
    res["solve_table"] = table

    s1 = rate("M1F", P)
    s0 = rate(m0p_name, P)
    delta = s1 - s0
    p_primary, b_, c_ = _mcnemar(sm["M1F"], sm[m0p_name], P)
    dlo, dhi, _ = _boot(P, lambda s: _rate_u(sm["M1F"], s)
                        - _rate_u(sm[m0p_name], s))
    res["primary"] = dict(s_m1f=s1, s_m0=s0, delta=delta,
                          ci=[dlo, dhi], p_mcnemar=p_primary,
                          discordant=[b_, c_])
    G1 = p_primary < 0.05 and delta > 0

    def retention(arm):
        def f(samp):
            a = _rate_u(sm[arm], samp)
            z = _rate_u(sm[m0p_name], samp)
            o = _rate_u(sm["M1F"], samp)
            if o - z <= 0:
                return None
            return (a - z) / (o - z)
        pt = (rate(arm, P) - s0) / (s1 - s0) if s1 > s0 else None
        lo, hi, frac = _boot(P, f)
        return dict(point=pt, ci=[lo, hi], boot_valid_frac=frac)

    rets = {}
    for a in ("HBAG", "HSHUF", "HRND", "ABLMAC", "ABLRET", "ABLBIG", "M1L"):
        if a in sm:
            rets[a] = retention(a)
            rets[a]["p_vs_m1f"] = _mcnemar(sm["M1F"], sm[a], P)[0]
    res["retention"] = rets

    p_bag = _mcnemar(sm["M1F"], sm["HBAG"], P)[0] if "HBAG" in sm else 1.0
    rb = rets.get("HBAG", {}).get("point")
    rs = rets.get("HSHUF", {}).get("point")
    rr = rets.get("HRND", {}).get("point")
    G2 = (G1 and rb is not None and rb < 0.7 and rs is not None and rs < 0.7
          and rr is not None and rr < 0.7 and p_bag < 0.05)

    # ----- z admission (macros): frozen behavioral criteria A..I
    devsols = set()
    if os.path.exists(os.path.join(FRZ, "machinery.json")):
        with open(os.path.join(FRZ, "machinery.json")) as f:
            mj = json.load(f)
        devsols = set(tuple(s) for s in mj.get("solutions", {}).values())
    macros = []
    if os.path.exists(os.path.join(RES, "dev_summary.json")):
        with open(os.path.join(RES, "dev_summary.json")) as f:
            macros = json.load(f)["macros"]
    zres = []
    pvals = []
    for i, mz in enumerate(macros):
        arm = "ABLZ%d" % i
        if arm not in sm:
            continue
        d_i = s1 - rate(arm, P)
        p_i, bb, cc = _mcnemar(sm["M1F"], sm[arm], P)
        ztok = tuple(mz["tokens"])
        used = []
        for r in arms["M1F"]:
            if not r["solved"]:
                continue
            sol = tuple(r["solution"])
            inmac = i in (r.get("macros_used") or [])
            sub = any(sol[k:k + len(ztok)] == ztok
                      for k in range(len(sol) - len(ztok) + 1))
            if inmac or sub:
                used.append(dict(uid=r["uid"], via_macro_token=inmac,
                                 novel=sol not in devsols))
        novel_used = [u for u in used if u["novel"]]
        frac = d_i / delta if delta > 0 else None
        zres.append(dict(idx=i, disasm=mz["disasm"], ntasks_dev=mz["ntasks"],
                         ablation_delta=d_i, frac_of_effect=frac,
                         p_raw=p_i, discordant=[bb, cc],
                         used_in=used, n_used=len(used),
                         n_used_novel=len(novel_used)))
        pvals.append(p_i)
    adj = _holm(pvals) if pvals else []
    admitted = []
    for zr, pa in zip(zres, adj):
        zr["p_holm"] = pa
        zr["admitted"] = bool(
            G1 and rb is not None and rb < 0.7
            and rs is not None and rs < 0.7
            and zr["frac_of_effect"] is not None
            and zr["frac_of_effect"] >= 0.30
            and pa < 0.05
            and zr["n_used_novel"] >= 2)
        if zr["admitted"]:
            admitted.append(zr["idx"])
    res["z_candidates"] = zres
    res["z_admitted"] = admitted
    res["n_z_tested"] = len(zres)
    G3 = len(admitted) > 0

    # ----- secondary endpoints
    sec = {}
    if F4:
        pf4, b4, c4 = _mcnemar(sm["M1F"], sm[m0p_name], F4)
        sec["F4_heldout"] = dict(m1f=rate("M1F", F4),
                                 m0=rate(m0p_name, F4),
                                 p=pf4, discordant=[b4, c4])
        for i in admitted:
            arm = "ABLZ%d" % i
            if arm in sm:
                sec.setdefault("F4_z_transfer", {})["z%d" % i] = dict(
                    m1f=rate("M1F", F4), abl=rate(arm, F4),
                    p=_mcnemar(sm["M1F"], sm[arm], F4)[0])
    if F6:
        pf6, b6, c6 = _mcnemar(sm["M1F"], sm[m0p_name], F6)
        sec["F6_misleading"] = dict(m1f=rate("M1F", F6),
                                    m0=rate(m0p_name, F6),
                                    p=pf6, discordant=[b6, c6])
    if F5:
        sec["F5_structureless"] = {a: rate(a, F5) for a in sorted(sm)}
    both = [u for u in P if sm["M1F"].get(u) and sm[m0p_name].get(u)]
    if both:
        ce = {a: [r["solve_evals"] for r in arms[a]
                  if r["uid"] in both and r["solve_evals"]]
              for a in ("M1F", m0p_name)}
        med = {a: sorted(v)[len(v) // 2] for a, v in ce.items() if v}
        sec["first_solve_evals_median_both_solved"] = med
        sec["n_both_solved"] = len(both)
    res["secondary"] = sec

    # ----- frozen verdict mapping
    noise_flags = []
    for a in ("HBAG", "HSHUF", "HRND"):
        r_ = rets.get(a)
        if r_ and r_["ci"][0] is not None and r_["ci"][0] < 0.7 <= r_["ci"][1]:
            noise_flags.append("%s retention CI spans 0.7" % a)
    if violations:
        verdict = "INVALID (budget violations)"
    elif not G1:
        verdict = "S0"
    elif not G2:
        verdict = "S1"
    elif not G3:
        verdict = "S2"
    else:
        verdict = "S3"
    res["gates"] = dict(G1_effect=G1, G2_organization=G2, G3_object=G3,
                        S4="not awarded (see PREREG: requires load-bearing "
                           "structure beyond designed splice/statistics "
                           "schema; test not passed by design ceiling)",
                        S5="not awarded (requires demonstrated mechanism "
                           "outside frozen positive ontology)")
    res["verdict"] = verdict
    res["noise_flags"] = noise_flags
    with open(os.path.join(RES, "RESULTS.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    print("VERDICT:", verdict)


# ------------------------------------------------------------------ main

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "smoke":
        cmd_smoke()
    elif cmd == "calibrate":
        cmd_calibrate(sys.argv[2])
    elif cmd == "validate":
        cmd_validate()
    elif cmd == "freeze":
        cmd_freeze(sys.argv[2])
    elif cmd == "dev":
        cmd_dev()
    elif cmd == "hrnd":
        cmd_hrnd()
    elif cmd == "evalrun":
        cmd_evalrun(sys.argv[2].split(","))
    elif cmd == "ablz":
        cmd_ablz()
    elif cmd == "stats":
        cmd_stats()
    else:
        raise SystemExit("unknown command " + cmd)
