"""Campaign 1 reference Players (controls only; DESIGN_C1 s6).

RANDOM_C1, ENUMERATE_C1, ENUMERATE_VM_C1, QUIT_C1 (abstention witness),
TABLE_MEMO_C1 (answer-table witness), PROCEDURE_REUSE_C1 (positive
control: calibration + template blocks with an argument port, planning in
the head, execution by BLK_INVOKE), PROCEDURE_NOCAL_C1 (same, permutation
ignored: the identifier-permutation witness).

Cross-task state lives only in the Workspace / BlockStore handed to run().
"""

from __future__ import annotations

import itertools
import random

from . import vm, world_c1 as w
from .env import TaskOver
from .player import PythonPlayer, VMPlayer

K = w.NUM_ACTIONS
RESET = w.RESET_ACTION
TAG_CAL, TAG_TEMPLATE = 1, 2
KIND_INDEX = {k: i for i, k in enumerate(w.KINDS)}


class RandomC1(PythonPlayer):
    name = "RANDOM_C1"

    def run(self, env, st):
        rng = random.Random("RANDOM_C1:%d:%r:%r" % (env.task_index, env.start, env.target))
        while True:
            env.charge(1)
            env.act(rng.randrange(K))


def enumerate_sequences(env, max_depth=3, observe=None):
    """Iterative deepening over action sequences with RESET. Returns the solving sequence or None."""
    for depth in range(1, max_depth + 1):
        for seq in itertools.product(range(K), repeat=depth):
            env.charge(1)
            env.act(RESET)
            for a in seq:
                before = env.current
                env.act(a)
                if observe is not None:
                    observe(a, before, env.current)
                if env.success:
                    return list(seq)
    return None


class EnumerateC1(PythonPlayer):
    name = "ENUMERATE_C1"

    def run(self, env, st):
        if enumerate_sequences(env) is None:
            env.halt()


class QuitC1(PythonPlayer):
    """Abstention shape: brute force only where it can pay (budget 2000 = depth 1), halt elsewhere."""

    name = "QUIT_C1"

    def run(self, env, st):
        if env.interaction_budget >= 2000:
            enumerate_sequences(env)
        env.halt()


class TableMemoC1(PythonPlayer):
    """Answer table: record id keyed by (start, target) in field 0/1, sequence in field 2."""

    name = "TABLE_MEMO_C1"

    def run(self, env, st):
        ws = st.ws
        key = env.start + env.target
        for rid in list(ws.records):
            env.charge(1)
            if ws.get_field(rid, 0) == key:
                seq = ws.get_field(rid, 2)
                if isinstance(seq, tuple):
                    ws.write(255, (ws.read(255) or 0) + 1)  # replays_hit counter, cell 255
                    env.act(RESET)
                    for a in seq:
                        env.act(a)
                    if env.success:
                        return
        seq = enumerate_sequences(env)
        if seq is not None:
            ws.create_record({0: key, 2: tuple(seq)})
            return
        env.halt()


