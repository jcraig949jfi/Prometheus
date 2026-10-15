"""Independent evaluation of PTE genomes on the C4 ladder: CPU oracle dynamics + re-implemented worlds and rulers.

    eval_programs(phys, env, seeds, genomes, ...) -> (per_trial [G, M, trials], Episode)
    competence_of(task, phys, env, seeds, genome, ...) -> ruler record

Mirror twins run the physics under the LEAD world seed (pair b, b+1 share every physics draw; only the sense stream
differs), as the engine's eval_programs does (c2a_common.py:186 `ws1`). Interventions: `sval_edit(sval, ep)` edits the
sense schedule (context off, teacher off), `after_tick(t, b, S_b)` edits state between ticks (register zero), and
`zero_comm` drops every packet copy. Genome edits (line NOP, substitution, use-disabled) are in mechanics.py.
"""
from __future__ import annotations

import numpy as np

from prometheus.ananke.oracle import H

from . import ruler, worlds
from .runner import run as oracle_run

C4_NS = worlds.C4_NS
ADMIT_KEY, DLIB_LIVE_KEY, DLIB_HELD_KEY, MODULE_ALONE_KEY = 0xAD4, 0xD11B, 0xD11C, 0x1AB
OWN_NS = 0xA7605019          # this packet's fresh namespace (Argus C-019-T040); disjoint keys under it


def eval_programs(phys: dict, env: worlds.Env, seeds, genomes, sval_edit=None, after_tick=None, zero_comm=False):
    ep = worlds.build(phys, env, seeds)
    sv = ep.sval.copy()
    if sval_edit is not None:
        sval_edit(sv, ep)
    sense = ep.sense(sv)
    lead = [int(seeds[m - (m % 2)]) for m in range(len(seeds))]
    out = []
    for g in genomes:
        g = np.asarray(g, dtype=np.int64)
        if g.ndim == 2:
            g = g[None]
        r = oracle_run(phys, [g] * len(seeds), lead, sense, env.T(), after_tick=after_tick, zero_comm=zero_comm)
        out.append(worlds.per_trial(ep, r["S0_trace"]))
    return np.stack(out), ep


def competence_of(task: str, phys: dict, env: worlds.Env, seeds, genome, **kw) -> dict:
    pt, ep = eval_programs(phys, env, seeds, [genome], **kw)
    return ruler.competence(worlds.ROLE[task], pt[0], ep)


def slim(c: dict) -> dict:
    o = {"status": c["status"], "role": c["role"]}
    for k in ("all", "late", "B"):
        if k in c:
            o[k] = {kk: c[k][kk] for kk in ("mean", "lo99", "hi99", "d_se", "status", "decided")}
    return o


# ------------------------------------------------------------------ seeds of the owner's known-answer checks
def admission_seeds(task: str, cell_key: int, M: int = 128) -> list:
    """c4_admission.py:27 (@ f58362c5e): H(C4_NS, 0xAD4, task id, cell_key), 128 worlds."""
    return worlds.world_seeds(H(C4_NS, ADMIT_KEY, worlds.TASK_ID[task], cell_key), M)


def dlib_held_seeds(cell_key: int, M: int = 128) -> list:
    """build_dlib.py:51 (@ f58362c5e): H(C4_NS, 0xD11C, cell_key), 128 worlds."""
    return worlds.world_seeds(H(C4_NS, DLIB_HELD_KEY, cell_key), M)


def module_alone_seeds(cell_key: int, M: int = 64) -> list:
    """c4_flight/module_alone_check.txt: 64 worlds H(C4_NS, 0x1AB, cell_key)."""
    return worlds.world_seeds(H(C4_NS, MODULE_ALONE_KEY, cell_key), M)


def own_seeds(purpose: int, cell_key: int, M: int) -> list:
    """Fresh worlds for this packet's own checks (never the owner's training/final/held namespaces)."""
    return worlds.world_seeds(H(OWN_NS, purpose, cell_key), M)


# ------------------------------------------------------------------ genomes
def null_genome(phys: dict) -> np.ndarray:
    return np.zeros((int(phys["rules"]), int(phys["prog_len"]), 5), dtype=np.int64)


def place(phys: dict, rows, start: int = 0) -> np.ndarray:
    """A NOP genome with `rows` written in order from line `start` (rule 0 broadcast to every rule)."""
    g = null_genome(phys)
    rows = np.asarray(rows, dtype=np.int64).reshape(-1, 5)
    assert start + len(rows) <= g.shape[1], "module does not fit"
    g[:, start:start + len(rows)] = rows
    return g


def place_at(phys: dict, indexed_rows) -> np.ndarray:
    """A NOP genome with (line index, row) pairs written at their own positions (build_dlib.place)."""
    g = null_genome(phys)
    for i, row in indexed_rows:
        g[:, i] = row
    return g


def canonical(g) -> np.ndarray:
    """Re-encode out-of-range CONST immediates into the GA support (c2a_common.canonical, :127-154 @ f58362c5e):
    CONST computes (imm + Kp) << (b & 7); 128 with b = 0 -> imm 64, b 1."""
    x = np.array(g, dtype=np.int64, copy=True)
    for r in range(x.shape[0]):
        for i in range(x.shape[1]):
            op, imm = int(x[r, i, 0]) % 16, int(x[r, i, 4])
            if -128 <= imm <= 127:
                continue
            assert op == 6 and (int(x[r, i, 3]) & 7) == 0
            for sh in range(1, 8):
                if imm % (1 << sh) == 0 and -128 <= imm >> sh <= 127:
                    x[r, i, 4] = imm >> sh; x[r, i, 3] = sh
                    break
            else:
                raise AssertionError("no canonical CONST encoding")
    return x


def relay_latch(phys: dict) -> np.ndarray:
    """FLIP copy adversary RELAY_LATCH (c2a_common.relay_latch, :103-110 @ f58362c5e), canonical, at `phys`."""
    from prometheus.ananke import plants
    from prometheus.ananke.physics import Physics
    ph = Physics.from_dict(phys).validate()
    body = plants.assemble(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "PAY0", "T3", 0),
        ("SUB", "T0", "PAY0", "S0", 0), ("MULQ", "EMIT", "T0", "PAY0", 0),
        ("MULQ", "T1", "PAY0", "PAY0", 0), ("SEL", "T1", "PAY0", "S0", 0), ("MOV", "S0", "T1", 0, 0),
        ("MULQ", "T3", "SENSE", "SENSE", 0), ("SEL", "T3", "SENSE", "S0", 0), ("MOV", "S0", "T3", 0, 0)])
    return canonical(np.broadcast_to(body, (ph.rules, *body.shape)).copy())


def register_layout(phys: dict) -> dict:
    """DESIGN.md s5 register file indices."""
    D, P, C = int(phys["state_dim"]), int(phys["payload_width"]), int(phys["channels"])
    NW = D + 8 + P
    NR = NW + C * P + C + 3
    return {"D": D, "NW": NW, "NR": NR, "T0": D, "EMIT": D + 4, "CHAN": D + 5, "RPORT": D + 6, "RVAL": D + 7,
            "PAY0": D + 8, "SENSE": NW + C * P + C, "ZERO": NR - 1}
