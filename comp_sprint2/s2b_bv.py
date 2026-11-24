"""Track S2-B Core IR & Exact Z3 UNSAT Equivalence Verifier (Verified 8/16-Bit Bit-Vector Superoptimization).

Fixed Primitive BV Instruction Set (every op instruction costs 1 primitive op; constants & inputs cost 0):
  Unary : NOT (~a), NEG (-a)
  Binary: AND (&), OR (|), XOR (^), ADD (+), SUB (-), MUL (*),
          SHL (<<), LSHR (logical >>), ASHR (arithmetic >>),
          ULT (a <u b -> 1/0), EQ (a == b -> 1/0)
  Ternary: ITE (cond != 0 ? a : b)

ZERO artificial macro discount: `op_count()` counts exact live primitive SSA instructions after dead-code pruning.
Equivalence is proven 100% mathematically exact across ALL 2^(width * n_inputs) inputs via Z3 `UNSAT` on
`Exists x: spec(x) != cand(x)`. Any `SAT`, `UNKNOWN`, or timeout is STRICTLY REJECTED.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import z3


UNARY_OPS = frozenset({"NOT", "NEG"})
BINARY_OPS = frozenset({"AND", "OR", "XOR", "ADD", "SUB", "MUL", "SHL", "LSHR", "ASHR", "ULT", "EQ"})
TERNARY_OPS = frozenset({"ITE"})
ALL_BV_OPS = UNARY_OPS | BINARY_OPS | TERNARY_OPS


@dataclass(frozen=True)
class BVNode:
    """One SSA node: op == 'IN' (arg0=input_idx), 'CONST' (arg0=int_val), or primitive BV op."""
    op: str
    args: Tuple[int, ...]


@dataclass(frozen=True)
class BVProgram:
    """Immutable, pruned, structurally hashed fixed-width bit-vector SSA program."""
    width: int               # 8 or 16
    n_inputs: int            # 1..3
    nodes: Tuple[BVNode, ...]
    out_id: int

    def op_count(self) -> int:
        """Exact primitive op count (inputs & constants = 0; every primitive op = 1; ZERO discount)."""
        return sum(1 for n in self.nodes if n.op in ALL_BV_OPS)

    def sha256(self) -> str:
        payload = {
            "width": self.width,
            "n_inputs": self.n_inputs,
            "nodes": [[n.op, list(n.args)] for n in self.nodes],
            "out_id": self.out_id,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()

    def eval_one(self, inputs: Sequence[int]) -> int:
        w = self.width
        mask = (1 << w) - 1
        sign_bit = 1 << (w - 1)
        vals: List[int] = []
        for nd in self.nodes:
            op = nd.op
            if op == "IN":
                vals.append(int(inputs[nd.args[0]]) & mask)
            elif op == "CONST":
                vals.append(int(nd.args[0]) & mask)
            elif op == "NOT":
                vals.append((~vals[nd.args[0]]) & mask)
            elif op == "NEG":
                vals.append((-vals[nd.args[0]]) & mask)
            elif op == "AND":
                vals.append(vals[nd.args[0]] & vals[nd.args[1]])
            elif op == "OR":
                vals.append(vals[nd.args[0]] | vals[nd.args[1]])
            elif op == "XOR":
                vals.append(vals[nd.args[0]] ^ vals[nd.args[1]])
            elif op == "ADD":
                vals.append((vals[nd.args[0]] + vals[nd.args[1]]) & mask)
            elif op == "SUB":
                vals.append((vals[nd.args[0]] - vals[nd.args[1]]) & mask)
            elif op == "MUL":
                vals.append((vals[nd.args[0]] * vals[nd.args[1]]) & mask)
            elif op == "SHL":
                sh = vals[nd.args[1]]
                vals.append(((vals[nd.args[0]] << sh) & mask) if sh < w else 0)
            elif op == "LSHR":
                sh = vals[nd.args[1]]
                vals.append((vals[nd.args[0]] >> sh) if sh < w else 0)
            elif op == "ASHR":
                a = vals[nd.args[0]]
                sh = vals[nd.args[1]]
                sa = a - (1 << w) if (a & sign_bit) else a
                if sh >= w:
                    vals.append(mask if sa < 0 else 0)
                else:
                    vals.append((sa >> sh) & mask)
            elif op == "ULT":
                vals.append(1 if vals[nd.args[0]] < vals[nd.args[1]] else 0)
            elif op == "EQ":
                vals.append(1 if vals[nd.args[0]] == vals[nd.args[1]] else 0)
            elif op == "ITE":
                vals.append(vals[nd.args[1]] if vals[nd.args[0]] != 0 else vals[nd.args[2]])
            else:
                raise ValueError(f"Unknown BV op: {op!r}")
        return vals[self.out_id]

    def eval_vectors(self, test_vectors: Sequence[Tuple[int, ...]]) -> Tuple[int, ...]:
        return tuple(self.eval_one(tv) for tv in test_vectors)

    def to_expr_str(self) -> str:
        """Compact readable SSA/expression view for diagnostics."""
        names: List[str] = []
        for idx, nd in enumerate(self.nodes):
            if nd.op == "IN":
                names.append(f"x{nd.args[0]}")
            elif nd.op == "CONST":
                names.append(str(nd.args[0]))
            elif nd.op in UNARY_OPS:
                s = "~" if nd.op == "NOT" else "-"
                names.append(f"({s}{names[nd.args[0]]})")
            elif nd.op == "ITE":
                names.append(f"ITE({names[nd.args[0]]},{names[nd.args[1]]},{names[nd.args[2]]})")
            else:
                sym = {
                    "AND": "&", "OR": "|", "XOR": "^", "ADD": "+", "SUB": "-",
                    "MUL": "*", "SHL": "<<", "LSHR": ">>u", "ASHR": ">>s", "ULT": "<u", "EQ": "==",
                }[nd.op]
                names.append(f"({names[nd.args[0]]}{sym}{names[nd.args[1]]})")
        return names[self.out_id]

    def to_z3(self, z3_vars: Sequence[z3.BitVecRef]) -> z3.BitVecRef:
        w = self.width
        vals: List[z3.BitVecRef] = []
        for nd in self.nodes:
            op = nd.op
            if op == "IN":
                vals.append(z3_vars[nd.args[0]])
            elif op == "CONST":
                vals.append(z3.BitVecVal(nd.args[0] & ((1 << w) - 1), w))
            elif op == "NOT":
                vals.append(~vals[nd.args[0]])
            elif op == "NEG":
                vals.append(-vals[nd.args[0]])
            elif op == "AND":
                vals.append(vals[nd.args[0]] & vals[nd.args[1]])
            elif op == "OR":
                vals.append(vals[nd.args[0]] | vals[nd.args[1]])
            elif op == "XOR":
                vals.append(vals[nd.args[0]] ^ vals[nd.args[1]])
            elif op == "ADD":
                vals.append(vals[nd.args[0]] + vals[nd.args[1]])
            elif op == "SUB":
                vals.append(vals[nd.args[0]] - vals[nd.args[1]])
            elif op == "MUL":
                vals.append(vals[nd.args[0]] * vals[nd.args[1]])
            elif op == "SHL":
                vals.append(vals[nd.args[0]] << vals[nd.args[1]])
            elif op == "LSHR":
                vals.append(z3.LShR(vals[nd.args[0]], vals[nd.args[1]]))
            elif op == "ASHR":
                vals.append(vals[nd.args[0]] >> vals[nd.args[1]])
            elif op == "ULT":
                vals.append(z3.If(z3.ULT(vals[nd.args[0]], vals[nd.args[1]]), z3.BitVecVal(1, w), z3.BitVecVal(0, w)))
            elif op == "EQ":
                vals.append(z3.If(vals[nd.args[0]] == vals[nd.args[1]], z3.BitVecVal(1, w), z3.BitVecVal(0, w)))
            elif op == "ITE":
                vals.append(z3.If(vals[nd.args[0]] != z3.BitVecVal(0, w), vals[nd.args[1]], vals[nd.args[2]]))
            else:
                raise ValueError(f"Unknown BV op: {op!r}")
        return vals[self.out_id]


class BVBuilder:
    """Structural-hashing + constant-folding SSA builder for BVProgram."""

    def __init__(self, width: int, n_inputs: int, fold_constants: bool = True) -> None:
        self.width = int(width)
        self.mask = (1 << self.width) - 1
        self.n_inputs = int(n_inputs)
        self.fold_constants = bool(fold_constants)
        self.nodes: List[BVNode] = []
        self._table: Dict[BVNode, int] = {}
        self._const_val: Dict[int, int] = {}
        for i in range(self.n_inputs):
            self._add_raw(BVNode("IN", (i,)))

    def _add_raw(self, nd: BVNode) -> int:
        if nd in self._table:
            return self._table[nd]
        idx = len(self.nodes)
        self.nodes.append(nd)
        self._table[nd] = idx
        if nd.op == "CONST":
            self._const_val[idx] = nd.args[0] & self.mask
        return idx

    def inp(self, i: int) -> int:
        if not (0 <= i < self.n_inputs):
            raise ValueError(f"Input index {i} out of range [0, {self.n_inputs})")
        return self._add_raw(BVNode("IN", (int(i),)))

    def const(self, val: int) -> int:
        return self._add_raw(BVNode("CONST", (int(val) & self.mask,)))

    def op(self, op_name: str, *args: int) -> int:
        if op_name not in ALL_BV_OPS:
            raise ValueError(f"Unsupported BV op: {op_name!r}")
        iargs = tuple(int(a) for a in args)
        if op_name in UNARY_OPS and len(iargs) != 1:
            raise ValueError(f"{op_name} takes 1 arg")
        if op_name in BINARY_OPS and len(iargs) != 2:
            raise ValueError(f"{op_name} takes 2 args")
        if op_name in TERNARY_OPS and len(iargs) != 3:
            raise ValueError(f"{op_name} takes 3 args")

        # Canonical commutative ordering
        if op_name in ("AND", "OR", "XOR", "ADD", "MUL", "EQ") and iargs[1] < iargs[0]:
            iargs = (iargs[1], iargs[0])

        # Exact constant folding when all args are constants
        if self.fold_constants and all(a in self._const_val for a in iargs):
            cvals = [self._const_val[a] for a in iargs]
            tmp = BVProgram(self.width, 0, tuple(BVNode("CONST", (v,)) for v in cvals) + (BVNode(op_name, tuple(range(len(cvals)))),), len(cvals))
            return self.const(tmp.eval_one(()))

        # Trivial sound local identities (when fold_constants=True)
        if self.fold_constants:
            if op_name == "NOT" and self.nodes[iargs[0]].op == "NOT":
                return self.nodes[iargs[0]].args[0]
            if op_name == "NEG" and self.nodes[iargs[0]].op == "NEG":
                return self.nodes[iargs[0]].args[0]
            if op_name in BINARY_OPS:
                a, b = iargs
                ca = self._const_val.get(a)
                cb = self._const_val.get(b)
                if op_name == "XOR":
                    if a == b: return self.const(0)
                    if ca == 0: return b
                    if cb == 0: return a
                elif op_name == "AND":
                    if a == b: return a
                    if ca == 0 or cb == 0: return self.const(0)
                    if ca == self.mask: return b
                    if cb == self.mask: return a
                elif op_name == "OR":
                    if a == b: return a
                    if ca == 0: return b
                    if cb == 0: return a
                    if ca == self.mask or cb == self.mask: return self.const(self.mask)
                elif op_name == "ADD":
                    if ca == 0: return b
                    if cb == 0: return a
                elif op_name == "SUB":
                    if a == b: return self.const(0)
                    if cb == 0: return a
                elif op_name == "MUL":
                    if ca == 0 or cb == 0: return self.const(0)
                    if ca == 1: return b
                    if cb == 1: return a
                elif op_name in ("SHL", "LSHR", "ASHR"):
                    if cb == 0: return a
                elif op_name == "EQ" and a == b:
                    return self.const(1)
                elif op_name == "ULT" and a == b:
                    return self.const(0)
            elif op_name == "ITE":
                c, t, f = iargs
                if t == f: return t
                cc = self._const_val.get(c)
                if cc is not None:
                    return t if cc != 0 else f

        return self._add_raw(BVNode(op_name, iargs))

    def build(self, out_id: int) -> BVProgram:
        """Dead-code prune to live reachable subgraph and return immutable BVProgram."""
        live = set()
        stack = [int(out_id)]
        while stack:
            u = stack.pop()
            if u in live:
                continue
            live.add(u)
            nd = self.nodes[u]
            if nd.op in ALL_BV_OPS:
                for a in nd.args:
                    stack.append(a)
        ordered = sorted(live)
        remap = {old: new for new, old in enumerate(ordered)}
        new_nodes: List[BVNode] = []
        for old in ordered:
            nd = self.nodes[old]
            if nd.op in ALL_BV_OPS:
                new_nodes.append(BVNode(nd.op, tuple(remap[a] for a in nd.args)))
            else:
                new_nodes.append(nd)
        return BVProgram(width=self.width, n_inputs=self.n_inputs, nodes=tuple(new_nodes), out_id=remap[int(out_id)])


def default_test_vectors(width: int, n_inputs: int, seed: int = 20261124, n_rand: int = 24) -> Tuple[Tuple[int, ...], ...]:
    """Deterministic edge-case + random test vectors for fast CEGIS concrete pre-filtering."""
    mask = (1 << width) - 1
    half = 1 << (width - 1)
    edge_vals = [0, 1, 2, mask, half, half - 1, 0x55 & mask if width == 8 else 0x5555, 0xAA & mask if width == 8 else 0xAAAA]
    vecs: List[Tuple[int, ...]] = []
    for i in range(len(edge_vals)):
        vecs.append(tuple(edge_vals[(i + j * 3) % len(edge_vals)] for j in range(n_inputs)))
    rng = random.Random(seed + width * 101 + n_inputs * 17)
    for _ in range(n_rand):
        vecs.append(tuple(rng.randint(0, mask) for _ in range(n_inputs)))
    return tuple(vecs)


def verify_bv_equiv_z3(
    spec: BVProgram,
    cand: BVProgram,
    timeout_ms: int = 1500,
) -> Tuple[bool, Optional[Tuple[int, ...]]]:
    """Exact mathematical equivalence proof via Z3 UNSAT on `spec(x) != cand(x)`.

    Returns `(True, None)` ONLY when Z3 returns `z3.unsat`.
    Returns `(False, counterexample_tuple)` when `z3.sat`.
    Returns `(False, None)` on `z3.unknown` / timeout / width mismatch (STRICT REJECTION!).
    """
    if spec.width != cand.width or spec.n_inputs != cand.n_inputs:
        return False, None
    if spec.sha256() == cand.sha256():
        return True, None

    zvars = [z3.BitVec(f"x{i}", spec.width) for i in range(spec.n_inputs)]
    s = z3.Solver()
    s.set("timeout", int(timeout_ms))
    s.add(spec.to_z3(zvars) != cand.to_z3(zvars))
    res = s.check()
    if res == z3.unsat:
        return True, None
    if res == z3.sat:
        m = s.model()
        ce = tuple(m.eval(v, model_completion=True).as_long() for v in zvars)
        return False, ce
    return False, None


def _z3_ast_to_bvprog(expr: z3.ExprRef, width: int, n_inputs: int, zvars: Sequence[z3.BitVecRef]) -> Optional[BVProgram]:
    """Translate a Z3 simplified BitVec expression back into a verified primitive BVProgram."""
    b = BVBuilder(width, n_inputs, fold_constants=True)
    var_names = {f"x{i}": i for i in range(n_inputs)}
    memo: Dict[int, int] = {}

    def conv(e: z3.ExprRef) -> Optional[int]:
        eid = e.get_id()
        if eid in memo:
            return memo[eid]
        if z3.is_bv_value(e):
            r = b.const(e.as_long())
            memo[eid] = r
            return r
        if z3.is_const(e) and e.decl().name() in var_names:
            r = b.inp(var_names[e.decl().name()])
            memo[eid] = r
            return r
        kind = e.decl().kind()
        ch = e.children()
        if kind == z3.Z3_OP_BNOT:
            a = conv(ch[0]); return None if a is None else b.op("NOT", a)
        if kind == z3.Z3_OP_BNEG:
            a = conv(ch[0]); return None if a is None else b.op("NEG", a)
        if kind in (z3.Z3_OP_BAND, z3.Z3_OP_BOR, z3.Z3_OP_BXOR, z3.Z3_OP_BADD, z3.Z3_OP_BMUL):
            op_map = {
                z3.Z3_OP_BAND: "AND", z3.Z3_OP_BOR: "OR", z3.Z3_OP_BXOR: "XOR",
                z3.Z3_OP_BADD: "ADD", z3.Z3_OP_BMUL: "MUL",
            }
            cur = conv(ch[0])
            if cur is None: return None
            for nxt in ch[1:]:
                cn = conv(nxt)
                if cn is None: return None
                cur = b.op(op_map[kind], cur, cn)
            memo[eid] = cur
            return cur
        if kind in (z3.Z3_OP_BSUB, z3.Z3_OP_BSHL, z3.Z3_OP_BLSHR, z3.Z3_OP_BASHR):
            op_map2 = {
                z3.Z3_OP_BSUB: "SUB", z3.Z3_OP_BSHL: "SHL",
                z3.Z3_OP_BLSHR: "LSHR", z3.Z3_OP_BASHR: "ASHR",
            }
            a, c = conv(ch[0]), conv(ch[1])
            if a is None or c is None: return None
            r = b.op(op_map2[kind], a, c)
            memo[eid] = r
            return r
        if kind == z3.Z3_OP_ITE and len(ch) == 3:
            cond, t_e, f_e = ch
            # Handle common Z3 simplified boolean conditions (ULT, EQ, != 0, Not(...))
            ck = cond.decl().kind()
            cc = cond.children()
            t_id, f_id = conv(t_e), conv(f_e)
            if t_id is None or f_id is None:
                return None
            if ck == z3.Z3_OP_NOT and len(cc) == 1:
                cond = cc[0]; ck = cond.decl().kind(); cc = cond.children()
                t_id, f_id = f_id, t_id
            if ck == z3.Z3_OP_ULT and len(cc) == 2:
                a, c = conv(cc[0]), conv(cc[1])
                if a is None or c is None: return None
                cid = b.op("ULT", a, c)
                r = b.op("ITE", cid, t_id, f_id)
                memo[eid] = r
                return r
            if ck == z3.Z3_OP_EQ and len(cc) == 2:
                a, c = conv(cc[0]), conv(cc[1])
                if a is None or c is None: return None
                cid = b.op("EQ", a, c)
                r = b.op("ITE", cid, t_id, f_id)
                memo[eid] = r
                return r
        return None

    out = conv(expr)
    if out is None:
        return None
    return b.build(out)


def simplify_bv_with_z3_industry(spec: BVProgram) -> BVProgram:
    """Arm A1_Z3_SIMPLIFY: Z3's built-in C++ `simplify` + `ctx-solver-simplify` industry baseline."""
    zvars = [z3.BitVec(f"x{i}", spec.width) for i in range(spec.n_inputs)]
    z_spec = spec.to_z3(zvars)
    best = spec

    # Try standard z3.simplify + aggressive bit-vector simplification options
    for z_cand in (
        z3.simplify(z_spec),
        z3.simplify(z_spec, som=True, flat=True, bv_ite2id=True, bv_le_extra=True, elim_and=False),
    ):
        prog = _z3_ast_to_bvprog(z_cand, spec.width, spec.n_inputs, zvars)
        if prog is not None and prog.op_count() < best.op_count():
            ok, _ = verify_bv_equiv_z3(spec, prog)
            if ok:
                best = prog
    return best
