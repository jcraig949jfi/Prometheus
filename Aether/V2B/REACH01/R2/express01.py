"""REACH01 R2 / EXPRESS01: minimum physics for composition (planted expressibility; NOT discovery).

PHYSICS FAMILY aeth01.op_<OP>: aeth01.v1 unchanged except that a winning write into a TEMPLATE field (opcode, arg0,
arg1, payload) stores OP(existing, incoming) instead of incoming. The energy field is unchanged. P0. One semantics id
per OP:
  REPLACE  incoming                                       (= aeth01.v1; historical control)
  XOR      existing ^ incoming                            combination
  ADD      (existing + incoming) & 0xFF                   accumulation
  AND      existing & incoming                            conditional combination
  SPLICE   (existing & 0xF0) | (incoming & 0x0F)          ALIEN: asymmetric part-state/part-input splice
  ROTX     rotl8(existing, incoming & 7) ^ incoming       ALIEN: input-keyed state rotation, then mixing
Implemented as a wrapper: the frozen kernel commits `incoming` (P0: no mutation), its observer says which (site, field)
received a winning write, and the wrapper replaces the stored byte with OP(pre-tick byte, committed byte).

PLANTED GADGETS run in the ECONOMICS.md "execution-only" regime (write cost 1, maintenance 0, no rain): a writer with
energy 1 fires exactly once, and a site becomes a writer one tick after another writer writes the activation value 1
into its opcode (OP(init, 1) == 1 with init chosen per OP: AND uses 0xFF, the others 0). Background: opcode 9
(inert), energy 0. Gadgets (inputs a, b, c, d planted as payloads):
  C0 transmission        A(a) -> T                                              out T = OP(t0, a)
  C1 state-dependent     T holds s; A(a) -> T                                   out T = OP(s, a)
  C2 delayed retention   A(a) -> M at t1; M activated by a 4-step chain, then M -> O     out O (tick 6) = OP(o0, a)
  C3 two inputs          A(a) -> T at t1; B(b) delayed one tick -> T at t2      out T = OP(OP(t0, a), b)
  C4 two-part composition  P1 = C3 computing x at T1; P2 = C(c) -> U at t1, T1 activated at t3, T1 -> U
                         out U = OP(OP(u0, c), x)
  C5 multi-step          C4 plus U activated at t4, U -> V, D(d) -> V at t1     out V = OP(OP(v0, d), U)
For every gadget and OP: the full function table over input values IN, plus ablations (remove A, remove B, remove both,
remove part 1, remove part 2, shuffle a component's aim, translate the whole gadget, random surroundings beyond a
4-site energy-0 moat). Verdicts in evaluate().
"""

import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (AETHER, os.path.join(AETHER, "test"), os.path.join(AETHER, "runpod", "aeth01_canary")):
    sys.path.insert(0, p)

OPS = ("REPLACE", "XOR", "ADD", "AND", "SPLICE", "ROTX")
SEM = {o: "aeth01.op_%s" % o.lower() for o in OPS}
SEM["REPLACE"] = "aeth01.v1"
EXEC_ONLY = dict(write_cost=1, maintenance_cost=0, replenish_numer=0, replenish_amount=0)
B_BAL = dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8)
N, E, S, W = 0, 1, 2, 3
INERT = 9
IN = (0x0F, 0x33, 0x55, 0xAA)
IDENT = {"REPLACE": 0, "XOR": 0, "ADD": 0, "AND": 0xFF, "SPLICE": 0, "ROTX": 0}
ACT_INIT = {"REPLACE": 0, "XOR": 0, "ADD": 0, "AND": 0xFF, "SPLICE": 0, "ROTX": 0}


def rotl(x, k):
    x = x.astype(np.int64) & 0xFF
    k = k.astype(np.int64) & 7
    return (((x << k) | (x >> ((8 - k) % 8))) & 0xFF).astype(np.int64)


