"""E-R8-H1b (SWARM_R8 s7 H1, its structural discriminator): WHICH donor component carries the gain over scratch?
Preregistered before any run, AFTER E-R8-H1 (receipt 1789599074033-0) read FLAT_NO_SYSTEMATIC_RESPONSE with every
donor-derived rung above scratch -- including L3 (no W feature structure) and L4 (per-genome W mean/sd only). What every
H1 rung shares and scratch lacks: the donor's W values/scale, bias b and action codebook C. H1b separates them.

OBSERVATION only. Not a Clause B control or verdict, not a transfer claim, not a transfer matrix (one pair). The R7
Clause B FAIL stands. Carried calibration: the v2 control's false-PASS rate <= ~7.2% (95% one-sided), 0/40 observed.

Pair, budget, streams: E-R8-H1 exactly (donor w14, recipient w13 train128_held64, linear, gens 800 x batch 128, K 16,
transfer.evolve + held_auc) EXCEPT fresh run seeds 32..39 (never used for this pair; H1's 24..31 motivated this design,
so H1's runs are NOT reused). Families 4200/2101/3303/5501 -> 32/4/8. Round-robin run order by run seed.

CELLS: a 2^3 factorial. Each of the 16 slots is (W, b, C) with each component taken from the donor top-16 (1) or from
the SAME 16 scratch init genomes (0) that the scratch arm uses (filler[:16]); slot i pairs donor genome i with scratch
genome i. Cell name "W{w}b{b}C{c}". W000 = scratch arm (bytes == H1-style scratch), W111 = unmodified donor (== L0).
Common filler (slots 16..127) and common mutation stream per run, as in H1.

RESPONSE held_auc. ANALYSIS (fixed now; analyze(rows)), alpha 0.05, transfer.signflip_p one-sided, pairs within run:
  main effect of component X in {W, b, C}: per run e_X = mean(held_auc over the 4 cells with X=1) - mean(4 cells X=0);
      p_X = signflip_p(e_X); Holm over the three.
  CARRIERS = the components with Holm p < 0.05 (e.g. "b+C"); NONE if empty.
  Reported only: two-way interactions (per-run contrasts, two-sided p's), every cell - W000, W111 - W000 beside H1's
  L0 - scratch (+1.86), zero_shot / held64 / train_auc means.
  WORDING: a carrier is a component of the donor genome whose presence raises the recipient's held_auc; never "transfer".
  INDETERMINATE if fewer than 32 complete runs (no classification on a partial sample).
Integrity (every run, exact): each cell's W / b / C bytes equal their declared source; W111 bytes == donor; W000 bytes ==
scratch slots; genome length. Oracles: donor fused == numpy every run; world honest/skip_lin + brain honest/cheat run 1.

    python -m primordial.cohorts.e.r8_h1b_carrier_factorial dev [gens] [batch]      # no rows
"""
from __future__ import annotations

import itertools
import json
import sys
import time

import numpy as np

from primordial.cohorts.e import r8_h1_sham_ladder as H
from primordial.cohorts.e import transfer as T
from primordial.cohorts.e import transfer_v2 as V
from primordial.qd import e7_run as E7
from primordial.soup.b6.fused import FusedRollout

EXP = "E-R8-H1b-carrier-factorial"
ROWS = f"primordial/ledger/rows/E/{EXP}.jsonl"
VERSION = "h1b_carrier_factorial_v1"
BITS = tuple(itertools.product((0, 1), repeat=3))                 # (W, b, C)
CELLS = tuple(f"W{w}b{b}C{c}" for w, b, c in BITS)
COMPONENTS = ("W", "b", "C")
RUN_SEEDS = tuple(range(32, 40))
FAMILIES = H.FAMILIES
GENS, BATCH = H.GENS, H.BATCH
ALPHA = 0.05
H1_L0_MINUS_SCRATCH = 1.8608589172363281                           # receipt 1789599074033-0, reported beside
STATUS = {c: ("record" if c in ("W0b0C0", "W1b1C1") else "control") for c in CELLS}


def bits_of(cell: str) -> tuple[int, int, int]:
    return int(cell[1]), int(cell[3]), int(cell[5])


def make_cells(g7r: E7.G7, dA: np.ndarray, scratch: np.ndarray) -> dict:
    (Wd, bd), Cd = g7r.unpack(dA)
    (Ws, bs), Cs = g7r.unpack(scratch)
    out = {}
    for cell in CELLS:
        w, b, c = bits_of(cell)
        out[cell] = g7r.pack((((Wd if w else Ws).copy(), (bd if b else bs).copy()), (Cd if c else Cs).copy()))
    return out


