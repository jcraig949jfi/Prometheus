"""Positive controls the EARLY stage must pass before the campaign is allowed to mean anything:
  vm_executes                 every known witness solves its task on the VM; the replicator copies itself bit-for-bit
  known_replicator_replicates a seeded replicator under ENDOGENOUS_COPY sustains high-fidelity replication
  known_witness_solves        a seeded task witness under EXTERNAL reproduction is a sustained solver
  external_reproduction_evolves  a RANDOM population under EXTERNAL + EXPLICIT + INCREMENTAL reaches the task
  endogenous_invades_when_seeded a seeded replicator MINORITY takes over a random majority under ENDOGENOUS_COPY
A failing positive control halts the campaign with the failure in the packet (the instrument is broken; nothing it
would produce afterwards is evidence). Seeded runs are never evidence for spontaneous origin: the scheduler tags them."""
from __future__ import annotations

from typing import Dict, List

from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score
from prometheus.z80atlas.world import World, Config

BASE = dict(world="GRID", representation="Z80_64", layout="SHARED", spatial="LOCAL", scoring="ATOMIC", read_gate="ABR",
            env_dynamics="FIXED", mutation="BYTE", mutation_rate="MED", recombination="NONE")


def vm_executes() -> Dict:
    L = 64; checks = {}
    mem = bytearray(256); mem[:8] = vm.replicator(L); tr = vm.execute(mem, L, 0, 512, [])
    checks["replicator_copies_exactly"] = bytes(mem[L:2 * L]) == bytes(mem[:L]) and tr.halted
    for name, prog in (("const", vm.witness_const(9)), ("echo", vm.witness_echo()), ("inc", vm.witness_inc()),
                       ("cond_one", vm.witness_cond_one()), ("cond_multi", vm.witness_cond_multi()), ("sum2", vm.witness_sum2())):
        checks["witness_" + name] = witness_check(name, prog)
    return {"name": "vm_executes", "passed": all(checks.values()), "checks": checks}


_WITNESS_CASES = {"const": (Task("CONST", k=9), [0]), "echo": (Task("ECHO"), [42]), "inc": (Task("INC"), [200]),
                  "cond_one": (Task("COND_ONE"), [201]), "cond_multi": (Task("COND_MULTI"), [130]), "sum2": (Task("SUM2"), [250, 10])}


def witness_check(name: str, prog: bytes, L: int = 64) -> bool:
    """A witness must answer its task (FORCED gate where the task needs a read). The v1 check accepted ANY program for
    'const' (`or name == "const"`; forensics m4)."""
    task, inp = _WITNESS_CASES[name]
    mem = bytearray(256); mem[:len(prog)] = prog
    for k, v in enumerate(inp):
        mem[vm.IN_BASE + k] = v
    tr = vm.execute(mem, L, 0, 256, inp)
    return score(task, tr.outputs, task.expected(inp), "ATOMIC", "FORCED", tr.first_out_step, tr.first_in_step) >= 0.999


CONTROL_VECS: List[Dict] = [
    {"name": "known_replicator_replicates", "vec": dict(BASE, reproduction="ENDOGENOUS_COPY", pressure="IMPLICIT", task="INC", init="SEEDED_REPLICATOR", mutation_rate="LOW"),
     "predicate": lambda s: (s["mean_fidelity_tail"] or 0) >= 0.8 and s["alive_fraction"] >= 0.5 and (s["replication_rate_tail"] or 0) >= 0.05},
    {"name": "known_witness_solves", "vec": dict(BASE, reproduction="EXTERNAL", pressure="EXPLICIT", task="INC", init="SEEDED_WITNESS"),
     "predicate": lambda s: (s["solvers_tail"] or 0) >= 1},
    {"name": "external_reproduction_evolves", "vec": dict(BASE, reproduction="EXTERNAL", pressure="EXPLICIT", task="INC", scoring="INCREMENTAL", init="RANDOM"),
     "predicate": lambda s: s["first_crossing"] is not None},
    {"name": "endogenous_invades_when_seeded", "vec": dict(BASE, reproduction="ENDOGENOUS_COPY", pressure="IMPLICIT", task="INC", init="SEEDED_REPLICATOR", mutation_rate="LOW"),
     "predicate": lambda s: s["seed_lineage_share"] >= 0.5},
]
