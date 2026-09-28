"""Self-location transplant tests (Nestor delegate, npe-arc3-2026-09-28). Declarations: DECLARATIONS.md.

    python selfloc.py sample     -> sample.json      (stratified sample; seed 20260928)
    python selfloc.py validate   -> validation.json  (GP11 in the standard layout == p11.assay, exactly)
    python selfloc.py run        -> results.jsonl    (all transplant conditions + self-state measure; 2 procs)

Read-only over the corpus and W1 code; writes only into this directory. At most 2 worker processes.
"""
from __future__ import annotations

import collections
import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[2]
CORPUS = CAMP / "npe-p2-endogenous-heredity-2026-09-27" / "delegates" / "corpus"
sys.path.insert(0, str(CORPUS))
import corpus_analysis as ca  # noqa: E402  (inserts the W1 / c9x / z80atlas paths; no writes on import)

NPROC = 2
K = 12                 # seeds per transplant condition
SS_SEEDS = 10          # self-state measure seeds per (side, k)
SS_KMAX = 2
SAMPLE_SEED = 20260928
N_NONSELF = 300
FRESH = (None, 0, 0)
B, Cr, D, E, H, L, A = 0, 1, 2, 3, 4, 5, 7


# ------------------------------------------------------------------ sample
def build_sample():
    rows = [json.loads(x) for x in open(CORPUS / "q1_partial.jsonl")]
    comp = [r for r in rows if r["rate_full"] >= 0.5]
    for r in comp:
        r["self_dep"] = r["rate_noself"] < 0.5
        r["origin_exp"] = r["origin_run"].split("/")[0]
    sd = [r for r in comp if r["self_dep"]]
    donors = [r for r in comp if r["nocopy_donor"] is not None and not r["self_dep"]]
    rest = [r for r in comp if r["nocopy_donor"] is None and not r["self_dep"]]
    need = N_NONSELF - len(donors)
    strata = collections.defaultdict(list)
    for r in rest:
        strata[(r["cell"], r["vm"], r["origin_exp"])].append(r)
    q = 0
    while sum(min(len(v), q + 1) for v in strata.values()) <= need and any(len(v) > q for v in strata.values()):
        q += 1
    rng = random.Random(SAMPLE_SEED)
    pick = []
    for k in sorted(strata):
        v = sorted(strata[k], key=lambda r: r["hex"])
        pick += v if len(v) <= q else rng.sample(v, q)
    # top up to exactly `need` from leftovers (deterministic), if water-filling left a remainder
    left = sorted([r for r in rest if r not in pick], key=lambda r: r["hex"])
    rng.shuffle(left)
    pick += left[:max(0, need - len(pick))]
    out = sd + donors + pick
    meta = {"n": len(out), "self_dep": len(sd), "first_donors_selfindep": len(donors),
            "stratified": len(pick), "quota_q": q,
            "strata": {"|".join(k): [len(v), min(len(v), q)] for k, v in sorted(strata.items())}}
    (HERE / "sample.json").write_text(json.dumps({"meta": meta, "genomes": out}))
    print(json.dumps(meta, indent=1))


# ------------------------------------------------------------------ generalized P-11
def _place(tape, off, b):
    T = len(tape)
    for i, x in enumerate(b):
        tape[(off + i) % T] = x


