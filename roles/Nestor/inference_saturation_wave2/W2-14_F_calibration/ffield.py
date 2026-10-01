"""W2-14 core: a map-built FIELD process for an implanted founder, built only from the world's own single-interaction
code (world.Runner._pair_interact on a constructed, NEVER-run runner; _mutate inside it; P-11 assay inside it).
No Runner.run(), no step(), no summary(). Static/illustrative.

Physics: 7ae3 C9 H2 arm-B cell (atlas_axis NONE), tier M (pop 256, slice 300), stock z8 (as X-TICKET / C-ATOMIC).
Write-back W: BASE = world.Runner; ATOMIC = run_ds.runner_cls(world) (== c_atomic/run_cat.py At).

The field: the runner's own 256 placed organisms, placed exactly as Runner.run() places them (same rng draws, so the
background genomes are the world's for that seed). Per epoch:
  r._env_epoch()  (COEVO_ENV consumes world rng; kept so the rng stream is the world's)
  shuffle the alive organisms with the world rng and pair them in order (as _pair_epoch); for each pair:
    - involving a founder-label member (anc == 0): r._pair_interact (world code, unchanged)
    - background-background: per PARTNER model
Knobs (each an ingredient, ablated one at a time):
  STRUCT  FIELD : the 256-site field above (kin pairing + density: partners are the current field contents)
          FREE  : no field; every member meets its own private background partner each epoch (no kin, no density
                  limit) -- the c7c / h1 branching-process topology
  PARTNER FULL  : bg-bg pairs are interacted too (=> FIELD+FULL is the world's pair epoch; the circular ceiling)
          BANK  : bg-bg pairs skipped; a bg organism is overwritten, at the moment it meets a member, by a draw
                  (genome + registers) from a bank of background states realized at that epoch in a bg-only field
          POOL  : as BANK but the draw is a fresh uniform genome + registers from a pool of post-execution states (h1)
          FRESH0: fresh uniform genome, registers None (c7c)
  CTX     CARRY (world: members keep the registers left by their last interaction; newborns keep the victim's)
          ZERO  (members' registers reset to None before every interaction)
  MUT     ON (world) / OFF (r._mutate replaced by identity; VM copy errors unchanged)
Readouts (horizon T epochs): world-style max causal depth over all recorded births (depth_all_causal) and over the
founder's causal tree only (depth_f); X-TICKET's B (cumulative P-11-causal births in the founder's causal lineage),
N (its live members), A (live anc==0); predecessor births from anc-0 parents (Ball); max A (c7c's CAP readout).
Early stop: A == 0; or (epoch >= 100 and no anc-0-parent birth in the last 100 epochs) [recorded as 'frozen'];
or decided runaway (depth_f >= 20 and B >= 163 and maxA >= 40).
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
CAMP = NESTOR / "campaigns"
C9 = CAMP / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(CAMP / "c9x-explore-2026-09-24" / "x_donor_swap"))
sys.path.insert(0, str(C9))
import world  # noqa: E402
import run_ds  # noqa: E402

SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
_man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
_b = next(b for b in _man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
ARM = next(a for a in _b["arms"] if a["arm"] == "B_reimplant_actual")
G7 = bytes.fromhex(ARM["kwargs"]["implant_hex"])
CELL = dict(ARM["cell"], atlas_axis="NONE")
TIER = ARM["tier"]
ATOMIC_CLS = run_ds.runner_cls(world)


def make_runner(rule, seed, mut=True, implant=True):
    base = world.Runner if rule == "BASE" else ATOMIC_CLS

    class F(base):
        pass
    if not mut:
        F._mutate = lambda self, g: bytes(g)
    kw = dict(implant="ACTUAL_GENOME", implant_bytes=G7) if implant else {}
    r = F(CELL, seed, tier=TIER, **kw)
    # population exactly as Runner.run() places it (same rng draws)
    anc = 0
    for i in range(r.pop_cap):
        if i == 0 and r.implant:
            g = r._pad(r._implant_genome())
        else:
            g = r._seed_genome()
        o = r._place(g, anc, niche=r._initial_niche(i))
        o.energy = r.t["slice"] * 2
        anc += 1
    return r


def set_org(r, o, g, st):
    r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
    r.mem[o.slot:o.slot + len(g)] = g
    o.length = len(g)
    o.regs = None if st[0] is None else list(st[0])
    o.fz, o.fc = st[1], st[2]


def state(o):
    return (None if o.regs is None else list(o.regs), o.fz, o.fc)


class Model:
    """Draws background partner states for the non-FULL partner models."""

    def __init__(self, partner, rng, bank=None, pool=None, L=64):
        self.partner, self.rng, self.bank, self.pool, self.L = partner, rng, bank, pool, L

    def draw(self, epoch):
        if self.partner == "BANK":
            snap = self.bank[min(epoch, len(self.bank) - 1)]
            g, st = snap[self.rng.randrange(len(snap))]
            return g, st
        g = bytes(self.rng.randrange(256) for _ in range(self.L))
        if self.partner == "POOL":
            return g, self.pool[self.rng.randrange(len(self.pool))]
        return g, (None, 0, 0)


def depth_from(lineage, roots=None):
    """max causal depth; roots=None -> all causal edges (world readout); else only the tree under roots."""
    cp = {e["child"]: e["parent"] for e in lineage if e["kind"] == "birth" and e["causal"]}
    if roots is None:
        return world.Runner._depths(cp)[0]
    ch = {}
    for c, p in cp.items():
        ch.setdefault(p, []).append(c)
    best, stack = 0, [(x, 0) for x in roots]
    while stack:
        x, d = stack.pop()
        best = max(best, d)
        for c in ch.get(x, ()):
            stack.append((c, d + 1))
    return best


def run(rule, seed, struct="FIELD", partner="FULL", ctx="CARRY", mut=True, T=300, bank=None, pool=None,
        traj=False, stop_runaway=True):
    r = make_runner(rule, seed, mut=mut)
    mrng = random.Random(repr(("W2-14", rule, seed, struct, partner, ctx, mut)))
    model = Model(partner, mrng, bank, pool, r.L)
    founder = next(o for o in r.orgs if o.anc == 0)
    f0 = founder.oid
    causal_set = {f0}
    cnt = {"B": 0, "Ball": 0, "last_birth": 0, "calls": 0}

    orig_lb = r._lin_birth

    def lb(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
        if causal and parent in causal_set:
            causal_set.add(child)
            cnt["B"] += 1
        if parent in anc0_oids:
            cnt["Ball"] += 1
            cnt["last_birth"] = r.epoch
        orig_lb(child, parent, niche, fid, span, causal, causal_pred, None)   # p11 record dropped (memory)
    r._lin_birth = lb
    anc0_oids = set()

    def interact(a, b, i):
        for o in (a, b):
            if ctx == "ZERO" and o.anc == 0:
                o.regs, o.fz, o.fc = None, 0, 0
        cnt["calls"] += 1
        anc0_oids.clear()
        anc0_oids.update(o.oid for o in (a, b) if o.anc == 0)
        r._pair_interact(i, a, b)

    tr, maxA, stop = [], 1, "horizon"
    for ep in range(T):
        r.epoch = ep
        r._env_epoch()
        alive = [o for o in r.orgs if o.alive]
        if struct == "FIELD":
            r.rng.shuffle(alive)
            for i in range(0, len(alive) - 1, 2):
                a, b = alive[i], alive[i + 1]
                lin = a.anc == 0 or b.anc == 0
                if not lin:
                    if partner == "FULL":
                        r._pair_interact(i, a, b)
                        cnt["calls"] += 1
                    continue
                if partner != "FULL":
                    for o in (a, b):
                        if o.anc != 0:
                            g, st = model.draw(ep)
                            set_org(r, o, g, st)
                interact(a, b, i)
        else:  # FREE: each member meets a private background partner
            mem = [o for o in alive if o.anc == 0]
            mrng.shuffle(mem)
            for k, o in enumerate(mem):
                if not o.alive or o.anc != 0:
                    continue
                if len(r.free_slots) < 2:
                    break
                g, st = model.draw(ep)
                p = r._place(g, 1)
                p.regs, p.fz, p.fc = (None if st[0] is None else list(st[0])), st[1], st[2]
                a, b = (o, p) if mrng.randrange(2) == 0 else (p, o)
                interact(a, b, 2 * k)
                for x in (o, p):
                    if x.anc != 0:
                        r._kill(x, "free_bg")
            if len(r.orgs) > 4 * r.pop_cap:
                r.orgs = [o for o in r.orgs if o.alive]
        for o in r.orgs:
            if o.alive:
                o.age += 1
        live = [o for o in r.orgs if o.alive]
        A = sum(o.anc == 0 for o in live)
        N = sum(o.oid in causal_set for o in live)
        maxA = max(maxA, A)
        if traj:
            tr.append((N, A, cnt["B"]))
        if A == 0:
            stop = "extinct"
            break
        if ep >= 100 and ep - cnt["last_birth"] >= 100:
            stop = "frozen"
            break
        if struct == "FREE" and A >= 256:
            stop = "free_cap256"
            break
        if stop_runaway and maxA >= 40 and cnt["B"] >= 163 and ep % 10 == 9 and \
                depth_from(r.lineage, [f0]) >= 20:
            stop = "runaway_decided"
            break
    out = {"rule": rule, "seed": seed, "struct": struct, "partner": partner, "ctx": ctx, "mut": mut,
           "epochs": ep + 1, "stop": stop, "B": cnt["B"], "Ball": cnt["Ball"], "maxA": maxA,
           "A_end": A, "N_end": N, "depth_f": depth_from(r.lineage, [f0]),
           "depth_world": depth_from(r.lineage), "calls": cnt["calls"]}
    if traj:
        out["traj"] = tr
    return out


def bg_bank(seed, T=300, per=64, rule="BASE"):
    """Background states realized at each epoch of a bg-only field (no implant), FULL partner model, rule W."""
    r = make_runner(rule, seed, implant=False)
    rng = random.Random(seed)
    snaps = []
    for ep in range(T):
        r.epoch = ep
        r._env_epoch()
        alive = [o for o in r.orgs if o.alive]
        r.rng.shuffle(alive)
        for i in range(0, len(alive) - 1, 2):
            r._pair_interact(i, alive[i], alive[i + 1])
        alive = [o for o in r.orgs if o.alive]
        snaps.append([(r._genome(o), state(o)) for o in rng.sample(alive, per)])
    return snaps, r


def post_exec_pool(seed, n=400):
    """h1-style pool: registers of fresh random genomes after one random-random interaction."""
    r = make_runner("BASE", seed, implant=False)
    rng = random.Random(seed)
    a, b = r.orgs[0], r.orgs[1]
    pool = []
    for _ in range(n // 2):
        set_org(r, a, bytes(rng.randrange(256) for _ in range(64)), (None, 0, 0))
        set_org(r, b, bytes(rng.randrange(256) for _ in range(64)), (None, 0, 0))
        r._pair_interact(0, a, b)
        pool += [state(a), state(b)]
    return pool
