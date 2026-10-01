"""AMENDMENT 17 -- the AMENDMENT 16 campaign, second execution (2026-09-26).

Derived from a16.py (frozen, unmodified) by renaming seeds/labels/outputs to
A17 and by three ENGINEERING changes, none of which changes a decision:
  - Q2 is exact-fast: (init, body) accumulators hoisted per probe and survivor
    counting as a NumPy boolean reduction (the accel/fasteval method);
  - every foundry evaluation is checkpointed to disk as it completes;
  - optionally, workers use accel/fasteval.run_program in place of
    basis_v4.run_program, ONLY if the in-campaign equivalence gate passes.
One design repair, frozen in AMENDMENT 17: E4's F3 is made genuinely
adversarial (F3*).
Stages:
  gate     conformance + fast-Q2 / fasteval equivalence on a PILOT stream
  foundry  catalogs A, B (G4) and C (G5 stream, generated only)
  e1 / e2  the AMENDMENT 15 assay on catalogs A / B (independent processes)
  e4       S1 necessity
Process pools are for throughput only; acceptance is decided in draw order.
"""
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G          # noqa: E402
import cert as CT             # noqa: E402
import conformance as CF      # noqa: E402
import engine as E            # noqa: E402
import fair as FR             # noqa: E402
import identity as I          # noqa: E402
import meta_tribunal as M     # noqa: E402
import tier3d as T3D          # noqa: E402
import tier3e as T3E          # noqa: E402

STRATA = ["add", "sub", "mul", "fdiv", "mod", "gcd", "powr"]
DRAWS, K, N, ESCROW, MAX_HITS, R_D, R_VAL, R_OBS, EMITTER = 32, 4, 16, FR.ESCROW, 5, 8, 8, 3, 2
WORKERS = int(os.environ.get("A17_WORKERS", "7"))
CKPT = "A17_FOUNDRY_EVALS_2026-09-26.jsonl"
LET = "abcdefghijklmnopqrstuvwxyz"
T0 = "2026-09-26T13:26:55Z"


def log(m):
    print("[a17 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n",
                             encoding="utf-8")


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------- provider
class Prov:
    """A catalog as a MetaTribunal / Cell provider (Tier-3 task shape)."""

    def __init__(self, specs):
        self.FAMILY_SPEC = dict(specs)          # name -> (body, final, init)

    def witness(self, f):
        b, fi, i = self.FAMILY_SPEC[f]
        return ("fold", i, b, fi)

    def task(self, f, rng, lr=G.SEARCH_LENGTHS):
        lo, hi = lr
        xs = [rng.randint(2, 30) for _ in range(rng.randint(lo, hi))]
        m = rng.randint(3, 97)
        return (("Family %s over: " % f) + ", ".join(map(str, xs)) + " with %d." % m,
                str(G.run_program(self.witness(f), xs + [m], True)))

    def tasks(self, f, n, seed, lr=G.SEARCH_LENGTHS):
        rng = random.Random((seed, f, lr).__str__())
        out = []
        for i in range(n):
            p, g = self.task(f, rng, lr)
            out.append({"family": f, "prompt": p, "gold": g, "key": "%s-%d-%d" % (f, seed, i)})
        return out

    @staticmethod
    def nums_of(t):
        return [int(x) for x in re.findall(r"-?\d+", t["prompt"])]


def use_fasteval():
    """Substitute the certified-exact evaluator (AMENDMENT 17 s0.3). Only when
    A17_FASTEVAL=1, which the driver sets only after the equivalence gate."""
    if os.environ.get("A17_FASTEVAL") == "1":
        sys.path.insert(0, str(HERE / "accel"))
        import fasteval as FE
        G.run_program = FE.run_program


def worker_init():
    import tempfile
    E.MARKER_DIR = Path(tempfile.gettempdir()) / ("aphrodite_engine_markers_w%d" % os.getpid())
    use_fasteval()


def pool_map(fn, items, chunks=1):
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=worker_init) as ex:
        return list(ex.map(fn, items, chunksize=chunks))


def pool_iter(fn, items):
    """As pool_map, but yields results as they complete (for checkpointing)."""
    from concurrent.futures import as_completed
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=worker_init) as ex:
        futs = [ex.submit(fn, it) for it in items]
        for f in as_completed(futs):
            yield f.result()


# ---------------------------------------------------------------- draws
_G5 = None


def g5_bodies():
    """G5 'g5-depth3-v1': G4 bodies plus prim(a, b), a in BODY_ATOMS, b a G4
    depth-2 non-atom body (AMENDMENT 16 s4)."""
    global _G5
    if _G5 is None:
        extra = [tmpl.format(a, b) for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())
                 for a in G.BODY_ATOMS for b in G.BODY_SPACE if b not in G.BODY_ATOMS]
        _G5 = list(G.BODY_SPACE) + extra
    return _G5


def _mentions(src, n):
    return re.search(r"\b%s\b" % n, src) is not None