def cell_integrity(g7r: E7.G7, dA: np.ndarray, scratch: np.ndarray, cells: dict) -> dict:
    (Wd, bd), Cd = g7r.unpack(dA)
    (Ws, bs), Cs = g7r.unpack(scratch)
    by = lambda x: np.ascontiguousarray(x).view(np.uint8)
    out = {}
    for cell in CELLS:
        w, b, c = bits_of(cell)
        (Wx, bx), Cx = g7r.unpack(cells[cell])
        chk = {"W_source": bool(np.array_equal(by(Wx), by(Wd if w else Ws))),
               "b_source": bool(np.array_equal(by(bx), by(bd if b else bs))),
               "C_source": bool(np.array_equal(Cx, Cd if c else Cs)),
               "genome_bytes": int(cells[cell].shape[1]) == int(dA.shape[1])}
        if cell == "W1b1C1":
            chk["bytes_eq_donor"] = T.sha(cells[cell]) == T.sha(dA)
        if cell == "W0b0C0":
            chk["bytes_eq_scratch"] = T.sha(cells[cell]) == T.sha(scratch)
        chk["ok"] = all(chk.values())
        out[cell] = chk
    return out


def base_row(sample: dict, campaign_stage: str = "PRODUCTION", gens: int = GENS, batch: int = BATCH) -> dict:
    return dict(H.base_row(sample, campaign_stage, gens, batch), exp_id=EXP, ladder_version=VERSION)


