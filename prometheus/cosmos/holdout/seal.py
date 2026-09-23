"""Write the sealed holdout spec ONCE. Run: COSMOS_BROKER=1 python -m prometheus.cosmos.holdout.seal

The nonce comes from the OS CSPRNG, so the sealed world list and the holdout run seeds
are independent of every visible-family seed (seed-leakage guard). The spec records the
sha256 of well.py so the broker can refuse a family that changed after sealing.
"""
from __future__ import annotations

import json
import secrets
from pathlib import Path

import numpy as np

from prometheus.cosmos.hashing import file_sha, h
from prometheus.cosmos.holdout.well import FAMILY as D

HERE = Path(__file__).resolve().parent
SPEC = HERE / "sealed_spec.json"
N_WORLDS = 240

INTERVENTION_PROTOCOL = {
    "axis": "kappa (maintenance power price), do(kappa: a -> a*f)",
    "n_base": 12,
    "selection": "sealed worlds whose frozen-law P(PAYS) >= 0.9, taken in ascending sha256(world index, nonce) order",
    "ladder": [2.0 ** (k / 2.0) for k in range(-8, 9)],
    "episodes": 1600,
    "prediction": "f_star = factor at which the frozen law's predicted class flips (C scales linearly in kappa); "
                  "band = factors at law P = 0.75 and P = 0.25",
    "score_direction": "observed PAYS at f_star/2 and observed QUIET at 2*f_star (both required)",
    "score_magnitude": "|log2(f_obs / f_star)| <= 1, f_obs = first ladder factor with observed margin < 0.10",
    "gate_G6": "direction correct on >= 10/12 bases AND magnitude correct on >= 8/12 bases",
}


def main():
    if SPEC.exists():
        raise SystemExit("sealed spec already exists; sealing is once-only (sha %s)" % file_sha(SPEC))
    nonce = secrets.token_hex(16)
    rng = np.random.default_rng(int(nonce, 16) % (2 ** 63))
    sp = D.space()
    worlds = []
    for _ in range(N_WORLDS):
        worlds.append({k: (v[rng.integers(len(v))]) for k, v in sp.items()})
    worlds = [{k: (float(x) if isinstance(x, float) else int(x)) for k, x in w.items()} for w in worlds]
    spec = {"family": D.name, "family_version": D.version,
            "family_src_sha": file_sha(HERE / "well.py"), "nonce": nonce, "worlds": worlds,
            "intervention_protocol": INTERVENTION_PROTOCOL}
    spec["spec_id"] = h({k: v for k, v in spec.items()})
    SPEC.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("sealed", SPEC, "sha256", file_sha(SPEC))


if __name__ == "__main__":
    main()
