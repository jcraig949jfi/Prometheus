"""T-H3-MAT: the H3 ruler tournament (C9-D14) and the material ruler's gate.

Every fixture drives REAL pair interactions through `Runner._pair_interact` (the code
path the campaign runs), with hand-assembled programs, chosen niches, logged migrations,
and a crossing recorded through `Runner._record_cross`. Four candidate rulers judge each
fixture:

  R0  id certificate, repaired (founder born easy -> logged migration -> hard crossing;
      every pair edge on the chain P-11 causal)                 - the current code
  R1  founder-genome fidelity: founder born easy, crossing in a hard niche, crossing
      genome >= 0.50 identical to the founder's birth genome
  R2  >= 1 P-11-causal edge on the chain, crossing within 50 epochs of the last one
  R3  material: crossing in a hard niche by a genome >= 0.50 easy-niche MATERIAL,
      tags carried by dataflow through the VM (z8taint)

EXPECTED outcomes encode the question H3 asks - did MATERIAL made in the easy niche
reach a hard niche and cross there - so a fixture's expectation depends only on where
the crossing genome's bytes were made.

Also: z8taint.run_tainted is bit-identical to z8.run on random programs, and the H3
worlds are unchanged by tracking (both checked here).

Run:  python tests/test_h3_material.py    Exit 0 iff the selected ruler R3 passes every
fixture, R0 is caught on the id-only fixture, and the equivalence checks hold.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import world          # noqa: E402
import z8             # noqa: E402
import z8taint        # noqa: E402
from constants import C   # noqa: E402

N = 64
CELL = {"world": "PAIR_TAPE", "environment": "STATIC", "representation": "Z8_64",
        "reproduction": "PAIR_EXECUTION", "self_location": "PRIMITIVE", "copy_primitive": "BLOCK",
        "pressure": "NONE_IMPLICIT", "structure": "RESERVOIR", "task_transform": "ADD1",
        "read_order": "ANSWER_BEFORE_READ", "bridge": "VALLEY", "seeding": "RANDOM",
        "mutation_operator": "BOTH", "mutation_locality": "LOCAL", "mutation_rate": "MID",
        "atlas_axis": "NONE"}
K_WINDOW = 50


def prog(src, seed):
    code, _ = z8.asm(src)
    r = random.Random(seed)
    return code + bytes(r.randrange(256) for _ in range(N - len(code)))


INERT = lambda seed: prog("HALT", seed)                                   # noqa: E731
COPIER = lambda seed: prog("SELF\nLD DE,64\nLDIR\nHALT", seed)            # a -> b half  # noqa: E731


def overwriter(k, seed):
    """Writes k computed bytes (INC A) over the OTHER half, starting at its base."""
    return prog("LD HL,64\nLD C,%d\nloop:\nINC A\nLD (HL),A\nINC HL\nDEC C\nJRNZ loop\nHALT" % k, seed)


class Fx:
    def __init__(self, locality="LOCAL", mut=0.0):
        cell = dict(CELL, mutation_locality=locality)
        self.r = world.Runner(cell, 777, tier="S", max_epochs=1)
        self.r.mut_rate = mut
        self.r.t["slice"] = 1000        # let fixture programs finish inside one slice
        self.birth = {}

    def place(self, genome, niche):
        o = self.r._place(genome, len(self.birth), niche=niche)
        self.birth[o.oid] = (bytes(genome), niche)
        return o

    def migrate(self, o, to):
        frm, o.niche = o.niche, to
        self.r._lin_migration(o.oid, frm, to)

    def interact(self, a, b, epochs=1):
        for _ in range(epochs):
            self.r._pair_interact(0, a, b)
            self.r.epoch += 1

    def cross(self, o):
        o.held = 1.0
        return self.r._record_cross(o)


# ------------------------------------------------------------------ rulers
def chain_of(r, oid):
    parent, _cp, birth_niche, moves = r._lineage_graph()
    ch, cur = [], oid
    while cur is not None and cur not in ch:
        ch.append(cur)
        cur = parent.get(cur)
    return ch, parent, birth_niche, moves


def R0(fx, o, ev):
    r = fx.r
    ch, parent, bn, moves = chain_of(r, o.oid)
    c = r.ancestry_certificate(o.oid, bn, parent, moves)
    return bool(c) and ev["niche"] != 0


def R1(fx, o, ev):
    ch, parent, bn, moves = chain_of(fx.r, o.oid)
    founder = ch[-1]
    g0, n0 = fx.birth.get(founder, (None, None))
    if g0 is None or n0 != 0 or ev["niche"] == 0:
        return False
    return world._fidelity(g0, fx.r._genome(o)) >= 0.5


def R2(fx, o, ev):
    r = fx.r
    ch, parent, bn, moves = chain_of(r, o.oid)
    edges = {e["child"]: e for e in r.lineage if e["kind"] == "birth"}
    causal = [edges[c] for c in ch if c in edges and edges[c]["causal"]]
    if not causal or ev["niche"] == 0:
        return False
    return ev["epoch"] - max(e["epoch"] for e in causal) <= K_WINDOW


def R3(fx, o, ev):
    share = ev.get("easy_material_share")
    return ev["niche"] != 0 and share is not None and share >= C["H3_MATERIAL_SHARE"]


RULERS = {"R0_id": R0, "R1_founder_fidelity": R1, "R2_causal_edge_window": R2, "R3_material": R3}


# ------------------------------------------------------------------ fixtures
def f1_same_id_overwritten():
    fx = Fx()
    x = fx.place(INERT(1), 0)
    fx.migrate(x, 2)
    y = fx.place(overwriter(64, 2), 2)
    fx.interact(y, x)
    return fx, x, False, "id kept, all 64 bytes rewritten by a hard-niche partner"


def f2_genome_retained():
    fx = Fx()
    x = fx.place(INERT(3), 0)
    fx.migrate(x, 2)
    y = fx.place(INERT(4), 2)
    fx.interact(y, x)
    return fx, x, True, "easy genome migrates unchanged"


def f3_gradual_mutation():
    fx = Fx(mut=0.01)
    x = fx.place(INERT(5), 0)
    fx.migrate(x, 2)
    y = fx.place(INERT(6), 2)
    fx.interact(y, x, epochs=25)
    return fx, x, True, "carried easy genome, ~20% point mutations in the hard niche"


def f3b_structural_mutation():
    fx = Fx(locality="STRUCTURAL", mut=0.01)
    x = fx.place(INERT(7), 0)
    fx.migrate(x, 2)
    y = fx.place(INERT(8), 2)
    fx.interact(y, x, epochs=25)
    return fx, x, True, "carried easy genome, ~20% mutations incl. frame-shifting indels"


def f4_noncausal_overwrite():
    fx = Fx()
    x = fx.place(INERT(9), 0)
    fx.migrate(x, 2)
    y = fx.place(overwriter(45, 10), 2)
    fx.interact(y, x)
    return fx, x, False, "70% of the carried genome overwritten by a hard partner, no copy"


def f5_p11_copy():
    fx = Fx()
    d = fx.place(COPIER(11), 0)
    v = fx.place(INERT(12), 2)
    fx.interact(d, v)
    return fx, v, True, "easy-niche donor copies itself into a hard-niche victim (P-11)"


def f6a_mixed_light():
    fx, v, _, _ = f5_p11_copy()
    z = fx.place(overwriter(19, 13), 2)
    fx.interact(z, v)
    return fx, v, True, "P-11 copy, then 30% noncausal hard overwrite"


def f6b_mixed_heavy():
    fx, v, _, _ = f5_p11_copy()
    z = fx.place(overwriter(45, 14), 2)
    fx.interact(z, v)
    return fx, v, False, "P-11 copy, then 70% noncausal hard overwrite"


def f7_partial_copy_no_edge():
    fx = Fx()
    d = fx.place(prog("SELF\nLD DE,64\nLD BC,40\nLDIR\nHALT", 15), 0)
    v = fx.place(INERT(16), 2)
    fx.interact(d, v)
    return fx, v, True, "easy donor copies 40/64 bytes into a hard victim; no lineage edge"


FIXTURES = [f1_same_id_overwritten, f2_genome_retained, f3_gradual_mutation,
            f3b_structural_mutation, f4_noncausal_overwrite, f5_p11_copy, f6a_mixed_light,
            f6b_mixed_heavy, f7_partial_copy_no_edge]


def equivalence(n=400):
    R = random.Random(11)
    bad = 0
    for _ in range(n):
        mem = bytearray(R.randrange(256) for _ in range(256))
        regs = [R.randrange(256) for _ in range(8)]
        pol, budget, seed = R.choice([z8.ARENA, z8.OWN]), R.choice([60, 220, 360]), R.randrange(10**9)
        outs = []
        for mode in (0, 1):
            m = bytearray(mem)
            ctx = z8.Ctx(m, 0, 96, policy=pol, rng=random.Random(seed), copy_mut_rate=0.02)
            ctx.regs = list(regs)
            pc = (z8.run(ctx, 0, budget, 0x3F) if mode == 0 else
                  z8taint.run_tainted(ctx, 0, budget, 0x3F, orig=bytearray(256), here=1)[0])
            outs.append((pc, bytes(m), ctx.regs, ctx.fz, ctx.fc, ctx.ops, ctx.writes,
                         ctx.writes_other, ctx.copy_errors))
        bad += outs[0] != outs[1]
    return bad


def main():
    ok = True
    table = []
    print("%-26s %-8s %s" % ("fixture", "expected", "  ".join("%-22s" % k for k in RULERS)))
    for fn in FIXTURES:
        fx, o, want, desc = fn()
        ev = fx.cross(o)
        row = {"fixture": fn.__name__, "desc": desc, "expected": want,
               "easy_material_share": ev.get("easy_material_share")}
        for name, rule in RULERS.items():
            row[name] = bool(rule(fx, o, ev))
        table.append(row)
        print("%-26s %-8s %s   share=%s" % (fn.__name__, want, "  ".join(
            "%-22s" % (("ok " if row[k] == want else "XX ") + str(row[k])) for k in RULERS),
            ev.get("easy_material_share")))
    score = {k: sum(r[k] == r["expected"] for r in table) for k in RULERS}
    print("score (of %d):" % len(table), score)
    r3_all = all(r["R3_material"] == r["expected"] for r in table)
    r0_caught = next(r for r in table if r["fixture"] == "f1_same_id_overwritten")["R0_id"] is True
    eq = equivalence()
    ok = r3_all and r0_caught and eq == 0
    print("R3 passes every fixture:", r3_all)
    print("fail-on-old-code: R0 (current id certificate) certifies the overwritten id:", r0_caught)
    print("run_tainted == z8.run on 400 random programs, mismatches:", eq)
    (ROOT / "H3_RULER_TOURNAMENT.json").write_text(json.dumps(
        {"fixtures": table, "score": score, "selected": "R3_material" if r3_all else None,
         "k_window_R2": K_WINDOW, "share_threshold": C["H3_MATERIAL_SHARE"]}, indent=1))
    print("T-H3-MAT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
