"""EvolutionB: archaeon.wse.evolve.Evolution with a pluggable evaluator and grammar (Campaign 5,
Phase B). Everything else (tournament, elitism, origins, records, trace, inject, result) is the
parent class's, so arms differ ONLY in (evaluator, descend_fn). Telemetry adds the crossing
share of the population (static invalidity under B) and the elite's fault counts.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from proteus.foundry.prng import seed_from
from archaeon.wse.evolve import Evolution, evaluate as evaluate_old, _shares
from archaeon.wse.telemetry import origin_shares
from archaeon.wse.worlds import Episode

from .evaluate_b import evaluate_b
from .grammar_b import descend_b
from .vm_b import static_validity


def make_evaluator(interp: str) -> Callable:
    if interp == "OLD":
        return lambda m, eps, rng_seed, reward_mode: evaluate_old(m, eps, rng_seed=rng_seed, reward_mode=reward_mode)
    mode = "FAIL" if interp == "B_FAIL" else "FIZZLE"
    return lambda m, eps, rng_seed, reward_mode: evaluate_b(m, eps, rng_seed=rng_seed, reward_mode=reward_mode, mode=mode)


class EvolutionB(Evolution):
    def __init__(self, *args, interp: str = "B_FAIL", grammar: str = "B", **kw):
        if grammar == "B":
            kw["descend_fn"] = lambda parent, seed, mate=None: descend_b(parent, seed, mate=mate)
        super().__init__(*args, **kw)
        self.interp = interp
        self.grammar_name = grammar
        self.evaluate_fn = make_evaluator(interp)

    def evaluate_generation(self, episodes: Optional[List[Episode]] = None, last: bool = False) -> dict:
        g = self.g
        eps = episodes if episodes is not None else self.episodes()
        m_g = self.multiplier()
        scored = []
        rs = seed_from("wse.eval", self.campaign_seed, g, self.cell_seed)
        for org in self.pop:
            ev = self.evaluate_fn(org["manifest"], eps, rs, self.reward_mode)
            f = self.regime.fitness(ev["reward"], ev["meter"], self.E, multiplier=m_g)
            scored.append((f, org, ev))
        self.exp_episodes += self.N * self.E
        self.exp_ticks += self.N * sum(len(e.ticks) for e in eps)
        scored.sort(key=lambda z: -z[0])
        top = scored[0]
        gen_best = max(z[2]["reward"] for z in scored)
        self.best_so_far = max(self.best_so_far, gen_best)
        self.mean_prev = sum(z[2]["reward"] for z in scored) / len(scored)
        if self.first_solved_gen is None and top[2]["reward"] >= self.solve_threshold:
            self.first_solved_gen = g
        crossing = sum(1 for z in scored if not static_validity(z[1]["manifest"])["all_valid"])
        row = {
            "m_g": round(m_g, 3), "gen": g, "best_fitness": round(top[0], 6), "best_reward": round(top[2]["reward"], 6),
            "mean_reward": round(self.mean_prev, 6), "mean_fitness": round(sum(z[0] for z in scored) / len(scored), 6),
            "elite_persist": top[2]["persist"], "elite_ops": round(top[2]["ops_per_episode"], 1),
            "elite_tape_occ": top[2]["tape_occupancy_max"], "elite_yield_share": round(top[2]["yield_share"], 3),
            "elite_tick_budget": top[2]["tick_budget"], "elite_tape_words": top[2]["tape_words"],
            "elite_n_regs": top[2]["n_regs"], "elite_id": top[1]["organism_id"][:16],
            "persist_shares": _shares(scored), "origin_shares": origin_shares(self.pop),
            "elite_origins": list(top[1].get("origins", ["gen0"])),
            "elite_per_ask": top[2].get("per_ask_reward", []),
            "cell": self.spec.name, "interp": self.interp, "grammar": self.grammar_name,
            "crossing_share": round(crossing / len(scored), 4),
            "trapped_share": round(sum(1 for z in scored if z[2].get("trapped")) / len(scored), 4),
            "faulted_share": round(sum(1 for z in scored if z[2].get("faults", 0) > 0) / len(scored), 4),
            "elite_faults": top[2].get("faults", 0), "elite_fault_sites": top[2].get("fault_sites", 0),
            "elite_len": len(top[1]["manifest"]["genome"]) // 4,
        }
        if g == 0:
            row["gen0_provenance"] = self.gen0_provenance
        self.trace.append(row)
        self.scored = scored
        return row
