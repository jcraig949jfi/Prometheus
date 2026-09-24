"""ENVGATE-01 engine: the frozen z80atlas physics for the held configuration (mechanism.HELD), plus inflow chambers and input
transforms. Five arms of one replicate block are stepped in LOCKSTEP in one process so that they share, exactly, the inflow tape
stream, the base environment stream, the offline ruler verdict for every arriving tape and a pure-function VM memo.

Physics identity. For the held configuration (shared layout, implicit_survival, ENDOGENOUS_COPY, well_mixed, fixed env, unlimited
resources, local_byte mutation) the per-organism step below is the z80atlas engine.run step, draw for draw. legacy=True reproduces
z80atlas.engine.run exactly (initial random population, campaign case keys, one RNG for world and mutation, vm_steps budget); a test
pins it. Energy is not modelled: under implicit_survival (no metabolic/exec/tape/resource pressure) it has no consequence.

Streams (all arm-independent; seeds recorded): inflow tapes seed_from('envgate.inflow', block); environment words
seed_from('envgate.env', block, cell, epoch); world (order, neighbours, deaths) seed_from('envgate.world', block); mutation (copy noise,
background mutation) seed_from('envgate.mutation', block). The inflow and environment code never touches the world or mutation RNG.

No vm_steps budget in assay mode: a step budget would end worlds at behaviour-dependent times and make exposure arm-dependent.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import vm, tasks as T
from archaeon.z80atlas import engine as ZE
from archaeon.z80atlas.grammar import FROZEN as F
from archaeon.envgate import mechanism as M

G = M.HELD["G"]; N = M.HELD["N_ecology"]; STEP_CAP = M.HELD["step_cap"]; TASK = M.HELD["task"]; NC = F["cases_per_opportunity"]
ZERO = bytes(G)
ORIGIN_INFLOW, ORIGIN_CONTROL = "random_inflow", "control_inserted"


class Memo:
    """Exact cache of the pure function vm.execute(tape, nbr, (x,), STEP_CAP, copy_prim=True). Speed only; never changes a result."""
    # An execution that never ran IN (inputs_read == 0) cannot depend on the input: it is stored once under inputs=None and serves
    # every input for that (tape, neighbour). Exact by the VM's semantics (inputs enter only through IN); tested against vm.execute.
    def __init__(self, cap: int = 300_000):
        self.d: Dict[tuple, dict] = {}; self.cap = cap; self.hits = 0; self.miss = 0

    def run(self, tape: bytes, nbr: bytes, inputs: tuple) -> dict:
        d = self.d; r = d.get((tape, nbr, None))
        if r is None: r = d.get((tape, nbr, inputs))
        if r is None:
            r = vm.execute(tape, nbr, inputs, STEP_CAP, True, -1.0); self.put(tape, nbr, inputs, r); self.miss += 1
        else:
            self.hits += 1
        return r

    def put(self, tape: bytes, nbr: bytes, inputs: tuple, r: dict):
        if len(self.d) >= self.cap: self.d.clear()
        self.d[(tape, nbr, None if r["inputs_read"] == 0 else inputs)] = r


class EnvStream:
    """Base environment words per (cell, epoch), computed once and shared by every arm of the block."""
    def __init__(self, block: int):
        self.block = block; self.epoch = -1; self.cache: Dict[int, list] = {}

    def words(self, cell: int, epoch: int) -> list:
        if epoch != self.epoch: self.epoch = epoch; self.cache = {}
        w = self.cache.get(cell)
        if w is None:
            r = SplitMix64(seed_from("envgate.env", self.block, cell, epoch)); w = [(r.next_u32(), r.next_u32()) for _ in range(NC)]
            self.cache[cell] = w
        return w


def inflow_stream(block: int):
    r = SplitMix64(seed_from("envgate.inflow", block))
    while True:
        yield bytes(r.randbelow(256) for _ in range(G))


class World:
    """One arm of one block. Cells 0..N-1 are the ecology, N..N+K-1 the chambers."""
    def __init__(self, arm: str, block: int, K: int, legacy_spec: Optional[dict] = None, legacy_seed: int = 0):
        self.arm_name = arm; self.arm = M.ARMS[arm]; self.block = block; self.K = K; self.C = N + K; self.legacy = legacy_spec is not None
        if self.legacy:                                                     # z80atlas.engine.run draw order: one RNG for everything
            self.rng = SplitMix64(seed_from("z80atlas.run", legacy_spec["spec_id"], legacy_seed)); self.mrng = self.rng; self.spec = legacy_spec; self.seed = legacy_seed
        else:
            self.rng = SplitMix64(seed_from("envgate.world", block)); self.mrng = SplitMix64(seed_from("envgate.mutation", block))
        C = self.C
        self.genomes: List[Optional[bytes]] = [None] * C; self.age = [0] * C; self.oid = [0] * C; self.lin = [0] * C; self.parent = [0] * C
        self.born = [0] * C; self.gen = [0] * C; self.anc: List[frozenset] = [frozenset()] * C; self.score = [0.0] * C
        self.steps = 0; self.tel_every = 50
        self.next_id = 1; self.births = 0; self.births_endo = 0; self.fid_sum = 0.0; self.fid_n = 0; self.refused_into_chamber = 0
        self.founder: Dict[int, dict] = {}                                  # founders that ever produced an ecology birth, plus controls
        self.chamber_fid: Dict[int, int] = {}                               # chamber cell -> founder id currently tested there
        self.fid_meta: Dict[int, dict] = {}                                 # founder id -> {arrival, epoch_in, cell, origin} for chambered tapes
        self.lcount: Dict[int, int] = {}                                    # lineage -> ecology members now
        self.lstat: Dict[int, dict] = {}                                    # lineage -> stats (only lineages with ecology members)
        self.checks: Dict[int, List[int]] = {}                              # epoch -> founders whose persistence is checked then
        self.telemetry: List[list] = []
        if self.legacy:
            self._legacy_init()

    # ---------------------------------------------------------------- legacy initial population (z80atlas init=random, draw for draw)
    def _legacy_init(self):
        rng = self.rng
        for i in range(N):
            if rng.randbelow(100) < F["init_fill_pct"]:
                self.genomes[i] = ZE.random_tape(rng, G)
                self.oid[i] = self.next_id; self.lin[i] = self.next_id; self.age[i] = rng.randbelow(F["max_age"] // 2); self.anc[i] = frozenset((self.next_id,)); self.next_id += 1

    # ---------------------------------------------------------------- inflow (touches no world/mutation RNG)
    def arrive(self, cell: int, tape: bytes, arrival: int, epoch: int, origin: str = ORIGIN_INFLOW):
        old = self.chamber_fid.get(cell)
        if old is not None: self._remove_founder(old, epoch)
        f = self.next_id; self.next_id += 1
        self.genomes[cell] = tape; self.age[cell] = 0; self.oid[cell] = f; self.lin[cell] = f; self.parent[cell] = 0; self.born[cell] = epoch; self.gen[cell] = 0
        self.anc[cell] = frozenset((f,)); self.score[cell] = 0.0; self.chamber_fid[cell] = f
        self.fid_meta[f] = {"arrival": arrival, "epoch_in": epoch, "cell": cell, "origin": origin, "tape": tape}

    def clear_chambers(self, epoch: int):
        for cell in list(self.chamber_fid):
            self._remove_founder(self.chamber_fid.pop(cell), epoch); self.genomes[cell] = None

    def _remove_founder(self, f: int, epoch: int):
        meta = self.fid_meta.pop(f)
        rec = self.founder.get(f)
        if rec is not None:
            rec["removed_epoch"] = epoch
            self.checks.setdefault(epoch + M.DEFAULTS["persistence_multiple"] * F["max_age"], []).append(f)

    # ---------------------------------------------------------------- one epoch (z80atlas engine.run loop body for the held config)
    def cases(self, env: EnvStream, i: int, epoch: int) -> list:
        if self.legacy:
            return T.cases(TASK, (self.spec["spec_id"], self.seed, i), NC, epoch)
        return [(M.transform(self.arm, u, v),) for u, v in env.words(i, epoch)]

    def step(self, epoch: int, env: EnvStream, memo: Memo):
        rng = self.rng; C = self.C; K = self.K; g = self.genomes
        occupied = [i for i in range(C) if g[i] is not None]
        order = list(occupied)
        for a in range(len(order) - 1, 0, -1):
            b_ = rng.randbelow(a + 1); order[a], order[b_] = order[b_], order[a]
        for i in order:
            if g[i] is None: continue
            if i >= N:                                                      # chamber: neighbour is a random ecology cell
                j = rng.randbelow(N)
            else:
                j = rng.randbelow(N - 1); j = j if j < i else j + 1
            nbr = g[j] if g[j] is not None else ZERO
            cs = self.cases(env, i, epoch); res0 = None; sc = 0.0
            for ci, c in enumerate(cs):
                r = memo.run(g[i], nbr, c); self.steps += r["steps"]
                if ci == 0: res0 = r
                sc += T.score_case(TASK, r["outputs"], c, {"K": 0})
            self.score[i] = sc / len(cs); self.age[i] += 1
            if res0["writes_nbr"] > 0:
                mask = res0["nbr_mask"]
                if sum(mask) / G >= F["copy_min_frac"]:
                    child = ZE.copy_noise(res0["nbr_window"], mask, self.mrng, F["copy_noise"])
                    donor = self.anc[j] if ZE.donor_contributes(g[j] is not None, res0, "ENDOGENOUS_COPY") else frozenset()
                    self._place(j, child, i, ZE.fidelity(child, g[i]), epoch, cs[0][0] if cs[0] else 0, donor)
        # background mutation + deaths: ecology only (chambers are test chambers: no mutation, no death)
        for i in range(N):
            if g[i] is None: continue
            if rng.randbelow(1000000) < F["background_mutation"] * 1000000:
                g[i] = ZE.mutate(g[i], M.HELD["mutation"], self.mrng, F["mutation_rate"])
            dead = self.age[i] > F["max_age"]
            if rng.randbelow(1000000) < F["death_rate"] * 1000000: dead = True
            if dead: self._kill(i, epoch)
        for f in self.checks.pop(epoch, []):
            rec = self.founder[f]; rec["alive_at_check"] = self.lcount.get(f, 0) > 0; rec["count_at_check"] = self.lcount.get(f, 0)
        pop = sum(1 for i in range(N) if g[i] is not None)
        if epoch % self.tel_every == 0:
            self.telemetry.append([epoch, pop, self.births, self.births_endo, round(self.fid_sum / self.fid_n, 3) if self.fid_n else None, len(self.lcount)])
        for L, c in self.lcount.items():
            st = self.lstat[L]
            if c > st["peak"]: st["peak"] = c; st["peak_epoch"] = epoch
            st["last_alive"] = epoch
            if epoch % 250 == 0: st["traj"].append([epoch, c])

    def _place(self, j: int, child: bytes, p: int, fid: float, epoch: int, x: int, donor: frozenset):
        g = self.genomes
        if j >= N:                                                          # chambers are write-protected (never reached: j is ecology)
            self.refused_into_chamber += 1; return
        if g[j] is not None: self._kill(j, epoch, overwritten=True)
        L = self.lin[p]
        g[j] = child; self.age[j] = 0; self.oid[j] = self.next_id; self.lin[j] = L; self.parent[j] = self.oid[p]; self.born[j] = epoch
        self.gen[j] = self.gen[p] + 1; self.anc[j] = self.anc[p] | donor; self.score[j] = 0.0; self.next_id += 1
        self.births += 1; self.births_endo += 1; self.fid_sum += fid; self.fid_n += 1
        exact = child == g[p]
        if L not in self.founder:                                           # first ecology birth of this lineage
            meta = self.fid_meta.get(L, {})
            self.founder[L] = {"founder": L, "arrival": meta.get("arrival"), "epoch_in": meta.get("epoch_in"), "cell": meta.get("cell"), "origin": meta.get("origin", "legacy"),
                               "tape": (meta.get("tape") or b"").hex(), "first_birth_epoch": epoch, "first_birth_input": x, "first_birth_fid": round(fid, 3),
                               "first_exact_epoch": None, "first_exact_input": None, "removed_epoch": None, "alive_at_check": None}
            self.lstat[L] = {"peak": 0, "peak_epoch": epoch, "last_alive": epoch, "births": 0, "exact": 0, "fid_sum": 0.0, "max_gen": 0, "traj": [], "inputs": {}, "chamber_births": 0, "chamber_exact": 0, "exact_inputs": {}}
        rec = self.founder[L]; st = self.lstat[L]
        if exact and rec["first_exact_epoch"] is None: rec["first_exact_epoch"] = epoch; rec["first_exact_input"] = x
        st["births"] += 1; st["exact"] += exact; st["fid_sum"] += fid; st["max_gen"] = max(st["max_gen"], self.gen[j])
        if p >= N:                                                          # which inputs let the chambered founder copy out
            st["inputs"][x] = st["inputs"].get(x, 0) + 1; st["chamber_births"] += 1
            if exact: st["chamber_exact"] += 1; st["exact_inputs"][x] = st["exact_inputs"].get(x, 0) + 1
        self.lcount[L] = self.lcount.get(L, 0) + 1

    def _kill(self, i: int, epoch: int, overwritten: bool = False):
        L = self.lin[i]; self.genomes[i] = None; self.anc[i] = frozenset()
        if L not in self.lcount: return                                     # untracked (legacy initial founder)
        c = self.lcount[L] - 1
        if c <= 0: self.lcount.pop(L)
        else: self.lcount[L] = c

    # ---------------------------------------------------------------- establishment (ESTABLISHED_RANDOM_INFLOW_LINEAGE)
    def established(self) -> List[dict]:
        out = []; min_pop = M.DEFAULTS["min_pop_frac"] * N
        for f, rec in self.founder.items():
            st = self.lstat[f]
            ok = (rec["origin"] == ORIGIN_INFLOW and rec["removed_epoch"] is not None and rec["alive_at_check"] is True and st["births"] >= 1
                  and (st["peak"] >= min_pop or st["max_gen"] >= M.DEFAULTS["min_generation"]))
            if ok: out.append(f)
        return out

    def ecology_tapes(self, L: int) -> Dict[str, int]:
        d: Dict[str, int] = {}
        for i in range(N):
            if self.genomes[i] is not None and self.lin[i] == L: d[self.genomes[i].hex()] = d.get(self.genomes[i].hex(), 0) + 1
        return d


def tape_sha(t: bytes) -> str:
    return hashlib.sha256(t).hexdigest()[:16]


def legacy_run(spec: dict, seed: int) -> dict:
    """z80atlas.engine.run semantics for the held configuration (tests only): initial random population, campaign case keys, one RNG,
    vm_steps budget, extinction stop. Returns per-epoch [pop, births, endo, fid] and the final population tapes."""
    w = World("U", 0, 0, legacy_spec=spec, legacy_seed=seed); w.tel_every = 1; memo = Memo(); epoch = 0
    while epoch < spec["budget"]["max_epochs"] and w.steps < spec["budget"]["vm_steps"]:
        if not any(w.genomes[i] is not None for i in range(N)): break
        w.step(epoch, None, memo); epoch += 1
    return {"telemetry": [[r[1], r[2], r[3], r[4]] for r in w.telemetry], "final": [w.genomes[i].hex() for i in range(N) if w.genomes[i] is not None]}
