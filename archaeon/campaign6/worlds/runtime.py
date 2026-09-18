"""AXIS W -- composed worlds (Campaign 6 item 3). A world is a composition of FEATURE modules over a
tick-based episode with FEEDBACK: the organism's outputs at tick t change the world state that
produces its inputs at tick t+1. The organism interface is unchanged (opaque input channels of
32-bit words, opaque output channels); the world decides what the words mean.

Features (each on/off with parameters; a world may have 0..10 of them):
  resources      R pool types with amounts; HARVEST (channel 0 = pool index) yields the pool's
                 current value; depletion per harvest; regeneration per tick
  locality       L nodes on a ring/graph; the organism has a position; MOVE (channel 1) walks to
                 a neighbour; pools/objects/hazards are AT nodes; the organism observes only its node
  objects        M manipulable cells; WRITE (channel 2 = value) sets the cell at the position;
                 a cell's value pays when later READ by the same or another organism
  delayed        actions take effect after d ticks (a consequence queue)
  hidden         a latent parameter (which pool is rich) observed only through a noisy/lagged channel
  hazards        some nodes carry a hazard state; standing there costs reward or ends the episode
  history        an opportunity whose value depends on the organism's past (a pool that pays only
                 after k prior harvests elsewhere)
  coupling       pools and object cells are SHARED across the organisms of one generation
                 (evaluated in sequence): one organism's harvest depletes what the next sees --
                 the ENDOGENOUS pressure source; a SIGNAL (channel 3) writes a shared word
  regime         parameters change at tick boundaries inside an episode (the Axis P slice)
  channels       K output channels are read; unused channels are ignored

Determinism: all randomness from SplitMix64 seeded by (world seed, episode index); the organism's
random stream is the evaluator's, as in the v0 evaluator.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player, Meter
from proteus.graph.handover import player_for, meter_for

MASK32 = 0xFFFFFFFF
FEATURES = ("resources", "locality", "objects", "delayed", "hidden", "hazards", "history", "coupling", "regime", "channels")
SCHEMA = "archaeon.c6.world_composed.v1"


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


class ComposedWorld:
    """Immutable composition. `params` is the generator's record; world_id is its digest."""

    def __init__(self, params: dict):
        self.params = params
        self.name = params.get("name", "cw_" + _h(params))
        self.features = [f for f in FEATURES if params.get(f, {}).get("on") and not (f == "channels" and params.get(f, {}).get("k", 1) < 2)]
        self.R = params.get("resources", {}).get("types", 1) if "resources" in self.features else 1
        self.L = params.get("locality", {}).get("nodes", 1) if "locality" in self.features else 1
        self.M = params.get("objects", {}).get("cells", 0) if "objects" in self.features else 0
        self.K = params.get("channels", {}).get("k", 1) if params.get("channels", {}).get("on") else 1
        self.ticks = params.get("ticks", 24)

    def world_id(self) -> str:
        return _h({"schema": SCHEMA, **self.params})

    def knobs(self) -> dict:
        return dict(self.params)

    def complexity_bin(self) -> int:
        return len(self.features)

    # ---------------------------------------------------------------- episode state
    def reset(self, seed: int, ep: int, shared: Optional[dict] = None) -> dict:
        rng = SplitMix64(seed_from("c6.world", self.world_id(), seed, ep))
        p = self.params
        st = {"tick": 0, "pos": 0, "reward": 0.0, "max_reward": 0.0, "alive": True, "rng": rng,
              "pools": [], "pool_node": [], "regen": 0.0, "deplete": 0.0, "cells": [], "cell_node": [], "queue": [], "hidden": 0, "hazard_nodes": set(),
              "history_count": 0, "harvests": 0, "actions": {}, "touched": set(), "objects_changed": 0, "deps": set(), "died": False, "moves": 0, "signals": 0}
        if "resources" in self.features:
            r = p["resources"]; st["regen"] = r.get("regen", 0.1); st["deplete"] = r.get("deplete", 0.5)
            st["pools"] = [1.0 + rng.randbelow(4) * 0.25 for _ in range(self.R)]
            st["pool_node"] = [rng.randbelow(self.L) for _ in range(self.R)]
        if "hidden" in self.features and st["pools"]:
            st["hidden"] = rng.randbelow(self.R); st["pools"][st["hidden"]] = 3.0
        if "objects" in self.features:
            st["cells"] = [0] * self.M; st["cell_node"] = [rng.randbelow(self.L) for _ in range(self.M)]
        if "hazards" in self.features:
            n_h = max(1, self.L // 4); st["hazard_nodes"] = {rng.randbelow(self.L) for _ in range(n_h)}
        st["max_reward"] = max(1e-9, self.ticks * (max(st["pools"]) if st["pools"] else 1.0))
        if shared is not None and "coupling" in self.features:
            if "pools" in shared:
                st["pools"] = shared["pools"]                     # the same list object: depletion is visible to the next organism
            else:
                shared["pools"] = st["pools"]
            if "cells" in shared:
                st["cells"] = shared["cells"]
            else:
                shared["cells"] = st["cells"]
            st["signal"] = shared.setdefault("signal", [0])
        else:
            st["signal"] = [0]
        return st

    def observe(self, st: dict) -> List[List[int]]:
        """One input channel of words: [tick, pos, local pool amounts (x1000) or 0, local cells, hazard flag, noisy hidden hint, signal]."""
        p = self.params; rng = st["rng"]
        words = [st["tick"], st["pos"]]
        st["deps"].add("tick")
        if "resources" in self.features:
            for i, amt in enumerate(st["pools"]):
                local = ("locality" not in self.features) or st["pool_node"][i] == st["pos"]
                words.append(int(amt * 1000) & MASK32 if local else 0)
            st["deps"].add("resources")
        if "objects" in self.features:
            for j, v in enumerate(st["cells"]):
                local = ("locality" not in self.features) or st["cell_node"][j] == st["pos"]
                words.append(v & MASK32 if local else 0)
            st["deps"].add("objects")
        if "hazards" in self.features:
            words.append(1 if st["pos"] in st["hazard_nodes"] else 0); st["deps"].add("hazards")
        if "hidden" in self.features:
            noise = p["hidden"].get("noise", 0.25)
            hint = st["hidden"] if rng.randbelow(1000) >= int(noise * 1000) else rng.randbelow(max(1, self.R))
            words.append(hint); st["deps"].add("hidden")
        if "coupling" in self.features:
            words.append(st["signal"][0] & MASK32); st["deps"].add("signal")
        return [words]

    def act(self, st: dict, outputs: List[List[int]]) -> None:
        """Apply the organism's outputs for this tick, then advance the world one tick."""
        p = self.params
        acts = {}
        for ch in range(min(self.K, len(outputs))):
            if outputs[ch]:
                acts[ch] = outputs[ch][0] & MASK32
                st["actions"][ch] = st["actions"].get(ch, 0) + 1
        if "delayed" in self.features:
            d = p["delayed"].get("d", 2)
            st["queue"].append((st["tick"] + d, acts)); acts = {}
            while st["queue"] and st["queue"][0][0] <= st["tick"]:
                _, a = st["queue"].pop(0); acts = {**acts, **a}
        # MOVE
        if "locality" in self.features and 1 in acts:
            step = 1 if acts[1] % 2 == 0 else -1
            st["pos"] = (st["pos"] + step) % self.L; st["moves"] += 1
        # HARVEST
        if "resources" in self.features and 0 in acts and st["pools"]:
            i = acts[0] % self.R
            local = ("locality" not in self.features) or st["pool_node"][i] == st["pos"]
            if local:
                gain = st["pools"][i]
                if "history" in self.features:
                    k = p["history"].get("k", 3); target = p["history"].get("pool", 0) % self.R
                    if i == target and st["history_count"] < k:
                        gain = 0.0                                   # pays only after k harvests elsewhere
                    elif i != target:
                        st["history_count"] += 1
                st["reward"] += gain; st["pools"][i] = max(0.0, st["pools"][i] * (1.0 - st["deplete"])); st["harvests"] += 1
                st["touched"].add("pool:%d" % i)
        # WRITE object
        if "objects" in self.features and 2 in acts and st["cells"]:
            j = acts[2] % self.M
            local = ("locality" not in self.features) or st["cell_node"][j] == st["pos"]
            if local:
                v = (acts[2] >> 8) & 0xFFFF
                if st["cells"][j] != v:
                    st["cells"][j] = v; st["objects_changed"] += 1; st["touched"].add("cell:%d" % j)
                # a cell holding the hidden index pays a bonus when written (history-conditioned opportunity)
                if "hidden" in self.features and v == st["hidden"]:
                    st["reward"] += p["objects"].get("bonus", 0.5)
        # SIGNAL
        if "coupling" in self.features and 3 in acts:
            st["signal"][0] = acts[3]; st["signals"] += 1
        # hazard
        if "hazards" in self.features and st["pos"] in st["hazard_nodes"]:
            cost = p["hazards"].get("cost", 0.25)
            st["reward"] -= cost
            if p["hazards"].get("lethal") and st["rng"].randbelow(4) == 0:
                st["alive"] = False; st["died"] = True
        # regeneration, regime, tick
        if "resources" in self.features:
            pools = st["pools"]
            for i, a in enumerate(pools):
                pools[i] = min(3.0, a + st["regen"])
        if "regime" in self.features:
            every = p["regime"].get("every", 8)
            if every and st["tick"] and st["tick"] % every == 0:
                st["regen"] = st["regen"] * p["regime"].get("regen_factor", 0.5)
                if st["pools"]:
                    st["pools"].reverse(); st["pool_node"].reverse()
        st["tick"] += 1

    def done(self, st: dict) -> bool:
        return (not st["alive"]) or st["tick"] >= self.ticks


def evaluate_world(manifest: dict, world: ComposedWorld, seed: int, E: int, rng_seed: int = 0, shared: Optional[dict] = None,
                   player_factory=None) -> dict:
    """The interactive evaluator: same result shape as archaeon.wse.evolve.evaluate (reward, reward_per_ask, meter, statuses, ...)
    plus the world-side fields the extension needs. `shared` (per generation) carries coupling state across organisms."""
    player = player_factory(manifest) if player_factory else player_for(manifest)
    meter = meter_for(manifest)
    glen = getattr(player, "genome_len", 0); has_tape = "genome" in manifest
    statuses = {"halt": 0, "yield": 0, "budget": 0, "trap": 0}
    total = 0.0; max_total = 0.0; occ = 0; tape_writes = 0
    answers: List[Optional[int]] = []; asks_per_episode: List[int] = []
    action_hist: Dict[str, int] = {}; touched = set(); deps = set(); objects_changed = 0; died = 0; moves = 0; signals = 0
    for ep in range(E):
        st = world.reset(seed, ep, shared)
        vm = player.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ep))
        n_ask = 0
        while not world.done(st):
            inputs = world.observe(st)
            player.begin_tick(vm)
            before = vm["tape"][glen:] if has_tape else None
            outs, status = player.run_tick(vm, inputs, world.K, rng, meter=meter)
            statuses[status] = statuses.get(status, 0) + 1
            if has_tape:
                after = vm["tape"][glen:]
                if after != before:
                    tape_writes += sum(1 for a, b in zip(after, before) if a != b)
                occ = max(occ, sum(1 for w in after if w != 0))
            answers.append(outs[0][0] if outs and outs[0] else None); n_ask += 1
            world.act(st, outs)
            if status == "trap":
                break
        asks_per_episode.append(n_ask)
        total += max(0.0, st["reward"]); max_total += st["max_reward"]
        for ch, n in st["actions"].items():
            action_hist[str(ch)] = action_hist.get(str(ch), 0) + n
        touched |= st["touched"]; deps |= st["deps"]; objects_changed += st["objects_changed"]; died += st["died"]; moves += st["moves"]; signals += st["signals"]
    m = {k: v for k, v in meter.as_dict(manifest).items() if k not in ("wall_s", "cpu_s", "gpu")}
    reward = min(1.0, total / max(1e-9, max_total))
    answered = sum(1 for a in answers if a is not None) / max(1, len(answers))
    return {"reward": reward, "reward_per_ask": reward, "reward_episode": reward, "reward_mode": "world", "asks": len(answers), "correct": None,
            "answered_share": answered, "meter": m, "ops_per_episode": m["ops"] / max(1, E), "persist": manifest.get("persist", manifest.get("persist_state")), "tick_budget": manifest["tick_budget"],
            "tape_words": manifest.get("tape_words", 0), "n_regs": manifest.get("n_regs", manifest.get("state_words", 0)), "code_writable": manifest.get("code_writable", False), "statuses": statuses,
            "yield_share": statuses["yield"] / max(1, sum(statuses.values())), "tape_occupancy_max": occ, "tape_writes_per_episode": tape_writes / max(1, E),
            "intervention": None, "interventions_applied": 0, "faults": 0, "trapped": False,
            "_answers": answers, "_asks_per_episode": asks_per_episode,
            "world": {"action_hist": action_hist, "resources_touched": sorted(touched), "env_dependencies": sorted(deps), "objects_changed": objects_changed,
                      "survival": ["died"] if died else ["survived"], "moves": moves, "signals": signals, "died_episodes": died, "features": world.features}}
