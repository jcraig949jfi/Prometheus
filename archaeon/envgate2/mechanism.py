"""ENVGATE-02: bounded window confirmation (operator directive 2026-09-24, Phase B). New identity; ENVGATE-01 untouched.

Claim under test (post-hoc, from ENVGATE-01): copier establishment depends on a multi-byte viable-offspring input WINDOW, not on the
exact-copy byte 128 alone. Source of every prediction: the FROZEN viability map archaeon/envgate/OFFSPRING_VIABILITY.json (commit
5649c78f8): for 81 census copiers gated at 128, how many yield a copier-grade child at each input byte.

Arm construction (mechanical, from the map only; computed below and frozen into PREREG):
  RRIGHT  the maximal contiguous interval containing 128 whose every byte has viability >= RRIGHT_FRAC * max viability
  RWEAK   among contiguous intervals of the SAME width inside the gate band 120..135 that also contain 128 (so exact-copy access is
          identical), the one with MINIMAL viability mass; DESIGN_NOT_IDENTIFIABLE if its mass > WEAK_MAX_RATIO * RRIGHT's mass
  Both, R128 and BAND0 start from BAND0 (block 120..135) and restore only their symbols; every blocked case is replaced from the SAME
  240-value pool (bytes outside the band), so restore arms differ from BAND0 only on cases whose base byte is in the restored set and
  every restored byte keeps exactly its uniform 1/256 rate. Transform: envgate mechanism (two u32 words per case, fixed consumption).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from archaeon.envgate import mechanism as M1

HERE = Path(__file__).resolve().parent
VIABILITY = HERE.parent / "envgate" / "OFFSPRING_VIABILITY.json"
ASSAY_ID = "ENVGATE-02"
BAND = tuple(range(120, 136))
RRIGHT_FRAC = 0.5
WEAK_MAX_RATIO = 0.75
LIFETIME = 60; CASE0_PER_EPOCH = 1                                        # branching approximation: R0 ~ LIFETIME * k / 256


def viability() -> dict:
    v = json.loads(VIABILITY.read_text(encoding="utf-8"))
    return {int(k): n for k, n in v["viable_inputs"].items()}, v["n"]


def design() -> dict:
    v, n = viability(); vmax = max(v.values()); thr = RRIGHT_FRAC * vmax
    lo = hi = 128
    while v.get(lo - 1, 0) >= thr: lo -= 1
    while v.get(hi + 1, 0) >= thr: hi += 1
    rright = tuple(range(lo, hi + 1)); w = len(rright); mass = lambda s: sum(v.get(x, 0) for x in s)
    cands = [tuple(range(s, s + w)) for s in range(BAND[0], BAND[-1] - w + 2) if 128 in range(s, s + w) and tuple(range(s, s + w)) != rright]
    rweak = min(cands, key=lambda s: (mass(s), s[0]))
    identifiable = mass(rweak) <= WEAK_MAX_RATIO * mass(rright)
    return {"rright": rright, "rweak": rweak, "width": w, "mass_rright": mass(rright), "mass_rweak": mass(rweak), "mass_ratio": round(mass(rweak) / mass(rright), 4),
            "threshold": thr, "identifiable": identifiable, "n_copiers": n}


def _arm(name, restored):
    blocked = tuple(x for x in BAND if x not in set(restored))
    pool = tuple(x for x in M1.ALL if x not in set(BAND))
    a = {"name": name, "blocked": blocked, "pool": pool if blocked else (), "restored": tuple(restored)}; a["_bset"] = frozenset(blocked); return a


D = design()
ARMS = {"U": {"name": "U", "blocked": (), "pool": (), "restored": BAND, "_bset": frozenset()},
        "BAND0": _arm("BAND0", ()), "R128": _arm("R128", (128,)), "RRIGHT": _arm("RRIGHT", D["rright"]), "RWEAK": _arm("RWEAK", D["rweak"])}
ARM_ORDER = ["U", "RRIGHT", "RWEAK", "R128", "BAND0"]


def alphabet(arm) -> set:
    return set(M1.ALL) - set(arm["blocked"])


def predictions() -> dict:
    """From the frozen map only: per arm, exact-copy access, copier-grade-child opportunities, viability mass, branching R0, ordering."""
    v, n = viability()
    hits = json.loads((HERE.parent / "z80atlas" / "census" / "HITS.json").read_text(encoding="utf-8"))["hits"]["vmcopy32"]
    exact = [h for h in hits if h["n_exact_inputs"]]
    out = {}
    for a in ARM_ORDER:
        al = alphabet(ARMS[a]); k = sum(v.get(x, 0) for x in al) / n
        out[a] = {"exact_copy_access_frac_census_exact_copiers": round(sum(1 for h in exact if set(h["exact_inputs"]) & al) / len(exact), 4),
                  "viable_child_inputs_per_128_copier": round(k, 3), "viability_mass": sum(v.get(x, 0) for x in al),
                  "branching_R0": round(LIFETIME * CASE0_PER_EPOCH * k / 256, 3)}
    order = sorted(ARM_ORDER, key=lambda a: -out[a]["viability_mass"])
    return {"per_arm": out, "predicted_ordering": order, "ties": [], "note": "ordinal prediction only; not fitted to ENVGATE-02"}


def spec(schedule: dict, blocks: list) -> dict:
    return {"assay": ASSAY_ID, "design": D, "arms": {k: {"blocked": list(v["blocked"]), "restored": list(v["restored"]), "pool": len(v["pool"])} for k, v in ARMS.items()},
            "schedule": schedule, "blocks": blocks, "streams": "envgate2.{inflow,env,world,mutation}(block)", "core": "archaeon.lineage.core (genetic attribution)",
            "held": "envgate mechanism.HELD (vmcopy32, ENDOGENOUS_COPY, well_mixed 128, implicit_survival, ECHO_forced, local_byte, empty initial ecology)"}


def digest(schedule, blocks) -> str:
    return hashlib.sha256(json.dumps(spec(schedule, blocks), sort_keys=True, default=list).encode()).hexdigest()[:16]