def _run_once(z8, T, n, donor, d_off, v_off, vb, donor_first, dsense, vsense, dstate, budget, ops, cmr, rng,
              entry=0, v_exec=True, disabled=False, vstate=FRESH):
    tape = bytearray(T)
    _place(tape, d_off, donor)
    _place(tape, v_off, vb)
    prov, lit = bytearray(T), bytearray(T)
    ex = [("d", d_off, dsense, dstate, entry), ("v", v_off, vsense, vstate, 0)]
    if not donor_first:
        ex.reverse()
    for who, base, sense, st, ent in ex:
        if who == "v" and not v_exec:
            continue
        pol, flo, fhi = z8.ARENA, 0, 0
        if disabled and who == "d":
            if base + n <= T:
                pol = z8.OWN
            else:                                  # wrapped own span: [base, T) as own, [0, base+n-T) as free
                pol, flo, fhi = z8.FREE, 0, base + n - T
        ctx = z8.Ctx(tape, base, n, policy=pol, rng=rng, copy_mut_rate=cmr, sense=sense, free_lo=flo, free_hi=fhi)
        regs, fz, fc = st
        ctx.regs, ctx.fz, ctx.fc = (list(regs) if regs is not None else None), fz, fc
        ctx.prov, ctx.prov_lit, ctx.who = prov, lit, (1 if who == "d" else 2)
        z8.run(ctx, (base + ent) % T, budget, ops_enabled=ops)
    return tape, prov


def gp11(world, z8, *, T, n, donor, d_off, v_off, donor_first, dsense, vsense, dstate, budget, ops, cmr, seed,
         victim="random", entry=0, v_exec=True, draws=3):
    import p11
    fid = p11.fidelity
    npass, pself = 0, 0
    for k in range(draws):
        if victim == "random":
            vr = random.Random(p11.event_seed(seed, "victim", k))
            vb = bytes(vr.randrange(256) for _ in range(n))
        elif victim == "blank":
            vb = bytes(n)
        else:
            vb = bytes(donor)
        cseed = p11.event_seed(seed, "copy", k)
        kw = dict(z8=z8, T=T, n=n, donor=donor, d_off=d_off, v_off=v_off, vb=vb, donor_first=donor_first,
                  dsense=dsense, vsense=vsense, dstate=dstate, budget=budget, ops=ops, cmr=cmr, entry=entry,
                  v_exec=v_exec)
        tape, prov = _run_once(rng=random.Random(cseed), **kw)
        final = bytes(tape[(v_off + i) % T] for i in range(n))
        dfinal = bytes(tape[(d_off + i) % T] for i in range(n))
        if victim == "self":
            pself += fid(donor, final) >= 0.9 and fid(donor, dfinal) >= 0.9
            continue
        Dx = [i for i in range(n) if vb[i] != donor[i] and final[i] == donor[i]]
        auth = sum(1 for i in Dx if prov[(v_off + i) % T] == 1)
        tape_d, _ = _run_once(rng=random.Random(cseed), disabled=True, **kw)
        fdis = fid(donor, bytes(tape_d[(v_off + i) % T] for i in range(n)))
        c2 = fid(donor, final) >= 0.90
        c4 = bool(Dx) and auth / len(Dx) >= 0.90
        c5 = fdis < 0.90
        npass += c2 and c4 and c5
    if victim == "self":
        return pself
    return npass >= 2


# ------------------------------------------------------------------ conditions
def regs(**kv):
    r = [0] * 8
    for name, v in kv.items():
        if name == "HL":
            r[H], r[L] = (v >> 8) & 0xFF, v & 0xFF
        elif name == "DE":
            r[D], r[E] = (v >> 8) & 0xFF, v & 0xFF
        else:
            r[{"B": B, "C": Cr, "D": D, "E": E, "H": H, "L": L, "A": A}[name]] = v & 0xFF
    return (r, 0, 0)


def rot(g, r):
    n = len(g)
    out = bytearray(n)
    for i in range(n):
        out[(i + r) % n] = g[i]
    return bytes(out)


T1_D = (1, 4, 8, 16, 32, 48, 64)
ROTS = (1, 4, 16, -4)


