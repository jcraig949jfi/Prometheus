"""T0 row assembly for the v0 (tape VM) profile: Proteus's proteus.behavior_fingerprint.v1 emitter
is THE row (D6-008); this module adds the world-side extension record and the frozen distances.

    t0, ext = rows_v0(manifest, organism_id, parent_id, eval_ordinal, lt, ev, answers, world_features)
    spread  = spread_from([(t0, ext), ...])       # per-field MAD over the calibration set, frozen with thresholds
    d       = fp_distance((t0a, exta), (t0b, extb), spread)
    s       = struct_distance(manifest_a, manifest_b)

Nothing in either record carries a reward: Proteus's emitter refuses reward-shaped keys and the
extension is checked by the same rule. Reward lives in the archived-generation observation.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Dict, List, Optional, Tuple

from proteus.eval.fingerprint import fingerprint as _proteus_row, from_v0_meter, _check_forbidden

EXT_SCHEMA = "archaeon.c6.world_ext.v1"
EXT_BYTES_MAX = 1024


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def _episode_digests(answers, asks_per_episode) -> List[str]:
    if not asks_per_episode:
        return [_h(answers)[:6]]
    out, i = [], 0
    for n in asks_per_episode:
        out.append(_h(answers[i:i + n])[:6]); i += n
    return out


def rows_v0(manifest: dict, organism_id: str, parent_id: Optional[str], eval_ordinal: int, lt: int, ev: dict,
            answers: List[Optional[int]], world_features: Optional[List[str]] = None, asks_per_episode: Optional[List[int]] = None) -> Tuple[dict, dict]:
    """asks_per_episode: answer slots per episode (episode digests need it); absent -> one digest over all."""
    behaviour = from_v0_meter(ev["meter"])
    behaviour["statuses"] = {k: v for k, v in ev["statuses"].items() if v}
    t0 = _proteus_row(organism_id=organism_id, parent_id=parent_id, eval_ordinal=eval_ordinal, logical_time=lt, behaviour=behaviour,
                      outputs=[[a for a in answers if a is not None]])
    vals = [a for a in answers if a is not None]
    ext = {
        "schema": EXT_SCHEMA, "eval": int(eval_ordinal), "organism_id": organism_id,
        "action_hist": {"0": len(vals)},
        "answered_share": round(len(vals) / max(1, len(answers)), 4), "distinct_answers": len(set(vals)),
        "answers_digest": _h(answers), "answers_first8": answers[:8],
        "episode_digests": _episode_digests(answers, asks_per_episode),
        "resources_touched": ["in:0"] if ev["meter"].get("in_reads", 0) else [],
        "env_dependencies": list(world_features or ["stream"]),
        "survival": [k for k in ("halt", "yield", "budget", "trap") if ev["statuses"].get(k, 0)],
        "tape_writes": round(ev.get("tape_writes_per_episode", 0.0), 3), "occupancy_max": ev.get("tape_occupancy_max", 0),
        "faults": ev.get("faults", 0), "trapped": bool(ev.get("trapped", False)),
        "len_instr": len(manifest["genome"]) // 4, "persist": manifest["persist"], "n_regs": manifest["n_regs"],
        "genotype_digest": _h({"genome": manifest["genome"], "n_regs": manifest["n_regs"], "tape_words": manifest["tape_words"], "persist": manifest["persist"]}),
    }
    _check_forbidden(ext)
    if len(json.dumps(ext, sort_keys=True, separators=(",", ":")).encode()) > EXT_BYTES_MAX:
        raise ValueError("extension exceeds %d bytes" % EXT_BYTES_MAX)
    ext["digest"] = _h(ext)
    return t0, ext


NUMERIC_T0 = ("ops", "branches_taken", "in_reads", "out_writes", "out_dropped", "rnd_draws", "budget_exhausted_ticks", "ticks", "code_region_writes")
NUMERIC_EXT = ("answered_share", "distinct_answers", "tape_writes", "occupancy_max", "faults")
CATEGORIES = ("halt_yield", "read_write", "indirection", "arithmetic", "logical", "comparison", "control", "opaque_io", "randomness")
# round 3 (D6-009): what the organism DID (episode answer digests, answered share, distinct answers) carries the distance;
# execution counts and category counts are tie-breakers (a loop running longer is not new behaviour)
DEFAULT_WEIGHTS = {**{k: 0.1 for k in NUMERIC_T0}, **{k: 0.1 for k in NUMERIC_EXT}, "answered_share": 1.0, "distinct_answers": 1.0,
                   **{"cat_" + c: 0.05 for c in CATEGORIES}, "answers": 2.0}


def numeric_vector(pair: Tuple[dict, dict]) -> Dict[str, float]:
    """Counts enter on a log1p scale (ops range 1e0..1e5); shares stay linear."""
    t0, ext = pair
    b = t0["behaviour"]
    v = {k: math.log1p(float(b.get(k, 0))) for k in NUMERIC_T0}
    v.update({k: (float(ext.get(k, 0)) if k == "answered_share" else math.log1p(float(ext.get(k, 0)))) for k in NUMERIC_EXT})
    cats = b.get("ops_by_category", {})
    v.update({"cat_" + c: math.log1p(float(cats.get(c, 0))) for c in CATEGORIES})
    return v


def episode_displacement(ea: dict, eb: dict) -> float:
    """Share of episodes whose answer sequence differs (1.0 when the partitions differ)."""
    da, db = ea.get("episode_digests", []), eb.get("episode_digests", [])
    if len(da) != len(db) or not da:
        return 1.0
    return sum(1 for x, y in zip(da, db) if x != y) / len(da)


def spread_from(pairs: List[Tuple[dict, dict]]) -> Dict[str, float]:
    keys = list(numeric_vector(pairs[0]).keys())
    out = {}
    for k in keys:
        xs = sorted(numeric_vector(p)[k] for p in pairs)
        med = xs[len(xs) // 2]
        mad = sorted(abs(x - med) for x in xs)[len(xs) // 2]
        out[k] = max(mad, 0.05 if k == "answered_share" else 0.1)     # log-count floor .1 (~10% change); shares .05 (frozen with the thresholds)
    return out


def fp_distance(a: Tuple[dict, dict], b: Tuple[dict, dict], spread: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    w = weights or DEFAULT_WEIGHTS
    va, vb = numeric_vector(a), numeric_vector(b)
    d = sum(w.get(k, 1.0) * abs(va[k] - vb[k]) / spread[k] for k in va)
    ea, eb = a[1], b[1]
    d += w.get("answers", 2.0) * episode_displacement(ea, eb) * 10.0      # the dominant term: what the organism DID, per episode
    return round(d, 6)


def struct_distance(ma: dict, mb: dict) -> float:
    """v0 genomes: differing aligned instructions + length delta, over the longer length."""
    ga, gb = ma["genome"], mb["genome"]
    n = max(len(ga), len(gb)) // 4
    diff = sum(1 for i in range(0, min(len(ga), len(gb)), 4) if ga[i:i + 4] != gb[i:i + 4])
    return round((diff + abs(len(ga) - len(gb)) // 4) / max(1, n), 6)
