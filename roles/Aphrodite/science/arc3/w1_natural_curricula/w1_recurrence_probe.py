"""W1 -- natural-curriculum recurrence probe (FORENSIC, NOT A DISPOSITION).

Question: under a less constructed task generator (one that never names G1 or any
specific abstraction), does composed one-hole schema structure RECUR across
families more than under the current uniform W5 sampler (A19 NAT rule) and more
than under a structure-shuffled (i.i.d.-marginal) twin?

No donor runs. Only the task side is measured (T4 family_profile admissibility,
ruler v2 accumulating), exactly as the A19 NAT supply rule, so the recurrence
statistic is fixed BEFORE any donor could see the supply.

Generators (each emits (init, body, final) with init in H1, final uniform among
acc-finals; kept iff accumulating and T4-admissible -- the A19 NAT screen):
  U      A19 NAT rule: uniform over the W5 body list.
  PCFG   i.i.d. draws from a W5-shaped PCFG (base of AG/FG; their shuffled twin).
  AG     adaptor grammar (Johnson et al.): the inner depth-2 subterm (E2) and the
         whole body (E3) are Pitman-Yor adapted over ACCEPTED families.
  FG     fragment grammar (O'Donnell): accepted bodies are cached as fragments with
         each leaf slot left open w.p. 1/2; reuse re-draws open slots from the base.
  LIN    lineage (POET/ACCEL-style edit chain, solver-free): each proposal is one
         random edit of a uniformly chosen archived (accepted) family.
  STAR   LIN's twin: one random edit of a FRESH PCFG draw (same edit law, no shared
         ancestry).
Labels "W1-...". Usage: python w1_recurrence_probe.py <n_fam> <gen:seed,...>
"""
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

os.environ["A17_FASTEVAL"] = "1"
HERE = Path(__file__).resolve().parent
ENG = HERE.parents[2] / "engine"
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(ENG.parent / "science" / "compounding" / "rb1"))
import a17  # noqa: E402
import a18  # noqa: E402
from a18 import G, T3D, I  # noqa: E402
import engine as E  # noqa: E402
import fair as FR  # noqa: E402

a17.worker_init()
a18.use_world("W5")
import tribunal_t4 as T4  # noqa: E402
import ruler_v2 as R  # noqa: E402

OPS = [tmpl for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())]
ATOMS = list(G.BODY_ATOMS)
FINALS = [f for f in G.FINAL_SPACE if "acc" in f]
PANEL = {"G1": "(acc + {H})", "SHAM_0": "(v - (acc - {H}))", "SHAM_1": "({H} + v)",
         "OFF_0": "(1 + (v - {H}))"}          # the frozen A19 panel
COMM = ("add", "mul", "gcd")
L1KEYS = None


