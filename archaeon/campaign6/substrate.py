"""Substrate-neutral evaluation and rows for the segment loop, built on Proteus's handover
(proteus/graph/handover.py: player_for, meter_for, organism_record_for, descend_for, generate_for,
fingerprint_for). A v0 manifest and a graph manifest go through the same five calls; nothing here
knows which one it holds beyond what the manifest schema says.

    ev  = evaluate_any(manifest, episodes, rng_seed)      # the evaluate() result shape (+ _answers, _asks_per_episode)
    a   = answers_any(manifest, episodes)                 # first output word per ask (from the same run as ev when possible)
    t0, ext = rows_any(manifest, organism_id, parent_id, eval_ordinal, lt, ev, answers, world_features, asks_per_episode)
    pop = gen0_any(profile, N, seed)                      # v0: the campaign FOUNDRY; graph: Proteus's DEFAULT graph foundry
"""
from __future__ import annotations

import hashlib
import json
from typing import List, Optional, Tuple

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.graph.handover import player_for, meter_for, organism_record_for, descend_for, generate_for, fingerprint_for, substrate_of, PROFILES
from proteus.graph import generate as G1
from proteus.eval.fingerprint import _check_forbidden
from archaeon.wse.evolve import FOUNDRY as V0_FOUNDRY
from archaeon.campaign6.observatory.fingerprint import EXT_SCHEMA, EXT_BYTES_MAX, _episode_digests

MASK32 = 0xFFFFFFFF


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


def evaluate_any(manifest: dict, episodes: List, rng_seed: int = 0, reward_mode: str = "per_ask") -> dict:
    """The campaign evaluator's loop over any substrate: same scoring, same result keys; tape-specific
    fields (occupancy, tape writes) are 0 where the substrate has no tape."""
    player = player_for(manifest); meter = meter_for(manifest)
    has_tape = substrate_of(manifest) == "v0"
    glen = getattr(player, "genome_len", 0)
    correct = asks = ep_all = 0
    statuses = {"halt": 0, "yield": 0, "budget": 0, "trap": 0}
    occ = 0; tape_writes = 0; answered = 0
    answers: List[Optional[int]] = []; asks_per_episode: List[int] = []
    per_ask_correct: List[int] = []; per_ask_n: List[int] = []
    for ei, ep in enumerate(episodes):
        ep_correct = ep_asks = 0
        st = player.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        for ti, words in enumerate(ep.ticks):
            player.begin_tick(st)
            before = st["tape"][glen:] if has_tape else None
            outs, status = player.run_tick(st, [words], 1, rng, meter=meter)
            statuses[status] = statuses.get(status, 0) + 1
            if has_tape:
                after = st["tape"][glen:]
                if after != before:
                    tape_writes += sum(1 for a, b in zip(after, before) if a != b)
                occ = max(occ, sum(1 for w in after if w != 0))
            if ti in ep.expected:
                ask_i = sum(1 for t in ep.expected if t < ti)
                while len(per_ask_n) <= ask_i:
                    per_ask_n.append(0); per_ask_correct.append(0)
                per_ask_n[ask_i] += 1; asks += 1; ep_asks += 1
                answers.append(outs[0][0] if outs[0] else None)
                if outs[0]:
                    answered += 1
                    if outs[0][0] == ep.expected[ti]:
                        correct += 1; ep_correct += 1; per_ask_correct[ask_i] += 1
        asks_per_episode.append(ep_asks)
        if ep_asks and ep_correct == ep_asks:
            ep_all += 1
    n = max(1, len(episodes))
    m = meter.as_dict(manifest)
    m = {k: v for k, v in m.items() if k not in ("wall_s", "cpu_s", "gpu")}
    r_ask = correct / max(1, asks); r_ep = ep_all / n
    return {"reward": r_ep if reward_mode == "episode" else r_ask, "reward_per_ask": r_ask, "reward_episode": r_ep, "reward_mode": reward_mode,
            "episodes_all_correct": ep_all, "asks": asks, "correct": correct, "per_ask_reward": [round(c / max(1, k), 4) for c, k in zip(per_ask_correct, per_ask_n)],
            "answered_share": answered / max(1, asks), "meter": m, "ops_per_episode": m.get("ops", 0) / n,
            "persist": manifest.get("persist", manifest.get("persist_state")), "tick_budget": manifest["tick_budget"], "tape_words": manifest.get("tape_words", 0),
            "n_regs": manifest.get("n_regs", 0), "code_writable": manifest.get("code_writable", False), "statuses": statuses,
            "yield_share": statuses["yield"] / max(1, sum(statuses.values())), "tape_occupancy_max": occ, "tape_writes_per_episode": tape_writes / n,
            "intervention": None, "interventions_applied": 0, "faults": m.get("faults", 0), "trapped": False, "substrate": substrate_of(manifest),
            "_answers": answers, "_asks_per_episode": asks_per_episode}


