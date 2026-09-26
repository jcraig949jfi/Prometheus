"""POST HOC check on `add`'s J-1 pass: is its endogenous change just counting?

Under `add`, v1's redundant writes (a source re-sending the same payload
to the same target every tick) become `target += payload` every tick.
That is guaranteed change with no information in it. This measures, with
perturbation OFF after the scout0 warmup, the share of changed (site,
field) pairs whose increment equals the previous tick's increment
(constant-step counting), and the share that are changed by the SAME
winning source slot as last tick. Design principle 6: a change the rule
guarantees is a mechanism check, not a finding.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [AETHER, os.path.join(AETHER, "test", "reference")]
import numpy as np
from observatory import aeth03_scouts as S
from observatory import aeth01_graph as G
out = {}
for s in (0, 1):
    seed, rng_seed = S.SEED0 + s, S.RNG0 + s
    f = S.initial("add", 128, rng_seed)
    par = S.params(seed, S.MUT_ON)
    for t in range(1, 1501):
        f, _ = S.step("add", f, t, par)
    off = S.params(seed, 0)
    hist, winners = [f], []
    for t in range(1501, 1501 + 60):
        f, obs = S.step("add", f, t, off, watch=True)
        hist.append(f); winners.append([G.unpack(o)[0] for o in obs])
    changed = const = same_src = 0
    for k in range(2, len(hist)):
        for i in range(4):
            a, b, c = (hist[k - 2][i].astype(np.int64), hist[k - 1][i].astype(np.int64),
                       hist[k][i].astype(np.int64))
            ch = c != b
            d1, d2 = (b - a) % 256, (c - b) % 256
            changed += int(ch.sum())
            const += int((ch & (d1 == d2)).sum())
            same_src += int((ch & (winners[k - 1][i] == winners[k - 2][i])
                             & (winners[k - 1][i] != G.NO_WINNER)).sum())
    out[s] = {"changed_pairs": changed,
              "constant_increment_share": const / float(changed),
              "same_source_as_last_tick_share": same_src / float(changed)}
    print(s, out[s], flush=True)
with open(os.path.join(HERE, "add_counting_check.json"), "w", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True); fh.write("\n")