def op_apply(xp, op, old, new):
    o = old.astype(xp.int64)
    i = new.astype(xp.int64)
    if op == "REPLACE":
        r = i
    elif op == "XOR":
        r = o ^ i
    elif op == "ADD":
        r = (o + i) & 0xFF
    elif op == "AND":
        r = o & i
    elif op == "SPLICE":
        r = (o & 0xF0) | (i & 0x0F)
    elif op == "ROTX":
        k = i & 7
        r = (((o << k) | (o >> ((8 - k) % 8))) & 0xFF) ^ i
    else:
        raise ValueError(op)
    return r.astype(xp.uint8)


def load(backend="cpu"):
    if backend == "gpu":
        import aeth01_gpu_kernel as K
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def step(xp, K, op, n, seed, tick, s, energy, observer=None):
    obs = [] if observer is None else observer
    out = K.gpu_step(n, n, seed, tick, energy["write_cost"], energy["maintenance_cost"],
                     energy["replenish_numer"], energy["replenish_amount"], 0, *s, observer=obs)
    nxt = list(out[:5])
    if op != "REPLACE":
        for f in range(4):
            wr = obs[f][0] != 255
            nxt[f] = xp.where(wr, op_apply(xp, op, s[f], nxt[f]), nxt[f])
    return nxt, obs


class World:
    def __init__(self, n=32):
        self.n = n
        self.s = [np.full((n, n), INERT, np.uint8), np.zeros((n, n), np.uint8), np.zeros((n, n), np.uint8),
                  np.zeros((n, n), np.uint8), np.zeros((n, n), np.uint8)]
        self.cells = set()

    def put(self, y, x, opcode=INERT, d=0, field=3, payload=0, energy=0):
        for f, v in enumerate((opcode, d, field, payload, energy)):
            self.s[f][y, x] = v
        self.cells.add((y, x))


def writer(w, y, x, d, field, payload, op, delayed_by=0, energy=1):
    """A one-shot writer at (y, x) firing at tick 1 + delayed_by. Delay is built from an activation chain placed
    behind the writer (opposite its aim). Returns the list of chain cells."""
    w.put(y, x, opcode=1 if delayed_by == 0 else ACT_INIT[op], d=d, field=field, payload=payload, energy=energy)
    back = {N: (1, 0), S: (-1, 0), E: (0, -1), W: (0, 1)}[d]
    cy, cx = y, x
    for i in range(delayed_by):
        ny, nx = cy + back[0], cx + back[1]
        last = i == delayed_by - 1
        w.put(ny, nx, opcode=1 if last else ACT_INIT[op], d=d, field=0, payload=1, energy=1)
        cy, cx = ny, nx
    return


def build(gadget, op, inputs, ablate=(), shuffle=None, offset=(0, 0), n=32):
    w = World(n)
    oy, ox = 12 + offset[0], 12 + offset[1]
    I = dict(inputs)
    t0 = IDENT[op]
    out = None
    if gadget in ("C0", "C1"):
        w.put(oy, ox, payload=I.get("s", t0))
        if "A" not in ablate:
            writer(w, oy, ox - 1, E, 3, I["a"], op)
        out, ticks = (oy, ox), 3
    elif gadget == "C2":
        w.put(oy, ox, opcode=ACT_INIT[op], d=E, field=3, payload=t0, energy=1)      # M, aimed east at O
        w.put(oy, ox + 1, payload=t0)                                               # O
        if "A" not in ablate:
            writer(w, oy - 1, ox, S, 3, I["a"], op)                                 # A -> M.payload at tick 1
        if "ACT" not in ablate:
            writer(w, oy + 1, ox, N, 0, 1, op, delayed_by=3)                        # activates M at tick 4
        out, ticks = (oy, ox + 1), 8
    elif gadget in ("C3", "C4", "C5"):
        # part 1: T1 = OP(OP(t0, a), b)
        w.put(oy, ox, opcode=ACT_INIT[op] if gadget != "C3" else INERT, d=S, field=3, payload=t0, energy=1)
        if "A" not in ablate and "P1" not in ablate:
            writer(w, oy, ox - 1, E, 3, I["a"], op)
        if "B" not in ablate and "P1" not in ablate:
            writer(w, oy, ox + 1, W, 3, I["b"], op, delayed_by=1)
        out, ticks = (oy, ox), 4
        if gadget in ("C4", "C5"):
            # part 2: U = OP(OP(u0, c), T1), T1 activated to fire at tick 3
            w.put(oy + 1, ox, opcode=ACT_INIT[op] if gadget == "C5" else INERT, d=E, field=3, payload=t0, energy=1)
            if "C" not in ablate:
                writer(w, oy + 2, ox, N, 3, I["c"], op)
            if "P2" not in ablate:
                writer(w, oy - 1, ox, S, 0, 1, op, delayed_by=1)                    # T1.opcode at tick 2
            out, ticks = (oy + 1, ox), 6
        if gadget == "C5":
            # stage 3: V = OP(OP(v0, d), U), U activated to fire at tick 4
            w.put(oy + 1, ox + 1, payload=t0)
            if "D" not in ablate:
                writer(w, oy + 1, ox + 2, W, 3, I["d"], op)
            if "P3" not in ablate:
                writer(w, oy + 1, ox - 1, E, 0, 1, op, delayed_by=2)                # U.opcode at tick 3
            out, ticks = (oy + 1, ox + 1), 8
    if shuffle is not None:
        rng = np.random.default_rng(shuffle)
        cells = sorted(w.cells - {out})
        y, x = cells[rng.integers(0, len(cells))]
        w.s[1][y, x] = (int(w.s[1][y, x]) + 1 + rng.integers(0, 3)) % 4                # re-aim one component
        w.s[2][y, x] = int(rng.integers(0, 5))                                      # and its field
    return w, out, ticks


