"""W2-38 re-screen: the world's own competence code (run_de.competent's two-stage P-11 assay, run_dd.assay_one's
seeds/K1/K2/blank partner) evaluated under four entry contexts, on dumped genomes+registers. Plus the world-rule
conversion rate (predecessor_accepts AND p11.assay pass) of each L organism against realized partners.

Contexts (donor state / partner state; the partner GENOME stays blank as in the frozen screen, the victim half is
randomized by P-11 itself):
  ZERO   (None,0,0) / (None,0,0)               - the frozen screen (must reproduce run_de.competent exactly)
  OWN    donor's carried (regs,fz,fc) / zero    - reading (b)
  REAL   donor's carried / a realized partner state drawn per seed from the dumped population - reading (c)
  INHER  a realized state drawn per seed (what a newborn inherits) / a realized partner state - reading (c')
    python -B rescreen.py replay_ffa6_27000052.json.gz [max_orgs_per_dump]
"""
from __future__ import annotations

import gzip
import hashlib
import json
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CI = HERE.parents[1] / "campaigns" / "npe-arc3-2026-09-28" / "c_a3_internalize"
sys.path.insert(0, str(CI))
import run_ci  # noqa: E402,F401

import world  # noqa: E402
import run_dc  # noqa: E402
import run_dd  # noqa: E402
world.z8 = run_dc.dense_z8()
p11 = world.p11
ZERO = (None, 0, 0)


def st_of(o):
    return (None if o["regs"] is None else list(o["regs"]), o["fz"], o["fc"])


def assay_ctx(R, g, tag, k, donor_st, partner_st_fn):
    """run_dd.assay_one with the entry states made explicit. partner_st_fn(i, side) -> state."""
    n = R["L"]
    tl = world._pow2(2 * n)
    hits = 0
    for i in range(k):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            ps = partner_st_fn(i, side)
            ds = donor_st(i, side)
            sa, sb = (ds, ps) if side == 0 else (ps, ds)
            res = p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb,
                            st_a=(None if sa[0] is None else list(sa[0]), sa[1], sa[2]),
                            st_b=(None if sb[0] is None else list(sb[0]), sb[1], sb[2]),
                            budget=R["slice"], ops_mask=R["ops_mask"], cmr=R["copy_mut"],
                            victim_side=1 - side, seed=("X-DONOR-DISCOVERY", tag, i, side))
            ok = ok or res["pass"]
        hits += ok
    return hits


def competent_ctx(R, g, donor_st, partner_st_fn):
    """run_de.competent, verbatim decision rule, with explicit contexts. Returns (competent, stage2_rate or None)."""
    tag = ("X-DD-ESTABLISH", hashlib.sha256(g).hexdigest()[:16])
    h = assay_ctx(R, g, tag + (1,), run_dd.K1, donor_st, partner_st_fn)
    if not h:
        return False, None
    h2 = assay_ctx(R, g, tag + (2,), run_dd.K2, donor_st, partner_st_fn)
    return h2 / run_dd.K2 >= 0.5, h2 / run_dd.K2


def convert(R, d, p, seed):
    """World rule for one pair (d donor, p victim) with realized genomes and states: interaction as world does it,
    predecessor_accepts on the victim half, then the P-11 assay. Donor side drawn from seed."""
    n = R["L"]
    tl = world._pow2(2 * n)
    rng = random.Random(seed)
    dside = rng.randrange(2)
    gd, gp = bytes.fromhex(d["genome"]), bytes.fromhex(p["genome"])
    ga, gb = (gd, gp) if dside == 0 else (gp, gd)
    sa, sb = (st_of(d), st_of(p)) if dside == 0 else (st_of(p), st_of(d))
    vs = 1 - dside
    kw = dict(n=n, tape_len=tl, ga=ga, gb=gb, st_a=sa, st_b=sb, budget=R["slice"], ops_mask=R["ops_mask"],
              cmr=R["copy_mut"])
    tape, _prov, _lit, wo = p11.interact(world.z8, rng=random.Random(seed + 1), **kw)
    v0 = 0 if vs == 0 else n
    new = bytes(tape[v0:v0 + n])
    fid_other, fid_self = world._fidelity(gd, new), world._fidelity(gp, new)
    acc = p11.predecessor_accepts(fid_other, fid_self, wo[dside], n)
    if not acc:
        return False, False
    res = p11.assay(world.z8, victim_side=vs, seed=("W2-38-CONV", seed), **kw)
    return True, res["pass"]


def main(path, cap, epochs=None):
    t0 = time.time()
    with gzip.open(path, "rt") as f:
        rep = json.load(f)
    R = rep["runner"]
    out = {"cell": rep["cell"], "seed": rep["seed"], "replay_identical": rep["replay_identical"], "cap": cap, "dumps": []}
    for dmp in rep["dumps"]:
        if epochs and dmp["epoch"] not in epochs:
            continue
        orgs = dmp["orgs"]
        states = [st_of(o) for o in orgs]
        L = [o for o in orgs if o["inL"]]
        sel = sorted(L, key=lambda o: hashlib.sha256(("W2-38", rep["seed"], dmp["epoch"], o["oid"]).__repr__().encode()).digest())[:cap]
        rows = []
        zcache = {}
        for o in sel:
            g = bytes.fromhex(o["genome"])
            own = st_of(o)
            key = int(hashlib.sha256(repr((rep["seed"], dmp["epoch"], o["oid"])).encode()).hexdigest()[:12], 16)

            def draw(i, side, salt):
                return states[random.Random(key + 7919 * i + 104729 * side + salt).randrange(len(states))]
            if g not in zcache:
                zcache[g] = competent_ctx(R, g, lambda i, s: ZERO, lambda i, s: ZERO)
            z = zcache[g]
            b = competent_ctx(R, g, lambda i, s: own, lambda i, s: ZERO)
            c = competent_ctx(R, g, lambda i, s: own, lambda i, s: draw(i, s, 1))
            ci = competent_ctx(R, g, lambda i, s: draw(i, s, 2), lambda i, s: draw(i, s, 3))
            conv = []
            for j in range(8):
                prng = random.Random(key + 31 * j)
                p = orgs[prng.randrange(len(orgs))]
                if p["oid"] == o["oid"]:
                    p = orgs[(orgs.index(p) + 1) % len(orgs)]
                conv.append(convert(R, o, p, key + 1000003 * j))
            rows.append({"oid": o["oid"], "zero_world": o["zero_competent"], "zero": z[0], "zero_rate": z[1],
                         "own": b[0], "own_rate": b[1], "real": c[0], "real_rate": c[1], "inher": ci[0],
                         "inher_rate": ci[1], "regs_none": o["regs"] is None,
                         "conv_accept": sum(a for a, _ in conv), "conv_p11": sum(p for _, p in conv), "conv_n": len(conv)})
        out["dumps"].append({"epoch": dmp["epoch"], "n_alive": len(orgs), "n_L": len(L), "n_screened": len(sel),
                             "distinct_genomes_L": len({o["genome"] for o in L}), "rows": rows})
        print(dmp["epoch"], len(sel), round(time.time() - t0, 1), flush=True)
    out["wall_s"] = round(time.time() - t0, 1)
    (HERE / ("rescreen_%s_%d_%s.json" % (rep["cell"], rep["seed"], "-".join(map(str, sorted(epochs or []))) or "all"))).write_text(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10**9,
         {int(x) for x in sys.argv[3].split(",")} if len(sys.argv) > 3 else None)
