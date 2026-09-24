"""cw01-e08 - rank-tax tensor evolution on the real Primordial Machine organism.

ORGANISM. The substrate's tt_digits tensor-train policy (primordial/brain/genomes.py
_TT / TTDigits: alpha [r], G [d,16,r,r], Wo [r,A], one core per hex digit of each
observation feature) joined to the two structural genes SUBSTRATE_RECONCILE.md names:
per-bond ranks r_0..r_d in [1, R_max] (the representation primordial/brain/plastic.py
uses, joined to evolution here for the first time) and the per-core read mask of
cohort C's bit metering (an unread core sees index 0). Zero-padding at R_max keeps the
substrate's batched forward exact: every entry outside the declared ranks is held at
zero, so the contraction equals the ragged tensor train.

BURDEN, recounted from the raw cores, never trusted from the declared vector:
    bond   = sum_k r_k                       total bond width
    params = r_0 + sum_k 16 r_k r_{k+1} + r_d A
    flops  = sum_k r_k r_{k+1} + r_d A       contractions per act
    bits   = 4 * (#unmasked cores)           world bits read per act
Selection under TAX: sel = fit - lambda * scalar(B). Recorded fitness is never taxed.

STRUCTURAL PRESSURE: truncate the widest eligible bond (r_k > 1, ties to the lowest k)
by one slice. Reads burden only. The sham finds the same bond, consumes the same draws,
changes nothing.

WORLD: w13 through the sanctioned constructor make_world (wforge is read-only). The
substrate's entry module qd/e4_run.py imports redis at import time; its six-line Spec is
reproduced here (e4_run.py:39-46) and e4_run is never imported.

CW01-D046: roots discovered by marker via lib/repopath.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402
import seeds as S              # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
REPO = RP.find_root(HERE)
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from primordial.brain.tt_policy import digits          # noqa: E402  (read-only substrate)
from primordial.soup.b1.common import make_world       # noqa: E402  (sanctioned world constructor)
from primordial.soup.b1.np_world import NpEncounter    # noqa: E402

ARMS = ("CONTROL", "TAX", "AMP", "TAX+AMP")
COORDS = ("bond", "params", "flops", "bits")


def is_tax(arm):
    return arm in ("TAX", "TAX+AMP")


def is_amp(arm):
    return arm in ("AMP", "TAX+AMP")


class Spec:
    """primordial/qd/e4_run.py:39-46, reproduced to avoid that module's redis import."""

    def __init__(self, gen_seed: int):
        self.gen_seed = gen_seed
        self.mech, self.wid = make_world(gen_seed)
        m = self.mech
        self.T, self.S, self.W = m.horizon, m.n_slots, m.act_width
        self.D = len(m.obs_perm)
        self.d = 4 * self.D


def world_spec(cfg):
    return Spec(cfg["world"]["gen_seed"])


def train_seeds(cfg):
    a, b = cfg["world"]["train_seeds"]
    return np.arange(a, b + 1, dtype=np.int64)


def held_seeds(cfg):
    a, b = cfg["world"]["held_seeds"]
    return np.arange(a, b + 1, dtype=np.int64)


# ----------------------------------------------------------------- population

def dims(cfg, spec):
    return spec.d, cfg["organism"]["R_max"], cfg["world"]["A"], spec.W


def rank_masks(rk, d, R):
    """Boolean keep-masks implied by the declared ranks."""
    P = rk.shape[0]
    ar = np.arange(R)
    al_m = ar[None, :] < rk[:, 0:1]                                   # (P,R)
    rows = ar[None, None, :] < rk[:, :d, None]                        # (P,d,R) input side of core k
    cols = ar[None, None, :] < rk[:, 1:d + 1, None]                   # (P,d,R) output side of core k
    G_m = rows[:, :, None, :, None] & cols[:, :, None, None, :]       # (P,d,1,R,R)
    Wo_m = (ar[None, :] < rk[:, d:d + 1])[:, :, None]                 # (P,R,1)
    return al_m, G_m, Wo_m


