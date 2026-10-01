"""Out-of-sample test, step 1: per-donor predictors for the X-DD-ESTABLISH W1 first donors (D0).

    python -B oos_predict.py   -> oos_predict.json

Pre-registered in FORENSIC_MAP_OUT_OF_SAMPLE.md (written before this ran). Static: single-interaction VM calls only.

Panel: every x_dd_establish/results/*.json run. D0 genome = x_dd_nocopy_context donor_hex matched on (cell, seed)
(that script records ONE genome per run: the first COMPETENT organism, comp[0], at the D0 check). x_dd_selfstate
records no hex. Runs with no recorded D0 genome -> excluded as NO_D0 (the status-NO_D0 run plus any run whose genome
was never recorded), counted in the output.

World: the X-DD-ESTABLISH runner is run_ds.runner_cls(world)(dict(run_ds.cells()[run_dd.CELLS[cell]]["cell"],
atlas_axis="NONE"), seed, tier=...) with world.z8 = run_dc.dense_z8() and no implant. Verified in the report that
this equals the map harness's cells exactly: 7ae3 -> harness cell "C7", ffa6 -> harness cell "CF" (same cell dict,
tier M, L 64, slice 300, ops mask 42, cmr 0.002). run_rs.runner(..., "CARRY") is the bare ATOMIC class, so the
harness CARRY context is the X-DD-ESTABLISH register physics. Nothing in the harness is changed.

Predictors (code reused unchanged, imported):
  law = map_offspring.condition(g, cell, "CARRY", T, map_offspring.partner_pool(cell), seed)
        with T = map_offspring.transmitted(g) (default cell, as map_offspring.main) and
        seed = 30_000 + 97 * i + CTX.index("CARRY") (map_offspring.main's formula, i = panel index);
  P_run500_causal = map_correlate.gw_run((CAUSAL p0, p1, p2))  [PRIMARY, pre-registered]
  P_est           = law["T"]["P_est"]                          [comparator, specified map]
  P_run500        = map_correlate.gw_run(T law)                [extra, non-decisive]
  P_run2          = map_correlate.gw2_run on the map_children two-type law [extra, non-decisive; see report:
                    map_children.main hard-codes cell CF, here the donor's own cell is passed -> adapted]
"""
from __future__ import annotations

import glob
import json
import os
import random
import sys
import time

sys.dont_write_bytecode = True
import map_common as M  # noqa: E402
import map_offspring as MO  # noqa: E402
import map_correlate as MC  # noqa: E402  (module RNG = default_rng(20260930), as in panel A/B)
import map_children as MCH  # noqa: E402

t0 = time.process_time()
W1 = M.W1
OUT = M.HERE / "oos_predict.json"
HCELL = {"7ae3": "C7", "ffa6": "CF"}


def panel():
    nc = {}
    for f in glob.glob(str(W1 / "x_dd_nocopy_context" / "results" / "*.json")):
        r = json.loads(open(f).read())
        nc[(r["cell"], int(r["seed"]))] = r
    rows, excl = [], []
    for f in sorted(glob.glob(str(W1 / "x_dd_establish" / "results" / "*.json"))):
        r = json.loads(open(f).read())
        k = (r["cell"], int(r["seed"]))
        src = nc.get(k)
        hx = src.get("donor_hex") if src else None
        base = {"cell": r["cell"], "seed": int(r["seed"]), "status": r["status"], "lineage_births": r["lineage_births"],
                "depth": r["depth"], "d0_size": r["d0_size"], "d0_epoch": r["d0_epoch"]}
        if not hx:
            excl.append(dict(base, reason="status NO_D0" if r["status"] == "NO_D0" else
                             "D0 exists (d0_size %d) but no source records its genome" % r["d0_size"]))
            continue
        rows.append(dict(base, hex=hx, nc_replay_ok=src.get("replay_ok"), nc_control_ok=src.get("control_ok"),
                         nc_label=src.get("label")))
    return rows, excl


def children_prun2(g, hcell, i, pool):
    """map_children.main's per-(donor, ctx) body for ctx CARRY, panel-A seed offset, cell passed explicitly."""
    ctx = "CARRY"
    seed = 40_000 + 97 * i + MCH.CTX.index(ctx)
    h = M.Harness(ctx, seed, hcell)
    rng = random.Random(repr(("MAPCH", "OOS", i, ctx)))
    J, kids, fconv = MCH.run_law(h, g, ctx, MCH.NF, rng, pool, collect=MCH.NC)
    cnt = [0, 0, 0]
    cconv = 0
    for kg, kst in kids:
        for _ in range(MCH.NI):
            side = rng.randrange(2)
            pg = M.rand_genome(rng, h.n)
            x = h.interact(kg, pg, side, d_state=kst, p_state=pool[rng.randrange(len(pool))])
            kst = x["d_state"]
            ch = x["p_conv"] and M.ident(x["gp"], kg) >= 0.9
            cconv += ch
            cnt[(1 if x["d_kept"] else 0) + (1 if ch else 0)] += 1
    tot = sum(cnt)
    cl = None if not tot else tuple(c / tot for c in cnt)
    return {"joint": J, "founder_conv": fconv, "n_children": len(kids), "child_law": cl,
            "child_conv": (cconv / tot) if tot else None, "P_run2": MC.gw2_run(J, cl)}


def main():
    rows, excl = panel()
    print("panel", len(rows), "excluded", len(excl), flush=True)
    pools = {c: MO.partner_pool(c) for c in ("CF", "C7")}
    print("pools", round(time.process_time() - t0, 1), flush=True)
    for i, r in enumerate(rows):
        g = bytes.fromhex(r["hex"])
        hc = HCELL[r["cell"]]
        T, src, nconv = MO.transmitted(g)
        law = MO.condition(g, hc, "CARRY", T, pools[hc], 30_000 + 97 * i + MO.CTX.index("CARRY"))
        r.update(harness_cell=hc, T_n=len(T), T_src=src, T_zero_conv_of_80=nconv,
                 law={k: law[k] for k in ("T", "CAUSAL", "W", "LABEL")},
                 conv_rate_by_side=law["conv_rate_by_side"], donor_overwritten_rate=law["donor_overwritten_rate"],
                 P_est=law["T"]["P_est"], P_est_causal=law["CAUSAL"]["P_est"], m=law["T"]["m"],
                 P_run500=MC.gw_run((law["T"]["p0"], law["T"]["p1"], law["T"]["p2"])),
                 P_run500_causal=MC.gw_run((law["CAUSAL"]["p0"], law["CAUSAL"]["p1"], law["CAUSAL"]["p2"])))
        print(i, r["cell"], r["seed"], r["status"], r["lineage_births"], "Pest", r["P_est"], "Prun500c",
              r["P_run500_causal"], round(time.process_time() - t0, 1), flush=True)
    stage1 = round(time.process_time() - t0, 1)
    for i, r in enumerate(rows):
        c = children_prun2(bytes.fromhex(r["hex"]), r["harness_cell"], i, pools[r["harness_cell"]])
        r.update(P_run2=c["P_run2"], child_conv=c["child_conv"] or 0.0, children=c)
        print("ch", i, r["P_run2"], r["child_conv"], round(time.process_time() - t0, 1), flush=True)
    res = {"rows": rows, "excluded": excl, "cpu_s_primary": stage1, "cpu_s": round(time.process_time() - t0, 1)}
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print("cpu", res["cpu_s"])


if __name__ == "__main__":
    main()
