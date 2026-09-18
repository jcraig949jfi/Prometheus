"""Node kinds of the graph organism (proteus.graph_organism.v1) -- the R1 affordance table.

Opened by the operator 2026-09-18 ("Yes" to PROTEUS-43: one new runtime profile for Campaign 6,
v0 frozen as the control). This is a NEW runtime with its own hash; nothing in proteus/foundry
changes and no v0 genome is re-keyed.

Every kind is a MINIMAL COMPUTATIONAL AFFORDANCE in one of v0's nine categories -- arithmetic,
comparison, logical, read_write, indirection (state slots), opaque_io (channels), randomness (a
costed external draw), halt_yield, control -- and never a cognitive function (R1 ontology gate).
What is NEW relative to v0 is only WHERE structure lives: in edges, not in positions.

    v0 positional jumps (JMP/JZ/JNZ over immediate offsets) are REMOVED; routing is a ROUTE node
    whose two control out-ports are selected by its predicate input. Moving a subgraph moves its
    edges with it, so structural mutation no longer breaks routing (C4-04's addressing damage).

    CALL / RETURN are admitted as "indirection over CONTROL": CALL pushes its `after` port on a
    bounded stack and enters its `body` port; RETURN pops. It carries no arguments beyond data
    edges, no notion of a procedure, module or name; a subgraph is only a connected set of nodes.
    If the R1 reviewer rejects this row, recurrence remains available through back-edges alone.

Ports. Every node has DATA_IN inputs (0..2), ONE data output (its value), and CONTROL_OUT control
ports (0, 1 or 2). An unconnected data input reads 0 (as v0's IN on an empty channel). An
unconnected control out-port ends the tick (halt semantics). A node with no control edge INTO it
and not the entry is DORMANT: it never executes and costs nothing -- neutral structure is
first-class, not an accident of jump targets.

The table's identity is `AFFORDANCE_HASH` (sha256 of its canonical serialisation) and is part of
the graph runtime hash. Adding a kind is a reviewed change and a new runtime version.
"""
from __future__ import annotations

import hashlib
import json

# (kind_id, name, category, data_in, control_out, semantics)
TABLE = (
    (0,  "NOP",    "halt_yield",  0, 1, "no effect; value 0; null element for knockout"),
    (1,  "HALT",   "halt_yield",  0, 0, "end this tick; next tick resumes at entry"),
    (2,  "YIELD",  "halt_yield",  0, 1, "end this tick; next tick resumes at this node's control successor"),
    (3,  "CONST",  "read_write",  0, 1, "value = params[0] (32-bit immediate)"),
    (4,  "ID",     "read_write",  1, 1, "value = in0 (a wire; the only way to persist or fan out a value)"),
    (5,  "LD",     "indirection", 1, 1, "value = state[in0 mod state_words]"),
    (6,  "ST",     "indirection", 2, 1, "state[in0 mod state_words] = in1; value = in1"),
    (7,  "ADD",    "arithmetic",  2, 1, "value = (in0 + in1) mod 2^32"),
    (8,  "SUB",    "arithmetic",  2, 1, "value = (in0 - in1) mod 2^32"),
    (9,  "MUL",    "arithmetic",  2, 1, "value = (in0 * in1) mod 2^32"),
    (10, "AND",    "logical",     2, 1, "value = in0 & in1"),
    (11, "OR",     "logical",     2, 1, "value = in0 | in1"),
    (12, "XOR",    "logical",     2, 1, "value = in0 ^ in1"),
    (13, "NOT",    "logical",     1, 1, "value = ~in0 mod 2^32"),
    (14, "SHL",    "logical",     2, 1, "value = (in0 << (in1 mod 32)) mod 2^32"),
    (15, "SHR",    "logical",     2, 1, "value = in0 >> (in1 mod 32)"),
    (16, "EQ",     "comparison",  2, 1, "value = 1 if in0 == in1 else 0"),
    (17, "LT",     "comparison",  2, 1, "value = 1 if in0 < in1 (unsigned) else 0"),
    (18, "ROUTE",  "control",     1, 2, "value = in0; control continues at port 0 if in0 != 0 else port 1"),
    (19, "CALL",   "control",     0, 2, "push the target of port 1 (after) on the bounded call stack; continue at port 0 (body); at depth limit continue at port 1 without pushing"),
    (20, "RETURN", "control",     0, 0, "pop the call stack and continue there; empty stack ends the tick (halt)"),
    (21, "IN",     "opaque_io",   1, 1, "value = next unread value on input channel (in0 mod n_in), or 0 if none"),
    (22, "INQ",    "opaque_io",   1, 1, "value = number of unread values on input channel (in0 mod n_in)"),
    (23, "OUT",    "opaque_io",   2, 1, "append in0 to output channel (in1 mod n_out); dropped beyond out_cap; value = in0"),
    (24, "RND",    "randomness",  0, 1, "value = next 32-bit value from the externally supplied random stream"),
)

N_KINDS = len(TABLE)
NAME = {row[0]: row[1] for row in TABLE}
KIND_OF = {row[1]: row[0] for row in TABLE}
CATEGORY = {row[0]: row[2] for row in TABLE}
DATA_IN = {row[0]: row[3] for row in TABLE}
CONTROL_OUT = {row[0]: row[4] for row in TABLE}
N_PARAMS = {k: (1 if k == 3 else 0) for k in NAME}          # only CONST carries an immediate
CATEGORIES = tuple(sorted(set(CATEGORY.values())))
assert CATEGORIES == ("arithmetic", "comparison", "control", "halt_yield", "indirection",
                      "logical", "opaque_io", "randomness", "read_write")

# Published storage bounds (manifest limits); config mutation steps inside these.
BOUNDS = {
    "n_nodes":        {"min": 1,  "max": 256},
    "state_words":    {"min": 4,  "max": 1024},
    "tick_budget":    {"min": 4,  "max": 4096},   # node executions per tick
    "out_cap":        {"min": 1,  "max": 64},
    "call_depth_max": {"min": 0,  "max": 16},
}


def canonical() -> str:
    return json.dumps({"table": TABLE, "bounds": BOUNDS, "params": N_PARAMS}, sort_keys=True,
                      separators=(",", ":"), ensure_ascii=True)


AFFORDANCE_HASH = hashlib.sha256(canonical().encode("utf-8")).hexdigest()
