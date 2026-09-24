"""Physics v3: the minimal computation -> resource -> reproduction coupling (Bellerophon, 2026-09-24).

One new physical quantity: the COPY RESOURCE R of each organism, a non-negative integer held in the World's ledger
(never in VM memory: no instruction can read or write it). Rules (all explicit, all logged):

  income      every interaction pays BASE units to the acting organism (the non-contingent floor)
  earning     after the interaction's execution has finished, the evaluator checks the organism's FIRST output against
              the task's expected answer for the inputs it was given (ATOMIC exact, under the run's read gate). The
              expected value is computed outside the VM before execution and never enters memory. What is paid depends
              on the declared coupling mode:
                ON             correct -> BONUS to the organism
                OFF            nothing (base income only; copying still charged)
                SHUFFLED       the output is compared with the answer for an independent input the organism never saw
                               (a verifier with the same rule structure but no learnable relationship) -> BONUS
                RANDOM_REWARD  correct -> BONUS to a uniformly random living organism (same total, no individual link)
                YOKED          no individual contingency: tick t's bonus total is the total paid at tick t in the
                               matched ON run (cfg.yoke), divided equally among the living (remainder carried forward)
                IRRELEVANT     first output == 0x5A (an observable unrelated to the configured task) -> BONUS
                DELAYED        correct -> BONUS credited `delay` ticks later if the same organism is still alive
              credit is added AFTER the execution: resource earned in an execution can only be spent in a LATER one.
  spending    CONSTRUCTING an offspring costs COST units per window byte the writer wrote (n_written; a full
              ENDOGENOUS_COPY child needs COST*L). The physics' viability rule is unchanged; a viable construction whose
              writer cannot pay is refused (no child, nothing charged -- unviable window writes were always scratch).
              (Design note: a charge-as-you-write budget was built first and failed its calibration pilot: an organism
              cannot see R, so a copier spent every income on partial copies and never reproduced -- FAILURE_LEDGER F1.)
  cap         R is clamped to CAP; every clamped unit is counted (never silently lost).
  inheritance a newborn starts with R = 0 (resource is not heritable); R dies with its holder (counted).
  ledger      earned_base + earned_bonus == spent + clamped + lost_at_death + lost_overwritten + held_end (asserted).
Coupled physics requires physics == "v3" (v2 physics + this ledger); v1/v2 behaviour is untouched (coupling "NONE").
PAIR_EXECUTION is not supported under coupling (the partner half is not a window): refused at construction."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

MODES = ("OFF", "ON", "SHUFFLED", "RANDOM_REWARD", "YOKED", "IRRELEVANT", "DELAYED")
IRRELEVANT_BYTE = 0x5A


class Ledger:
    def __init__(self, cfg, seed: int):
        if cfg.coupling not in MODES:
            raise ValueError("coupling %r not in %s" % (cfg.coupling, MODES))
        if cfg.physics != "v3":
            raise ValueError("coupled physics requires physics='v3'")
        if cfg.reproduction == "PAIR_EXECUTION":
            raise ValueError("PAIR_EXECUTION is not supported under coupling")
        self.cfg = cfg
        self.mode = cfg.coupling
        self.rng = random.Random(seed * 1000003 + 77)           # the coupling's OWN stream: arms consume the world rng identically
        self.base = int(cfg.base_income); self.bonus = int(cfg.bonus); self.cost = int(cfg.copy_cost); self.cap = int(cfg.resource_cap)
        assert self.base >= 0 and self.bonus >= 0 and self.cost >= 1 and self.cap >= 1
        self.t = {"earned_base": 0, "earned_bonus": 0, "spent": 0, "clamped": 0, "lost_death": 0, "lost_overwritten": 0,
                  "refused_births": 0, "paid_births": 0, "correct_events": 0, "rewarded_events": 0}
        self.tick_bonus = 0; self.tick_base = 0; self.tick_spent = 0; self.tick_correct = 0
        self.schedule: List[int] = []                          # bonus paid per tick (the yoke for a matched YOKED run)
        self.pending: List[tuple] = []                         # DELAYED: (due_tick, org_id, amount)
        self.carry = 0

    # ---- accounting primitives -------------------------------------------------------------------------------------
    def _credit(self, o, amount: int, kind: str) -> None:
        if amount <= 0:
            return
        room = self.cap - o.res
        got = min(room, amount)
        o.res += got
        self.t["clamped"] += amount - got
        self.t["earned_" + kind] += amount
        if kind == "bonus":
            self.tick_bonus += amount
        else:
            self.tick_base += amount

    def can_pay(self, o, n_written: int) -> bool:
        return o.res >= n_written * self.cost

    def refuse(self) -> None:
        self.t["refused_births"] += 1

    def pay_birth(self, o, n_written: int) -> None:
        c = n_written * self.cost
        if c > o.res:
            raise AssertionError("resource underflow: %d > %d" % (c, o.res))
        o.res -= c
        self.t["spent"] += c; self.tick_spent += c; self.t["paid_births"] += 1

    def on_death(self, o, overwritten: bool = False) -> None:
        self.t["lost_overwritten" if overwritten else "lost_death"] += o.res
        o.res = 0

    # ---- the evaluator (runs AFTER the execution; its inputs never enter VM memory) ----------------------------------
    def after_interaction(self, world, o, task, inputs, outputs, first_out_step, first_in_step, correct: bool) -> None:
        self._credit(o, self.base, "base")
        if correct:
            self.t["correct_events"] += 1; self.tick_correct += 1
        m = self.mode
        pay_to = None
        if m == "ON" and correct:
            pay_to = o
        elif m == "SHUFFLED":
            other = task.inputs(self.rng)
            from prometheus.z80atlas.tasks import score
            if score(task, outputs, task.expected(other), "ATOMIC", self.cfg.read_gate, first_out_step, first_in_step) >= 0.999:
                pay_to = o
        elif m == "RANDOM_REWARD" and correct:
            alive = [c for c in world.cells if c is not None]
            pay_to = alive[self.rng.randrange(len(alive))] if alive else None
        elif m == "IRRELEVANT" and outputs and outputs[0] == IRRELEVANT_BYTE:
            pay_to = o
        elif m == "DELAYED" and correct:
            self.pending.append((world.tick + int(self.cfg.delay), o.id, self.bonus))
        if pay_to is not None:
            self.t["rewarded_events"] += 1
            self._credit(pay_to, self.bonus, "bonus")

    def end_tick(self, world) -> dict:
        alive = [c for c in world.cells if c is not None]
        if self.mode == "YOKED":
            yk = self.cfg.yoke
            total = (int(yk[world.tick]) if world.tick < len(yk) else 0) + self.carry
            if alive and total > 0:
                each = total // len(alive); self.carry = total - each * len(alive)
                for c in alive:
                    self._credit(c, each, "bonus")
                if each:
                    self.t["rewarded_events"] += len(alive)
            else:
                self.carry = total
        if self.mode == "DELAYED" and self.pending:
            due = [p for p in self.pending if p[0] <= world.tick]; self.pending = [p for p in self.pending if p[0] > world.tick]
            by_id = {c.id: c for c in alive}
            for _, oid, amt in due:
                if oid in by_id:
                    self.t["rewarded_events"] += 1
                    self._credit(by_id[oid], amt, "bonus")
        rec = {"bonus_paid": self.tick_bonus, "base_paid": self.tick_base, "spent": self.tick_spent, "correct": self.tick_correct,
               "res_held": sum(c.res for c in alive)}
        self.schedule.append(self.tick_bonus)
        self.tick_bonus = self.tick_base = self.tick_spent = self.tick_correct = 0
        return rec

    def close(self, world) -> dict:
        held = sum(c.res for c in world.cells if c is not None)
        t = dict(self.t, held_end=held, undelivered_delayed=sum(p[2] for p in self.pending), yoke_carry=self.carry)
        lhs = t["earned_base"] + t["earned_bonus"]
        rhs = t["spent"] + t["clamped"] + t["lost_death"] + t["lost_overwritten"] + held
        t["balanced"] = lhs == rhs
        if lhs != rhs:
            raise AssertionError("resource ledger does not balance: %d != %d (%s)" % (lhs, rhs, t))
        t["bonus_schedule"] = list(self.schedule)
        return t


# ---- competence (measurement only: never feeds back into the organism) ------------------------------------------------
class Competence:
    """Cached verified competence of a tape on the CONFIGURED task (tasks.verify_tape semantics: the tape alone, empty
    window, every input of the fixed panel exact under the read gate) plus the irrelevant observable (first output
    0x5A). Pure measurement: results are only written to telemetry."""

    def __init__(self, world):
        self.w = world; self.cache: Dict[bytes, tuple] = {}
        self.task = world.configured_task()

    def of(self, tape: bytes) -> tuple:
        r = self.cache.get(tape)
        if r is None:
            from prometheus.z80atlas.tasks import verify_tape, panel
            from prometheus.z80atlas import vm
            cfg = self.w.cfg
            v = verify_tape(tape, self.w.L, self.task, cfg.read_gate, cfg.budget, cfg.layout, cfg.allow_copyall)
            mem = bytearray(256); mem[:self.w.L] = tape
            tr = vm.execute(mem, self.w.L, 0, cfg.budget, [42], allow_copyall=cfg.allow_copyall, ldir=cfg.ldir, undefined=cfg.undefined_op)
            r = (bool(v["exact"]), bool(tr.outputs and tr.outputs[0] == IRRELEVANT_BYTE))
            if len(self.cache) < 200000:
                self.cache[tape] = r
        return r