def surround(w, seed, moat=4):
    rng = np.random.default_rng(seed)
    n = w.n
    ys = [c[0] for c in w.cells]
    xs = [c[1] for c in w.cells]
    y0, y1, x0, x1 = min(ys) - moat, max(ys) + moat, min(xs) - moat, max(xs) + moat
    for y in range(n):
        for x in range(n):
            if y0 <= y <= y1 and x0 <= x <= x1:
                continue
            for f in range(5):
                w.s[f][y, x] = rng.integers(0, 256)
            if rng.random() < 0.5:
                w.s[0][y, x] = 1


def run(gadget, op, inputs, energy=EXEC_ONLY, seed=7, surround_seed=None, **kw):
    xp, K = load("cpu")
    w, out, ticks = build(gadget, op, inputs, **kw)
    if surround_seed is not None:
        surround(w, surround_seed)
    s = [x.copy() for x in w.s]
    for t in range(ticks):
        s, _ = step(xp, K, op, w.n, seed, t + 1, s, energy)
    return int(s[3][out])


INPUT_NAMES = {"C0": ("a",), "C1": ("s", "a"), "C2": ("a",), "C3": ("a", "b"), "C4": ("a", "b", "c"),
               "C5": ("a", "b", "c", "d")}


def table(gadget, op, **kw):
    names = INPUT_NAMES[gadget]
    return {vals: run(gadget, op, dict(zip(names, vals)), **kw) for vals in itertools.product(IN, repeat=len(names))}


def depends_on(tab, names, var):
    """True iff, for EVERY assignment of the other inputs, varying `var` changes the output (strict dependence)."""
    i = names.index(var)
    groups = {}
    for k, v in tab.items():
        groups.setdefault(k[:i] + k[i + 1:], set()).add(v)
    return all(len(g) > 1 for g in groups.values())


def depends_any(tab, names, var):
    i = names.index(var)
    groups = {}
    for k, v in tab.items():
        groups.setdefault(k[:i] + k[i + 1:], set()).add(v)
    return any(len(g) > 1 for g in groups.values())


