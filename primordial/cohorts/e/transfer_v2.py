"""E-R5-1: hardened Clause B control clauseB_ctrl_v2_featperm (preregistered bus 1789467311525-0; SWARM_R5 s3, O1, O6).
E-R7-1: the RNG FAMILY axis (operator 23 ruling: CANDIDATE_N binds Clause B; SWARM_R7 O1 EVIDENCE_N_v1).

E-R4-1 (receipt INDETERMINATE, eff6ec294) showed the v1 cheat rand_graft LOST to scratch at w13 train128 (13/16 run
seeds, p .0012), so beating it proved nothing. v2 reads a graft against two controls, paired per run:

  scratch   16 fresh init genomes in the K slots (equal budget: same filler, same mutation stream);
  sham      the SAME donor top-16 with the linear weight W (D x A) row-permuted along the observation-feature axis by a
            seeded DERANGEMENT (every feature moves). Kept exactly: every W value, each action column's value multiset
            (so its norm), the zero count, the bias b, the action codebook C (decoder), genome bytes. Destroyed: which
            observation feature drives which logit (sham(x) == graft(x displaced)).

Family axis (E-R7-1). A run is (rng_family F, run_seed rs). Every stream of the run is prefixed by F:
PCG64([F, 1701, rs, donor]) donor evolve, [F, 1705, rs, recipient] filler, [F, 1704, rs, recipient] common mutation stream,
[F, 1706, rs, recipient] sham derangement, [F, 1702, ...] self donor, [F, 1707, ...] random donor. rng_family=None keeps the
round 5/6 streams and checkpoint keys exactly (E-R6-1 rows reproduce). Rows carry rng_family + run_id 'F|rs'; check_b v2
pairs scratch/graft/sham within (family, run seed). Jobs stamp the sample block: runs_total, rng_family_count,
runs_per_family, families, n_per_family (EVIDENCE_N_v1: 32 / 4 / 8 balanced for a verdict).

The judge is score.transfer_b (rows stamped control_version): PASS iff the graft beats BOTH (one-sided sign-flip, exact
n <= 20 else seeded Monte Carlo, p_max, Holm across pairs) with gates clean. The E-T1 harness (transfer.evolve/score) is
reused unchanged.

Validation (SMOKE): donor_mode "self" (w13-evolved on a disjoint stream: planted positive, must PASS) and "random" (an
untrained init genome: planted negative, must not PASS). R7: at 32/4/8 (VAL7). The live pair runs in the round clock.

    python -m primordial.fabric.worker submit E primordial.cohorts.e.transfer_v2:validation_job \\
        --exp E-R7-1-val-positive --rows primordial/ledger/rows/E/E-R7-1-val-positive.jsonl --ttl-cpu-s 900 \\
        --kwargs '{"mode": "positive", "families": [4200, 2101, 3303, 5501]}'
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
FAMILIES7 = (4200, 2101, 3303, 5501)                                        # SWARM_R7 O1 / operator 16 family order
VAL = {"recipient": 13, "pressure": "train128_held64", "run_seeds": tuple(range(100, 108)), "gens": 50, "batch": 64}
VAL7 = dict(VAL, families=FAMILIES7)


def _s(rng_family, *parts) -> list:
    """A run stream's PCG64 seed list: the round 5/6 list when rng_family is None, else prefixed by the family."""
    return [int(x) for x in parts] if rng_family is None else [int(rng_family)] + [int(x) for x in parts]


def run_ids(families, run_seeds) -> list:
    """[(F or None, rs)] in family order then run seed order."""
    return [(None, int(rs)) for rs in run_seeds] if families is None else \
        [(int(f), int(rs)) for f in families for rs in run_seeds]


def rid_key(fam, rs) -> str:
    return str(int(rs)) if fam is None else f"{int(fam)}|{int(rs)}"


def sample_block(families, run_seeds) -> dict:
    fams = [None] if families is None else [int(f) for f in families]
    out = {"runs_total": len(fams) * len(run_seeds), "rng_family_count": len(fams), "runs_per_family": len(run_seeds)}
    if families is not None:
        out.update(families=fams, n_per_family={str(f): len(run_seeds) for f in fams})
    return out


# ------------------------------------------------------------------ the sham
def derangement(D: int, rng) -> np.ndarray:
    if D < 2:
        raise ValueError(f"no derangement of {D} features")
    while True:
        p = rng.permutation(D)
        if np.all(p != np.arange(D)):
            return p


