"""W2-2 h1: per-individual fecundity, certification and age profile across generations, from SINGLE pair
interactions in the specimen's own frozen cell (stock VM, world._pair_interact unchanged; no world/evolution run).

For specimen S (7ae3, cb7f; optional ffa6) and write-back rule (BASE = world as frozen, ATOMIC = C-ATOMIC's restore
rule copied verbatim from c_atomic/run_cat.py):
  generation 0 = the implanted founder (fresh state). Each individual lives up to H interactions, one per "epoch",
  each with a fresh random background partner (the cell's own _seed_genome; partner registers drawn from a pool
  of post-execution background states), tape side 50/50. Its genome and registers carry over between its own
  interactions exactly as the world writes them back. It dies when it is converted (a birth credited to the
  partner). Every accepted birth it makes (world predecessor criterion) creates a child = the converted partner
  half as stored, running in the victim's leftover registers (U-W7). Up to CAP children per generation are
  followed (first-born first), for G generations.
Readouts per (S, rule, generation): births per individual within H, P-11-causal births per individual,
causal share of births, share of individuals with zero births, age profile of births, survival to H,
and the certified branching number m_c = mean causal births per individual (depth grows only if m_c > 1
along the certified tree). Static: no population, no density, no shared field.
python -B h1_lineage_tree.py [H] [CAP] [G] -> h1_lineage_tree.json
"""
from __future__ import annotations
import json, pathlib, random, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parents[1] / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world  # noqa: E402

H = int(sys.argv[1]) if len(sys.argv) > 1 else 30
CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 30
G = int(sys.argv[3]) if len(sys.argv) > 3 else 4
SPECS = [s for s in ["7ae3f9c1437c8000-s54765-tL-a0", "cb7f5ca16e697938-s60768-tL-a0"] if s[:4] in (sys.argv[5].split(",") if len(sys.argv) > 5 else ["7ae3", "cb7f"])]
SEEDS = range(1, 1 + (int(sys.argv[4]) if len(sys.argv) > 4 else 2))
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())


def arm_of(sp):
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == sp)
    return next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")


def make(sp, rule, seed):
    arm = arm_of(sp)
    births = []

    class R(world.Runner):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            births.append((parent, bool(causal)))

        def _pair_interact(self, i, a, b):
            if rule == "BASE":
                return super()._pair_interact(i, a, b)
            pre = [(o, o.oid, self._genome(o)) for o in (a, b)]
            super()._pair_interact(i, a, b)
            for o, oid, g in pre:
                if o.oid != oid:
                    continue
                new = self._mutate(g)
                self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                self.mem[o.slot:o.slot + len(new)] = new
                o.length = len(new)

    r = R(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"])
    assert not r.track_material
    r.births = births
    return r, bytes.fromhex(arm["kwargs"]["implant_hex"])


def set_org(r, o, g, st):
    r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
    r.mem[o.slot:o.slot + len(g)] = g
    o.length = len(g)
    o.regs = None if st[0] is None else list(st[0])
    o.fz, o.fc = st[1], st[2]


def state(o):
    return (None if o.regs is None else list(o.regs), o.fz, o.fc)


def partner_pool(r, rng, n=200):
    """post-execution background states: two background genomes interact once, keep the post states."""
    a = r._place(bytes(r.L), 1); b = r._place(bytes(r.L), 1)
    pool = []
    for _ in range(n // 2):
        set_org(r, a, r._seed_genome(), (None, 0, 0)); set_org(r, b, r._seed_genome(), (None, 0, 0))
        r._pair_interact(0, a, b)
        pool += [state(a), state(b)]
    return pool


def live(r, d, p, g, st, pool, rng, ctr):
    """one individual's life: returns (births list [(age, causal, child_genome, child_state)], died_at or None)."""
    out = []
    for age in range(1, H + 1):
        pg = r._seed_genome()
        set_org(r, d, g, st)
        set_org(r, p, pg, pool[rng.randrange(len(pool))])
        d.anc, p.anc = 0, 1
        doid, poid = d.oid, p.oid
        del r.births[:]
        r.epoch = ctr[0]; ctr[0] += 1
        a, b = (d, p) if rng.randrange(2) == 0 else (p, d)
        r._pair_interact(0, a, b)
        got = [c for par, c in r.births if par == doid]
        lost = any(par == poid for par, c in r.births)
        if got:
            out.append((age, got[0], r._genome(p), state(p)))
        if lost:
            return out, age
        g, st = r._genome(d), state(d)
    return out, None


def run(sp, rule, seed):
    r, g0 = make(sp, rule, seed)
    rng = random.Random(repr(("W2-2-h1", sp, rule, seed)))
    pool = partner_pool(r, rng)
    d = r._place(bytes(r.L), 0); p = r._place(bytes(r.L), 1)
    ctr = [10_000]
    gen = [(g0, (None, 0, 0), -1, True)] * CAP      # generation 0: CAP independent founder lives
    res, tree = [], []
    for k in range(G):
        rows = []
        nxt = []
        for (g, st, par, viacausal) in gen[:CAP]:
            b, died = live(r, d, p, g, st, pool, rng, ctr)
            me = len(tree)
            tree.append(dict(hex=g.hex(), gen=k, parent=par, via_causal=viacausal, births=len(b), causal=sum(c for _, c, _, _ in b),
                             ages=[a for a, _, _, _ in b], causal_flags=[c for _, c, _, _ in b], died=died))
            rows.append(tree[-1])
            nxt += [(cg, cs, me, c) for _, c, cg, cs in b]
        n = len(rows)
        if not n:
            break
        rng.shuffle(nxt)          # follow a random subset of children, not the first-born (avoids an age bias)
        nb = sum(x["births"] for x in rows); nc = sum(x["causal"] for x in rows)
        prof = {f"{lo}-{hi}": sum(lo <= a <= hi for x in rows for a in x["ages"]) for lo, hi in ((1, 1), (2, 3), (4, 6), (7, 12), (13, 30), (31, 999))}
        died = sorted(x["died"] for x in rows if x["died"])
        res.append(dict(gen=k, n=n, births_per_ind=round(nb / n, 3), causal_per_ind=round(nc / n, 3),
                        causal_share=round(nc / nb, 3) if nb else None, zero_birth_share=round(sum(x["births"] == 0 for x in rows) / n, 3),
                        survive_H=round(sum(x["died"] is None for x in rows) / n, 3), birth_age_profile=prof,
                        median_died=died[len(died) // 2] if died else None))
        gen = nxt
    return res, tree


def main():
    t0 = time.process_time()
    out = dict(H=H, CAP=CAP, G=G, runs={})
    for sp in SPECS:
        for rule in ("BASE", "ATOMIC"):
            reps = []
            for seed in SEEDS:
                res, tree = run(sp, rule, 77_000 + seed)
                reps.append(dict(summary=res, tree=tree))
                print(sp[:4], rule, seed, [(x["gen"], x["n"], x["births_per_ind"], x["causal_per_ind"], x["causal_share"], x["zero_birth_share"], x["survive_H"], x["birth_age_profile"]) for x in res],
                      round(time.process_time() - t0), flush=True)
            out["runs"][f"{sp[:4]}_{rule}"] = reps
    out["cpu_s"] = round(time.process_time() - t0, 1)
    (HERE / ("h1_lineage_tree_%s.json" % "_".join(x[:4] for x in SPECS))).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