def draws(cat):
    """32 draws per stratum, without replacement at the behavior level."""
    grammar = g5_bodies() if cat == "C" else G.BODY_SPACE
    rng = random.Random(I._seed("APHRODITE/A17/CATALOG_%s/v1" % cat))
    finals = [f for f in G.FINAL_SPACE if _mentions(f, "acc")]
    out, seen = {}, set()
    for op in STRATA:
        pool = [b for b in grammar if T3E._top_op(b) == op and _mentions(b, "acc") and _mentions(b, "v")]
        lst, guard = [], 0
        while len(lst) < DRAWS and guard < 5000:
            guard += 1
            p = ("fold", rng.choice(G.H1_SPACE), rng.choice(pool), rng.choice(finals))
            bid = I.behavior_id(p, True)
            if bid in seen:
                continue
            seen.add(bid)
            k = len(lst)
            lst.append({"name": "h%s_%s_%s%s" % (cat, op, LET[k // 26], LET[k % 26]),
                        "stratum": op, "draw": k, "init": p[1], "body": p[2], "final": p[3]})
        out[op] = lst
    return out


# ---------------------------------------------------------------- qualification Q2-Q4
def _fe():
    sys.path.insert(0, str(HERE / "accel"))
    import fasteval as FE
    return FE


def q2_vectors(prov, f, label):
    """Exact-fast Q2 part 1: target vector and the distinct wrong vectors over
    the 240-probe pool (same set as qualify_ref; order irrelevant)."""
    FE = _fe()
    target = prov.witness(f)
    pool = prov.tasks(f, 240, E.dev_entropy(label + "-pool-" + f, 0))
    probes = [prov.nums_of(t) for t in pool]
    tv = tuple(FE.run_program(target, n, True) for n in probes)
    pinfo = [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0)) for n in probes]
    accs, wrong = {}, {}
    for p in T3D.reachable_programs():
        _, i, b, fi = p
        al = accs.get((i, b))
        if al is None:
            ifn, bfn = FE.fn(i), FE.fn(b)
            al = accs[(i, b)] = [FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _ in pinfo]
        ffn = FE.fn(fi)
        v = tuple(None if a is FE._FAIL else FE._final(ffn, a, vl, fst, lst)
                  for a, (_v, fst, lst, vl) in zip(al, pinfo))
        if v != tv and v not in wrong:
            wrong[v] = 1
    return tv, list(wrong)


def q2_counter(tv, wv):
    import numpy as np
    mat = np.array([[v[i] is not None and v[i] == tv[i] for i in range(240)] for v in wv],
                   dtype=bool).reshape(len(wv), 240)
    return lambda idx: int(mat[:, idx].all(axis=1).sum()) if len(wv) else 0


def qualify(prov, f, label):
    """Exact-fast Q2 (AMENDMENT 17 s0.2): same rng draws, same counts, same
    decision as qualify_ref."""
    tv, wv = q2_vectors(prov, f, label)
    count = q2_counter(tv, wv)
    rng = random.Random(E.dev_entropy(label + "-draws-" + f, 0))
    for size in (4, 6, 8, 12, 16, 24):
        s = [count(rng.sample(range(240), size)) for _ in range(200)]
        up = statistics.mean(s) + 1.96 * statistics.pstdev(s) / math.sqrt(len(s))
        if up < 0.05:
            return size
    return None


def qualify_ref(prov, f, label):
    target = prov.witness(f)
    pool = prov.tasks(f, 240, E.dev_entropy(label + "-pool-" + f, 0))
    probes = [prov.nums_of(t) for t in pool]
    tv = tuple(G.run_program(target, n, True) for n in probes)
    wrong = {}
    for p in T3D.reachable_programs():
        v = tuple(G.run_program(p, n, True) for n in probes)
        if v != tv and v not in wrong:
            wrong[v] = 1
    wv = list(wrong)
    rng = random.Random(E.dev_entropy(label + "-draws-" + f, 0))
    for size in (4, 6, 8, 12, 16, 24):
        s = []
        for _ in range(200):
            idx = rng.sample(range(240), size)
            s.append(sum(1 for v in wv if all(v[i] is not None and v[i] == tv[i] for i in idx)))
        up = statistics.mean(s) + 1.96 * statistics.pstdev(s) / math.sqrt(len(s))
        if up < 0.05:
            return size
    return None


def job_q23(args):
    cat, d = args
    prov = Prov({d["name"]: (d["body"], d["final"], d["init"])})
    M.use_provider(prov)
    size = qualify(prov, d["name"], "A17-%s" % cat)
    q3 = None
    if size is not None:
        art = M.artifact_for(d["name"], prov.witness(d["name"]), EMITTER)
        tr = M.MetaTribunal.after_freeze(art, d["name"])
        q3 = tr.qualified(tr.score(art))
    return (cat, d["name"]), {"Q2_size": size, "Q3": q3}


def job_draw(args):
    """Q2, Q3 and (if both pass) the 16-recipient PRISTINE Q4 pilot for one
    draw. The acceptance DECISION is still taken in draw order by foundry()."""
    t0 = time.perf_counter()
    cat, d = args
    k, v = job_q23(args)
    if v["Q2_size"] is not None and v["Q3"]:
        specs = {d["name"]: (d["body"], d["final"], d["init"])}
        rows = [run_recipient((d["name"], "PRISTINE", FR.pristine().entries, i, v["Q2_size"],
                               "A17-%s-pilot" % cat, specs))[1] for i in range(N)]
        v["Q4_pristine_pilot"] = sum(r["qualified"] for r in rows)
        v["ACCEPTED_CANDIDATE"] = v["Q4_pristine_pilot"] <= 8
    else:
        v["ACCEPTED_CANDIDATE"] = False
    v["seconds"] = round(time.perf_counter() - t0, 1)
    return k, v


def run_recipient(args):
    """fam, arm, entries, i, size, label, specs"""
    fam, arm, entries, i, size, label, specs = args
    prov = Prov(specs)
    M.use_provider(prov)
    lib = FR.KLib(entries)
    c = FR.Cell(prov, fam, i, size, label=label)
    esc = E.Escrow(ESCROW)
    hits = FR.search_collect(lib, c.parsed, esc, ESCROW, c.seed, max_hits=MAX_HITS)
    fp, first = 0, None
    for prog, coord, ch in hits:
        art = M.artifact_for(fam, prog, EMITTER)
        tr = M.MetaTribunal.after_freeze(art, fam)
        if tr.qualified(tr.score(art)):
            first = {"charges": ch, "coordinate": coord, "program": list(prog), "sha256": art.sha256}
            break
        fp += 1
    return (fam, arm, label, i), {
        "recipient": i, "arm": arm, "family": fam, "escrow_spent": esc.spent, "hits": len(hits),
        "qualified": first is not None, "charges": first["charges"] if first else None,
        "coordinate": first["coordinate"] if first else None,
        "solution_program": first["program"] if first else None,
        "solution_body_key": T3E.body_key(first["program"][2]) if first else None,
        "artifact_sha256": first["sha256"] if first else None, "false_positives": fp}


