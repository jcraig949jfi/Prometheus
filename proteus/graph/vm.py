"""The graph organism runtime (proteus.graph_organism.v1): manifest schema, validation, interpreter, meter.

Genome = nodes + edges. Structure IS connectivity:
    nodes[i]        {"kind": int, "params": [ints], "persist": bool}
    data_edges      [[src_node, dst_node, dst_port], ...]   at most one edge per (dst, port)
    control_edges   [[src_node, src_port, dst_node], ...]   at most one edge per (src, port)
    entry           the node executed first on a fresh tick
    limits          state_words, tick_budget (node executions per tick), out_cap, call_depth_max,
                    persist_state (does the state array survive tick boundaries)

Execution of one tick: start at `resume` (entry on a fresh state, or the successor of a YIELD);
each node reads its data inputs from the value table (0 when unconnected), executes, writes its
own value, and hands control to the edge on the selected control port; no edge -> the tick
ends with status "halt" and the next tick resumes at entry. `tick_budget` bounds node executions
per tick (status "budget"). Values of nodes with persist=false reset to 0 at every tick boundary;
persist=true values survive. The state array survives iff persist_state.

A node that is neither the entry nor the target of any control edge is DORMANT: it never runs
and costs nothing. Determinism: the only randomness is the externally supplied stream (RND).
The ABI a WORLD sees is unchanged from v0 (A1): run_tick(state, inputs, n_out, rng, meter) with
opaque integer channels -- W0..W7 run a graph organism without change.
"""
from __future__ import annotations

from .affordances import BOUNDS, CATEGORY, CONTROL_OUT, DATA_IN, N_KINDS, N_PARAMS, NAME

SCHEMA = "proteus.graph_manifest.v1"
MASK32 = (1 << 32) - 1
STATUSES = ("halt", "yield", "budget")

NOP, HALT, YIELD, CONST, ID, LD, ST, ADD, SUB, MUL, AND, OR, XOR, NOT, SHL, SHR, EQ, LT, ROUTE, CALL, RETURN, IN, INQ, OUT, RND = range(25)


def validate_manifest(m: dict) -> None:
    if m.get("schema_version") != SCHEMA:
        raise ValueError("graph manifest schema mismatch")
    nodes = m["nodes"]
    n = len(nodes)
    b = BOUNDS
    if not (b["n_nodes"]["min"] <= n <= b["n_nodes"]["max"]):
        raise ValueError("n_nodes outside bounds")
    for key in ("state_words", "tick_budget", "out_cap", "call_depth_max"):
        v = m[key]
        if not isinstance(v, int) or not (b[key]["min"] <= v <= b[key]["max"]):
            raise ValueError("%s outside bounds" % key)
    if not isinstance(m["persist_state"], bool):
        raise ValueError("persist_state must be bool")
    if not (isinstance(m["entry"], int) and 0 <= m["entry"] < n):
        raise ValueError("entry out of range")
    for i, nd in enumerate(nodes):
        k = nd["kind"]
        if not (isinstance(k, int) and 0 <= k < N_KINDS):
            raise ValueError("node %d kind out of table" % i)
        params = nd.get("params", [])
        if len(params) != N_PARAMS[k] or any(not isinstance(p, int) or not (0 <= p <= MASK32) for p in params):
            raise ValueError("node %d params invalid" % i)
        if not isinstance(nd.get("persist", False), bool):
            raise ValueError("node %d persist must be bool" % i)
        if set(nd.keys()) - {"kind", "params", "persist"}:
            raise ValueError("node %d has unknown keys" % i)
    seen = set()
    for e in m["data_edges"]:
        if len(e) != 3:
            raise ValueError("data edge arity")
        s, d, p = e
        if not (0 <= s < n and 0 <= d < n):
            raise ValueError("data edge node out of range")
        if not (0 <= p < DATA_IN[nodes[d]["kind"]]):
            raise ValueError("data edge port out of range for kind %s" % NAME[nodes[d]["kind"]])
        if (d, p) in seen:
            raise ValueError("two data edges into one port")
        seen.add((d, p))
    seen = set()
    for e in m["control_edges"]:
        if len(e) != 3:
            raise ValueError("control edge arity")
        s, p, d = e
        if not (0 <= s < n and 0 <= d < n):
            raise ValueError("control edge node out of range")
        if not (0 <= p < CONTROL_OUT[nodes[s]["kind"]]):
            raise ValueError("control edge port out of range for kind %s" % NAME[nodes[s]["kind"]])
        if (s, p) in seen:
            raise ValueError("two control edges out of one port")
        seen.add((s, p))
    extra = set(m.keys()) - {"schema_version", "nodes", "data_edges", "control_edges", "entry",
                             "state_words", "tick_budget", "out_cap", "call_depth_max", "persist_state"}
    if extra:
        raise ValueError("unknown manifest keys: %s" % sorted(extra))


