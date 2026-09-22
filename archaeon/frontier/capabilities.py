"""Machine-readable capabilities (operator directive s4). An experiment declares required_capabilities;
the scheduler compares against present() and marks BLOCKED_MISSING_CAPABILITY without any prose.

Each capability is a probe that either imports/instantiates the thing or fails. Probes are cheap and
run once per scheduler start; the result is written into every receipt.
"""
from __future__ import annotations

import importlib
from typing import Dict


def _probe_v0_runtime() -> bool:
    from proteus.foundry.vm import Player  # noqa: F401
    return True


def _probe_graph_runtime() -> bool:
    from proteus.graph.handover import player_for, generate_for  # noqa: F401
    from proteus.graph import generate as G1
    fm = dict(G1.DEFAULT_FOUNDRY_MANIFEST); fm["n"] = 1; fm["seed"] = 0
    return len(generate_for(fm)) == 1


def _probe_repb_fizzle() -> bool:
    from archaeon.campaign5.repb.evaluate_b import evaluate_b  # noqa: F401
    from archaeon.campaign5.repb.grammar_b import descend_b  # noqa: F401
    return True


def _probe_composed_world_v1() -> bool:
    from archaeon.campaign6.worlds import sample_world, world_from_record
    r = sample_world(1); return world_from_record(r).world_id() == r["world_id"]


def _probe_wse_worldspec() -> bool:
    from archaeon.campaign4 import c4_01 as C1
    return "W0" in C1.ENVS


def _probe_pressure_schedules_v1() -> bool:
    from archaeon.campaign6.pressure import schedules as P
    return P.labeled(1, 10)["schedule_id"] == P.labeled(1, 10)["schedule_id"]


def _probe_detectors_v1() -> bool:
    from archaeon.campaign6.observatory import detectors as D
    from pathlib import Path
    import json
    f = Path(__file__).resolve().parents[1] / "campaign6" / "observatory" / "DETECTORS_FROZEN_candidate.json"
    return len(D.IN_LOOP) == 9 and f.exists() and "digest" in json.loads(f.read_text(encoding="utf-8"))


def _probe_c4_parents() -> bool:
    from archaeon.campaign4 import c4_01 as C1
    return len(C1.parents_from_population()) == 57


def _probe_segment_v1() -> bool:
    from archaeon.campaign6 import segment as SG
    return callable(SG.run_segment)


PROBES = {
    "v0_runtime": _probe_v0_runtime, "graph_runtime": _probe_graph_runtime, "repb_fizzle": _probe_repb_fizzle,
    "composed_world_v1": _probe_composed_world_v1, "wse_worldspec": _probe_wse_worldspec, "pressure_schedules_v1": _probe_pressure_schedules_v1,
    "detectors_v1": _probe_detectors_v1, "c4_parents": _probe_c4_parents, "segment_v1": _probe_segment_v1,
}


def present() -> Dict[str, bool]:
    out = {}
    for name, fn in PROBES.items():
        try:
            out[name] = bool(fn())
        except Exception as exc:                                        # noqa: BLE001  a failed probe is an absent capability, recorded
            out[name] = False
            out[name + ".error"] = str(exc)[:160]
    return out


def missing(required, caps: Dict[str, bool]) -> list:
    return sorted(c for c in required if not caps.get(c, False))


if __name__ == "__main__":
    import json
    print(json.dumps(present(), indent=1))
