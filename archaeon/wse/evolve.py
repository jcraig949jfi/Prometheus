"""Evaluation and selection over Proteus players (the part Proteus by charter does not supply).

evaluate() runs one manifest over a list of episodes, optionally with one intervention
applied at each episode's intervention tick, and returns reward plus the resource meter and
a few mechanism-neutral descriptors (persist policy, tape occupancy, tick-ending statuses).

run_cell() is a (mu + lambda)-style loop: N organisms, elitism, tournament selection, children
by proteus.foundry.lineage.descend (which carries the grammar's splice = crossover), FRESH
episodes every generation. Everything derives from the campaign seed; no LLM anywhere.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Meter, Player

from . import interventions as I
from .economics import Regime
from .worlds import Episode, WorldSpec, episodes_for

MASK62 = (1 << 62) - 1

# Generation-0 sampling ranges. tick_budget and tape_words are EVOLVABLE (config_perturbation).
FOUNDRY = {
    "schema_version": G.FOUNDRY_SCHEMA,
    "seed": 0,
    "n": 0,
    "n_regs_range": [2, 16],
    "tape_words_choices": [16, 32, 64, 128, 256],
    "genome_instr_range": [1, 32],
    "code_writable_weights": [1, 1],
    "persist_weights": [1, 1, 1, 1],
    "tick_budget_choices": [16, 64, 256],
    "out_cap_choices": [1, 4],
}


def _state_at(player: Player, ep: Episode, tick: int, rng_seed: int) -> dict:
    st = player.fresh_state()
    rng = SplitMix64(seed_from("wse.vmrng", rng_seed, -1))
    for ti in range(min(tick, len(ep.ticks))):
        player.run_tick(st, [ep.ticks[ti]], 1, rng)
    return st


def evaluate(manifest: dict, episodes: List[Episode], intervention: Optional[str] = None,
             rng_seed: int = 0) -> dict:
    player = Player(manifest)
    meter = Meter()
    glen = player.genome_len
    correct = asks = 0
    statuses = {"halt": 0, "yield": 0, "budget": 0}
    occupancy_max = 0
    tape_writes = 0
    answered = 0
    irng = SplitMix64(seed_from("wse.intervention", rng_seed, intervention or ""))
    for ei, ep in enumerate(episodes):
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        halved = False
        donor = None
        if intervention == "TRANSPLANT":
            donor = _state_at(player, episodes[(ei + 1) % len(episodes)], ep.intervention_tick, rng_seed)
        for ti, words in enumerate(ep.ticks):
            if intervention is not None and ti == ep.intervention_tick:
                I.apply(intervention, player, st, irng, donor)
                halved = intervention == "HALVE_CAP"
            player.begin_tick(st)                      # idempotent; makes the snapshot honest
            before = st["tape"][glen:]
            outs, status = player.run_tick(st, [words], 1, rng, meter=meter)
            if halved:
                I.halve_cap_enforce(player, st)
            statuses[status] += 1
            after = st["tape"][glen:]
            if after != before:
                tape_writes += sum(1 for a, b in zip(after, before) if a != b)
            occ = sum(1 for w in after if w != 0)
            if occ > occupancy_max:
                occupancy_max = occ
            if ti in ep.expected:
                asks += 1
                if outs[0]:
                    answered += 1
                    if outs[0][0] == ep.expected[ti]:
                        correct += 1
    n = max(1, len(episodes))
    m = meter.as_dict(manifest)
    return {
        "reward": correct / max(1, asks),
        "asks": asks,
        "correct": correct,
        "answered_share": answered / max(1, asks),
        "meter": m,
        "ops_per_episode": m["ops"] / n,
        "persist": manifest["persist"],
        "tick_budget": manifest["tick_budget"],
        "tape_words": manifest["tape_words"],
        "n_regs": manifest["n_regs"],
        "code_writable": manifest["code_writable"],
        "statuses": statuses,
        "yield_share": statuses["yield"] / max(1, sum(statuses.values())),
        "tape_occupancy_max": occupancy_max,
        "tape_writes_per_episode": tape_writes / n,
    }


def _tournament(scored: list, rng: SplitMix64, k: int) -> dict:
    best = None
    for _ in range(k):
        c = scored[rng.randbelow(len(scored))]
        if best is None or c[0] > best[0]:
            best = c
    return best[1]


def run_cell(spec: WorldSpec, regime: Regime, campaign_seed: int, cell_seed: int,
             N: int = 200, G_: int = 100, E: int = 24, elitism: int = 4, tournament: int = 4,
             init_pop: Optional[List[dict]] = None, branch: str = "B1_naive",
             ramp: bool = False, ramp_foothold: float = 0.30, curve_every: int = 0,
             ramp_mode: str = "best", chance: float = 0.0,
             tabu: Optional[set] = None, tabu_retries: int = 1, tabu_key=None,
             descend_fn=None,
             curve_episodes: Optional[List[Episode]] = None, foundry: Optional[dict] = None) -> dict:
    """Evolve one cell. Returns the elite, its ancestry chain, the per-generation trace and
    (v0.2) the learning curve: held-out competence of the elite every `curve_every`
    generations against cumulative experience (episodes and ticks the lineage evaluated)."""
    rng = SplitMix64(seed_from("wse.evolve.v0", campaign_seed, spec.world_id(), regime.name, cell_seed, branch))
    if init_pop is None:
        fm = dict(foundry or FOUNDRY); fm["seed"] = seed_from("wse.gen0", campaign_seed, cell_seed) & MASK62; fm["n"] = N
        pop = G.generate(fm)
    else:
        pop = list(init_pop)
        while len(pop) < N:
            pop.append(pop[rng.randbelow(len(init_pop))])
    records: Dict[str, dict] = {}
    trace: List[dict] = []
    curve: List[dict] = []
    scored = []
    best_so_far = 0.0
    mean_prev = 0.0
    tabu_hits = [0]
    exp_episodes = 0
    exp_ticks = 0
    for g in range(G_):
        eps = episodes_for(spec, campaign_seed, "train", g * 100003 + cell_seed, E)
        if not ramp:
            m_g = 1.0
        elif ramp_mode == "mean":
            # v0.3 (DESIGN_v0.3 W1): the population MEAN of the previous generation above chance
            m_g = min(1.0, max(0.0, (mean_prev - chance) / ramp_foothold))
        else:
            m_g = min(1.0, best_so_far / ramp_foothold)
        scored = []
        for org in pop:
            ev = evaluate(org["manifest"], eps, rng_seed=seed_from("wse.eval", campaign_seed, g, cell_seed))
            f = regime.fitness(ev["reward"], ev["meter"], E, multiplier=m_g)
            scored.append((f, org, ev))
        exp_episodes += N * E
        exp_ticks += N * sum(len(e.ticks) for e in eps)
        scored.sort(key=lambda z: -z[0])
        top = scored[0]
        best_so_far = max(best_so_far, max(z[2]["reward"] for z in scored))
        mean_prev = sum(z[2]["reward"] for z in scored) / len(scored)
        if curve_every and curve_episodes is not None and (g % curve_every == 0 or g == G_ - 1):
            cev = evaluate(top[1]["manifest"], curve_episodes, rng_seed=seed_from("wse.curve", campaign_seed, cell_seed))
            curve.append({"gen": g, "experience_episodes": exp_episodes, "experience_ticks": exp_ticks,
                          "competence": round(cev["reward"], 4), "ops_per_episode": round(cev["ops_per_episode"], 1),
                          "persistent_words": cev["meter"].get("persistent_state_words", 0),
                          "peak_state": cev["tape_occupancy_max"] + cev["n_regs"], "m_g": round(m_g, 3)})
        trace.append({
            "m_g": round(m_g, 3),
            "gen": g, "best_fitness": round(top[0], 6), "best_reward": round(top[2]["reward"], 6),
            "mean_reward": round(sum(z[2]["reward"] for z in scored) / len(scored), 6),
            "mean_fitness": round(sum(z[0] for z in scored) / len(scored), 6),
            "elite_persist": top[2]["persist"], "elite_ops": round(top[2]["ops_per_episode"], 1),
            "elite_tape_occ": top[2]["tape_occupancy_max"], "elite_yield_share": round(top[2]["yield_share"], 3),
            "elite_tick_budget": top[2]["tick_budget"], "elite_tape_words": top[2]["tape_words"],
            "elite_n_regs": top[2]["n_regs"], "elite_id": top[1]["organism_id"][:16],
            "persist_shares": _shares(scored),
        })
        if g == G_ - 1:
            break
        new_pop = [z[1] for z in scored[:elitism]]
        while len(new_pop) < N:
            parent = _tournament(scored, rng, tournament)
            mate = _tournament(scored, rng, tournament)
            _descend = descend_fn or descend        # SFE-09: an alternative REPRESENTATION's child generator
            child, rec = _descend(parent, rng.next_u64() & MASK62, mate=mate if mate is not parent else None)
            # Campaign-1 SFE-01: FAILURE residue as a tabu set of genome tuples; a child whose
            # genome is tabu is re-drawn (tabu_retries times); the residue prunes, never proposes.
            if tabu:
                tries = 0
                kf = tabu_key or (lambda g: tuple(g))
                while kf(child["manifest"]["genome"]) in tabu and tries < tabu_retries:
                    child, rec = _descend(parent, rng.next_u64() & MASK62, mate=mate if mate is not parent else None)
                    tries += 1
                    tabu_hits[0] += 1
            # A no-op mutation yields child_id == parent_id; recording it made the ancestry walk
            # a self-loop (v01 rows carry ancestry_depth 10000 = the cap, INVALID; results unaffected).
            if child["organism_id"] != parent["organism_id"] and child["organism_id"] not in records:
                records[child["organism_id"]] = rec
            new_pop.append(child)
        pop = new_pop
    elite_f, elite, elite_ev = scored[0]
    chain = []
    oid = elite["organism_id"]
    seen = set()
    while oid in records and oid not in seen and len(chain) < 10000:
        seen.add(oid)
        r = records[oid]
        chain.append({"organism_id": oid, "parent_ids": r["parent_ids"],
                      "operators": [o["operator"] for o in r["operators"]], "generation": r["generation"]})
        oid = r["parent_ids"][0]
    return {
        "elite": elite, "elite_fitness": elite_f, "elite_eval": elite_ev,
        "ancestry": chain, "trace": trace, "branch": branch, "learning_curve": curve,
        "experience_episodes": exp_episodes, "experience_ticks": exp_ticks,
        "final_population_ids": [z[1]["organism_id"] for z in scored[:elitism]],
        "final_population": [{"fitness": z[0], "reward": z[2]["reward"], "manifest": z[1]["manifest"]} for z in scored],
        "tabu_hits": tabu_hits[0],
        "final_elites": [z[1] for z in scored[:elitism]],
    }


def _shares(scored: list) -> dict:
    out = {"none": 0, "regs": 0, "tape": 0, "all": 0}
    for _, org, _ in scored:
        out[org["manifest"]["persist"]] += 1
    n = max(1, len(scored))
    return {k: round(v / n, 3) for k, v in out.items()}