def answers_any(manifest: dict, episodes: List) -> List[Optional[int]]:
    return evaluate_any(manifest, episodes, rng_seed=0)["_answers"]


def rows_any(manifest: dict, organism_id: str, parent_id: Optional[str], eval_ordinal: int, lt: int, ev: dict, answers: List[Optional[int]],
             world_features: Optional[List[str]] = None, asks_per_episode: Optional[List[int]] = None) -> Tuple[dict, dict]:
    vals = [a for a in answers if a is not None]
    id_truncated = False
    try:
        t0 = fingerprint_for(manifest, ev["meter"], organism_id=organism_id, parent_id=parent_id, eval_ordinal=eval_ordinal, logical_time=lt, outputs=[vals])
    except ValueError as exc:
        if "exceeds" not in str(exc):
            raise
        # Proteus's 1 KiB cap: large graph rows plus two 64-hex ids can exceed it by a few bytes; keep the row, shorten the ids
        # (32 hex each keeps them unique for the campaign) and say so in the extension. The full ids are in the segment records.
        id_truncated = True
        t0 = fingerprint_for(manifest, ev["meter"], organism_id=organism_id[:32], parent_id=(parent_id[:32] if parent_id else None), eval_ordinal=eval_ordinal, logical_time=lt, outputs=[vals])
    sub = substrate_of(manifest)
    ext = {"schema": EXT_SCHEMA, "eval": int(eval_ordinal), "organism_id": organism_id, "substrate": sub,
           "action_hist": {"0": len(vals)}, "answered_share": round(len(vals) / max(1, len(answers)), 4), "distinct_answers": len(set(vals)),
           "answers_digest": _h(answers), "answers_first8": answers[:8], "episode_digests": _episode_digests(answers, asks_per_episode),
           "resources_touched": ["in:0"] if ev["meter"].get("in_reads", 0) else [], "env_dependencies": list(world_features or ["stream"]),
           "survival": [k for k in ("halt", "yield", "budget", "trap") if ev["statuses"].get(k, 0)],
           "tape_writes": round(ev.get("tape_writes_per_episode", 0.0), 3), "occupancy_max": ev.get("tape_occupancy_max", 0), "faults": ev.get("faults", 0), "trapped": bool(ev.get("trapped", False)),
           "len_instr": (len(manifest["genome"]) // 4) if sub == "v0" else len(manifest["nodes"]), "persist": str(manifest.get("persist", manifest.get("persist_state"))),
           "n_regs": manifest.get("n_regs", manifest.get("state_words", 0)), "genotype_digest": _h(manifest), "id_truncated": id_truncated}
    _check_forbidden(ext)
    if len(json.dumps(ext, sort_keys=True, separators=(",", ":")).encode()) > EXT_BYTES_MAX:
        raise ValueError("extension exceeds %d bytes" % EXT_BYTES_MAX)
    ext["digest"] = _h(ext)
    return t0, ext


def gen0_any(profile: str, N: int, seed: int) -> List[dict]:
    """Generation-0 manifests for a profile: v0 from the campaign FOUNDRY, graph from Proteus's default graph foundry (no lift from v0 exists)."""
    if profile == "v0":
        fm = dict(V0_FOUNDRY); fm["n"] = N; fm["seed"] = seed
    elif profile == "graph":
        fm = dict(G1.DEFAULT_FOUNDRY_MANIFEST); fm["n"] = N; fm["seed"] = seed
    else:
        raise ValueError(profile)
    return [o["manifest"] for o in generate_for(fm)]


def struct_distance_any(ma: dict, mb: dict) -> float:
    """v0: aligned instruction diff; graph: symmetric difference of node kinds+edges over the union (a connectivity edit distance proxy)."""
    if substrate_of(ma) == "v0" and substrate_of(mb) == "v0":
        ga, gb = ma["genome"], mb["genome"]; n = max(len(ga), len(gb)) // 4
        diff = sum(1 for i in range(0, min(len(ga), len(gb)), 4) if ga[i:i + 4] != gb[i:i + 4])
        return round((diff + abs(len(ga) - len(gb)) // 4) / max(1, n), 6)
    if substrate_of(ma) != substrate_of(mb):
        return 1.0
    sa = {json.dumps(x, sort_keys=True) for x in ma["nodes"]} | {("d", json.dumps(e, sort_keys=True)) for e in ma["data_edges"]} | {("c", json.dumps(e, sort_keys=True)) for e in ma["control_edges"]}
    sb = {json.dumps(x, sort_keys=True) for x in mb["nodes"]} | {("d", json.dumps(e, sort_keys=True)) for e in mb["data_edges"]} | {("c", json.dumps(e, sort_keys=True)) for e in mb["control_edges"]}
    return round(len(sa ^ sb) / max(1, len(sa | sb)), 6)


__all__ = ["evaluate_any", "answers_any", "rows_any", "gen0_any", "struct_distance_any", "player_for", "meter_for", "organism_record_for", "descend_for", "PROFILES", "substrate_of"]