def run_one(fam: int, rs: int, base: dict, gens: int = GENS, batch: int = BATCH, oracles: bool = False) -> dict:
    from primordial.metric import floors as F
    g7r, g7d = E7.G7(H.RECIPIENT, H.FAMILY), E7.G7(H.DONOR, H.FAMILY)
    ok, why = T.compatible(g7d, g7r)
    if not ok:
        raise ValueError(why)
    train = np.arange(9100, 9100 + len(F.PRESSURES[H.PRESSURE]), dtype=np.int64)
    t0 = time.process_time()
    dA = T.evolve(g7d, H.FAMILY, train, gens, batch, H._pcg(fam, 1701, rs, H.DONOR))[0].top()
    filler = g7r.pack(g7r.init(H._pcg(fam, 1705, rs, H.RECIPIENT), batch))
    scratch = filler[:T.TOP].copy()
    cells = make_cells(g7r, dA, scratch)
    integ = cell_integrity(g7r, dA, scratch, cells)
    np_fit = E7.rollout(g7r, g7r.unpack(dA), train)[0]
    fu_fit = FusedRollout(g7r.spec, T.TOP, train, family=H.FAMILY).run(g7r.unpack(dA))[0]
    ids = {"rng_family": int(fam), "run_seed": int(rs), "run_id": V.rid_key(fam, rs)}
    rows = {}
    for cell in CELLS:
        gen0 = filler.copy()
        gen0[:T.TOP] = cells[cell]
        c0 = time.process_time()
        arch, curve, hcurve = T.evolve(g7r, H.FAMILY, train, gens, batch, H._pcg(fam, 1704, rs, H.RECIPIENT), gen0,
                                       held=T.HELD64)
        w, b, c = bits_of(cell)
        row = dict(base, **ids, status=STATUS[cell], condition=cell, donor_W=w, donor_b=b, donor_C=c,
                   held_auc=float(hcurve.mean()), held_curve=[round(float(x), 3) for x in hcurve],
                   train_auc=float(curve.mean()), train_final=float(curve[-1]), held64=float(hcurve[-1]),
                   zero_shot_held64=T.score(g7r, H.FAMILY, gen0[:T.TOP], T.HELD64), cells=len(arch),
                   slot_sha256=T.sha(gen0[:T.TOP]), donor_sha256=T.sha(dA), cell_integrity=integ[cell],
                   arm_cpu_s=time.process_time() - c0)
        if cell == "W1b1C1":
            row["donor_fused_eq_numpy"] = bool(np.array_equal(np_fit, fu_fit))
            if oracles:
                tg = g7r.unpack(arch.top())
                row["world_oracle_honest"] = E7.world_oracle(g7r, tg, T.HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(g7r, tg, T.HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(g7r, tg, T.HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(g7r, tg, T.HELD8, cheat=True)
        rows[cell] = row
    rows["_run_cpu_s"] = time.process_time() - t0
    return rows


def _two_sided(d) -> float:
    return min(1.0, 2 * min(T.signflip_p(d), T.signflip_p(-np.asarray(d))))


def analyze(rows: list[dict], need: int = 32) -> dict:
    per = {}
    for x in rows:
        if x.get("exp_id") == EXP and x.get("condition") in CELLS and x.get("status") in ("record", "control"):
            per.setdefault(x["run_id"], {})[x["condition"]] = x
    runs = sorted(k for k, v in per.items() if all(c in v for c in CELLS))
    out = {"version": VERSION, "n_complete_runs": len(runs), "runs": runs, "alpha": ALPHA,
           "p_method": T.signflip_method(len(runs))}
    if len(runs) < 2:
        out["outcome"] = "INDETERMINATE"
        return out
    Y = {c: np.array([per[k][c]["held_auc"] for k in runs]) for c in CELLS}
    out["means_held_auc"] = {c: float(Y[c].mean()) for c in CELLS}
    sign = lambda i, cell: 1.0 if bits_of(cell)[i] else -1.0
    effects, ps = {}, {}
    for i, comp in enumerate(COMPONENTS):
        e = sum(sign(i, c) * Y[c] for c in CELLS) / 4.0
        effects[comp] = float(e.mean())
        ps[comp] = T.signflip_p(e)
    adj = H.holm(ps)
    out["main_effects"] = {comp: {"effect": effects[comp], "p": ps[comp], "p_holm": adj[comp]} for comp in COMPONENTS}
    inter = {}
    for i, j in ((0, 1), (0, 2), (1, 2)):
        e = sum(sign(i, c) * sign(j, c) * Y[c] for c in CELLS) / 4.0
        inter[f"{COMPONENTS[i]}x{COMPONENTS[j]}"] = {"effect": float(e.mean()), "p_two_sided": _two_sided(e)}
    e3 = sum(sign(0, c) * sign(1, c) * sign(2, c) * Y[c] for c in CELLS) / 4.0
    inter["WxbxC"] = {"effect": float(e3.mean()), "p_two_sided": _two_sided(e3)}
    out["interactions_descriptive"] = inter
    out["vs_scratch_descriptive"] = {c: {"diff_mean": float((Y[c] - Y["W0b0C0"]).mean()),
                                         "p_above": T.signflip_p(Y[c] - Y["W0b0C0"])} for c in CELLS[1:]}
    out["donor_minus_scratch_vs_H1"] = {"here": float((Y["W1b1C1"] - Y["W0b0C0"]).mean()), "H1_L0_minus_scratch": H1_L0_MINUS_SCRATCH}
    for extra in ("held64", "zero_shot_held64", "train_auc"):
        out[f"means_{extra}"] = {c: float(np.mean([per[k][c][extra] for k in runs])) for c in CELLS}
    integ = [per[k][c]["cell_integrity"]["ok"] for k in runs for c in CELLS]
    out["integrity_ok"] = f"{sum(integ)}/{len(integ)}"
    out["donor_fused_eq_numpy"] = f"{sum(bool(per[k]['W1b1C1'].get('donor_fused_eq_numpy')) for k in runs)}/{len(runs)}"
    carriers = [comp for comp in COMPONENTS if adj[comp] < ALPHA]
    out["carriers"] = carriers
    out["outcome"] = "INDETERMINATE" if len(runs) < need else ("CARRIERS_" + "+".join(carriers) if carriers else "CARRIERS_NONE")
    return out


def sample_block(families=FAMILIES, run_seeds=RUN_SEEDS) -> dict:
    return V.sample_block(list(families), list(run_seeds))


ENVELOPE = {"campaign_stage": "PRODUCTION", "checkpointable": True, "cohort": "E", "cpu_budget_s": 36000,
            "evidence_class": "OBSERVATION", "expected_output_rows": 32 * len(CELLS) + 1,
            "experiment_class": "SHAM_RESPONSE", "gpu_budget_s": 0, "predicate_id": EXP,
            "required_controls": ["scratch_cell_W0b0C0", "donor_cell_W1b1C1", "component_swaps"],
            "required_oracles": ["world", "brain", "donor_fused_eq_numpy", "cell_integrity"],
            "wall_budget_s": 2400, **sample_block()}


def job(ctx, families=FAMILIES, run_seeds=RUN_SEEDS, gens: int = GENS, batch: int = BATCH,
        campaign_stage: str = "PRODUCTION"):
    order = H.run_order(families, run_seeds)
    base = base_row(sample_block(families, run_seeds), campaign_stage, gens, batch)
    st = ctx.load_checkpoint() or {"done": {}, "cpu": {}}
    for i, (fam, rs) in enumerate(order):
        k = V.rid_key(fam, rs)
        if k in st["done"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        rows = run_one(fam, rs, base, gens, batch, oracles=(i == 0))
        st["cpu"][k] = rows.pop("_run_cpu_s")
        for c in CELLS:
            ctx.emit(rows[c])
        st["done"][k] = rows
        ctx.checkpoint(st)
    allrows = [r for k in st["done"] for r in st["done"][k].values()]
    got = analyze(allrows, need=len(order))
    ctx.emit(dict(base, kind="h1b_analysis", status="record", condition="analysis",
                  run_cpu_s_median=float(np.median(list(st["cpu"].values()))) if st["cpu"] else None, **got))


def dev(gens: int = 4, batch: int = 32) -> dict:
    base = base_row(sample_block(), "SMOKE", gens, batch)
    t0 = time.perf_counter()
    rows = run_one(4200, 32, base, gens, batch, oracles=True)
    cpu = rows.pop("_run_cpu_s")
    return {"gens": gens, "batch": batch, "run_cpu_s": cpu, "wall_s": time.perf_counter() - t0,
            "integrity": {c: rows[c]["cell_integrity"]["ok"] for c in CELLS},
            "fused_eq": rows["W1b1C1"]["donor_fused_eq_numpy"]}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        g = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        b = int(sys.argv[3]) if len(sys.argv) > 3 else 32
        print(json.dumps(dev(g, b), indent=1, default=str))
