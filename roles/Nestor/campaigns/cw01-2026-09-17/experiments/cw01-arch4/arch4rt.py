"""Shared runtime shim for the reactivated Campaign 4 descendants.

Imports the FROZEN Archaeon/Proteus runtime by path from the Nestor execution worktree
(F:/Prometheus-worktrees/nestor-arch4, branch nestor/arch4-loop-2026-09-18 from origin/main
9cd33ff1e). Read-only: nothing under archaeon/ or proteus/ is edited, and the engine client is
never imported or contacted (no token exists here; rows are committed to git in the CW01
worktree). Computational scope: integer programs on a bounded VM; see loop/pool_arch4.py.

Provides: the 57 canonical parents, environments and episodes (CRN), evaluation, the C4-01
classification, decode-rule transforms (modulo / trap-to-NOP / trap-to-HALT), and a process pool.
"""
from __future__ import annotations

import json
import pathlib
import sys

ARCH = pathlib.Path("F:/Prometheus-worktrees/nestor-arch4")
ARCH_SHA = "9cd33ff1e"
for p in (ARCH, ARCH / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry.affordances import N_OPCODES, NOP, CATEGORY             # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from proteus.eval.population_manifest import structural_descriptor           # noqa: E402
from archaeon.wse.evolve import evaluate                                     # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for, with_knobs          # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_05 as C5                                   # noqa: E402
from archaeon.campaign4.c4base import CAMPAIGN_SEED                          # noqa: E402

HALT = 1
IW = GR.IW
LOOP_SEED = 20260922          # this reactivation's campaign seed: continues the sequence (C4 used 20260921)


def parents():
    pop = json.loads((ARCH / "archaeon" / "campaign4" / "STARTING_POPULATION.json").read_text(encoding="utf-8"))
    out = []
    for e in pop["organisms"]:
        out.append({"organism_id": e["organism_id"], "stratum": e["class"], "manifest": e["manifest"],
                    "ancestries": e.get("ancestries")})
    return out


# ---------------------------------------------------------------- decode rules (a genome transform; the VM is untouched)
def canonical(m):
    """Opcode words reduced modulo the table: behaviour-identical under the VM (it applies the same modulo)."""
    c = json.loads(json.dumps(m))
    g = c["genome"]
    for i in range(0, len(g), IW):
        g[i] = g[i] % N_OPCODES
    return c


def trap(m, mode):
    """Decode rule applied to a manifest: 'modulo' returns it unchanged; 'nop' rewrites every out-of-table
    opcode word to NOP; 'halt' rewrites it to HALT. Returns (manifest, n_trapped)."""
    if mode == "modulo":
        return m, 0
    c = json.loads(json.dumps(m))
    g = c["genome"]
    n = 0
    for i in range(0, len(g), IW):
        if g[i] >= N_OPCODES:
            g[i] = NOP if mode == "nop" else HALT
            n += 1
    return c, n


# ---------------------------------------------------------------- environments
ENVS = dict(C1.ENVS)
PARENT_ENV = dict(C1.PARENT_ENV)
OTHER_ENVS = tuple(C1.OTHER_ENVS)


def episodes(env, e=C1.E, spec=None, seed=CAMPAIGN_SEED):
    return episodes_for(spec if spec is not None else ENVS[env], seed, "train", 1, e)


def eval_all(m, eps):
    return C1.eval_all(m, eps)


def classify(child_ev, parent_ev, disp, undecodable, env):
    return C1.classify(child_ev, parent_ev, disp, undecodable, env)


def digest(m):
    import hashlib
    return hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def pool(n=8):
    from concurrent.futures import ProcessPoolExecutor
    return ProcessPoolExecutor(max_workers=n)