def evaluate(op):
    """Planted expressibility verdicts for one OP. Strict dependence = every slice; ablation = no slice depends."""
    R = {}
    def dep(tab, g, v):
        return depends_on(tab, INPUT_NAMES[g], v)

    def anydep(tab, g, v):
        return depends_any(tab, INPUT_NAMES[g], v)

    def robust(g, base):
        moved = table(g, op, offset=(3, -4))
        surr = [table(g, op, surround_seed=s) for s in (11, 12)]
        shuf = [table(g, op, shuffle=s) for s in (21, 22, 23)]
        return {"translation_invariant": moved == base, "surroundings_invariant": all(t == base for t in surr),
                "shuffles_breaking": sum(1 for t in shuf if t != base), "shuffles": len(shuf)}
    t = table("C0", op)
    R["C0"] = {"pass": dep(t, "C0", "a"), **robust("C0", t)}
    t = table("C1", op)
    R["C1"] = {"pass": dep(t, "C1", "s") and dep(t, "C1", "a"), "dep_s": dep(t, "C1", "s"), "dep_a": dep(t, "C1", "a")}
    t = table("C2", op)
    ta = table("C2", op, ablate=("ACT",))
    R["C2"] = {"pass": dep(t, "C2", "a") and not anydep(ta, "C2", "a"), "dep_a": dep(t, "C2", "a"),
               "ablate_activation_kills": not anydep(ta, "C2", "a"), **robust("C2", t)}
    t = table("C3", op)
    tA, tB = table("C3", op, ablate=("A",)), table("C3", op, ablate=("B",))
    R["C3"] = {"pass": dep(t, "C3", "a") and dep(t, "C3", "b") and not anydep(tA, "C3", "a") and not anydep(tB, "C3", "b"),
               "dep_a": dep(t, "C3", "a"), "dep_b": dep(t, "C3", "b"), **robust("C3", t)}
    t = table("C4", op)
    t1, t2, t12 = (table("C4", op, ablate=x) for x in (("P1",), ("P2",), ("P1", "P2")))
    R["C4"] = {"dep_all": all(dep(t, "C4", v) for v in "abc"),
               "P1_removed_kills_ab": not anydep(t1, "C4", "a") and not anydep(t1, "C4", "b"),
               "P2_removed_kills_ab": not anydep(t2, "C4", "a") and not anydep(t2, "C4", "b"),
               "both_removed_kills_ab": not anydep(t12, "C4", "a") and not anydep(t12, "C4", "b"),
               "either_part_alone_lacks_capability": (not all(dep(t1, "C4", v) for v in "abc")) and
                                                    (not all(dep(t2, "C4", v) for v in "abc")),
               **robust("C4", t)}
    R["C4"]["pass"] = R["C4"]["dep_all"] and R["C4"]["P1_removed_kills_ab"] and R["C4"]["P2_removed_kills_ab"] \
        and R["C4"]["translation_invariant"] and R["C4"]["surroundings_invariant"]
    t = table("C5", op)
    k1, k2, k3 = (table("C5", op, ablate=(x,)) for x in ("P1", "P2", "P3"))
    R["C5"] = {"dep_all": all(dep(t, "C5", v) for v in "abcd"),
               "P1_removed_kills_ab": not anydep(k1, "C5", "a") and not anydep(k1, "C5", "b"),
               "P2_removed_kills_ab": not anydep(k2, "C5", "a") and not anydep(k2, "C5", "b"),
               "P3_removed_kills_abc": not any(anydep(k3, "C5", v) for v in "abc")}
    R["C5"]["pass"] = all(R["C5"][k] for k in ("dep_all", "P1_removed_kills_ab", "P2_removed_kills_ab", "P3_removed_kills_abc"))
    # environmental limit: the same C3 gadget under B_balanced energy (rain, maintenance) -- reported, not gated
    tb = table("C3", op, energy=B_BAL)
    R["env_B_balanced_C3_same_table"] = tb == table("C3", op)
    return R


def main():
    out = {"schema": "aether.reach01.r2.express.v1", "semantics": SEM, "inputs": IN, "results": {}}
    for op in OPS:
        r = evaluate(op)
        out["results"][op] = r
        print(op, {g: r[g]["pass"] for g in ("C0", "C1", "C2", "C3", "C4", "C5")}, "B_bal C3 same:", r["env_B_balanced_C3_same_table"],
              "C4 detail:", {k: v for k, v in r["C4"].items() if k != "pass"}, file=sys.stderr, flush=True)
    json.dump(out, open(os.path.join(HERE, "express01_results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
