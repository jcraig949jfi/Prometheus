"""The crucible: a population of Z80-like tapes in a world with declared physics.

Everything an experiment varies is a field of Config (assembled from a factor vector by grammar.py). One World is
deterministic given (Config, seed). A tick:
  1. the Environment advances (task shifts / drift / co-evolution / environment reproduction)
  2. every organism, in seeded random order, picks a partner by the spatial structure, interacts with the probability
     the pressure coupling dictates, EXECUTES (own tape at [0,L), partner tape in the neighbour window [L,2L), task
     input at IN_BASE), is scored on the task, pays its costs and earns its inflow
  3. REPRODUCTION PHYSICS decides what the neighbour-window writes mean:
        EXTERNAL            they mean nothing (the window is scratch); the population manager reproduces in step 5
        ENDOGENOUS_COPY     a descendant exists iff ALL L bytes of the partner window were written
        ENDOGENOUS_PARTIAL  a descendant exists iff >= 1 byte was written (the rest is inherited from the target: chimeras)
        OVERWRITE           the target must be OCCUPIED; >= L/2 bytes written replaces it
        CONSTRUCTIVE        the target must be EMPTY;    >= L/2 bytes written constructs into it
        PAIR_EXECUTION      the two tapes are concatenated into one 2L program and executed as one; either may
                            overwrite portions of the other; the halves are split back (the soup physics)
     Under every ENDOGENOUS treatment the population manager is a no-op: an organism persists only by executing
     writes that cause descendants (external_births is asserted 0 by the observatory and the tests).
  4. energy / age: death when energy <= 0 or age > lifespan; background mutation on every tape
  5. EXTERNAL reproduction (only when reproduction == EXTERNAL): selection by the pressure coupling, placement by
     the spatial structure, mutation (+ crossover when recombination is on)
  6. migration between niches by the spatial policy
Telemetry, snapshots, lineage, first-crossing genealogy, serendipity triggers and anti-cheat records are collected
by the World and drained by the observatory."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Environment, Task, score as task_score

INIT_ENERGY = 12.0
REPRO = ("EXTERNAL", "ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
ENDOGENOUS = frozenset(REPRO[1:])


@dataclass
class Config:
    world: str = "GRID"                 # SOUP | GRID | NICHES | GRAPH
    representation: str = "Z80_64"      # Z80_64 | BYTECODE32 | VM_COPY
    layout: str = "SHARED"              # SHARED | SEPARATED
    reproduction: str = "EXTERNAL"      # one of REPRO
    pressure: str = "IMPLICIT"          # IMPLICIT | EXPLICIT | GATED_INTERACTION | RESOURCE_GATED | METABOLIC | NOVELTY | QD | MINIMAL_CRITERION | EXPLOIT
    spatial: str = "LOCAL"              # WELL_MIXED | LOCAL | NICHES_ISOLATED | NICHES_LOW_MIG | NICHES_HIGH_MIG | NICHES_PERIODIC | NICHES_COMPETENCE_MIG | NICHES_POLLINATION | NICHES_ENV_MIG | RESERVOIR
    task: str = "INC"
    scoring: str = "ATOMIC"             # ATOMIC | INCREMENTAL | NEUTRAL
    read_gate: str = "ABR"              # ABR | FORCED
    env_dynamics: str = "FIXED"
    mutation: str = "BYTE"              # OPERAND | OPCODE | BYTE | STRUCTURAL
    mutation_rate: str = "MED"          # LOW | MED | HIGH
    recombination: str = "NONE"         # NONE | CROSSOVER
    init: str = "RANDOM"                # RANDOM | SEEDED_REPLICATOR | SEEDED_WITNESS | SEEDED_HYBRID
    cells: int = 144
    ticks: int = 200
    budget: int = 256
    lifespan: int = 40
    init_tapes: tuple = ()              # transplant / environment-swap interventions: hex tapes seeded as a minority (mechanism "transplant")

    @property
    def L(self) -> int:
        return 32 if self.representation == "BYTECODE32" else 64

    @property
    def allow_copyall(self) -> bool:
        return self.representation == "VM_COPY"

    @property
    def n_niches(self) -> int:
        return 4 if (self.world == "NICHES" or self.spatial.startswith("NICHES") or self.spatial == "RESERVOIR") else 1

    @property
    def side(self) -> int:
        return int(round(self.cells ** 0.5))

    @property
    def mut_rate(self) -> float:
        return {"LOW": 0.002, "MED": 0.008, "HIGH": 0.03}[self.mutation_rate]

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


@dataclass
class Org:
    id: int
    tape: bytearray
    parent: Optional[int]
    lineage: int
    birth: int
    mechanism: str
    energy: float = INIT_ENERGY
    age: int = 0
    score_ema: float = 0.0
    last_score: float = 0.0
    replications: int = 0
    last_repro_tick: int = -1
    repro_span: Optional[int] = None
    fidelity_last: Optional[float] = None
    niche: int = 0
    novelty: float = 0.0
    last_out: Optional[int] = None
    glineage: int = 0                 # GENETIC lineage: whose bytes this tape descends from (lineage = CAUSAL: who wrote it)


class World:
    def __init__(self, cfg: Config, seed: int):
        self.cfg = cfg; self.seed = seed
        self.rng = random.Random(seed)
        self.L = cfg.L
        n = cfg.cells
        self.cells: List[Optional[Org]] = [None] * n
        self.next_id = 1
        self.tick = 0
        side = cfg.side
        self.side = side
        self.env = Environment(cfg.task, cfg.env_dynamics, cfg.n_niches, seed * 7 + 1)
        # niche index per cell: 2x2 blocks
        self.niche_of = [((i // side) * 2 // side) * 2 + ((i % side) * 2 // side) for i in range(n)] if cfg.n_niches > 1 else [0] * n
        if cfg.spatial == "RESERVOIR":
            # niche 0 is the persistent EASY niche (ECHO, incremental); the others carry the configured task
            self.env.tasks[0] = Task("ECHO")
        # graph world: random 4-regular-ish adjacency
        self.adj: Optional[List[List[int]]] = None
        if cfg.world == "GRAPH":
            self.adj = [[] for _ in range(n)]
            for i in range(n):
                while len(self.adj[i]) < 4:
                    j = self.rng.randrange(n)
                    if j != i and j not in self.adj[i]:
                        self.adj[i].append(j); self.adj[j].append(i)
        # telemetry
        self.parent_of: Dict[int, Optional[int]] = {}
        self.birth_tick: Dict[int, int] = {}
        self.seed_lineages: set = set()
        self.events: List[dict] = []
        self.ticks_log: List[dict] = []
        self.snapshots: List[dict] = []
        self.specimens: List[dict] = []
        self.exploits: List[dict] = []
        self.first_crossing: Optional[dict] = None
        self.first_replication: Optional[dict] = None
        self.external_births = 0
        self.endogenous_births = 0
        self.refused_writes = 0
        self.overwrite_deaths = 0
        self.births_by_mech: Dict[str, int] = {}
        self.deaths = 0
        self.extinctions = 0
        self.migrations = 0
        self.cross_niche_transport = 0
        self.captures = 0                 # copy events whose material came from the TARGET, not the writer
        self.null_rewrites = 0            # partner rewritten as exactly itself: not a birth
        self.escape_events: List[dict] = []
        self.best_ema = 0.0; self.plateau_since = 0
        self.stat_ema: Dict[str, float] = {}
        self.qd_archive: Dict[Tuple[int, int], Tuple[float, int]] = {}
        self.novelty_archive: List[Tuple[int, ...]] = []
        self.resource_pool: List[float] = [1.0] * cfg.n_niches
        self._init_population()

    # ---- init -----------------------------------------------------------------------------------------------------
    def _random_tape(self) -> bytearray:
        return bytearray(self.rng.randrange(256) for _ in range(self.L))

    def _spawn(self, i: int, tape: bytearray, parent: Optional[int], mechanism: str, lineage: Optional[int] = None, glineage: Optional[int] = None) -> Org:
        oid = self.next_id; self.next_id += 1
        o = Org(oid, tape, parent, lineage if lineage is not None else oid, self.tick, mechanism, niche=self.niche_of[i],
                glineage=glineage if glineage is not None else (lineage if lineage is not None else oid))
        self.cells[i] = o
        self.parent_of[oid] = parent; self.birth_tick[oid] = self.tick
        self.births_by_mech[mechanism] = self.births_by_mech.get(mechanism, 0) + 1
        if mechanism in ("seed", "transplant"):
            self.seed_lineages.add(o.glineage)
        return o

    def _init_population(self) -> None:
        cfg = self.cfg; n = cfg.cells
        fill = self.rng.sample(range(n), max(1, n // 2))
        seed_tape = None
        if cfg.init == "SEEDED_REPLICATOR":
            seed_tape = vm.replicator_copyall(self.L) if cfg.allow_copyall else vm.replicator(self.L)
        elif cfg.init == "SEEDED_WITNESS":
            seed_tape = self._witness_for(self.env.task_for(0))
        elif cfg.init == "SEEDED_HYBRID":
            rep = vm.replicator_copyall(self.L) if cfg.allow_copyall else vm.replicator(self.L)
            seed_tape = vm.hybrid(rep, self._witness_for(self.env.task_for(0)))
        transplant = [bytearray(bytes.fromhex(h))[:self.L] for h in cfg.init_tapes] if cfg.init_tapes else []
        for k, i in enumerate(fill):
            if transplant and k < max(1, len(fill) // 4):                 # a transplanted minority (a quarter) into a random majority
                t = bytearray(self.L); src = transplant[k % len(transplant)]; t[:len(src)] = src
                self._spawn(i, t, None, "transplant")
            elif seed_tape is not None and k < max(1, len(fill) // 8):     # seeded: a MINORITY, into a random majority
                t = bytearray(self.L); t[:len(seed_tape)] = seed_tape
                self._spawn(i, t, None, "seed")
            else:
                self._spawn(i, self._random_tape(), None, "init")

    def _witness_for(self, task: Task) -> bytes:
        return {"CONST": vm.witness_const(task.k), "ECHO": vm.witness_echo(), "INC": vm.witness_inc(),
                "COND_ONE": vm.witness_cond_one(), "COND_MULTI": vm.witness_cond_multi(), "SUM2": vm.witness_sum2()}[task.kind]

    # ---- spatial ----------------------------------------------------------------------------------------------------
    def _neighbours(self, i: int) -> List[int]:
        if self.adj is not None:
            return self.adj[i]
        s = self.side; x, y = i % s, i // s
        out = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = (x + dx) % s, (y + dy) % s
            out.append(ny * s + nx)
        return out

    def _partner(self, i: int) -> int:
        cfg = self.cfg
        if cfg.spatial == "WELL_MIXED" or cfg.world == "SOUP":
            j = self.rng.randrange(cfg.cells)
            return j if j != i else (j + 1) % cfg.cells
        if cfg.n_niches > 1:
            # within-niche partner unless migration policy lets interactions cross (pollination handled in migrate)
            cands = [j for j in self._neighbours(i) if self.niche_of[j] == self.niche_of[i]]
            if cands:
                return self.rng.choice(cands)
        return self.rng.choice(self._neighbours(i))

    # ---- mutation -----------------------------------------------------------------------------------------------------
    def _opcode_positions(self, tape: bytearray) -> List[int]:
        pos = []; pc = 0
        while pc < len(tape):
            pos.append(pc); pc += 1 + vm.OPLEN.get(tape[pc], 0)
        return pos

    def _mutate(self, tape: bytearray, rate: float) -> int:
        """Background mutation by the declared operator. Returns the number of changes."""
        cfg = self.cfg; L = len(tape); changes = 0
        if cfg.mutation == "STRUCTURAL":
            if self.rng.random() < rate * L:
                kind = self.rng.choice(("insert", "delete", "dup"))
                p = self.rng.randrange(L)
                if kind == "insert":
                    tape[p + 1:] = tape[p:-1]; tape[p] = self.rng.randrange(256)
                elif kind == "delete":
                    tape[p:-1] = tape[p + 1:]; tape[-1] = 0
                else:
                    ln = self.rng.randrange(2, 9); q = self.rng.randrange(L)
                    seg = bytes(tape[p:p + ln]); tape[q:q + len(seg)] = seg[:L - q]
                changes += 1
            return changes
        positions = list(range(L))
        if cfg.mutation in ("OPCODE", "OPERAND"):
            ops = set(self._opcode_positions(tape))
            positions = [p for p in range(L) if (p in ops) == (cfg.mutation == "OPCODE")] or positions
        for p in positions:
            if self.rng.random() < rate:
                if cfg.mutation == "OPERAND":
                    tape[p] = (tape[p] + self.rng.choice((-1, 1))) & 0xFF      # local: operands step
                else:
                    tape[p] = self.rng.randrange(256)
                changes += 1
        return changes

    # ---- execution ----------------------------------------------------------------------------------------------------
    def _execute(self, o: Org, partner_tape: Optional[bytearray], inputs: List[int]):
        cfg = self.cfg; L = self.L
        mem = bytearray(256)
        mem[:L] = o.tape
        if partner_tape is not None:
            mem[L:2 * L] = partner_tape
        for k, v in enumerate(inputs[:16]):
            mem[vm.IN_BASE + k] = v
        if cfg.layout == "SEPARATED":
            tr1 = vm.execute(mem, L, 0, cfg.budget // 2, inputs, region=(0, L // 2), allow_copyall=cfg.allow_copyall)
            tr2 = vm.execute(mem, L, L // 2, cfg.budget // 2, inputs, region=(L // 2, L), allow_copyall=cfg.allow_copyall)
            tr = tr1
            tr.steps += tr2.steps; tr.outputs = tr1.outputs + tr2.outputs
            tr.reads_in += tr2.reads_in; tr.self_writes += tr2.self_writes; tr.neighbour_writes += tr2.neighbour_writes
            tr.copy_events += tr2.copy_events; tr.io_writes += tr2.io_writes; tr.io_corrupt += tr2.io_corrupt; tr.neighbour_reads += tr2.neighbour_reads
            if tr.io_corrupt_step is None and tr2.io_corrupt_step is not None:
                tr.io_corrupt_step = tr2.io_corrupt_step + tr1.steps
            tr.first_in_step = tr1.first_in_step if tr1.first_in_step is not None else (None if tr2.first_in_step is None else tr2.first_in_step + tr1.steps)
            tr.first_out_step = tr1.first_out_step if tr1.first_out_step is not None else (None if tr2.first_out_step is None else tr2.first_out_step + tr1.steps)
            tr.halted = tr2.halted
            for k, v in tr2.opcodes.items():
                tr.opcodes[k] = tr.opcodes.get(k, 0) + v
            tr.writes.update(tr2.writes)
        else:
            tr = vm.execute(mem, L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall)
        return mem, tr

    def _pair_execute(self, a: Org, b: Org, inputs: List[int]):
        """PAIR_EXECUTION: one 2L program from both tapes; both halves may be rewritten."""
        cfg = self.cfg; L = self.L
        mem = bytearray(256)
        mem[:L] = a.tape; mem[L:2 * L] = b.tape
        for k, v in enumerate(inputs[:16]):
            mem[vm.IN_BASE + k] = v
        tr = vm.execute(mem, 2 * L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall)
        return mem, tr

    # ---- the tick ---------------------------------------------------------------------------------------------------------
    def step(self) -> dict:
        cfg = self.cfg; L = self.L; rng = self.rng
        # 1. environment
        modal = self._modal_answers(); persistent = self._niche_persistent()
        change = self.env.step(self.tick, modal, persistent)
        if change:
            self.events.append({"tick": self.tick, "kind": "env_change", **change, "standing_variation": self._standing_variation()})
            if cfg.spatial == "NICHES_ENV_MIG":
                self._migrate(force=True)
        # 2-3. interactions
        order = [i for i, c in enumerate(self.cells) if c is not None]
        rng.shuffle(order)
        scores = []; steps_total = 0; copy_attempts = 0; interactions = 0
        for i in order:
            o = self.cells[i]
            if o is None:
                continue
            j = self._partner(i)
            p_int = 1.0
            if cfg.pressure == "GATED_INTERACTION":
                p_int = 0.15 + 0.85 * o.score_ema
            if rng.random() > p_int:
                continue
            interactions += 1
            task = self.env.task_for(o.niche)
            inputs = task.inputs(rng)
            expected = task.expected(inputs)
            partner = self.cells[j]
            if cfg.reproduction == "PAIR_EXECUTION" and partner is not None:
                mem, tr = self._pair_execute(o, partner, inputs)
                new_a = bytearray(mem[:L]); new_b = bytearray(mem[L:2 * L])
                changed_b = new_b != partner.tape
                o.tape = new_a
                if changed_b:
                    fid = 1.0 - sum(1 for x, y in zip(new_b, o.tape) if x != y) / L
                    self._register_offspring(j, new_b, o, "PAIR_EXECUTION", fid, tr, replaced=partner)
                    copy_attempts += 1
            else:
                mem, tr = self._execute(o, partner.tape if partner is not None else None, inputs)
                o.tape = bytearray(mem[:L])
                if tr.neighbour_writes:
                    copy_attempts += 1
                    self._apply_reproduction(o, j, mem, tr)
            s = task_score(task, tr.outputs, expected, cfg.scoring, cfg.read_gate, tr.first_out_step, tr.first_in_step)
            o.last_score = s; o.score_ema = 0.7 * o.score_ema + 0.3 * s
            o.last_out = tr.outputs[0] if tr.outputs else None
            scores.append(s); steps_total += tr.steps
            # anti-cheat
            if s >= 0.999 and tr.io_corrupt_step is not None and (tr.first_in_step is None or tr.io_corrupt_step < tr.first_in_step):
                self._exploit("corrupt_validation", o, tr)          # a perfect answer after changing the input region BEFORE reading it
            if cfg.read_gate == "FORCED" and task.needs_read() and s >= 0.999 and tr.reads_in == 0:
                self._exploit("evaluator_leakage", o, tr)
            if not tr.halted and tr.steps >= cfg.budget and tr.outputs:
                o.__dict__["nonterm"] = o.__dict__.get("nonterm", 0) + 1
            # first crossing
            if o.score_ema >= 0.85 and self.first_crossing is None and cfg.scoring != "NEUTRAL":     # sustained, not one lucky output
                self.first_crossing = {"tick": self.tick, "id": o.id, "lineage": o.lineage, "tape": bytes(o.tape).hex(),
                                       "genealogy": self._ancestry(o.id), "task": task.to_dict(), "mechanism": o.mechanism}
            # energy
            o.energy += self._inflow(o, s, tr)
            o.energy -= self._cost(o, tr)
            o.age += 1
        # 4. death + background mutation
        deaths = 0
        for i, o in enumerate(self.cells):
            if o is None:
                continue
            dead = o.energy <= 0 or o.age > cfg.lifespan
            if cfg.pressure == "MINIMAL_CRITERION" and cfg.reproduction in ENDOGENOUS and o.age > 15 and o.replications == 0:
                dead = True
            if dead:
                self.cells[i] = None; deaths += 1
                continue
            self._mutate(o.tape, cfg.mut_rate)
        self.deaths += deaths
        # 5. external reproduction
        ext_births = 0
        if cfg.reproduction == "EXTERNAL":
            ext_births = self._external_reproduce()
        # 6. migration
        self._migrate()
        # telemetry
        alive = [o for o in self.cells if o is not None]
        rec = self._telemetry(alive, scores, steps_total, copy_attempts, interactions, deaths, ext_births)
        self.ticks_log.append(rec)
        self._serendipity(rec, alive)
        if self.tick % 50 == 0 or self.tick == cfg.ticks - 1:
            self._snapshot(alive, "periodic")
        self.tick += 1
        return rec

    # ---- reproduction physics ------------------------------------------------------------------------------------------------
    def _apply_reproduction(self, o: Org, j: int, mem: bytearray, tr) -> None:
        cfg = self.cfg; L = self.L
        if cfg.reproduction == "EXTERNAL":
            return                                    # the window is scratch: writes mean nothing
        target = self.cells[j]
        written = [a - L for a in tr.writes if L <= a < 2 * L]
        n_written = len(set(written))
        physics = cfg.reproduction
        if physics == "CONSTRUCTIVE" and target is not None:
            self.refused_writes += 1; return
        if physics == "OVERWRITE" and target is None:
            self.refused_writes += 1; return
        viable = {"ENDOGENOUS_COPY": n_written >= L, "ENDOGENOUS_PARTIAL": n_written >= 1,
                  "OVERWRITE": n_written >= L // 2, "CONSTRUCTIVE": n_written >= L // 2,
                  "PAIR_EXECUTION": n_written >= L // 2}[physics]                 # pair physics with an EMPTY partner: construct into it
        if not viable:
            self.refused_writes += 1; return
        child = bytearray(mem[L:2 * L])
        if target is not None and child == target.tape:
            self.null_rewrites += 1; return              # the partner was rewritten as EXACTLY itself: nothing was caused, no birth
        fid = 1.0 - sum(1 for x, y in zip(child, o.tape) if x != y) / L
        self._register_offspring(j, child, o, physics, fid, tr, replaced=target)

    def _register_offspring(self, j: int, child: bytearray, parent: Org, mechanism: str, fidelity: float, tr, replaced: Optional[Org]) -> None:
        # the WRITER is the causal parent; the GENETIC source is whichever tape the child's bytes resemble more --
        # the writer's, or the target's own previous contents (a writer can rewrite its partner as a shifted copy of
        # itself: "code capture", the byte-soup ambiguity made explicit rather than hidden)
        material = "writer"; glin = parent.glineage
        if replaced is not None:
            L = self.L
            fid_target = 1.0 - sum(1 for x, y in zip(child, replaced.tape) if x != y) / L
            if fid_target > fidelity:
                material = "target"; glin = replaced.glineage
                self.captures += 1
                fidelity = fid_target                      # copy fidelity is measured against the GENETIC source
        if replaced is not None:
            self.overwrite_deaths += 1
        c = self._spawn(j, child, parent.id, mechanism, lineage=parent.lineage, glineage=glin)     # fresh energy, no registers: nothing non-heritable travels
        parent.replications += 1; parent.last_repro_tick = self.tick
        parent.fidelity_last = fidelity
        parent.repro_span = tr.pc_max + 1
        self.endogenous_births += 1
        self.events.append({"tick": self.tick, "kind": "copy", "parent": parent.id, "child": c.id, "cell": j, "fidelity": round(fidelity, 3),
                            "mechanism": mechanism, "span": tr.pc_max + 1, "steps": tr.steps, "replaced": replaced.id if replaced else None,
                            "material": material, "glineage": glin})
        if self.first_replication is None:
            self.first_replication = {"tick": self.tick, "id": parent.id, "lineage": parent.lineage, "tape": bytes(parent.tape).hex(),
                                      "mechanism": mechanism, "fidelity": fidelity, "span": tr.pc_max + 1, "genealogy": self._ancestry(parent.id),
                                      "seeded": parent.glineage in self.seed_lineages or (glin in self.seed_lineages)}

    def _external_reproduce(self) -> int:
        """The population manager. ONLY under reproduction == EXTERNAL (asserted)."""
        cfg = self.cfg; rng = self.rng
        assert cfg.reproduction == "EXTERNAL", "population-manager reproduction invoked under an ENDOGENOUS treatment"
        alive_idx = [i for i, o in enumerate(self.cells) if o is not None]
        if not alive_idx:
            return 0
        empties = [i for i, o in enumerate(self.cells) if o is None]
        n_births = max(1, len(alive_idx) // 8)
        weights = self._selection_weights([self.cells[i] for i in alive_idx])
        births = 0
        for _ in range(n_births):
            pi = rng.choices(alive_idx, weights=weights)[0]; parent = self.cells[pi]
            if parent is None:
                continue
            if cfg.spatial in ("WELL_MIXED",) or cfg.world == "SOUP":
                cands = empties or alive_idx
            else:
                nb = self._neighbours(pi)
                cands = [j for j in nb if self.cells[j] is None] or nb
            j = rng.choice(cands)
            child = bytearray(parent.tape)
            if cfg.recombination == "CROSSOVER":
                mate = self.cells[rng.choice(alive_idx)]
                if mate is not None:
                    cut = rng.randrange(1, self.L); child[cut:] = mate.tape[cut:]
            self._mutate(child, cfg.mut_rate * 4)
            replaced = self.cells[j]
            if replaced is not None:
                self.overwrite_deaths += 1
            c = self._spawn(j, child, parent.id, "EXTERNAL", lineage=parent.lineage, glineage=parent.glineage)
            parent.replications += 1; parent.last_repro_tick = self.tick
            if j in empties:
                empties.remove(j)
            births += 1
            self.external_births += 1
        return births

    def _selection_weights(self, orgs: List[Org]) -> List[float]:
        cfg = self.cfg
        if cfg.pressure in ("EXPLICIT", "RESOURCE_GATED", "GATED_INTERACTION", "MINIMAL_CRITERION"):
            return [0.05 + o.score_ema for o in orgs]
        if cfg.pressure == "NOVELTY":
            return [0.05 + o.novelty for o in orgs]
        if cfg.pressure == "QD":
            return [1.0 + (1.0 if self.qd_archive.get(self._qd_cell(o), (None, None))[1] == o.id else 0.0) for o in orgs]
        return [1.0] * len(orgs)                      # IMPLICIT / METABOLIC / EXPLOIT: drift under survival

    # ---- pressure ----------------------------------------------------------------------------------------------------------
    def _inflow(self, o: Org, s: float, tr) -> float:
        cfg = self.cfg
        base = 1.0
        if cfg.pressure in ("EXPLICIT", "MINIMAL_CRITERION") and cfg.reproduction in ENDOGENOUS:
            return base + 2.0 * s
        if cfg.pressure == "RESOURCE_GATED":
            pool = self.resource_pool[o.niche % len(self.resource_pool)]
            take = min(pool, 0.5 + 2.0 * s)
            self.resource_pool[o.niche % len(self.resource_pool)] = pool - take + 0.25
            return 0.4 + take
        if cfg.pressure == "NOVELTY":
            o.novelty = self._novelty(tr); return base + 1.5 * o.novelty
        if cfg.pressure == "QD":
            cell = self._qd_cell(o); best = self.qd_archive.get(cell)
            if best is None or s > best[0]:
                self.qd_archive[cell] = (s, o.id); return base + 1.5
            return base
        if cfg.pressure == "EXPLOIT" and tr.neighbour_reads and tr.neighbour_writes:
            return base + 1.5                          # the exploiter feeds on the partner it read and overwrote
        return base + (0.5 * s if cfg.scoring != "NEUTRAL" else 0.0)

    def _cost(self, o: Org, tr) -> float:
        cfg = self.cfg
        c = 0.9 + 0.001 * tr.steps
        if cfg.pressure == "METABOLIC":
            c = 0.6 + 0.006 * tr.steps + 0.004 * sum(1 for b in o.tape if b)
        return c

    def _novelty(self, tr) -> float:
        sig = tuple(sorted(tr.opcodes.items()))[:8]
        key = tuple(k for k, _ in sig)
        d = min((sum(1 for a, b in zip(key, k2) if a != b) + abs(len(key) - len(k2)) for k2 in self.novelty_archive), default=8)
        if d >= 2 and len(self.novelty_archive) < 400:
            self.novelty_archive.append(key)
        return min(1.0, d / 8.0)

    def _qd_cell(self, o: Org) -> Tuple[int, int]:
        used = sum(1 for b in o.tape if b)
        return (used // 8, min(3, o.replications))

    # ---- migration -----------------------------------------------------------------------------------------------------------
    def _migrate(self, force: bool = False) -> None:
        cfg = self.cfg; rng = self.rng
        if cfg.n_niches <= 1:
            return
        rate = {"NICHES_ISOLATED": 0.0, "NICHES_LOW_MIG": 0.01, "NICHES_HIGH_MIG": 0.1, "NICHES_PERIODIC": (0.2 if self.tick % 25 == 0 else 0.0),
                "NICHES_COMPETENCE_MIG": 0.05, "NICHES_POLLINATION": 0.03, "NICHES_ENV_MIG": (0.2 if force else 0.0), "RESERVOIR": 0.02}.get(cfg.spatial, 0.0)
        if cfg.world == "NICHES" and cfg.spatial in ("LOCAL", "WELL_MIXED"):
            rate = 0.02
        if rate <= 0:
            return
        alive = [i for i, o in enumerate(self.cells) if o is not None]
        for i in alive:
            o = self.cells[i]
            if o is None or rng.random() > rate:
                continue
            if cfg.spatial == "NICHES_COMPETENCE_MIG" and rng.random() > o.score_ema:
                continue
            src = self.niche_of[i]
            dst = (src + 1) % cfg.n_niches if cfg.spatial != "RESERVOIR" else rng.randrange(cfg.n_niches)
            if cfg.spatial == "RESERVOIR" and src != 0:
                continue                                   # only the reservoir seeds outward
            targets = [j for j in range(cfg.cells) if self.niche_of[j] == dst and self.cells[j] is None]
            if not targets:
                continue
            j = rng.choice(targets)
            if cfg.spatial == "NICHES_POLLINATION" or cfg.spatial == "RESERVOIR":
                c = self._spawn(j, bytearray(o.tape), o.id, "pollination", lineage=o.lineage, glineage=o.glineage)    # a copy crosses, the source stays
            else:
                self.cells[j] = o; self.cells[i] = None; o.niche = dst
            self.migrations += 1; self.cross_niche_transport += 1
            self.events.append({"tick": self.tick, "kind": "migration", "id": o.id, "from_niche": src, "to_niche": dst, "policy": cfg.spatial})

    # ---- telemetry / genealogy / serendipity ------------------------------------------------------------------------------------
    def _ancestry(self, oid: int, depth: int = 40) -> List[int]:
        chain = []; cur: Optional[int] = oid
        while cur is not None and len(chain) < depth:
            chain.append(cur); cur = self.parent_of.get(cur)
        return chain

    def _descends_from_seed(self, oid: int) -> bool:
        for o in self.cells:
            if o is not None and o.id == oid:
                return o.lineage in self.seed_lineages
        return False

    def _modal_answers(self) -> List[Optional[int]]:
        out = []
        for k in range(self.cfg.n_niches):
            cnt: Dict[int, int] = {}
            for o in self.cells:
                if o is not None and o.niche == k and o.last_out is not None:
                    cnt[o.last_out] = cnt.get(o.last_out, 0) + 1
            out.append(max(cnt, key=cnt.get) if cnt else None)
        return out

    def _niche_persistent(self) -> List[bool]:
        occ = [0] * self.cfg.n_niches
        for o in self.cells:
            if o is not None:
                occ[o.niche % len(occ)] += 1
        per = self.cfg.cells / self.cfg.n_niches
        return [c > 0.3 * per for c in occ]

    def _standing_variation(self) -> dict:
        tapes = [bytes(o.tape) for o in self.cells if o is not None]
        uniq = len(set(tapes))
        if len(tapes) < 2:
            return {"n": len(tapes), "unique": uniq, "mean_hamming": None}
        rng = random.Random(self.tick)
        pairs = [(rng.choice(tapes), rng.choice(tapes)) for _ in range(min(64, len(tapes)))]
        mh = sum(sum(1 for x, y in zip(a, b) if x != y) for a, b in pairs) / len(pairs)
        return {"n": len(tapes), "unique": uniq, "mean_hamming": round(mh, 2)}

    def _telemetry(self, alive: List[Org], scores, steps_total, copy_attempts, interactions, deaths, ext_births) -> dict:
        n = len(alive)
        reps = [o for o in alive if o.last_repro_tick == self.tick]
        fids = [o.fidelity_last for o in alive if o.fidelity_last is not None and o.last_repro_tick == self.tick]
        spans = [o.repro_span for o in alive if o.repro_span is not None and o.last_repro_tick == self.tick]
        lineages = len({o.lineage for o in alive})
        arch = len({tuple(sorted((k for k in self._opcode_positions(o.tape)[:6]))) for o in alive}) if alive else 0
        niches = [0] * self.cfg.n_niches
        for o in alive:
            niches[o.niche % len(niches)] += 1
        best = max((o.score_ema for o in alive), default=0.0)
        rec = {"tick": self.tick, "alive": n, "interactions": interactions, "mean_score": round(sum(scores) / len(scores), 4) if scores else 0.0,
               "best_score": best, "solvers": sum(1 for o in alive if o.score_ema >= 0.85), "copy_attempts": copy_attempts,
               "replications": len(reps), "replication_rate": round(len(reps) / n, 4) if n else 0.0,
               "mean_fidelity": round(sum(fids) / len(fids), 3) if fids else None, "mean_repro_span": round(sum(spans) / len(spans), 1) if spans else None,
               "deaths": deaths, "external_births": ext_births, "lineages": lineages, "arch_clusters": arch,
               "mean_steps": round(steps_total / max(1, interactions), 1), "niches": niches, "refused_writes": self.refused_writes,
               "mean_age": round(sum(o.age for o in alive) / n, 1) if n else 0.0}
        # stasis / escape detector on the best score
        self.best_ema = 0.9 * self.best_ema + 0.1 * best
        if best >= self.best_ema + 0.25 and self.plateau_since >= 30:
            self.escape_events.append({"tick": self.tick, "best": best, "ema_before": round(self.best_ema, 3), "plateau_ticks": self.plateau_since})
            self.plateau_since = 0
        elif abs(best - self.best_ema) < 0.05:
            self.plateau_since += 1
        else:
            self.plateau_since = 0
        return rec

    def _snapshot(self, alive: List[Org], why: str) -> None:
        cnt: Dict[str, int] = {}
        for o in alive:
            h = bytes(o.tape).hex(); cnt[h] = cnt.get(h, 0) + 1
        top = sorted(cnt.items(), key=lambda kv: -kv[1])[:12]
        self.snapshots.append({"tick": self.tick, "why": why, "alive": len(alive), "unique": len(cnt), "tapes": top,
                               "env": [t.to_dict() for t in self.env.tasks], "variation": self._standing_variation()})

    _SERENDIPITY_KEYS = ("mean_steps", "replication_rate", "mean_fidelity", "mean_repro_span", "arch_clusters", "lineages", "mean_score", "alive")

    def _serendipity(self, rec: dict, alive: List[Org]) -> None:
        """Archive specimens when a tracked statistic changes sharply against its running mean."""
        fired = []
        for k in self._SERENDIPITY_KEYS:
            v = rec.get(k)
            if not isinstance(v, (int, float)):
                continue
            ema = self.stat_ema.get(k)
            if ema is not None and self.tick > 10:
                scale = max(abs(ema), 1e-6)
                if abs(v - ema) / scale > 0.6 and abs(v - ema) > 0.02:
                    fired.append((k, round(ema, 3), v))
            self.stat_ema[k] = v if ema is None else 0.8 * ema + 0.2 * v
        if fired and alive and len(self.specimens) < 200:
            best = max(alive, key=lambda o: (o.replications, o.score_ema))
            self.specimens.append({"tick": self.tick, "why": "sharp_change", "signals": fired, "id": best.id, "lineage": best.lineage,
                                   "tape": bytes(best.tape).hex(), "replications": best.replications, "score_ema": round(best.score_ema, 3),
                                   "mechanism": best.mechanism, "disasm": vm.disassemble(bytes(best.tape), 24)})
            self._snapshot(alive, "serendipity")

    def _exploit(self, kind: str, o: Org, tr) -> None:
        if len(self.exploits) < 100:
            self.exploits.append({"tick": self.tick, "kind": kind, "id": o.id, "lineage": o.lineage, "tape": bytes(o.tape).hex(),
                                  "io_writes": tr.io_writes, "io_corrupt": tr.io_corrupt, "reads_in": tr.reads_in, "outputs": tr.outputs[:4], "frozen_specimen": True})

    # ---- run ----------------------------------------------------------------------------------------------------------------------
    def run(self) -> dict:
        for _ in range(self.cfg.ticks):
            self.step()
            if not any(o is not None for o in self.cells):
                self.extinctions += 1
                self.events.append({"tick": self.tick, "kind": "extinction"})
                break
        alive = [o for o in self.cells if o is not None]
        self._snapshot(alive, "final")
        return self.summary(alive)

    def summary(self, alive: List[Org]) -> dict:
        cfg = self.cfg
        logs = self.ticks_log; last = logs[-1] if logs else {}
        tail = logs[-20:] if logs else []
        def mean(key):
            vals = [r[key] for r in tail if isinstance(r.get(key), (int, float))]
            return round(sum(vals) / len(vals), 4) if vals else None
        top = sorted(alive, key=lambda o: (o.replications, o.score_ema), reverse=True)[:5]
        return {
            "ticks_run": len(logs), "final_alive": len(alive), "alive_fraction": round(len(alive) / cfg.cells, 3), "cells": cfg.cells,
            "seed_lineage_share": round(sum(1 for o in alive if o.glineage in self.seed_lineages) / len(alive), 3) if alive else 0.0,
            "seed_causal_share": round(sum(1 for o in alive if o.lineage in self.seed_lineages) / len(alive), 3) if alive else 0.0,
            "captures": self.captures, "null_rewrites": self.null_rewrites, "genetic_lineages_final": len({o.glineage for o in alive}),
            "hifi_replication_rate_tail": round(sum(1 for r in logs[-20:] if (r.get("mean_fidelity") or 0) >= 0.9 and r.get("replication_rate", 0) > 0) / max(1, len(logs[-20:])), 3),
            "extinct": len(alive) == 0, "external_births": self.external_births, "endogenous_births": self.endogenous_births,
            "births_by_mechanism": self.births_by_mech, "refused_writes": self.refused_writes, "overwrite_deaths": self.overwrite_deaths,
            "deaths": self.deaths, "migrations": self.migrations, "cross_niche_transport": self.cross_niche_transport,
            "replication_rate_tail": mean("replication_rate"), "mean_fidelity_tail": mean("mean_fidelity"), "repro_span_tail": mean("mean_repro_span"),
            "mean_score_tail": mean("mean_score"), "best_score_tail": mean("best_score"), "solvers_tail": mean("solvers"),
            "lineages_final": last.get("lineages"), "arch_clusters_final": last.get("arch_clusters"), "mean_steps_tail": mean("mean_steps"),
            "first_crossing": self.first_crossing, "first_replication": self.first_replication,
            "escape_events": self.escape_events, "n_exploits": len(self.exploits), "exploit_kinds": sorted({e["kind"] for e in self.exploits}),
            "n_specimens": len(self.specimens), "env_history": self.env.history[-10:], "env_lineage": self.env.lineage,
            "niche_occupancy_final": last.get("niches"), "coexistence_ticks": sum(1 for r in logs if r.get("lineages", 0) >= 2),
            "top": [{"id": o.id, "lineage": o.lineage, "replications": o.replications, "score_ema": round(o.score_ema, 3), "span": o.repro_span,
                     "fidelity": o.fidelity_last, "age": o.age, "mechanism": o.mechanism, "tape": bytes(o.tape).hex(), "unique_bytes": len(set(o.tape)),
                     "disasm": vm.disassemble(bytes(o.tape), 20)} for o in top],
        }