def conditions(h):
    """name -> (overrides of the REF spec, per-seed state factory or None)."""
    hf = h == 0                         # home order: side 0 runs first
    hs = 0 if h == 0 else 1
    ref = dict(T=128, d_off=h, v_off=(h + 64) % 128, donor_first=hf, dsense=hs, vsense=1 - hs)
    C = {"REF": dict(ref)}
    o = 64 - h
    C["STD_OTHER"] = dict(T=128, d_off=o, v_off=(o + 64) % 128, donor_first=not hf, dsense=1 - hs, vsense=hs)
    for d in T1_D:
        C["T1_d%d" % d] = dict(ref, d_off=(h + d) % 128, v_off=(h + d + 64) % 128)
    C["G256_ADJ"] = dict(ref, T=256, v_off=h + 64)
    C["G256_HALF"] = dict(ref, T=256, v_off=h + 128)
    C["G256_HI"] = dict(ref, T=256, d_off=128 + h, v_off=(192 + h) % 256)
    C["G192_ADJ"] = dict(ref, T=192, v_off=h + 64)
    C["I_CONST55"] = dict(ref, dstate=([0x55] * 8, 0, 0))
    C["I_CONSTFF"] = dict(ref, dstate=([0xFF] * 8, 0, 0))
    C["I_RAND"] = dict(ref, dstate="RAND")
    C["I_HL_PARTNER"] = dict(ref, dstate=regs(HL=h + 64))
    C["I_SELFPTRS"] = dict(ref, dstate=regs(HL=h, DE=h + 64))
    k = h + 32
    dsp = dict(ref, d_off=k % 128, v_off=(k + 64) % 128)
    C["D32_HL_SELF"] = dict(dsp, dstate=regs(HL=k))
    C["D32_DE_PARTNER"] = dict(dsp, dstate=regs(DE=(k + 64) % 128))
    C["D32_HLDE"] = dict(dsp, dstate=regs(HL=k, DE=(k + 64) % 128))
    C["D32_PTRSHIFT"] = dict(dsp, dstate=regs(L=32, E=32))
    C["P_BLANK"] = dict(ref, victim="blank")
    C["P_NOEXEC"] = dict(ref, v_exec=False)
    C["ORDER_FLIP"] = dict(ref, donor_first=not hf)
    C["SENSE_FLIP"] = dict(ref, dsense=1 - hs, vsense=hs)
    C["P_SELF"] = dict(ref, victim="self")
    for r in ROTS:
        C["ROT%+d_BASE" % r] = dict(ref, rotate=r, entry=0)
        C["ROT%+d_FOLLOW" % r] = dict(ref, rotate=r, entry=r % 64)
    return C


def rate(world, rr, g, spec, hexg):
    z8 = world.z8
    spec = dict(spec)
    r_ = spec.pop("rotate", None)
    donor = rot(g, r_) if r_ is not None else g
    st = spec.pop("dstate", FRESH)
    hits = 0
    for i in range(K):
        s = st
        if st == "RAND":
            q = random.Random(json.dumps(["SELFLOC-RAND", hexg, i]))
            s = ([q.randrange(256) for _ in range(8)], q.randrange(2), q.randrange(2))
        hits += gp11(world, z8, n=rr.L, donor=donor, dstate=s, budget=rr.t["slice"], ops=rr._ops_mask(),
                     cmr=rr.copy_mut, seed=("SELFLOC", hexg, i), **spec)
    return hits / (3 * K) if spec.get("victim") == "self" else hits / K


# ------------------------------------------------------------------ self-state measure (run_ss.py logic)
def selfstate(world, rr, g, hexg):
    import p11
    import run_nc
    n = rr.L
    blank = bytes(n)
    tl = world._pow2(2 * n)
    rates = []
    for k in range(SS_KMAX + 1):
        hits = tot = 0
        for sd in range(SS_SEEDS):
            for side in (0, 1):
                st = FRESH
                for j in range(k):
                    ga, gb = (g, blank) if side == 0 else (blank, g)
                    mem = bytearray(tl)
                    mem[0:n] = ga
                    mem[n:2 * n] = gb
                    rng = random.Random(p11.event_seed("SELFLOC-SS-pre", hexg, k, sd, side, j))
                    dctx = None
                    for who, start in ((0, 0), (1, n)):
                        stw = st if who == side else FRESH
                        c = world.z8.Ctx(mem, start, n, policy=world.z8.ARENA, rng=rng, copy_mut_rate=rr.copy_mut,
                                         sense=who)
                        c.regs, c.fz, c.fc = (None if stw[0] is None else list(stw[0])), stw[1], stw[2]
                        world.z8.run(c, start, rr.t["slice"], ops_enabled=rr._ops_mask())
                        if who == side:
                            dctx = c
                    st = (None if dctx.regs is None else list(dctx.regs), dctx.fz, dctx.fc)
                tot += 1
                hits += run_nc.copies(world, rr, g, st, blank, FRESH, side, ("SELFLOC-SS", hexg, k, sd, side))
        rates.append(round(hits / tot, 4))
    return rates