def foundry(cats=("A", "B")):
    """Q2/Q3 in parallel over a draw-order prefix, then Q4 pilots in draw
    order; acceptance = first 4 qualifying draws per stratum."""
    st = {c: draws(c) for c in ("A", "B", "C")}
    write("A17_DRAWS_2026-09-26.json", {c: {"sha256": sha(st[c]), "draws": st[c]} for c in st})
    log("draws hashed A=%s B=%s C=%s" % tuple(sha(st[c])[:12] for c in ("A", "B", "C")))
    res = {}
    accepted = {c: {op: [] for op in STRATA} for c in cats}
    ptr = {(c, op): 0 for c in cats for op in STRATA}
    q = {}
    if (HERE / CKPT).exists():                          # resume: reuse checkpointed draws
        for line in (HERE / CKPT).read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            q[tuple(r["key"])] = r["v"]
        log("resumed %d checkpointed evaluations" % len(q))
    while True:
        open_ = [(c, op) for c in cats for op in STRATA
                 if len(accepted[c][op]) < K and ptr[(c, op)] < DRAWS]
        if not open_:
            break
        batch = []
        for c, op in open_:                               # next wave, in draw order
            need = K - len(accepted[c][op])
            take = st[c][op][ptr[(c, op)]: ptr[(c, op)] + max(2, need * 2)]
            batch += [(c, d) for d in take]
        todo = [(c, d) for c, d in batch if (c, d["name"]) not in q]
        with open(HERE / CKPT, "a", encoding="utf-8") as fh:        # checkpoint every draw
            for k, v in pool_iter(job_draw, todo):
                q[k] = v
                fh.write(json.dumps({"key": list(k), "v": v}, sort_keys=True) + "\n")
                fh.flush()
        for c, op in open_:
            lst = st[c][op]
            end = min(DRAWS, ptr[(c, op)] + max(2, (K - len(accepted[c][op])) * 2))
            for d in lst[ptr[(c, op)]:end]:
                if len(accepted[c][op]) < K and q[(c, d["name"])]["ACCEPTED_CANDIDATE"]:
                    accepted[c][op].append(d)
            ptr[(c, op)] = end
        log("foundry wave: %s" % {c: {op: "%d/%d" % (len(accepted[c][op]), ptr[(c, op)])
                                       for op in STRATA} for c in cats})
    for c in cats:
        fams = []
        for op in STRATA:
            acc = list(accepted[c][op])
            random.Random(I._seed("APHRODITE/A17/ASSIGN/%s/%s" % (c, op))).shuffle(acc)
            for d, role in zip(acc, ["OBSERVE", "VALIDATE", "TRANSFER", "TRANSFER"]):
                fams.append(dict(d, role=role, qualified_dev_size=q[(c, d["name"])]["Q2_size"],
                                 Q4_pristine_pilot=q[(c, d["name"])]["Q4_pristine_pilot"]))
        roles = {r: [f["name"] for f in fams if f["role"] == r] for r in ("OBSERVE", "VALIDATE", "TRANSFER")}
        ok = len(roles["OBSERVE"]) >= 3 and len(roles["VALIDATE"]) >= 3 and len(roles["TRANSFER"]) >= 2
        res[c] = {"accepted_pool_sha256": sha([accepted[c][op] for op in STRATA]),
                  "families": fams, "roles": roles,
                  "per_stratum": {op: {"accepted": len(accepted[c][op]), "evaluated": ptr[(c, op)]}
                                  for op in STRATA},
                  "DISPOSITION": "CATALOG_TESTABLE" if ok else "CATALOG_UNTESTABLE"}
    res["evaluations"] = {"%s/%s" % k: v for k, v in q.items()}
    return res


# ---------------------------------------------------------------- the assay (AMENDMENT 15 s2, s4-s7)
def L1_entries():
    art = read("S3_ARTIFACT_2026-09-23.json")
    assert FR.KLib(art["selected_entries"] + FR.pristine().entries).sha256() == art["selected_sha256"]
    return art["selected_entries"] + FR.pristine().entries


def schema_entry(name, schema):
    return {"name": name, "inits": list(G.H1_SPACE), "bodies": T3D.instantiate(schema),
            "finals": list(G.FINAL_SPACE), "schema": schema}


def coverage(entries):
    lib = FR.KLib(entries)
    out = []
    for e, bodies in zip(lib.entries, lib._bodies):
        out += [("fold", i, b, f) for i in e["inits"] for b in bodies for f in e["finals"]]
    return list(dict.fromkeys(out))


def members_in(space, observed, parsed):
    target = I.behavior_id(observed, True)
    out = []
    for p in space:
        ok = True
        for nums, gold in parsed:
            got = G.run_program(p, nums, True)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok and I.behavior_id(p, True) == target:
            out.append(p)
    return out


