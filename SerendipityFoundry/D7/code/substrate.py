"""
D7 substrate: the Gated Field Machine (GFM) and the generic synthesis grammar.

Design notes (frozen physics):
  * A WORLD is a finite deterministic machine. State = tuple of `nreg` integers
    mod prime `p`. So |V| = p**nreg. The proof world uses nreg=3 (r,u,s) => enumerable.
  * The machine's ISA is a tiny serializable micro-language (tuples only, no
    Python closures) so the whole constitution can be hashed and frozen.
  * BASE PHYSICS (E0) is a designated subset of primitive operators. It induces
    G0 = (V, E0). A certified cut means T is not in the transitive closure of E0
    from S (see certify.py) -- an exact, path-length-infinite fact plus an
    algebraic invariant proof.
  * A HOARD ARTIFACT is a fixed micro-program with an opaque id + byte hash. The
    learner treats it as an executable black box.
  * The generic SYNTHESIS GRAMMAR composes hoard artifacts with sequence,
    bounded repetition, and a machine-state conditional. It contains no
    solution-shaped named API (no MAKE_PORTAL / COMPOSE_OPENERS / WRAP ...).

Nothing in here references a target, a barrier descriptor, or a human category.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Callable

# ----------------------------------------------------------------------------
# Micro-ISA interpreter.  A micro-program is a tuple of micro-instructions.
# Each micro-instruction is a tuple whose first element is an opcode string.
# All arithmetic is mod p.  State is a tuple[int, ...] of length nreg.
# ----------------------------------------------------------------------------

# opcodes (documented; the learner never sees these names, only executes bytes):
#   ("addk", i, k)          reg[i] += k
#   ("subk", i, k)          reg[i] -= k       (p-agnostic decrement)
#   ("mulk", i, k)          reg[i] *= k
#   ("set",  i, k)          reg[i]  = k
#   ("copy", i, j)          reg[i]  = reg[j]
#   ("addreg", i, j)        reg[i] += reg[j]
#   ("submul", i, j, l)     reg[i] += reg[j]*reg[l]      (NONLINEAR, quadratic)
#   ("submul3", i, j,k,l)   reg[i] += reg[j]*reg[k]*reg[l] (NONLINEAR, cubic)
#   ("swap", i, j)          swap reg[i], reg[j]
#   ("ifz", i, subprog)     if reg[i]==0: run subprog     (CONTEXT-SENSITIVE)
#   ("ifnz", i, subprog)    if reg[i]!=0: run subprog     (CONTEXT-SENSITIVE, a GATE)

MICRO_STEP_LIMIT = 10_000  # guards pathological nested programs


class MicroFault(Exception):
    pass


def run_micro(prog, state, p, budget=None):
    """Run a micro-program. Returns (new_state, steps). Deterministic."""
    reg = list(state)
    steps = [0]

    def exec_seq(seq):
        for ins in seq:
            steps[0] += 1
            if steps[0] > MICRO_STEP_LIMIT:
                raise MicroFault("micro step limit")
            if budget is not None and steps[0] > budget:
                raise MicroFault("micro budget")
            op = ins[0]
            if op == "addk":
                _, i, k = ins
                reg[i] = (reg[i] + k) % p
            elif op == "subk":
                _, i, k = ins
                reg[i] = (reg[i] - k) % p
            elif op == "mulk":
                _, i, k = ins
                reg[i] = (reg[i] * k) % p
            elif op == "set":
                _, i, k = ins
                reg[i] = k % p
            elif op == "copy":
                _, i, j = ins
                reg[i] = reg[j]
            elif op == "addreg":
                _, i, j = ins
                reg[i] = (reg[i] + reg[j]) % p
            elif op == "submul":
                _, i, j, l = ins
                reg[i] = (reg[i] + reg[j] * reg[l]) % p
            elif op == "submul3":
                _, i, j, k, l = ins
                reg[i] = (reg[i] + reg[j] * reg[k] * reg[l]) % p
            elif op == "swap":
                _, i, j = ins
                reg[i], reg[j] = reg[j], reg[i]
            elif op == "ifz":
                _, i, sub = ins
                if reg[i] % p == 0:
                    exec_seq(sub)
            elif op == "ifnz":
                _, i, sub = ins
                if reg[i] % p != 0:
                    exec_seq(sub)
            else:
                raise MicroFault(f"bad opcode {op}")

    exec_seq(prog)
    return tuple(reg), steps[0]


# ----------------------------------------------------------------------------
# Canonical serialization + hashing (for freezing the constitution).
# ----------------------------------------------------------------------------

def canon(obj):
    """Deterministic canonical form: lists <-> tuples normalized to lists."""
    if isinstance(obj, (list, tuple)):
        return [canon(x) for x in obj]
    return obj


def sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(canon(obj), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


# ----------------------------------------------------------------------------
# Artifacts.
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class Artifact:
    aid: str                 # opaque id, e.g. "a07"
    prog: tuple              # micro-program (tuple of micro-instructions)
    origin: str = ""         # developmental provenance tag (machine-native, not a hint)

    @property
    def bytes_hash(self) -> str:
        return sha(["ARTIFACT", self.prog])

    def run(self, state, p, budget=None):
        return run_micro(self.prog, state, p, budget=budget)


# ----------------------------------------------------------------------------
# World.
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class World:
    name: str
    p: int
    nreg: int
    base_ops: tuple          # tuple of (opname, micro_prog) for base physics E0
    note: str = ""

    def states(self):
        p, n = self.p, self.nreg
        total = p ** n
        for idx in range(total):
            s, rem = [], idx
            for _ in range(n):
                s.append(rem % p)
                rem //= p
            yield tuple(s)

    def base_neighbors(self, state):
        outs = []
        for _, prog in self.base_ops:
            ns, _ = run_micro(prog, state, self.p)
            outs.append(ns)
        return outs

    def fingerprint(self) -> str:
        return sha(["WORLD", self.name, self.p, self.nreg,
                    [[nm, canon(pr)] for nm, pr in self.base_ops]])


# ----------------------------------------------------------------------------
# The generic synthesis grammar (machine-native composition language).
#
# AST nodes are nested tuples (serializable, hashable):
#   ("nop",)
#   ("quote", aid)                 run artifact `aid` once
#   ("seq", child, child)          run left then right
#   ("rep", n, child)              run child n times   (1 <= n <= rep_max)
#   ("ifz", coord, child)          if state[coord]==0 run child else skip
#
# The grammar intentionally supports multiple composition topologies
# (sequence / repetition / conditional / nesting) and NO solution-named API.
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class Grammar:
    rep_max: int = 6         # bounded repetition
    max_nodes: int = 14      # program-size ceiling
    allow_ifz: bool = True
    allow_rep: bool = True
    ncoord: int = 2          # number of machine coords the ifz/ifnz guard may read

    def fingerprint(self) -> str:
        return sha(["GRAMMAR", self.rep_max, self.max_nodes,
                    self.allow_ifz, self.allow_rep, self.ncoord])


def z_size(ast) -> int:
    tag = ast[0]
    if tag in ("nop", "quote"):
        return 1
    if tag == "seq":
        return 1 + z_size(ast[1]) + z_size(ast[2])
    if tag == "rep":
        return 1 + z_size(ast[2])
    if tag == "ifz":
        return 1 + z_size(ast[2])
    raise MicroFault(f"bad ast tag {tag}")


def z_artifacts_used(ast):
    tag = ast[0]
    if tag == "quote":
        return [ast[1]]
    if tag == "nop":
        return []
    if tag == "seq":
        return z_artifacts_used(ast[1]) + z_artifacts_used(ast[2])
    if tag in ("rep", "ifz"):
        return z_artifacts_used(ast[2])
    raise MicroFault(f"bad ast tag {tag}")


def run_z(ast, state, world: World, hoard: dict, budget=None):
    """Execute a synthesized program z as a macro on `state`. Returns new state."""
    p = world.p
    cost = [0]

    def ev(node, st):
        tag = node[0]
        if tag == "nop":
            return st
        if tag == "quote":
            art = hoard[node[1]]
            ns, steps = art.run(st, p, budget=budget)
            cost[0] += steps
            if budget is not None and cost[0] > budget:
                raise MicroFault("z budget")
            return ns
        if tag == "seq":
            return ev(node[2], ev(node[1], st))
        if tag == "rep":
            n = node[1]
            cur = st
            for _ in range(n):
                cur = ev(node[2], cur)
                cost[0] += 1
                if budget is not None and cost[0] > budget:
                    raise MicroFault("z budget")
            return cur
        if tag == "ifz":
            coord = node[1]
            if st[coord] % p == 0:
                return ev(node[2], st)
            return st
        raise MicroFault(f"bad ast tag {tag}")

    return ev(ast, state), cost[0]


def z_function(ast, world: World, hoard: dict):
    """Materialize z as an explicit function V->V (a dict) over the whole state space."""
    fn = {}
    for st in world.states():
        try:
            ns, _ = run_z(ast, st, world, hoard)
        except MicroFault:
            ns = st  # a faulting program is treated as identity on that state
        fn[st] = ns
    return fn
