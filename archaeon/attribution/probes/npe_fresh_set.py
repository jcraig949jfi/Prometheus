"""G2 FRESH agreement set (Amendment C9 s5). Committed BEFORE its seed exists.

- The seed is the full SHA of the git commit that records BOTH re-freeze hashes (Nestor's re-frozen tracer, and the re-attested
  reference). It is passed on the command line. This generator must not change after that commit.
- It emits pre-states only. It runs no tracer and reads neither tracer's output. The output file is hashed and the hash posted
  before either side traces it.
- Set A: 300 interactions, uniform pre-states in the fuzz format of the first set: ga, gb uniform over 32 bytes; regs None with
  p=1/4 (reset), else uniform bytes; flags uniform bits; budget 300; ops_mask 0x0C. Compared per locus, BEFORE write-back.
- Set M (added BEFORE the fresh run, to exercise the MUTATION class, which the first set did not): 100 further interactions of the
  same distribution. Each carries a write-back RNG seed, "wb_seed". Loci are compared AFTER write-back (world.py:484-550; C6 E).
    python -m archaeon.attribution.probes.npe_fresh_set SEED_SHA OUT.jsonl
"""
import hashlib
import json
import random
import sys


def gen(seed, n_a=300, n_m=100):
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    out = []
    for k in range(n_a + n_m):
        pre = {"ga": bytes(rng.randrange(256) for _ in range(32)).hex(), "gb": bytes(rng.randrange(256) for _ in range(32)).hex(),
               "regs_a": None if rng.random() < 0.25 else [rng.randrange(256) for _ in range(8)],
               "regs_b": None if rng.random() < 0.25 else [rng.randrange(256) for _ in range(8)],
               "flags_a": [rng.randrange(2), rng.randrange(2)], "flags_b": [rng.randrange(2), rng.randrange(2)],
               "budget": 300, "ops_mask": 0x0C, "tape_len": 64}
        rec = {"k": k, "set": "A" if k < n_a else "M", "pre": pre}
        if k >= n_a:
            rec["wb_seed"] = rng.randrange(2 ** 62)
        out.append(rec)
    return out


if __name__ == "__main__":
    seed, outp = sys.argv[1], sys.argv[2]
    assert len(seed) == 40 and all(c in "0123456789abcdef" for c in seed), "seed must be a full commit SHA"
    with open(outp, "w", newline="\n") as fh:
        for r in gen(seed): fh.write(json.dumps(r, sort_keys=True) + "\n")
    print(hashlib.sha256(open(outp, "rb").read()).hexdigest(), outp)