def log(m):
    print("[W1 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


# ------------------------------------------------------------------ base PCFG (W5-shaped)
def e1(rng):
    if rng.random() < 0.5:
        return rng.choice(ATOMS)
    return rng.choice(OPS).format(rng.choice(ATOMS), rng.choice(ATOMS))


def e2(rng, a=None, b=None):
    return rng.choice(OPS).format(a or e1(rng), b or e1(rng))


def e3(rng, inner=None):
    return rng.choice(OPS).format(rng.choice(ATOMS), inner or e2(rng))


def top(rng, e2f, e3f):
    return e3f() if rng.random() < 0.95 else e2f()


# ------------------------------------------------------------------ Pitman-Yor restaurant
class PY:
    def __init__(self, d=0.5, a=1.0):
        self.d, self.a, self.tables, self.n = d, a, [], 0

    def draw(self, rng, base):
        """Returns (value, table_index or None). Counts are added by seat()."""
        K = len(self.tables)
        u = rng.random() * (self.n + self.a)
        if u < self.a + self.d * K or not K:
            return base(), None
        u -= self.a + self.d * K
        for k, (val, c) in enumerate(self.tables):
            u -= c - self.d
            if u <= 0:
                return val, k
        return self.tables[-1][0], K - 1

    def seat(self, val, k):
        if k is None:
            self.tables.append([val, 1])
        else:
            self.tables[k][1] += 1
        self.n += 1


# ------------------------------------------------------------------ generators
class Gen:
    """propose() -> (body_src, token); accept(token) called only for kept families."""
    def __init__(self, kind, rng):
        self.kind, self.rng = kind, rng
        a = 10.0 if kind.endswith("W") else 1.0
        self.py2, self.py3 = PY(a=a), PY(a=a)
        self.fg = PY(a=a)
        self.archive = []

    def propose(self):
        rng, k = self.rng, self.kind
        if k == "U":
            return rng.choice(G.BODY_SPACE), None
        if k == "PCFG":
            return top(rng, lambda: e2(rng), lambda: e3(rng)), None
        if k in ("AG", "AG2", "AG2W"):
            tok = {}

            def ad_e2():
                v, t = self.py2.draw(rng, lambda: e2(rng))
                tok["e2"] = (v, t)
                return v

            def ad_e3():
                v, t = self.py3.draw(rng, lambda: e3(rng, ad_e2()))
                tok["e3"] = (v, t)
                return v
            return top(rng, ad_e2, (ad_e3 if k == "AG" else (lambda: e3(rng, ad_e2())))), tok
        if k in ("FG", "FGW"):
            if rng.random() < 0.05:
                return e2(rng), None
            K = len(self.fg.tables)
            u = rng.random() * (self.fg.n + self.fg.a)
            if not K or u < self.fg.a + self.fg.d * K:
                full = (rng.choice(OPS), rng.choice(ATOMS), rng.choice(OPS), e1(rng), e1(rng))
                frag = tuple(v if (j in (0, 2) or rng.random() < 0.5) else None for j, v in enumerate(full))
                t = None
            else:
                t = self._pick_fg(rng)
                frag = self.fg.tables[t][0]
                full = (frag[0], frag[1] or rng.choice(ATOMS), frag[2], frag[3] or e1(rng), frag[4] or e1(rng))
            op_o, a, op_i, x, y = full
            return op_o.format(a, op_i.format(x, y)), ("fg", frag, t)
        if k in ("LIN", "STAR"):
            if k == "LIN" and len(self.archive) >= 8:
                parent = rng.choice(self.archive)
            elif k == "LIN":
                return top(rng, lambda: e2(rng), lambda: e3(rng)), None   # founders
            else:
                parent = top(rng, lambda: e2(rng), lambda: e3(rng))
            return mutate(rng, parent), None
        raise ValueError(k)

    def _pick_fg(self, rng):
        u = rng.random() * (self.fg.n - self.fg.d * len(self.fg.tables))
        for k, (_val, c) in enumerate(self.fg.tables):
            u -= c - self.fg.d
            if u <= 0:
                return k
        return len(self.fg.tables) - 1

    def accept(self, body, tok):
        if self.kind.startswith("AG") and tok:
            if "e2" in tok:
                self.py2.seat(*tok["e2"])
            if "e3" in tok:
                self.py3.seat(*tok["e3"])
        if self.kind.startswith("FG") and tok:
            _, frag, t = tok
            self.fg.seat(frag, t)
        if self.kind == "LIN":
            self.archive.append(body)


def mutate(rng, src):
    """One random edit: replace a random subterm (non-root) of depth <= 1 by a fresh
    E1, or change the operator of a random internal node."""
    t = I.parse(src)
    nodes = []

    def walk(x, p):
        nodes.append(p)
        for i, c in enumerate(x[1]):
            walk(c, p + (i,))
    walk(t, ())
    p = rng.choice(nodes)

    def get(x, p):
        return x if not p else get(x[1][p[0]], p[1:])

    def put(x, p, y):
        if not p:
            return y
        op, args = x
        args = list(args)
        args[p[0]] = put(args[p[0]], p[1:], y)
        return (op, args)
    sub = get(t, p)
    if sub[1] and rng.random() < 0.5:
        new = (rng.choice([o for o in ("add", "sub", "mul", "fdiv", "mod", "gcd", "powr") if o != sub[0]]), sub[1])
    else:
        new = I.parse(e1(rng))
    return I.to_src(put(t, p, new)) if p else I.to_src(new)


# ------------------------------------------------------------------ recurrence measures
def l1keys():
    global L1KEYS
    if L1KEYS is None:
        L1KEYS = {key(I.normalise(I.parse(x))) for x in FR.LEVEL1}
    return L1KEYS


def key(t):
    op, args = t
    if not args:
        return op
    ks = [key(a) for a in args]
    if op in COMM:
        ks = sorted(ks)
    return "%s(%s)" % (op, ",".join(ks))


def nops(t):
    return 0 if (not t[1] or t[0] == "HOLE") else 1 + sum(nops(a) for a in t[1])


def schemas(body):
    """Composed one-hole schemas of a canonical body: hole at a non-root subterm
    that is a LEVEL1 expression (the donor's filler space), >= 2 operator nodes
    outside the hole."""
    t = I.normalise(I.parse(body))
    out = set()

    def walk(x, p):
        for i, c in enumerate(x[1]):
            q = p + (i,)
            if key(c) in l1keys():
                s = put(t, q)
                if nops(s) >= 2:
                    out.add(key(s))
            walk(c, q)

    def put(x, p):
        if not p:
            return ("HOLE", [])
        op, args = x
        args = list(args)
        args[p[0]] = put(args[p[0]], p[1:])
        return (op, args)
    walk(t, ())
    return out


def panel_index():
    idx = {}
    for name, s in PANEL.items():
        per = {}
        for w in a18.compositions(s):
            for b in T3D.instantiate(w):
                per.setdefault(b, set()).add(w)
        idx[name] = per
    return idx


def measure(fams, pidx, rng, n_rep=400):
    bodies = [f[1] for f in fams]
    sch = [schemas(b) for b in bodies]
    cnt = Counter(s for ss in sch for s in ss)
    N = len(fams)
    r3 = sum(any(cnt[s] >= 3 for s in ss) for ss in sch) / N
    # the same, after collapsing identical bodies (duplicate bodies = trivial recurrence)
    ub = sorted(set(bodies))
    usch = [schemas(b) for b in ub]
    ucnt = Counter(s for ss in usch for s in ss)
    r3u = sum(any(ucnt[s] >= 3 for s in ss) for ss in usch) / max(1, len(ub))
    # donor-shaped reuse opportunity: 4 VALIDATE + 8 TRANSFER at random
    hit = 0
    for _ in range(n_rep):
        pick = rng.sample(range(N), 12)
        val, tr = pick[:4], pick[4:]
        vs = set().union(*[sch[i] for i in val])
        tc = Counter(s for i in tr for s in sch[i])
        hit += any(tc[s] >= 2 for s in vs)
    pan = {}
    for name, per in pidx.items():
        members = [b for b in bodies if b in per]
        wc = Counter(w for b in members for w in per[b])
        pan[name] = {"share": round(len(members) / N, 4), "distinct_compositions": len(wc),
                     "max_one_composition": max(wc.values()) if wc else 0}
    top = cnt.most_common(5)
    return {"N": N, "distinct_bodies": len(ub), "dup_body_share": round(1 - len(ub) / N, 4),
            "R3": round(r3, 4), "R3_unique_bodies": round(r3u, 4), "P_reuse": round(hit / n_rep, 4),
            "n_schemas": len(cnt), "n_schemas_ge3": sum(c >= 3 for c in cnt.values()),
            "top5": top, "panel": pan}


# ------------------------------------------------------------------ supply
def supply(kind, seed, n_fam, max_prop=60000):
    rng = random.Random(I._seed("W1/SUPPLY/%s/%d" % (kind, seed)))
    gen = Gen(kind, rng)
    fams, prop, acc_n, t0 = [], 0, 0, time.time()
    while len(fams) < n_fam and prop < max_prop:
        prop += 1
        src, tok = gen.propose()
        b = T3D.in_space_body(src)
        if b is None or not R.accumulating(b):
            continue
        acc_n += 1
        p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(FINALS))
        if not T4.family_profile(p)["admissible"]:
            continue
        fams.append(p[1:])
        gen.accept(b, tok)
        # lineage: keep the canonical accepted body as the archived parent
    return fams, {"proposals": prop, "accumulating": acc_n, "admitted": len(fams),
                  "seconds": round(time.time() - t0, 1)}


def main():
    n_fam = int(sys.argv[1])
    jobs = [(j.split(":")[0], int(j.split(":")[1])) for j in sys.argv[2].split(",")]
    out_path = HERE / ("W1_RECURRENCE_%s.json" % (sys.argv[3] if len(sys.argv) > 3 else "probe"))
    res = json.loads(out_path.read_text()) if out_path.exists() else {}
    T3D.in_space_body("(acc + v)")
    pidx = panel_index()
    log("index ready; panel instance sets %s" % {k: len(v) for k, v in pidx.items()})
    for kind, seed in jobs:
        tag = "%s:%d" % (kind, seed)
        if tag in res:
            continue
        fams, st = supply(kind, seed, n_fam)
        m = measure(fams, pidx, random.Random(I._seed("W1/MEASURE/" + tag)))
        res[tag] = {"stats": st, "measure": m, "families": fams}
        out_path.write_text(json.dumps(res, indent=1))
        log("%s %s R3=%.3f R3u=%.3f Preuse=%.3f dup=%.3f G1=%s" % (
            tag, st, m["R3"], m["R3_unique_bodies"], m["P_reuse"], m["dup_body_share"], m["panel"]["G1"]))


if __name__ == "__main__":
    main()
