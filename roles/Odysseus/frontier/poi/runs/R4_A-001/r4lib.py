"""R4_A-001 library: fast W2_K2 scorer, hand-written summit, planted control, walk arms.

Stdlib only. Imports the frozen runtime (proteus.foundry) and the WSE world read-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
for p in (REPO, os.path.join(REPO, "SerendipityFoundry", "SerendipityFoundryClient")):
    if p not in sys.path:
        sys.path.insert(0, p)

from proteus.foundry import grammar as GR                      # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402
from proteus.foundry.vm import Player, ManifestError, SCHEMA   # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402

CAMPAIGN_SEED = 20260921
W2_K2 = WorldSpec("W2_K2", K=2, value_bits=4)                  # c4_01.ENVS["W2_K2"]
BAND = 1 / 16
EPS = 1e-9
OPS = tuple(GR.NAMES)

_EPS_CACHE = {}


def episodes(family="train", index=1, n=16):
    key = (family, index, n)
    if key not in _EPS_CACHE:
        _EPS_CACHE[key] = episodes_for(W2_K2, CAMPAIGN_SEED, family, index, n)
    return _EPS_CACHE[key]


def expected_vector(eps):
    out = []
    for ep in eps:
        for ti in range(len(ep.ticks)):
            if ti in ep.expected:
                out.append(ep.expected[ti])
    return out


def answers(manifest, eps, rng_seed=0):
    """Answer vector, same loop as archaeon.wse.evolve.evaluate (per episode fresh state,
    vm rng seed_from('wse.vmrng', rng_seed, ei), first word on channel 0 at ask ticks)."""
    player = Player(manifest)
    out = []
    for ei, ep in enumerate(eps):
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        for ti, words in enumerate(ep.ticks):
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [words], 1, rng)
            if ti in ep.expected:
                out.append(outs[0][0] if outs[0] else None)
    return tuple(out)


def score(ans, exp):
    return sum(1 for a, e in zip(ans, exp) if a == e) / len(exp)


def episode_score(ans, exp, per_ep=2):
    n = len(exp) // per_ep
    return sum(1 for i in range(n) if all(ans[i * per_ep + j] == exp[i * per_ep + j] for j in range(per_ep))) / n


def digest(m):
    return hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


# ------------------------------------------------------------------ hand-written summit
NOP, HALT, LDC, MOV, EQ, JZ, JNZ, IN, OUT = 0, 1, 3, 4, 16, 19, 20, 21, 23


def I(op, a=0, b=0, c=0):
    return [op, a, b, c]


def summit_genome(clobbers=0):
    """Two-value keyed memory for W2_K2 (K=2, D=1). Registers persist ('regs').
    r6 = first tag seen, r7 = its value, r9 = the other stream's value.
    clobbers=1/2 inserts 'LDC r9 <- 0' (kills the second value before any answer):
    clobber A at instruction 0 (every tick), clobber B at the head of the ASK path."""
    pre = [I(LDC, 9, 0)] if clobbers >= 1 else []
    askhead = [I(LDC, 9, 0)] if clobbers >= 2 else []
    body = [
        I(IN, 1, 0),        # kind
        I(IN, 2, 0),        # tag
        I(IN, 3, 0),        # value (0 on ASK)
        I(LDC, 4, 1),
        I(EQ, 5, 1, 4),     # is PUT
        None,               # JZ r5 -> ASK path (filled below)
        I(JNZ, 6, 4),       # slot1 taken -> slot2 (4 ahead)
        I(MOV, 6, 2),
        I(MOV, 7, 3),
        I(HALT),
        I(MOV, 9, 3),       # slot2 value
        I(HALT),
    ]
    ask = askhead + [
        I(EQ, 10, 2, 6),
        I(JZ, 10, 3),
        I(OUT, 7, 0),
        I(HALT),
        I(OUT, 9, 0),
        I(HALT),
    ]
    jz_index = 5
    body[jz_index] = I(JZ, 5, len(body) - jz_index)   # to first instruction of ask path
    g = []
    for ins in pre + body + ask:
        g += ins
    return g


def manifest_of(genome, persist="regs", n_regs=12):
    return {"schema_version": SCHEMA, "n_regs": n_regs, "tape_words": 128, "genome": list(genome),
            "code_writable": False, "persist": persist, "tick_budget": 128, "out_cap": 4}


def levenshtein_instr(g1, g2):
    a = [tuple(g1[i:i + 4]) for i in range(0, len(g1), 4)]
    b = [tuple(g2[i:i + 4]) for i in range(0, len(g2), 4)]
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, y in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (0 if x == y else 1))
        prev = cur
    return prev[-1]


# ------------------------------------------------------------------ edits
def one_edit(m, rng, name=None):
    """One applied grammar edit or None (ManifestError or noop)."""
    try:
        c, rec = GR.mutate(m, rng, mate=None, name=name)
    except ManifestError:
        return None, None
    if "noop" in (rec.get("args") or {}):
        return None, rec
    return c, rec


def compound(m, rng, n_edits, max_tries=64):
    cur = m
    done = 0
    tries = 0
    while done < n_edits and tries < max_tries:
        tries += 1
        c, _ = one_edit(cur, rng)
        if c is not None:
            cur = c
            done += 1
    return cur if done == n_edits else None
