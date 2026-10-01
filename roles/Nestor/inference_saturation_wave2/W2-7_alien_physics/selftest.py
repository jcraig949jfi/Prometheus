"""W2-7 self-tests. Must pass before any probe number is trusted.   python -B selftest.py -> SELFTEST.json

T1  DENSE (this folder's injection, with the rd/rdd split) == run_dc.dense_z8() bit for bit: memory, provenance,
    registers, flags, returned pc and every telemetry counter, over random single-context executions.
T2  every VM variant == DENSE bit for bit on every execution where its modification did not fire (_HITS == 0);
    and the modification is LIVE (some executions with hits > 0 differ).
T3  alien_pair.assay(DENSE, layout={}, early=False) == p11.assay(run_dc dense) draw for draw; early=True gives the
    same verdict.
T4  alien_pair.competent(DENSE) == run_de.competent (via forensics/fsetup) verdict for verdict on the 128-genome
    competent panel, 38 panel non-competents, the 3 known random-genome passes and 150 random genomes.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))

import alien_vm  # noqa: E402
import alien_pair as AP  # noqa: E402
import fsetup as F  # noqa: E402  (read-only; constructs runners, never runs a world)
import p11  # noqa: E402

T0 = time.process_time()
OUT = HERE / "SELFTEST.json"
REF = F.DENSE                 # run_dc.dense_z8()
rng = random.Random(7072026)
res = {}


def panel():
    d = json.loads((FOR / "core_map.json").read_text())
    comp = [bytes.fromhex(r["hex"]) for r in d["rows"] if r["vm"] == "DENSE" and str(r["competent"]) == "True"]
    non = [bytes.fromhex(r["hex"]) for r in d["rows"] if r["vm"] == "DENSE" and str(r["competent"]) != "True"]
    mp = json.loads((FOR / "minimal_prior.json").read_text())
    known = [bytes.fromhex(h) for k in ("P1R", "P2R", "P3R") for h in mp[k]["pass_hex"]]
    return comp, non, known


def gen_case(kind):
    tape = bytearray(128)
    if kind == "uniform":
        tape[:] = bytes(rng.randrange(256) for _ in range(128))
    elif kind == "sparse":                 # mostly NOPs + a few ops + HALTs: keeps pc and pointers local
        for i in range(128):
            u = rng.random()
            tape[i] = 0 if u < 0.6 else (0x76 if u < 0.68 else rng.choice(
                (0x1E, 0x2E, 0x0E, 0x40, 0xC0, 0xE5, 0xE7, 0x7E, 0x12, 0x23, 0x13, 0x18, 0x77, 0x36, rng.randrange(256))))
    else:                                  # panel genome + random partner
        g = rng.choice(PANEL)
        tape[0:64] = bytes(rng.randrange(256) for _ in range(64))
        side = rng.randrange(2)
        tape[64 * side:64 * side + len(g)] = g
    base = rng.choice((0, 64))
    u = rng.random()
    regs = None if u < 0.5 else ([0] * 8 if u < 0.6 else [rng.randrange(256) for _ in range(8)])
    if regs is not None and rng.random() < 0.5:   # pointers into the tape (keeps NOWRAP inside its domain)
        regs[2] = regs[4] = 0
    mask = rng.choice((0x2A, 0x2A, 0xFF, 0x0A))
    budget = rng.choice((300, 300, 60, 1500))
    return bytes(tape), base, regs, (rng.randrange(2), rng.randrange(2)), mask, budget, rng.randrange(1 << 30)


def execute(vm, case, aoff=0, policy=None):
    tape, base, regs, (fz, fc), mask, budget, seed = case
    mem = bytearray(tape)
    ctx = vm.Ctx(mem, base, 64, policy=vm.ARENA if policy is None else policy, rng=random.Random(seed),
                 copy_mut_rate=0.002, sense=base // 64)
    ctx.regs, ctx.fz, ctx.fc = (None if regs is None else list(regs)), fz, fc
    ctx.prov, ctx.prov_lit, ctx.who = bytearray(128), bytearray(128), 1 + base // 64
    if aoff:
        ctx.aoff = aoff
    h0 = vm._HITS[0] if hasattr(vm, "_HITS") else 0
    pc = vm.run(ctx, base, budget, ops_enabled=mask)
    hits = (vm._HITS[0] - h0) if hasattr(vm, "_HITS") else 0
    state = (bytes(mem), bytes(ctx.prov), bytes(ctx.prov_lit), tuple(ctx.regs), ctx.fz, ctx.fc, pc,
             tuple(sorted(ctx.telemetry().items())))
    return state, hits


COMP, NON, KNOWN = panel()
PANEL = COMP + NON
KINDS = ("uniform", "sparse", "panel")

# ---- T1
dense = alien_vm.build("DENSE")
n_bad = 0
NT1 = 3000
for i in range(NT1):
    c = gen_case(KINDS[i % 3])
    for pol in (None, dense.OWN):
        if execute(dense, c, policy=pol)[0] != execute(REF, c, policy=pol)[0]:
            n_bad += 1
res["T1_dense_equals_run_dc"] = {"cases": 2 * NT1, "mismatches": n_bad, "pass": n_bad == 0}
print("T1", res["T1_dense_equals_run_dc"], flush=True)

# ---- T2
T2 = {}
for name in alien_vm.VM_NAMES:
    if name == "DENSE":
        continue
    vm = alien_vm.build(name)
    st = {"hits0": 0, "hits0_identical": 0, "hits_pos": 0, "hits_pos_differ": 0}
    for i in range(1500):
        c = gen_case(KINDS[i % 3])
        aoff = 0
        if name == "AOFF" and i % 2:
            aoff = rng.choice((-rng.randrange(1, 128), 64, rng.randrange(1, 128)))
        a, h = execute(vm, c, aoff=aoff)
        b, _ = execute(dense, c)
        if h == 0:
            st["hits0"] += 1
            st["hits0_identical"] += a == b
        else:
            st["hits_pos"] += 1
            st["hits_pos_differ"] += a != b
    st["pass"] = st["hits0"] >= 100 and st["hits0_identical"] == st["hits0"] and st["hits_pos_differ"] > 0
    T2[name] = st
    print("T2", name, st, flush=True)
res["T2_variant_identity_where_unmodified"] = T2

# ---- T3
n_draw_bad = n_verdict_bad = 0
cases3 = 0
for g in COMP[:40] + NON[:10] + [bytes(rng.randrange(256) for _ in range(64)) for _ in range(30)]:
    for side in (0, 1):
        ga, gb = (g, bytes(64)) if side == 0 else (bytes(64), g)
        seed = ("W2-7-T3", g.hex()[:12], side)
        kw = dict(n=64, tape_len=128, ga=ga, gb=gb, st_a=(None, 0, 0), st_b=(None, 0, 0), budget=300,
                  ops_mask=0x2A, cmr=0.002, victim_side=1 - side, seed=seed)
        ref = p11.assay(REF, **kw)
        mine = AP.assay(dense, early=False, **kw)
        fast = AP.assay(dense, early=True, **kw)
        cases3 += 1
        n_draw_bad += ref["draws"] != mine["draws"] or ref["pass"] != mine["pass"]
        n_verdict_bad += ref["pass"] != fast["pass"]
res["T3_assay_equals_p11"] = {"cases": cases3, "draw_mismatches": n_draw_bad, "early_verdict_mismatches": n_verdict_bad,
                              "pass": n_draw_bad == 0 and n_verdict_bad == 0}
print("T3", res["T3_assay_equals_p11"], flush=True)

# ---- T4
rand150 = [bytes(rng.randrange(256) for _ in range(64)) for _ in range(150)]
sets = {"panel_competent": COMP, "panel_noncompetent": NON, "known_random_passes": KNOWN, "random": rand150}
T4 = {}
for k, gs in sets.items():
    mm, pos = 0, 0
    for g in gs:
        ref = F.competent("7ae3", g, dense=True)
        mine = AP.competent(dense, g)
        mm += ref != mine
        pos += mine
    T4[k] = {"n": len(gs), "mismatches": mm, "competent_here": pos}
    print("T4", k, T4[k], flush=True)
T4["pass"] = all(v["mismatches"] == 0 for v in T4.values() if isinstance(v, dict))
res["T4_competent_equals_run_de"] = T4
res["ALL_PASS"] = (res["T1_dense_equals_run_dc"]["pass"] and all(v["pass"] for v in T2.values())
                   and res["T3_assay_equals_p11"]["pass"] and T4["pass"])
res["cpu_s"] = round(time.process_time() - T0, 1)
OUT.write_text(json.dumps(res, indent=1))
print("ALL_PASS", res["ALL_PASS"], "cpu", res["cpu_s"])
