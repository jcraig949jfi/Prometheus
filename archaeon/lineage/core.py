"""Attributed ecology core (Phase A genetic-attribution repair; used by ENVGATE-02 and RIE-01, and by the ENVGATE-01 audit replays).

Physics: identical to archaeon.envgate.engine (itself identical to the frozen z80atlas physics for its configuration), draw for draw:
same shuffle, neighbour, case, copy-noise, background-mutation and death order. With the ENVGATE-01 input source it reproduces an
ENVGATE-01 world exactly (tested). What is new is observation only:

FOUR IDENTITIES PER BIRTH (operator ruling, Phase A1)
  executor            the organism whose execution produced the child window (cell i, oid, genetic lineage)
  executed material   opcode fetches by source: the executor's own material (E), the neighbour's material (N), other
  child contributors  per-byte genetic attribution of the child genome (below); conservative sets for computed bytes
  ecological host     the executor when the child's template is NOT the executor (it supplied execution + the target cell)

BYTE-LEVEL MATERIAL (Phase A2). Every organism carries orig: 32 material ids, one per genome byte.
  founder material    id = fid * 32 + pos >= 32 (a chambered arrival's or a control's original bytes)
  new material        id < 0; kind = (-id) % 8: 1 mutation (copy noise / background), 2 input-derived, 3 constant/zero, 4 computed
Child byte j: if copy noise changed it -> new mutation; else by taint label (lineage.taint_vm): ('E',p) -> executor.orig[p];
('N',q) -> occupant.orig[q] (zeros of an empty cell are constant material); I -> input; K/Z -> constant; ('X', S) -> computed, with
contributors S recorded conservatively.
GENETIC LINEAGE (glin): template = whichever of executor / neighbour contributed more COPIED bytes. If the template contributed >= G/2
bytes the child continues the template's glin (genome reproduction); otherwise the child ORIGINATES a new glin (a new genome, root
'origination', parents = contributing glins). Foreign execution that emits a resident genome therefore stays in the resident's glin;
the executor gets host credit only. Inserted (control) material taints every glin it contributes to; it can never become random.
Fast path: a birth with a full-window write, no neighbour reads, no foreign execution and window == executor genome is attributed
E(p)->p without running the taint VM (tested equal to the taint path).
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Callable, Dict, List, Optional

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import vm, tasks as T
from archaeon.z80atlas import engine as ZE
from archaeon.z80atlas.grammar import FROZEN as F
from archaeon.lineage.taint_vm import execute_taint

G = 32; N = F["N"]; NC = F["cases_per_opportunity"]; STEP_CAP = F["budgets"]["late"]["step_cap"]; TASK = "ECHO_forced"
ZERO = bytes(G)
MUT, INP, CONST, COMP = 1, 2, 3, 4
ORIGIN_INFLOW, ORIGIN_CONTROL, ORIGIN_ORIGINATED = "random_inflow", "control_inserted", "originated"
PERSIST = 3 * F["max_age"]; MIN_POP = 0.25 * N; MIN_GEN = 10


class Memo:
    def __init__(self, copy_prim: bool = True, cap: int = 300_000):
        self.d: Dict[tuple, dict] = {}; self.cap = cap; self.cp = copy_prim; self.hits = 0; self.miss = 0

    def run(self, tape, nbr, inputs):
        d = self.d; r = d.get((tape, nbr, None))
        if r is None: r = d.get((tape, nbr, inputs))
        if r is None:
            r = vm.execute(tape, nbr, inputs, STEP_CAP, self.cp, -1.0); self.put(tape, nbr, inputs, r); self.miss += 1
        else:
            self.hits += 1
        return r

    def put(self, tape, nbr, inputs, r):
        if len(self.d) >= self.cap: self.d.clear()
        self.d[(tape, nbr, None if r["inputs_read"] == 0 else inputs)] = r


class World:
    """Ecology cells 0..N-1 (+ chambers N..N+K-1). `inputs(world, cell, epoch)` supplies the NC case tuples; `neighbour(world, i)`
    picks an ecology neighbour for an ecology cell (default well-mixed); chambers face a random ecology cell."""
    def __init__(self, name: str, K: int, world_seed: tuple, mut_seed: tuple, inputs: Callable, neighbour: Callable = None,
                 copy_prim: bool = True, event_cap: int = 4000):
        self.name = name; self.K = K; self.C = N + K; self.inputs = inputs; self.neighbour = neighbour; self.cp = copy_prim
        self.rng = SplitMix64(seed_from(*world_seed)); self.mrng = SplitMix64(seed_from(*mut_seed))
        C = self.C
        self.genomes: List[Optional[bytes]] = [None] * C; self.orig: List[Optional[tuple]] = [None] * C
        self.age = [0] * C; self.oid = [0] * C; self.lin = [0] * C; self.gen = [0] * C; self.glin = [0] * C; self.ggen = [0] * C; self.ins = [False] * C
        self.next_id = 1; self.next_mat = 1; self.next_glin = 1; self.steps = 0
        self.births = 0; self.births_mech = defaultdict(int); self.taint_calls = 0; self.fast_calls = 0
        self.chamber = {}                                                     # cell -> (oid, glin, arrival)
        self.pending: Dict[int, dict] = {}                                     # unregistered arrival glins (-fid) -> arrival info
        self.gl: Dict[int, dict] = {}                                          # glin registry
        self.alive = defaultdict(int)                                         # glin -> ecology members
        self.lin_alive = defaultdict(int)                                     # parent-chain lineage -> ecology members (ENVGATE-01 comparison)
        self.lin_rec: Dict[int, dict] = {}                                     # parent-chain records (as ENVGATE-01)
        self.checks = defaultdict(list); self.lin_checks = defaultdict(list)
        self.events: List[dict] = []; self.event_cap = event_cap
        self.telemetry: List[list] = []; self.tel_every = 50

    # ---------------------------------------------------------------- material helpers
    def _new(self, kind: int) -> int:
        m = -(self.next_mat * 8 + kind); self.next_mat += 1; return m

    def _glin_new(self, root: str, epoch: int, origin: str, inserted: bool, **kw) -> int:
        g = self.next_glin; self.next_glin += 1
        self.gl[g] = {"glin": g, "root": root, "origin": origin, "inserted": inserted, "epoch": epoch, "births": 0, "births_hosted": 0,
                      "births_self": 0, "exact": 0, "fid_sum": 0.0, "peak": 0, "max_ggen": 0, "root_end": None, "alive_at_check": None,
                      "last_alive": None, "first_birth_epoch": None, "first_birth_input": None, "hosts": defaultdict(int), "traj": [], **kw}
        return g

    # ---------------------------------------------------------------- inflow (no world/mutation RNG)
    def arrive(self, cell: int, tape: bytes, arrival: int, epoch: int, origin: str = ORIGIN_INFLOW):
        if cell in self.chamber: self._chamber_out(cell, epoch)
        f = self.next_id; self.next_id += 1
        # the arrival's glin is registered lazily at its first birth (-f = unregistered): millions of arrivals never reproduce
        self.genomes[cell] = tape; self.orig[cell] = tuple(f * 32 + p for p in range(G)); self.age[cell] = 0; self.oid[cell] = f
        self.lin[cell] = f; self.gen[cell] = 0; self.glin[cell] = -f; self.ggen[cell] = 0; self.ins[cell] = origin == ORIGIN_CONTROL
        self.chamber[cell] = (f, None, arrival); self.pending[-f] = {"arrival": arrival, "epoch": epoch, "origin": origin, "tape": tape, "cell": cell}
        self.lin_rec[f] = {"arrival": arrival, "epoch_in": epoch, "births": 0, "removed": None, "alive_at_check": None, "peak": 0, "max_gen": 0, "tape": tape.hex()}

    def _chamber_out(self, cell: int, epoch: int):
        f, _, a = self.chamber.pop(cell); g = self.glin[cell]; self.genomes[cell] = None
        if g < 0: self.pending.pop(g, None)
        else: self.gl[g]["root_end"] = epoch; self.checks[epoch + PERSIST].append(g)
        lr = self.lin_rec[f]; lr["removed"] = epoch
        if lr["births"]: self.lin_checks[epoch + PERSIST].append(f)
        else: del self.lin_rec[f]

    def clear_chambers(self, epoch: int):
        for c in list(self.chamber): self._chamber_out(c, epoch)

    def insert_ecology(self, cell: int, tape: bytes, epoch: int, origin: str):
        """Controls/tests only: place an organism directly in an ecology cell."""
        f = self.next_id; self.next_id += 1
        g = self._glin_new("inserted" if origin == ORIGIN_CONTROL else "seeded_test", epoch, origin, origin == ORIGIN_CONTROL, founder_oid=f, tape=tape.hex())
        if self.genomes[cell] is not None: self._kill(cell, epoch)
        self.genomes[cell] = tape; self.orig[cell] = tuple(f * 32 + p for p in range(G)); self.age[cell] = 0; self.oid[cell] = f; self.lin[cell] = f
        self.gen[cell] = 0; self.glin[cell] = g; self.ggen[cell] = 0; self.ins[cell] = origin == ORIGIN_CONTROL
        self.alive[g] += 1; self.gl[g]["root_oid"] = f
        return g

    # ---------------------------------------------------------------- one epoch (envgate engine body, draw for draw)
    def step(self, epoch: int, memo: Memo):
        rng = self.rng; g = self.genomes
        occupied = [i for i in range(self.C) if g[i] is not None]
        order = list(occupied)
        for a in range(len(order) - 1, 0, -1):
            b_ = rng.randbelow(a + 1); order[a], order[b_] = order[b_], order[a]
        for i in order:
            if g[i] is None: continue
            if i >= N: j = rng.randbelow(N)
            elif self.neighbour is None:
                j = rng.randbelow(N - 1); j = j if j < i else j + 1
            else: j = self.neighbour(self, i)
            nbr = g[j] if g[j] is not None else ZERO
            cs = self.inputs(self, i, epoch); res0 = None
            for ci, c in enumerate(cs):
                r = memo.run(g[i], nbr, c); self.steps += r["steps"]
                if ci == 0: res0 = r
            self.age[i] += 1
            if res0["writes_nbr"] > 0:
                mask = res0["nbr_mask"]
                if sum(mask) / G >= F["copy_min_frac"]:
                    child = ZE.copy_noise(res0["nbr_window"], mask, self.mrng, F["copy_noise"])
                    self._birth(i, j, child, res0, nbr, cs[0], epoch)
        for i in range(N):
            if g[i] is None: continue
            if rng.randbelow(1000000) < F["background_mutation"] * 1000000:
                new = ZE.mutate(g[i], "local_byte", self.mrng, F["mutation_rate"])
                if new != g[i]:
                    o = list(self.orig[i])
                    for p in range(G):
                        if new[p] != g[i][p]: o[p] = self._new(MUT)
                    self.orig[i] = tuple(o)
                g[i] = new
            dead = self.age[i] > F["max_age"]
            if rng.randbelow(1000000) < F["death_rate"] * 1000000: dead = True
            if dead: self._kill(i, epoch)
        for gg in self.checks.pop(epoch, []):
            self.gl[gg]["alive_at_check"] = self.alive.get(gg, 0) > 0; self.gl[gg]["count_at_check"] = self.alive.get(gg, 0)
        for f in self.lin_checks.pop(epoch, []):
            if f in self.lin_rec: self.lin_rec[f]["alive_at_check"] = self.lin_alive.get(f, 0) > 0
        for gg, c in self.alive.items():
            st = self.gl[gg]
            if c > st["peak"]: st["peak"] = c
            st["last_alive"] = epoch
            if epoch % 250 == 0: st["traj"].append([epoch, c])
        for f, c in self.lin_alive.items():
            lr = self.lin_rec.get(f)
            if lr is not None and c > lr["peak"]: lr["peak"] = c
        if epoch % self.tel_every == 0:
            pop = sum(1 for i in range(N) if g[i] is not None)
            self.telemetry.append([epoch, pop, self.births, len(self.alive)])

    # ---------------------------------------------------------------- attribution
    def _labels(self, i, nbr, x, res0, child_window):
        m = res0["nbr_mask"]
        if res0["exec_foreign"] == 0 and res0["reads_nbr"] == 0 and all(m) and not res0["sealed"] and child_window == self.genomes[i]:
            self.fast_calls += 1
            return [("E", p) for p in range(G)], {"self": res0["steps"], "nbr": 0, "other": 0}
        self.taint_calls += 1
        res, wl, ex = execute_taint(self.genomes[i], nbr, x, STEP_CAP, self.cp, -1.0)
        if res != res0:
            raise AssertionError("ATTRIBUTION: taint shadow disagrees with the frozen VM -- refusing to attribute")
        return wl, ex

    def attribute(self, i, j, child, res0, nbr, x):
        """Returns (orig tuple, stats) for a child written by executor i into cell j (pure: no world state changed)."""
        wl, ex = self._labels(i, nbr, x, res0, res0["nbr_window"])
        occ = self.genomes[j] is not None; oi = self.orig[i]; oj = self.orig[j] if occ else None
        o = []; nE = nN = 0; contrib_g = set(); ins = False; comp = 0
        for p in range(G):
            if child[p] != res0["nbr_window"][p]:
                o.append(self._new(MUT)); continue
            lb = wl[p]
            if lb[0] == "E":
                o.append(oi[lb[1]]); nE += 1
            elif lb[0] == "N":
                if occ: o.append(oj[lb[1]]); nN += 1
                else: o.append(self._new(CONST))
            elif lb[0] == "I": o.append(self._new(INP))
            elif lb[0] == "X":
                o.append(self._new(COMP)); comp += 1
                for s in lb[1]:
                    if s[0] == "E": contrib_g.add(self.glin[i]); ins = ins or self.ins[i]
                    elif occ: contrib_g.add(self.glin[j]); ins = ins or self.ins[j]
            else: o.append(self._new(CONST))
        if nE: contrib_g.add(self.glin[i]); ins = ins or self.ins[i]
        if nN: contrib_g.add(self.glin[j]); ins = ins or self.ins[j]
        return tuple(o), {"nE": nE, "nN": nN, "comp": comp, "exec": ex, "contrib": contrib_g, "ins": ins, "occupied": occ}

    def _register(self, cell: int) -> int:
        g = self.glin[cell]
        if g >= 0: return g
        info = self.pending.pop(g)
        ng = self._glin_new("arrival", info["epoch"], info["origin"], info["origin"] == ORIGIN_CONTROL, arrival=info["arrival"], founder_oid=-g, tape=info["tape"].hex())
        self.glin[cell] = ng; return ng

    def _birth(self, i, j, child, res0, nbr, x, epoch):
        if self.glin[i] < 0: self._register(i)
        if self.genomes[j] is not None and self.glin[j] < 0: self._register(j)
        o, s = self.attribute(i, j, child, res0, nbr, x)
        tmpl_exec = s["nE"] >= s["nN"]; tcount = s["nE"] if tmpl_exec else s["nN"]
        tmpl_cell = i if tmpl_exec else j
        exact = child == self.genomes[i]
        executed = "self" if s["exec"]["nbr"] == 0 else ("neighbour" if s["exec"]["self"] == 0 else "mixed")
        if tcount >= G // 2:
            gg = self.glin[tmpl_cell]; ggen = self.ggen[tmpl_cell] + 1
            mech = "SELF_COPY" if tmpl_exec else ("HOST_EXECUTION" if s["exec"]["nbr"] > 0 else "NEIGHBOUR_COPY")
        else:
            gg = self._glin_new("origination", epoch, ORIGIN_CONTROL if s["ins"] else ORIGIN_ORIGINATED, s["ins"], parents=sorted(s["contrib"]),
                                executor_glin=self.glin[i], nE=s["nE"], nN=s["nN"], comp=s["comp"], tape=child.hex())
            ggen = 0; mech = "ORIGINATION"
        if s["nE"] >= 4 and s["nN"] >= 4: mech += "+RECOMBINATION"
        host = self.glin[i] if (not tmpl_exec and not mech.startswith("ORIGINATION")) else None
        # place (parent-chain fields kept exactly as ENVGATE-01 for comparison)
        if self.genomes[j] is not None: self._kill(j, epoch)
        L = self.lin[i]
        self.genomes[j] = child; self.orig[j] = o; self.age[j] = 0; self.oid[j] = self.next_id; self.next_id += 1; self.lin[j] = L; self.gen[j] = self.gen[i] + 1
        self.glin[j] = gg; self.ggen[j] = ggen; self.ins[j] = s["ins"]
        self.births += 1; self.births_mech[mech] += 1; self.alive[gg] += 1; self.lin_alive[L] += 1
        st = self.gl[gg]; st["births"] += 1; st["exact"] += exact; st["max_ggen"] = max(st["max_ggen"], ggen)
        if st["first_birth_epoch"] is None: st["first_birth_epoch"] = epoch; st["first_birth_input"] = x[0] if x else 0; st["first_birth_mech"] = mech
        if host is not None and host != gg: st["births_hosted"] += 1; st["hosts"][host] += 1
        elif tmpl_exec: st["births_self"] += 1
        if mech.startswith("ORIGINATION"): st["root_oid"] = self.oid[j]
        lr = self.lin_rec.get(L)
        if lr is not None:
            lr["births"] += 1; lr["max_gen"] = max(lr["max_gen"], self.gen[j])
        if len(self.events) < self.event_cap:
            self.events.append({"e": epoch, "executor_cell": i, "executor_oid": self.oid[i], "executor_glin": self.glin[i], "executed_material": executed,
                                "exec_counts": s["exec"], "child_cell": j, "child_glin": gg, "template": "executor" if tmpl_exec else "neighbour",
                                "template_glin": self.glin[tmpl_cell] if not mech.startswith("ORIGINATION") else None, "contributors": sorted(s["contrib"]),
                                "copied_exec": s["nE"], "copied_nbr": s["nN"], "computed": s["comp"], "host_glin": host, "mechanism": mech,
                                "input": x[0] if x else None, "exact": exact, "novel_genome": mech.startswith("ORIGINATION")})

    def _kill(self, i, epoch):
        gg = self.glin[i]; L = self.lin[i]
        self.genomes[i] = None
        if i < N:
            c = self.alive[gg] - 1
            if c <= 0:
                self.alive.pop(gg, None)
            else: self.alive[gg] = c
            st = self.gl[gg]
            if st.get("root_oid") == self.oid[i] and st["root_end"] is None:
                st["root_end"] = epoch; self.checks[epoch + PERSIST].append(gg)
            if L in self.lin_alive:
                c = self.lin_alive[L] - 1
                if c <= 0: self.lin_alive.pop(L)
                else: self.lin_alive[L] = c

    def migrate(self, i, j):
        """Move an organism between ecology cells with all genetic AND ecological state (RIE topologies with migration)."""
        for arr in (self.genomes, self.orig, self.age, self.oid, self.lin, self.gen, self.glin, self.ggen, self.ins):
            arr[j] = arr[i]
        self.genomes[i] = None

    # ---------------------------------------------------------------- endpoints
    def genetic_establishments(self) -> List[int]:
        out = []
        for gg, st in self.gl.items():
            if st["inserted"] or st["origin"] == ORIGIN_CONTROL: continue
            if st["births"] >= 1 and st["root_end"] is not None and st["alive_at_check"] is True and (st["peak"] >= MIN_POP or st["max_ggen"] >= MIN_GEN):
                out.append(gg)
        return out

    def parent_chain_establishments(self) -> List[int]:
        """ENVGATE-01's frozen endpoint, recomputed identically on this core (conformance only)."""
        out = []
        for f, lr in self.lin_rec.items():
            if lr["removed"] is not None and lr["alive_at_check"] is True and lr["births"] >= 1 and (lr["peak"] >= MIN_POP or lr["max_gen"] >= MIN_GEN):
                out.append(lr["arrival"])
        return sorted(out)


def tape_sha(t: bytes) -> str:
    return hashlib.sha256(t).hexdigest()[:16]
