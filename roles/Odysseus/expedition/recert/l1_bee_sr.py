"""L1 -- BEE "self-replicator" (sr_depth > 0; the run's dominant_sr_tape). Label spec + runner.

WHAT THE LABEL IS (provenance): the world gives an organism sr_depth > 0 when ITS BIRTH was a self-replication event of
its WRITER (prometheus/z80atlas/world.py:543 + _is_self_copy :576). summary.dominant_sr_tape is the most common living
tape with sr_depth > 0 (world.py:885). The label is therefore a birth record; nothing re-tests the organism itself.

CLAIMED PROPERTY: the tape, executed as the world executes it, writes a copy of itself (>= 0.9 L bytes written into the
neighbour window and not moved there from the window itself, window ends >= 0.9 identical to the tape) -- in more than one input / window context.
EXPECTED MECHANISM: template-directed copying -- the child's bytes are caused by the parent's bytes. Intervention:
do(tape[p] := b) for every position p (2 random b each); the copy mechanism predicts child[p] == b. A painter (code that
writes a fixed byte pattern that happens to resemble the tape) predicts child[p] unchanged. Transmission T = share of
(p, b) edits carried into the child. Mechanism OK iff T >= 0.5. INFORMATION: bits_transmitted = 8 x positions carried in
both draws (a homopolymer painter carries ~0 bits); the tape's own content (dominant-byte share, entropy) is reported
beside it. Descriptor (not verdict-bearing): knock out the EXECUTED copy-op positions -> does the behaviour vanish?
STRUCTURE: the tape contains a copy-op byte (LDI / LDIR, + COPYALL where the representation has it).

    python3 l1_bee_sr.py [--limit N] [--workers 4]      -> L1_rows.json
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

INPUTS = (0, 42, 128, 255, 7, 99, 173, 230)
WINDOWS = ("zero", "self", "rand1", "rand2")
T_MIN = 0.5


def _seed(*parts) -> int:
    return int(hashlib.sha256(repr(parts).encode()).hexdigest()[:12], 16)


def window_bytes(kind: str, tape: bytes, L: int) -> bytes:
    if kind == "zero":
        return bytes(L)
    if kind == "self":
        return bytes(tape[:L])
    if kind == "ff":
        return bytes([0xFF]) * L
    r = random.Random(_seed("win", kind, L))
    return bytes(r.randrange(256) for _ in range(L))


def reproduce(tape: bytes, s: dict, x, win: bytes):
    """Functional self-reproduction test + the world's own (copy-op provenance) self_copy rule, one execution."""
    L = s["L"]
    mem, tr = E.execute(tape, s, x, win)
    child = bytes(mem[L:2 * L])
    written = {a - L for a in tr.writes if L <= a < 2 * L}
    # bytes whose last write was a move FROM the window itself (the in-place sweep, M2) do not count as produced
    swept = sum(1 for off, (src, pc, op) in tr.win_prov.items() if off < L and src is not None and L <= src < 2 * L)
    fid = R.fidelity(child, tape[:L])
    functional = len(written) - swept >= 0.9 * L and fid >= 0.9
    own = [pc for off, (src, pc, op) in tr.win_prov.items() if off < L and op in vm.COPY_OPS and src is not None and src < L]
    world_rule = len(own) >= 0.9 * L and sum(1 for pc in own if pc < L) >= 0.9 * max(1, len(own)) and fid >= 0.9
    return functional, world_rule, child, tr, len(written), fid


class Obj:
    __slots__ = ("oid", "tape", "s", "prov", "labelled")

    def __init__(self, oid, tape, s, prov, labelled=True):
        self.oid, self.tape, self.s, self.prov, self.labelled = oid, tape, s, prov, labelled


def environments(o):
    return [{"x": x, "w": w} for w in WINDOWS for x in INPUTS]


def behavioural(o, env):
    win = window_bytes(env["w"], o.tape, o.s["L"])
    f, wr, _, _, nw, fid = reproduce(o.tape, o.s, env["x"], win)
    return {"pass": f, "world_rule": wr, "written": nw, "fid": round(fid, 3)}


def structural(o):
    ops = E.copy_ops(o.s)
    t = o.tape[:o.s["L"]]
    return {"ok": any(b in ops for b in t), "n_copy_op_bytes": sum(1 for b in t if b in ops),
            "dominant_byte_share": round(R.dominant_share(t), 4), "entropy_bits_per_byte": round(R.entropy_bits(t), 3),
            "nonzero_bytes": sum(1 for b in t if b)}


