"""L3 -- BEE "competent" / "verified exact solver". Label spec + runner.

WHY THIS LABEL. It is the other half of the coupling campaign's primary endpoint ("de novo competent SELF-REPLICATING
tape"): S1 and L1 recertify the self-replicator half; this recertifies the competence half, on the same 68 origin-ledger
tapes plus every verified exact solver in the 12,130-run grounding round (summary.verified.exact_tapes, 835 distinct
tape x task). It also feeds G3's "endogenous causal advantage" and every task_reached flag.

WHAT THE LABEL IS (provenance): tasks.verify_tape -- the tape ALONE, EMPTY neighbour window, the 16 fixed panel inputs
(tasks._PANEL_1), each answered exactly under the run's read gate (coupling.Competence.of / world._verified). Note that
verify_tape runs the default chemistry (ldir on, undefined NOP) whatever the run's chemistry was.

CLAIMED PROPERTY: the tape computes the task function f on its input domain, not only on the 16 panel points, and does
so with something other than zeros in the neighbour window (in the world, the window always holds a neighbour or the
target's old bytes). Environments: all 256 inputs with an empty window (for SUM2: 256 seeded input pairs), plus 32
inputs x 3 other windows (random, random, a copy of the tape); the run's own chemistry.
EXPECTED MECHANISM (input-dependent tasks): the answer is computed from the input READ THROUGH THE IN PORT (the read
the FORCED gate and the anticheat account for). Intervention: NOP the IN instructions actually executed (operand bytes
untouched); the mechanism predicts accuracy collapses. Accuracy that survives the knockout means the input is reached
another way (e.g. LD A,(S) at 0xE0 -- the input region read as memory, invisible to first_in_step). For CONST the
expected mechanism is input-independence: do(input) must not change the answer (then the knockout is n/a).
STRUCTURE: passes the 16-input panel now (the certificate, recomputed) and carries IN (0x40) and OUT (0x41) bytes.

    python3 l3_bee_solver.py [--workers 4]      -> L3_rows.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recert as R  # noqa: E402
import bee_engine as E  # noqa: E402
from bee_engine import vm  # noqa: E402
from prometheus.z80atlas import tasks as TK  # noqa: E402

OTHER_WINDOWS = ("rand1", "rand2", "self")
N_OTHER = 32
KO_MAX = 0.5          # knockout accuracy must fall below this share of the intact accuracy for the IN-port mechanism


def _seed(*parts) -> int:
    return int(hashlib.sha256(repr(parts).encode()).hexdigest()[:12], 16)


def window_bytes(kind, tape, L):
    if kind == "zero":
        return bytes(L)
    if kind == "self":
        return bytes(tape[:L])
    r = random.Random(_seed("win", kind, L))
    return bytes(r.randrange(256) for _ in range(L))


class Obj:
    __slots__ = ("oid", "tape", "s", "task", "prov", "labelled")

    def __init__(self, oid, tape, s, task, prov, labelled=True):
        self.oid, self.tape, self.s, self.task, self.prov, self.labelled = oid, tape, s, task, prov, labelled


def _inputs(task, i):
    if task.kind == "SUM2":
        r = random.Random(_seed("sum2", i))
        return [r.randrange(256), r.randrange(256)]
    return [i]


def answer_ok(tape, s, task, xs, win, trace=False):
    _, tr = E.execute(tape, s, xs, win, trace_pcs=trace)
    sc = TK.score(task, tr.outputs, task.expected(xs), "ATOMIC", s["read_gate"], tr.first_out_step, tr.first_in_step)
    return sc >= 0.999, tr


def environments(o):
    envs = [{"i": i, "w": "zero"} for i in range(256)]
    r = random.Random(_seed("other", o.oid))
    for w in OTHER_WINDOWS:
        envs += [{"i": i, "w": w} for i in sorted(r.sample(range(256), N_OTHER))]
    return envs


def behavioural(o, env):
    ok, _ = answer_ok(o.tape, o.s, o.task, _inputs(o.task, env["i"]), window_bytes(env["w"], o.tape, o.s["L"]))
    return {"pass": ok}


def structural(o):
    L = o.s["L"]
    v = TK.verify_tape(o.tape, L, o.task, o.s["read_gate"], o.s["budget"], o.s["layout"], o.s["allow_copyall"])
    t = o.tape[:L]
    return {"ok": bool(v["exact"]) and vm.IN_A in t and vm.OUT_A in t, "panel_exact_now": bool(v["exact"]),
            "panel_accuracy_now": v["accuracy"], "has_IN": vm.IN_A in t, "has_OUT": vm.OUT_A in t, "task": o.task.to_dict()}


def causal(o, beh):
    allr = beh["_all"]
    zero = [rr["pass"] for e, rr in allr if e["w"] == "zero"]
    by_w = {}
    for e, rr in allr:
        by_w.setdefault(e["w"], []).append(rr["pass"])
    acc = {w: round(sum(v) / len(v), 4) for w, v in by_w.items()}
    base = {"accuracy_by_window": acc, "accuracy_all_inputs_zero_window": acc.get("zero"),
            "panel_inputs_only": o.task.kind != "SUM2" and all(zero[i] for i in TK._PANEL_1) and sum(zero) < 256}
    if not any(zero):
        return dict(base, ok=None, why="no behaviour to intervene on")
    L = o.s["L"]
    if o.task.kind == "CONST":
        outs = set()
        for i in range(0, 256, 17):
            _, tr = E.execute(o.tape, o.s, _inputs(o.task, i), bytes(L))
            outs.add(tuple(tr.outputs[:1]))
        return dict(base, ok=len(outs) == 1, mechanism="input-independent constant", distinct_first_outputs=len(outs))
    # IN-port knockout at the executed IN positions (collected over the inputs the tape answers)
    pos = set()
    for i in [k for k in range(256) if zero[k]][:32]:
        _, tr = E.execute(o.tape, o.s, _inputs(o.task, i), bytes(L))
        pos |= {pc for pc in (tr.pcs or ()) if pc < L and o.tape[pc] == vm.IN_A}
    t = bytearray(o.tape[:L])
    for pc in pos:
        t[pc] = vm.NOP
    ko_in = list(range(0, 256, 4))                  # 64 inputs
    ko = [answer_ok(bytes(t), o.s, o.task, _inputs(o.task, i), bytes(L))[0] for i in ko_in]
    intact = sum(zero[i] for i in ko_in) / len(ko_in)
    ko_acc = sum(ko) / len(ko_in)
    # input reached as memory? (reads of the input region by LD A,(S)/(T) are not visible in the trace; infer from knockout)
    return dict(base, ok=bool(pos) and ko_acc < KO_MAX * intact, executed_IN_positions=sorted(pos),
                accuracy_after_IN_knockout=round(ko_acc, 4), mechanism="IN-port read" if pos else "no IN executed")


LABEL = R.Label(
    name="BEE competent / verified exact solver (16-input panel)",
    claimed_property="computes the configured task f on the input domain (all 256 inputs / 256 input pairs) and with "
                     "non-empty neighbour windows, in the run's chemistry",
    expected_mechanism="answer computed from the input read through the IN port (executed-IN knockout collapses "
                       "accuracy); CONST: answer invariant to the input",
    provenance=lambda o: o.prov, structural=structural, environments=environments, behavioural=behavioural,
    causal=causal, obj_id=lambda o: o.oid, labelled=lambda o: o.labelled, min_rate=0.9,
    notes={"env": "256 inputs x zero window + 32 inputs x (rand1, rand2, self)", "KO_MAX": KO_MAX,
           "min_rate_note": "a solver is expected to be right almost everywhere; 0.9 of 352 environments"})


def load_grounding():
    groups = {}
    for r, cfg in E.grounding_runs():
        v = r["summary"].get("verified") or {}
        for t in v.get("exact_tapes") or []:
            s = E.sig(cfg)
            key = (t, v["task"]["kind"], v["task"]["k"], json.dumps(s, sort_keys=True))
            g = groups.setdefault(key, {"runs": [], "s": s, "task": v["task"], "rg": v.get("read_gate")})
            g["runs"].append((r["id"], r["lane"], r["cell"]))
    objs = []
    for (t, kind, k, sj), g in groups.items():
        prov = {"label_then": "verified exact solver (summary.verified.exact_tapes)", "n_runs": len(g["runs"]),
                "runs": [x[0] for x in g["runs"]][:6], "lanes": sorted({x[1] for x in g["runs"]}),
                "cells": sorted({x[2] for x in g["runs"]})[:6], "task": g["task"], "read_gate": g["rg"],
                "chemistry": {"ldir": g["s"]["ldir"], "undefined": g["s"]["undefined"], "layout": g["s"]["layout"]}}
        oid = "G:" + hashlib.sha256("|".join((t, kind, str(k), sj)).encode()).hexdigest()[:12]
        objs.append(Obj(oid, bytes.fromhex(t), g["s"], TK.Task(kind, k=k), prov))
    objs.sort(key=lambda o: o.oid)
    return objs


def load_coupling():
    from prometheus.z80atlas.world import World
    objs = []
    for r, cfg, p in E.coupling_runs():
        task = World(cfg, p["seed"]).configured_task()
        prov = {"label_then": "competent (coupling origin ledger: dominant competent SR tape)", "run": r["run"],
                "arm": r["arm"], "K": r["K"], "lane": r["lane"], "task": task.to_dict(),
                "ledger_task_accuracy_then": r["arch"].get("task_accuracy"), "auto_verdict_then": r.get("auto_verdict")}
        objs.append(Obj("C:" + r["run"], bytes.fromhex(r["tape"]), E.sig(cfg), TK.Task(task.kind, k=task.k), prov))
    return objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "L3_rows.json"))
    a = ap.parse_args()
    t0 = time.time()
    oc = load_coupling()
    og = load_grounding()
    if a.limit:
        og = og[:a.limit]
    print("L3: %d grounding solvers, %d coupling competent tapes" % (len(og), len(oc)), flush=True)
    rc = R.run(LABEL, oc, a.workers)
    rg = R.run(LABEL, og, a.workers)
    extra = {"summary_grounding": R.summarise(rg, lambda r: ",".join(r["then"]["lanes"]) + "|" + r["then"]["task"]["kind"]),
             "summary_coupling": R.summarise(rc, lambda r: r["then"]["arm"] + "|" + r["then"]["task"]["kind"]),
             "wall_s": round(time.time() - t0, 1)}
    R.write(a.out, LABEL, rg + rc, extra)
    print(json.dumps(extra, indent=1))


if __name__ == "__main__":
    main()
