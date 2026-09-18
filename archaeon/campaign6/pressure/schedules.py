"""AXIS P -- pressure schedules (Campaign 6 item 4). A schedule is a list of SEGMENTS over generations,
each changing one or more world parameters (the composed world's params, or the fitness map via
`reward_scale`), composed from eight kinds:

  stable          nothing changes
  step            a parameter jumps to a new value at from_gen
  drift           a parameter moves linearly from a to b over the segment
  periodic        a parameter alternates between two values with period p
  catastrophe     a one-generation collapse (e.g. regen -> 0, hazard cost x4) then recovery to the
                  previous value
  redistribution  pools' nominal richness is permuted (which resource is rich)
  migration       a share of the population is replaced by organisms from a donor run (the loop
                  applies it; the schedule only names it)
  temporary       a window [from, to) with a bonus parameter, then back

Two generators: `labeled(seed, kinds=...)` composes named kinds; `unlabeled(seed)` is a seeded
random walk over (parameter, magnitude, duration) with NO kind label (the directive: "some schedules
deliberately generated without a semantic label"). Both produce the same record shape and the
exact realized history is what the loop writes per generation. EXOGENOUS_PRESSURE = every change
the schedule applies; ENDOGENOUS_PRESSURE is written by the loop from what the population did to
the world (coupling depletion, signals, objects), never by this module.

    params_g, events = apply(schedule, base_params, g)
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Dict, List, Tuple

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.campaign6 import schemas as S

GENERATOR = "archaeon.c6.pressure_gen"
VERSION = "0.1"
KINDS = ("stable", "step", "drift", "periodic", "catastrophe", "redistribution", "migration", "temporary")
# parameters a schedule may move: (path in params, low, high)
TARGETS = {
    "resources.regen": (0.0, 0.4), "resources.deplete": (0.1, 0.95), "hazards.cost": (0.0, 0.8), "hidden.noise": (0.0, 0.8),
    "delayed.d": (1, 8), "objects.bonus": (0.0, 1.5), "ticks": (8, 48), "reward_scale": (0.25, 2.0),
}


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def _get(params: dict, path: str):
    cur = params
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _set(params: dict, path: str, value) -> bool:
    keys = path.split("."); cur = params
    for k in keys[:-1]:
        if not isinstance(cur, dict) or k not in cur:
            return False
        cur = cur[k]
    if not isinstance(cur, dict):
        return False
    if keys[-1] in ("d", "ticks"):
        value = int(round(value))
    cur[keys[-1]] = value
    return True


def _val(rng: SplitMix64, lo, hi):
    if isinstance(lo, int) and isinstance(hi, int):
        return rng.randint(lo, hi)
    return round(lo + (hi - lo) * (rng.next_u32() / 2 ** 32), 3)


def labeled(seed: int, horizon: int, *, lane: str = "PROCEDURAL", n_segments: int | None = None) -> dict:
    rng = SplitMix64(seed_from(GENERATOR, VERSION, "labeled", seed))
    n = n_segments if n_segments is not None else rng.randint(1, 6)
    segs = []; g = 0
    for i in range(n):
        kind = KINDS[rng.randbelow(len(KINDS))]
        length = max(1, rng.randint(horizon // (2 * n) if n else 1, max(1, horizon // n)))
        target = list(TARGETS)[rng.randbelow(len(TARGETS))]; lo, hi = TARGETS[target]
        seg = {"from_gen": g, "to_gen": min(horizon, g + length), "kind": "EXOGENOUS_PRESSURE", "label": kind, "target": target, "params": {}}
        if kind == "step":
            seg["params"] = {"value": _val(rng, lo, hi)}
        elif kind == "drift":
            seg["params"] = {"a": _val(rng, lo, hi), "b": _val(rng, lo, hi)}
        elif kind == "periodic":
            seg["params"] = {"lo": _val(rng, lo, hi), "hi": _val(rng, lo, hi), "period": rng.randint(2, 16)}
        elif kind == "catastrophe":
            seg["params"] = {"at": g + rng.randbelow(max(1, length)), "value": lo}
        elif kind == "redistribution":
            seg["params"] = {"permutation_seed": rng.next_u32()}
        elif kind == "migration":
            seg["params"] = {"share": round(0.05 + 0.25 * rng.next_u32() / 2 ** 32, 3), "at": g + rng.randbelow(max(1, length))}
        elif kind == "temporary":
            seg["params"] = {"value": _val(rng, lo, hi), "until": min(horizon, g + max(1, length // 2))}
        segs.append(seg); g = seg["to_gen"]
        if g >= horizon:
            break
    prov = S.provenance(lane, GENERATOR, VERSION, seed, {"mode": "labeled", "horizon": horizon, "n_segments": len(segs)})
    return {"schema": "archaeon.c6.pressure_schedule.v1", "mode": "labeled", "horizon": horizon, "segments": segs, "provenance": prov, "schedule_id": _h(segs)}


def unlabeled(seed: int, horizon: int, *, lane: str = "PROCEDURAL", step_every: int = 8) -> dict:
    """A seeded random walk: every `step_every` generations one target moves by a random magnitude; no kind label."""
    rng = SplitMix64(seed_from(GENERATOR, VERSION, "unlabeled", seed))
    segs = []; g = 0
    while g < horizon:
        target = list(TARGETS)[rng.randbelow(len(TARGETS))]; lo, hi = TARGETS[target]
        segs.append({"from_gen": g, "to_gen": min(horizon, g + step_every), "kind": "EXOGENOUS_PRESSURE", "label": "unlabeled", "target": target,
                     "params": {"value": _val(rng, lo, hi)}})
        g += step_every
    prov = S.provenance(lane, GENERATOR, VERSION, seed, {"mode": "unlabeled", "horizon": horizon, "step_every": step_every})
    return {"schema": "archaeon.c6.pressure_schedule.v1", "mode": "unlabeled", "horizon": horizon, "segments": segs, "provenance": prov, "schedule_id": _h(segs)}


def stable(horizon: int) -> dict:
    segs = [{"from_gen": 0, "to_gen": horizon, "kind": "EXOGENOUS_PRESSURE", "label": "stable", "target": None, "params": {}}]
    prov = S.provenance("HUMAN_DIRECTED", GENERATOR, VERSION, 0, {"mode": "stable", "horizon": horizon}, note="Phase 0 control: no pressure change")
    return {"schema": "archaeon.c6.pressure_schedule.v1", "mode": "stable", "horizon": horizon, "segments": segs, "provenance": prov, "schedule_id": _h(segs)}


def apply(schedule: dict, base_params: dict, g: int) -> Tuple[dict, List[dict]]:
    """World params at generation g and the EXOGENOUS events realized AT g (empty when nothing changes at g).
    reward_scale is returned in params['reward_scale'] for the loop to apply to the fitness map."""
    p = copy.deepcopy(base_params); p.setdefault("reward_scale", 1.0)
    events = []
    for seg in schedule["segments"]:
        if not (seg["from_gen"] <= g < seg["to_gen"]) or seg["label"] == "stable":
            continue
        t = seg["target"]; lab = seg["label"]; sp = seg["params"]
        before = _get(p, t) if t != "reward_scale" else p["reward_scale"]
        value = None
        if lab in ("step", "unlabeled"):
            value = sp["value"]
        elif lab == "drift":
            span = max(1, seg["to_gen"] - seg["from_gen"]); value = round(sp["a"] + (sp["b"] - sp["a"]) * (g - seg["from_gen"]) / span, 4)
        elif lab == "periodic":
            value = sp["lo"] if ((g - seg["from_gen"]) // sp["period"]) % 2 == 0 else sp["hi"]
        elif lab == "catastrophe":
            value = sp["value"] if g == sp["at"] else None
        elif lab == "temporary":
            value = sp["value"] if g < sp["until"] else None
        elif lab == "redistribution":
            p["redistribution_seed"] = sp["permutation_seed"]
            if g == seg["from_gen"]:
                events.append({"generation": g, "kind": "EXOGENOUS_PRESSURE", "label": lab, "target": "pools", "before": None, "after": sp["permutation_seed"], "schedule_id": schedule["schedule_id"]})
            continue
        elif lab == "migration":
            if g == sp["at"]:
                p["migration"] = {"share": sp["share"]}
                events.append({"generation": g, "kind": "EXOGENOUS_PRESSURE", "label": lab, "target": "population", "before": None, "after": sp["share"], "schedule_id": schedule["schedule_id"]})
            continue
        if value is None:
            continue
        if t == "reward_scale":
            p["reward_scale"] = value; applied = True
        else:
            applied = _set(p, t, value)
        if applied and (before != value) and (g == seg["from_gen"] or lab in ("drift", "periodic", "unlabeled", "catastrophe") or (lab == "temporary" and g == seg["from_gen"])):
            events.append({"generation": g, "kind": "EXOGENOUS_PRESSURE", "label": lab, "target": t, "before": before, "after": value, "schedule_id": schedule["schedule_id"]})
    return p, events


def self_test() -> int:
    from archaeon.campaign6.worlds import sample_world
    rep = {}
    a = labeled(3, 200); b = labeled(3, 200); rep["labeled_deterministic"] = a["schedule_id"] == b["schedule_id"]
    u = unlabeled(5, 200); rep["unlabeled_has_no_kind_label"] = all(s["label"] == "unlabeled" for s in u["segments"])
    rep["kinds_seen_over_50_seeds"] = sorted({s["label"] for i in range(50) for s in labeled(i, 200)["segments"]})
    w = sample_world(11, bin_target=8); base = w["params"]
    hist = []; changed = 0
    for g in range(200):
        pg, ev = apply(a, base, g); hist += ev; changed += pg != base
    rep["labeled_events"] = len(hist); rep["generations_changed"] = changed
    pg0, _ = apply(a, base, 0); rep["base_untouched"] = base == w["params"]
    # exact history is reproducible
    hist2 = [e for g in range(200) for e in apply(a, base, g)[1]]
    rep["history_reproducible"] = hist == hist2
    hu = [e for g in range(200) for e in apply(u, base, g)[1]]; rep["unlabeled_events"] = len(hu)
    st = stable(50); rep["stable_events"] = sum(len(apply(st, base, g)[1]) for g in range(50))
    print(json.dumps(rep, indent=1))
    return 0 if (rep["labeled_deterministic"] and rep["unlabeled_has_no_kind_label"] and rep["base_untouched"] and rep["history_reproducible"] and rep["stable_events"] == 0 and rep["labeled_events"] > 0) else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
