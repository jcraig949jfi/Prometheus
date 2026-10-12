"""C-018-T030 Aether evidence adapter: records paired native executions; never implements Aether's physics.

Every world step is Aether's own code, imported read-only from the pinned tree (`Aether/` last changed at 383bb3584):
  native worlds    Aether/V2B/PROP01/prop01_run.py:78 law_step (V1 = aeth01.v1, RX = aeth03.mob_r1x1e0)
  attribution      prop01_run.py:119 run_unit (the engine-side ATTRIBUTED tree), prop01_tree.py:12 choose_cut (B)
  fixture worlds   rso/aether/demand/fixtures.py:64 step -> Aether/V2B/REACH01/R1/r1_test4.py:76 law_step (Cadmus, C-018-T020)
  content features r1_test4.py:131 features; decoder r1_reduce.py:35 decode (in evaluate.py)
What is new here is OBSERVATION only: lockstep CONTROL / IMPULSE / CUT_B / CUT_N worlds, the clamp (prop01_run.py:220-223
semantics: the clamped site's five fields := CONTROL's, every tick), per-site first-divergence ticks, digests, and the
non-ancestor rule. The record is (meta JSON, arrays NPZ); `arrays_sha256` binds them. The evaluator (evaluate.py) re-derives
every verdict from the arrays and the engine's tree; it never reads a producer verdict.
"""
import hashlib
import json
import os

import numpy as np

from rso.aether.demand import fixtures as F    # sets sys.path to the pinned Aether tree (fixtures.py:11-18)
import prop01_run as P                         # noqa: E402  (Aether, unmodified)
import prop01_tree as TR                       # noqa: E402  (Aether, unmodified)

ADAPTER = "rso.aether.adapter 1.0.0"
_, K = P.load_backend("cpu")
# NEW seed range, disjoint from Cadmus's 0xC18A..0xC18E and every Aether range (0xE2010000, 0xE2011000, 0x1A9F; grep'd)
SEEDS = {"rng": 0xC30A0000, "phys": 0xC30B0000, "imp": 0xC30E0000, "graded": 0xC30C0000}
DEV_K = range(0, 16)                           # development / qualification seed indices; confirmatory k >= 0x1000 (confirm.py)
FIX_ORIGIN = (24, 10)                          # Cadmus's fixture origin (fixtures.py:92)
WORLDS = ("impulse", "cutB", "cutN")
TS = (25, 50, 100, 200)                        # Aether's feature ticks (r1_test4.py:51)


def arrays_sha256(a):
    h = hashlib.sha256()
    for k in sorted(a):
        v = np.ascontiguousarray(a[k])
        h.update(("%s|%s|%s|" % (k, v.dtype.str, v.shape)).encode())
        h.update(v.tobytes())
    return h.hexdigest()


def cheb(n, a, b):
    ay, ax = divmod(int(a), n)
    by, bx = divmod(int(b), n)
    dy, dx = abs(ay - by), abs(ax - bx)
    return max(min(dy, n - dy), min(dx, n - dx))


def choose_nonancestor(tree, B, O, n):
    """N for the non-ancestor clamp: an ATTRIBUTED site (generation >= 1) outside B's subtree and B's ancestry, i.e. by the
    engine's own attribution an ancestor of none of B's descendants; divergent by construction (it is in the tree), so its
    clamp is a real intervention, never the identity. Matched to B: min |cheb(N,O) - cheb(B,O)|, then earliest first
    divergence, then lowest index. None if no such site exists."""
    par = dict(zip(tree["site"], tree["parent"]))
    desc = TR.descendants(tree, B)
    anc, p = set(), par.get(B, -1)
    while p is not None and p >= 0:
        anc.add(p)
        p = par.get(p)
    dB = cheb(n, B, O)
    cands = [(abs(cheb(n, s, O) - dB), t, s) for s, g, t in zip(tree["site"], tree["gen"], tree["ftick"])
             if g >= 1 and s != B and s != O and s not in desc and s not in anc]
    return min(cands)[2] if cands else None


def pair_run(step, control, impulse, horizon, clamps, keep=()):
    """Lockstep worlds from tick 1..horizon. clamps = {world: flat site or None}. Returns per-world first-divergence ticks
    vs CONTROL (int16, -1 never; 0 = differs at t0), final digests, and CONTROL states at `keep` ticks."""
    n = control[0].shape[0]
    c = [f.copy() for f in control]
    ws = {w: [f.copy() for f in impulse] for w in ("impulse",) + tuple(clamps)}
    t0 = F.diff_mask(impulse, control).ravel()
    ft = {w: np.where(t0, 0, -1).astype(np.int16) for w in ws}
    kept = {}
    for t in range(1, horizon + 1):
        nc = step(c, t)
        for w in ws:
            nx = step(ws[w], t)
            site = clamps.get(w)
            if site is not None:
                y, x = divmod(int(site), n)
                for f in range(5):
                    nx[f][y, x] = nc[f][y, x]
            m = F.diff_mask(nx, nc).ravel() & (ft[w] < 0)
            ft[w][m] = t
            ws[w] = nx
        c = nc
        if t in keep:
            kept[t] = [f.copy() for f in c]
    return ft, {w: P.digest(s) for w, s in dict(ws, control=c).items()}, kept


