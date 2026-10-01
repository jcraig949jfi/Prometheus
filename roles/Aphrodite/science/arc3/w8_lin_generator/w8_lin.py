"""ARC3 W8 -- CG-1 LIN-NX natural-recurrence generator, TASK SIDE ONLY (W1 WP-1).
FORENSIC, NOT A DISPOSITION. No donor is run. No existing file is modified.

Generator (W1 REPORT s4, CG-1):
  LIN   founders: i.i.d. W5-shaped PCFG draws until 8 families pass the NAT screen;
        then loop: parent = uniform archived (admitted) family; ONE edit
          p = .5 operator swap at a uniformly chosen INTERNAL node (new op != old),
          else a uniformly chosen NON-ROOT subterm -> a fresh E1 (atom or op(atom, atom));
        canonicalise (T3D.in_space_body, G5); re-draw init (H1) and final (acc-finals);
        NAT screen (accumulating + T4 family_profile admissible); archive if admitted.
  STAR  twin: the SAME edit law applied to a FRESH PCFG draw each time (no ancestry).
  U     reference: A19 NAT rule (uniform over the W5 body list), same screen.
  Deviation from W1's probe code (declared): W1's mutate() could also pick the ROOT for
  replacement (the whole body -> an E1); CG-1's text and W1's docstring say non-root.
Supply = first N admitted families. Family names: letters only (no digits).

Subcommands (python w8_lin.py <cmd> ...):
  gen      N kinds:seeds...       -> W8_SUPPLIES.json          (2-core pool)
  genuine                         -> W8_GENUINE_CACHE.json     (all wrap pairs + panel)
  panel                           -> W8_PANEL.json             (frequency-matched on U)
  cover                           -> W8_COVER.json             (PRISTINE window per family)
  analyse                         -> W8_RESULTS.json
"""
import hashlib
import bisect
import json
import math
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ["A17_FASTEVAL"] = "1"
os.environ.setdefault("A18_TAG", "A19")
# the W2 G5 signature table (w2_fallback.sig_table) lives in the session scratchpad
os.environ.setdefault("W2_SCRATCH", "C:/Users/jcrai/AppData/Local/Temp/claude/C--Prometheus/"
                      "fd24c325-0446-4c1e-8406-68bd122d26aa/scratchpad")
HERE = Path(__file__).resolve().parent
ARC3 = HERE.parent
ROOT = HERE.parents[2]
ENG = ROOT / "engine"
for p in (ENG, ENG / "accel", ROOT / "science" / "compounding" / "rb1",
          ARC3 / "c3r2_feasibility", ARC3 / "w2_learnability"):
    sys.path.insert(0, str(p))
import a17  # noqa: E402
import a18  # noqa: E402
from a18 import G, T3D, I  # noqa: E402
import engine as E  # noqa: E402
import fair as FR  # noqa: E402

NPROC = int(os.environ.get("W8_NPROC", "2"))
OPS = [tmpl for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())]
OPNAMES = [n for n, _ in sorted(E.PRIMITIVES.items())]
ATOMS = list(G.BODY_ATOMS)
COMM = ("add", "mul", "gcd")
IDW = ["(1 * {S})", "({S} * 1)", "({S} // 1)", "({S} - 0)", "({S} + 0)", "(0 + {S})", "pow({S}, 1)"]
ATOM_OPS = {"var:acc", "var:v", "var:first", "var:last", "const:0", "const:1"}