def enforce_pad(pop, cfg, spec):
    """Hold every entry outside the declared ranks at exactly zero. In place."""
    d, R, A, W = dims(cfg, spec)
    al_m, G_m, Wo_m = rank_masks(pop["rk"], d, R)
    pop["al"] *= al_m
    pop["G"] *= G_m
    pop["Wo"] *= Wo_m
    return pop


def init_population(cfg, spec, rng, P):
    d, R, A, W = dims(cfg, spec)
    al = rng.standard_normal((P, R)).astype(np.float32)
    G = (np.eye(R, dtype=np.float32)
         + cfg["organism"]["init_G_noise"] * rng.standard_normal((P, d, 16, R, R))).astype(np.float32)
    Wo = rng.standard_normal((P, R, A)).astype(np.float32)
    C = rng.integers(0, 16, size=(P, A, W), dtype=np.uint8)
    C[:, 0] = 0
    rk = rng.integers(1, R + 1, size=(P, d + 1))
    mk = rng.random((P, d)) < 0.5
    pop = {"al": al, "G": G, "Wo": Wo, "C": C, "rk": rk, "mk": mk}
    return enforce_pad(pop, cfg, spec)


def copy_pop(pop):
    return {k: v.copy() for k, v in pop.items()}


def take(pop, idx):
    return {k: v[idx].copy() for k, v in pop.items()}


def concat(a, b):
    return {k: np.concatenate([a[k], b[k]], axis=0) for k in a}


def mutate(cfg, spec, rng, pop):
    """The substrate's jitter + codebook flip, plus mask flip and one rank step. Same in every arm."""
    ev = cfg["evolution"]
    d, R, A, W = dims(cfg, spec)
    P = pop["rk"].shape[0]
    out = copy_pop(pop)
    for key in ("al", "G", "Wo"):
        x = out[key]
        m = rng.random(x.shape) < ev["mut_rate"]
        x += (m * ev["mut_sigma"] * rng.standard_normal(x.shape)).astype(np.float32)
    m = rng.random(out["C"].shape) < 1.0 / (A * W)
    out["C"] = np.where(m, rng.integers(0, 16, out["C"].shape, dtype=np.uint8), out["C"])
    out["C"][:, 0] = 0
    out["mk"] ^= rng.random(out["mk"].shape) < 1.0 / d
    # one rank step per organism with probability p_rank; direction equiprobable
    do = rng.random(P) < ev["p_rank"]
    k = rng.integers(0, d + 1, size=P)
    up = rng.random(P) < 0.5
    new_al = rng.standard_normal((P, R)).astype(np.float32)
    new_G_row = (ev["grow_sigma"] * rng.standard_normal((P, 16, R))).astype(np.float32)
    new_G_col = (ev["grow_sigma"] * rng.standard_normal((P, 16, R))).astype(np.float32)
    new_Wo = rng.standard_normal((P, A)).astype(np.float32)
    for p in np.where(do)[0]:
        kk = int(k[p])
        r = int(out["rk"][p, kk])
        if up[p] and r < R:
            j = r                                   # index of the new slice
            if kk == 0:
                out["al"][p, j] = new_al[p, j]
            else:
                out["G"][p, kk - 1, :, :, j] = new_G_col[p]      # new output column of core kk-1
            if kk == d:
                out["Wo"][p, j, :] = new_Wo[p]
            else:
                out["G"][p, kk, :, j, :] = new_G_row[p]          # new input row of core kk
            out["rk"][p, kk] = r + 1
        elif (not up[p]) and r > 1:
            out["rk"][p, kk] = r - 1
    return enforce_pad(out, cfg, spec)


# ----------------------------------------------------------------- durable genome bytes

class GenomeRefused(ValueError):
    """Raised when a byte record is not exactly one fixed-length genome."""


