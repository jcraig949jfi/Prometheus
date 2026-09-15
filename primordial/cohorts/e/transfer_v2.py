"""E-R5-1: hardened Clause B control clauseB_ctrl_v2_featperm (preregistered bus 1789467311525-0; SWARM_R5 s3, O1, O6).

E-R4-1 (receipt INDETERMINATE, eff6ec294) showed the v1 cheat rand_graft LOST to scratch at w13 train128 (13/16 run
seeds, p .0012), so beating it proved nothing. v2 reads a graft against two controls, paired per run seed:

  scratch   16 fresh init genomes in the K slots (equal budget: same filler, same mutation stream);
  sham      the SAME donor top-16 with the linear weight W (D x A) row-permuted along the observation-feature axis by a
            seeded DERANGEMENT (PCG64([1706, rs, recipient]); every feature moves). Kept exactly: every W value, each
            action column's value multiset (so its norm), the zero count, the bias b, the action codebook C (decoder),
            genome bytes. Destroyed: which observation feature drives which logit (sham(x) == graft(x displaced)).

The judge is score.transfer_b (rows stamped control_version): PASS iff the graft beats BOTH (one-sided exact
sign-flip, p_max, Holm across pairs) with gates clean. The E-T1 harness (transfer.evolve/score) is reused unchanged.

Validation (P-BUILD, SMOKE): donor_mode "self" (w13-evolved on a disjoint stream: planted positive, must PASS) and
"random" (an untrained init genome: planted negative, must not PASS). The live pair is a round 5 pilot job:
o1_donors() (O1 rule) + check_seeds() (pairs seen before run only on run seeds >= 16).

    python -m primordial.fabric.worker submit E primordial.cohorts.e.transfer_v2:validation_job \\
        --exp E-R5-1-val-positive --rows primordial/ledger/rows/E/E-R5-1-val-positive.jsonl --ttl-cpu-s 450 \\
        --kwargs '{"mode": "positive"}'
"""
from __future__ import annotations

import time

import numpy as np

from primordial.cohorts.e import transfer as T
from primordial.qd import e7_run as E7
from primordial.soup.b6.fused import FusedRollout

CONTROL_VERSION = "clauseB_ctrl_v2_featperm"
CONDITIONS = ("scratch", "graft", "sham")
STATUS = {"scratch": "record", "graft": "record", "sham": "cheat"}
DONOR_MODES = ("world", "self", "random")
SEEN = {(14, 13): frozenset(range(16)), (20, 13): frozenset(range(16))}     # E-R4-1 (linear, w13 train128_held64)
LIVE_MIN_SEED = 16
VAL = {"recipient": 13, "pressure": "train128_held64", "run_seeds": tuple(range(100, 108)), "gens": 50, "batch": 64}


# ------------------------------------------------------------------ the sham
def derangement(D: int, rng) -> np.ndarray:
    if D < 2:
        raise ValueError(f"no derangement of {D} features")
    while True:
        p = rng.permutation(D)
        if np.all(p != np.arange(D)):
            return p


def featperm(g7: E7.G7, raw: np.ndarray, rs: int, recipient: int) -> tuple[np.ndarray, np.ndarray]:
    """Donor packed genomes [K, glen] -> (sham packed [K, glen], perm). W'[:, f] = W[:, perm[f]] for every genome."""
    if g7.fam.name != "linear":
        raise ValueError(f"featperm sham is defined for the linear family, not {g7.fam.name}")
    (W, b), C = g7.unpack(raw)
    perm = derangement(W.shape[1], np.random.Generator(np.random.PCG64([1706, int(rs), int(recipient)])))
    return g7.pack(((W[:, perm, :].copy(), b), C)), perm


def sham_integrity(g7: E7.G7, graft_raw: np.ndarray, sham_raw: np.ndarray, perm) -> dict:
    """Exact checks that the sham kept the nuisance structure and moved every feature."""
    (W, b), C = g7.unpack(graft_raw)
    (Ws, bs), Cs = g7.unpack(sham_raw)
    perm = np.asarray(perm)
    col = lambda X: np.sort(X, axis=1)                                         # per genome, per action column
    out = {"derangement": bool(len(perm) >= 2 and np.all(perm != np.arange(len(perm)))),
           "is_row_permutation": bool(np.array_equal(Ws, W[:, perm, :])),
           "values_multiset": bool(np.array_equal(np.sort(W.reshape(len(W), -1), 1), np.sort(Ws.reshape(len(Ws), -1), 1))),
           "column_multisets": bool(np.array_equal(col(W), col(Ws))),
           "zero_count": bool(np.array_equal((W == 0).sum((1, 2)), (Ws == 0).sum((1, 2)))),
           "bias_bytes": bool(np.array_equal(b.view(np.uint8), bs.view(np.uint8))),
           "codebook_bytes": bool(np.array_equal(C, Cs)),
           "genome_bytes": int(sham_raw.shape[1]) == int(graft_raw.shape[1]),
           "mapping_changed": bool(not np.array_equal(W, Ws))}
    out["ok"] = all(v for k, v in out.items())
    return out


