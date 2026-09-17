"""Evaluation and selection over Proteus players (the part Proteus by charter does not supply).

evaluate() runs one manifest over a list of episodes, optionally with one intervention
applied at each episode's intervention tick, and returns reward plus the resource meter, a
few mechanism-neutral descriptors (persist policy, tape occupancy, tick-ending statuses) and
-- campaign 2 -- the number of episodes on which the intervention was actually APPLIED.

Evolution is the GENERATION-STEP API (campaign 2, Phase A group G): one object holds the
population and the loop's state; evaluate_generation() scores the current population on the
current generation's episodes and appends a trace row; reproduce() builds the next
population (elitism, tournament, proteus.foundry.lineage.descend which carries the grammar's
splice = crossover, optional tabu, optional alternative representation). Curricula, ramps,
producer-consumer schedules and changing pressures change `spec` / `regime` between steps
instead of re-implementing the loop. run_cell() is Evolution(...).run(G) and returns what it
always returned, plus first_solved_gen, gen0 provenance and per-generation origin shares.

COMMON RANDOM NUMBERS BY DEFAULT (group C): the loop's RNG is keyed on (campaign seed, world,
regime, cell seed) and NOT on the provenance label `branch`. Two arms that differ only in
their branch label draw identical random streams. A harness that WANTS distinct streams
passes rng_label (opt-out). Campaign-1 harnesses reproduce their frozen rows by passing
rng_label=<their branch label> (the pre-campaign-2 loop keyed the RNG on the label).

GENERATION ZERO (group C): gen0() is the cell's own population; common_fill() substitutes
organisms (imports, residue, seeds) into that SAME population and records provenance. An
init_pop handed in without provenance is accepted and flagged GEN0_FILL_UNVERIFIED.
Everything derives from the campaign seed; no LLM anywhere.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Meter, Player

from . import interventions as I
from .economics import Regime
from .telemetry import genome_summary, origin_shares
from .worlds import Episode, WorldSpec, episodes_for

MASK62 = (1 << 62) - 1
CRN_LABEL = "crn"            # the default rng_label: every arm in a cell shares this stream

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
             rng_seed: int = 0, reward_mode: str = "per_ask") -> dict:
    """reward_mode (campaign 3, C3-SFE-08 replacement): 'per_ask' (every campaign so far) gives
    partial credit per correct ask; 'episode' gives credit only for episodes in which EVERY ask
    is correct (all-or-nothing). Both are always reported: 'reward' follows reward_mode and
    'reward_per_ask' / 'reward_episode' carry the two readouts, so arms are comparable."""
    player = Player(manifest)
    meter = Meter()
    glen = player.genome_len
    correct = asks = 0
    ep_all = 0
    statuses = {"halt": 0, "yield": 0, "budget": 0}
    occupancy_max = 0
    tape_writes = 0
    answered = 0
    applied = 0
    per_ask_correct: List[int] = []                    # campaign 3: credit per ask POSITION (which stream is solved)
    per_ask_n: List[int] = []
    irng = SplitMix64(seed_from("wse.intervention", rng_seed, intervention or ""))
    for ei, ep in enumerate(episodes):
        ep_correct = ep_asks = 0
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        halved = False
        donor = None
        if intervention == "TRANSPLANT":
            donor = _state_at(player, episodes[(ei + 1) % len(episodes)], ep.intervention_tick, rng_seed)
        for ti, words in enumerate(ep.ticks):
            if intervention is not None and ti == ep.intervention_tick:
                I.apply(intervention, player, st, irng, donor)
                applied += 1
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
                ask_i = sum(1 for t in ep.expected if t < ti)          # position of this ask within the episode
                while len(per_ask_n) <= ask_i:
                    per_ask_n.append(0); per_ask_correct.append(0)
                per_ask_n[ask_i] += 1
                asks += 1
                ep_asks += 1
                if outs[0]:
                    answered += 1
                    if outs[0][0] == ep.expected[ti]:
                        correct += 1
                        ep_correct += 1
                        per_ask_correct[ask_i] += 1
        if ep_asks and ep_correct == ep_asks:
            ep_all += 1
    n = max(1, len(episodes))
    m = meter.as_dict(manifest)
    r_ask = correct / max(1, asks)
    r_ep = ep_all / n
    return {
        "reward": r_ep if reward_mode == "episode" else r_ask,
        "reward_per_ask": r_ask,
        "reward_episode": r_ep,
        "reward_mode": reward_mode,
        "episodes_all_correct": ep_all,
        "asks": asks,
        "correct": correct,
        "per_ask_reward": [round(c / max(1, k), 4) for c, k in zip(per_ask_correct, per_ask_n)],
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
        "intervention": intervention,
        "interventions_applied": applied,
    }


def _tournament(scored: list, rng: SplitMix64, k: int) -> dict:
    best = None
    for _ in range(k):
        c = scored[rng.randbelow(len(scored))]
        if best is None or c[0] > best[0]:
            best = c
    return best[1]


# ------------------------------------------------------------------ generation zero
def gen0(campaign_seed: int, cell_seed: int, N: int, foundry: Optional[dict] = None) -> List[dict]:
    """The cell's own generation-0 population: keyed on (campaign seed, cell seed) only, so
    every arm in a cell starts from the same organisms unless it substitutes some."""
    fm = dict(foundry or FOUNDRY); fm["seed"] = seed_from("wse.gen0", campaign_seed, cell_seed) & MASK62; fm["n"] = N
    pop = G.generate(fm)
    for org in pop:
        org["origins"] = ["gen0"]
    return pop


def common_fill(campaign_seed: int, cell_seed: int, N: int, substitutes: List[dict], *,
                tag: str = "import", foundry: Optional[dict] = None, position: str = "front") -> tuple:
    """substitutes (manifests or organism records) REPLACE the first len(substitutes) organisms
    of the cell's generation 0 (position 'front') or are spread evenly through it ('spread');
    the remainder is the same population every other arm draws. Returns (pop, provenance)."""
    subs = []
    for s in substitutes[:N]:
        org = s if "organism_id" in s and "manifest" in s else G.organism_record(dict(s), None, 0)
        org = dict(org); org["origins"] = [tag]
        subs.append(org)
    base = gen0(campaign_seed, cell_seed, N, foundry)
    if position == "spread" and subs:
        pop = list(base)
        stride = max(1, N // len(subs))
        for i, org in enumerate(subs):
            pop[(i * stride) % N] = org
    else:
        pop = subs + base[: max(0, N - len(subs))]
    prov = {"fill": "wse.gen0", "campaign_seed": campaign_seed, "cell_seed": cell_seed, "n": N,
            "n_substituted": len(subs), "substitute_tag": tag, "position": position, "verified_common": True}
    return pop, prov


# ------------------------------------------------------------------ the step API
class Evolution:
    def __init__(self, spec: WorldSpec, regime: Regime, campaign_seed: int, cell_seed: int, *,
                 N: int = 200, E: int = 24, elitism: int = 4, tournament: int = 4,
                 init_pop: Optional[List[dict]] = None, gen0_provenance: Optional[dict] = None,
                 branch: str = "B1_naive", rng_label: Optional[str] = None,
                 ramp: bool = False, ramp_foothold: float = 0.30, ramp_mode: str = "best", chance: float = 0.0,
                 tabu: Optional[set] = None, tabu_retries: int = 1, tabu_key=None,
                 descend_fn: Optional[Callable] = None, foundry: Optional[dict] = None,
                 curve_every: int = 0, curve_episodes: Optional[List[Episode]] = None,
                 solve_threshold: float = 0.5, train_family: str = "train", reward_mode: str = "per_ask",
                 offspring_cap: Optional[float] = None, import_tags: Sequence[str] = ("import",)):
        """offspring_cap (campaign 3, group F): at most this SHARE of each generation's children
        may have a primary parent carrying an import origin (tags in import_tags); beyond it the
        parent is redrawn among resident organisms. None = no cap (campaign-2 behaviour)."""
        self.spec, self.regime = spec, regime
        self.offspring_cap, self.import_tags = offspring_cap, tuple(import_tags)
        self.reward_mode = reward_mode
        self.campaign_seed, self.cell_seed = campaign_seed, cell_seed
        self.N, self.E, self.elitism, self.tournament = N, E, elitism, tournament
        self.branch = branch
        self.rng_label = rng_label if rng_label is not None else CRN_LABEL
        self.rng = SplitMix64(seed_from("wse.evolve.v0", campaign_seed, spec.world_id(), regime.name, cell_seed, self.rng_label))
        self.ramp, self.ramp_foothold, self.ramp_mode, self.chance = ramp, ramp_foothold, ramp_mode, chance
        self.tabu, self.tabu_retries, self.tabu_key = tabu, tabu_retries, tabu_key
        self.descend_fn = descend_fn or descend
        self.foundry = foundry
        self.curve_every, self.curve_episodes = curve_every, curve_episodes
        self.solve_threshold = solve_threshold
        self.train_family = train_family
        self.warnings: List[str] = []
        if init_pop is None:
            self.pop = gen0(campaign_seed, cell_seed, N, foundry)
            self.gen0_provenance = {"fill": "wse.gen0", "campaign_seed": campaign_seed, "cell_seed": cell_seed, "n": N,
                                    "n_substituted": 0, "verified_common": True}
        else:
            self.pop = list(init_pop)
            while len(self.pop) < N:
                self.pop.append(self.pop[self.rng.randbelow(len(init_pop))])
            if gen0_provenance is None:
                self.gen0_provenance = {"fill": "caller", "n": len(init_pop), "verified_common": False}
                self.warnings.append("GEN0_FILL_UNVERIFIED")
            else:
                self.gen0_provenance = dict(gen0_provenance)
        self.records: Dict[str, dict] = {}
        self.trace: List[dict] = []
        self.curve: List[dict] = []
        self.scored: list = []
        self.best_so_far = 0.0
        self.mean_prev = 0.0
        self.tabu_hits = 0
        self.tabu_checked = 0
        self.exp_episodes = 0
        self.exp_ticks = 0
        self.g = 0
        self.first_solved_gen: Optional[int] = None

    # -- one generation --------------------------------------------------
    def multiplier(self) -> float:
        if not self.ramp:
            return 1.0
        if self.ramp_mode == "mean":
            # v0.3 (DESIGN_v0.3 W1): the population MEAN of the previous generation above chance
            return min(1.0, max(0.0, (self.mean_prev - self.chance) / self.ramp_foothold))
        return min(1.0, self.best_so_far / self.ramp_foothold)

    def episodes(self) -> List[Episode]:
        return episodes_for(self.spec, self.campaign_seed, self.train_family, self.g * 100003 + self.cell_seed, self.E)

    def evaluate_generation(self, episodes: Optional[List[Episode]] = None, last: bool = False) -> dict:
        g = self.g
        eps = episodes if episodes is not None else self.episodes()
        m_g = self.multiplier()
        scored = []
        for org in self.pop:
            ev = evaluate(org["manifest"], eps, rng_seed=seed_from("wse.eval", self.campaign_seed, g, self.cell_seed), reward_mode=self.reward_mode)
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
        if self.curve_every and self.curve_episodes is not None and (g % self.curve_every == 0 or last):
            cev = evaluate(top[1]["manifest"], self.curve_episodes, rng_seed=seed_from("wse.curve", self.campaign_seed, self.cell_seed))
            self.curve.append({"gen": g, "experience_episodes": self.exp_episodes, "experience_ticks": self.exp_ticks,
                               "competence": round(cev["reward"], 4), "ops_per_episode": round(cev["ops_per_episode"], 1),
                               "persistent_words": cev["meter"].get("persistent_state_words", 0),
                               "peak_state": cev["tape_occupancy_max"] + cev["n_regs"], "m_g": round(m_g, 3)})
        row = {
            "m_g": round(m_g, 3),
            "gen": g, "best_fitness": round(top[0], 6), "best_reward": round(top[2]["reward"], 6),
            "mean_reward": round(self.mean_prev, 6),
            "mean_fitness": round(sum(z[0] for z in scored) / len(scored), 6),
            "elite_persist": top[2]["persist"], "elite_ops": round(top[2]["ops_per_episode"], 1),
            "elite_tape_occ": top[2]["tape_occupancy_max"], "elite_yield_share": round(top[2]["yield_share"], 3),
            "elite_tick_budget": top[2]["tick_budget"], "elite_tape_words": top[2]["tape_words"],
            "elite_n_regs": top[2]["n_regs"], "elite_id": top[1]["organism_id"][:16],
            "persist_shares": _shares(scored),
            "origin_shares": origin_shares(self.pop),
            "elite_origins": list(top[1].get("origins", ["gen0"])),
            "elite_per_ask": top[2].get("per_ask_reward", []),        # campaign 3: which stream the elite solves
            "pop_max_per_ask": [round(max(z[2]["per_ask_reward"][i] for z in scored if len(z[2]["per_ask_reward"]) > i), 4)
                                for i in range(len(top[2].get("per_ask_reward", [])))],
            "cell": self.spec.name,
        }
        if g == 0:
            row["gen0_provenance"] = self.gen0_provenance
        self.trace.append(row)
        self.scored = scored
        return row

    def _is_import(self, org: dict) -> bool:
        return any(t in org.get("origins", ()) for t in self.import_tags)

    def reproduce(self) -> None:
        scored, rng = self.scored, self.rng
        new_pop = [z[1] for z in scored[:self.elitism]]
        cap_n = None if self.offspring_cap is None else int(self.offspring_cap * (self.N - self.elitism))
        import_children = 0
        residents = [z for z in scored if not self._is_import(z[1])]
        while len(new_pop) < self.N:
            parent = _tournament(scored, rng, self.tournament)
            mate = _tournament(scored, rng, self.tournament)
            if cap_n is not None and self._is_import(parent) and import_children >= cap_n and residents:
                parent = _tournament(residents, rng, self.tournament)     # the cap: redraw among residents
            if cap_n is not None and self._is_import(parent):
                import_children += 1
            child, rec = self.descend_fn(parent, rng.next_u64() & MASK62, mate=mate if mate is not parent else None)
            # Campaign-1 SFE-01: FAILURE residue as a tabu set; a tabu child is re-drawn
            # (tabu_retries times); the residue prunes, never proposes.
            if self.tabu:
                tries = 0
                kf = self.tabu_key or (lambda gg: tuple(gg))
                self.tabu_checked += 1
                while kf(child["manifest"]["genome"]) in self.tabu and tries < self.tabu_retries:
                    child, rec = self.descend_fn(parent, rng.next_u64() & MASK62, mate=mate if mate is not parent else None)
                    tries += 1
                    self.tabu_hits += 1
            origins = list(parent.get("origins", ["gen0"]))
            if mate is not parent:
                for t in mate.get("origins", ["gen0"]):
                    if t not in origins:
                        origins.append(t)
            child["origins"] = origins
            # A no-op mutation yields child_id == parent_id; recording it made the ancestry walk
            # a self-loop (v01 rows carry ancestry_depth 10000 = the cap, INVALID; results unaffected).
            if child["organism_id"] != parent["organism_id"] and child["organism_id"] not in self.records:
                self.records[child["organism_id"]] = rec
            new_pop.append(child)
        self.pop = new_pop
        self.g += 1

    def inject(self, manifests: List[dict], tag: str = "import") -> int:
        """Campaign 3 (group F): imported organisms enter the CURRENT scored generation in place
        of its worst members and compete from this generation on (elitism and tournament see
        them); the offspring cap applies to their children. Call after evaluate_generation()
        and before reproduce(). Returns the number injected."""
        eps = self.episodes()
        rs = seed_from("wse.eval", self.campaign_seed, self.g, self.cell_seed)
        new = []
        for m in manifests:
            org = G.organism_record(dict(m), None, self.g); org["origins"] = [tag]
            e = evaluate(m, eps, rng_seed=rs, reward_mode=self.reward_mode)
            new.append((self.regime.fitness(e["reward"], e["meter"], self.E, multiplier=self.multiplier()), org, e))
        scored = sorted(self.scored, key=lambda z: -z[0])
        scored = scored[: max(0, len(scored) - len(new))] + new
        scored.sort(key=lambda z: -z[0])
        self.scored = scored
        self.pop = [z[1] for z in scored]
        self.trace[-1]["injected"] = {"n": len(new), "tag": tag, "origin_shares_after": origin_shares(self.pop)}
        return len(new)

    def step(self, episodes: Optional[List[Episode]] = None) -> dict:
        """Score the current generation and produce the next one."""
        row = self.evaluate_generation(episodes)
        self.reproduce()
        return row

    def run(self, G_: int) -> dict:
        for i in range(G_):
            self.evaluate_generation(last=(i == G_ - 1))
            if i == G_ - 1:
                break
            self.reproduce()
        return self.result()

    # -- results ---------------------------------------------------------
    def ancestry(self, organism_id: str) -> List[dict]:
        chain = []
        oid = organism_id
        seen = set()
        while oid in self.records and oid not in seen and len(chain) < 10000:
            seen.add(oid)
            r = self.records[oid]
            chain.append({"organism_id": oid, "parent_ids": r["parent_ids"],
                          "operators": [o["operator"] for o in r["operators"]], "generation": r["generation"]})
            oid = r["parent_ids"][0]
        return chain

    def result(self) -> dict:
        scored = self.scored
        elite_f, elite, elite_ev = scored[0]
        return {
            "elite": elite, "elite_fitness": elite_f, "elite_eval": elite_ev,
            "ancestry": self.ancestry(elite["organism_id"]), "trace": self.trace, "branch": self.branch,
            "rng_label": self.rng_label, "learning_curve": self.curve,
            "experience_episodes": self.exp_episodes, "experience_ticks": self.exp_ticks,
            "final_population_ids": [z[1]["organism_id"] for z in scored[:self.elitism]],
            "final_population": [{"fitness": z[0], "reward": z[2]["reward"], "manifest": z[1]["manifest"],
                                  "origins": list(z[1].get("origins", ["gen0"]))} for z in scored],
            "tabu_hits": self.tabu_hits, "tabu_checked": self.tabu_checked,
            "final_elites": [z[1] for z in scored[:self.elitism]],
            "first_solved_gen": self.first_solved_gen, "solve_threshold": self.solve_threshold,
            "gen0_provenance": self.gen0_provenance, "warnings": list(self.warnings),
            "elite_summary": genome_summary(elite["manifest"]),
            "elite_origins": list(elite.get("origins", ["gen0"])),
            "generations": self.g + 1,
        }


def run_cell(spec: WorldSpec, regime: Regime, campaign_seed: int, cell_seed: int,
             N: int = 200, G_: int = 100, E: int = 24, elitism: int = 4, tournament: int = 4,
             init_pop: Optional[List[dict]] = None, branch: str = "B1_naive",
             ramp: bool = False, ramp_foothold: float = 0.30, curve_every: int = 0,
             ramp_mode: str = "best", chance: float = 0.0,
             tabu: Optional[set] = None, tabu_retries: int = 1, tabu_key=None,
             descend_fn=None, rng_label: Optional[str] = None, gen0_provenance: Optional[dict] = None,
             solve_threshold: float = 0.5,
             curve_episodes: Optional[List[Episode]] = None, foundry: Optional[dict] = None) -> dict:
    """Evolve one cell for G_ generations (Evolution(...).run). Returns the elite, its ancestry
    chain, the per-generation trace, the learning curve, first_solved_gen and gen0 provenance."""
    ev = Evolution(spec, regime, campaign_seed, cell_seed, N=N, E=E, elitism=elitism, tournament=tournament,
                   init_pop=init_pop, gen0_provenance=gen0_provenance, branch=branch, rng_label=rng_label,
                   ramp=ramp, ramp_foothold=ramp_foothold, ramp_mode=ramp_mode, chance=chance,
                   tabu=tabu, tabu_retries=tabu_retries, tabu_key=tabu_key, descend_fn=descend_fn,
                   foundry=foundry, curve_every=curve_every, curve_episodes=curve_episodes,
                   solve_threshold=solve_threshold)
    return ev.run(G_)


def _shares(scored: list) -> dict:
    out = {"none": 0, "regs": 0, "tape": 0, "all": 0}
    for _, org, _ in scored:
        out[org["manifest"]["persist"]] += 1
    n = max(1, len(scored))
    return {k: round(v / n, 3) for k, v in out.items()}
