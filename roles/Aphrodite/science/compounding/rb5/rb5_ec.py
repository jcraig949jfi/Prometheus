"""RB-5 part (a): the EC 2013 polynomial ladder -> fold tasks (forensic, not a
disposition).

Task world (Dechter et al. 2013, Sec. 4.1): f(x) = a x^2 + b x + c, a, b, c in
0..9 (1000 polynomials). Tiers: CONST (a=b=0), LINEAR (a=0, b>0), QUAD (a>0);
EC's ablation subsets QUAD_COMPLEX (a, b, c > 0) and QUAD_COEF_GT1 (a, b, c > 1).

Mappings into the fold task shape (list xs, query m -> integer), all on the
Aphrodite input distribution (values 2..30, query 1..97):
  SUM       sum_{v in xs} f(v)                 G1-SHAPED BY CONSTRUCTION (acc + f(v))
  FSUM      f(sum xs)                          G1 body, polynomial in the final
  PRODMOD   (prod_{v in xs} f(v)) mod m        multiplicative reduce, bounded by m
  ORBIT     x0 = 0, x_{t+1} = f(x_t) + v_t     the polynomial as a DRIVEN MAP
  ORBITMOD  x0 = 0, x_{t+1} = (f(x_t) + v_t) mod m
  POINT     f(m)                               control: the list is ignored
Usage: python rb5_ec.py g4|g5
"""
import json
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rb5_common as C      # noqa: E402

MAPPINGS = ["SUM", "FSUM", "PRODMOD", "ORBIT", "ORBITMOD", "POINT"]
COEF = range(10)


def tiers(a, b, c):
    t = ["CONST" if a == b == 0 else ("LINEAR" if a == 0 else "QUAD")]
    if a > 0 and b > 0 and c > 0:
        t.append("QUAD_COMPLEX")
    if a > 1 and b > 1 and c > 1:
        t.append("QUAD_COEF_GT1")
    return t


def gold(mapping, a, b, c, nums):
    xs, m = nums[:-1], nums[-1]

    def f(x):
        return a * x * x + b * x + c

    def ok(x):
        return None if x is None or abs(x) > C.CEIL else x
    if mapping == "SUM":
        return ok(sum(f(v) for v in xs))
    if mapping == "FSUM":
        return ok(f(sum(xs)))
    if mapping == "POINT":
        return ok(f(m))
    if mapping == "PRODMOD":
        acc = 1
        for v in xs:
            acc = (acc * f(v)) % m
        return acc
    acc = 0
    for v in xs:
        acc = f(acc) + v
        if mapping == "ORBITMOD":
            acc %= m
        if abs(acc) > C.CEIL:
            return None
    return acc


def families():
    return [(mp, a, b, c) for mp in MAPPINGS for a in COEF for b in COEF for c in COEF]


def fid(fam):
    return "%s|%d|%d|%d" % fam


def dev_set():
    rng = random.Random(C.LABEL + "/EC/dev")
    out = [[rng.randint(2, 30) for _ in range(6)] + [rng.randint(3, 97)]]
    for L in (4, 5, 7, 8, 9, 9, 5):
        out.append([rng.randint(2, 30) for _ in range(L)] + [rng.randint(3, 97)])
    return out


def holdout_set():
    rng = random.Random(C.LABEL + "/EC/holdout")
    return [[rng.randint(2, 30) for _ in range(rng.randint(2, 60))] + [rng.randint(1, 97)]
            for _ in range(60)]


def job(args):
    grammar, lo, hi = args
    bodies = C.a17.g5_bodies() if grammar == "g5" else C.G.BODY_SPACE
    bodies = bodies[lo:hi]
    if grammar == "g5":                       # G5 = G4 bodies + depth-3 extras; only extras here
        g4 = set(C.G.BODY_SPACE)
        bodies = [b for b in bodies if b not in g4]
    dev = dev_set()
    targets = {fid(fm): tuple(gold(*fm, n) for n in dev) for fm in families()}
    t = time.time()
    inits = C.G.H1_SPACE if grammar == "g5" else None     # G5 catalog convention: H1 inits
    h = C.search(dev, targets, bodies, inits=inits, cap=40, per_body=40,
                 expr=(lo == 0 and grammar == "g4"))
    return h, time.time() - t, len(bodies)


def main(grammar):
    C.worker_init()
    n = len(C.a17.g5_bodies() if grammar == "g5" else C.G.BODY_SPACE)
    k = 24 if grammar == "g5" else 6
    cuts = [(grammar, n * j // k, n * (j + 1) // k) for j in range(k)]
    hits, secs = {}, 0.0
    with ProcessPoolExecutor(max_workers=C.WORKERS, initializer=C.worker_init) as ex:
        for h, s, nb in ex.map(job, cuts):          # ordered merge = enumeration order
            secs += s
            for f, ps in h.items():
                lst = hits.setdefault(f, [])
                lst.extend(ps[: 40 - len(lst)])
            print("chunk done", nb, "bodies", round(s, 1), "s", flush=True)
    hold = holdout_set()
    out = {}
    for fm in families():
        f = fid(fm)
        ps = hits.get(f, [])
        hg = [(n, gold(*fm, n)) for n in hold]
        ver = [list(p) for p in ps if C.verify(p, hg)]
        out[f] = {"dev_hits": len(ps), "verified": ver}
    (HERE / ("EC_SEARCH_%s.json" % grammar.upper())).write_text(
        json.dumps({"grammar": grammar, "search_seconds": round(secs, 1), "families": out}),
        encoding="utf-8")
    print("expressible (verified):", sum(1 for v in out.values() if v["verified"]), "/", len(out))


if __name__ == "__main__":
    main(sys.argv[1])
