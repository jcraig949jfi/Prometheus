"""C-DENSE-COPY (CONFIRM lane, fresh and frozen). Parent: X-DD-DENSE-COPY (EXPLORE, SIGNAL).

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, arms, endpoint, rule, allocation, controls.

Exploratory result: in random populations (7ae3 / ffa6 cells, ATOMIC write-back), giving LDIR and LDDR
an additional one-byte encoding (0xE5, 0xE7; semantics and ops-mask gating unchanged) raised the share
of runs in which a fresh-start-competent donor appears from 0/96 to 49/96, and runaway heredity from
0/96 to 23/96, although 87/96 PLAIN runs contain a block-copy encoding somewhere.
Claim under test: spontaneous donor acquisition in this cell class is limited by the accessibility of
the block-copy instruction's encoding; a one-byte block-copy encoding makes it common.

Design: exactly X-DD-DENSE-COPY's runner, VM injection, ruler and cells (run_dc.job), with FRESH
seeds 17_000_000 + s, s < 32, per cell per arm: PLAIN vs DENSE_COPY, 64 runs per arm, 128 total.
One job per process; the VM is set explicitly per job.
Endpoint (per run): L2 = at some checkpoint (every 100 epochs) at least one live genome is COMPETENT
(fresh-start P-11 pass rate >= 0.5 over 20 seeds after the 4-seed screen, assay on the job's VM).
CONFIRMED iff share(DENSE_COPY) - share(PLAIN) >= 0.25 AND one-sided Fisher exact p < 0.001.
NOT_CONFIRMED otherwise.
Frozen controls (INVALID if any fails): the VM self-test (0xE5 block-copies on the dense VM, not on
the stock VM); every result records the VM it ran on and it matches its arm; the 7ae3 genome is
COMPETENT under the parent screen on both VMs (the aliases add encodings, remove none).
Eligibility (before freezing): with PLAIN at 0 the count bar (16 of 64) binds before the p bar (10);
at the exploratory rate (51%) the expected DENSE count is ~33; computed P(pass) with PLAIN = 0 is
0.84 at a true DENSE rate of 0.30, 0.97 at 0.35, 1.00 at 0.50.
Secondary, never decisive: L4 (runaway) per arm; L4 given L2; per-cell counts.

    python run_cdc.py -> RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "x_dd_dense_copy"
DD = HERE.parent / "x_donor_discovery"
for p in (DC, DD, HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
N = 32
SEED0 = 17_000_000
ARMS = ("PLAIN", "DENSE_COPY")


def job(args):
    import run_dc
    run_dc.HERE = HERE                  # results go to THIS directory; logic unchanged
    return run_dc.job(args)


def jobs():
    return [(arm, c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6") for arm in ARMS]


def pc_both_vms():
    import world
    import z8 as plain
    import run_dc
    import run_dd
    import run_ds
    out = {}
    for name, vm in (("plain", plain), ("dense", run_dc.dense_z8())):
        world.z8 = vm
        arm = run_ds.cells()[run_dd.CELLS["7ae3"]]
        r = world.Runner(dict(arm["cell"], atlas_axis="NONE"), 1, tier=arm["tier"])
        out[name] = run_dd.screen(world, r, [bytes(r._pad(run_ds.donor_genome()))], ("C-DENSE-COPY-PC", name))["L2"] == 1
    world.z8 = plain
    return out


def fisher(a, b, n1, n2):
    k0 = a + b
    return (sum(math.comb(n1, x) * math.comb(n2, k0 - x) for x in range(a, min(n1, k0) + 1))
            / math.comb(n1 + n2, k0)) if k0 else 1.0


def main():
    import run_dc
    st = run_dc.selftest()
    pc = pc_both_vms()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [t for t in jobs() if "%s_%s_%d" % t not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    assert len(res) == len(jobs()), len(res)
    vm_ok = all((r["vm"] == "z8_dense_copy") == (r["arm"] == "DENSE_COPY") for r in res)
    controls_ok = st == {"plain": False, "dense": True} and vm_ok and all(pc.values())
    by = {a: [r for r in res if r["arm"] == a] for a in ARMS}
    l2 = {a: sum(any(c["L2"] > 0 for c in r["checkpoints"]) for r in by[a]) for a in ARMS}
    n = {a: len(by[a]) for a in ARMS}
    diff = l2["DENSE_COPY"] / n["DENSE_COPY"] - l2["PLAIN"] / n["PLAIN"]
    p = fisher(l2["DENSE_COPY"], l2["PLAIN"], n["DENSE_COPY"], n["PLAIN"])
    verdict = ("INVALID" if not controls_ok else
               "CONFIRMED" if diff >= 0.25 and p < 0.001 else "NOT_CONFIRMED")
    sec = {a: {"L4": sum(r["depth"] >= 20 for r in by[a]),
               "L4_given_L2": sum(r["depth"] >= 20 for r in by[a] if any(c["L2"] > 0 for c in r["checkpoints"])),
               "per_cell_L2": {c: sum(any(k["L2"] > 0 for k in r["checkpoints"]) for r in by[a] if r["cell"] == c)
                               for c in ("7ae3", "ffa6")}} for a in ARMS}
    v = {"verdict": verdict, "controls": {"selftest": st, "vm_ok": vm_ok, "pc_7ae3_competent": pc},
         "L2_runs": l2, "n": n, "share_diff": round(diff, 4), "fisher_p": p, "secondary": sec}
    (HERE / "RESULTS.json").write_text(json.dumps([{k: r[k] for k in ("arm", "cell", "seed", "depth", "p11_events", "vm")}
                                                   for r in res]))
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
