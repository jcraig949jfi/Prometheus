"""L2 -- NPE "P-11 causal copy" certificate (PAIR_EXECUTION). Label spec + runner.

WHAT THE LABEL IS (provenance): an event is P-11 causal when, re-executed from its EXACT recorded pre-interaction state
(both genomes, both register files and flags), the donor rebuilds a randomized victim half to >= 0.90 positional
fidelity in >= 2 of 3 draws, >= 90% of the donor-directed changes authored by the donor, and a donor-disabled control
stays < 0.90 (roles/Nestor/campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md, p11.py). The 57 surviving runs of the
1,031 (P11_REASSAY.jsonl, first certified event per run, donor genome recorded) are the objects here. The certified
unit is thus an (event, register state) pair; the label is then carried by a GENOME and a LINEAGE (depth, heredity).

CLAIMED PROPERTY: the donor genome rebuilds a random partner half as itself -- in register states the organism can
actually reach (fresh = newborn, and after 1-8 ordinary pair interactions with random partners, sides drawn at random,
registers carried as the world carries them), on either side of the tape. Behaviour per environment = the P-11 assay
itself (p11.assay, unmodified, NPE's own z8 substrate copy) with the donor in that register state.
EXPECTED MECHANISM: copying -- the child's bytes are caused by the donor's bytes. Intervention: do(genome[p] := b) for
every position (2 random b each), same warm-up and victim seeds; copying predicts final victim[p] == b. Painting (code
that writes its own constant pattern, e.g. the 0x36 'LD (HL),n' homopolymers FR-011 found) predicts no transmission.
Mechanism OK iff transmission T >= 0.5. bits_transmitted = 8 x positions carried in both draws.
STRUCTURE: a copy routine is present (ED B0 / ED B8 in BLOCK cells; LD A,(HL) 7E + LD (DE),A 12 bytes in BYTEWISE).

    python3 l2_npe_p11.py [--workers 4]      -> L2_rows.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recert as R  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
FOR = os.path.join(REPO, "roles/Nestor/campaigns/z80atlas-forensics-2026-09-23")
VER = os.path.join(REPO, "roles/Nestor/campaigns/z80atlas-verify-2026-09-22")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


z8 = _load("z8", os.path.join(FOR, "substrate", "z8.py"))           # the substrate the P-11 reassay ran on
constants = _load("constants", os.path.join(VER, "constants.py"))
p11 = _load("p11", os.path.join(VER, "p11.py"))

REP_LEN = {"Z8_64": 64, "Z8_32": 32, "Z8_SHARED": 96, "Z8_SEPARATED": 96, "Z8_SLOTTED": 64}   # substrate/world.py:37
MUT_RATE = {"LOW": 0.002, "MID": 0.01, "HIGH": 0.04}                                          # substrate/world.py:38
SLICE = {"S": 220, "M": 300, "L": 360}                                                       # substrate/grammar.py:231
SIDES = (0, 1)
WARM = (0, 1, 2, 4, 8)
WSEEDS = (0, 1)
T_MIN = 0.5
FRESH = (None, 0, 0)


def _seed(*parts) -> int:
    return int(hashlib.sha256(repr(parts).encode()).hexdigest()[:12], 16)


def ops_mask(c: dict) -> int:
    """substrate/world.py _ops_mask, for a PAIR_EXECUTION cell."""
    m = 0x08
    if c["reproduction"] in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE"):
        m |= 0x01
    if c["reproduction"] == "ENDOGENOUS_PARTIAL":
        m |= 0x10
    if c["self_location"] == "PRIMITIVE":
        m |= 0x02
    if c["self_location"] == "PC_RELATIVE":
        m |= 0x04
    if c["copy_primitive"] == "BLOCK":
        m |= 0x20
    return m


def pow2(n):
    p = 1
    while p < n:
        p *= 2
    return p


class Obj:
    __slots__ = ("oid", "genome", "n", "tape_len", "mask", "cmr", "budget", "cell", "prov", "labelled")

    def __init__(self, oid, genome, cell, tier, prov, labelled=True, budget=None, cmr=None, mask=None):
        self.oid, self.genome, self.cell, self.prov, self.labelled = oid, genome, cell, prov, labelled
        self.n = REP_LEN[cell["representation"]]
        self.tape_len = pow2(2 * self.n)
        self.mask = ops_mask(cell) if mask is None else mask
        self.cmr = MUT_RATE[cell["mutation_rate"]] if cmr is None else cmr
        self.budget = SLICE[tier] if budget is None else budget


def pair_run(o, genome, partner, donor_side, st_donor, rng):
    """One ordinary pair interaction (a runs first, then b), as world._pair_epoch. Returns (tape, donor state after)."""
    n = o.n
    tape = bytearray(o.tape_len)
    ga, gb = (genome, partner) if donor_side == 0 else (partner, genome)
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    st_out = None
    for who, start in ((0, 0), (1, n)):
        ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=rng, copy_mut_rate=o.cmr, sense=who)
        st = st_donor if who == donor_side else FRESH
        ctx.regs, ctx.fz, ctx.fc = (list(st[0]) if st[0] is not None else None), st[1], st[2]
        z8.run(ctx, start, o.budget, ops_enabled=o.mask)
        if who == donor_side:
            st_out = (ctx.regs, ctx.fz, ctx.fc)
    return tape, st_out


def warm_state(o, genome, env):
    """Register state after `warm` ordinary interactions with random partners on random sides (genome reset each time:
    the certified genome is what is being tested; only the reachable register state is carried)."""
    st = FRESH
    r = random.Random(_seed("warm", o.oid, env["ws"]))
    for i in range(env["warm"]):
        partner = bytes(r.randrange(256) for _ in range(o.n))
        side = r.randrange(2)
        _, st = pair_run(o, genome, partner, side, st, random.Random(_seed("wrng", o.oid, env["ws"], i)))
    return st


def environments(o):
    return [{"side": s, "warm": w, "ws": k} for s in SIDES for w in WARM for k in (WSEEDS if w else (0,))]


def assay(o, genome, env):
    st = warm_state(o, genome, env)
    vs = 1 - env["side"]                       # victim side
    dummy = bytes(o.n)                         # the victim's bytes are replaced by the assay's random draws
    ga, gb = (dummy, genome) if vs == 0 else (genome, dummy)
    st_a, st_b = (FRESH, st) if vs == 0 else (st, FRESH)
    return p11.assay(z8, n=o.n, tape_len=o.tape_len, ga=ga, gb=gb, st_a=st_a, st_b=st_b, budget=o.budget,
                     ops_mask=o.mask, cmr=o.cmr, victim_side=vs, seed=("recert", o.oid, env["side"], env["warm"], env["ws"]))


def behavioural(o, env):
    a = assay(o, o.genome, env)
    return {"pass": bool(a["pass"]), "draws_passed": a["draws_passed"],
            "fid_final_mean": round(sum(d["fid_final"] for d in a["draws"]) / len(a["draws"]), 3),
            "C2": a["C2_majority"], "C4": a["C4_majority"], "C5": a["C5_majority"]}


def structural(o):
    g = o.genome
    block = any(g[i] == 0xED and g[i + 1] in (0xB0, 0xB8) for i in range(len(g) - 1))
    loop = 0x7E in g and 0x12 in g
    ok = block if o.cell["copy_primitive"] == "BLOCK" else loop
    return {"ok": bool(ok), "has_ED_B0_B8": block, "has_7E_and_12": loop, "copy_primitive": o.cell["copy_primitive"],
            "dominant_byte_share": round(R.dominant_share(g), 4), "dominant_byte": "%02x" % max(set(g), key=g.count),
            "entropy_bits_per_byte": round(R.entropy_bits(g), 3), "near_homopolymer": R.dominant_share(g) >= 0.8}


def transmission(o, env):
    vs = 1 - env["side"]
    v0, d0 = (0, o.n) if vs == 0 else (o.n, 0)
    vict = bytes(random.Random(_seed("tv", o.oid)).randrange(256) for _ in range(o.n))
    r = random.Random(_seed("T", o.oid))
    carried = [0] * o.n
    tot = 0
    for p in range(o.n):
        for _ in range(2):
            b = r.randrange(255)
            b = b if b < o.genome[p] else b + 1
            g = bytearray(o.genome); g[p] = b; g = bytes(g)
            st = warm_state(o, g, env)
            tape, _ = pair_run(o, g, vict, env["side"], st, random.Random(_seed("trng", o.oid)))
            carried[p] += tape[v0 + p] == b
            tot += 1
    return sum(carried) / tot, 8 * sum(1 for c in carried if c == 2)


def causal(o, beh):
    envs = [e for e, rr in beh["_all"] if rr["pass"]]
    fresh = [rr["pass"] for e, rr in beh["_all"] if e["warm"] == 0]
    base = {"fresh_state_pass_rate": round(sum(fresh) / max(1, len(fresh)), 4)}
    if not envs:
        return dict(base, ok=None, why="no behaviour to intervene on")
    env = envs[0]
    T, bits = transmission(o, env)
    return dict(base, ok=T >= T_MIN, intervention_env=env, transmission=round(T, 4), bits_transmitted=bits,
                info_above_homopolymer=bits > 0)


LABEL = R.Label(
    name="NPE P-11 causal copy (PAIR_EXECUTION donor)",
    claimed_property="the certified donor genome rebuilds a randomized partner half as itself (P-11 assay passes) from "
                     "register states it can reach (fresh; after 1-8 ordinary interactions), on either tape side",
    expected_mechanism="copying: do(genome[p]=b) -> victim[p]=b for >= 50% of edits",
    provenance=lambda o: o.prov, structural=structural, environments=environments, behavioural=behavioural,
    causal=causal, obj_id=lambda o: o.oid, labelled=lambda o: o.labelled, min_rate=0.5,
    notes={"sides": SIDES, "warm": WARM, "warm_seeds": WSEEDS, "T_min": T_MIN,
           "substrate": "roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/substrate/z8.py",
           "assay": "roles/Nestor/campaigns/z80atlas-verify-2026-09-22/p11.py (unmodified)"})


def load():
    objs = []
    for line in open(os.path.join(FOR, "P11_REASSAY.jsonl")):
        r = json.loads(line)
        if not r.get("n_p11_events"):
            continue
        e = r["first_p11_event"]
        prov = {"label_then": "P-11 causal pair event (first certified event of the run)", "run_id": r["run_id"],
                "draws_passed_then": e["draws_passed"], "fid_other_then": e["fid_other"], "donor_wrote_then": e["donor_wrote"],
                "max_p11_depth_then": r["max_p11_depth"], "n_p11_events_then": r["n_p11_events"],
                "n_pred_events_then": r["n_pred_events"], "cell": {k: r["cell"][k] for k in (
                    "representation", "copy_primitive", "self_location", "atlas_axis", "structure", "pressure", "mutation_rate")}}
        objs.append(Obj("N:" + r["run_id"], bytes.fromhex(e["donor_genome"]), r["cell"], r["tier"], prov))
    return objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "L2_rows.json"))
    a = ap.parse_args()
    t0 = time.time()
    objs = load()[:a.limit] if a.limit else load()
    print("L2: %d P-11-certified donor genomes" % len(objs), flush=True)
    rows = R.run(LABEL, objs, a.workers)
    extra = {"summary_by_copy_primitive": R.summarise(rows, lambda r: r["then"]["cell"]["copy_primitive"]),
             "wall_s": round(time.time() - t0, 1)}
    R.write(a.out, LABEL, rows, extra)
    print(json.dumps(extra, indent=1))


if __name__ == "__main__":
    main()
