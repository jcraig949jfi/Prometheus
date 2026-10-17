"""B118h -- what do the evolved type readers DO? (descriptive; single process)
For each genome, on the B118d held-out set (12 worlds x 8 episodes): count harvests on SAFE vs TOXIC pools
(a harvest = an action on channel 0 at a node holding that pool with amount > 0) and moves.
Reference: GEN3 (harvests both kinds) and CHK3 (should harvest ~0 toxic).
"""
import json
import sys
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b118c_interleaved import chk, gen
from archaeon.beta.b118d_seeded_forager import heldout
from archaeon.campaign6.worlds.runtime import player_for


def trace(m, ho, E=8):
    c = {"safe": 0, "toxic": 0, "moves": 0, "ticks": 0}
    for w, s in ho:
        cw = w.w.w; player = player_for(m)
        for ep in range(E):
            st = w.reset(s, ep, None); vm = player.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep))
            while not w.done(st):
                outs, status = player.run_tick(vm, w.observe(st), w.K, rng)
                if outs and outs[0] and st["pools"]:
                    i = outs[0][0] % cw.R
                    if st["pool_node"][i] == st["pos"] and st["pools"][i] > 0:
                        c["toxic" if st["toxic"][i] else "safe"] += 1
                if len(outs) > 1 and outs[1]:
                    c["moves"] += 1
                c["ticks"] += 1
                w.act(st, outs)
                if status == "trap":
                    break
    c["toxic_share"] = round(c["toxic"] / max(1, c["toxic"] + c["safe"]), 3)
    return c


if __name__ == "__main__":
    ho = heldout()
    progs = {"GEN3": gen(3), "CHK3": chk(3)}
    for f in sys.argv[1:]:
        progs[Path(f).stem] = json.loads(Path(f).read_text(encoding="utf-8"))
    out = {}
    for k, m in progs.items():
        out[k] = trace(m, ho); print(k, json.dumps(out[k]), flush=True)
    Path(__file__).resolve().parent.joinpath("results", "B118g_type_rep_clean", "B118h_decode.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
