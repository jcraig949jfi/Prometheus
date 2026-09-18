"""evaluate_b: the campaign evaluator (archaeon.wse.evolve.evaluate) run through PlayerB.

Identical scoring, statuses and telemetry, plus fault accounting. In FAIL mode a trap ends the
evaluation: every episode from the trap onward is unscored (reward 0 for the whole evaluation,
`trapped` true, `trap_episode`/`trap_tick` recorded). In FIZZLE mode faults are counted and the
program continues. No interventions (Phase B does not use them).
"""
from __future__ import annotations

from typing import List

from proteus.foundry.prng import SplitMix64, seed_from

from .vm_b import PlayerB, MeterB, static_validity


def evaluate_b(manifest: dict, episodes: List, rng_seed: int = 0, reward_mode: str = "per_ask", mode: str = "FAIL") -> dict:
    player = PlayerB(manifest, mode)
    meter = MeterB()
    glen = player.genome_len
    correct = asks = ep_all = 0
    statuses = {"halt": 0, "yield": 0, "budget": 0, "trap": 0}
    occupancy_max = 0; tape_writes = 0; answered = 0
    per_ask_correct: List[int] = []; per_ask_n: List[int] = []
    trapped = False; trap_at = None
    first_fault = None
    for ei, ep in enumerate(episodes):
        if trapped:
            break
        ep_correct = ep_asks = 0
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        for ti, words in enumerate(ep.ticks):
            player.begin_tick(st)
            before = st["tape"][glen:]
            f0 = meter.faults
            outs, status = player.run_tick(st, [words], 1, rng, meter=meter)
            if meter.faults > f0 and first_fault is None:
                first_fault = {"episode": ei, "tick": ti}
            statuses[status] += 1
            if status == "trap":
                trapped = True; trap_at = {"episode": ei, "tick": ti}
                break
            after = st["tape"][glen:]
            if after != before:
                tape_writes += sum(1 for a, b in zip(after, before) if a != b)
            occ = sum(1 for w in after if w != 0)
            if occ > occupancy_max:
                occupancy_max = occ
            if ti in ep.expected:
                ask_i = sum(1 for t in ep.expected if t < ti)
                while len(per_ask_n) <= ask_i:
                    per_ask_n.append(0); per_ask_correct.append(0)
                per_ask_n[ask_i] += 1
                asks += 1; ep_asks += 1
                if outs[0]:
                    answered += 1
                    if outs[0][0] == ep.expected[ti]:
                        correct += 1; ep_correct += 1; per_ask_correct[ask_i] += 1
        if ep_asks and ep_correct == ep_asks and not trapped:
            ep_all += 1
    n = max(1, len(episodes))
    m = meter.as_dict(manifest)
    total_asks = sum(ep.n_asks() for ep in episodes)
    if trapped:
        r_ask, r_ep, answered_share = 0.0, 0.0, 0.0
    else:
        r_ask = correct / max(1, asks); r_ep = ep_all / n; answered_share = answered / max(1, asks)
    return {
        "reward": r_ep if reward_mode == "episode" else r_ask,
        "reward_per_ask": r_ask, "reward_episode": r_ep, "reward_mode": reward_mode,
        "episodes_all_correct": ep_all if not trapped else 0, "asks": total_asks, "correct": correct if not trapped else 0,
        "per_ask_reward": [round(c / max(1, k), 4) for c, k in zip(per_ask_correct, per_ask_n)] if not trapped else [],
        "answered_share": answered_share, "meter": m, "ops_per_episode": m["ops"] / n,
        "persist": manifest["persist"], "tick_budget": manifest["tick_budget"], "tape_words": manifest["tape_words"],
        "n_regs": manifest["n_regs"], "code_writable": manifest["code_writable"],
        "statuses": statuses, "yield_share": statuses["yield"] / max(1, sum(statuses.values())),
        "tape_occupancy_max": occupancy_max, "tape_writes_per_episode": tape_writes / n,
        "intervention": None, "interventions_applied": 0,
        "mode": mode, "trapped": trapped, "trap_at": trap_at, "faults": m["faults"], "fault_sites": m["fault_sites"],
        "fault_ticks": m["fault_ticks"], "first_fault": first_fault, "static": static_validity(manifest),
    }
