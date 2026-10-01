"""Step 10 (symmetry check for s9): are side-0 copiers equally dependent on FRESH registers? Run each side-0-certified
DENSE donor (all 114 rows with certified_sides == [0] on DENSE) in its own context (base 0, sense 0) from pc 0 on
[G | 64 x HALT] with FRESH registers vs 30 random register files; outcome = side-1 half >= 0.9 identical to G.
Same for the 17 side-1 copiers in their own context (base n, sense 1, pc n) for a like-for-like table."""
import json, pathlib, collections, random
from _env import A, ROWS
import p11


def trial(z, P, G, side, rs):
    n = P["n"]
    tape = bytearray(P["tape_len"])
    d0 = 0 if side == 0 else n; v0 = n - d0
    tape[d0:d0 + n] = G; tape[v0:v0 + n] = bytes([0x76]) * n
    ctx = z.Ctx(tape, d0, n, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=side)
    ctx.regs, ctx.fz, ctx.fc = (None, 0, 0) if rs is None else (list(rs[0]), rs[1], rs[2])
    z.run(ctx, d0, P["budget"], ops_enabled=P["mask"])
    return p11.fidelity(G, bytes(tape[v0:v0 + n])) >= 0.9


if __name__ == "__main__":
  out = {}
  for side in (0, 1):
      sel = [r for r in ROWS if r["P11"]["certified"] and r["P11"]["certified_sides"] == [side] and r["vm"] == "DENSE"]
      fresh = 0; rand = 0; tot = 0; per = []
      for r in sel:
          G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
          rr = random.Random("W2-16-regs-" + r["key"])
          f = trial(z, P, G, side, None)
          k = sum(trial(z, P, G, side, ([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2)))
                  for _ in range(30))
          fresh += f; rand += k; tot += 30; per.append(k / 30)
      per.sort()
      out["side%d" % side] = {"n_genomes": len(sel), "fresh_good": fresh, "randregs_good": rand, "randregs_trials": tot,
                              "randregs_rate": round(rand / tot, 3),
                              "genomes_randregs_rate_ge_0.9": sum(1 for x in per if x >= 0.9),
                              "median_genome_rate": per[len(per) // 2]}
      print(side, out["side%d" % side])
  pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
