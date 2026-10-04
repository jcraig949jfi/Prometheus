"""Producer adapter: finite-world executions and ruler/gate outcomes -> producer receipts (C-004-T016).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0 (draft A A3 runtime boundary; draft B B3 receipt) with
AMENDMENT_v1.0.1.md (V1 node ids, V2 trace roles); NEXT_ROUND_PLAN_v0.4 s3 Receipt; closure review F (one
finite transition fixture with a producer/consumer receipt boundary and a small adapter).

The adapter is the producer side of the boundary. It runs lives of world W-S1 (rso/slice001/world.py) on a
runtime, writes the output traces in exactly the consumer's byte layout (checker.TRACE_LAYOUT, FD-T015-1:
written through checker.make_trace, which validates what it writes), and wraps one ruler/gate outcome into a
producer receipt that records code, input and output identities, execution status and resources. It never
computes, edits or qualifies an outcome: the outcome is whatever the ruler/gate callable returned, verbatim,
and a producer receipt has no authority field (FD-B1). The consumer sees only receipt bytes and trace bytes.

Not here: rulers, gates and reset predicates (T011, T012), the traces of roles with no recomputation layout
(trace:deliveries, trace:capture, trace:observer; a caller passes their bytes in `extra_traces`), and any
universal runtime adapter (plan s1). Which outcome is true is never decided here.

Python >= 3.8, standard library only.
"""
import copy
import hashlib
import math
import os
import time

from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001 import world as W

ALL_RESETS = frozenset(range(1, W.EPISODES))
NAME_TO_ID = {n: p for p, n in R.PREDICATE_NAMES}
LIMITATIONS = ("draft A A7: what the registered model does not contain is not tested",
               "draft B B5.4: a receipt shows what was recorded, never that execution happened")


# --------------------------------------------------------------------------------------------------------
# World runs -> trace runs in the checker's layout (FD-T015-1)

def _clamp_hook(make, j, v):
    """At boundary j (after its reset, if any): capture, set a := v, restore into a fresh instance (A5 P5)."""
    def hook(rt, point):
        if point != ("RESET", j):
            return rt
        c = rt.capture()
        c["a"] = v
        fresh = make()
        fresh.restore(c)
        return fresh
    return hook


def world_runs(make, variant="STANDARD"):
    """{role: {run key: digit string}} for every layout role, from world.run_life over the whole domain.

    trace:probe_a  RESET (every reset) and SKIP1..SKIP3 (the reset at boundary j alone left out);
                   per episode y_A then the PROBE_A display.
    trace:probe_d  RESET; y_D per episode.
    trace:sends    RESET; per episode two slots "<bit><k>" or "--".
    trace:clamp    CLAMP; y_A at PROBE_A of episode j+1 after the clamp at j, for j = 1..3, v = 0, 1.
    Raises world.BoundsViolation if the runtime leaves the registered model.
    """
    hs = W.histories()
    reset = [W.run_life(make, h, variant) for h in hs]
    pa = {"RESET": "".join("%d%d" % life.probe_a(e) for life in reset for e in range(1, W.EPISODES + 1))}
    for j in W.BOUNDARIES:
        lives = (W.run_life(make, h, variant, reset_at=ALL_RESETS - {j}) for h in hs)
        pa["SKIP%d" % j] = "".join("%d%d" % life.probe_a(e) for life in lives for e in range(1, W.EPISODES + 1))
    pd = "".join("%d" % life.probe_d(e) for life in reset for e in range(1, W.EPISODES + 1))
    sends = "".join("".join("%d%d" % s for s in life.sends(e)) + "--" * (W.S - len(life.sends(e)))
                    for life in reset for e in range(1, W.EPISODES + 1))
    clamp = "".join("%d" % W.run_life(make, h, variant, hook=_clamp_hook(make, j, v)).probe_a(j + 1)[0]
                    for h in hs for j in W.BOUNDARIES for v in (0, 1))
    return {"trace:probe_a": pa, "trace:probe_d": {"RESET": pd}, "trace:sends": {"RESET": sends},
            "trace:clamp": {"CLAMP": clamp}}


def traces_from_runs(runs):
    """Canonical trace bytes per role (checker.make_trace validates the layout as it writes)."""
    return {role: C.make_trace(role, r) for role, r in sorted(runs.items())}


def world_traces(make, variant="STANDARD"):
    return traces_from_runs(world_runs(make, variant))


# --------------------------------------------------------------------------------------------------------
# Identities

def file_code_ref(path, commit, root):
    """A CodeRef for a repository text file: sha256 and length of its LF-normalised bytes (= the git blob)."""
    with open(os.path.join(root, *path.split("/")), "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return {"role": "code:" + path, "sha256": hashlib.sha256(data).hexdigest(), "length": len(data),
            "commit": commit}