def featperm(g7: E7.G7, raw: np.ndarray, rs: int, recipient: int, rng_family=None) -> tuple[np.ndarray, np.ndarray]:
    """Donor packed genomes [K, glen] -> (sham packed [K, glen], perm). W'[:, f] = W[:, perm[f]] for every genome."""
    if g7.fam.name != "linear":
        raise ValueError(f"featperm sham is defined for the linear family, not {g7.fam.name}")
    (W, b), C = g7.unpack(raw)
    perm = derangement(W.shape[1], np.random.Generator(np.random.PCG64(_s(rng_family, 1706, rs, recipient))))
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


# ------------------------------------------------------------------ one paired run
def run_seed(donor_mode: str, donor: int, recipient: int, family: str, rs: int, gens: int, batch: int, n_train: int,
             base: dict, oracles: bool = False, rng_family=None) -> tuple[dict, dict]:
    if donor_mode not in DONOR_MODES:
        raise ValueError(f"donor_mode {donor_mode!r}")
    gb = E7.G7(recipient, family)
    train = np.arange(9100, 9100 + n_train, dtype=np.int64)
    pcg = lambda *parts: np.random.Generator(np.random.PCG64(_s(rng_family, *parts)))
    if donor_mode == "world":
        ga = E7.G7(donor, family)
        ok, why = T.compatible(ga, gb)
        if not ok:
            raise ValueError(why)
        dA = T.evolve(ga, family, train, gens, batch, pcg(1701, rs, donor))[0].top()
    elif donor_mode == "self":
        dA = T.evolve(gb, family, train, gens, batch, pcg(1702, rs + 1000, recipient))[0].top()
    else:
        dA = gb.pack(gb.init(pcg(1707, rs, recipient), T.TOP))
    filler = gb.pack(gb.init(pcg(1705, rs, recipient), batch))
    sham, perm = featperm(gb, dA, rs, recipient, rng_family)
    slots = {"scratch": filler[:T.TOP].copy(), "graft": dA, "sham": sham}
    ids = {} if rng_family is None else {"rng_family": int(rng_family), "run_id": rid_key(rng_family, rs)}
    rows, curves = {}, {}
    for cond in CONDITIONS:
        gen0 = filler.copy()
        gen0[:T.TOP] = slots[cond]
        rng = pcg(1704, rs, recipient)                                          # common stream per run
        arch, curve, hcurve = T.evolve(gb, family, train, gens, batch, rng, gen0, held=T.HELD64)
        row = dict(base, status=STATUS[cond], condition=cond, run_seed=rs, **ids, cells=len(arch),
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
    """Paired runs needed for a one-sided test at (alpha, power), normal approximation from the observed diffs.
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
    out = dict(base, status="record", condition="summary", run_seeds=list(run_seeds),
               p_method=T.signflip_method(len(per["graft"])))
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


def _runs(ctx, donor_mode, donor, recipient, family, families, run_seeds, gens, batch, n_train, base):
    """Every (family, run seed) with an F9 checkpoint per run; returns (per-condition row lists, run keys, walls)."""
    ids = run_ids(families, run_seeds)
    st = ctx.load_checkpoint() or {"done": {}, "wall": {}}
    for i, (fam, rs) in enumerate(ids):
        k = rid_key(fam, rs)
        if k in st["done"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        t0 = time.perf_counter()
        rows, _ = run_seed(donor_mode, donor, recipient, family, rs, gens, batch, n_train, base, oracles=i == 0,
                           rng_family=fam)
        for c in CONDITIONS:
            ctx.emit(rows[c])
        st["done"][k], st["wall"][k] = rows, time.perf_counter() - t0
        ctx.checkpoint(st)
    keys = [rid_key(f, rs) for f, rs in ids]
    per = {c: [st["done"][k][c] for k in keys] for c in CONDITIONS}
    return st, per, keys


# ------------------------------------------------------------------ validation job (planted positive / negative)
def validation_job(ctx, mode: str = "positive", recipient: int = VAL["recipient"], pressure: str = VAL["pressure"],
                   run_seeds=VAL["run_seeds"], gens: int = VAL["gens"], batch: int = VAL["batch"], family: str = "linear",
                   exp: str | None = None, campaign_stage: str = "SMOKE", families=None):
    """Planted positive ('positive': self donor, must PASS) or planted negative ('negative': random donor, must not
    PASS). Rows per run (F9 checkpoint each), a summary, and check-b's verdict on these rows (report).
    families=None: the round 5 single stream; E-R7-1: FAMILIES7 x run_seeds (32/4/8)."""
    from primordial.metric import floors as F
    from primordial.score.transfer_b import check_b
    donor_mode = {"positive": "self", "negative": "random"}[mode]
    exp = exp or (f"E-R5-1-val-{mode}" if families is None else f"E-R7-1-val-{mode}")
    n_train = len(F.PRESSURES[pressure])
    run_seeds = [int(s) for s in run_seeds]
    base = dict(base_row(donor_mode, recipient, recipient, family, pressure, gens, batch, n_train, f"val-{mode}"),
                campaign_stage=campaign_stage, expected="PASS" if mode == "positive" else "NOT_PASS",
                **sample_block(families, run_seeds))
    st, per, keys = _runs(ctx, donor_mode, recipient, recipient, family, families, run_seeds, gens, batch, n_train, base)
    summ = summarize(base, per, keys, [st["wall"][k] for k in keys])
    ctx.emit(summ)
    rows = [dict(r, exp_id=exp) for k in keys for r in st["done"][k].values()] + [dict(summ, exp_id=exp)]
    got = check_b(rows)
    verdict = got["pairs"][0]["verdict"] if got["pairs"] else "INDETERMINATE"
    ctx.emit({"kind": "check_b", "status": "record", "report_only": True, "exp_id": exp, "control_version": CONTROL_VERSION,
              "mode": mode, "expected": base["expected"], "verdict": verdict, **sample_block(families, run_seeds),
              "as_expected": (verdict == "PASS") if mode == "positive" else (verdict != "PASS"), **got})


# ------------------------------------------------------------------ the live pair (O1 + O6; R7: 32/4/8)
LIVE = {"recipient": 13, "pressure": "train128_held64", "run_seeds": tuple(range(16, 32)), "gens": 800, "batch": 128}
LIVE7 = dict(LIVE, run_seeds=tuple(range(16, 24)), families=FAMILIES7)


def live_job(ctx, donor: int | None = None, recipient: int = LIVE["recipient"], pressure: str = LIVE["pressure"],
             run_seeds=LIVE["run_seeds"], gens: int = LIVE["gens"], batch: int = LIVE["batch"], family: str = "linear",
             exp: str | None = None, campaign_stage: str = "PILOT", families=None):
    """The ONE live Clause B pair: donor = first o1_donors() entry (code rule, never chosen), run seeds checked disjoint
    from any earlier use of the pair (check_seeds), M2 budget. Rows per run (F9 checkpoint each), summary, check-b.
    families=None: round 5/6 single stream; E-R7-1 (in the clock): LIVE7 = FAMILIES7 x run seeds 16..23."""
    from primordial.metric import floors as F
    from primordial.score.transfer_b import check_b
    donors = o1_donors(f"w{recipient}", pressure, family)
    if donor is None:
        donor = donors[0]
    elif int(donor) != donors[0]:
        raise ValueError(f"O1: the live donor is the first o1_donors() entry {donors[0]}, not {donor}")
    run_seeds = [int(s) for s in run_seeds]
    check_seeds(donor, recipient, run_seeds)
    exp = exp or f"E-R5-1-live-w{donor}-w{recipient}"
    n_train = len(F.PRESSURES[pressure])
    base = dict(base_row("world", donor, recipient, family, pressure, gens, batch, n_train, "live"),
                campaign_stage=campaign_stage, o1_donors=donors, **sample_block(families, run_seeds))
    st, per, keys = _runs(ctx, "world", donor, recipient, family, families, run_seeds, gens, batch, n_train, base)
    summ = summarize(base, per, keys, [st["wall"][k] for k in keys])
    ctx.emit(summ)
    rows = [dict(r, exp_id=exp) for k in keys for r in st["done"][k].values()] + [dict(summ, exp_id=exp)]
    got = check_b(rows)
    ctx.emit({"kind": "check_b", "status": "record", "exp_id": exp, "control_version": CONTROL_VERSION,
              "verdict": got["pairs"][0]["verdict"] if got["pairs"] else "INDETERMINATE", **got})
