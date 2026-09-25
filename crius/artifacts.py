"""Executable artifacts: blocks of VM instructions with local state, kept in a bounded store.

The store knows only that a block is a list of instructions plus state
slots. Execution of a block is the VM's job (crius/vm.py invoke_block);
the store records creation, deletion and invocation events per task so
the constructed machinery can be inspected afterwards.
"""

from __future__ import annotations

import copy
import random

from .workspace import OBJECT_METADATA_BYTES, is_value, value_size

COSTS = {
    "new": 3,
    "append": 2,
    "patch": 2,
    "copy_per_instr": 1,
    "compose_per_instr": 1,
    "delete": 1,
    "invoke": 1,
    "state_get": 1,
    "state_set": 1,
    "len": 1,
    "count": 1,
}

STATE_SLOTS = 8
INSTR_BYTES = 4
LOG_CAP = 20000   # telemetry lists (events, edges, invocation log) keep at most this many entries; overflow is counted


class ExecutableBlock:
    __slots__ = ("block_id", "instructions", "local_state", "input_ports", "output_ports", "origin")

    def __init__(self, block_id: int, instructions=None, origin: str = "new"):
        self.block_id = block_id
        self.instructions = list(instructions or [])
        self.local_state = [0] * STATE_SLOTS
        self.input_ports = tuple(range(8))   # blocks run in the caller's register file
        self.output_ports = tuple(range(8))
        self.origin = origin

    def size_bytes(self) -> int:
        return OBJECT_METADATA_BYTES + len(self.instructions) * INSTR_BYTES + sum(value_size(v) for v in self.local_state)

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "instructions": [list(i) for i in self.instructions],
            "local_state": [list(v) if isinstance(v, tuple) else v for v in self.local_state],
            "origin": self.origin,
        }


