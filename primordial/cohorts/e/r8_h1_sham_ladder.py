"""E-R8-H1 (SWARM_R8 s7, prompts_r8/E.md item 1): the SHAM RESPONSE CURVE. Preregistered before any run.

Why. Round 7's first admissible Clause B verdict (E-R7-1, receipt 1789514378793-0) was FAIL: on w14 -> w13 the
feature-permuted sham (clauseB_ctrl_v2_featperm) beat the unmodified graft (graft - sham -0.662) and beat scratch by
MORE than the graft did (sham - scratch +1.400). That FAIL STANDS and is not relabelled here. H1 asks a different
question: does recipient performance vary SYSTEMATICALLY with the destruction of donor structure?

Nothing here is a Clause B control, a Clause B verdict, or a transfer claim. evidence_class OBSERVATION. No arm is
applied to any live pair as a control; a changed control would be recalibrated (O8-style) before that, in a later round.

Pair and budget (E-R7-1 exactly, except run seeds): donor w14 (o1_donors()[0]), recipient w13 train128_held64, linear
family, M2 budget gens 800 x batch 128, K = 16 slots, the E-T1 loop (transfer.evolve) and readout unchanged.
Sample: families 4200/2101/3303/5501 x run seeds 24..31 (32/4/8; disjoint from E-R7-1's 16..23, E-R6-1's 16..31
single-stream, E-R4-1's 0..15). Streams are transfer_v2's family-prefixed PCG64 lists: donor [F,1701,rs,14], filler
[F,1705,rs,13], common mutation stream [F,1704,rs,13] (identical for every arm of a run), full featperm [F,1706,rs,13];
new H1 tags 1801-1803 (never used before). Run order: round-robin by run seed across families (24: F1..F4, 25: ...),
so a run stopped by the clock leaves a family-balanced prefix.

ARMS (all share one donor top-16 per run, one filler, one mutation stream; only the 16 slots differ):
  scratch              16 fresh init genomes (reference; NOT donor-derived, NOT on the ladder)
  L0_identity          donor top-16 bytes unmodified (== transfer_v2 "graft")
  L1_partial_featperm  W columns permuted over a seeded 3-of-5 feature subset by a derangement of that subset
                       (3 features move, 2 stay): subset = rng.choice(5, 3, replace=False), rng [F,1801,rs,13]
  L2_full_featperm     transfer_v2.featperm exactly (derangement of all 5 features, stream 1706) == R7's sham
  L3_entry_shuffle     each genome's 40 W entries permuted by ONE common derangement of the 40 positions
                       (rng [F,1802,rs,13]): row vectors AND column multisets destroyed; exact per-genome value
                       multiset, norm, zero count, and every between-genome W distance kept
  L4_matched_gaussian  W replaced by fresh N(0,1) draws (rng [F,1803,rs,13]) standardised per genome to mean 0 / sd 1,
                       then set to the donor genome's own W mean and sd (float32): only gross scale kept
  X_charge_align       STRUCTURAL DISCRIMINATOR, not on the ladder: the donor's charge column (obs column c with
                       obs_perm[c] == D-1; w14: 3) swapped with the recipient's charge column (w13: 2). Charge is the
                       ONLY observation channel whose meaning is common to both worlds (the register channels read
                       world-specific registers under world-specific dynamics), and the identity graft reads it from
                       the wrong column. Deterministic; identical to L0 if the columns coincide (flagged).
Every donor-derived arm keeps the bias b, the action codebook C and the genome length byte-exact.
Destruction ordinal (donor frame, fixed now): L0 0 < L1 1 < L2 2 < L3 3 < L4 4.
Per sham arm, charge_aligned = (the arm's W column at the recipient charge column is the donor's charge column).

RESPONSE: held_auc (check_b's primary: mean over geometric checkpoints of the archive top-16 held-out mean per seed).
Reported, not judged: held64 final, zero_shot_held64, train_auc, train_final.

ANALYSIS (fixed now; analyze(rows)), alpha 0.05, one-sided paired sign-flip = transfer.signflip_p (D25 canonical order;
exact n <= 20 else seeded MC 200000), all pairing within (family, run seed):
  T   trend: per run Spearman rho(ordinal 0..4, held_auc of L0..L4), average ranks on ties (a run with all 5 equal
      contributes rho 0). p_dec = signflip_p(-rho), p_inc = signflip_p(rho).
  N   non-monotonicity: for each interior level k in {1,2,3}: peak_k p = max(p(L_k > L0), p(L_k > L4)) and
      trough_k p = max(p(L_k < L0), p(L_k < L4)) (intersection-union); Holm over these 6.
  OUTCOME (first that applies):
      C_NONMONOTONIC                 any Holm-adjusted peak/trough p < 0.05
      A_DECREASING_WITH_DESTRUCTION  p_dec < 0.05
      B_INCREASING_WITH_DESTRUCTION  p_inc < 0.05
      FLAT_NO_SYSTEMATIC_RESPONSE    otherwise (at this N; not evidence of no response)
      INDETERMINATE                  fewer than 32 complete runs (no classification on a partial sample)
  S   structural discriminator: d = held_auc(X_charge_align) - held_auc(L0); CHARGE_ALIGNMENT_RAISES iff
      signflip_p(d) < 0.05, CHARGE_ALIGNMENT_LOWERS iff signflip_p(-d) < 0.05, else CHARGE_ALIGNMENT_NO_EFFECT.
  Reported only: every arm - scratch (mean, one-sided p), adjacent-level diffs, L2 - L0 and L2 - scratch beside
  E-R7-1's (-0.662 graft - sham, +1.400 sham - scratch), L1/L2 split by charge_aligned (descriptive, never judged).
  WORDING: none of A/B/C/S may be called "transfer".
Integrity (every run): slot bytes == donor bytes for L0; per-arm integrity dict (below) ok; donor fused == numpy.
Oracles (first run, L0 final top-16, E7 numpy on HELD8): world honest / skip_lin, brain honest / cheat.

    python -m primordial.cohorts.e.r8_h1_sham_ladder dev [gens]        # no rows: wiring + CPU per evolve
    python -m primordial.fabric.worker submit E primordial.cohorts.e.r8_h1_sham_ladder:job ...   (envelope in ENVELOPE)
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

from primordial.cohorts.e import transfer as T
from primordial.cohorts.e import transfer_v2 as V
from primordial.qd import e7_run as E7
from primordial.soup.b6.fused import FusedRollout

EXP = "E-R8-H1-sham-response-curve"
ROWS = f"primordial/ledger/rows/E/{EXP}.jsonl"
LADDER_VERSION = "h1_sham_ladder_v1"
LADDER = ("L0_identity", "L1_partial_featperm", "L2_full_featperm", "L3_entry_shuffle", "L4_matched_gaussian")
ARMS = ("scratch",) + LADDER + ("X_charge_align",)
ORDINAL = {a: i for i, a in enumerate(LADDER)}
STATUS = dict({a: "control" for a in ARMS}, scratch="record", L0_identity="record")
TAG_PARTIAL, TAG_SHUFFLE, TAG_GAUSS = 1801, 1802, 1803
PARTIAL_K = 3
DONOR, RECIPIENT, PRESSURE, FAMILY = 14, 13, "train128_held64", "linear"
FAMILIES = V.FAMILIES7
RUN_SEEDS = tuple(range(24, 32))
GENS, BATCH = V.LIVE["gens"], V.LIVE["batch"]
ALPHA = 0.05
R7_REFERENCE = {"graft_minus_sham": -0.6624374389648438, "sham_minus_scratch": 1.4003677368164062,
                "receipt": "1789514378793-0"}
OUTCOMES = ("C_NONMONOTONIC", "A_DECREASING_WITH_DESTRUCTION", "B_INCREASING_WITH_DESTRUCTION",
            "FLAT_NO_SYSTEMATIC_RESPONSE", "INDETERMINATE")


def run_order(families=FAMILIES, run_seeds=RUN_SEEDS) -> list[tuple[int, int]]:
    """Round-robin by run seed across families: a clock-stopped prefix stays family-balanced per completed seed."""
    return [(int(f), int(rs)) for rs in run_seeds for f in families]


def charge_col(g7: E7.G7) -> int:
    perm = list(g7.spec.mech.obs_perm)
    return perm.index(len(perm) - 1)


def _pcg(fam, *parts):
    return np.random.Generator(np.random.PCG64(V._s(fam, *parts)))


def derange_subset(D: int, k: int, rng) -> np.ndarray:
    """A permutation of range(D) that moves exactly the k features of a seeded subset (a derangement on the subset)."""
    sub = np.sort(rng.choice(D, size=k, replace=False))
    inner = V.derangement(k, rng)
    perm = np.arange(D)
    perm[sub] = sub[inner]
    return perm


def colperm(g7, raw, perm):
    (W, b), C = g7.unpack(raw)
    return g7.pack(((W[:, perm, :].copy(), b), C))


def make_arms(g7r: E7.G7, g7d: E7.G7, dA: np.ndarray, filler: np.ndarray, fam: int, rs: int) -> tuple[dict, dict]:
    """-> (slots {arm: packed [16, glen]}, meta {arm: {perm/charge_aligned/...}}). Pure function of the run streams."""
    D = g7r.D
    cr, cd = charge_col(g7r), charge_col(g7d)
    (W, b), C = g7r.unpack(dA)
    slots, meta = {"scratch": filler[:T.TOP].copy(), "L0_identity": dA.copy()}, {}
    ident = np.arange(D)
    meta["L0_identity"] = {"perm": ident.tolist(), "charge_aligned": bool(cd == cr)}
    p1 = derange_subset(D, PARTIAL_K, _pcg(fam, TAG_PARTIAL, rs, RECIPIENT))
    slots["L1_partial_featperm"] = colperm(g7r, dA, p1)
    meta["L1_partial_featperm"] = {"perm": p1.tolist(), "moved": int((p1 != ident).sum()),
                                   "charge_aligned": bool(p1[cr] == cd)}
    s2, p2 = V.featperm(g7r, dA, rs, RECIPIENT, fam)
    slots["L2_full_featperm"] = s2
    meta["L2_full_featperm"] = {"perm": [int(x) for x in p2], "moved": int((np.asarray(p2) != ident).sum()),
                                "charge_aligned": bool(p2[cr] == cd)}
    n = W.shape[1] * W.shape[2]
    p3 = V.derangement(n, _pcg(fam, TAG_SHUFFLE, rs, RECIPIENT))
    W3 = W.reshape(len(W), n)[:, p3].reshape(W.shape).copy()
    slots["L3_entry_shuffle"] = g7r.pack(((W3, b), C))
    meta["L3_entry_shuffle"] = {"position_perm_sha": T.sha(p3.astype(np.int64)), "charge_aligned": None}
    z = _pcg(fam, TAG_GAUSS, rs, RECIPIENT).standard_normal(W.shape)
    zf = z.reshape(len(W), -1)
    zf = (zf - zf.mean(1, keepdims=True)) / zf.std(1, keepdims=True)
    Wf = W.reshape(len(W), -1).astype(np.float64)
    W4 = (zf * Wf.std(1, keepdims=True) + Wf.mean(1, keepdims=True)).astype(np.float32).reshape(W.shape)
    slots["L4_matched_gaussian"] = g7r.pack(((W4, b), C))
    meta["L4_matched_gaussian"] = {"charge_aligned": None}
    px = ident.copy()
    px[cr], px[cd] = cd, cr
    slots["X_charge_align"] = colperm(g7r, dA, px)
    meta["X_charge_align"] = {"perm": px.tolist(), "charge_aligned": True, "identical_to_L0": bool(cd == cr),
                              "donor_charge_col": int(cd), "recipient_charge_col": int(cr)}
    return slots, meta


def arm_integrity(g7r: E7.G7, dA: np.ndarray, slots: dict, meta: dict) -> dict:
    """Exact nuisance checks per arm (b, C, genome length always; the arm-specific invariants on W)."""
    (W, b), C = g7r.unpack(dA)
    msort = lambda X: np.sort(X.reshape(len(X), -1), 1)
    out = {}
    for arm in ARMS[1:]:
        (Wa, ba), Ca = g7r.unpack(slots[arm])
        chk = {"bias_bytes": bool(np.array_equal(b.view(np.uint8), ba.view(np.uint8))),
               "codebook_bytes": bool(np.array_equal(C, Ca)),
               "genome_bytes": int(slots[arm].shape[1]) == int(dA.shape[1])}
        if arm == "L0_identity":
            chk["bytes_unmodified"] = T.sha(slots[arm]) == T.sha(dA)
        if arm in ("L1_partial_featperm", "L2_full_featperm", "X_charge_align"):
            perm = np.asarray(meta[arm]["perm"])
            chk["is_column_permutation"] = bool(np.array_equal(Wa, W[:, perm, :]))
            chk["column_multisets"] = bool(np.array_equal(np.sort(W, 1), np.sort(Wa, 1)))
        if arm == "L1_partial_featperm":
            chk["moved_k"] = meta[arm]["moved"] == PARTIAL_K
        if arm == "L2_full_featperm":
            chk["derangement"] = meta[arm]["moved"] == g7r.D
        if arm in ("L1_partial_featperm", "L2_full_featperm", "L3_entry_shuffle", "X_charge_align"):
            chk["values_multiset"] = bool(np.array_equal(msort(W), msort(Wa)))
            chk["zero_count"] = bool(np.array_equal((W == 0).sum((1, 2)), (Wa == 0).sum((1, 2))))
        if arm == "L3_entry_shuffle":
            flat, flata = W.reshape(len(W), -1).astype(np.float64), Wa.reshape(len(Wa), -1).astype(np.float64)
            dist = lambda X: np.sort((X[:, None] - X[None]) ** 2, -1).sum(-1)     # sorted terms: order-free sum
            chk["pairwise_dist"] = bool(np.array_equal(dist(flat), dist(flata)))
            chk["column_multisets_changed"] = bool(not np.array_equal(np.sort(W, 1), np.sort(Wa, 1)))
        if arm == "L4_matched_gaussian":
            f, fa = W.reshape(len(W), -1).astype(np.float64), Wa.reshape(len(Wa), -1).astype(np.float64)
            chk["mean_matched"] = bool(np.allclose(f.mean(1), fa.mean(1), atol=1e-4))
            chk["sd_matched"] = bool(np.allclose(f.std(1), fa.std(1), rtol=1e-4, atol=1e-5))
        if arm != "L0_identity":
            chk["mapping_changed"] = bool(not np.array_equal(W, Wa)) or bool(meta[arm].get("identical_to_L0"))
        chk["ok"] = all(v for v in chk.values())
        out[arm] = chk
    return out


def base_row(sample: dict, campaign_stage: str = "PRODUCTION", gens: int = GENS, batch: int = BATCH) -> dict:
    from primordial.metric import floors as F
    return {"exp_id": EXP, "ladder_version": LADDER_VERSION, "evidence_class": "OBSERVATION", "family": FAMILY,
            "donor_world": DONOR, "recipient_world": RECIPIENT, "pressure": PRESSURE, "gens": gens, "batch": batch,
            "train_seeds": len(F.PRESSURES[PRESSURE]), "genome_bytes": E7.G7(RECIPIENT, FAMILY).glen, "top_k": T.TOP,
            "checkpoints": T.checkpoints(gens).tolist(), "campaign_stage": campaign_stage, **sample}


def run_one(fam: int, rs: int, base: dict, gens: int = GENS, batch: int = BATCH, oracles: bool = False) -> dict:
    """One (family, run seed): the donor top-16 once, then every arm on the common filler + mutation stream."""
    from primordial.metric import floors as F
    g7r, g7d = E7.G7(RECIPIENT, FAMILY), E7.G7(DONOR, FAMILY)
    ok, why = T.compatible(g7d, g7r)
    if not ok:
        raise ValueError(why)
    train = np.arange(9100, 9100 + len(F.PRESSURES[PRESSURE]), dtype=np.int64)
    t0 = time.process_time()
    dA = T.evolve(g7d, FAMILY, train, gens, batch, _pcg(fam, 1701, rs, DONOR))[0].top()
    filler = g7r.pack(g7r.init(_pcg(fam, 1705, rs, RECIPIENT), batch))
    slots, meta = make_arms(g7r, g7d, dA, filler, fam, rs)
    integ = arm_integrity(g7r, dA, slots, meta)
    np_fit = E7.rollout(g7r, g7r.unpack(dA), train)[0]
    fu_fit = FusedRollout(g7r.spec, T.TOP, train, family=FAMILY).run(g7r.unpack(dA))[0]
    ids = {"rng_family": int(fam), "run_seed": int(rs), "run_id": V.rid_key(fam, rs)}
    rows = {}
    for arm in ARMS:
        gen0 = filler.copy()
        gen0[:T.TOP] = slots[arm]
        c0 = time.process_time()
        arch, curve, hcurve = T.evolve(g7r, FAMILY, train, gens, batch, _pcg(fam, 1704, rs, RECIPIENT), gen0,
                                       held=T.HELD64)
        row = dict(base, **ids, status=STATUS[arm], condition=arm, ordinal=ORDINAL.get(arm),
                   held_auc=float(hcurve.mean()), held_curve=[round(float(x), 3) for x in hcurve],
                   train_auc=float(curve.mean()), train_final=float(curve[-1]), held64=float(hcurve[-1]),
                   zero_shot_held64=T.score(g7r, FAMILY, gen0[:T.TOP], T.HELD64), cells=len(arch),
                   slot_sha256=T.sha(gen0[:T.TOP]), donor_sha256=T.sha(dA), arm_cpu_s=time.process_time() - c0)
        if arm != "scratch":
            row["arm_meta"] = meta[arm]
            row["arm_integrity"] = integ[arm]
        if arm == "L0_identity":
            row["donor_fused_eq_numpy"] = bool(np.array_equal(np_fit, fu_fit))
            if oracles:
                tg = g7r.unpack(arch.top())
                row["world_oracle_honest"] = E7.world_oracle(g7r, tg, T.HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(g7r, tg, T.HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(g7r, tg, T.HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(g7r, tg, T.HELD8, cheat=True)
        rows[arm] = row
    rows["_run_cpu_s"] = time.process_time() - t0
    return rows


# ------------------------------------------------------------------ analysis (preregistered)
def _ranks(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman_levels(y) -> float:
    y = np.asarray(y, float)
    ry, rx = _ranks(y), np.arange(len(y), dtype=float)
    if np.all(ry == ry[0]):
        return 0.0
    ry, rx = ry - ry.mean(), rx - rx.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def holm(ps: dict) -> dict:
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m, out, run = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def analyze(rows: list[dict], need: int = 32) -> dict:
    per = {}
    for x in rows:
        if x.get("exp_id") == EXP and x.get("condition") in ARMS and x.get("status") in ("record", "control"):
            per.setdefault(x["run_id"], {})[x["condition"]] = x
    runs = sorted(k for k, v in per.items() if all(a in v for a in ARMS))
    y = {a: np.array([per[k][a]["held_auc"] for k in runs]) for a in ARMS}
    out = {"ladder_version": LADDER_VERSION, "n_complete_runs": len(runs), "runs": runs, "alpha": ALPHA,
           "p_method": T.signflip_method(len(runs)), "means_held_auc": {a: float(y[a].mean()) if runs else None
                                                                        for a in ARMS}}
    if len(runs) < 2:
        out["outcome"] = "INDETERMINATE"
        return out
    L = np.stack([y[a] for a in LADDER], 1)
    rho = np.array([spearman_levels(r) for r in L])
    out["trend"] = {"rho_mean": float(rho.mean()), "p_dec": T.signflip_p(-rho), "p_inc": T.signflip_p(rho)}
    ps, diffs = {}, {}
    for k in (1, 2, 3):
        a = LADDER[k]
        d0, d4 = y[a] - y[LADDER[0]], y[a] - y[LADDER[4]]
        diffs[a] = {"minus_L0": float(d0.mean()), "minus_L4": float(d4.mean())}
        ps[f"peak_{a}"] = max(T.signflip_p(d0), T.signflip_p(d4))
        ps[f"trough_{a}"] = max(T.signflip_p(-d0), T.signflip_p(-d4))
    adj = holm(ps)
    out["nonmonotone"] = {"p_raw": ps, "p_holm": adj, "interior_diffs": diffs}
    d = y["X_charge_align"] - y["L0_identity"]
    s_up, s_dn = T.signflip_p(d), T.signflip_p(-d)
    out["structural_charge_align"] = {"diff_mean": float(d.mean()), "p_raises": s_up, "p_lowers": s_dn,
                                      "reading": "CHARGE_ALIGNMENT_RAISES" if s_up < ALPHA else
                                      "CHARGE_ALIGNMENT_LOWERS" if s_dn < ALPHA else "CHARGE_ALIGNMENT_NO_EFFECT"}
    out["vs_scratch"] = {a: {"diff_mean": float((y[a] - y["scratch"]).mean()), "p_above": T.signflip_p(y[a] - y["scratch"])}
                         for a in ARMS[1:]}
    out["adjacent"] = {f"{LADDER[i + 1]}_minus_{LADDER[i]}": float((y[LADDER[i + 1]] - y[LADDER[i]]).mean())
                       for i in range(len(LADDER) - 1)}
    out["r7_replication_descriptive"] = {"L0_minus_L2": float((y["L0_identity"] - y["L2_full_featperm"]).mean()),
                                         "L2_minus_scratch": float((y["L2_full_featperm"] - y["scratch"]).mean()),
                                         "r7": R7_REFERENCE}
    split = {}
    for a in ("L1_partial_featperm", "L2_full_featperm"):
        al = np.array([bool(per[k][a]["arm_meta"]["charge_aligned"]) for k in runs])
        dd = y[a] - y["L0_identity"]
        split[a] = {"n_aligned": int(al.sum()), "minus_L0_aligned": float(dd[al].mean()) if al.any() else None,
                    "minus_L0_not_aligned": float(dd[~al].mean()) if (~al).any() else None}
    out["charge_aligned_split_descriptive"] = split
    for extra in ("held64", "zero_shot_held64", "train_auc"):
        out[f"means_{extra}"] = {a: float(np.mean([per[k][a][extra] for k in runs])) for a in ARMS}
    integ = [per[k][a]["arm_integrity"]["ok"] for k in runs for a in ARMS[1:]]
    out["integrity_ok"] = f"{sum(integ)}/{len(integ)}"
    out["donor_fused_eq_numpy"] = f"{sum(bool(per[k]['L0_identity'].get('donor_fused_eq_numpy')) for k in runs)}/{len(runs)}"
    if len(runs) < need:
        out["outcome"] = "INDETERMINATE"
    elif min(adj.values()) < ALPHA:
        out["outcome"] = "C_NONMONOTONIC"
    elif out["trend"]["p_dec"] < ALPHA:
        out["outcome"] = "A_DECREASING_WITH_DESTRUCTION"
    elif out["trend"]["p_inc"] < ALPHA:
        out["outcome"] = "B_INCREASING_WITH_DESTRUCTION"
    else:
        out["outcome"] = "FLAT_NO_SYSTEMATIC_RESPONSE"
    return out


# ------------------------------------------------------------------ worker job
def sample_block(families=FAMILIES, run_seeds=RUN_SEEDS) -> dict:
    return V.sample_block(list(families), list(run_seeds))


ENVELOPE = {"campaign_stage": "PRODUCTION", "checkpointable": True, "cohort": "E", "cpu_budget_s": 36000,
            "evidence_class": "OBSERVATION", "expected_output_rows": 32 * len(ARMS) + 1, "experiment_class": "SHAM_RESPONSE",
            "gpu_budget_s": 0, "predicate_id": EXP,
            "required_controls": ["scratch_reference", "sham_ladder_L1_L4", "charge_align_discriminator"],
            "required_oracles": ["world", "brain", "donor_fused_eq_numpy", "arm_integrity"],
            "wall_budget_s": 2400, **sample_block()}


def job(ctx, families=FAMILIES, run_seeds=RUN_SEEDS, gens: int = GENS, batch: int = BATCH,
        campaign_stage: str = "PRODUCTION"):
    order = run_order(families, run_seeds)
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
        for a in ARMS:
            ctx.emit(rows[a])
        st["done"][k] = rows
        ctx.checkpoint(st)
    allrows = [r for k in st["done"] for r in st["done"][k].values()]
    got = analyze(allrows, need=len(order))
    ctx.emit(dict(base, kind="h1_analysis", status="record", condition="analysis", report_only=False,
                  run_cpu_s_median=float(np.median(list(st["cpu"].values()))) if st["cpu"] else None, **got))


def dev(gens: int = 4, batch: int = 32) -> dict:
    """No rows: wiring, integrity and CPU per evolve at a tiny budget on run (4200, 24)."""
    base = base_row(sample_block(), "SMOKE", gens, batch)
    t0 = time.perf_counter()
    rows = run_one(4200, 24, base, gens, batch, oracles=True)
    cpu = rows.pop("_run_cpu_s")
    return {"gens": gens, "batch": batch, "run_cpu_s": cpu, "wall_s": time.perf_counter() - t0,
            "integrity": {a: rows[a]["arm_integrity"]["ok"] for a in ARMS[1:]},
            "meta": {a: rows[a].get("arm_meta") for a in ARMS[1:]},
            "arm_cpu_s": {a: round(rows[a]["arm_cpu_s"], 2) for a in ARMS}, "fused_eq": rows["L0_identity"]["donor_fused_eq_numpy"]}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        g = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        b = int(sys.argv[3]) if len(sys.argv) > 3 else 32
        print(json.dumps(dev(g, b), indent=1, default=str))