def certified_classes(observed, cov):
    """observed: list of {family, program, parsed}. D2 + D3 with certificates."""
    buckets = {}
    for o in observed:
        buckets.setdefault(I.behavior_id(tuple(o["program"]), True), []).append(o)
    classes, certs = [], []
    for bid, obs in sorted(buckets.items()):
        progs = [tuple(o["program"]) for o in obs]
        mem = members_in(cov, progs[0], obs[0]["parsed"]) if cov is not None else []
        rec = CT.certify(progs + mem, anchor=progs[0])
        certs.append({"bucket": bid, "PASS": rec["PASS"], "sub_buckets": rec["sub_buckets"]})
        groups = [(progs, mem)]
        if not rec["PASS"]:
            bat = list(I.B1) + CT.b_cert() + CT.adversarial(progs + mem)
            sub = {}
            for p in dict.fromkeys(progs + mem):
                sub.setdefault(I.values(p, True, bat), []).append(p)
            groups = [([p for p in v if p in progs], [p for p in v if p in mem])
                      for v in sub.values() if any(p in progs for p in v)]
        for gp, gm in groups:
            classes.append({"bucket": bid, "families": sorted({o["family"] for o in obs
                                                               if tuple(o["program"]) in gp}),
                            "observed": [list(p) for p in gp],
                            "member_bodies": sorted({p[2] for p in gm} | {p[2] for p in gp})})
    return classes, certs


def select(cands, start, cells):
    libs = {n: FR.KLib(e) for n, e in cands.items()}
    costs = {n: [c.cost(l)[0] for c in cells] for n, l in libs.items()}
    table = {}
    for n in cands:
        row = FR.paired_summary(costs["INHERITED"], costs[n])
        row.update({"sha256": libs[n].sha256(), "size": libs[n].size(),
                    "eligible": n != "INHERITED" and row["lower95_one_sided"] > 0})
        table[n] = row
    elig = [n for n in table if table[n]["eligible"]]
    chosen = (min(elig, key=lambda n: (-table[n]["mean_paired_saving"], table[n]["size"],
                                       table[n]["sha256"])) if elig else "INHERITED")
    return chosen, table, sum(sum(v) for v in costs.values())


def candidates_from(derived, start, classes):
    cands = {"INHERITED": start,
             "MEMORISE": [{"name": "memorised", "inits": list(G.H1_SPACE),
                           "bodies": sorted({b for c in classes for b in c["member_bodies"]}),
                           "finals": list(G.FINAL_SPACE)}] + start}
    for k, d in enumerate(derived):
        cands["SCHEMA_%d" % k] = [schema_entry("g2_new", d["schema"])] + start
    if len(derived) > 1:
        allb = list(dict.fromkeys(b for d in derived for b in T3D.instantiate(d["schema"])))
        cands["SCHEMA_ALL"] = [{"name": "g2_new", "inits": list(G.H1_SPACE), "bodies": allb,
                                "finals": list(G.FINAL_SPACE),
                                "schemas": [d["schema"] for d in derived]}] + start
    return cands


def donor(args):
    cat, kind, r, fams, specs = args
    t0 = time.perf_counter()
    prov = Prov(specs)
    start = L1_entries() if kind == "G1" else FR.pristine().entries
    base, cov = FR.KLib(start), coverage(start)
    size = {f["name"]: f["qualified_dev_size"] for f in fams}
    obs_f = [f["name"] for f in fams if f["role"] == "OBSERVE"]
    val_f = [f["name"] for f in fams if f["role"] == "VALIDATE"]
    meta, observed = 0, []
    for fam in obs_f:
        for c in range(R_OBS):
            cell = FR.Cell(prov, fam, r * R_OBS + c, size[fam], label="A17-%s-obs/r%d" % (cat, r))
            esc = E.Escrow(ESCROW)
            hits = FR.search_collect(base, cell.parsed, esc, ESCROW, cell.seed, max_hits=1)
            meta += esc.spent
            if hits:
                observed.append({"family": fam, "program": list(hits[0][0]), "parsed": cell.parsed,
                                 "charges": hits[0][2]})
    classes, certs = certified_classes(observed, cov)
    derived = T3D.derive_schemas([c["member_bodies"] for c in classes])
    for d in derived:
        d.update(T3E.semantically_new(d["schema"]))
    cands = candidates_from(derived, start, classes)
    cells = [FR.Cell(prov, f, r * R_VAL + j, size[f], label="A17-%s-val/r%d" % (cat, r))
             for f in val_f for j in range(R_VAL)]
    chosen, table, vcost = select(cands, start, cells)
    meta += vcost
    if chosen == "SCHEMA_ALL":
        sel_schemas = [d["schema"] for d in derived]
        sel_new = any(d["SEMANTICALLY_NEW"] for d in derived)
    elif chosen.startswith("SCHEMA_"):
        d = derived[int(chosen.split("_")[1])]
        sel_schemas, sel_new = [d["schema"]], d["SEMANTICALLY_NEW"]
    else:
        sel_schemas, sel_new = [], False
    return {"catalog": cat, "donor": kind, "replicate": r,
            "trace": {"observed": [{k: v for k, v in o.items() if k != "parsed"} for o in observed],
                      "class_certificates": certs, "classes": classes,
                      "candidate_schemas": derived, "selection_table": table, "selected": chosen,
                      "selected_schemas": sel_schemas, "selected_entries": cands[chosen],
                      "selected_sha256": table[chosen]["sha256"]},
            "observed_class_set": sorted(c["bucket"] for c in classes),
            "observed_body_keys": sorted({T3E.body_key(o["program"][2]) for o in observed}),
            "SELECTED_SEMANTICALLY_NEW": sel_new, "meta_charges": meta,
            "seconds": round(time.perf_counter() - t0, 1)}