class BlockStore:
    def __init__(self, max_blocks: int = 32, max_block_len: int = 64):
        self.max_blocks = max_blocks
        self.max_block_len = max_block_len
        self.blocks = {}
        self.next_id = 0
        self.cost = 0
        self.current_task = -1
        self.events = []          # creation / deletion / patch events with task index
        self.invocations = {}     # block_id -> total invocations
        self.task_invocations = {}  # block_id -> invocations during the current task
        self.edges = []           # (kind, from_id, to_id, task_index): copy/compose/invoked_from
        self.invocation_log = []  # {task, block, entry: R0..R3, actions: emitted action ids}; capped
        self.dropped = {"events": 0, "edges": 0, "invocation_log": 0}

    @classmethod
    def empty(cls, cfg: dict = None) -> "BlockStore":
        if cfg is None:
            return cls()
        w = cfg["workspace"]
        return cls(max_blocks=w["max_blocks"], max_block_len=w["max_block_len"])

    # ------------------------------------------------------------ accounting
    def bytes_used(self) -> int:
        return sum(b.size_bytes() for b in self.blocks.values())

    def clear(self):
        self.__init__(self.max_blocks, self.max_block_len)

    def begin_task(self, task_index: int):
        self.current_task = task_index
        self.task_invocations = {}

    def snapshot(self) -> dict:
        return copy.deepcopy(
            {"blocks": {k: (b.instructions, b.local_state, b.origin) for k, b in self.blocks.items()},
             "next_id": self.next_id}
        )

    def restore(self, snap: dict):
        snap = copy.deepcopy(snap)
        self.blocks = {}
        for k, (ins, st, origin) in snap["blocks"].items():
            b = ExecutableBlock(k, ins, origin)
            b.local_state = st
            self.blocks[k] = b
        self.next_id = snap["next_id"]

    def structure(self) -> dict:
        return {
            "blocks": len(self.blocks),
            "instructions": sum(len(b.instructions) for b in self.blocks.values()),
            "bytes": self.bytes_used(),
            "log_dropped": dict(self.dropped),
        }

    def _event(self, kind: str, block_id: int, **extra):
        if len(self.events) >= LOG_CAP:
            self.dropped["events"] += 1
            return
        e = {"task": self.current_task, "kind": kind, "block_id": block_id}
        e.update(extra)
        self.events.append(e)

    def _edge(self, kind: str, a: int, b: int):
        if len(self.edges) >= LOG_CAP:
            self.dropped["edges"] += 1
            return
        self.edges.append((kind, a, b, self.current_task))

    # ------------------------------------------------------------ construction
    def create(self, instructions=None, origin: str = "new") -> int:
        self.cost += COSTS["new"]
        if len(self.blocks) >= self.max_blocks:
            return -1
        instructions = list(instructions or [])[: self.max_block_len]
        bid = self.next_id
        self.next_id += 1
        self.blocks[bid] = ExecutableBlock(bid, instructions, origin)
        self._event("create", bid, origin=origin, length=len(instructions))
        return bid

    def append(self, block_id: int, instruction) -> bool:
        self.cost += COSTS["append"]
        b = self.blocks.get(int(block_id))
        if b is None or len(b.instructions) >= self.max_block_len:
            return False
        b.instructions.append(tuple(instruction))
        self._event("append", b.block_id)
        return True

    def patch(self, block_id: int, index: int, instruction) -> bool:
        self.cost += COSTS["patch"]
        b = self.blocks.get(int(block_id))
        if b is None or not b.instructions:
            return False
        b.instructions[int(index) % len(b.instructions)] = tuple(instruction)
        self._event("patch", b.block_id, index=int(index) % len(b.instructions))
        return True

    def copy(self, block_id: int) -> int:
        src = self.blocks.get(int(block_id))
        if src is None:
            self.cost += COSTS["new"]
            return -1
        self.cost += COSTS["copy_per_instr"] * max(1, len(src.instructions))
        nid = self.create(src.instructions, origin="copy")
        if nid >= 0:
            self.blocks[nid].local_state = list(src.local_state)
            self._edge("copy", src.block_id, nid)
        return nid

    def compose(self, a: int, b: int) -> int:
        ba, bb = self.blocks.get(int(a)), self.blocks.get(int(b))
        if ba is None or bb is None:
            self.cost += COSTS["new"]
            return -1
        self.cost += COSTS["compose_per_instr"] * max(1, len(ba.instructions) + len(bb.instructions))
        nid = self.create(ba.instructions + bb.instructions, origin="compose")
        if nid >= 0:
            self._edge("compose", ba.block_id, nid)
            self._edge("compose", bb.block_id, nid)
        return nid

    def delete(self, block_id: int) -> bool:
        self.cost += COSTS["delete"]
        b = self.blocks.pop(int(block_id), None)
        if b is None:
            return False
        self._event("delete", b.block_id)
        return True

    def length(self, block_id: int) -> int:
        self.cost += COSTS["len"]
        b = self.blocks.get(int(block_id))
        return len(b.instructions) if b is not None else -1

    def count(self) -> int:
        self.cost += COSTS["count"]
        return len(self.blocks)

    def ids(self) -> list:
        return sorted(self.blocks)

    def state_get(self, block_id: int, slot: int):
        self.cost += COSTS["state_get"]
        b = self.blocks.get(int(block_id))
        if b is None:
            return 0
        return b.local_state[int(slot) % STATE_SLOTS]

    def state_set(self, block_id: int, slot: int, value) -> bool:
        self.cost += COSTS["state_set"]
        b = self.blocks.get(int(block_id))
        if b is None or not is_value(value):
            return False
        b.local_state[int(slot) % STATE_SLOTS] = value
        return True

    def log_invocation(self, block_id: int, entry_regs, actions, arg=None):
        if len(self.invocation_log) >= 5000:
            self.dropped["invocation_log"] += 1
            return
        if arg is None:
            arg = entry_regs[0] if entry_regs else 0
        self.invocation_log.append({"task": self.current_task, "block": block_id,
                                    "entry": [list(r) if isinstance(r, tuple) else (r if isinstance(r, int) else str(r)) for r in entry_regs],
                                    "arg": (arg if isinstance(arg, int) else str(arg)),
                                    "actions": list(actions)})

    def note_invocation(self, block_id: int, from_block: int):
        self.cost += COSTS["invoke"]
        self.invocations[block_id] = self.invocations.get(block_id, 0) + 1
        self.task_invocations[block_id] = self.task_invocations.get(block_id, 0) + 1
        if from_block >= 0:
            self._edge("invoked_from", from_block, block_id)

    # ------------------------------------------------------------ scramble
    def scramble(self, rng: random.Random):
        """Shuffle each block's instruction order and permute block ids; sizes preserved."""
        ids = sorted(self.blocks)
        perm = list(ids)
        rng.shuffle(perm)
        new = {}
        for old_id, new_id in zip(ids, perm):
            b = self.blocks[old_id]
            ins = list(b.instructions)
            rng.shuffle(ins)
            nb = ExecutableBlock(new_id, ins, b.origin)
            nb.local_state = list(b.local_state)
            new[new_id] = nb
        self.blocks = new