# ------------------------------------------------------------------ jobs
def job(e):
    world, rr = ca.env(e["vm"], e["cell"])
    g = bytes.fromhex(e["hex"])
    s0 = rate(world, rr, g, dict(T=128, d_off=0, v_off=64, donor_first=True, dsense=0, vsense=1), e["hex"])
    s1 = rate(world, rr, g, dict(T=128, d_off=64, v_off=0, donor_first=False, dsense=1, vsense=0), e["hex"])
    h = 0 if s0 >= s1 else 64
    res = {}
    for name, spec in conditions(h).items():
        if name == "REF":
            res[name] = s0 if h == 0 else s1
        elif name == "STD_OTHER":
            res[name] = s1 if h == 0 else s0
        else:
            res[name] = rate(world, rr, g, spec, e["hex"])
    ss = selfstate(world, rr, g, e["hex"])
    return {"hex": e["hex"], "vm": e["vm"], "cell": e["cell"], "origin_run": e["origin_run"],
            "nocopy_donor": e["nocopy_donor"], "self_dep": e["self_dep"], "rate_full": e["rate_full"],
            "rate_noself": e["rate_noself"], "home": h, "rates": res, "ss_rates": ss}


def run():
    S = json.loads((HERE / "sample.json").read_text())["genomes"]
    out = HERE / "results.jsonl"
    done = set()
    if out.exists():
        done = {json.loads(x)["hex"] + json.loads(x)["cell"] for x in open(out)}
    todo = [e for e in S if e["hex"] + e["cell"] not in done]
    print("todo", len(todo), flush=True)
    with mp.Pool(NPROC) as pool, open(out, "a") as f:
        for i, rec in enumerate(pool.imap_unordered(job, todo)):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if i % 20 == 0:
                print(i, flush=True)


# ------------------------------------------------------------------ validation
def validate():
    import p11
    S = json.loads((HERE / "sample.json").read_text())["genomes"]
    rng = random.Random(7)
    pick = rng.sample(S, 48)
    rows, agree, tot = [], 0, 0
    for e in pick:
        world, rr = ca.env(e["vm"], e["cell"])
        g = bytes.fromhex(e["hex"])
        n, tl = rr.L, 128
        for i in range(3):
            for side in (0, 1):
                seed = ("X-DONOR-DISCOVERY", ("SELFLOC-VAL", e["hex"]), i, side)
                ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
                ref = p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                budget=rr.t["slice"], ops_mask=rr._ops_mask(), cmr=rr.copy_mut,
                                victim_side=1 - side, seed=seed)["pass"]
                mine = gp11(world, world.z8, T=128, n=n, donor=g, d_off=64 * side, v_off=64 * (1 - side),
                            donor_first=side == 0, dsense=side, vsense=1 - side, dstate=FRESH,
                            budget=rr.t["slice"], ops=rr._ops_mask(), cmr=rr.copy_mut, seed=seed)
                tot += 1
                agree += ref == mine
                rows.append([e["hex"][:12], i, side, ref, mine])
    res = {"trials": tot, "agree": agree, "p11_pass": sum(r[3] for r in rows), "rows": rows}
    (HERE / "validation.json").write_text(json.dumps(res))
    print(tot, agree, res["p11_pass"])


if __name__ == "__main__":
    {"sample": build_sample, "validate": validate, "run": run}[sys.argv[1]]()