def shams_for(cat):
    out = []
    for k in range(8):
        rng = random.Random(I._seed("APHRODITE/A17-%s/SHAM/v1/%d" % (cat, k)))
        while True:
            b = rng.choice(G.BODY_SPACE)
            t = I.normalise(I.parse(b))
            paths = []

            def walk(n, p):
                for i, a in enumerate(n[1]):
                    paths.append(p + (i,))
                    walk(a, p + (i,))
            walk(t, ())
            if not paths:
                continue
            path = rng.choice(paths)

            def put(n, p):
                if not p:
                    return ("hole", [])
                op, args = n
                args = list(args)
                args[p[0]] = put(args[p[0]], p[1:])
                return (op, args)
            s = T3D.schema_src(put(t, path))
            if len(T3D.instantiate(s)) >= 2 and T3E.semantically_new(s)["SEMANTICALLY_NEW"]:
                break
        e = schema_entry("sham_%d" % k, s)
        out.append({"k": k, "schema": s, "entry": e, "sha256": FR.KLib([e] + L1_entries()).sha256()})
    return out


def r1(donors):
    g = {d["replicate"]: d for d in donors if d["donor"] == "G1"}
    p = {d["replicate"]: d for d in donors if d["donor"] == "P"}
    altered = [r for r in range(R_D) if g[r]["observed_class_set"] != p[r]["observed_class_set"]]
    a = sum(1 for r in range(R_D) if g[r]["SELECTED_SEMANTICALLY_NEW"] and not p[r]["SELECTED_SEMANTICALLY_NEW"])
    b = sum(1 for r in range(R_D) if p[r]["SELECTED_SEMANTICALLY_NEW"] and not g[r]["SELECTED_SEMANTICALLY_NEW"])
    both = [r for r in range(R_D) if g[r]["SELECTED_SEMANTICALLY_NEW"] and p[r]["SELECTED_SEMANTICALLY_NEW"]]
    n = a + b
    pv = sum(math.comb(n, k) for k in range(a, n + 1)) / 2 ** n if n else 1.0
    rb, fb = pv < 0.05 and a > b, None
    if a == 0 and b == 0 and both:
        s = FR.paired_summary([g[r]["meta_charges"] for r in both], [p[r]["meta_charges"] for r in both])
        fb = {"n": len(both), "upper95_G1_minus_P": s["mean_paired_saving"] + 1.645 * s["se"]}
        rb = fb["upper95_G1_minus_P"] < 0
    g1new = [r for r in range(R_D) if g[r]["SELECTED_SEMANTICALLY_NEW"]]
    return {"altered_replicates": altered, "R1a": bool(altered), "G1_new_replicates": g1new,
            "P_new_replicates": [r for r in range(R_D) if p[r]["SELECTED_SEMANTICALLY_NEW"]],
            "discordant_G1_only": a, "discordant_P_only": b, "sign_test_p": pv,
            "meta_cost_fallback": fb, "R1b": rb, "PASS": bool(altered) and rb,
            "L2_replicate": g1new[0] if g1new else None}


def summarise(rows):
    q = [r for r in rows if r["qualified"]]
    return {"censored_effort": round(statistics.mean([r["charges"] if r["qualified"] else ESCROW
                                                     for r in rows]), 1),
            "qualified": len(q), "hits": sum(r["hits"] for r in rows),
            "false_positives": sum(r["false_positives"] for r in rows)}


