"""The engine: one arena, several physics, no hidden reproduction operator.

ONE ARENA FOR EVERY WORLD. Organisms live in fixed slots of a shared byte arena, and the
worlds differ only in (a) which slots an ALLOC may return, (b) who may interact with
whom, (c) whether execution happens on a private slot or on a shared pair tape. That is
deliberate: when the same code runs every world, a difference between worlds is a
difference in physics rather than in two authors' simulators.

WHO CAUSES A DESCENDANT. In every ENDOGENOUS treatment the only path to a child is the
organism executing ALLOC (ask for a slot), writing bytes there itself, and executing
BIRTH (declare it). The world's bookkeeping is one pair of integers - which slot did I
hand you - and it never copies a byte on the organism's behalf. `births_external` counts
any birth the runner caused; in an endogenous treatment anticheat flags a single one as
critical, because that is the failure that would quietly void the campaign.

TIME. Registers, flags and the program counter persist across time slices, so an organism
is a continuously running process, not a function call. That also makes 'persistent
internal state' an observable rather than an assumption.

COST. Validation is cached by genome and run with world ops disabled in a scratch arena,
so scoring can neither reproduce nor touch the soup.

Computational scope: integer programs on a bounded virtual machine. Nothing in this file
models any biological system.
"""
from __future__ import annotations

import hashlib
import random
import zlib

import anticheat
import grammar as G
import tasks
import z8

REP_LEN = {"Z8_64": 64, "Z8_32": 32, "Z8_SHARED": 96, "Z8_SEPARATED": 96, "Z8_SLOTTED": 64}
MUT_RATE = {"LOW": 0.002, "MID": 0.01, "HIGH": 0.04}
CROSS_THRESH = 0.90          # held-out competence that counts as crossing the task
MIN_LEN, SLOT_FACTOR = 8, 2


def _pow2(n):
    k = 1
    while k < n:
        k <<= 1
    return k


class Org:
    __slots__ = ("oid", "slot", "length", "pc", "regs", "fz", "fc", "energy", "age",
                 "anc", "pid", "born", "comp", "held", "probe", "niche", "alive",
                 "fidelity", "repro_span", "births", "ops", "last_tel")

    def __init__(self, oid, slot, length, anc, pid=None, born=0, niche=0):
        self.oid = oid
        self.slot = slot
        self.length = length
        self.pc = slot
        self.regs = None
        self.fz = 0
        self.fc = 0
        self.energy = 0.0
        self.age = 0
        self.anc = anc
        self.pid = pid
        self.born = born
        self.comp = 0.0
        self.held = 0.0
        self.probe = -1
        self.niche = niche
        self.alive = True
        self.fidelity = None
        self.repro_span = None
        self.births = 0
        self.ops = 0
        self.last_tel = None


