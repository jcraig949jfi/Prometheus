"""C-ZERO-SPECIFIC (CONFIRM lane, fresh and frozen). Parent: X-P2-REGSTATE (EXPLORE, SIGNAL ZERO_SPECIFIC).
Theory-aware by date.

NOTHING HERE MAY CHANGE AFTER COMMIT: cell, donor panel, seeds, arms, endpoint, rule, allocation, controls.

Exploratory result (X-P2-REGSTATE, CF = ffa6's cell, implanted 16-donor panel): establishment S5 ZERO 0.53 vs
CONST(0x5A) 0.16, CARRY 0.28, RANDOM 0.19 -- only the zero reset rescues; other clean states do worse than carried.
Claim under test: the establishment rescue by fresh-state execution (C-STATELESS-FFA6) is specific to the ZERO
initial register state; resetting to a different fixed clean state (all register bytes 0x5A, flags 0) does not
rescue. (Reading: the donors are specialists of the environment's zero reset, not victims of carried state as such.)

Scaffold (LABELLED): single implanted competent donor per run. FRESH donor panel, disjoint from X-P2-BRIDGE /
X-P2-REGSTATE's: the first competent genome of each C-DENSE-COPY DENSE_COPY run with any L2 (c_dense_copy/results,
seeds 17_000_000 + s, in seed order), 8 from the 7ae3 cell and 8 from ffa6 -- taking, in each run, the first
recorded competent genome that passes a re-screen (dense VM, zeros, fixed seeds keyed by the genome); fixed in
DONORS.json, written before the freeze commit. (Pre-freeze repair: the first draft took the first recorded genome
regardless, and 4 of 16 then failed the re-screen control.)
Cell: CF (7ae3's H2 B-arm cell with representation Z8_SLOTTED and structure NICHES_HIGH_MIG = ffa6's cell),
dense VM, ATOMIC runner, max_epochs 500.
Arms (register policy before every pair interaction, X-P2-REGSTATE's runner): ZERO, CONST, CARRY, RANDOM.
Seeds: fresh, 23_000_000 + 3 d + k, k < 3, per donor per arm: 48 runs per arm, 192 total.
Endpoint (per run): ESTABLISHED = world causal depth >= 20 by epoch 500 AND final anc0 share >= 0.9 (X-P2-BRIDGE S5).
CONFIRMED iff share(ZERO) - share(CONST) >= 0.25 AND one-sided Fisher exact p < 0.001 (ZERO > CONST).
NOT_CONFIRMED otherwise.
Frozen controls (INVALID if any fails): X-P2-REGSTATE's self-test (each policy's register vector reaches z8.run);
16 donors loaded; every donor COMPETENT on the dense VM from zeros (run_dd screen) before launch.
Eligibility (before freezing): at the exploratory rates (0.53 vs 0.16) with 48 per arm the expected counts (25 vs
8) give Fisher p = 2.4e-4; P(pass) is high if the true difference is >= 0.3, falls towards 0.5 at a difference of 0.25.
Secondary, never decisive: CARRY and RANDOM shares; S1-S4; per donor origin.

    python run_cz.py -> VERDICT.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
RS = HERE.parent / "x_p2_regstate"
BR = HERE.parent / "x_p2_bridge"
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
for p in (RS, BR, W1 / "x_dd_stateless", W1 / "x_dd_establish", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
ARMS = ("ZERO", "CONST", "CARRY", "RANDOM")
SEED0 = 23_000_000
K = 3


_PANEL = None


def _competent_now(g):
    """Re-screen on the dense VM from zeros (fixed seeds): the panel admits only donors that pass it."""
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS["ffa6"]]
    r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    return run_dd.screen(world, r, [bytes(r._pad(g))], ("C-ZERO-SPECIFIC-PANEL", g.hex()))["L2"] == 1


def donors():
    global _PANEL
    if _PANEL is not None:
        return _PANEL
    f = HERE / "DONORS.json"
    if f.exists():
        _PANEL = json.loads(f.read_text())
        return _PANEL
    out = []
    cd = W1 / "c_dense_copy" / "results"
    for cell in ("7ae3", "ffa6"):
        k = 0
        for s in range(32):
            p = cd / ("DENSE_COPY_%s_%d.json" % (cell, 17_000_000 + s))
            if not p.exists():
                continue
            r = json.loads(p.read_text())
            cp = next((c for c in r["checkpoints"] if c["L2"] > 0), None)
            if cp is None:
                continue
            pick = next((g["hex"] for g in cp["competent_genomes"] if _competent_now(bytes.fromhex(g["hex"]))), None)
            if pick is None:
                continue
            out.append({"origin": cell, "run_seed": r["seed"], "hex": pick})
            k += 1
            if k == 8:
                break
    _PANEL = out
    return out


def jobs():
    n = len(donors())
    return [("CF", a, d, SEED0 + K * d + k) for a in ARMS for d in range(n) for k in range(K)]


def job(args):
    import run_br
    import run_rs
    run_br.donors = donors                 # the fresh panel; the runner logic is X-P2-REGSTATE's, unchanged
    run_rs.HERE = HERE
    return run_rs.job(args)


def fisher(a, b, n1, n2):
    k0 = a + b
    return (sum(math.comb(n1, x) * math.comb(n2, k0 - x) for x in range(a, min(n1, k0) + 1))
            / math.comb(n1 + n2, k0)) if k0 else 1.0


def precheck():
    import world
    import run_dc
    import run_dd
    import run_ds
    import run_rs
    ok_st, st = run_rs.selftest()
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS["ffa6"]]
    r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    D = donors()
    comp = [run_dd.screen(world, r, [bytes(r._pad(bytes.fromhex(x["hex"])))], ("C-ZERO-SPECIFIC-PANEL", bytes.fromhex(x["hex"]).hex()))["L2"] == 1
            for x in D]
    return {"selftest": st, "selftest_ok": ok_st, "n_donors": len(D), "donors_competent": sum(comp)}


def main():
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    pc = precheck()
    (HERE / "PRECHECK.json").write_text(json.dumps(pc, indent=1))
    todo = jobs()
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%s_%d_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    assert len(res) == len(todo), len(res)
    controls_ok = pc["selftest_ok"] and pc["n_donors"] == 16 and pc["donors_competent"] == 16
    by = {a: [r for r in res if r["policy"] == a] for a in ARMS}
    est = {a: sum(r["S5"] for r in by[a]) for a in ARMS}
    n = {a: len(by[a]) for a in ARMS}
    diff = est["ZERO"] / n["ZERO"] - est["CONST"] / n["CONST"]
    p = fisher(est["ZERO"], est["CONST"], n["ZERO"], n["CONST"])
    verdict = ("INVALID" if not controls_ok else "CONFIRMED" if diff >= 0.25 and p < 0.001 else "NOT_CONFIRMED")
    v = {"verdict": verdict, "controls": pc, "established": est, "n": n, "share": {a: round(est[a] / n[a], 4) for a in ARMS},
         "diff_ZERO_minus_CONST": round(diff, 4), "fisher_p": p,
         "secondary": {a: {k: round(sum(r[k] is not None for r in by[a]) / n[a], 4) for k in ("S1", "S2", "S3", "S4")} for a in ARMS}}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