def record_layout(cfg, spec):
    d, R, A, W = dims(cfg, spec)
    return [("al", (R,), "<f4"), ("G", (d, 16, R, R), "<f4"), ("Wo", (R, A), "<f4"),
            ("C", (A, W), "u1"), ("rk", (d + 1,), "<i2"), ("mk", (d,), "u1")]


def record_nbytes(cfg, spec):
    return int(sum(int(np.prod(s)) * np.dtype(t).itemsize for _, s, t in record_layout(cfg, spec)))


def pack(pop, cfg, spec):
    """uint8 [P, nbytes]: the fixed-length durable form. Everything the organism is."""
    P = pop["rk"].shape[0]
    parts = []
    for key, shape, dt in record_layout(cfg, spec):
        parts.append(np.ascontiguousarray(pop[key].astype(dt)).reshape(P, -1).view(np.uint8))
    return np.concatenate(parts, axis=1)


def unpack(B, cfg, spec):
    """Refuses any record whose length is not exactly the layout's: no hidden bytes, no truncation."""
    B = np.asarray(B, np.uint8)
    n = record_nbytes(cfg, spec)
    if B.ndim != 2 or B.shape[1] != n:
        raise GenomeRefused("record width %s != layout %d bytes; extra or missing bytes are refused"
                            % (B.shape[1:] if B.ndim == 2 else B.shape, n))
    P, off, out = B.shape[0], 0, {}
    for key, shape, dt in record_layout(cfg, spec):
        cnt = int(np.prod(shape)) * np.dtype(dt).itemsize
        arr = np.ascontiguousarray(B[:, off:off + cnt]).view(dt).reshape((P,) + shape)
        out[key] = arr.astype({"al": np.float32, "G": np.float32, "Wo": np.float32, "C": np.uint8,
                               "rk": np.int64, "mk": bool}[key])
        off += cnt
    return enforce_pad(out, cfg, spec)


# ----------------------------------------------------------------- burden

def burden_from_ranks(rk, mk, A):
    d = mk.shape[1]
    bond = rk.sum(1)
    params = rk[:, 0] + (16 * rk[:, :d] * rk[:, 1:d + 1]).sum(1) + rk[:, d] * A
    flops = (rk[:, :d] * rk[:, 1:d + 1]).sum(1) + rk[:, d] * A
    bits = 4 * mk.sum(1)
    return {"bond": bond, "params": params, "flops": flops, "bits": bits}


def recount_ranks(pop, cfg, spec):
    """Effective ranks from the RAW cores: highest slice carrying any non-zero entry."""
    d, R, A, W = dims(cfg, spec)
    P = pop["rk"].shape[0]
    eff = np.ones((P, d + 1), dtype=int)
    ar = np.arange(1, R + 1)

    def last_nonzero(mask_over_R):               # (P,R) bool -> highest index+1 with True, min 1
        return np.maximum((mask_over_R * ar[None, :]).max(1), 1)

    nz_al = pop["al"] != 0
    eff[:, 0] = last_nonzero(nz_al)
    for kk in range(d):
        nz = pop["G"][:, kk] != 0                     # (P,16,R,R)
        rows = nz.any(axis=(1, 3))                    # (P,R) input side
        cols = nz.any(axis=(1, 2))                    # (P,R) output side
        eff[:, kk] = np.maximum(eff[:, kk], last_nonzero(rows))
        eff[:, kk + 1] = np.maximum(eff[:, kk + 1], last_nonzero(cols))
    nz_wo = (pop["Wo"] != 0).any(2)
    eff[:, d] = np.maximum(eff[:, d], last_nonzero(nz_wo))
    return eff


def burden(pop, cfg, spec, recount=True):
    """The burden vector, from a recount of the raw cores. Refuses on declared/recounted disagreement."""
    d, R, A, W = dims(cfg, spec)
    if recount:
        eff = recount_ranks(pop, cfg, spec)
        bad = (eff > pop["rk"]).any(1)                # entries live outside the declared ranks
        if bad.any():
            raise BurdenRefused("recount exceeds declared ranks for %d organism(s): %s"
                                % (int(bad.sum()), np.where(bad)[0][:8].tolist()))
    B = burden_from_ranks(pop["rk"], pop["mk"], A)
    return B


