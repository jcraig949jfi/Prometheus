"""W2-12 step 4: static test of the kin-pairing route. No world run: single pair interactions through
p11.interact (the world's own pair-tape code path re-executed on a private tape), stock z8.

Question: 7ae3 at side 0 is overwritten ("hijacked") by a random partner in ~40-60% of interactions.
Is it overwritten when the partner is a copy of itself (or a lightly mutated copy)?  If kin pairing
protects, k founders share protection (a candidate superadditive route); its size scales with the
kin share of the population, which is ~k/256 early.

Outcome per interaction (half = the 7ae3 half at the stated side, final tape, before world _mutate):
    kept   : fidelity(final half, 7ae3) >= 0.9
    lost   : < 0.9
    bytes  : # positions of the 7ae3 half that changed
Register contexts: ZERO (fresh, regs None) and CARRIED (regs left by a previous 7ae3-vs-random
interaction at the same side, the state an established member typically carries).
"""
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
sys.path[:0] = [str(NESTOR / "campaigns/c9x-explore-2026-09-24/x_donor_swap"),
                str(NESTOR / "campaigns/z80atlas-verify-2026-09-22")]
import world  # noqa: E402
import z8  # noqa: E402
import p11  # noqa: E402
import run_ds  # noqa: E402

SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
G = run_ds.donor_genome()
ARM = run_ds.cells()[SPEC]
R0 = world.Runner(dict(ARM["cell"], atlas_axis="NONE"), 1, tier=ARM["tier"])
N = R0.L
KW = dict(n=N, tape_len=world._pow2(2 * N), budget=R0.t["slice"], ops_mask=R0._ops_mask())
OPERAND_POS = [i for i in range(N) if i not in set(R0._boundaries(G))]
ZERO = (None, 0, 0)
TRIALS = 400


def interact(ga, gb, sa, sb, seed, cmr):
    tape, prov, lit, wo = p11.interact(z8, ga=ga, gb=gb, st_a=sa, st_b=sb, rng=random.Random(seed), cmr=cmr, **KW)
    return bytes(tape[0:N]), bytes(tape[N:2 * N]), wo


def carried_state(side, seed):
    """Run the world's Ctx on a 7ae3-vs-random pair to obtain the regs 7ae3 carries afterwards."""
    rng = random.Random(seed)
    pb = bytes(rng.randrange(256) for _ in range(N))
    tape = bytearray(KW["tape_len"])
    ga, gb = (G, pb) if side == 0 else (pb, G)
    tape[0:N], tape[N:2 * N] = ga, gb
    st = None
    for who, start in ((0, 0), (1, N)):
        ctx = z8.Ctx(tape, start, N, policy=z8.ARENA, rng=rng, copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        ctx.prov, ctx.prov_lit, ctx.who = bytearray(len(tape)), bytearray(len(tape)), who + 1
        z8.run(ctx, start, KW["budget"], ops_enabled=KW["ops_mask"])
        if who == side:
            st = (list(ctx.regs) if ctx.regs is not None else None, ctx.fz, ctx.fc)
    return st


def mutant(rng, m):
    g = bytearray(G)
    for i in rng.sample(OPERAND_POS, m):
        g[i] = rng.randrange(256)
    return bytes(g)


def partner(kind, rng):
    if kind == "random":
        return bytes(rng.randrange(256) for _ in range(N))
    if kind == "self_exact":
        return G
    if kind.startswith("self_mut"):
        return mutant(rng, int(kind[len("self_mut"):]))
    raise KeyError(kind)


def run(cmr):
    out = {}
    for side in (0, 1):
        for ctxname in ("ZERO", "CARRIED"):
            for kind in ("random", "self_exact", "self_mut1", "self_mut2", "self_mut4"):
                for pctx in ("ZERO", "CARRIED"):
                    if kind == "random" and pctx == "CARRIED":
                        continue
                    rng = random.Random(("W2-12", side, ctxname, kind, pctx).__repr__())
                    kept = bytes_changed = partner_became_7ae3 = 0
                    for t in range(TRIALS):
                        pb = partner(kind, rng)
                        s_me = ZERO if ctxname == "ZERO" else carried_state(side, ("cs", side, t).__repr__())
                        s_pa = ZERO if pctx == "ZERO" else carried_state(1 - side, ("cp", side, t).__repr__())
                        ga, gb = (G, pb) if side == 0 else (pb, G)
                        sa, sb = (s_me, s_pa) if side == 0 else (s_pa, s_me)
                        h0, h1, wo = interact(ga, gb, sa, sb, ("int", side, t).__repr__(), cmr)
                        mine, theirs = (h0, h1) if side == 0 else (h1, h0)
                        kept += p11.fidelity(mine, G) >= 0.9
                        bytes_changed += sum(1 for i in range(N) if mine[i] != G[i])
                        partner_became_7ae3 += (p11.fidelity(theirs, G) >= 0.9 and p11.fidelity(pb, G) < 0.9)
                    key = "side%d|me_%s|partner_%s|pctx_%s" % (side, ctxname, kind, pctx)
                    out[key] = {"trials": TRIALS, "kept": kept, "lost": TRIALS - kept,
                                "lost_share": round(1 - kept / TRIALS, 4),
                                "mean_bytes_changed": round(bytes_changed / TRIALS, 3),
                                "random_partner_converted_to_7ae3": partner_became_7ae3 if kind == "random" else None}
                    print(key, out[key], flush=True)
    return out


if __name__ == "__main__":
    res = {"genome": G.hex(), "n": N, "ops_mask": KW["ops_mask"], "budget": KW["budget"],
           "operand_positions": OPERAND_POS, "cmr0": run(0.0), "cmr_world": None}
    res["cmr_world_value"] = R0.copy_mut
    res["cmr_world"] = run(R0.copy_mut)
    (HERE / "kin_hijack.json").write_text(json.dumps(res, indent=1))