def canonicalize(m: dict) -> dict:
    """The one canonical form an organism_id is taken over: edges sorted, params as lists,
    persist explicit. Two manifests with the same connectivity hash the same."""
    validate_manifest(m)
    return {
        "schema_version": m["schema_version"],
        "nodes": [{"kind": nd["kind"], "params": list(nd.get("params", [])), "persist": bool(nd.get("persist", False))}
                  for nd in m["nodes"]],
        "data_edges": sorted([list(e) for e in m["data_edges"]]),
        "control_edges": sorted([list(e) for e in m["control_edges"]]),
        "entry": m["entry"], "state_words": m["state_words"], "tick_budget": m["tick_budget"],
        "out_cap": m["out_cap"], "call_depth_max": m["call_depth_max"], "persist_state": m["persist_state"],
    }


def live_nodes(m: dict) -> set:
    """Nodes reachable by control edges from entry (static; the complement is dormant)."""
    succ = {}
    for s, _p, d in m["control_edges"]:
        succ.setdefault(s, []).append(d)
    seen, stack = set(), [m["entry"]]
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(succ.get(x, ()))
    return seen


class GraphMeter:
    """Resource vector + T0 behavioural fingerprint fields. NO timings (the 09-05 lesson: wall/cpu
    made the meter irreproducible 0/40); everything here is a deterministic count."""

    def __init__(self, n_nodes: int):
        self.ops = 0
        self.by_category = {}
        self.node_exec = [0] * n_nodes
        self.route_taken = {}          # node -> [port0 count, port1 count]
        self.call_depth_max_reached = 0
        self.call_depth_refused = 0
        self.in_reads = 0
        self.out_writes = 0
        self.out_dropped = 0
        self.rnd_draws = 0
        self.state_writes = 0
        self.state_addresses_written = set()
        self.ticks = 0
        self.budget_exhausted_ticks = 0
        self.statuses = {"halt": 0, "yield": 0, "budget": 0}

    def as_dict(self) -> dict:
        return {
            "ops": self.ops,
            "ops_by_category": dict(sorted(self.by_category.items())),
            "node_exec": list(self.node_exec),
            "nodes_executed": sum(1 for c in self.node_exec if c),
            "route_taken": {str(k): v for k, v in sorted(self.route_taken.items())},
            "call_depth_max_reached": self.call_depth_max_reached,
            "call_depth_refused": self.call_depth_refused,
            "in_reads": self.in_reads, "out_writes": self.out_writes, "out_dropped": self.out_dropped,
            "rnd_draws": self.rnd_draws,
            "state_writes": self.state_writes,
            "state_addresses_written": sorted(self.state_addresses_written),
            "ticks": self.ticks, "budget_exhausted_ticks": self.budget_exhausted_ticks,
            "statuses": dict(self.statuses),
        }