def causal(o, beh):
    envs = [e for e, r in beh["_all"] if r["pass"]]
    world_rule_rate = round(sum(1 for _, r in beh["_all"] if r["world_rule"]) / max(1, len(beh["_all"])), 4)
    if not envs:
        return {"ok": None, "why": "no behaviour to intervene on", "world_rule_rate": world_rule_rate}
    env = next((e for e in envs if e["w"] == "zero" and e["x"] == 42), next((e for e in envs if e["w"] != "self"), envs[0]))
    L = o.s["L"]
    win = window_bytes(env["w"], o.tape, L)        # built from the ORIGINAL tape: an unwritten byte cannot fake transmission
    rng = random.Random(_seed("T", o.oid))
    carried = [0] * L
    n = 0
    for p in range(L):
        for _ in range(2):
            b = rng.randrange(255)
            b = b if b < o.tape[p] else b + 1
            t = bytearray(o.tape[:L]); t[p] = b
            _, _, child, _, _, _ = reproduce(bytes(t), o.s, env["x"], win)
            carried[p] += child[p] == b
            n += 1
    T = sum(carried) / n
    bits = 8 * sum(1 for c in carried if c == 2)
    # descriptor: knock out the copy-op positions EXECUTED in the chosen environment (operand bytes untouched)
    _, _, _, tr, _, _ = reproduce(o.tape, o.s, env["x"], win)
    ops = E.copy_ops(o.s)
    ko_pos = sorted(pc for pc in (tr.pcs or ()) if pc < L and o.tape[pc] in ops)
    ko_rate = None
    if ko_pos:
        t = bytearray(o.tape[:L])
        for pc in ko_pos:
            t[pc] = vm.NOP
        ko = [reproduce(bytes(t), o.s, e["x"], window_bytes(e["w"], o.tape, L))[0] for e in environments(o)]
        ko_rate = round(sum(ko) / len(ko), 4)
    return {"ok": T >= T_MIN, "intervention_env": env, "transmission": round(T, 4), "bits_transmitted": bits,
            "homopolymer_bits": 0, "info_above_homopolymer": bits > 0,
            "executed_copy_op_positions": ko_pos, "behaviour_after_copy_op_knockout": ko_rate,
            "world_rule_rate": world_rule_rate}


LABEL = R.Label(
    name="BEE self-replicator (sr_depth>0, dominant_sr_tape)",
    claimed_property="executed as the world executes it, the tape writes a >=0.9-fidelity copy of itself (>=0.9 L bytes "
                     "written) into the neighbour window, across inputs and window contents",
    expected_mechanism="template-directed copying: do(tape[p]=b) -> child[p]=b for >= 50% of edits",
    provenance=lambda o: o.prov, structural=structural, environments=environments, behavioural=behavioural,
    causal=causal, obj_id=lambda o: o.oid, labelled=lambda o: o.labelled, min_rate=0.5,
    notes={"inputs": INPUTS, "windows": WINDOWS, "T_min": T_MIN})


def load_grounding(limit=None):
    groups = {}
    for r, cfg in E.grounding_runs():
        t = r.get("dominant_sr_tape")
        if not t:
            continue
        s = E.sig(cfg)
        key = (t, json.dumps(s, sort_keys=True))
        g = groups.setdefault(key, {"runs": [], "s": s})
        d = r.get("dominant_sr_descriptor") or {}
        g["runs"].append({"id": r["id"], "lane": r["lane"], "cell": r["cell"], "sr_max_depth": r["summary"]["sr_max_depth"],
                          "descriptor_self_copy_then": d.get("self_copy"), "spontaneous": r.get("spontaneous")})
    objs = []
    for (t, _), g in groups.items():
        runs = g["runs"]
        prov = {"label_then": "dominant self-replicating tape (sr_depth>0)", "n_runs": len(runs),
                "lanes": sorted({x["lane"] for x in runs}), "cells": sorted({x["cell"] for x in runs})[:6],
                "runs": [x["id"] for x in runs][:6],
                "descriptor_self_copy_then": sorted({str(x["descriptor_self_copy_then"]) for x in runs}),
                "sr_max_depth_max": max(x["sr_max_depth"] for x in runs), "any_spontaneous": any(x["spontaneous"] for x in runs),
                "representation": g["s"]["representation"], "reproduction": g["s"]["reproduction"],
                "chemistry": {"ldir": g["s"]["ldir"], "undefined": g["s"]["undefined"], "layout": g["s"]["layout"]}}
        oid = "G:" + hashlib.sha256((t + json.dumps(g["s"], sort_keys=True)).encode()).hexdigest()[:12]
        objs.append(Obj(oid, bytes.fromhex(t), g["s"], prov))
    objs.sort(key=lambda o: o.oid)
    return objs[:limit] if limit else objs


def load_coupling():
    objs = []
    for r, cfg, p in E.coupling_runs():
        s = E.sig(cfg)
        prov = {"label_then": "de novo dominant competent self-replicating tape (coupling origin ledger)", "run": r["run"],
                "arm": r["arm"], "K": r["K"], "lane": r["lane"], "ledger_self_copy_then": r["arch"].get("self_copy"),
                "ledger_n_copy_ops": r["arch"].get("n_copy_ops"), "auto_verdict_then": r.get("auto_verdict")}
        objs.append(Obj("C:" + r["run"], bytes.fromhex(r["tape"]), s, prov))
    return objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(HERE, "L1_rows.json"))
    a = ap.parse_args()
    t0 = time.time()
    objs_c = load_coupling()
    objs_g = load_grounding(a.limit)
    print("L1: %d grounding objects (distinct tape x chemistry), %d coupling (S1 set)" % (len(objs_g), len(objs_c)), flush=True)
    rows_c = R.run(LABEL, objs_c, a.workers)
    rows_g = R.run(LABEL, objs_g, a.workers)
    rows = rows_g + rows_c
    extra = {"summary_grounding": R.summarise(rows_g, lambda r: ",".join(r["then"]["lanes"])),
             "summary_coupling_S1set": R.summarise(rows_c, lambda r: r["then"]["arm"]),
             "wall_s": round(time.time() - t0, 1)}
    R.write(a.out, LABEL, rows, extra)
    print(json.dumps({k: v for k, v in extra.items()}, indent=1))


if __name__ == "__main__":
    main()