class BurdenRefused(AssertionError):
    """Raised when the raw cores disagree with the declared burden."""


def burden_max(cfg, spec):
    d, R, A, W = dims(cfg, spec)
    rk = np.full((1, d + 1), R)
    mk = np.ones((1, d), bool)
    return {k: float(v[0]) for k, v in burden_from_ranks(rk, mk, A).items()}


def scalar_burden(B, cfg, spec):
    w = cfg["tax"]["weights"]
    Bm = burden_max(cfg, spec)
    return sum(w[i] * np.asarray(B[c], float) / Bm[c] for i, c in enumerate(COORDS))


# ----------------------------------------------------------------- structural pressure

def widest_bond(rk):
    """Per organism: the widest eligible bond (r_k > 1), ties to the lowest index; -1 if none."""
    P, n = rk.shape
    elig = rk > 1
    order = np.where(elig, rk, -1)
    k = np.argmax(order, axis=1)                     # argmax returns the FIRST maximum: lowest k
    k[~elig.any(1)] = -1
    return k


def amputate(pop, cfg, spec, sham=False):
    """Truncate the widest eligible bond by one slice, in place. Deterministic given the ranks:
    no random draw is consumed, so the sham (same bond search, no change) is exactly a no-op."""
    k = widest_bond(pop["rk"])
    n_changed = 0
    if not sham:
        for p in np.where(k >= 0)[0]:
            pop["rk"][p, k[p]] -= 1
            n_changed += 1
        enforce_pad(pop, cfg, spec)
    return {"targets": k, "n_changed": n_changed}


# ----------------------------------------------------------------- executor

def forward(pop, obs, grow, spec):
    """obs int [n, D] -> action index [n]. The substrate's forward at R_max with masked digits."""
    idx = digits(obs.astype(np.uint16)).astype(np.int64)             # (n, d)
    idx = np.where(pop["mk"][grow], idx, 0)
    G, al, Wo = pop["G"], pop["al"], pop["Wo"]
    v = al[grow]
    for c in range(idx.shape[1]):
        v = np.einsum("nr,nrs->ns", v, G[grow, c, idx[:, c]])
        v /= np.maximum(np.abs(v).max(1, keepdims=True), 1e-30)
    return np.einsum("nr,nra->na", v, Wo[grow]).argmax(1)


def ref_action(pop, p, obs_row, spec):
    """One genome, one row, float64, on the RAGGED cores sliced to declared ranks (the oracle)."""
    d = spec.d
    rk = pop["rk"][p]
    idx = digits(np.asarray(obs_row, np.uint16)[None]).astype(np.int64)[0]
    idx = np.where(pop["mk"][p], idx, 0)
    v = pop["al"][p, :rk[0]].astype(np.float64)
    for c in range(d):
        Gc = pop["G"][p, c, idx[c], :rk[c], :rk[c + 1]].astype(np.float64)
        v = v @ Gc
        v /= max(np.abs(v).max(), 1e-300)
    return int((v @ pop["Wo"][p, :rk[d]].astype(np.float64)).argmax())