# ------------------------------------------------------------------ O1 donor rule
def o1_donors(recipient_world: str = "w13", pressure: str = "train128_held64", family: str = "linear", doc=None) -> list[int]:
    """Screened worlds (on worlds_r4.json) whose genome layout (D, A, W, bytes) equals the recipient's, gen_seed order.
    The recipient must be SURVIVED under the file's active variant. The ONE candidate is the first."""
    from primordial.metric import worlds as WR
    doc = WR.load() if doc is None else doc
    g = WR.guard(doc, recipient_world, pressure)
    if g is not None:
        raise ValueError(f"recipient {recipient_world} {pressure} is not SURVIVED: {g['why']}")
    rgs = next(c["gen_seed"] for c in doc["cells"] if c["world"] == recipient_world and c["pressure"] == pressure)
    gb = E7.G7(int(rgs), family)
    seen = sorted({int(c["gen_seed"]) for c in doc["cells"]} - {int(rgs)})
    return [gs for gs in seen if T.compatible(E7.G7(gs, family), gb)[0]]


def check_seeds(donor: int, recipient: int, run_seeds) -> None:
    """O1: a pair seen before runs only on run seeds disjoint from those used before (and >= LIVE_MIN_SEED)."""
    used = SEEN.get((int(donor), int(recipient)), frozenset())
    bad = sorted(set(int(s) for s in run_seeds) & used)
    if bad:
        raise ValueError(f"w{donor}->w{recipient} already ran on run seeds {bad}; use seeds >= {LIVE_MIN_SEED}")