def assay(cat, cataloginfo):
    t0 = time.perf_counter()
    fams = cataloginfo["families"]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
    out = {"catalog": cat, "accepted_pool_sha256": cataloginfo["accepted_pool_sha256"]}
    shams = shams_for(cat)
    out["shams"] = [{k: v for k, v in s.items() if k != "entry"} for s in shams]
    log("E(%s) shams hashed %s" % (cat, [(s["schema"], s["sha256"][:8]) for s in shams]))
    donors = pool_map(donor, [(cat, kind, r, fams, specs) for r in range(R_D) for kind in ("G1", "P")])
    write("A17_%s_DONORS_2026-09-26.json" % cat, donors)
    for d in sorted(donors, key=lambda d: (d["replicate"], d["donor"])):
        log("E(%s) donor %s r%d classes=%d cands=%s sel=%s NEW=%s" % (
            cat, d["donor"], d["replicate"], len(d["trace"]["classes"]),
            [(x["schema"], x["SEMANTICALLY_NEW"]) for x in d["trace"]["candidate_schemas"]],
            d["trace"]["selected"], d["SELECTED_SEMANTICALLY_NEW"]))
    rr = r1(donors)
    out["R1"] = rr
    out["donor_adjudication_valid"] = True
    log("E(%s) R1 %s" % (cat, {k: v for k, v in rr.items()}))
    if rr["L2_replicate"] is None or not rr["PASS"]:
        out["BOUNDED_RSI"] = "NO"
        out["failure_link"] = ("R1: no SEMANTICALLY_NEW selection by DONOR_G1"
                               if rr["L2_replicate"] is None else "R1: G1-dependence not shown")
        out["R1_failure_is_novelty"] = True
        out["seconds"] = round(time.perf_counter() - t0, 1)
        return out
    g1rep = next(d for d in donors if d["donor"] == "G1" and d["replicate"] == rr["L2_replicate"])
    L1 = L1_entries()
    l2 = g1rep["trace"]["selected_entries"]
    out["L2"] = {"replicate": rr["L2_replicate"], "schemas": g1rep["trace"]["selected_schemas"],
                 "sha256": FR.KLib(l2).sha256()}
    prep = next(d for d in donors if d["donor"] == "P" and d["replicate"] == rr["L2_replicate"])
    arms = {"L2": l2, "L1": L1, "PRISTINE": FR.pristine().entries}
    for s in shams:
        arms["L1+SHAM_%d" % s["k"]] = [s["entry"]] + L1
    if prep["SELECTED_SEMANTICALLY_NEW"]:
        arms["L1+P_SCHEMA"] = [schema_entry("g2_new", prep["trace"]["selected_schemas"][0])] + L1
    trans = [f for f in fams if f["role"] == "TRANSFER"]
    jobs = [(f["name"], a, arms[a], i, f["qualified_dev_size"], "A17-%s-rx" % cat, specs)
            for f in trans for a in arms for i in range(N)]
    rows = dict(pool_map(run_recipient, jobs))
    fnames = [f["name"] for f in trans]
    det = {f: {a: [rows[(f, a, "A17-%s-rx" % cat, i)] for i in range(N)] for a in arms} for f in fnames}
    pf = {f: {a: summarise(det[f][a]) for a in arms} for f in fnames}
    out["arms"] = {a: FR.KLib(e).sha256() for a, e in arms.items()}
    out["per_family"], out["detail"] = pf, det
    shn = [a for a in arms if a.startswith("L1+SHAM_")]
    fam, d2, d1 = {}, [], []
    g1m, obsk = T3E.g1_mechanisms(), set(g1rep["observed_body_keys"])
    for f in fnames:
        a = [r["charges"] if r["qualified"] else ESCROW for r in det[f]["L2"]]
        b = [r["charges"] if r["qualified"] else ESCROW for r in det[f]["L1"]]
        d2 += a
        d1 += b
        s = FR.paired_summary(b, a)
        se = sorted(pf[f][x]["censored_effort"] for x in shn)
        e2 = pf[f]["L2"]["censored_effort"]
        q = [r for r in det[f]["L2"] if r["qualified"]]
        att = [r for r in q if r["coordinate"] == "g2_new" and r["solution_body_key"] not in obsk
               and r["solution_body_key"] not in g1m]
        fam[f] = {"paired_L2_vs_L1": s, "L2_q": pf[f]["L2"]["qualified"], "L1_q": pf[f]["L1"]["qualified"],
                  "effect": s["lower95_one_sided"] > 0 and pf[f]["L2"]["qualified"] >= pf[f]["L1"]["qualified"],
                  "beats_every_sham": e2 < se[0], "below_sham_median": e2 < statistics.median(se),
                  "attributed": len(att), "qualified": len(q), "R3_family": bool(q) and 2 * len(att) > len(q)}
    pooled = FR.paired_summary(d1, d2)
    eff = [f for f in fnames if fam[f]["effect"]]
    hits = sum(pf[f]["L2"]["hits"] for f in fnames)
    fps = sum(pf[f]["L2"]["false_positives"] for f in fnames)
    c = {"R1_G1_dependent_derivation": rr["PASS"],
         "R2_G2_beats_G1": pooled["lower95_one_sided"] > 0 and all(fam[f]["L2_q"] >= fam[f]["L1_q"] for f in fnames),
         "R3_attribution_new_mechanism": sum(fam[f]["R3_family"] for f in fnames) >= 2,
         "R4_hostile_controls": (sum(fam[f]["beats_every_sham"] for f in fnames) * 2 >= len(fnames)
                                 and all(fam[f]["below_sham_median"] for f in eff)
                                 and (fps / hits if hits else 0.0) <= 0.25
                                 and all(FR.KLib(e).desugars()[0] for e in arms.values())),
         "R5_clean_transplant": True}
    out.update({"conditions": c, "pooled_L2_vs_L1": pooled, "per_family_criterion": fam,
                "L2_fp_fraction": round(fps / hits, 4) if hits else 0.0,
                "BOUNDED_RSI": "YES" if all(c.values()) else "NO",
                "failed": [k for k, v in c.items() if not v], "R1_failure_is_novelty": False,
                "seconds": round(time.perf_counter() - t0, 1)})
    return out


# ---------------------------------------------------------------- E4
def e4_job(args):
    fset, proc, observed, cov_kind = args
    import tier3d as T3
    M.use_provider(T3)
    cov = coverage(FR.pristine().entries) if proc == "WHOLE" else None
    if proc == "WHOLE":
        classes, certs = certified_classes(observed, cov)
        derived = T3.derive_schemas([c["member_bodies"] for c in classes])
    else:
        certs = []
        bk = {}
        for o in observed:
            bk.setdefault(I.behavior_id(tuple(o["program"]), True), set()).add(o["program"][2])
        classes = [{"member_bodies": sorted(v)} for v in bk.values()]
        derived = T3.derive_schemas([c["member_bodies"] for c in classes])
    start = FR.pristine().entries
    cands = candidates_from(derived, start, classes)
    cells = [FR.Cell(T3, f, j, 4, label="A17-E4-val/%s" % fset)
             for f in ("md_e_negsum_times_first", "md_f_sumdec_plus_last", "md_g_prodinc_minus_first")
             for j in range(R_VAL)]
    chosen, table, _ = select(cands, start, cells)
    g1m = T3E.g1_mechanisms()
    sel_bodies = [b for e in cands[chosen] if e.get("name") == "g2_new" for b in e["bodies"]]
    recovered = bool(sel_bodies) and {T3E.body_key(b) for b in sel_bodies} == g1m
    return (fset, proc), {"derived": [d["schema"] for d in derived], "selected": chosen,
                          "table": {k: {x: v[x] for x in ("mean_paired_saving", "lower95_one_sided", "eligible")}
                                    for k, v in table.items()},
                          "certificates": certs, "RECOVERED": recovered}


