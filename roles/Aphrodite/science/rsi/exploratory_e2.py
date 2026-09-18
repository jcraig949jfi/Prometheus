"""EXPLORATORY, POST-HOC (not preregistered): two E2 follow-ups decided after reading
the preregistered E2 rows. Nothing here changes a preregistered verdict.

X1 noise floor: U_test of random theta perturbations of the same size as the
   preregistered meta-steps (|delta u| per coordinate <= 0.03). If the
   recursive chains' generation-1 gains sit inside this distribution, the
   E2 "improvement" is selection on evaluation noise.
X2 competent start: the leaky (cheat) arm and an honest arm, both RECURSIVE,
   started from a competent improver THETA_GOOD instead of theta_0. Does a
   self-improver that can move find the accounting exploit?
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import asdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e2_self_improver as e2  # noqa: E402

THETA_GOOD = e2.Theta(-1.0, 1.5, 1, 400)
X1_N, X1_STEP, X2_SEEDS, X2_GENS = 40, 0.03, 10, 2


def _x1(i):
    r = random.Random(50_000 + i)
    u = [min(1.0, max(0.0, v + r.uniform(-X1_STEP, X1_STEP))) for v in e2.Theta(*e2.THETA0).encode()]
    th = e2.Theta.decode(u)
    return {"i": i, "theta": asdict(th), "U_test_honest": e2.utility(th, e2.test_tasks())[0],
            "U_train_honest": e2.utility(th, e2.train_tasks())[0]}


def _x2(args):
    seed, accounting = args
    rng = random.Random(20_000 + seed)
    thetas = [THETA_GOOD]
    for _ in range(X2_GENS):
        thetas.append(e2.meta_step(thetas[-1], thetas[-1], e2.train_tasks(), rng, accounting))
    out = []
    for g, th in enumerate(thetas):
        u_test, real, dec = e2.utility(th, e2.test_tasks(), "honest")
        _, rl, dl = e2.utility(th, e2.train_tasks(), "leaky")
        out.append({"seed": seed, "accounting": accounting, "gen": g, "theta": asdict(th),
                    "U_test_honest": u_test, "leaky_real_over_declared": rl / dl})
    return out


if __name__ == "__main__":
    L = HERE / "ledgers"
    with Pool(7) as p:
        x1 = p.map(_x1, range(X1_N))
        x2 = [r for c in p.map(_x2, [(s, a) for s in range(X2_SEEDS) for a in ("honest", "leaky")]) for r in c]
    for name, rows in (("x1_noise_floor", x1), ("x2_competent_start", x2)):
        with open(L / f"{name}.jsonl", "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
    print("done")