def rollout(spec, pop, seeds, hash_obs=False):
    """P genomes x len(seeds) episodes in lockstep (e5_run.py:102-127). Returns per-genome
    summed final clipped charge, live slot-ticks, and optionally a hash of the observation
    stream (Q6-8: the world stream must not depend on the structural operator)."""
    P, k, S, D = pop["rk"].shape[0], len(seeds), spec.S, spec.D
    n = P * k
    w = NpEncounter(spec.mech, spec.wid, with_obs=True)
    obs = w.reset(np.tile(np.asarray(seeds, np.int64), P))
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S)
    cnt = np.zeros(n)
    h = hashlib.sha256() if hash_obs else None
    for t in range(spec.T):
        if h is not None:
            h.update(np.ascontiguousarray(obs).tobytes())
        idx = forward(pop, obs.reshape(n * S, D), grow, spec).reshape(n, S)
        a = pop["C"][genv[:, None], idx].astype(np.int32)
        live = w.alive & ~w.done[:, None]
        cnt += live.sum(1)
        obs, _, done = w.step(a)
        if done.all():
            break
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int64)
    live_ticks = cnt.reshape(P, k).sum(1)
    return {"fit": fit, "live_ticks": live_ticks, "obs_hash": (h.hexdigest() if h else None),
            "ticks": t + 1}


def constant_policy_fit(spec, seeds, action_vec):
    """Fitness of a constant action on the given seeds (one env per seed)."""
    k = len(seeds)
    w = NpEncounter(spec.mech, spec.wid, with_obs=False)
    w.reset(np.asarray(seeds, np.int64))
    a = np.broadcast_to(np.asarray(action_vec, np.int32)[None, None, :], (k, spec.S, spec.W)).copy()
    for t in range(spec.T):
        _, _, done = w.step(a)
        if done.all():
            break
    return float(np.clip(w.charge, 0, None).sum(1).sum())


def trivial_floors(spec, seeds):
    """Always-abstain and best-constant-action fitness on `seeds` (metric/floors.py definitions)."""
    from itertools import product
    W = spec.W
    fits = {}
    for act in product(range(8), repeat=W):
        fits[act] = constant_policy_fit(spec, seeds, act)
    abst = fits[tuple([0] * W)]
    best_act = max(sorted(fits), key=lambda a: fits[a])
    return {"abstain": abst, "best_constant": fits[best_act], "best_constant_action": list(best_act),
            "per_seed": {"abstain": abst / len(seeds), "best_constant": fits[best_act] / len(seeds)}}


# ----------------------------------------------------------------- evolution

def next_generation(pop, sel, rng, cfg, spec):
    ev = cfg["evolution"]
    P = len(sel)
    order = np.argsort(-sel, kind="stable")
    elites = take(pop, order[:ev["elite"]])
    n_child = P - ev["elite"]
    cand = rng.integers(0, P, size=(n_child, ev["tournament"]))
    winners = cand[np.arange(n_child), np.argmax(sel[cand], axis=1)]
    children = mutate(cfg, spec, rng, take(pop, winners))
    return concat(elites, children)


def evolve(cfg, spec, aid, arm, lineage, generations, lam, g_amp, seed_component="evo",
           history_every=1, on_generation=None):
    """One lineage. Arms differ ONLY in (a) whether sel subtracts lambda*scalar(B), (b) whether the
    scheduled structural operator truncates or shams. Everything else is shared code and RNG order."""
    if arm not in ARMS:
        raise ValueError(arm)
    ev = cfg["evolution"]
    rng = S.rng(aid, "%s|%s|%d" % (seed_component, arm, lineage))
    seeds = train_seeds(cfg)
    pop = init_population(cfg, spec, rng, ev["n_org"])
    hist = []
    for g in range(generations):
        amp_info = None
        if g_amp and g > 0 and g % g_amp == 0:
            amp_info = amputate(pop, cfg, spec, sham=not is_amp(arm))
        ro = rollout(spec, pop, seeds)
        B = burden(pop, cfg, spec)
        sb = scalar_burden(B, cfg, spec)
        fit = ro["fit"].astype(float)
        sel = fit - lam * sb if is_tax(arm) else fit.copy()
        if history_every and (g % history_every == 0 or g == generations - 1):
            rec = {"gen": g, "fit_mean": float(fit.mean()), "fit_max": float(fit.max()),
                   "sel_mean": float(sel.mean()), "sel_max": float(sel.max()),
                   "scalar_mean": float(sb.mean()), "live_ticks_mean": float(ro["live_ticks"].mean()),
                   "amputated": (amp_info["n_changed"] if amp_info else 0)}
            for c in COORDS:
                rec[c + "_mean"] = float(B[c].mean())
            hist.append(rec)
            if on_generation:
                on_generation(rec)
        if g == generations - 1:
            break
        pop = next_generation(pop, sel, rng, cfg, spec)
    return {"pop": pop, "fit": fit, "sel": sel, "burden": B, "history": hist, "arm": arm,
            "lineage": lineage}


