"""W2-6 check C7 (T6 vs T7 on the BASE miss): is "erosion / content sterility" (which T7 must add by hand) already a
two-step quantity of the rewrite field (T6 clauses (ii)-(iv)), i.e. visible in single interactions chained twice?

The one-step map gives 7ae3 under BASE a GW P_est of 0.26 vs ~0.03 observed (U-S1); under ATOMIC the map fits
(0.49-0.63 vs 0.52). If T6's closure terms carry the erosion, then chaining two world interactions should show the
donor's (or its child's) second-step conversion collapsing under BASE but not under ATOMIC.

Physics: 7ae3's C9 H2 arm-B cell (the X-TICKET / C-ATOMIC cell), atlas_axis NONE, stock VM; BASE = world.Runner,
ATOMIC = run_ds.runner_cls(world) (C-ATOMIC write-back). The runner is constructed and never run; each interaction is
one call of the world's own _pair_interact (write-back, mutation, P-11 assay unchanged). Initial organisms enter with
regs None (as placed by the world). Partners: uniform random 64-byte genomes (the initial background is random).
Step 1: founder vs partner (side alternating). Step 2a: the founder's post-interaction content+context (if still the
founder's label) vs a new partner. Step 2b: the child (partner half after conversion, in its own leftover context) vs a
new partner, at the same side the founder used. Output c7_t6_t7_base_closure.json.
"""
import json
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[1] / "campaigns"
C9 = CAMP / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(CAMP / "c9x-explore-2026-09-24" / "x_donor_swap"))
sys.path.insert(0, str(C9))
import world  # noqa: E402  (stock z8, as X-TICKET)
import run_ds  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
t0 = time.process_time()
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == "7ae3f9c1437c8000-s54765-tL-a0")
arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
G7 = bytes.fromhex(arm["kwargs"]["implant_hex"])
CELL = dict(arm["cell"], atlas_axis="NONE")


def harness(base, seed):
    births = []

    class H(base):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            births.append((parent, bool(causal)))
    r = H(CELL, seed, tier=arm["tier"])
    r.t["epochs"] = 0
    d, p = r._place(bytes(r.L), 0), r._place(bytes(r.L), 1)
    return r, d, p, births


def one(h, g, st, pg, side):
    r, d, p, births = h
    for o, gg, s, anc in ((d, g, st, 0), (p, pg, (None, 0, 0), 1)):
        r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
        r.mem[o.slot:o.slot + len(gg)] = gg
        o.length, o.anc = len(gg), anc
        o.regs = None if s[0] is None else list(s[0])
        o.fz, o.fc = s[1], s[2]
    did, pid = d.oid, p.oid
    del births[:]
    r.epoch += 1
    a, bb = (d, p) if side == 0 else (p, d)
    r._pair_interact(0, a, bb)
    conv = any(par == did for par, _ in births)
    hij = any(par == pid for par, _ in births)
    return {"conv": conv, "hijacked": hij, "d_after": (r._genome(d), (None if d.regs is None else list(d.regs), d.fz, d.fc)),
            "p_after": (r._genome(p), (None if p.regs is None else list(p.regs), p.fz, p.fc))}


rng = random.Random(20261001)
parts = [bytes(rng.randrange(256) for _ in range(64)) for _ in range(3 * N)]
out = {}
for name, base in (("BASE", world.Runner), ("ATOMIC", run_ds.runner_cls(world))):
    h = harness(base, 4242)
    s1 = s2a = s2a_n = s2b = s2b_n = hij = 0
    d_changed = []
    for i in range(N):
        side = i % 2
        a = one(h, G7, (None, 0, 0), parts[3 * i], side)
        s1 += a["conv"]
        hij += a["hijacked"]
        if not a["hijacked"]:
            dg, dst = a["d_after"]
            d_changed.append(sum(1 for x, y in zip(dg, G7) if x != y))
            b2 = one(h, dg, dst, parts[3 * i + 1], side)
            s2a_n += 1
            s2a += b2["conv"]
        if a["conv"]:
            cg, cst = a["p_after"]
            b3 = one(h, cg, cst, parts[3 * i + 2], side)
            s2b_n += 1
            s2b += b3["conv"]
    out[name] = {"trials": N, "step1_conv": round(s1 / N, 3), "step1_founder_hijacked": round(hij / N, 3),
                 "founder_bytes_changed_mean": round(sum(d_changed) / len(d_changed), 2) if d_changed else None,
                 "founder_unchanged_share": round(sum(1 for x in d_changed if x == 0) / len(d_changed), 3) if d_changed else None,
                 "step2_founder_conv": round(s2a / s2a_n, 3) if s2a_n else None,
                 "step2_child_conv": round(s2b / s2b_n, 3) if s2b_n else None, "children": s2b_n}
    print(name, out[name], round(time.process_time() - t0, 1), flush=True)
out["cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "c7_t6_t7_base_closure.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