def log(m):
    print("[W8 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def init():
    a18.worker_init()
    T3D.in_space_body("(acc + v)")


# ------------------------------------------------------------------ PCFG (W5-shaped; = W1)
def e1(rng):
    if rng.random() < 0.5:
        return rng.choice(ATOMS)
    return rng.choice(OPS).format(rng.choice(ATOMS), rng.choice(ATOMS))


def e2(rng):
    return rng.choice(OPS).format(e1(rng), e1(rng))


def e3(rng):
    return rng.choice(OPS).format(rng.choice(ATOMS), e2(rng))


def pcfg(rng):
    return e3(rng) if rng.random() < 0.95 else e2(rng)


def mutate(rng, src):
    """CG-1 edit law: p=.5 op swap at a random internal node, else a random NON-ROOT
    subterm -> fresh E1. Falls back to the other branch if one is impossible."""
    t = I.parse(src)
    nodes = []

    def walk(x, p):
        nodes.append((p, x))
        for i, c in enumerate(x[1]):
            walk(c, p + (i,))
    walk(t, ())
    internal = [p for p, x in nodes if x[1]]
    nonroot = [p for p, x in nodes if p]

    def get(x, p):
        return x if not p else get(x[1][p[0]], p[1:])

    def put(x, p, y):
        if not p:
            return y
        op, args = x
        args = list(args)
        args[p[0]] = put(args[p[0]], p[1:], y)
        return (op, args)
    if internal and (rng.random() < 0.5 or not nonroot):
        p = rng.choice(internal)
        sub = get(t, p)
        new = (rng.choice([o for o in OPNAMES if o != sub[0]]), sub[1])
    else:
        p = rng.choice(nonroot)
        new = I.parse(e1(rng))
    return I.to_src(put(t, p, new))


# ------------------------------------------------------------------ supply
_LET = "abcdefghijklmnopqrstuvwxyz"


def fam_name(kind, seed, j):
    x = (["LIN", "STAR", "U", "LIND"].index(kind) * 100 + seed) * 1000 + j
    s = ""
    for _ in range(5):
        s += _LET[x % 26]
        x //= 26
    return "w" + s


def supply(kind, seed, n_fam, max_prop=150000):
    import ruler_v2 as R
    import tribunal_t4 as T4
    rng = random.Random(I._seed("ARC3/W8/SUPPLY/%s/%d" % (kind, seed)))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    archive, fams, prop, acc_n, t0 = [], [], 0, 0, time.time()
    while len(fams) < n_fam and prop < max_prop:
        prop += 1
        if kind == "U":
            src = rng.choice(G.BODY_SPACE)
        elif kind in ("LIN", "LIND"):
            src = pcfg(rng) if len(archive) < 8 else mutate(rng, rng.choice(archive))
        elif kind == "STAR":
            src = mutate(rng, pcfg(rng))
        else:
            raise ValueError(kind)
        b = T3D.in_space_body(src)
        if b is None or not R.accumulating(b):
            continue
        if kind == "LIND" and b in archive:      # CG-1d duplicate-body guard (variant)
            continue
        acc_n += 1
        p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
        if not T4.family_profile(p)["admissible"]:
            continue
        fams.append([fam_name(kind, seed, len(fams)), p[1], p[2], p[3]])
        archive.append(b)
    return {"families": fams, "stats": {"proposals": prop, "accumulating": acc_n, "admitted": len(fams),
                                        "seconds": round(time.time() - t0, 1)}}


def _gen_job(a):
    kind, seed, n = a
    return "%s:%d" % (kind, seed), supply(kind, seed, n)


# ------------------------------------------------------------------ schemas
_L1 = None


def l1keys():
    global _L1
    if _L1 is None:
        _L1 = {key(I.normalise(I.parse(x))) for x in FR.LEVEL1}
    return _L1


def key(t):
    op, args = t
    if not args:
        return op
    ks = [key(a) for a in args]
    if op in COMM:
        ks = sorted(ks)
    return "%s(%s)" % (op, ",".join(ks))


def nops(t):
    return 0 if (not t[1] or t[0].startswith("hole")) else 1 + sum(nops(a) for a in t[1])


def has_hole(t):
    return t[0].startswith("hole") or any(has_hole(a) for a in t[1])


def schemas(body):
    """W1's composed one-hole schemas (hole at a non-root LEVEL1 subterm, >= 2 ops
    outside). Returns {key: (w_src, S_src) or None}: the wrap decomposition
    w = op(atom, S) / op(S, atom) when it exists (else None: not a composition)."""
    t = I.normalise(I.parse(body))
    out = {}

    def put(x, p):
        if not p:
            return ("hole", [])
        op, args = x
        args = list(args)
        args[p[0]] = put(args[p[0]], p[1:])
        return (op, args)

    def walk(x, p):
        for i, c in enumerate(x[1]):
            q = p + (i,)
            if key(c) in l1keys():
                s = put(t, q)
                if nops(s) >= 2:
                    k = key(s)
                    dec = None
                    a0, a1 = s[1] if len(s[1]) == 2 else (None, None)
                    for atom, ch in ((a0, a1), (a1, a0)):
                        if atom is not None and atom[0] in ATOM_OPS and has_hole(ch) and nops(ch) >= 1:
                            dec = (T3D.schema_src(s), T3D.schema_src(ch))
                    out[k] = dec
            walk(c, q)
    walk(t, ())
    return out


# ------------------------------------------------------------------ genuine cache
def _genuine_job(pairs):
    import genuine_motifs as GM
    out = {}
    for w, s in pairs:
        try:
            out["%s||%s" % (w, s)] = bool(GM.genuine(w, s)[0])
        except Exception as ex:  # noqa: BLE001
            out["%s||%s" % (w, s)] = None
    return out


def run_genuine(pairs, cache_path):
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    todo = sorted({p for p in pairs if "%s||%s" % p not in cache})
    log("genuine: %d pairs, %d to test" % (len(set(pairs)), len(todo)))
    if todo:
        # group by S so each worker reuses S's spans (lru caches in ruler_v2)
        todo.sort(key=lambda p: (p[1], p[0]))
        chunks = [todo[i:i + 40] for i in range(0, len(todo), 40)]
        with ProcessPoolExecutor(NPROC, initializer=init) as ex:
            for k, r in enumerate(ex.map(_genuine_job, chunks)):
                cache.update(r)
                if k % 10 == 0:
                    cache_path.write_text(json.dumps(cache))
                    log("genuine %d/%d chunks" % (k + 1, len(chunks)))
    cache_path.write_text(json.dumps(cache))
    return cache


# ------------------------------------------------------------------ panel-schema membership
def comp_index(s, gen_cache, genuine_only):
    """body -> set of compositions of s it instantiates (non-trivial: not an instance
    of s itself; identity wraps excluded; optionally genuine only)."""
    own = set(T3D.instantiate(s))
    idw = {x.replace("{S}", s) for x in IDW}
    per = {}
    for w in a18.compositions(s):
        if w in idw:
            continue
        if genuine_only and not gen_cache.get("%s||%s" % (w, s)):
            continue
        for b in T3D.instantiate(w):
            if b not in own:
                per.setdefault(b, set()).add(w)
    return per


def hyp_ge2(Nm1, n, K):
    """P(>= 2 of K draws w/o replacement from Nm1 items contain one of n marked)."""
    if n < 2 or K < 2:
        return 0.0
    tot = math.comb(Nm1, K)
    p0 = math.comb(Nm1 - n, K) / tot
    p1 = n * math.comb(Nm1 - n, K - 1) / tot
    return 1 - p0 - p1


def xs(bodies, per, K=8):
    """share and exact COND_K (W1 definition, hypergeometric instead of MC)."""
    N = len(bodies)
    mem = [i for i, b in enumerate(bodies) if b in per]
    if not mem:
        return {"share": 0.0, "COND": 0.0, "members": 0}
    cnt = Counter()
    for b in bodies:
        for w in per.get(b, ()):
            cnt[w] += 1
    tot = 0.0
    for i in mem:
        ws = sorted(per[bodies[i]])
        tot += sum(hyp_ge2(N - 1, cnt[w] - 1, K) for w in ws) / len(ws)
    return {"share": round(len(mem) / N, 4), "COND": round(tot / len(mem), 4), "members": len(mem)}


# ------------------------------------------------------------------ PRISTINE window (W2 logic)
_SIG = None
# exact fallback body rank only when the expected rank is small enough to matter for
# escrows <= 250k (rank <= 543); above 3000 the rank's sd (~55) makes <= 543 impossible
# in practice and the rank is recorded as its expectation (declared approximation).
RB_EXACT_BELOW = 3000


def _cover_job(fams):
    import w2_coverage as W
    import w2_fallback as WF
    import fasteval as FE
    global _SIG
    if _SIG is None:
        _SIG = WF.sig_table()
    out = {}
    NG5, NF = len(G.BODY_SPACE), len(G.FINAL_SPACE)
    for name, init, body, final in fams:
        w = ("fold", init, body, final)
        gold = tuple(str(x) for x in W.outputs(w, W.PINFO))
        eq = W.consistent(W.PINFO, gold, "probe")
        seeds = [E.search_entropy("A19-pilot-PRISTINE/%s/%d" % (name, r)) for r in range(4)]
        rec = {"covered": bool(eq), "k_cov": len(eq)}
        if eq:
            rec["charges"] = [min(W.charge(p, sd) for p in eq) for sd in seeds]
        else:
            ifn, bfn, ffn = FE.fn(init), FE.fn(body), FE.fn(final)
            s = tuple(FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _ in WF.SIGP)
            wacc = [FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _ in W.PINFO]
            eqb = [G.BODY_SPACE[k] for k in _SIG[init].get(hash(s), [])
                   if all(FE._fold_acc(ifn, FE.fn(G.BODY_SPACE[k]), vals, fst, lst) == a
                          for (vals, fst, lst, _), a in zip(W.PINFO, wacc))]
            if body not in eqb:
                eqb.append(body)
            def sf(fn, a, vl, fst, lst):          # a failed fold (FE._FAIL) -> "FAIL"
                return "FAIL" if a is FE._FAIL else FE._final(fn, a, vl, fst, lst)
            wout = [sf(ffn, a, vl, fst, lst) for a, (vals, fst, lst, vl) in zip(wacc, W.PINFO)]
            eqf = [f for f in G.FINAL_SPACE if all(sf(FE.fn(f), a, vl, fst, lst) == o
                                                   for a, (vals, fst, lst, vl), o in zip(wacc, W.PINFO, wout))]
            iv = [FE.fn(init)(0, 0, fst, lst) for vals, fst, lst, _ in W.PINFO]
            eqi = [i for i in G.INIT_SPACE if all(WF._safe(FE.fn(i), fst, lst) == x
                                                   for (vals, fst, lst, _), x in zip(W.PINFO, iv))]
            ch, napprox = [], 0
            for sd in seeds:
                ik = sorted(WF.kval(sd, "g4init", i) for i in dict.fromkeys(G.INIT_SPACE))
                ri = min(bisect.bisect_left(ik, WF.kval(sd, "g4init", i)) for i in eqi)
                fk = sorted(WF.kval(sd, "g4final", f) for f in G.FINAL_SPACE)
                rf = min(bisect.bisect_left(fk, WF.kval(sd, "g4final", f)) for f in eqf)
                if ri > 0:
                    rb = None                      # >= one full init block (83.9M) away
                    ch.append(W.N_COV + NF + ri * NG5 * NF + rf + 1)   # lower bound
                else:
                    kstar = min(WF.kval(sd, "g4body", b) for b in eqb)
                    xr = int(kstar, 16) / 16 ** 64 * NG5          # expected rank
                    if xr > RB_EXACT_BELOW:
                        rb = int(round(xr))                        # approx (sd ~ sqrt(rank))
                        napprox += 1
                    else:
                        pre = hashlib.sha256(("APHRODITE/S2/ORDER/v1/%d/g4body/" % sd).encode())
                        rb = 0
                        for b in G.BODY_SPACE:
                            h = pre.copy()
                            h.update(b.encode())
                            if h.hexdigest() < kstar:
                                rb += 1
                    ch.append(W.N_COV + NF + rb * NF + rf + 1)
            rec.update({"k_body_G5": len(eqb), "k_init": len(eqi), "charges": ch, "n_rank_approx": napprox})
        out[name] = rec
    return out


# ------------------------------------------------------------------ main phases
def load(p):
    return json.loads((HERE / p).read_text())


def cmd_gen(n, jobs_s):
    out_p = HERE / os.environ.get("W8_SUPPLY_FILE", "W8_SUPPLIES.json")
    res = json.loads(out_p.read_text()) if out_p.exists() else {}
    jobs = []
    for spec in jobs_s:
        kind, rng_s = spec.split(":")
        a, b = (int(x) for x in rng_s.split("-")) if "-" in rng_s else (int(rng_s), int(rng_s))
        jobs += [(kind, s, n) for s in range(a, b + 1) if "%s:%d" % (kind, s) not in res]
    log("gen %d supplies" % len(jobs))
    with ProcessPoolExecutor(NPROC, initializer=init) as ex:
        for tag, r in ex.map(_gen_job, jobs):
            res[tag] = r
            out_p.write_text(json.dumps(res))
            log("%s %s" % (tag, r["stats"]))


def cmd_panel_candidates(n_draw=600):
    """Clean random schemas (a20_c3.clean), pre-filtered on raw non-trivial U-share."""
    import ruler_v2 as R
    import a20_c3 as B
    sup = load("W8_SUPPLIES.json")
    ubodies = [f[2] for t, r in sup.items() if t.startswith("U:") for f in r["families"]]
    sp, tsp = R.span_of_schema(a18.G1), R.traj_span(R.reexpression_bodies(a18.G1))
    rng = random.Random(I._seed("ARC3/W8/PANEL/v1"))
    g1raw = xs(ubodies, comp_index(a18.G1, {}, False))
    seen, cands = {a18.G1}, []
    for _ in range(n_draw):
        s = a18._random_schema(rng)
        if not s or s in seen:
            continue
        seen.add(s)
        if not B.clean(s, sp, tsp):
            continue
        raw = xs(ubodies, comp_index(s, {}, False))
        cands.append((s, raw))
    log("panel: %d clean candidates; G1 raw %s" % (len(cands), g1raw))
    return cands, g1raw


def cmd_genuine_and_panel():
    sup = load("W8_SUPPLIES.json")
    pairs = set()
    for r in sup.values():
        for f in r["families"]:
            for k, dec in schemas(f[2]).items():
                if dec:
                    pairs.add(tuple(dec))
    cands, g1raw = cmd_panel_candidates()
    # keep candidates whose RAW U-share >= 0.25x G1 raw share (genuine share <= raw share)
    keep = [(s, raw) for s, raw in cands if raw["share"] >= 0.25 * g1raw["share"]]
    log("panel: %d candidates survive raw pre-filter" % len(keep))
    for s in [a18.G1] + [s for s, _ in keep]:
        for w in a18.compositions(s):
            pairs.add((w, s))
    cache = run_genuine(sorted(pairs), HERE / "W8_GENUINE_CACHE.json")
    ubodies = [f[2] for t, r in sup.items() if t.startswith("U:") for f in r["families"]]
    g1 = xs(ubodies, comp_index(a18.G1, cache, True))
    rows = []
    for s, raw in keep:
        x = xs(ubodies, comp_index(s, cache, True))
        rs = x["share"] / g1["share"] if g1["share"] else float("nan")
        rc = x["COND"] / g1["COND"] if g1["COND"] else float("nan")
        rows.append({"schema": s, "U_raw": raw, "U_genuine": x, "ratio_share": round(rs, 3),
                     "ratio_COND": round(rc, 3),
                     "matched": bool(0.5 <= rs <= 1.5 and 0.5 <= rc <= 1.5)})
    rows.sort(key=lambda r: -r["U_genuine"]["share"])
    (HERE / "W8_PANEL.json").write_text(json.dumps({"G1_U_genuine": g1, "G1_U_raw": g1raw, "n_clean_candidates": len(cands),
                                                    "candidates": rows}, indent=1))
    log("panel: G1 %s; matched %d" % (g1, sum(r["matched"] for r in rows)))


def cmd_cover():
    sup = load("W8_SUPPLIES.json")
    out_p = HERE / "W8_COVER.json"
    res = json.loads(out_p.read_text()) if out_p.exists() else {}
    fams = [f for r in sup.values() for f in r["families"] if f[0] not in res]
    chunks = [fams[i:i + 24] for i in range(0, len(fams), 24)]
    log("cover: %d families, %d chunks" % (len(fams), len(chunks)))
    with ProcessPoolExecutor(NPROC, initializer=init) as ex:
        for k, r in enumerate(ex.map(_cover_job, chunks)):
            res.update(r)
            if k % 5 == 0:
                out_p.write_text(json.dumps(res))
                log("cover %d/%d" % (k + 1, len(chunks)))
    out_p.write_text(json.dumps(res))


if __name__ == "__main__":
    init()
    c = sys.argv[1]
    if c == "gen":
        cmd_gen(int(sys.argv[2]), sys.argv[3:])
    elif c == "genuine":
        cmd_genuine_and_panel()
    elif c == "cover":
        cmd_cover()
    else:
        raise SystemExit("unknown " + c)