# ----------------------------------------------------------------- assay (blinded: genomes only)

def representatives(pop, fit, top_k):
    idx = np.argsort(-fit, kind="stable")[:top_k]
    return take(pop, idx), idx


def assay(cfg, spec, pop, aid, tag="assay"):
    """Tax-free held-out capability, recounted burden, retention after a frozen amputation.
    Takes genomes only; knows no arm label."""
    hs = held_seeds(cfg)
    ro = rollout(spec, pop, hs)
    B = burden(pop, cfg, spec)
    out = {"held64": ro["fit"] / len(hs), "live_ticks": ro["live_ticks"],
           "work": ro["live_ticks"] * B["flops"], "burden": B,
           "scalar": scalar_burden(B, cfg, spec)}
    amp = copy_pop(pop)
    for _ in range(cfg["assay"]["s_amp"]):
        amputate(amp, cfg, spec, sham=False)
    ro2 = rollout(spec, amp, hs)
    out["held64_after_amp"] = ro2["fit"] / len(hs)
    out["burden_after_amp"] = burden(amp, cfg, spec)
    return out


# ----------------------------------------------------------------- statistics

def _ols(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def stratified_contrast(y, C, tax, amp, n_perm, rng):
    """y_l = a + b C_l + c_tax TAX + c_amp AMP (+ c_int TAX*AMP). Randomisation of TAX labels within
    each AMP stratum gives the null for c_tax (additive model) and c_int (full model)."""
    y, C = np.asarray(y, float), np.asarray(C, float)
    tax, amp = np.asarray(tax, bool), np.asarray(amp, bool)
    n = len(y)

    def fit(t):
        Xa = np.column_stack([np.ones(n), C, t.astype(float), amp.astype(float)])
        Xf = np.column_stack([Xa, (t & amp).astype(float)])
        return float(_ols(y, Xa)[2]), float(_ols(y, Xf)[4])

    c_tax, c_int = fit(tax)
    null_tax, null_int = np.empty(n_perm), np.empty(n_perm)
    for i in range(n_perm):
        t = tax.copy()
        for stratum in (False, True):
            m = np.where(amp == stratum)[0]
            t[m] = tax[m][rng.permutation(len(m))]
        null_tax[i], null_int[i] = fit(t)
    q = lambda a, p: float(np.percentile(a, p))   # noqa: E731
    return {"c_tax": c_tax, "c_tax_p05": q(null_tax, 5), "c_tax_p95": q(null_tax, 95),
            "c_tax_below_p05": bool(c_tax < q(null_tax, 5)),
            "c_int": c_int, "c_int_p05": q(null_int, 5), "c_int_p95": q(null_int, 95),
            "c_int_inside": bool(q(null_int, 5) <= c_int <= q(null_int, 95)),
            "n": int(n), "n_perm": int(n_perm)}


def overlap(C_a, C_b, k_min):
    lo_a, hi_a = float(np.min(C_a)), float(np.max(C_a))
    lo_b, hi_b = float(np.min(C_b)), float(np.max(C_b))
    b_in = int(np.sum((C_b >= lo_a) & (C_b <= hi_a)))
    a_in = int(np.sum((C_a >= lo_b) & (C_a <= hi_b)))
    return {"a_inside_b": a_in, "b_inside_a": b_in, "required": k_min,
            "ok": bool(a_in >= k_min and b_in >= k_min),
            "range_a": [lo_a, hi_a], "range_b": [lo_b, hi_b]}


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])
