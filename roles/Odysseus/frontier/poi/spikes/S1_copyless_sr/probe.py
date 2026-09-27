"""Spike S1 (POI frontier): are BEE coupling-campaign "competent self-replicators" that execute no copy
instruction actually replicators?

Background. roles/Bellerophon/coupling_2026-09-24/COUPLING_ORIGIN_LEDGER.jsonl lists 68 de novo "dominant competent
self-replicating tapes". 15 of them have arch.n_copy_ops == 0: run ONCE alone (input 42, zero window) they write
nothing. The world labels an organism a self-replicator by HOW IT WAS BORN (sr_depth > 0: its birth was a
self-replication event of its WRITER), not by what it can do (world.py _competence_summary).

Question. For each tape: (a) under ANY of the 256 input values, and with the window holding zeros, a copy of itself,
or random bytes, does the tape write >= 0.9*L bytes of its own tape into the window with its own code (the
repro_descriptor self_copy rule)? (b) How many single-byte edits (64 x 255) turn it into such a self-copier on
input 42 / zero window? Copy-bearing tapes are the control.

Stdlib only; uses the frozen VM at the commit this file ships with. Output: JSON to argv[1].
"""
import json
import os
import random
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
sys.path.insert(0, REPO)
from prometheus.z80atlas import vm  # noqa: E402

L, BUDGET = 64, 256
LEDGER = "roles/Bellerophon/coupling_2026-09-24/COUPLING_ORIGIN_LEDGER.jsonl"


def run(tape, inp, window):
    mem = bytearray(256)
    mem[:L] = tape
    mem[L:2 * L] = window
    mem[vm.IN_BASE] = inp
    tr = vm.execute(mem, L, 0, BUDGET, [inp], allow_copyall=False, trace_pcs=True, ldir="on", undefined="NOP")
    prov = tr.win_prov
    own = [(off, pc) for off, (src, pc, op) in prov.items() if off < L and op in vm.COPY_OPS and src is not None and src < L]
    own_code = sum(1 for _, pc in own if pc < L)
    child = bytes(mem[L:2 * L])
    fid = 1.0 - sum(1 for x, y in zip(child, tape) if x != y) / L
    self_copy = len(own) >= 0.9 * L and own_code >= 0.9 * max(1, len(own)) and fid >= 0.9
    copy_writes = sum(1 for (src, pc, op) in prov.values() if op in vm.COPY_OPS)
    return self_copy, len(prov), copy_writes, fid


def profile(tape, rng):
    windows = {"zero": bytes(L), "self": bytes(tape), "random": bytes(rng.randrange(256) for _ in range(L))}
    out = {}
    for wname, w in windows.items():
        sc = [i for i in range(256) if run(tape, i, w)[0]]
        writes = [run(tape, i, w)[1] for i in (0, 42, 128, 255)]
        out[wname] = {"self_copy_inputs": len(sc), "first_inputs": sc[:5], "window_writes_at_0_42_128_255": writes}
    return out


def one_edit_copiers(tape):
    n = 0
    for pos in range(L):
        orig = tape[pos]
        for b in range(256):
            if b == orig:
                continue
            t = bytearray(tape)
            t[pos] = b
            if run(bytes(t), 42, bytes(L))[0]:
                n += 1
    return n


def main(out_path):
    t0 = time.time()
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rows = [json.loads(l) for l in open(os.path.join(REPO, LEDGER), encoding="utf-8")]
    rng = random.Random(20260927)
    res = []
    for r in rows:
        tape = bytes.fromhex(r["tape"])
        copyless = not r["arch"].get("n_copy_ops")
        rec = {"run": r["run"], "arm": r["arm"], "K": r["K"], "copyless_by_ledger": copyless,
               "ledger_self_copy": r["arch"].get("self_copy"), "profile": profile(tape, rng)}
        rec["self_copy_any"] = any(v["self_copy_inputs"] for v in rec["profile"].values())
        if copyless:
            rec["one_edit_copiers"] = one_edit_copiers(tape)
        res.append(rec)
    json.dump({"commit": commit, "ledger": LEDGER, "n": len(res), "wall_s": round(time.time() - t0, 1), "rows": res},
              open(out_path, "w"), indent=1)
    cl = [x for x in res if x["copyless_by_ledger"]]
    ctl = [x for x in res if not x["copyless_by_ledger"]]
    print(json.dumps({
        "copyless": len(cl),
        "copyless_self_copy_any_input_or_window": sum(1 for x in cl if x["self_copy_any"]),
        "copyless_one_edit_copiers": sorted(x["one_edit_copiers"] for x in cl),
        "control": len(ctl),
        "control_self_copy_any": sum(1 for x in ctl if x["self_copy_any"]),
        "control_ledger_self_copy_true": sum(1 for x in ctl if x["ledger_self_copy"]),
        "wall_s": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