def fixture_unit(kind, seedk, B=None, N=None, law="V1", n=48, horizon=100, label=3):
    """Cadmus's planted fixtures (fixtures.py:39 plant; seeds as the demand gate, phys 0xC18B0000 + k) through this recorder.
    Recipe-chosen sites: B = origin+(0,2), N = origin+(0,6) (downstream terminal: an ancestor of none of the targets),
    targets = origin+(0,3..5). Override B / N with (y, x) to build the near-misses."""
    y0, x0 = FIX_ORIGIN
    base, pl = F.blank(n), F.blank(n)
    F.plant(base, kind, y0, x0, n, None, seedk)
    F.plant(pl, kind, y0, x0, n, label, seedk, branch=label)
    flat = lambda yx: (yx[0] % n) * n + yx[1] % n      # noqa: E731
    Bs, Ns = flat(B or (y0, x0 + 2)), flat(N or (y0, x0 + 6))
    phys = F.PHYS + seedk
    ft, dig, _ = pair_run(lambda s, t: F.step(s, t, phys, law), base, pl, horizon, {"cutB": Bs, "cutN": Ns})
    meta = {"schema": "prometheus.rso.aether.unit.v1", "adapter": ADAPTER, "kind": "fixture", "fixture": kind, "law": law,
            "seed": seedk, "phys": hex(phys), "n": n, "H": horizon, "origin": flat((y0, x0)), "B": Bs, "N": Ns,
            "targets": [flat((y0, x0 + k)) for k in (3, 4, 5)], "digests": dig}
    arrays = {"snap": np.stack(base), "imp": np.stack(pl), "ftick_impulse": ft["impulse"], "ftick_cutB": ft["cutB"],
              "ftick_cutN": ft["cutN"]}
    return meta, arrays


class _Seeds:
    """Point Aether's module-level seed bases at this adapter's range for one call (no file is edited)."""
    def __enter__(self):
        self.old = (P.RNG_SEED_BASE, P.PHYS_SEED_BASE, P.IMPULSE_DOMAIN)
        P.RNG_SEED_BASE, P.PHYS_SEED_BASE, P.IMPULSE_DOMAIN = SEEDS["rng"], SEEDS["phys"], SEEDS["imp"]

    def __exit__(self, *a):
        P.RNG_SEED_BASE, P.PHYS_SEED_BASE, P.IMPULSE_DOMAIN = self.old


def native_unit(law, k, n=128, warm=300, H=400, obs=200, ts=TS):
    """One native paired unit. (1) Aether's run_unit: the ATTRIBUTED tree. (2) B = Aether's choose_cut; N = the
    non-ancestor rule. (3) This recorder: CONTROL / IMPULSE (bit 0 of the origin payload, as prop01_run.py:135) / CUT_B /
    CUT_N in lockstep. (4) Content, Aether's r1 decodability design on the same snapshot: 8 branches with payload := V[j]
    at every r1 grid origin (16 at 128^2; one origin per world was too few to train the decoder at a 0.05 margin,
    qual/QUALIFICATION_v1_48origins.json), Aether's features vs CONTROL at `ts`. The warm-up is recomputed here and must reproduce Aether's warm digest."""
    with _Seeds():
        u = P.run_unit("cpu", law, k, n, warm, H)
        f0, _ = P.R.build_initial(P.R.SPARSE_SOUP, n, n, P.RNG_SEED_BASE + k, write_density=P.DENSITY,
                                  energy_mode=P.R.ENERGY_UNIFORM)
        phys = P.PHYS_SEED_BASE + k
        s = [np.asarray(f).copy() for f in f0]
        for t in range(warm):
            s, _ = P.law_step(np, K, law, n, phys, t + 1, s)
        O = P.pick_origin(np, K, s, k)
    if P.digest(s) != u["warm_digest"] or O != u["origin"]:
        raise RuntimeError("recorder warm-up does not reproduce Aether's run_unit (law %s k %d)" % (law, k))
    B, bt = TR.choose_cut(u)
    Nn = choose_nonancestor(u["tree"], B, O, n) if B is not None else None
    oy, ox = divmod(O, n)
    imp = [f.copy() for f in s]
    imp[3][oy, ox] ^= np.uint8(1)

    def step(w, t):
        return P.law_step(np, K, law, n, phys, warm + t, w)[0]
    clamps = {"cutB": B, "cutN": Nn} if B is not None else {}
    ft, dig, kept = pair_run(step, s, imp, H, clamps, keep=set(ts))
    for w in ("cutB", "cutN"):
        ft.setdefault(w, np.full(n * n, -1, np.int16))
    org = F.T.choose_origins(s, K, n)                  # Aether's r1 origin grid (r1_test4.py:108), 16 at 128^2
    ys, xs = [o[0] for o in org], [o[1] for o in org]
    Hs = np.zeros((8, len(org), len(ts), 6, 4, 256), np.uint8)
    Ds = np.zeros((8, len(org), len(ts), 6), np.float32)
    for j in range(8):
        w = [f.copy() for f in s]
        w[3][ys, xs] = np.uint8(F.T.V[j])              # r1_test4.py:200: payload := V[j] at EVERY origin
        for t in range(1, obs + 1):
            w = step(w, t)
            if t in ts:
                h, d = F.T.features(np, w, kept[t], ys, xs, n)
                Hs[j, :, ts.index(t)], Ds[j, :, ts.index(t)] = h, d
    meta = {"schema": "prometheus.rso.aether.unit.v1", "adapter": ADAPTER, "kind": "native", "law": law,
            "semantics_id": P.LAWS[law], "seed": k, "seeds": {x: hex(v) for x, v in SEEDS.items()}, "n": n, "warm": warm,
            "H": H, "obs": obs, "ts": list(ts), "V": list(F.T.V), "origin": O, "content_origins": [list(o) for o in org], "B": B, "B_tick": bt, "N": Nn,
            "tree": u["tree"], "aether": {k_: u[k_] for k_ in ("runner", "table_hash", "warm_digest", "final_digest_control",
                                                               "final_digest_impulse", "extinct_tick", "ever_sites",
                                                               "max_gen", "unknown_sites")},
            "digests": dig}
    arrays = {"snap": np.stack(s), "imp": np.stack(imp), "ftick_impulse": ft["impulse"], "ftick_cutB": ft["cutB"],
              "ftick_cutN": ft["cutN"], "H": Hs, "D": Ds}
    return meta, arrays