class GraphPlayer:
    """Interpreter bound to one graph manifest. State is passed in and mutated in place."""

    def __init__(self, manifest: dict):
        validate_manifest(manifest)
        self.m = manifest
        self.nodes = manifest["nodes"]
        self.n = len(self.nodes)
        self.kind = [nd["kind"] for nd in self.nodes]
        self.params = [nd.get("params", []) for nd in self.nodes]
        self.persist = [bool(nd.get("persist", False)) for nd in self.nodes]
        self.din = [[None] * DATA_IN[k] for k in self.kind]
        for s, d, p in manifest["data_edges"]:
            self.din[d][p] = s
        self.cout = [[None] * CONTROL_OUT[k] for k in self.kind]
        for s, p, d in manifest["control_edges"]:
            self.cout[s][p] = d
        self.entry = manifest["entry"]
        self.state_words = manifest["state_words"]
        self.tick_budget = manifest["tick_budget"]
        self.out_cap = manifest["out_cap"]
        self.call_depth_max = manifest["call_depth_max"]
        self.persist_state = manifest["persist_state"]
        self.dormant = sorted(set(range(self.n)) - live_nodes(manifest))

    def fresh_state(self) -> dict:
        return {"vals": [0] * self.n, "state": [0] * self.state_words, "resume": self.entry,
                "stack": [], "ticks": 0}

    def begin_tick(self, st: dict) -> None:
        if st["ticks"] == 0:
            return
        vals = st["vals"]
        for i in range(self.n):
            if not self.persist[i]:
                vals[i] = 0
        if not self.persist_state:
            st["state"] = [0] * self.state_words
        st["stack"] = []

    def run_tick(self, st: dict, inputs: list, n_out: int, rng, meter: GraphMeter | None = None,
                 budget: int | None = None):
        """One tick. Returns (outputs, status). Same ABI shape as the v0 Player (A1)."""
        self.begin_tick(st)
        vals, state, stack = st["vals"], st["state"], st["stack"]
        n_in = len(inputs)
        cursors = [0] * n_in
        outputs = [[] for _ in range(n_out)]
        cap = self.tick_budget if budget is None else min(budget, self.tick_budget)
        sw = self.state_words
        m = meter
        cur = st["resume"]
        status = "budget"
        ops = 0
        while ops < cap:
            k = self.kind[cur]
            ins = [vals[s] if s is not None else 0 for s in self.din[cur]]
            ops += 1
            if m is not None:
                m.node_exec[cur] += 1
                c = CATEGORY[k]
                m.by_category[c] = m.by_category.get(c, 0) + 1
            port = 0
            nxt = None
            if k == NOP:
                vals[cur] = 0
            elif k == HALT:
                status = "halt"; cur = self.entry; break
            elif k == YIELD:
                status = "yield"
                nxt = self.cout[cur][0]
                cur = nxt if nxt is not None else self.entry
                if nxt is None:
                    status = "halt"
                break
            elif k == CONST:
                vals[cur] = self.params[cur][0] & MASK32
            elif k == ID:
                vals[cur] = ins[0] & MASK32
            elif k == LD:
                vals[cur] = state[ins[0] % sw]
            elif k == ST:
                a = ins[0] % sw
                state[a] = ins[1] & MASK32
                vals[cur] = ins[1] & MASK32
                if m is not None:
                    m.state_writes += 1; m.state_addresses_written.add(a)
            elif k == ADD:
                vals[cur] = (ins[0] + ins[1]) & MASK32
            elif k == SUB:
                vals[cur] = (ins[0] - ins[1]) & MASK32
            elif k == MUL:
                vals[cur] = (ins[0] * ins[1]) & MASK32
            elif k == AND:
                vals[cur] = ins[0] & ins[1]
            elif k == OR:
                vals[cur] = ins[0] | ins[1]
            elif k == XOR:
                vals[cur] = ins[0] ^ ins[1]
            elif k == NOT:
                vals[cur] = (~ins[0]) & MASK32
            elif k == SHL:
                vals[cur] = (ins[0] << (ins[1] % 32)) & MASK32
            elif k == SHR:
                vals[cur] = ins[0] >> (ins[1] % 32)
            elif k == EQ:
                vals[cur] = 1 if ins[0] == ins[1] else 0
            elif k == LT:
                vals[cur] = 1 if ins[0] < ins[1] else 0
            elif k == ROUTE:
                vals[cur] = ins[0]
                port = 0 if ins[0] != 0 else 1
                if m is not None:
                    r = m.route_taken.setdefault(cur, [0, 0]); r[port] += 1
            elif k == CALL:
                after = self.cout[cur][1]
                if len(stack) < self.call_depth_max:
                    stack.append(after)
                    port = 0
                    if m is not None:
                        m.call_depth_max_reached = max(m.call_depth_max_reached, len(stack))
                else:
                    port = 1
                    if m is not None:
                        m.call_depth_refused += 1
            elif k == RETURN:
                if stack:
                    nxt = stack.pop()
                    if nxt is None:
                        status = "halt"; cur = self.entry; break
                    cur = nxt
                    continue
                status = "halt"; cur = self.entry; break
            elif k == IN:
                if n_in:
                    ch = ins[0] % n_in
                    src = inputs[ch]
                    if cursors[ch] < len(src):
                        vals[cur] = src[cursors[ch]] & MASK32
                        cursors[ch] += 1
                        if m is not None:
                            m.in_reads += 1
                    else:
                        vals[cur] = 0
                else:
                    vals[cur] = 0
            elif k == INQ:
                vals[cur] = (len(inputs[ins[0] % n_in]) - cursors[ins[0] % n_in]) if n_in else 0
            elif k == OUT:
                vals[cur] = ins[0] & MASK32
                if n_out:
                    dst = outputs[ins[1] % n_out]
                    if len(dst) < self.out_cap:
                        dst.append(vals[cur])
                        if m is not None:
                            m.out_writes += 1
                    elif m is not None:
                        m.out_dropped += 1
            elif k == RND:
                vals[cur] = rng.next_u32() & MASK32
                if m is not None:
                    m.rnd_draws += 1
            nxt = self.cout[cur][port] if self.cout[cur] else None
            if nxt is None:
                status = "halt"; cur = self.entry; break
            cur = nxt
        if status == "budget":
            cur = self.entry
            if m is not None:
                m.budget_exhausted_ticks += 1
        st["resume"] = cur
        if m is not None:
            m.ops += ops
            m.ticks += 1
            m.statuses[status] += 1
        return outputs, status
