"""Exact XAG / AIG Boolean circuit representation, strash, macro flattening, and verifier.

Pinned conventions (immutable for the 28-day sprint):
  - Node IDs:
      * -1              : constant 0 (CONST0). Constant 1 is (-1, out_inv=True).
      * 0 .. n_inputs-1 : primary inputs x_0 .. x_{n_inputs-1}
      * n_inputs + i    : gate i (0-indexed into `gates`), topological order required
                          (strictly left < node_id and right < node_id).
  - Gate basis:
      * op in {"AND", "XOR"} with optional input inversions (left_inv, right_inv).
      * Free wire inversions at gate inputs and primary outputs -> gate count is
        strictly NPN-invariant, and XAG == Knuth B_2 full normal 2-input basis.
      * AIG is the strict subset where every gate has op == "AND".
  - Truth-table encoding:
      * For n inputs, row r in 0..(2^n - 1) assigns x_k = (r >> k) & 1.
      * Truth table is a non-negative Python int of width 2^n bits where bit r
        is f(r). All operations mask by FULL_MASK = (1 << (1 << n)) - 1.
  - Anti-cheating macro contract:
      * Every Macro flattens to primitive {AND, XOR} gates before scoring and
        verification. Structural hashing (strash) deduplicates shared sub-DAGs.
        Macros receive ZERO artificial gate-count discount.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

VALID_OPS = ("AND", "XOR")


def full_mask(n_inputs: int) -> int:
    if n_inputs < 1:
        raise ValueError("n_inputs must be >= 1")
    return (1 << (1 << n_inputs)) - 1


def input_masks(n_inputs: int) -> Tuple[int, ...]:
    """Return canonical truth-table bitmasks for primary inputs x_0 .. x_{n-1}."""
    size = 1 << n_inputs
    masks: List[int] = []
    for k in range(n_inputs):
        m = 0
        bit = 1 << k
        for r in range(size):
            if r & bit:
                m |= 1 << r
        masks.append(m)
    return tuple(masks)


@dataclass(frozen=True)
class Gate:
    op: str
    left: int
    left_inv: bool
    right: int
    right_inv: bool

    def __post_init__(self) -> None:
        if self.op not in VALID_OPS:
            raise ValueError(f"Unsupported gate op: {self.op!r}")


@dataclass(frozen=True)
class XAGCircuit:
    n_inputs: int
    gates: Tuple[Gate, ...]
    outputs: Tuple[Tuple[int, bool], ...]  # (node_id, out_inv)

    def __post_init__(self) -> None:
        if self.n_inputs < 1:
            raise ValueError("n_inputs must be >= 1")
        for idx, g in enumerate(self.gates):
            node_id = self.n_inputs + idx
            if not (-1 <= g.left < node_id) or not (-1 <= g.right < node_id):
                raise ValueError(
                    f"Gate {idx} (node {node_id}) references invalid fanin ({g.left}, {g.right})"
                )
        max_node = self.n_inputs + len(self.gates) - 1
        for out_node, _ in self.outputs:
            if not (-1 <= out_node <= max_node):
                raise ValueError(f"Invalid output node {out_node} (max {max_node})")

    def gate_count(self) -> int:
        return len(self.gates)

    def and_count(self) -> int:
        return sum(1 for g in self.gates if g.op == "AND")

    def xor_count(self) -> int:
        return sum(1 for g in self.gates if g.op == "XOR")

    def is_aig(self) -> bool:
        return all(g.op == "AND" for g in self.gates)

    def truth_tables(self) -> Tuple[int, ...]:
        """Evaluate exact full truth-table bitmasks for all outputs."""
        mask = full_mask(self.n_inputs)
        vals: List[int] = list(input_masks(self.n_inputs))
        for g in self.gates:
            lv = 0 if g.left == -1 else vals[g.left]
            if g.left_inv:
                lv ^= mask
            rv = 0 if g.right == -1 else vals[g.right]
            if g.right_inv:
                rv ^= mask
            if g.op == "AND":
                vals.append(lv & rv)
            else:
                vals.append(lv ^ rv)
        outs: List[int] = []
        for node_id, inv in self.outputs:
            v = 0 if node_id == -1 else vals[node_id]
            if inv:
                v ^= mask
            outs.append(v)
        return tuple(outs)

    def strash_and_prune(self) -> "XAGCircuit":
        """Canonical structural hashing (dedup + dead-gate elimination)."""
        builder = StrashBuilder(self.n_inputs)
        node_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
        for i in range(self.n_inputs):
            node_map[i] = (i, False)
        for idx, g in enumerate(self.gates):
            ln, li = node_map[g.left]
            rn, ri = node_map[g.right]
            res = builder.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
            node_map[self.n_inputs + idx] = res
        mapped_outs = []
        for onode, oinv in self.outputs:
            mn, mi = node_map[onode]
            mapped_outs.append((mn, mi ^ oinv))
        return builder.build(mapped_outs, prune_dead=True)

    def sha256(self) -> str:
        payload = {
            "n_inputs": self.n_inputs,
            "gates": [
                [g.op, g.left, g.left_inv, g.right, g.right_inv]
                for g in self.gates
            ],
            "outputs": [[n, inv] for n, inv in self.outputs],
        }
        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def from_macro_calls(
        cls,
        n_inputs: int,
        calls: Sequence[Tuple["Macro", Sequence[int]]],
        outputs: Sequence[Tuple[str, int, bool]],
    ) -> "XAGCircuit":
        """Instantiate macros by flattening into primitive gates with strash dedup.

        calls: list of (Macro, arg_refs) where arg_refs are primary input indices
               (int >= 0, or -1 for CONST0) or tuples ("callK", out_idx, inv).
        outputs: list of ("in", input_idx, inv) or ("callK", out_idx, inv).
        """
        builder = StrashBuilder(n_inputs)
        call_outs: Dict[str, List[Tuple[int, bool]]] = {}

        def resolve(ref) -> Tuple[int, bool]:
            if isinstance(ref, int):
                return (ref, False)
            if isinstance(ref, tuple) and len(ref) == 2 and isinstance(ref[0], int):
                return (ref[0], bool(ref[1]))
            if isinstance(ref, tuple) and len(ref) == 3 and isinstance(ref[0], str):
                tag, idx, inv = ref
                if tag == "in":
                    return (int(idx), bool(inv))
                bn, bi = call_outs[tag][int(idx)]
                return (bn, bi ^ bool(inv))
            raise ValueError(f"Unsupported wire ref: {ref!r}")

        for c_idx, (macro, args) in enumerate(calls):
            if len(args) != macro.n_inputs:
                raise ValueError(
                    f"Macro {macro.name!r} expects {macro.n_inputs} args, got {len(args)}"
                )
            resolved_args = [resolve(a) for a in args]
            node_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
            for i, pair in enumerate(resolved_args):
                node_map[i] = pair
            for g_idx, g in enumerate(macro.gates):
                ln, li = node_map[g.left]
                rn, ri = node_map[g.right]
                node_map[macro.n_inputs + g_idx] = builder.add_gate(
                    g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv
                )
            outs_c: List[Tuple[int, bool]] = []
            for onode, oinv in macro.outputs:
                mn, mi = node_map[onode]
                outs_c.append((mn, mi ^ oinv))
            call_outs[f"call{c_idx}"] = outs_c

        final_outs = [resolve(o) for o in outputs]
        return builder.build(final_outs, prune_dead=True)


class StrashBuilder:
    """Structural-hashing DAG builder with algebraic local simplifications & dead pruning."""

    def __init__(self, n_inputs: int) -> None:
        self.n_inputs = n_inputs
        self.gates: List[Gate] = []
        self._table: Dict[Tuple[str, int, bool, int, bool], int] = {}

    def add_gate(
        self,
        op: str,
        left: int,
        left_inv: bool,
        right: int,
        right_inv: bool,
    ) -> Tuple[int, bool]:
        if op == "AND":
            # Constant / idempotence / complementarity simplifications
            if left == -1:
                return (-1, False) if not left_inv else (right, right_inv)
            if right == -1:
                return (-1, False) if not right_inv else (left, left_inv)
            if left == right:
                if left_inv == right_inv:
                    return (left, left_inv)
                return (-1, False)
            # Canonical operand order
            if (right, right_inv) < (left, left_inv):
                left, left_inv, right, right_inv = right, right_inv, left, left_inv
            key = ("AND", left, left_inv, right, right_inv)
            if key in self._table:
                return (self._table[key], False)
            nid = self.n_inputs + len(self.gates)
            self.gates.append(Gate("AND", left, left_inv, right, right_inv))
            self._table[key] = nid
            return (nid, False)

        if op == "XOR":
            # Push inversions to output: (~a) ^ b == ~(a ^ b)
            out_inv = left_inv ^ right_inv
            if left == -1:
                return (right, out_inv)
            if right == -1:
                return (left, out_inv)
            if left == right:
                return (-1, out_inv)
            if right < left:
                left, right = right, left
            key = ("XOR", left, False, right, False)
            if key in self._table:
                return (self._table[key], out_inv)
            nid = self.n_inputs + len(self.gates)
            self.gates.append(Gate("XOR", left, False, right, False))
            self._table[key] = nid
            return (nid, out_inv)

        raise ValueError(f"Unsupported op: {op!r}")

    def build(
        self,
        outputs: Sequence[Tuple[int, bool]],
        prune_dead: bool = True,
    ) -> XAGCircuit:
        if not prune_dead:
            return XAGCircuit(
                n_inputs=self.n_inputs,
                gates=tuple(self.gates),
                outputs=tuple((int(n), bool(i)) for n, i in outputs),
            )
        live = set()
        stack = [n for n, _ in outputs if n >= self.n_inputs]
        while stack:
            nid = stack.pop()
            if nid in live or nid < self.n_inputs:
                continue
            live.add(nid)
            g = self.gates[nid - self.n_inputs]
            if g.left >= self.n_inputs:
                stack.append(g.left)
            if g.right >= self.n_inputs:
                stack.append(g.right)

        kept_old = sorted(live)
        remap: Dict[int, int] = {-1: -1}
        for i in range(self.n_inputs):
            remap[i] = i
        new_gates: List[Gate] = []
        for new_idx, old_nid in enumerate(kept_old):
            remap[old_nid] = self.n_inputs + new_idx
            g = self.gates[old_nid - self.n_inputs]
            new_gates.append(
                Gate(g.op, remap[g.left], g.left_inv, remap[g.right], g.right_inv)
            )
        new_outs = tuple((remap[n], bool(inv)) for n, inv in outputs)
        return XAGCircuit(
            n_inputs=self.n_inputs,
            gates=tuple(new_gates),
            outputs=new_outs,
        )


@dataclass(frozen=True)
class Macro:
    name: str
    n_inputs: int
    gates: Tuple[Gate, ...]
    outputs: Tuple[Tuple[int, bool], ...]
    truth_tables: Tuple[int, ...]
    sha256: str
    origin: str = "unknown"

    @classmethod
    def from_circuit(
        cls,
        name: str,
        circuit: XAGCircuit,
        origin: str = "unknown",
    ) -> "Macro":
        clean = circuit.strash_and_prune()
        return cls(
            name=name,
            n_inputs=clean.n_inputs,
            gates=clean.gates,
            outputs=clean.outputs,
            truth_tables=clean.truth_tables(),
            sha256=clean.sha256(),
            origin=origin,
        )


def verify_truth_tables(
    circuit: XAGCircuit,
    targets: Sequence[int],
    meter: Optional[object] = None,
    phase: str = "verify",
) -> bool:
    """Exact bitmask verification of all outputs against target truth tables."""
    if meter is not None:
        meter.charge_evals(1, phase=phase)
    actual = circuit.truth_tables()
    if len(actual) != len(targets):
        return False
    mask = full_mask(circuit.n_inputs)
    return all((a & mask) == (t & mask) for a, t in zip(actual, targets))