class Runner:
    """One experiment: a cell of the frozen grammar, a seed, and a compute tier."""

    def __init__(self, cell, seed, tier=None, max_epochs=None, observer=None, invaders=0):
        self.cell = cell
        self.invaders = invaders
        self.d = G.derived(cell)
        self.seed = seed
        self.rng = random.Random((seed * 1000003) ^ zlib.crc32(G.cell_id(cell).encode()))
        self.tier_name = tier or cell.get("tier", "S")
        t = dict(G.TIERS[self.tier_name])
        if max_epochs:
            t["epochs"] = min(t["epochs"], max_epochs)
        self.t = t
        self.observer = observer

        self.L = REP_LEN[cell["representation"]]
        self.slot_size = self.L * SLOT_FACTOR
        self.pop_cap = t["pop"]
        self.n_slots = self.pop_cap * 2
        self.arena_size = _pow2(self.n_slots * self.slot_size)
        self.mem = bytearray(self.arena_size)
        # BYTE OFFSETS, not slot indices. Everything downstream - _place, _kill,
        # _alloc_allowed_slots, slot_owner, Org.slot, Org.pc - addresses the arena
        # directly, so holding indices here placed all 256 organisms on top of each other
        # in the first 256 bytes and every genome read back as zeros.
        self.free_slots = [i * self.slot_size for i in range(self.n_slots)]
        self.rng.shuffle(self.free_slots)
        self.slot_owner = {}

        self.mut_rate = MUT_RATE[cell["mutation_rate"]]
        self.copy_mut = self.mut_rate
        self.spec = self._task_spec()
        self.n_niches = 4 if cell["structure"].startswith("NICHES") or cell["structure"] in ("RESERVOIR", "COMPETENCE_MIG", "ENV_MIG") else 1
        self.grid_w = max(4, int(self.pop_cap ** 0.5))
        self.graph_adj = self._build_graph() if cell["world"] == "GRAPH" else None

        self.next_oid = 0
        self.orgs = []
        self.val_cache = {}
        self.series = []
        self.lineage = []
        self.specimens = []
        self.flags_seen = {}
        self.novel_archive = []
        self.qd_map = {}
        self.env_pop = None
        self.epoch = 0
        self.pending = {}          # oid -> (slot, size) handed out by ALLOC

        self.ct = {"births_endogenous": 0, "births_external": 0, "births_no_copy": 0,
                   "replication_events": 0, "births_similar_no_write": 0,
                   "births_no_copy_live": 0, "deaths": 0, "reaped": 0, "alloc_calls": 0,
                   "alloc_fails": 0, "writes_blocked": 0, "writes_other": 0,
                   "validation_writes": 0, "validation_world_ops": 0, "copy_bytes": 0,
                   "nonheritable_state_inherited": 0, "migrations": 0, "predations": 0,
                   "budget_exhausted": 0, "slices": 0, "ops": 0}
        self.first_cross = None
        self.first_replicator = None
        # FORENSIC TELEMETRY (2026-09-23). An observer object set by the replay harness
        # after construction; None in every non-forensic use. Every hook below is guarded
        # by it and none reads or advances self.rng, so a replay is the original run.
        self.fx = None

    def _build_graph(self, m=2):
        """A degree-heterogeneous interaction graph (preferential attachment) over the
        slots: the GraphWorld-like structure, where who can reach whom is not uniform."""
        n = self.n_slots
        adj = [set() for _ in range(n)]
        targets = [0, 1]
        adj[1].add(0)
        adj[0].add(1)
        for v in range(2, n):
            chosen = set()
            while len(chosen) < min(m, len(targets)):
                chosen.add(targets[self.rng.randrange(len(targets))])
            for u in chosen:
                adj[v].add(u)
                adj[u].add(v)
                targets.append(u)
            targets.append(v)
        return [sorted(a) for a in adj]

    # ------------------------------------------------------------------ task
    def _task_spec(self):
        return tasks.spec_from_cell(self.cell, n_episodes=self.t["val_episodes"], budget=140)

    def _ops_mask(self):
        c = self.cell
        m = 0
        if c["reproduction"] in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE"):
            m |= 0x01
        if c["reproduction"] == "ENDOGENOUS_PARTIAL":
            m |= 0x10
        if c["self_location"] == "PRIMITIVE":
            m |= 0x02
        if c["self_location"] == "PC_RELATIVE":
            m |= 0x04
        m |= 0x08                                  # SENSE always available
        if c["copy_primitive"] == "BLOCK":
            m |= 0x20
        return m

    def _policy(self):
        r = self.cell["reproduction"]
        if r == "OVERWRITE" or r == "PAIR_EXECUTION":
            return z8.ARENA
        if r in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE"):
            return z8.FREE
        return z8.OWN

    # ------------------------------------------------------------------ population
    def _genome(self, org):
        return bytes(self.mem[org.slot:org.slot + org.length])

    def _seed_genome(self):
        c = self.cell
        if c["seeding"] == "RANDOM":
            return bytes(self.rng.randrange(256) for _ in range(self.L))
        if c["seeding"] == "SEEDED_PLATEAU":
            g = tasks.plateau(self.spec)
        elif c["seeding"] == "SEEDED_READER":
            g = tasks.reader_ancestor(self.spec)
        else:
            g = self._replicator_bytes()
        return self._pad(g)

    def _pad(self, g):
        """Pad a hand-written program to the representation length with RANDOM bytes.

        A zero tail would be a NOP sled, and a NOP sled quietly changes what a frame shift
        does - the very thing the structural-mutation factor is supposed to measure.
        """
        g = bytes(g)
        if len(g) < self.L:
            g = g + bytes(self.rng.randrange(256) for _ in range(self.L - len(g)))
        return g[:self.slot_size]

    def _replicator_bytes(self):
        """The seeded replicator, matched to what the world actually grants."""
        c = self.cell
        if c["self_location"] == "PRIMITIVE" and c["copy_primitive"] == "BLOCK":
            src = "SELF\nALLOC\nJRZ go\nHALT\ngo:\nLDIR\nSELF\nBIRTH\nHALT"
        elif c["self_location"] == "PRIMITIVE":
            src = ("SELF\nALLOC\nJRZ go\nHALT\ngo:\nSELF\nloop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\n"
                   "DEC BC\nLD A,B\nOR C\nJRNZ loop\nSELF\nBIRTH\nHALT")
        elif c["self_location"] == "PC_RELATIVE":
            # GETPC sits at offset 0, so it returns the organism's own base: the bounds
            # are COMPUTED rather than granted, which is the point of this level.
            src = ("GETPC\nLD BC,%d\nALLOC\nJRZ go\nHALT\ngo:\n%s\nLD BC,%d\nBIRTH\nHALT"
                   % (self.L, "LDIR" if c["copy_primitive"] == "BLOCK" else
                      "loop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\nDEC BC\nLD A,B\nOR C\nJRNZ loop",
                      self.L))
        else:
            # self_location NONE: nothing reports where you are, so a hand-written
            # replicator has to hardcode an address - and that address is wrong the
            # moment the organism is placed anywhere else. No general replicator exists
            # at this level, which is a property of the factor and is recorded as one
            # (the grammar forbids pairing NONE with a SEEDED_REPLICATOR for exactly
            # this reason; a seed that cannot replicate would be a mislabelled seed).
            src = ("LD HL,0\nLD BC,%d\nALLOC\nJRZ go\nHALT\ngo:\n%s\nLD BC,%d\nBIRTH\nHALT"
                   % (self.L, "LDIR" if c["copy_primitive"] == "BLOCK" else
                      "loop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\nDEC BC\nLD A,B\nOR C\nJRNZ loop",
                      self.L))
        code, _ = z8.asm(src)
        return code

    def _place(self, genome, anc, pid=None, niche=0):
        if not self.free_slots:
            if not self._reap(1):
                return None
        slot = self.free_slots.pop()
        n = min(len(genome), self.slot_size)
        self.mem[slot:slot + self.slot_size] = bytes(self.slot_size)
        self.mem[slot:slot + n] = genome[:n]
        o = Org(self.next_oid, slot, n, anc, pid, self.epoch, niche)
        self.next_oid += 1
        self.slot_owner[slot] = o.oid
        self.orgs.append(o)
        return o

    def _kill(self, o, why="reaped"):
        if not o.alive:
            return
        if self.fx is not None:
            self.fx.death(self, o, why)
        o.alive = False
        self.ct["deaths"] += 1
        if why == "reaped":
            self.ct["reaped"] += 1
        self.free_slots.append(o.slot)
        self.slot_owner.pop(o.slot, None)
        self.pending.pop(o.oid, None)

    def _reap(self, n=1):
        alive = [o for o in self.orgs if o.alive]
        if len(alive) <= 2:
            return False
        if self.cell["pressure"] in ("RESOURCE_GATED", "METABOLIC", "COMPETITION"):
            alive.sort(key=lambda o: o.energy)
        elif self.cell["pressure"] == "QUALITY_DIVERSITY":
            alive.sort(key=lambda o: (self._qd_protected(o), o.age * -1))
        else:
            alive.sort(key=lambda o: -o.age)          # oldest first
        for o in alive[:n]:
            self._kill(o)
        return True

    def _qd_protected(self, o):
        key = (int(o.comp * 4), min(int((o.repro_span or 0) / 16), 4))
        best = self.qd_map.get(key)
        return 1 if (best is not None and best[0] == o.oid) else 0

    # ------------------------------------------------------------------ mutation
    def _boundaries(self, g):
        return [a for a, _ in z8.dis(g)]

    def _mutate(self, g):
        """Mutation, with the numeric/categorical distinction the whole campaign rests on.

        An OPCODE is categorical: mutating one yields a uniformly random byte. An OPERAND
        is a number, so it is perturbed the way cycle 8's grammar perturbs one - most of
        the time by a small signed delta or a single bit flip, and only rarely replaced
        outright. This is not a detail. If operand mutation were uniform, then from 0x00
        the byte 0x01 and the byte 0x5A would both be 1/256 away, and ATOMIC versus
        INCREMENTAL constants - the campaign's central accessibility factor - would be
        measuring nothing at all. With a gradient, 0x01 is one delta or one bit flip away
        while 0x5A is four bit flips away with no fitness signal in between, which is the
        distance cycle 8 actually found and could not cross.
        """
        c = self.cell
        rate = self.mut_rate
        if self.fx is not None:
            self.fx.ct["mutate_calls"] += 1
        g = bytearray(g)
        if c["atlas_axis"] == "RECOMBINATION":
            g = bytearray(self._recombine(bytes(g)))
        opcodes = set(self._boundaries(bytes(g)))

        def perturb(i, is_op):
            if is_op:
                g[i] = self.rng.randrange(256)
                return
            u = self.rng.random()
            if u < 0.45:
                g[i] = (g[i] + self.rng.randint(-8, 8)) & 0xFF
            elif u < 0.90:
                g[i] ^= 1 << self.rng.randrange(8)
            else:
                g[i] = self.rng.randrange(256)

        if c["representation"] == "Z8_SLOTTED":
            # 4-byte slotted layout: slot-aligned edits only, never an insertion or a
            # deletion, so the reading frame cannot shift.
            for s in range(max(1, len(g) // 4)):
                if self.rng.random() >= rate * 4:
                    continue
                i = s * 4
                if c["mutation_operator"] == "OPERAND":
                    j = i + 1 + self.rng.randrange(3)
                elif c["mutation_operator"] == "OPCODE":
                    j = i
                else:
                    j = i + self.rng.randrange(4)
                if j < len(g):
                    perturb(j, j in opcodes)
            return bytes(g)

        for i in range(len(g)):
            if i >= len(g):                                   # a deletion shrank it under us
                break
            if self.rng.random() >= rate:
                continue
            is_op = i in opcodes
            if c["mutation_operator"] == "OPCODE" and not is_op:
                continue
            if c["mutation_operator"] == "OPERAND" and is_op:
                continue
            if c["mutation_locality"] == "STRUCTURAL" and self.rng.random() < 0.5:
                if self.rng.random() < 0.5 and len(g) > MIN_LEN:
                    del g[i]                                  # deletion: the frame shifts
                elif len(g) < self.slot_size:
                    g.insert(i, self.rng.randrange(256))      # insertion: the frame shifts
            else:
                perturb(i, is_op)
        return bytes(g[:self.slot_size])

    def _recombine(self, g, rate=0.2):
        """One-point splice with a random living organism (the RECOMBINATION axis).

        Which parent's bytes dominate the child is measured, not assumed: the record
        keeps the donated span so 'dominance of the contributed span' is readable.
        """
        if self.rng.random() >= rate:
            return g
        alive = [o for o in self.orgs if o.alive]
        if len(alive) < 2:
            return g
        mate = self._genome(alive[self.rng.randrange(len(alive))])
        if not mate:
            return g
        cut = self.rng.randrange(1, max(2, min(len(g), len(mate))))
        self.ct.setdefault("recombinations", 0)
        self.ct["recombinations"] += 1
        return g[:cut] + mate[cut:]

    # ------------------------------------------------------------------ validation
    def _competence(self, g):
        if self.spec.neutral:
            return {"comp": 0.0, "held": 0.0, "reads_at_answer": -1, "answered": 0.0,
                    "halted": 0.0, "ops": 0.0, "neutral": True}
        h = hashlib.blake2b(g, digest_size=8).digest()
        hit = self.val_cache.get(h)
        if hit is not None:
            return hit
        r = tasks.competence(g, self.spec, seed=(self.seed * 7919 + self.epoch),
                             held_seed=(self.seed * 7919 + self.epoch + 500000))
        if len(self.val_cache) > 20000:
            self.val_cache.clear()
        self.val_cache[h] = r
        return r

    # ------------------------------------------------------------------ world ops
    def _alloc_allowed_slots(self, o):
        w = self.cell["world"]
        if w == "GRID":
            cells = self.grid_w
            idx = o.slot // self.slot_size
            x, y = idx % cells, idx // cells
            cand = [((x + dx) % cells) + (((y + dy) % cells) * cells)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            return [c * self.slot_size for c in cand if c < self.n_slots]
        if w == "GRAPH":
            idx = o.slot // self.slot_size
            return [n * self.slot_size for n in self.graph_adj[idx % len(self.graph_adj)]
                    if n < self.n_slots]
        return None                                   # soup: anywhere free

    def _on_alloc(self, o, ctx, want):
        self.ct["alloc_calls"] += 1
        if self.fx is not None:
            self.fx.alloc_attempt(self, o)
        prev = self.pending.pop(o.oid, None)
        if prev is not None:
            # ONE pending daughter cell at a time: a second ALLOC releases the first.
            # Without this an organism holds a slot it never births, and a soup of random
            # programs - which hit the two ALLOC bytes by chance often enough - quietly
            # consumes every free slot. The symptom reads as 'endogenous reproduction does
            # not invade'; the cause is an allocator leak. That is precisely the kind of
            # physics bug a headline metric would have hidden.
            self.free_slots.append(prev[0])
            self.slot_owner.pop(prev[0], None)
        if want <= 0 or want > self.slot_size:
            want = self.slot_size
        # competence gating acts HERE: on the opportunity to reproduce, never on copying
        if self.cell["pressure"] == "TASK_GATED_INTERACTION" and self.d["has_task"]:
            if self.rng.random() > 0.15 + 0.85 * o.comp:
                self.ct["alloc_fails"] += 1
                return None
        if self.cell["pressure"] == "MINIMAL_CRITERION" and self.d["has_task"] and o.comp < 0.35:
            self.ct["alloc_fails"] += 1
            return None
        local = self._alloc_allowed_slots(o)
        slot = None
        if local is not None:
            free = [s for s in local if s in self.free_slots]
            if free:
                slot = free[self.rng.randrange(len(free))]
                self.free_slots.remove(slot)
            elif self.cell["reproduction"] in ("OVERWRITE", "ENDOGENOUS_PARTIAL"):
                victim_slot = local[self.rng.randrange(len(local))]
                vid = self.slot_owner.get(victim_slot)
                if vid is not None:
                    v = next((x for x in self.orgs if x.oid == vid and x.alive), None)
                    if v is not None and v.oid != o.oid:
                        self._kill(v, "overwritten")
                        if victim_slot in self.free_slots:
                            self.free_slots.remove(victim_slot)
                        slot = victim_slot
        else:
            if not self.free_slots:
                if self.cell["reproduction"] == "CONSTRUCTIVE":
                    self.ct["alloc_fails"] += 1
                    return None                      # constructive: free substrate only
                self._reap(1)
            if self.free_slots:
                slot = self.free_slots.pop()
        if slot is None:
            self.ct["alloc_fails"] += 1
            return None
        # Snapshot what the slot HELD when it was handed over, so a birth can be
        # attributed to bytes this organism actually placed rather than to whatever was
        # lying there. The pre-image is kept, not a counter: see _on_birth.
        self.pending[o.oid] = (slot, want, bytes(self.mem[slot:slot + self.slot_size]))
        ctx.free_lo, ctx.free_hi = slot, slot + self.slot_size
        if self.fx is not None:
            self.fx.alloc_ok(self, o, slot)
        return slot

    def _on_birth(self, o, ctx, dst, cnt, partial):
        p = self.pending.get(o.oid)
        if p is None:
            return False
        slot, size, pre = p
        n = max(MIN_LEN, min(cnt if partial else size, self.slot_size))
        child_bytes = bytes(self.mem[slot:slot + n])
        parent = self._genome(o)
        # Bytes this organism actually PLACED, measured against the slot's pre-image.
        # Counter deltas cannot do this job: a bytewise copy loop takes about seven
        # instructions per byte and therefore spans several time slices, and each slice
        # runs in a fresh context whose counters start at zero - so the delta reported
        # only the final slice's writes and a working replicator read as 'born without
        # copying'. Comparing against the pre-image is slice independent, and it makes
        # residue heredity visible for free: if the slot already held these bytes, the
        # organism placed nothing, however much its child resembles it.
        wrote_bytes = sum(1 for i in range(n) if child_bytes[i] != pre[i])
        wrote = wrote_bytes > 0
        if not wrote:
            self.ct["births_no_copy"] += 1
            if set(child_bytes) != {0}:
                self.ct["births_no_copy_live"] += 1
        g = self._mutate(child_bytes)
        if len(g) < MIN_LEN:
            self.pending.pop(o.oid, None)
            self.free_slots.append(slot)
            return False
        self.mem[slot:slot + self.slot_size] = bytes(self.slot_size)
        self.mem[slot:slot + len(g)] = g
        child = Org(self.next_oid, slot, len(g), o.anc, o.oid, self.epoch, o.niche)
        # A child carries its parent's competence as a PROVISIONAL estimate until the next
        # validation pass corrects it. Without this a newborn scores zero to every selector
        # until it happens to be validated, so a beneficial mutant is invisible for several
        # epochs and can be reaped before it is ever seen - which is a property of the
        # measurement schedule, not of the evolutionary process.
        child.comp, child.held, child.probe = o.comp, o.held, o.probe
        self.next_oid += 1
        self.slot_owner[slot] = child.oid
        self.orgs.append(child)
        self.pending.pop(o.oid, None)
        fid = _fidelity(parent, g)
        o.fidelity = fid
        o.repro_span = wrote_bytes or len(g)
        o.births += 1
        self.ct["births_endogenous"] += 1
        self.lineage.append((child.oid, o.oid, self.epoch, o.niche, round(fid, 3), o.repro_span))
        # REPLICATION REQUIRES EVIDENCE OF CAUSATION, NOT RESEMBLANCE. A child may
        # resemble its parent because the population has converged and the slot still
        # holds a dead near-relative's bytes. So a birth counts as replication only if
        # this organism placed at least half the child's bytes itself.
        is_repl = fid >= 0.90 and wrote_bytes >= 0.5 * len(g)
        if fid >= 0.90 and not is_repl:
            self.ct["births_similar_no_write"] += 1
        if is_repl:
            self.ct["replication_events"] += 1
        if self.first_replicator is None and is_repl:
            self.first_replicator = {"epoch": self.epoch, "oid": o.oid, "fidelity": round(fid, 3),
                                     "genome": parent.hex(), "repro_span": o.repro_span,
                                     "seeded": self.d["seeded_instrument"], "slot": o.slot,
                                     "base_is_zero": o.slot == 0}
        if self.fx is not None:
            self.fx.birth_ok(self, o, child, fid, wrote_bytes, is_repl, partial)
        return True

    # ------------------------------------------------------------------ execution
    def _slice_len(self, o):
        s = self.t["slice"]
        if self.cell["pressure"] == "EXEC_TIME_COST":
            s = int(s * self.L / max(o.length, MIN_LEN))
        if self.cell["pressure"] in ("RESOURCE_GATED", "METABOLIC", "COMPETITION"):
            s = int(min(s, max(0.0, o.energy)))
        return max(0, s)

    def _execute(self, o):
        budget = self._slice_len(o)
        if budget <= 0:
            return
        ctx = z8.Ctx(self.mem, o.slot, o.length, policy=self._policy(), rng=self.rng,
                     copy_mut_rate=self.copy_mut, sense=len(self.free_slots) & 0xFF)
        ctx.regs, ctx.fz, ctx.fc = o.regs, o.fz, o.fc
        # An allocated daughter cell stays writable for as long as it is allocated. The
        # write window lives on the context, and a context lasts one time slice, so
        # without this the world handed out a slot and then revoked access at the next
        # tick: a bytewise copy loop - about seven instructions per byte, so three slices
        # for a 64-byte genome - wrote the first thirty bytes and had the rest blocked.
        # Block copy passed the same control only because LDIR finishes inside one slice.
        p = self.pending.get(o.oid)
        if p is not None:
            ctx.free_lo, ctx.free_hi = p[0], p[0] + self.slot_size
        ctx.on_alloc = lambda c, w, _o=o: self._on_alloc(_o, c, w)
        ctx.on_birth = lambda c, d, n, p, _o=o: self._on_birth(_o, c, d, n, p)
        if self.fx is not None:
            self.fx.attach(self, ctx, o)
        pc = o.pc if o.slot <= o.pc < o.slot + self.slot_size else o.slot
        npc = z8.run(ctx, pc, budget, ops_enabled=self._ops_mask())
        o.pc = o.slot if ctx.halted else npc
        o.regs, o.fz, o.fc = ctx.regs, ctx.fz, ctx.fc
        o.ops += ctx.ops
        o.last_tel = ctx.telemetry()
        self.ct["ops"] += ctx.ops
        self.ct["slices"] += 1
        self.ct["writes_blocked"] += ctx.writes_blocked
        self.ct["writes_other"] += ctx.writes_other
        self.ct["copy_bytes"] += ctx.copy_bytes
        self.ct["budget_exhausted"] += 1 if ctx.budget_exhausted else 0
        if self.cell["pressure"] in ("RESOURCE_GATED", "METABOLIC", "COMPETITION"):
            o.energy -= ctx.ops

    # ------------------------------------------------------------------ pair tape
    def _pair_epoch(self):
        alive = [o for o in self.orgs if o.alive]
        self.rng.shuffle(alive)
        for i in range(0, len(alive) - 1, 2):
            a, b = alive[i], alive[i + 1]
            if self.cell["pressure"] == "TASK_GATED_INTERACTION" and self.d["has_task"]:
                if self.rng.random() > 0.15 + 0.85 * max(a.comp, b.comp):
                    continue
            if self.cell["pressure"] == "MINIMAL_CRITERION" and self.d["has_task"] \
                    and min(a.comp, b.comp) < 0.35:
                continue
            ga, gb = self._genome(a), self._genome(b)
            n = self.L
            tape = bytearray(_pow2(2 * n))
            tape[0:len(ga)] = ga
            tape[n:n + len(gb)] = gb
            ctxs = {}
            fxp = self.fx is not None and self.fx.p11
            if fxp:
                st0 = ((None if a.regs is None else list(a.regs), a.fz, a.fc),
                       (None if b.regs is None else list(b.regs), b.fz, b.fc))
                prov, lit = bytearray(len(tape)), bytearray(len(tape))
            for who, start, org in ((0, 0, a), (1, n, b)):
                ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=self.rng,
                             copy_mut_rate=self.copy_mut, sense=who)
                ctx.regs, ctx.fz, ctx.fc = org.regs, org.fz, org.fc
                if fxp:
                    ctx.prov, ctx.prov_lit, ctx.who = prov, lit, who + 1
                z8.run(ctx, start, self.t["slice"], ops_enabled=self._ops_mask())
                org.regs, org.fz, org.fc = ctx.regs, ctx.fz, ctx.fc
                org.ops += ctx.ops
                org.last_tel = ctx.telemetry()
                ctxs[id(org)] = ctx          # keyed by identity: oid is reassigned below
                self.ct["ops"] += ctx.ops
                self.ct["slices"] += 1
                self.ct["copy_bytes"] += ctx.copy_bytes
            na, nb = bytes(tape[0:n]), bytes(tape[n:2 * n])
            # Heredity, if any, is whatever is on the tape when the dust settles - but
            # "this half is now a copy of the other" must mean the other one WROTE it.
            # Once a pair-tape population converges, any two halves resemble each other,
            # so a similarity test alone reports replication continuously and reports it
            # loudest exactly where nothing is happening.
            for org, old, new in ((a, ga, na), (b, gb, nb)):
                pre_mut = new
                new = self._mutate(new)
                self.mem[org.slot:org.slot + self.slot_size] = bytes(self.slot_size)
                self.mem[org.slot:org.slot + len(new)] = new
                org.length = len(new)
                fid_self = _fidelity(old, new)
                other = gb if org is a else ga
                donor = b if org is a else a
                fid_other = _fidelity(other, new)
                donor_wrote = ctxs[id(donor)].writes_other
                if fid_other >= 0.90 and fid_self < 0.90 and donor_wrote >= 0.25 * n:
                    if fxp:
                        self.fx.pair_event(self, i=i, a=a, b=b, victim=org, st0=st0, ga=ga,
                                           gb=gb, final_half=pre_mut, prov=prov, lit=lit,
                                           n=n, tape_len=len(tape), fid_other=fid_other,
                                           fid_self=fid_self, donor_wrote=donor_wrote,
                                           child_oid=self.next_oid,
                                           parent_oid=(b if org is a else a).oid)
                    # this half was overwritten by (a copy of) the other organism
                    self.ct["replication_events"] += 1
                    self.ct["births_endogenous"] += 1
                    src = b if org is a else a
                    src.births += 1
                    src.fidelity = fid_other
                    src.repro_span = n
                    self.lineage.append((self.next_oid, src.oid, self.epoch, org.niche,
                                         round(fid_other, 3), n))
                    org.pid, org.anc, org.oid = src.oid, src.anc, self.next_oid
                    self.next_oid += 1
                    if self.first_replicator is None:
                        self.first_replicator = {"epoch": self.epoch, "oid": src.oid,
                                                 "fidelity": round(fid_other, 3),
                                                 "genome": other.hex(), "repro_span": n,
                                                 "donor_writes_other": donor_wrote,
                                                 "seeded": self.d["seeded_instrument"],
                                                 "slot": src.slot, "base_is_zero": src.slot == 0}
                elif fid_other >= 0.90 and fid_self < 0.90:
                    self.ct["births_similar_no_write"] += 1

    # ------------------------------------------------------------------ external control
    def _external_births(self):
        """The matched exogenous control: the population manager copies, as ordinary
        evolutionary runs do. Counted separately so no reading can confuse the two."""
        alive = [o for o in self.orgs if o.alive]
        if len(alive) < 2:
            return
        n_births = max(1, int(0.05 * len(alive)))
        for _ in range(n_births):
            if self.cell["pressure"] in ("EXPLICIT_FITNESS", "TASK_GATED_INTERACTION",
                                         "RESOURCE_GATED", "MINIMAL_CRITERION",
                                         "QUALITY_DIVERSITY", "COMPETITION") and self.d["has_task"]:
                cand = [alive[self.rng.randrange(len(alive))] for _ in range(3)]
                parent = max(cand, key=lambda o: o.comp)
            elif self.cell["pressure"] == "NOVELTY":
                cand = [alive[self.rng.randrange(len(alive))] for _ in range(3)]
                parent = max(cand, key=lambda o: self._novelty(o))
            else:
                parent = alive[self.rng.randrange(len(alive))]
            g = self._mutate(self._genome(parent))
            if not self.free_slots:
                self._reap(1)
            child = self._place(g, parent.anc, parent.oid, parent.niche)
            if child is None:
                return
            child.comp, child.held, child.probe = parent.comp, parent.held, parent.probe
            child.energy = parent.energy * 0.5
            self.ct["births_external"] += 1
            self.lineage.append((child.oid, parent.oid, self.epoch, parent.niche,
                                 round(_fidelity(self._genome(parent), g), 3), None))

    # ------------------------------------------------------------------ pressure / ecology
    def _novelty(self, o):
        v = o.last_tel or {}
        vec = (v.get("writes", 0), v.get("copy_bytes", 0), v.get("out_writes", 0),
               v.get("in_reads", 0), o.length)
        if not self.novel_archive:
            return 1.0
        d = min(sum(abs(a - b) for a, b in zip(vec, u)) for u in self.novel_archive[-50:])
        return d / (1.0 + d)

    def _pressure_epoch(self):
        c = self.cell
        alive = [o for o in self.orgs if o.alive]
        if c["pressure"] in ("RESOURCE_GATED", "METABOLIC", "COMPETITION"):
            pool = self.t["slice"] * len(alive) * 1.05
            if c["pressure"] == "METABOLIC":
                for o in alive:
                    o.energy = min(o.energy + self.t["slice"] * 1.05, self.t["slice"] * 3)
            else:
                tot = sum((o.comp if self.d["has_task"] else 1.0) + 0.05 for o in alive) or 1.0
                for o in alive:
                    share = ((o.comp if self.d["has_task"] else 1.0) + 0.05) / tot
                    o.energy = min(o.energy + pool * share, self.t["slice"] * 3)
            for o in alive:
                if o.energy <= 0 and o.age > 2:
                    self._kill(o, "starved")
        if c["pressure"] == "TAPE_COST":
            for o in alive:
                if self.rng.random() < 0.002 * o.length:
                    self._kill(o, "tape_cost")
        if c["pressure"] == "PREDATION" and self.d["has_task"]:
            for o in alive:
                if o.comp < 0.5:
                    continue
                nb = self._alloc_allowed_slots(o)
                pool_slots = nb if nb is not None else [x.slot for x in alive[:16]]
                for s in pool_slots:
                    vid = self.slot_owner.get(s)
                    v = next((x for x in self.orgs if x.oid == vid and x.alive), None) if vid is not None else None
                    if v is not None and v.oid != o.oid and v.comp < o.comp - 0.3 and self.rng.random() < 0.15:
                        self._kill(v, "predated")
                        self.ct["predations"] += 1
                        o.energy += 50
                        break
        if c["pressure"] == "NOVELTY":
            for o in alive[:32]:
                v = o.last_tel or {}
                self.novel_archive.append((v.get("writes", 0), v.get("copy_bytes", 0),
                                           v.get("out_writes", 0), v.get("in_reads", 0), o.length))
            self.novel_archive = self.novel_archive[-500:]
        if c["pressure"] == "QUALITY_DIVERSITY":
            for o in alive:
                key = (int(o.comp * 4), min(int((o.repro_span or 0) / 16), 4))
                best = self.qd_map.get(key)
                if best is None or o.comp > best[1]:
                    self.qd_map[key] = (o.oid, o.comp)

    def _migrate(self):
        s = self.cell["structure"]
        if self.n_niches <= 1 or s in ("WELL_MIXED", "VON_NEUMANN", "NICHES_ISOLATED"):
            return
        rate = {"NICHES_LOW_MIG": 0.005, "NICHES_HIGH_MIG": 0.08, "NICHES_PERIODIC_MIG": 0.0,
                "COMPETENCE_MIG": 0.05, "ENV_MIG": 0.05, "RESERVOIR": 0.02}.get(s, 0.0)
        if s == "NICHES_PERIODIC_MIG":
            rate = 0.25 if (self.epoch % 40 == 0 and self.epoch) else 0.0
        for o in [x for x in self.orgs if x.alive]:
            if self.rng.random() >= rate:
                continue
            if s == "COMPETENCE_MIG" and self.d["has_task"] and o.comp < 0.6:
                continue
            if s == "ENV_MIG" and self.env_difficulty(o.niche) < 0.5:
                continue
            o.niche = self.rng.randrange(self.n_niches)
            self.ct["migrations"] += 1

    def env_difficulty(self, niche):
        if self.cell["structure"] == "RESERVOIR":
            return 0.2 if niche == 0 else 1.0
        return 1.0

    def _niche_spec(self, niche):
        """RESERVOIR gives niche 0 an easy variant: the same task with a forced read and a
        neutral bridge, i.e. the accessibility manipulations made easy rather than a
        different task. That is what makes it a possible genetic reservoir."""
        if self.cell["structure"] == "RESERVOIR" and niche == 0:
            return tasks.TaskSpec(transform=self.spec.transform, read_order="FORCED_READ",
                                  bridge="NEUTRAL_BRIDGE", n_episodes=self.spec.n_episodes,
                                  budget=self.spec.budget, neutral=self.spec.neutral)
        return self.spec

    # ------------------------------------------------------------------ environment
    def _env_epoch(self):
        c = self.cell
        if c["environment"] == "NONSTATIONARY_SHIFT":
            n = self.t["epochs"]
            if self.epoch in (n // 3, 2 * n // 3):
                order = ["XOR1", "ADD1", "XOR15", "XOR5A", "ADD37"]
                cur = order.index(self.spec.transform) if self.spec.transform in order else 0
                self.spec = tasks.TaskSpec(transform=order[(cur + 1) % len(order)],
                                           read_order=self.spec.read_order, bridge=self.spec.bridge,
                                           n_episodes=self.spec.n_episodes, budget=self.spec.budget,
                                           neutral=self.spec.neutral)
                self.val_cache.clear()
        elif c["environment"] == "COEVO_ENV":
            if self.env_pop is None:
                self.env_pop = [{"transform": self.rng.choice(["XOR1", "ADD1", "XOR15", "XOR5A"]),
                                 "read_order": self.rng.choice(tasks.READ_ORDERS),
                                 "score": 0.0, "age": 0, "id": i} for i in range(self.n_niches)]
            if self.epoch % 25 == 0 and self.epoch:
                for e in self.env_pop:
                    occ = [o for o in self.orgs if o.alive and o.niche == e["id"] % self.n_niches]
                    p = sum(o.comp for o in occ) / len(occ) if occ else 0.0
                    e["score"] = 4 * p * (1 - p)       # peaks where the task is half solved
                    e["age"] += 1
                self.env_pop.sort(key=lambda e: -e["score"])
                worst = self.env_pop[-1]
                best = self.env_pop[0]
                worst["transform"] = best["transform"] if self.rng.random() < 0.5 else \
                    self.rng.choice(["XOR1", "ADD1", "XOR15", "XOR5A"])
                worst["read_order"] = best["read_order"] if self.rng.random() < 0.7 else \
                    self.rng.choice(tasks.READ_ORDERS)
                worst["score"], worst["age"] = 0.0, 0
                self.val_cache.clear()

    def _env_spec_for(self, o):
        if self.cell["environment"] == "COEVO_ENV" and self.env_pop:
            e = self.env_pop[o.niche % len(self.env_pop)]
            return tasks.TaskSpec(transform=e["transform"], read_order=e["read_order"],
                                  bridge=self.spec.bridge, n_episodes=self.spec.n_episodes,
                                  budget=self.spec.budget, neutral=self.spec.neutral)
        return self._niche_spec(o.niche)

    # ------------------------------------------------------------------ the epoch
    def _validate(self, force=False):
        every = self.t["val_every"]
        if not force and (self.epoch % every):
            return
        if self.spec.neutral:
            return
        for o in self.orgs:
            if not o.alive:
                continue
            spec_o = self._env_spec_for(o)
            saved, self.spec = self.spec, spec_o
            try:
                r = self._competence(self._genome(o))
            finally:
                self.spec = saved
            o.comp, o.held, o.probe = r["comp"], r["held"], r["reads_at_answer"]
            if self.first_cross is None and o.held >= CROSS_THRESH:
                self.first_cross = {"epoch": self.epoch, "oid": o.oid, "held": o.held,
                                    "comp": o.comp, "genome": self._genome(o).hex(),
                                    "niche": o.niche, "anc": o.anc, "pid": o.pid,
                                    "seeded": self.d["seeded_instrument"],
                                    "reads_at_answer": o.probe}

    def step(self):
        self._env_epoch()
        self._validate()
        self._pressure_epoch()
        if self.cell["world"] == "PAIR_TAPE" and self.cell["reproduction"] == "PAIR_EXECUTION":
            self._pair_epoch()
        else:
            alive = [o for o in self.orgs if o.alive]
            self.rng.shuffle(alive)
            for o in alive:
                if o.alive:
                    self._execute(o)
        if self.cell["reproduction"] == "EXTERNAL":
            self._external_births()
        self._migrate()
        for o in self.orgs:
            if o.alive:
                o.age += 1
        if len(self.orgs) > 4 * self.pop_cap:
            self.orgs = [o for o in self.orgs if o.alive]
        alive_n = sum(1 for o in self.orgs if o.alive)
        while alive_n > self.pop_cap:
            if not self._reap(max(1, alive_n - self.pop_cap)):
                break
            alive_n = sum(1 for o in self.orgs if o.alive)
        self._telemetry()
        if self.fx is not None:
            self.fx.end_epoch(self)
        self.epoch += 1

    def _telemetry(self):
        if self.epoch % max(1, self.t["snap_every"] // 4):
            return
        alive = [o for o in self.orgs if o.alive]
        if not alive:
            self.series.append({"e": self.epoch, "pop": 0})
            return
        gs = [self._genome(o) for o in alive]
        comps = [o.comp for o in alive]
        best = max(alive, key=lambda o: (o.held, o.comp))
        uniq = len({hashlib.blake2b(g, digest_size=6).digest() for g in gs})
        dom = _dominant_share(gs)
        fids = [o.fidelity for o in alive if o.fidelity is not None]
        spans = [o.repro_span for o in alive if o.repro_span]
        self.series.append({
            "e": self.epoch, "pop": len(alive), "births_endo": self.ct["births_endogenous"],
            "births_ext": self.ct["births_external"], "deaths": self.ct["deaths"],
            "comp_mean": round(sum(comps) / len(comps), 4), "comp_max": round(max(comps), 4),
            "held_best": round(best.held, 4), "probe_best": best.probe,
            "len_mean": round(sum(o.length for o in alive) / len(alive), 2),
            "age_mean": round(sum(o.age for o in alive) / len(alive), 2),
            "uniq": uniq, "dom_share": round(dom, 4),
            "fid_mean": round(sum(fids) / len(fids), 4) if fids else None,
            "span_mean": round(sum(spans) / len(spans), 2) if spans else None,
            "entropy": round(_entropy(gs), 4),
            "energy_mean": round(sum(o.energy for o in alive) / len(alive), 1),
        })

    # ------------------------------------------------------------------ run
    def run(self):
        anc = 0
        for i in range(self.pop_cap):
            # invaders are ancestors 0..invaders-1, so their lineage share is readable
            # later without tagging anything the organisms themselves can see
            g = self._pad(self._replicator_bytes()) if i < self.invaders else self._seed_genome()
            o = self._place(g, anc)
            if o is None:
                break
            o.energy = self.t["slice"] * 2
            anc += 1
        self._validate(force=True)
        for _ in range(self.t["epochs"]):
            if not any(o.alive for o in self.orgs):
                break
            self.step()
        self._validate(force=True)
        return self.summary()

    def summary(self):
        alive = [o for o in self.orgs if o.alive]
        gs = [self._genome(o) for o in alive]
        comps = [o.comp for o in alive] or [0.0]
        helds = [o.held for o in alive] or [0.0]
        best = max(alive, key=lambda o: (o.held, o.comp)) if alive else None
        s0 = self.series[0] if self.series else {}
        agg = {
            "pop_final": len(alive), "extinct": len(alive) == 0,
            "epochs_run": self.epoch,
            "births_endogenous": self.ct["births_endogenous"],
            "births_external": self.ct["births_external"],
            "births_no_copy": self.ct["births_no_copy"], "births_no_copy_live": self.ct["births_no_copy_live"],
            "replication_events": self.ct["replication_events"],
            "births_similar_no_write": self.ct["births_similar_no_write"],
            "deaths": self.ct["deaths"], "alloc_calls": self.ct["alloc_calls"],
            "alloc_fails": self.ct["alloc_fails"], "writes_blocked": self.ct["writes_blocked"],
            "writes_other": self.ct["writes_other"], "copy_bytes": self.ct["copy_bytes"],
            "migrations": self.ct["migrations"], "predations": self.ct["predations"],
            "ops": self.ct["ops"], "slices": self.ct["slices"],
            "budget_exhausted_share": round(self.ct["budget_exhausted"] / max(1, self.ct["slices"]), 4),
            "validation_writes": self.ct["validation_writes"],
            "validation_world_ops": self.ct["validation_world_ops"],
            "nonheritable_state_inherited": self.ct["nonheritable_state_inherited"],
            "comp_mean": round(sum(comps) / len(comps), 4), "comp_max": round(max(comps), 4),
            "held_max": round(max(helds), 4),
            "held_of_best": round(best.held, 4) if best else 0.0,
            "reads_at_answer_of_best": best.probe if best else -1,
            "halted_share_of_best": (best.last_tel or {}).get("halted", 0.0) if best else 0.0,
            "max_age_seen": max((o.age for o in self.orgs), default=0),
            "uniq_final": len({hashlib.blake2b(g, digest_size=6).digest() for g in gs}),
            "dom_share_final": round(_dominant_share(gs), 4) if gs else 0.0,
            "entropy_final": round(_entropy(gs), 4) if gs else 0.0,
            "entropy_initial": s0.get("entropy"),
            "len_mean_final": round(sum(o.length for o in alive) / len(alive), 2) if alive else 0.0,
            "fid_mean_final": _mean([o.fidelity for o in alive if o.fidelity is not None]),
            "span_mean_final": _mean([o.repro_span for o in alive if o.repro_span]),
            "lineage_events": len(self.lineage),
            "distinct_ancestors_final": len({o.anc for o in alive}),
            "invaders_seeded": self.invaders,
            "invader_share_final": (round(sum(1 for o in alive if o.anc < self.invaders) / len(alive), 4)
                                    if alive and self.invaders else None),
            "first_cross": self.first_cross, "first_replicator": self.first_replicator,
            "crossed": bool(self.first_cross), "replicated": bool(self.first_replicator),
            "niche_occupancy": _occupancy(alive, self.n_niches),
        }
        agg["replication_rate"] = round(agg["births_endogenous"] / max(1, agg["slices"]), 5)
        agg["entropy_drop"] = (round(agg["entropy_initial"] - agg["entropy_final"], 4)
                               if agg["entropy_initial"] is not None else None)
        flags = anticheat.scan(self.cell, self.d, agg,
                               opts={"policy": self._policy(), "max_age": self.t["epochs"] + 2})
        agg["flags"] = flags
        agg["voided"] = anticheat.voids_run(flags)
        self.specimens = self._collect_specimens(alive)
        return agg

    def _collect_specimens(self, alive):
        out = []
        seen = set()
        ranked = sorted(alive, key=lambda o: (-(o.held), -(o.comp), -(o.births)))[:6]
        for o in ranked + [o for o in alive if o.births > 0][:4]:
            g = self._genome(o)
            h = hashlib.blake2b(g, digest_size=8).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            out.append({"oid": o.oid, "anc": o.anc, "pid": o.pid, "born": o.born, "age": o.age,
                        "len": o.length, "comp": round(o.comp, 4), "held": round(o.held, 4),
                        "probe": o.probe, "births": o.births,
                        "fidelity": o.fidelity, "repro_span": o.repro_span,
                        "genome_hex": g.hex(), "hash": h,
                        "dis": ["%04X %s" % (a - o.slot if a >= o.slot else a, t)
                                for a, t in z8.dis(g)][:48],
                        "telemetry": o.last_tel})
        return out


# ---------------------------------------------------------------- small helpers
def _fidelity(a, b):
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    same = sum(1 for i in range(n) if a[i] == b[i])
    return same / max(len(a), len(b))


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


def _entropy(gs):
    if not gs:
        return 0.0
    counts = [0] * 256
    tot = 0
    for g in gs:
        for b in g:
            counts[b] += 1
            tot += 1
    if not tot:
        return 0.0
    import math
    h = 0.0
    for c in counts:
        if c:
            p = c / tot
            h -= p * math.log(p, 2)
    return h


def _dominant_share(gs):
    if not gs:
        return 0.0
    counts = {}
    for g in gs:
        k = hashlib.blake2b(g, digest_size=6).digest()
        counts[k] = counts.get(k, 0) + 1
    return max(counts.values()) / len(gs)


def _occupancy(alive, n):
    occ = [0] * max(1, n)
    for o in alive:
        occ[o.niche % len(occ)] += 1
    return occ


def run_cell(cell, seed, tier=None, max_epochs=None, invaders=0):
    """The consumer's entry point: a cell in, a record out."""
    r = Runner(cell, seed, tier=tier, max_epochs=max_epochs, invaders=invaders)
    agg = r.run()
    return {"summary": agg, "series": r.series, "specimens": r.specimens,
            "lineage_n": len(r.lineage), "lineage_tail": r.lineage[-400:]}
