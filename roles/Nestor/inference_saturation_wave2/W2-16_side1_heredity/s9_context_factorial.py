"""Step 9: why does the copier's own code, executed from its own entry by the PARTNER's context, damage it?
The partner context differs from the copier's own in three ways: base (SELF returns HL=0 instead of n), sense
(SENSE returns 0 instead of 1), and registers/flags (inherited from ~random execution, not FRESH). Factorial: run ONLY
one context starting at pc = n (the copier's entry) on [64 x HALT | G], with base in {0 (partner), n (own)},
sense in {0, 1}, regs in {FRESH, 30 random register files + flags}. Outcome: copier half intact afterwards and
side-0 half >= 0.9 identical to G (good copy)."""
import json, pathlib, collections, random
from _env import A, ROWS
import p11

side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
out = {}
agg = collections.defaultdict(collections.Counter)
for r in side1:
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]
    res = {}
    rr = random.Random("W2-16-regs-" + r["key"])
    regsets = [None] + [([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2)) for _ in range(30)]
    for base in (0, n):
        for sense in (0, 1):
            for ri, rs in enumerate(regsets):
                tape = bytearray(P["tape_len"]); tape[0:n] = bytes([0x76]) * n; tape[n:2 * n] = G
                ctx = z.Ctx(tape, base, n, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=sense)
                if rs is None:
                    ctx.regs, ctx.fz, ctx.fc = None, 0, 0
                else:
                    ctx.regs, ctx.fz, ctx.fc = list(rs[0]), rs[1], rs[2]
                z.run(ctx, n, P["budget"], ops_enabled=P["mask"])
                intact = bytes(tape[n:2 * n]) == G
                good = p11.fidelity(G, bytes(tape[0:n])) >= 0.9
                key = "base%s_sense%d_%s" % ("0" if base == 0 else "n", sense, "FRESH" if rs is None else "RANDREGS")
                c = res.setdefault(key, collections.Counter())
                c["n"] += 1; c["intact"] += intact; c["good"] += good
                agg[key]["n"] += 1; agg[key]["intact"] += intact; agg[key]["good"] += good
    out[r["key"]] = {k: dict(v) for k, v in res.items()}
    print(r["key"], {k: (v["good"], v["intact"], v["n"]) for k, v in res.items()})
out["_aggregate"] = {k: dict(v) for k, v in agg.items()}
print(json.dumps(out["_aggregate"], indent=0))
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
