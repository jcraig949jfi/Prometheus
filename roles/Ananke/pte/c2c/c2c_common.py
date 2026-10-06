"""PTE-C2C / C2BX common. Operator order: roles/Ananke/prompts/2026-10-06_c2b_close_c2bx_c2c/ (64dad7553).

Additive to C2A/C2B: imports roles/Ananke/pte/c2a (instrument) and pte/c2b (lineage-tagged GA operators) unchanged.

BLOCK OPERATOR (OPB), mechanism-blind, fixed before production:
  offspring = OP0 offspring (c2b.mutate_tagged: the frozen field/instruction/swap mutation, same RNG order), then with
  probability P_BLOCK = 0.25 ONE block move on a uniformly chosen rule:
    length b ~ uniform{2, 3, 4}; source start s ~ uniform{0 .. L-b};
    kind ~ uniform{DUPLICATE, MOVE, REPLACE}:
      DUPLICATE  copy lines [s, s+b) over [t, t+b), t ~ uniform{0 .. L-b} (tags copied with the lines)
      MOVE       cut lines [s, s+b) and reinsert them at t ~ uniform{0 .. L-b} of the remainder (tags move)
      REPLACE    lines [s, s+b) := fresh random instructions (search._rand_instr; tags False)
  Lengths, positions and kinds are uniform and independent of genome content: the operator encodes no knowledge
  of any FLIP solution.

GRADED STEPPING STONE (FLIP): a partially functional degradation of the plant of record P_FLIP. For each
(cell, idx), attempt a = 0..199 draws exactly k ~ (1 if a even else 2) GA-native field edits of P_FLIP from
rng(C2C_NS, STONE_KEY, cell_key, idx, a) and scores it with the frozen FLIP ruler on STONE_QUAL worlds
(128, H(C2C_NS, STONE_QUAL_KEY, cell_key)). The FIRST draw with
    competence status FALSE (not INDETERMINATE)  AND  0.60 <= B mean  AND  B hi99 < 0.75
is the stone (graded: above the copy/chance region's floor, below the competence bar and not near it).
No qualified draw within 200 attempts -> that (cell, idx) has no stone (STEP arms unavailable there).
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "c2b"))
import c2b_common as B  # noqa: E402
C = B.C
from prometheus.ananke import assays  # noqa: E402
from prometheus.ananke.search import _rand_instr  # noqa: E402

C2C_NS = 0xC2C01006
SEED_KEY = 0x5EED
STONE_KEY = 0x570E
STONE_QUAL_KEY = 0x5A0E
P_BLOCK = 0.25
BLOCK_LENGTHS = (2, 3, 4)
STONE_B_LO = 0.60
MAX_STONE_ATTEMPTS = 200


def search_seed(cell_key: int, idx: int) -> int:
    """Fresh production seeds (not C2A/C2B seeds); shared by the four C2C arms at idx (CRN pairing)."""
    return C.H_int(C2C_NS, SEED_KEY, cell_key, idx)


def block_move(g, c, t):
    """One mechanism-blind block move, in place on copies; returns (c, t)."""
    c = c.copy(); t = t.copy()
    R, L, _ = c.shape
    r = int(g.integers(R))
    b = int(BLOCK_LENGTHS[int(g.integers(len(BLOCK_LENGTHS)))])
    s = int(g.integers(0, L - b + 1))
    kind = int(g.integers(3))
    if kind == 0:                                   # DUPLICATE
        d = int(g.integers(0, L - b + 1))
        blk, tb = c[r, s:s + b].copy(), t[r, s:s + b].copy()
        c[r, d:d + b] = blk; t[r, d:d + b] = tb
    elif kind == 1:                                 # MOVE
        d = int(g.integers(0, L - b + 1))
        idx = list(range(L))
        blk = idx[s:s + b]; rest = idx[:s] + idx[s + b:]
        order = rest[:d] + blk + rest[d:]
        c[r] = c[r, order]; t[r] = t[r, order]
    else:                                           # REPLACE
        c[r, s:s + b] = _rand_instr(g, (b,)); t[r, s:s + b] = False
    return c, t, (r, b, s, kind)


def mutate_opb(g, parent, ptag, sp):
    c, t = B.mutate_tagged(g, parent, ptag, sp)
    if g.random() < P_BLOCK:
        c, t, _ = block_move(g, c, t)
    return c, t


def stone_qual_seeds(cell_key):
    return assays.world_seeds(C.H_int(C2C_NS, STONE_QUAL_KEY, cell_key), 128)


def _stone_draw(plant, cell_key, idx, a):
    k = 1 if a % 2 == 0 else 2
    rng = np.random.default_rng(C.H_int(C2C_NS, STONE_KEY, cell_key, idx, a))
    g, edits = B.k_edit(plant, k, rng)
    return g, edits, k


def graded_stone(ph, env, plant, cell_key, idx, device="cpu", score=None, batch=25):
    """First qualified graded draw wins (attempt order). Real scoring evaluates attempts in batches of `batch`
    on the same worlds (programs are independent, so each attempt's reading is identical to scoring it alone);
    attempts after the first qualified one in a batch are discarded unrecorded.
    score(genome) -> (status, B_mean, B_hi99) may be injected by tests (then attempts are scored one by one)."""
    seeds = stone_qual_seeds(cell_key)
    att = []
    a = 0
    while a < MAX_STONE_ATTEMPTS:
        span = range(a, min(a + (1 if score is not None else batch), MAX_STONE_ATTEMPTS))
        draws = [_stone_draw(plant, cell_key, idx, j) for j in span]
        if score is None:
            pt, ep = C.eval_programs(ph, env, seeds, [d[0] for d in draws], device=device)
            reads = []
            for i in range(len(draws)):
                comp = C.competence("FLIP", pt[i], ep)
                reads.append((comp["status"], comp["B"]["mean"], comp["B"]["hi99"]))
        else:
            reads = [score(d[0]) for d in draws]
        for j, (g, edits, k), (st, bm, bh) in zip(span, draws, reads):
            ok = st == "FALSE" and bm >= STONE_B_LO and bh < C.B_CUT
            att.append({"attempt": j, "k": k, "edits": edits, "status": st, "B": bm, "B_hi99": bh, "qualified": ok})
            if ok:
                return g, att
        a = span[-1] + 1
    return None, att
