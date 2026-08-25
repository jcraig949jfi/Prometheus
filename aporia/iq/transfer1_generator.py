"""transfer1_generator.py — TRANSFER-1: the frozen G-heldout generator and the X-heldout routes.

Preregistration: aporia/iq/PREREG_TRANSFER_1_2026-08-25.md, committed e7a9b314 BEFORE this file
existed. Every design choice below is fixed there; nothing here is chosen after seeing a score.

The relation is all_but_n: remove N from T, report what remains.

WHY THE STRATA EXIST, and it is not tidiness. c66ea4a9 measured that one of five canary
all_but_n tasks has T = 2N, so the target coincides with an operand. That one task let a
return-N rule and a half-total rule each score dE +0.008333, and it broke strict provenance set
membership across 464,652 pipelines. So every draw here is classified, the primary reading uses
NONDEGENERATE only, and DEGENERATE is generated anyway and reported SEPARATELY as a
contamination channel. Deleting it silently would hide the effect that motivated the rung.

DISTRACTORS INCLUDE THE OPERANDS BY CONSTRUCTION. In the nondegenerate stratum that makes
"echo an operand" a wrong answer definitionally, not incidentally.

SURFACE VARIES INDEPENDENTLY OF STRUCTURE. Four surface realisations, one of which (v2) does not
match the port's regex at all. That is deliberate: the point of separating surface from structure
is to be able to see the port fail for a surface reason and not mistake it for a capability
reason. Scores are reported per variant as well as overall.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "apollo" / "scripts",
          ROOT / "agents" / "hephaestus" / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

SEED = 20260825          # fixed in the preregistration, never re-drawn after seeing a result
N_TRAIN = 400
N_TEST = 200

FILLERS = ["exactly as stated", "precisely by definition", "unambiguously in this case",
           "specifically as stated", "by definition precisely", "in this case exactly"]

# Surface realisations. v0/v1/v3 match the port's regex family; v2 deliberately does not.
SURFACES = {
    "v0": "There were {T} items. {N} were removed. How many remain?",
    "v1": "There were {T} items. {N} was removed. How many remain?",
    "v2": "A box held {T} items. {N} were removed. How many are left?",
    "v3": "There were {T} items in total. {N} were removed. What remains?",
}
TRAIN_SURFACES = ["v0", "v1", "v2"]      # v3 appears NOWHERE in train
TEST_SURFACES = ["v0", "v1", "v2", "v3"]  # -> (test range x v3) is the unseen combination

# Parameter partition is over the PARAMETER SPACE, not over instances.
TRAIN_T = (5, 60)
TEST_T = (61, 200)


def stratum(T: int, N: int) -> str:
    """Exactly one of three labels. Asserted to partition in the harness."""
    target = T - N
    operands = {T, N}
    if target in operands:
        return "DEGENERATE"
    if any(abs(target - o) <= 1 for o in operands):
        return "NEAR_DEGENERATE"
    return "NONDEGENERATE"


def make_candidates(T: int, N: int, rng: random.Random) -> tuple[list[str], str]:
    """Four candidates. The OPERANDS ARE ALWAYS AMONG THEM, so echoing an operand is wrong by
    construction outside the degenerate stratum. Returns (candidates, correct)."""
    target = T - N
    values = [target, T, N]
    # pad to four distinct values with near-misses that are not operands
    for delta in (1, -1, 2, -2, 3, -3, 4):
        cand = target + delta
        if cand not in values and cand >= 0:
            values.append(cand)
        if len(values) == 4:
            break
    while len(values) < 4:                      # degenerate collisions can starve the loop
        cand = rng.randint(0, max(T, 5) + 10)
        if cand not in values:
            values.append(cand)
    values = values[:4]
    strings = [f"{v} {rng.choice(FILLERS)}" for v in values]
    correct = strings[0]
    rng.shuffle(strings)
    return strings, correct


# Declared stratum proportions. Uniform parameter draws put DEGENERATE near 2%, which is far
# too thin to serve as the contamination channel the preregistration requires it to be, so the
# stratum is sampled FIRST and the parameters are then drawn to satisfy it. The proportions are
# fixed here and reported with every reading.
STRATUM_MIX = [("NONDEGENERATE", 0.70), ("DEGENERATE", 0.15), ("NEAR_DEGENERATE", 0.15)]


def _draw_params(rng: random.Random, lo: int, hi: int, want: str) -> tuple[int, int]:
    """Rejection-sample (T, N) in range until the requested stratum is hit. DEGENERATE is
    constructed directly (T = 2N gives target == N) because rejection would be slow."""
    if want == "DEGENERATE":
        for _ in range(200):
            N = rng.randint(max(1, lo // 2), max(1, hi // 2))
            T = 2 * N                      # target = T - N = N, an operand
            if lo <= T <= hi and stratum(T, N) == "DEGENERATE":
                return T, N
    for _ in range(2000):
        T = rng.randint(lo, hi)
        N = rng.randint(1, max(1, T - 1))
        if stratum(T, N) == want:
            return T, N
    return T, N                            # LOUD: fallthrough is counted by the harness


def draw(rng: random.Random, split: str) -> dict:
    lo, hi = TRAIN_T if split == "train" else TEST_T
    surfaces = TRAIN_SURFACES if split == "train" else TEST_SURFACES
    r = rng.random()
    acc, want = 0.0, STRATUM_MIX[-1][0]
    for name, share in STRATUM_MIX:
        acc += share
        if r < acc:
            want = name
            break
    T, N = _draw_params(rng, lo, hi, want)
    sv = rng.choice(surfaces)
    cands, correct = make_candidates(T, N, rng)
    return {"prompt": SURFACES[sv].format(T=T, N=N), "candidates": cands, "correct": correct,
            "category": "all_but_n", "T": T, "N": N, "target": T - N,
            "stratum": stratum(T, N), "stratum_requested": want,
            "surface": sv, "split": split,
            "unseen_combination": (split == "test" and sv == "v3")}


# ── X-heldout: the SAME relation through structurally different construction ────
# Not paraphrases. A rewording of the same template is still G.

def x_set_membership(T: int, N: int, rng: random.Random) -> dict:
    cands, correct = make_candidates(T, N, rng)
    return {"prompt": (f"The set S contains {T} elements. {N} of them are marked as removed. "
                       f"How many elements of S are not marked as removed?"),
            "candidates": cands, "correct": correct, "category": "all_but_n",
            "T": T, "N": N, "target": T - N, "stratum": stratum(T, N), "route": "set_membership"}


def x_tabular(T: int, N: int, rng: random.Random) -> dict:
    cands, correct = make_candidates(T, N, rng)
    return {"prompt": (f"A table has {T} rows. The removed flag is set on {N} rows. "
                       f"On how many rows is the removed flag not set?"),
            "candidates": cands, "correct": correct, "category": "all_but_n",
            "T": T, "N": N, "target": T - N, "stratum": stratum(T, N), "route": "tabular"}


X_ROUTES = {"set_membership": x_set_membership, "tabular": x_tabular}


def build():
    """Deterministic. Same seed -> same task list, byte for byte."""
    rng = random.Random(SEED)
    train = [draw(rng, "train") for _ in range(N_TRAIN)]
    test = [draw(rng, "test") for _ in range(N_TEST)]
    xr = random.Random(SEED + 1)
    x = {name: [fn(xr.randint(61, 200), xr.randint(1, 50), xr) for _ in range(100)]
         for name, fn in X_ROUTES.items()}
    return train, test, x


def corpus_hash(train, test, x) -> str:
    h = hashlib.sha256()
    for split in (train, test):
        for t in split:
            h.update(json.dumps(t, sort_keys=True).encode())
    for name in sorted(x):
        for t in x[name]:
            h.update(json.dumps(t, sort_keys=True).encode())
    return h.hexdigest()


if __name__ == "__main__":
    tr, te, xx = build()
    print(f"train {len(tr)} test {len(te)} x {[(k, len(v)) for k, v in xx.items()]}")
    print("corpus sha256:", corpus_hash(tr, te, xx))
    from collections import Counter
    print("train strata:", Counter(t["stratum"] for t in tr))
    print("test strata:", Counter(t["stratum"] for t in te))
    print("test unseen-combination cell:", sum(t["unseen_combination"] for t in te))