class ProcedureReuseC1(PythonPlayer):
    """Positive control. State lives ONLY in blocks: a calibration block and one block per template."""

    name = "PROCEDURE_REUSE_C1"
    CALIBRATE = True
    MAX_PLAN_DEPTH = 3

    # ------------------------------------------------ calibration (action id -> primitive)
    @staticmethod
    def classify(before, after):
        diff = [i for i in range(w.L) if before[i] != after[i]]
        if len(diff) == 1:
            p = diff[0]
            d = (after[p] - before[p]) % w.B
            if d == 1:
                return KIND_INDEX["INC"] * w.L + p
            if d == w.B - 1:
                return KIND_INDEX["DEC"] * w.L + p
            return None
        if len(diff) == 2:
            p, q = diff
            if (q - p) % w.L == 1 and after[p] == before[q] and after[q] == before[p]:
                return KIND_INDEX["SWAP"] * w.L + p
            if p == 0 and q == w.L - 1 and after[q] == before[p] and after[p] == before[q]:
                return KIND_INDEX["SWAP"] * w.L + q
        return None

    def _find(self, blocks, tag):
        for bid in blocks.ids():
            if blocks.state_get(bid, 3) == tag:
                return bid
        return -1

    def _ensure_calibration(self, env, st):
        blocks = st.blocks
        cal = self._find(blocks, TAG_CAL)
        if cal < 0:
            cal = blocks.create([], origin="new")
            blocks.state_set(cal, 0, tuple([-1] * K))
            blocks.state_set(cal, 3, TAG_CAL)
        fwd = list(blocks.state_get(cal, 0))
        if not self.CALIBRATE:
            fwd = list(range(K))
        changed = False
        for k in range(K):
            if fwd[k] >= 0:
                continue
            env.charge(1)
            env.act(RESET)
            before = env.current
            env.act(k)
            prim = self.classify(before, env.current)
            if prim is not None:
                fwd[k] = prim
                changed = True
            if env.success:  # a probe happened to solve the task; keep going next task
                break
        if changed or not self.CALIBRATE:
            inv = [-1] * K
            for k, prim in enumerate(fwd):
                if prim >= 0:
                    inv[prim] = k
            blocks.state_set(cal, 0, tuple(fwd))
            blocks.state_set(cal, 1, tuple(inv))
        return cal

    # ------------------------------------------------ template blocks
    @staticmethod
    def template_instructions(kinds, offsets):
        """Bytecode taking the argument in R0 and emitting the template's actions through the LIVE
        inverse map of the calibration block, whose id is in this block's state[2]."""
        ins = [
            (vm.OP["INPUT"], 7, vm.INPUT_FIELDS.index("current_block"), 0),
            (vm.OP["CONST"], 6, 2, 0),
            (vm.OP["BLK_STATE_GET"], 7, 7, 6),   # R7 = calibration block id
            (vm.OP["CONST"], 6, 1, 0),
            (vm.OP["BLK_STATE_GET"], 4, 7, 6),   # R4 = inverse map (primitive index -> action id)
            (vm.OP["CONST"], 5, w.L, 0),
        ]
        for kind, off in zip(kinds, offsets):
            ins += [
                (vm.OP["CONST"], 3, off, 0),
                (vm.OP["ADD"], 3, 0, 3),
                (vm.OP["MOD"], 3, 3, 5),
                (vm.OP["CONST"], 2, kind * w.L, 0),
                (vm.OP["ADD"], 2, 2, 3),
                (vm.OP["VGET"], 3, 4, 2),
                (vm.OP["ACT"], 3, 0, 0),
            ]
        return ins

    def _templates(self, blocks):
        out = []
        for bid in blocks.ids():
            if blocks.state_get(bid, 3) == TAG_TEMPLATE:
                kinds, offs = blocks.state_get(bid, 0), blocks.state_get(bid, 1)
                if isinstance(kinds, tuple) and isinstance(offs, tuple) and len(kinds) == len(offs):
                    out.append((bid, kinds, offs))
        return out

    MAX_WITNESSES = 24

    def _witnesses(self, blocks, cal):
        v = blocks.state_get(cal, 4)
        if not isinstance(v, tuple):
            return []
        n = 2 * w.L
        return [(v[i:i + w.L], v[i + w.L:i + n]) for i in range(0, len(v) - n + 1, n)]

    def _add_witness(self, env, blocks, cal):
        ws_ = self._witnesses(blocks, cal)
        pair = (tuple(env.start), tuple(env.target))
        if pair in ws_:
            return
        ws_ = (ws_ + [pair])[-self.MAX_WITNESSES:]
        flat = tuple(x for s, t in ws_ for x in (s + t))
        blocks.state_set(cal, 4, flat)

    @staticmethod
    def _explains(kinds, offs, start, target):
        return any(ProcedureReuseC1._apply_mental(kinds, offs, a, start) == target for a in range(w.L))

    def _record_template(self, env, st, cal, seq):
        blocks = st.blocks
        fwd = blocks.state_get(cal, 0)
        prims = [fwd[a] for a in seq]
        if any(p < 0 for p in prims):
            return
        kinds = tuple(p // w.L for p in prims)
        poss = [p % w.L for p in prims]
        a0 = poss[0]
        offs = tuple((p - a0) % w.L for p in poss)
        for _, k2, o2 in self._templates(blocks):
            if (k2, o2) == (kinds, offs):
                return
        # a template is recorded only when it explains at least two independent solved tasks
        self._add_witness(env, blocks, cal)
        explained = sum(1 for s_, t_ in self._witnesses(blocks, cal) if self._explains(kinds, offs, s_, t_))
        env.charge(len(self._witnesses(blocks, cal)))
        if explained < 2:
            return
        if len(blocks.blocks) >= blocks.max_blocks:
            return
        bid = blocks.create(self.template_instructions(kinds, offs), origin="new")
        if bid >= 0:
            blocks.state_set(bid, 0, kinds)
            blocks.state_set(bid, 1, offs)
            blocks.state_set(bid, 2, cal)
            blocks.state_set(bid, 3, TAG_TEMPLATE)

    # ------------------------------------------------ planning in the head
    @staticmethod
    def _apply_mental(kinds, offs, a, x):
        for kind, off in zip(kinds, offs):
            x = w.apply_primitive(w.KINDS[kind], (a + off) % w.L, x)
        return x

    def _plan(self, env, templates, start, target):
        for depth in range(1, self.MAX_PLAN_DEPTH + 1):
            found = self._dfs(env, templates, start, target, depth, [])
            if found is not None:
                return found
        return None

    def _dfs(self, env, templates, x, target, depth, path):
        if depth == 0:
            return list(path) if x == target else None
        for bid, kinds, offs in templates:
            for a in range(w.L):
                env.charge(1)
                y = self._apply_mental(kinds, offs, a, x)
                path.append((bid, a))
                r = self._dfs(env, templates, y, target, depth - 1, path)
                path.pop()
                if r is not None:
                    return r
        return None

    def _execute(self, env, st, plan, templates):
        env.act(RESET)
        by_id = {bid: (kinds, offs) for bid, kinds, offs in templates}
        for bid, a in plan:
            st.regs[0] = a
            before = env.current
            try:
                vm.invoke_block(bid, st)
            except TaskOver:
                if env.success:
                    return True
                raise
            kinds, offs = by_id[bid]
            if env.current != self._apply_mental(kinds, offs, a, before):
                st.blocks.delete(bid)  # the block's behaviour contradicted its own description: retire it
                return False
            if env.success:
                return True
        return False

    # ------------------------------------------------ the task
    def run(self, env, st):
        blocks = st.blocks
        cal = self._ensure_calibration(env, st)
        if env.success:
            return
        # cheap first: a single primitive (12 probes); a one-step solution is a procedure worth keeping
        seq = enumerate_sequences(env, max_depth=1)
        if seq is not None:
            self._record_template(env, st, cal, seq)
            return
        templates = self._templates(blocks)
        if templates:
            plan = self._plan(env, templates, env.start, env.target)
            if plan is not None and self._execute(env, st, plan, templates):
                return
        seq = enumerate_sequences(env)
        if seq is not None:
            self._record_template(env, st, cal, seq)
            return
        env.halt()


class ProcedureNoCalC1(ProcedureReuseC1):
    """Identifier-permutation witness: assumes action id == primitive index."""

    name = "PROCEDURE_NOCAL_C1"
    CALIBRATE = False


BASELINES = {
    "RANDOM_C1": RandomC1,
    "ENUMERATE_C1": EnumerateC1,
    "QUIT_C1": QuitC1,
    "TABLE_MEMO_C1": TableMemoC1,
    "PROCEDURE_REUSE_C1": ProcedureReuseC1,
    "PROCEDURE_NOCAL_C1": ProcedureNoCalC1,
}
ALL_NAMES = ("RANDOM_C1", "ENUMERATE_C1", "ENUMERATE_VM_C1", "QUIT_C1", "TABLE_MEMO_C1",
             "PROCEDURE_REUSE_C1", "PROCEDURE_NOCAL_C1")


def make_baseline(name: str):
    if name == "ENUMERATE_VM_C1":
        return VMPlayer(vm.enumerate_program(), name="ENUMERATE_VM_C1")
    return BASELINES[name]()