# ------------------------------------------------------------------ one paired run seed
def run_seed(donor_mode: str, donor: int, recipient: int, family: str, rs: int, gens: int, batch: int, n_train: int,
             base: dict, oracles: bool = False) -> tuple[dict, dict]:
    if donor_mode not in DONOR_MODES:
        raise ValueError(f"donor_mode {donor_mode!r}")
    gb = E7.G7(recipient, family)
    train = np.arange(9100, 9100 + n_train, dtype=np.int64)
    if donor_mode == "world":
        ga = E7.G7(donor, family)
        ok, why = T.compatible(ga, gb)
        if not ok:
            raise ValueError(why)
        dA = T.evolve(ga, family, train, gens, batch, np.random.Generator(np.random.PCG64([1701, rs, donor])))[0].top()
    elif donor_mode == "self":
        dA = T.evolve(gb, family, train, gens, batch, np.random.Generator(np.random.PCG64([1702, rs + 1000, recipient])))[0].top()
    else:
        dA = gb.pack(gb.init(np.random.Generator(np.random.PCG64([1707, rs, recipient])), T.TOP))
    filler = gb.pack(gb.init(np.random.Generator(np.random.PCG64([1705, rs, recipient])), batch))
    sham, perm = featperm(gb, dA, rs, recipient)
    slots = {"scratch": filler[:T.TOP].copy(), "graft": dA, "sham": sham}
    rows, curves = {}, {}
    for cond in CONDITIONS:
        gen0 = filler.copy()
        gen0[:T.TOP] = slots[cond]
        rng = np.random.Generator(np.random.PCG64([1704, rs, recipient]))      # common stream per run seed
        arch, curve, hcurve = T.evolve(gb, family, train, gens, batch, rng, gen0, held=T.HELD64)
        row = dict(base, status=STATUS[cond], condition=cond, run_seed=rs, cells=len(arch),
                   held_auc=float(hcurve.mean()), held_curve=[round(float(x), 3) for x in hcurve],
                   train_auc=float(curve.mean()), train_final=float(curve[-1]),
                   zero_shot_held64=T.score(gb, family, gen0[:T.TOP], T.HELD64), held64=float(hcurve[-1]),
                   slot_sha256=T.sha(gen0[:T.TOP]))
        if cond == "graft":
            row["donor_sha256"] = T.sha(dA)
            row["graft_bytes_unmodified"] = row["slot_sha256"] == row["donor_sha256"]
            np_fit = E7.rollout(gb, gb.unpack(dA), train)[0]
            fu_fit = FusedRollout(gb.spec, T.TOP, train, family=family).run(gb.unpack(dA))[0]
            row["graft_fused_eq_numpy"] = bool(np.array_equal(np_fit, fu_fit))
            if oracles:
                tg = gb.unpack(arch.top())
                row["world_oracle_honest"] = E7.world_oracle(gb, tg, T.HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(gb, tg, T.HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(gb, tg, T.HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(gb, tg, T.HELD8, cheat=True)
        if cond == "sham":
            row["sham_perm"] = [int(x) for x in perm]
            row["sham_integrity"] = sham_integrity(gb, dA, sham, perm)
        rows[cond], curves[cond] = row, curve
    return rows, curves


def base_row(donor_mode: str, donor: int, recipient: int, family: str, pressure: str, gens: int, batch: int,
             n_train: int, tag: str) -> dict:
    return {"control_version": CONTROL_VERSION, "donor_mode": donor_mode, "tag": tag, "family": family,
            "donor_world": int(donor), "recipient_world": int(recipient), "pressure": pressure, "gens": gens,
            "batch": batch, "train_seeds": n_train, "genome_bytes": E7.G7(recipient, family).glen, "top_k": T.TOP,
            "checkpoints": T.checkpoints(gens).tolist()}


def power_n(d, alpha: float = 0.05, power: float = 0.8) -> float | None:
    """Paired run seeds needed for a one-sided test at (alpha, power), normal approximation from the observed diffs.
    None when the observed mean is <= 0 (no effect in the right direction to power)."""
    from statistics import NormalDist
    d = np.asarray(d, float)
    if len(d) < 2 or d.mean() <= 0:
        return None
    sd = d.std(ddof=1)
    if sd == 0:
        return 2.0
    z = NormalDist().inv_cdf(1 - alpha) + NormalDist().inv_cdf(power)
    return float(np.ceil((z * sd / d.mean()) ** 2))


def summarize(base: dict, per: dict, run_seeds, cpu_s_per_seed=None) -> dict:
    col = lambda c: np.array([r["held_auc"] for r in per[c]])
    out = dict(base, status="record", condition="summary", run_seeds=list(run_seeds))
    for other in ("scratch", "sham"):
        d = col("graft") - col(other)
        out[f"graft_vs_{other}_held_auc_diff_mean"] = float(d.mean())
        out[f"graft_vs_{other}_held_auc_p"] = T.signflip_p(d)
        out[f"power_n_vs_{other}"] = power_n(d)
    out["graft_vs_controls_held_auc_p_max"] = max(out["graft_vs_scratch_held_auc_p"], out["graft_vs_sham_held_auc_p"])
    ds = col("sham") - col("scratch")
    out["sham_vs_scratch_held_auc_diff_mean"] = float(ds.mean())
    out["sham_below_scratch_p"] = T.signflip_p(-ds)                               # the E-R4-1 defect, reported
    out["medians"] = {c: float(np.median(col(c))) for c in CONDITIONS}
    if cpu_s_per_seed:
        out["wall_s_per_run_seed"] = float(np.median(cpu_s_per_seed))
    return out


# ------------------------------------------------------------------ P-BUILD validation job
def validation_job(ctx, mode: str = "positive", recipient: int = VAL["recipient"], pressure: str = VAL["pressure"],
                   run_seeds=VAL["run_seeds"], gens: int = VAL["gens"], batch: int = VAL["batch"], family: str = "linear",
                   exp: str | None = None, campaign_stage: str = "SMOKE"):
    """Planted positive ('positive': self donor, must PASS) or planted negative ('negative': random donor, must not
    PASS). Rows per run seed (F9 checkpoint each), a summary, and check-b's verdict on these rows (report)."""
    from primordial.metric import floors as F
    from primordial.score.transfer_b import check_b
    donor_mode = {"positive": "self", "negative": "random"}[mode]
    exp = exp or f"E-R5-1-val-{mode}"
    n_train = len(F.PRESSURES[pressure])
    base = dict(base_row(donor_mode, recipient, recipient, family, pressure, gens, batch, n_train, f"val-{mode}"),
                campaign_stage=campaign_stage, expected="PASS" if mode == "positive" else "NOT_PASS")
    run_seeds = [int(s) for s in run_seeds]
    st = ctx.load_checkpoint() or {"done": {}, "wall": {}}
    for rs in run_seeds:
        if str(rs) in st["done"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        t0 = time.perf_counter()
        rows, _ = run_seed(donor_mode, recipient, recipient, family, rs, gens, batch, n_train, base,
                           oracles=rs == run_seeds[0])
        for c in CONDITIONS:
            ctx.emit(rows[c])
        st["done"][str(rs)], st["wall"][str(rs)] = rows, time.perf_counter() - t0
        ctx.checkpoint(st)
    per = {c: [st["done"][str(s)][c] for s in run_seeds] for c in CONDITIONS}
    summ = summarize(base, per, run_seeds, [st["wall"][str(s)] for s in run_seeds])
    ctx.emit(summ)
    rows = [dict(r, exp_id=exp) for s in run_seeds for r in st["done"][str(s)].values()] + [dict(summ, exp_id=exp)]
    got = check_b(rows)
    verdict = got["pairs"][0]["verdict"] if got["pairs"] else "INDETERMINATE"
    ctx.emit({"kind": "check_b", "status": "record", "report_only": True, "exp_id": exp, "control_version": CONTROL_VERSION,
              "mode": mode, "expected": base["expected"], "verdict": verdict,
              "as_expected": (verdict == "PASS") if mode == "positive" else (verdict != "PASS"), **got})