def graded_labels(seedk, n_origins, p):
    """Label written at origin i of branch j: j with probability p, else uniform over the 8 labels (independent of j).
    Common random numbers across p, so the set of faithful (i, j) only grows with p. Expected excess over chance 7p/8."""
    rng = np.random.default_rng([SEEDS["graded"], seedk])
    r = rng.random((8, n_origins))
    u = rng.integers(0, 8, (8, n_origins))
    return np.where(r < p, np.arange(8)[:, None], u)


GRADED_ORIGINS = [(8 + 16 * i, 2 + 16 * j) for i in range(6) for j in range(6)]    # Cadmus's 36-origin grid (fixtures.py:144)


def graded_unit(seedk, p, n=96, obs=100, ts=(25, 50, 100)):
    """Graded-content relay (SELECTION.md s4 limit (i)): fixture A at 36 origins; branch j writes label graded_labels[j, i].
    v1 used 12 origins x 4 seeds (48) and failed the sensitivity criterion; v2 uses 36 x 20 seeds (720), matched to the
    native RX design (48 worlds x 16 origins = 768)."""
    L = graded_labels(seedk, len(GRADED_ORIGINS), p)
    phys = SEEDS["graded"] + seedk
    ys, xs = [o[0] for o in GRADED_ORIGINS], [o[1] for o in GRADED_ORIGINS]

    def world(j):
        s = F.blank(n)
        for i, (y, x) in enumerate(GRADED_ORIGINS):
            F.plant(s, "A", y, x, n, None if j is None else int(L[j, i]), seedk)
        return s
    b, base = world(None), {}
    for t in range(1, obs + 1):
        b = F.step(b, t, phys)
        if t in ts:
            base[t] = [f.copy() for f in b]
    Hs = np.zeros((8, len(GRADED_ORIGINS), len(ts), 6, 4, 256), np.uint8)
    Ds = np.zeros((8, len(GRADED_ORIGINS), len(ts), 6), np.float32)
    for j in range(8):
        w = world(j)
        for t in range(1, obs + 1):
            w = F.step(w, t, phys)
            if t in ts:
                Hs[j, :, ts.index(t)], Ds[j, :, ts.index(t)] = F.T.features(np, w, base[t], ys, xs, n)
    return {"kind": "graded", "seed": seedk, "p": p, "labels_sha256": hashlib.sha256(L.astype(np.int64).tobytes()).hexdigest()}, \
        {"H": Hs, "D": Ds}


def save_unit(path, meta, arrays):
    """path without extension: writes <path>.npz and <path>.json (meta carries arrays_sha256)."""
    np.savez_compressed(path + ".npz", **arrays)
    meta = dict(meta, arrays_sha256=arrays_sha256(arrays))
    with open(path + ".json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, sort_keys=True, separators=(",", ":"))
    return meta


def load_unit(path):
    with open(path + ".json", encoding="utf-8") as f:
        meta = json.load(f)
    with np.load(path + ".npz") as z:
        arrays = {k: z[k] for k in z.files}
    return meta, arrays


def unit_path(d, meta):
    return os.path.join(d, "%s_%s_%s" % (meta["kind"], meta.get("fixture", meta["law"]), meta["seed"]))