def _artifact(role, data):
    return {"role": role, "sha256": hashlib.sha256(data).hexdigest(), "length": len(data)}


DOMAIN_BYTES = ("W-S1 domain: %d histories, bits MSB first (u_1, f_1, ..., u_6, f_6)" % W.HISTORIES).encode()


class Identity(object):
    """What the producer records about where a receipt came from. Every field is supplied by the caller
    (the registered cell, the subject's code, the build); the adapter adds only measured values."""

    def __init__(self, registration_ref, contract_ref, cell, subject, world_code, producer_code, code_state,
                 expected_table, reset_model=None, oracle=None):
        if "measurement" in cell:
            raise ValueError("cell.measurement is the predicate version; the adapter derives it")
        self.registration_ref = dict(registration_ref)
        self.contract_ref = dict(contract_ref)
        self.cell = dict(cell)
        self.subject = copy.deepcopy(subject)
        self.world_code = copy.deepcopy(world_code)
        self.producer_code = copy.deepcopy(producer_code)
        self.code_state = dict(code_state)
        self.expected_table = dict(expected_table)
        model = reset_model if reset_model is not None else {
            "episodes": W.EPISODES, "boundaries": list(W.BOUNDARIES), "H": W.H, "K": W.K, "S": W.S, "Q": W.Q}
        self.reset_model_sha256 = R.sha256_hex(model)
        self.oracle = oracle


def _oracle_ref(variant):
    data = R.canonical_bytes([[W.truth(h, variant)["retained"][j] for j in W.BOUNDARIES] for h in W.histories()])
    return _artifact("oracle", data)


# --------------------------------------------------------------------------------------------------------
# Receipt

def _utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def make_receipt(identity, name, evaluate, predicate_code, run_id, make=None, runs=None, variant="STANDARD",
                 observer=None, extra_traces=None, created_at_utc=None):
    """One producer receipt and the trace bytes it binds: (Receipt, {role: bytes}).

    `runs` (from world_runs) or `make` (a runtime factory, run here) supplies the execution. `evaluate(runs)`
    is the ruler/gate: its return value is the receipt's outcome, unchanged. If the runtime leaves the
    registered model the receipt is BLOCKED (missing BOUNDS_VIOLATION:<bound>), carries no outcome and no
    traces, and `evaluate` is never called. The receipt is validated (receipt.Receipt) before it is returned.
    """
    if name not in NAME_TO_ID:
        raise ValueError("unknown predicate name %r" % (name,))
    pid = NAME_TO_ID[name]
    node_id = R.make_node_id(identity.subject["id"], name, variant, observer=observer)
    c0, w0 = time.process_time(), time.perf_counter()
    execution, outcome, traces = {"status": "RAN", "missing": [], "run_id": run_id}, None, {}
    try:
        if runs is None:
            runs = world_runs(make, variant)
    except W.BoundsViolation as e:
        execution = {"status": "BLOCKED", "missing": ["BOUNDS_VIOLATION:%s" % e.bound], "run_id": run_id}
    if execution["status"] == "RAN":
        roles = C.RECOMPUTE_ROLES.get(name, ())
        traces = traces_from_runs({role: runs[role] for role in roles})
        traces.update(extra_traces or {})
        outcome = copy.deepcopy(evaluate(runs))
    cell = dict(identity.cell, measurement=EV.predicate_version(predicate_code))
    d = {
        "schema": R.SCHEMA, "node_id": node_id,
        "registration_ref": identity.registration_ref, "contract_ref": identity.contract_ref,
        "cell": cell,
        "subject": identity.subject,
        "observer": None if observer is None else {"id": observer, "code": identity.subject["code"]},
        "world": {"variant": variant, "code": identity.world_code},
        "predicate": {"id": pid, "kind": R.PREDICATE_KINDS[pid], "code": copy.deepcopy(predicate_code)},
        "code": dict(identity.code_state, producer=identity.producer_code),
        "inputs": {"domain": _artifact("domain", DOMAIN_BYTES),
                   "reset_model_sha256": identity.reset_model_sha256},
        "outputs": [_artifact(role, traces[role]) for role in sorted(traces)],
        "oracle": identity.oracle if identity.oracle is not None else _oracle_ref(variant),
        "expected_answer": {"table": identity.expected_table, "row_id": node_id},
        "dependencies": sorted(EV.required_deps(node_id)),
        "execution": execution,
        "outcome": outcome,
        "resources": {"cpu_seconds": int(math.ceil(time.process_time() - c0)),
                      "wall_seconds": int(math.ceil(time.perf_counter() - w0)), "launches": 1,
                      "artifact_bytes": sum(len(b) for b in traces.values())},
        "limitations": list(LIMITATIONS),
        "created_at_utc": created_at_utc or _utc_now(),
    }
    return R.Receipt.from_dict(d), traces
