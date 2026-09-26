"""v2 detectors (added 2026-09-23 by the post-campaign forensics; roles/Bellerophon/forensics_2026-09-23/).

The frozen v1 triggers in observatory.py stay byte-for-byte (their hash is part of the historical campaign); they are
NOT fit for adjudication (ISSUE_AND_REPAIR_LEDGER.md). These predicates read only the repaired summary fields:
  task_reached       a verified exact solver of the CONFIGURED task is alive at the end, and the world is not extinct
  self_replication   >= 1 SELF_REPLICATION birth (own bytes, own code, pre- and post-execution fidelity >= 0.9)
  sustained          a SELF_REPLICATION chain of depth >= min_depth
  spontaneous        self_replication from a fresh start: init RANDOM, no init_tapes, first self-replicator unseeded
They are predicates on ONE run. Comparisons between arms are made by the preregistered analysis (GROUNDING_PREREG.md)
with a declared experimental unit, never by any() over unequal run sets."""
from __future__ import annotations

from typing import Dict, Optional

from prometheus.z80atlas.tasks import Task, verify_tape as _verify
from prometheus.z80atlas.world import Config


def task_reached(s: Dict) -> bool:
    return (not s.get("extinct")) and (s.get("verified") or {}).get("exact_solvers_final", 0) >= 1


def self_replication(s: Dict) -> bool:
    return (s.get("self_rep_births") or 0) > 0


def sustained(s: Dict, min_depth: int = 3) -> bool:
    return (s.get("sr_max_depth") or 0) >= min_depth


def spontaneous(s: Dict, vec: Dict[str, str], has_init_tapes: bool) -> bool:
    fsr = s.get("first_self_replication") or {}
    return vec.get("init") == "RANDOM" and not has_init_tapes and bool(fsr) and not fsr.get("seeded")


def verify_tape(tape: bytes, cfg: Config, task: Optional[Task] = None) -> Dict:
    task = task or Task(cfg.task)
    return _verify(tape, cfg.L, task, cfg.read_gate, cfg.budget, cfg.layout, cfg.allow_copyall)


# ---- G5 frozen reproductive-architecture descriptor (frozen in GROUNDING_PREREG.md before any grounding run) ----------
def repro_descriptor(tape: bytes, cfg: Config, task: Optional[Task] = None) -> Dict:
    """Execute the tape ALONE (empty neighbour window, one panel input) and describe its reproductive organisation:
      self_copy        >= 90% of the L window bytes last written by a copy op from the tape's OWN bytes, executed by its
                       own code, and the window matches the pre-execution tape at >= 0.9
      copy_op          the instruction that wrote most window bytes (LDI 0x14 / LDIR 0x15 / COPYALL 0x16 / other)
      copy_pc          lowest PC that wrote a window byte (where the copy routine sits)
      exec_own_bytes   distinct own-tape PCs executed (the code the organism actually runs)
      exec_before_copy own-tape PCs < copy_pc that were executed (the copy routine's setup extent)
      uses_io          executed IN or OUT
      task_accuracy    fraction of the configured task's fixed panel answered exactly (tasks.verify_tape)
    The descriptor is a pure function of (tape, cfg, task)."""
    from prometheus.z80atlas import vm
    L = cfg.L
    t = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    mem = bytearray(256); mem[:L] = t
    task = task or Task(cfg.task)
    inputs = [42] if task.kind != "SUM2" else [42, 7]
    for k, v in enumerate(inputs):
        mem[vm.IN_BASE + k] = v
    tr = vm.execute(mem, L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall, trace_pcs=True, ldir=cfg.ldir, undefined=cfg.undefined_op)
    prov = tr.win_prov
    own = [(off, pc) for off, (src, pc, op) in prov.items() if off < L and op in vm.COPY_OPS and src is not None and src < L]
    own_code = sum(1 for _, pc in own if pc < L)
    child = bytes(mem[L:2 * L])
    fid = 1.0 - sum(1 for x, y in zip(child, t) if x != y) / L
    ops: Dict[int, int] = {}
    for off, (src, pc, op) in prov.items():
        ops[op] = ops.get(op, 0) + 1
    copy_pc = min((pc for _, (src, pc, op) in prov.items()), default=None)
    pcs = {p for p in (tr.pcs or ()) if p < L}
    return {"self_copy": len(own) >= 0.9 * L and own_code >= 0.9 * max(1, len(own)) and fid >= 0.9,
            "copy_op": max(ops, key=ops.get) if ops else None, "copy_pc": copy_pc,
            "exec_own_bytes": len(pcs), "exec_before_copy": len([p for p in pcs if copy_pc is not None and p < copy_pc]),
            "uses_io": bool(tr.opcodes.get(vm.IN_A) or tr.opcodes.get(vm.OUT_A)),
            "task_accuracy": verify_tape(t, cfg, task)["accuracy"]}