def e4():
    import tier3d as T3
    import tier3c as T3C
    import improver as T3A
    art = read("S3_ARTIFACT_2026-09-23.json")
    quals = read("T3D_QUALIFICATION_2026-09-23.json")["quals"]

    def parsed_for(mod, fam, n, label):
        ex = mod.tasks(fam, n, E.dev_entropy(label + fam, 0))
        return [(T3.nums_of(t), t["gold"]) for t in ex]
    f1 = []
    for cl in art["classes"]:
        for p in cl["observed_programs"]:
            fam = cl["families"][0]
            prog = p
            if fam == "md_b_sumsq_plus_first":
                prog = ["fold", "0", "(acc - (v * v))", "(first - acc)"]
            f1.append({"family": fam, "program": prog,
                       "parsed": parsed_for(T3, fam, quals[fam]["qualified_dev_size"], "A17-E4-F1-")})
    c3 = read("TIER3C_ARTIFACT_2026-09-22.json")
    f2 = [{"family": c3["observe_used"][k // 3], "program": p,
           "parsed": parsed_for(T3C, c3["observe_used"][k // 3], 8, "A17-E4-F2-")}
          for k, p in enumerate(c3["observed_programs"])]
    a3 = read("TIER3A_ARTIFACT_2026-09-22.json")
    # F3* (AMENDMENT 17 s3): Tier-3A recorded observations, with every
    # md_sumsq_plus_last observation in the plain additive form replaced by the
    # recorded compensating member of the same family -- the substitution F1
    # applies to md_b. The replacement must certify into the same class.
    comp = ["fold", "0", "(acc - (v * v))", "(last - acc)"]
    f3, f3_subs = [], []
    for k, p in enumerate(a3["observed_successful_programs"]):
        fam = a3["meta_dev_families"][k // 2]
        prog = p
        if fam == "md_sumsq_plus_last" and p[2] == "(acc + (v * v))":
            rec = CT.certify([tuple(p), tuple(comp)], anchor=tuple(p))
            f3_subs.append({"index": k, "original": p, "replacement": comp, "certificate_PASS": rec["PASS"]})
            if not rec["PASS"]:
                raise SystemExit("F3* substitution does not certify into the same class")
            prog = comp
        f3.append({"family": fam, "program": prog,
                   "parsed": parsed_for(T3A, fam, 8, "A17-E4-F3-")})
    sets = {"F1": f1, "F2": f2, "F3": f3}
    res = dict(pool_map(e4_job, [(k, proc, v, None) for k, v in sets.items() for proc in ("BODY_ONLY", "WHOLE")]))
    whole = sum(res[(k, "WHOLE")]["RECOVERED"] for k in sets)
    body = sum(res[(k, "BODY_ONLY")]["RECOVERED"] for k in sets)
    disp = ("SUPPORTED" if whole == 3 and body == 0 else
            "NOT_SUPPORTED" if body >= whole else "INCONCLUSIVE")
    return {"results": {"%s/%s" % k: v for k, v in res.items()},
            "whole_recovered": whole, "body_only_recovered": body, "S1_NECESSITY": disp,
            "F3_star_substitutions": f3_subs}


# ---------------------------------------------------------------- AMENDMENT 17 s0 gates
def pilot_draws():
    """One behaviour-distinct draw per stratum from the PILOT seed -- never a
    catalog seed; pilot families are used for equivalence and timing only."""
    rng = random.Random(I._seed("APHRODITE/A17/PILOT/v1"))
    finals = [f for f in G.FINAL_SPACE if _mentions(f, "acc")]
    out = []
    for op in STRATA:
        pool = [b for b in G.BODY_SPACE if T3E._top_op(b) == op and _mentions(b, "acc") and _mentions(b, "v")]
        p = ("fold", rng.choice(G.H1_SPACE), rng.choice(pool), rng.choice(finals))
        out.append({"name": "pilot_%s" % op, "stratum": op, "init": p[1], "body": p[2], "final": p[3]})
    return out


def job_q2_equiv(d):
    """Fast Q2 vs reference Q2 on one pilot draw: identical target vector,
    identical wrong-vector SET, identical survivor count on 50 calibration
    samples per size (reference counting), and the fast decision + timing."""
    prov = Prov({d["name"]: (d["body"], d["final"], d["init"])})
    lab = "A17-PILOT"
    t0 = time.perf_counter()
    tv, wv = q2_vectors(prov, d["name"], lab)
    size = qualify(prov, d["name"], lab)
    fast_s = time.perf_counter() - t0
    FE = _fe()
    target = prov.witness(d["name"])
    pool = prov.tasks(d["name"], 240, E.dev_entropy(lab + "-pool-" + d["name"], 0))
    probes = [prov.nums_of(t) for t in pool]
    rtv = tuple(G.run_program(target, n, True) for n in probes)
    pinfo = [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0)) for n in probes]
    reach = T3D.reachable_programs()
    srng = random.Random(I._seed("APHRODITE/A17/PILOT/SAMPLE/" + d["name"]))
    vec_mm, wvset = 0, set(wv)
    for p in srng.sample(reach, 3000):          # hoisted fast vector vs reference vector
        _, i, b, fi = p
        al = [FE._fold_acc(FE.fn(i), FE.fn(b), vals, fst, lst) for vals, fst, lst, _ in pinfo]
        fv = tuple(None if x is FE._FAIL else FE._final(FE.fn(fi), x, vl, fst, lst)
                   for x, (_v, fst, lst, vl) in zip(al, pinfo))
        rv = tuple(G.run_program(p, n, True) for n in probes)
        vec_mm += fv != rv
        vec_mm += (rv != rtv) and (rv not in wvset)      # every wrong ref vector is in the fast set
    rw = wv
    count = q2_counter(tv, wv)
    rng = random.Random(I._seed("APHRODITE/A17/PILOT/COUNTS/" + d["name"]))
    cm = 0
    for sz in (4, 6, 8, 12, 16, 24):
        for _ in range(50):
            idx = rng.sample(range(240), sz)
            ref = sum(1 for v in rw if all(v[i] is not None and v[i] == rtv[i] for i in idx))
            cm += ref != count(idx)
    return {"draw": d["name"], "target_equal": tv == rtv, "sampled_programs": 3000,
            "vector_mismatches": vec_mm, "wrong_set_equal": vec_mm == 0,
            "n_wrong": len(wv), "count_mismatches": cm, "fast_Q2_size": size,
            "fast_q2_seconds_contended": round(fast_s, 1)}


def job_fe_equiv(k):
    """200 random programs x 60 inputs per job, fasteval vs reference."""
    sys.path.insert(0, str(HERE / "accel"))
    import fasteval as FE
    ref = G.run_program
    rng = random.Random(I._seed("APHRODITE/A17/FE-EQUIV/%d" % k))
    g5 = g5_bodies()
    inputs = [list(x) for x in list(I.B1)[:20] + list(I.B1_BOUNDARY)[:20]]
    inputs = [x for x in inputs if isinstance(x, list) and x] or []
    while len(inputs) < 60:
        inputs.append([rng.randint(2, 30) for _ in range(rng.randint(2, 60))] + [rng.randint(1, 97)])
    mm, n = [], 0
    for _ in range(200):
        body = rng.choice(g5) if rng.random() < 0.3 else rng.choice(G.BODY_SPACE)
        p = ("fold", rng.choice(G.INIT_SPACE), body, rng.choice(G.FINAL_SPACE))
        for x in inputs:
            n += 1
            a, b = ref(p, x, True), FE.run_program(p, x, True)
            if a != b or type(a) is not type(b):
                mm.append([list(p), x[:5], repr(a), repr(b)])
    return {"pairs": n, "mismatches": mm[:10], "n_mismatches": len(mm)}


def gate():
    t0 = time.perf_counter()
    g = conformance_gate()
    log("conformance %s (%.0fs)" % (g, time.perf_counter() - t0))
    fe = pool_map(job_fe_equiv, list(range(24)))
    fe_sum = {"pairs": sum(x["pairs"] for x in fe), "n_mismatches": sum(x["n_mismatches"] for x in fe),
              "examples": [m for x in fe for m in x["mismatches"]][:10]}
    log("fasteval equivalence %s" % {k: v for k, v in fe_sum.items() if k != "examples"})
    q2 = pool_map(job_q2_equiv, pilot_draws())
    for r in q2:
        log("q2 equiv %s" % r)
    q2_ok = all(r["target_equal"] and r["wrong_set_equal"] and r["count_mismatches"] == 0 for r in q2)
    return {"conformance": g, "fasteval_equivalence": fe_sum,
            "FASTEVAL_ADMITTED": g["GREEN"] and fe_sum["n_mismatches"] == 0 and fe_sum["pairs"] >= 200_000,
            "fast_q2_equivalence": q2, "FAST_Q2_ADMITTED": q2_ok,
            "seconds": round(time.perf_counter() - t0, 1)}


def conformance_gate():
    std = CF.check()
    rng = random.Random(I._seed("APHRODITE/A17/CONF/v1"))
    progs = [("fold", rng.choice(G.INIT_SPACE), rng.choice(G.BODY_SPACE), rng.choice(G.FINAL_SPACE))
             for _ in range(30)]
    p2 = [CF.check_whole_program(p, b, EMITTER) for p in progs for b in (I.B1, I.B1_BOUNDARY)]
    mm = sum(len(x["mismatches"]) for x in p2)
    return {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"],
            "part2_checked": sum(x["checked"] for x in p2), "part2_mismatches": mm,
            "GREEN": std["GREEN"] and mm == 0}


if __name__ == "__main__":
    stage = sys.argv[1]
    use_fasteval()
    log("stage %s fasteval=%s workers=%d" % (stage, os.environ.get("A17_FASTEVAL") == "1", WORKERS))
    if stage == "gate":
        r = gate()
        write("A17_GATE_2026-09-26.json", r)
        log("GATE conformance=%s FASTEVAL_ADMITTED=%s FAST_Q2_ADMITTED=%s" % (
            r["conformance"]["GREEN"], r["FASTEVAL_ADMITTED"], r["FAST_Q2_ADMITTED"]))
    elif stage == "foundry":
        if not read("A17_GATE_2026-09-26.json")["FAST_Q2_ADMITTED"]:
            raise SystemExit("FAST Q2 NOT ADMITTED")
        g = conformance_gate()
        log("conformance %s" % g)
        if not g["GREEN"]:
            raise SystemExit("CONFORMANCE RED")
        r = foundry()
        r["conformance_before"] = g
        write("A17_CATALOGS_2026-09-26.json", r)
        log("CATALOG_A %s roles %s" % (r["A"]["DISPOSITION"], {k: len(v) for k, v in r["A"]["roles"].items()}))
        log("CATALOG_B %s roles %s" % (r["B"]["DISPOSITION"], {k: len(v) for k, v in r["B"]["roles"].items()}))
    elif stage in ("e1", "e2"):
        cat = "A" if stage == "e1" else "B"
        cats = read("A17_CATALOGS_2026-09-26.json")
        if cats[cat]["DISPOSITION"] != "CATALOG_TESTABLE":
            write("A17_%s_RESULT_2026-09-26.json" % stage.upper(), {"BOUNDED_RSI": "UNTESTABLE",
                                                                   "reason": "CATALOG_UNTESTABLE"})
            log("%s UNTESTABLE (catalog)" % stage)
        else:
            g = conformance_gate()
            log("%s conformance %s" % (stage, g))
            r = assay(cat, cats[cat])
            r["conformance_before"] = g
            write("A17_%s_RESULT_2026-09-26.json" % stage.upper(), r)
            log("%s BOUNDED_RSI=%s %s" % (stage, r["BOUNDED_RSI"], r.get("failed") or r.get("failure_link")))
    elif stage == "e4":
        r = e4()
        write("A17_E4_RESULT_2026-09-26.json", r)
        log("E4 S1_NECESSITY=%s whole=%d body=%d" % (r["S1_NECESSITY"], r["whole_recovered"],
                                                     r["body_only_recovered"]))
