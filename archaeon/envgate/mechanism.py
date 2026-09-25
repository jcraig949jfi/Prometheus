"""ENVGATE-01: environmental gating causal assay -- identity, held configuration, arms, input transforms, digest.

A NEW experiment identity (operator directive 2026-09-24, roles/Archaeon/prompts/2026-09-24_environmental_gating/). It is not a
continuation of the 72-hour Z80 x Atlas campaign; that campaign's code, grammar and records are frozen inputs. The world physics are
the frozen z80atlas physics for ONE configuration (below); the only additions are (1) random-inflow chambers and (2) an input
transform per arm. Both are specified here and hashed into MECHANISM_DIGEST.

Inflow chambers. The ecology is the frozen 128-cell world. K additional CHAMBER cells receive fresh random tapes on a fixed schedule
(every DWELL epochs all K chambers are refilled from the block's inflow stream), independent of population size and of arm, so the
denominator "random tapes introduced" is fixed. A chambered tape is executed exactly like any organism; its neighbour is a random
ECOLOGY cell; its births go into the ecology. Chambers are write-protected (no birth ever lands in a chamber), and chambered tapes
are exempt from death and background mutation while chambered: every arrival is tested for exactly DWELL epochs, unchanged, in every
arm. Ecology organisms never see chambers as neighbours. A chambered tape never counts as established; only its ecology descendants
can.

Input transforms. Every case input starts from the SAME base stream in every arm: per (block, cell, epoch, case) two 32-bit words
(u, v) are drawn from the environment stream -- always both, in every arm (fixed consumption). Base byte x = u >> 24. An arm blocks
a set B of byte values: if x is in B it is replaced by POOL[(v * |POOL|) >> 32]; otherwise x passes unchanged. Non-blocked values are
therefore IDENTICAL across arms case by case, and each arm's alphabet is exactly its complement of B.
"""
from __future__ import annotations

import hashlib
import json

from archaeon.z80atlas.grammar import FROZEN

ASSAY_ID = "ENVGATE-01"
GATE_BAND = tuple(range(120, 136))                      # from the frozen copier census (89 of 96 gated-copier gates); directive-fixed
SHAM_BAND = tuple(range(156, 172))                      # frozen by rule from the census BEFORE any ecology (see SHAM_RULE)
SHAM_RULE = ("16-byte intervals disjoint from 120..135, ranked by (exact-copier gate incidences in the frozen vmcopy32 census; "
             "birth-input incidences over all 176 vmcopy32 census hits; -distance to 128; start): 156..171 has 0 gated-copier gates "
             "(its 16 incidences are the single UNGATED copier, identical for every interval), 257 birth incidences")
DOMINANT_GATE = 128

HELD = {"substrate": "vmcopy", "G": 32, "layout": "shared", "reproduction": "ENDOGENOUS_COPY", "topology": "well_mixed", "pressure": "implicit_survival",
        "task": "ECHO_forced", "mutation": "local_byte", "resources": "unlimited", "env_dynamics": "fixed", "N_ecology": FROZEN["N"],
        "initial_ecology": "empty", "step_cap": FROZEN["budgets"]["late"]["step_cap"]}
HELD_RATIONALE = ("vmcopy32 is the only censused substrate with copiers. ECHO_forced supplies one fresh uniform byte per case (the census "
                  "input model); under implicit_survival the task score has no reproductive consequence. Everything else is the plainest "
                  "frozen level. Nothing is taken from the 84616cf8257b specimen's world.")

ALL = tuple(range(256))


def _arm(name, blocked, pool_excludes):
    pool = tuple(x for x in ALL if x not in set(pool_excludes))
    return {"name": name, "blocked": tuple(sorted(blocked)), "pool": pool}


ARMS = {
    "U": _arm("U", (), ()),
    "BAND_BLOCK": _arm("BAND_BLOCK", GATE_BAND, GATE_BAND),
    "SHAM_BLOCK": _arm("SHAM_BLOCK", SHAM_BAND, SHAM_BAND),
    "BLOCK_128": _arm("BLOCK_128", (DOMINANT_GATE,), (DOMINANT_GATE,)),
    # BAND_BLOCK with 128 restored at exactly 1/256: 128 passes through; the other 15 band values are replaced from the SAME
    # 240-value pool as BAND_BLOCK, so RESCUE_128 and BAND_BLOCK differ ONLY on cases whose base byte is 128.
    "RESCUE_128": _arm("RESCUE_128", tuple(x for x in GATE_BAND if x != DOMINANT_GATE), GATE_BAND),
}
ARM_ORDER = ["U", "BAND_BLOCK", "SHAM_BLOCK", "BLOCK_128", "RESCUE_128"]


def transform(arm: dict, u: int, v: int) -> int:
    x = u >> 24
    if x in arm["_bset"]:
        p = arm["pool"]; return p[(v * len(p)) >> 32]
    return x


for _a in ARMS.values():
    _a["_bset"] = frozenset(_a["blocked"])


def alphabet(arm: dict) -> set:
    return set(ALL) - set(arm["blocked"])


# ---- schedule / exposure (set by the preregistration from census density + measured throughput; see PREREG.json)
DEFAULTS = {"K_chambers": 1024, "dwell": 64, "persistence_multiple": 3, "min_pop_frac": 0.25, "min_generation": 10}


def mechanism_spec(schedule: dict) -> dict:
    return {"assay": ASSAY_ID, "held": HELD, "frozen_physics": {k: FROZEN[k] for k in ("copy_min_frac", "copy_noise", "background_mutation", "mutation_rate",
                                                                                        "max_age", "death_rate", "energy_init", "cases_per_opportunity")},
            "arms": {k: {"blocked": v["blocked"], "pool_size": len(v["pool"])} for k, v in ARMS.items()}, "gate_band": GATE_BAND, "sham_band": SHAM_BAND,
            "schedule": schedule, "streams": ["envgate.inflow(block)", "envgate.env(block,cell,epoch)", "envgate.world(block)", "envgate.mutation(block)"]}


def digest(schedule: dict) -> str:
    return hashlib.sha256(json.dumps(mechanism_spec(schedule), sort_keys=True, default=list).encode()).hexdigest()[:16]
