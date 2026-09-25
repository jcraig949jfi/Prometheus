"""C-R4-05: drawn cell tt_digits / w13 / bit_metering / torch_gpu / none (draw seed 11059902093008038213).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run. C-R4-02..04 were drawn on
graphworld_b2 and aborted as infeasible (no action channel, observations or fitness). No text in the repo defines
bit_metering; the definitions below are fixed before any run.

  world     w13 (E4.Spec(13)), the round 4 screen's only SURVIVED world (train128_held64). D=5, S=1, W=1, T=32.
            Selection on floors.TRAIN128 (9100..9227), score on HELD64 (30000..30063): the survivor's pressure seeds.
  brain     tt_digits (C4 TTDigits, rank 3, one core per hex digit, 20 cores, MSD first) + lane E's codebook C[8, W]
            (row 0 abstain) + a 20-bit READ MASK, one bit per digit core. An unread digit reaches the brain as 0.
            Genome = 2907 float32 + 8 codebook + 3 mask bytes -> 11,640 bytes.
  pressure  bit_metering: every bit the brain reads is paid for. Per live slot-tick, cost = BETA * 4 * |mask|;
            selection fitness = sum over TRAIN seeds of (clipped final charge) - rint(total cost).
            BETA is derived from the screen, not tuned: reading all 80 bits on all 32 ticks costs exactly the w13
            train128 headroom above floor, (baseline median 182.71875 - floor 166.46875) / (32 * 80) = 16.25 / 2560.
            HELD64 is scored as raw charge (the mask still limits what the brain sees; no cost).
  arms      cell (mask evolves, cost paid) vs control (same family, mask fixed all-read, no cost). Same bytes.
  substrate torch_gpu: brain forward AND world (U1 TorchWorld, primordial/nv/cudagraph/world.py) on CUDA; numpy
            NpEncounter and wforge are references only.
  budget    the survivor pressure's own budget (E10 closed / M2 baseline): 800 gens x 128, 8 run seeds per arm,
            LuaArchive sampler_seed [9505, run_seed, arm], GA stream PCG64([4505, run_seed, arm]); float genes C4
            mutate (p .05, sigma .2), codebook E7, mask bits flip p = 1/20, init mask bits uniform. Elites saved to HOT.
            F9: the job pauses only at run boundaries; ttl_cpu_s declared from a no-rows timing check.
  primary   median over run seeds of HELD64 per-seed charge (cell, top-16 by selection fitness)
            >= median (control) - 0.5 * IQR(control)
  clause A  none claimable: the pressure is not train128_held64 and 11,640 bytes > the 200-byte baseline. Progress
            above floor is REPORTED only, from worlds_r4.json.
  oracles   run seed 0, each arm, top-16, HELD8:
            world  every GPU episode's per-tick (regs, charge, alive) hash and pre-step obs hash == the wforge
                   Encounter replaying the GPU actions (b1.common.reference): honest 0/16 elites failing; the
                   TorchWorld skip_lin cheat fails >= 14/16.
            brain  E's powered verdict (cohorts/e/oracles.brain_verdict) on the torch forward vs float64 masked
                   ref_logits: honest 0 mismatched, shift_action every elite, ablate_top >= 14/16.
            meter  cheat free_read (torch forward ignores the mask) mismatches the masked reference on >= 90% of
                   ELIGIBLE rows (clear rows where the reference itself changes argmax with the mask ignored; count
                   reported, >= 1 required; cell arm only -- the control reads everything).
            cost   numpy recount of 4 * |mask| * live slot-ticks * BETA == the GPU cost on those elites (exact).
  report    numpy cross-check (E7.rollout with the same torch brain): top-16 fitness per run on TRAIN128 and HELD64,
            and every offer of the first 25 gens of run seed 0; mismatches counted and reported, not judged
            (float32 order near argmax ties). Bits read, features read, cost per seed, train per seed, coverage.

  worker:  python -m primordial.fabric.worker submit C primordial.cohorts.c.r4_05_tt_digits_w13_bit_metering_gpu:job
             --exp C-R4-05-tt-digits-w13-bit-metering-gpu
             --rows primordial/ledger/rows/C/C-R4-05-tt-digits-w13-bit-metering-gpu.jsonl --ttl-cpu-s S
  ledger:  python -m primordial.cohorts.c.r4_05_tt_digits_w13_bit_metering_gpu qd
  dev:     python -m primordial.cohorts.c.r4_05_tt_digits_w13_bit_metering_gpu dev   (no rows)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np
import torch

from primordial.brain import genomes as gm
from primordial.brain.tt_policy import _SH
from primordial.metric import floors as F
from primordial.nv.cudagraph.world import TorchWorld
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.soup.b1.common import hash_log, hash_obs, reference

EXP = "C-R4-05-tt-digits-w13-bit-metering-gpu"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C") / EXP
GS, BATCH, TOP, A = 13, 128, 16, E7.A
GENS = 800
DEV = torch.device("cuda")
CELL = {"representation": "tt_digits", "world": "w13", "pressure": "bit_metering", "substrate": "torch_gpu",
        "channel": "none"}
CELL_CTRL = dict(CELL, pressure="none_control")
AUDIT_GENS = 25


def screen_cell():
    doc = json.loads((ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json").read_text(encoding="utf-8"))
    c = [x for x in doc["cells"] if x["world"] == "w13" and x["pressure"] == "train128_held64"][0]
    assert c["verdict"] == "SURVIVED"
    # the ACTIVE variant's floor (SWARM_R4 s7, gate_in|HOLD) -- the top-level "floor" is the four-policy one (159.0)
    return c["verdicts"]["gate_in|HOLD"]["floor"], c["baseline"]["median"], c["baseline"]["bytes"]


FLOOR, BASE_MED, BASE_BYTES = screen_cell()
SPEC = E4.Spec(GS)
T_, D_ = SPEC.mech.horizon, len(SPEC.mech.obs_perm)
NC = 4 * D_
BETA = (BASE_MED - FLOOR) / (T_ * 4 * NC)
assert BETA == 16.25 / 2560, BETA
MB = (NC + 7) // 8
SH_T = torch.tensor(np.asarray(_SH, np.int64).reshape(-1), device=DEV)


class MaskedTTDigits(gm.TTDigits):
    """TTDigits whose params carry a read mask bool [P, 4D]; unread digit cores see index 0."""
    name = "tt_digits_masked"

    @property
    def nbytes(self) -> int:
        return self.nf * 4 + MB

    def init(self, rng, P):
        return tuple(super().init(rng, P)) + (rng.random((P, 4 * self.D)) < 0.5,)

    def mutate(self, rng, g, rate: float = 0.05, sigma: float = 0.2):
        return tuple(super().mutate(rng, g[:3], rate, sigma)) + (g[3] ^ (rng.random(g[3].shape) < 1.0 / (4 * self.D)),)

    def pack(self, g) -> np.ndarray:
        P = len(g[0])
        f = np.concatenate([x.reshape(P, -1) for x in g[:3]], 1).astype("<f4").view(np.uint8).reshape(P, self.nf * 4)
        m = np.packbits(g[3].astype(np.uint8), axis=1, bitorder="little")[:, :MB]
        return np.concatenate([f, m], 1)

    def unpack(self, B):
        fb = self.nf * 4
        p = super().unpack(np.ascontiguousarray(B[:, :fb]))
        m = np.unpackbits(np.ascontiguousarray(B[:, fb:fb + MB]), axis=1, bitorder="little")[:, :4 * self.D].astype(bool)
        return tuple(p) + (m,)

    def index(self, obs):
        return super().index(obs)

    def logits(self, g, obs, gidx, cheat=False):
        al, G, Wo, mk = g
        return super().logits((al, G, Wo), np.ascontiguousarray(obs), gidx, cheat) if mk.all() else \
            self._masked_logits(g, obs, gidx, cheat)

    def _masked_logits(self, g, obs, gidx, cheat):
        al, G, Wo, mk = g
        idx = np.where(mk[gidx], self.index(obs), 0)
        v = al[gidx]
        for c in range(idx.shape[1]):
            if cheat and c % 2:
                continue
            v = np.einsum("nr,nrs->ns", v, G[gidx, c, idx[:, c]])
            v /= np.maximum(np.abs(v).max(1, keepdims=True), 1e-30)
        return np.einsum("nr,nra->na", v, Wo[gidx])

    def forward_fast(self, *a, **k):
        raise NotImplementedError("no unmasked fast path")

    def ref_logits(self, g1, obs, ignore_mask=False):
        al, G, Wo, mk = g1
        al, G, Wo = (x.astype(np.float64) for x in (al, G, Wo))
        idx = self.index(obs)
        if not ignore_mask:
            idx = np.where(mk[None, :], idx, 0)
        out = np.zeros((len(obs), self.A))
        for i in range(len(obs)):
            v = al.copy()
            for c in range(idx.shape[1]):
                v = v @ G[c, idx[i, c]]
                v /= max(np.abs(v).max(), 1e-300)
            out[i] = v @ Wo
        return out


class TorchMasked(MaskedTTDigits):
    """Same family; forward runs on CUDA. forward() takes/returns numpy (E's oracle, E7.rollout); forward_t is the
    device path used by the GPU rollout."""

    def __init__(self, D, A=8):
        super().__init__(D, A)
        self._src, self._t = None, None

    def to_t(self, g):
        if self._src is not g[1]:
            self._t = tuple(torch.from_numpy(np.ascontiguousarray(x)).to(DEV) for x in g)
            self._src = g[1]
        return self._t

    def forward_t(self, tp, obs, gidx, cheat=False, free_read=False):
        al, G, Wo, mk = tp
        dig = ((obs.to(torch.int64)[:, :, None] >> SH_T) & 15).reshape(len(obs), -1)
        if not free_read:
            dig = torch.where(mk[gidx], dig, 0)
        v = al[gidx]
        for c in range(dig.shape[1]):
            if cheat and c % 2:
                continue
            v = torch.bmm(v[:, None, :], G[gidx, c, dig[:, c]])[:, 0]
            v = v / torch.clamp(v.abs().amax(1, keepdim=True), min=1e-30)
        return torch.bmm(v[:, None, :], Wo[gidx])[:, 0].argmax(1)

    def forward(self, g, obs, gidx, cheat=False, free_read=False):
        tp = self.to_t(g)
        o = torch.from_numpy(np.ascontiguousarray(obs, np.int64)).to(DEV)
        gi = torch.from_numpy(np.ascontiguousarray(gidx, np.int64)).to(DEV)
        return self.forward_t(tp, o, gi, cheat, free_read).cpu().numpy()


def make_g7():
    g7 = E7.G7(GS, "tt_digits")
    g7.fam = TorchMasked(g7.D, A)
    g7.pb = g7.fam.nbytes
    g7.glen = (g7.pb + g7.cb + 3) // 4 * 4
    return g7


def force_read_all(g):
    p, C = g
    return tuple(p[:3]) + (np.ones_like(p[3]),), C


def gpu_rollout(g7, g, seeds, metered, world_cheat="", log=False):
    """-> dict(sel, fit, cost, cells numpy [P]; logs if log)."""
    p, C = g
    fam = g7.fam
    tp = fam.to_t(p)
    P, k, S, D, W = len(C), len(seeds), g7.S, g7.D, g7.W
    n = P * k
    w = TorchWorld(g7.spec.mech, g7.spec.wid, device=DEV, cheat=world_cheat)
    obs = w.reset(np.tile(np.asarray(seeds, np.int64), P))
    Ct = torch.from_numpy(np.ascontiguousarray(C)).to(DEV)
    genv = torch.arange(P, device=DEV).repeat_interleave(k)
    grow = genv.repeat_interleave(S)
    abst = torch.zeros(n, device=DEV); mag = torch.zeros(n, device=DEV); cnt = torch.zeros(n, device=DEV)
    L = {"obs": [], "acts": [], "idx": [], "live": [], "regs": [], "charge": [], "alive": []} if log else None
    for t in range(g7.T):
        idx = fam.forward_t(tp, obs.reshape(n * S, D), grow).reshape(n, S)
        a = Ct[genv[:, None], idx].to(torch.int64)
        live = w.alive & ~w.done[:, None]
        x = (a % 8).sum(-1)
        abst += ((x == 0) & live).sum(1); mag += (x * live).sum(1); cnt += live.sum(1)
        if log:
            L["obs"].append(obs.clone()); L["acts"].append(a.clone()); L["idx"].append(idx.clone())
            L["live"].append(live.clone())
        w.step(a)
        if log:
            L["regs"].append(w.regs.clone()); L["charge"].append(w.charge.clone()); L["alive"].append(w.alive.clone())
        obs = w.observe()
    fit = torch.clamp_min(w.charge, 0).sum(1).reshape(P, k).sum(1).cpu().numpy().astype(np.int64)
    live_st = cnt.reshape(P, k).sum(1).cpu().numpy()
    bits = 4 * p[3].sum(1)
    cost = BETA * bits * live_st if metered else np.zeros(P)
    sel = (fit - np.rint(cost)).astype(np.int32)
    tot = np.maximum(live_st, 1)
    ab = abst.reshape(P, k).sum(1).cpu().numpy() / tot
    mg = mag.reshape(P, k).sum(1).cpu().numpy() / (tot * W * 7)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    out = {"sel": sel, "fit": fit, "cost": cost, "cells": cells, "live_slot_ticks": live_st, "bits": bits}
    if log:
        out["L"] = {kk: torch.stack(v).cpu().numpy() for kk, v in L.items()}
        out["done_tick"] = w.done_tick.cpu().numpy()
    return out


def world_oracle(g7, g, seeds, world_cheat=""):
    o = gpu_rollout(g7, g, seeds, False, world_cheat=world_cheat, log=True)
    L, dt = o["L"], o["done_tick"]
    k, P = len(seeds), len(g[1])
    bad, mt, mo = np.zeros(P, bool), 0, 0
    for e in range(P * k):
        th = hash_log(L["regs"][:, e], L["charge"][:, e], L["alive"][:, e], int(dt[e]))
        oh = hash_obs(L["obs"][:, e], int(dt[e]))
        rt, ro = reference(g7.spec.mech, g7.spec.wid, int(seeds[e % k]), L["acts"][:, e], with_obs=True)
        mt += th != rt; mo += oh != ro
        bad[e // k] |= (th != rt) or (oh != ro)
    return {"elites": P, "elites_failing": int(bad.sum()), "trace_mismatch": int(mt), "obs_mismatch": int(mo)}


def meter_oracle(g7, g, seeds, rows_per_elite=256, seed=0):
    """free_read cheat vs the masked float64 reference, on GPU-logged rows; eligibility from the reference only."""
    o = gpu_rollout(g7, g, seeds, True, log=True)
    L = o["L"]
    fam, p = g7.fam, g[0]
    k, P = len(seeds), len(g[1])
    rng = np.random.Generator(np.random.PCG64(seed))
    rows = elig = caught = honest_bad = 0
    for q in range(P):
        t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
        if len(t_i) == 0:
            continue
        pick = np.sort(rng.choice(len(t_i), size=min(rows_per_elite, len(t_i)), replace=False))
        t_i, e_i, s_i = t_i[pick], e_i[pick] + q * k, s_i[pick]
        ob = L["obs"][t_i, e_i, s_i]
        one = fam.one(p, q)
        ref = fam.ref_logits(one, ob)
        ref_free = fam.ref_logits(one, ob, ignore_mask=True)
        clear = gm.clear_rows(ref) & gm.clear_rows(ref_free)
        emitted = L["idx"][t_i, e_i, s_i]
        honest_bad += int(((emitted != ref.argmax(1)) & gm.clear_rows(ref)).sum())
        el = clear & (ref.argmax(1) != ref_free.argmax(1))
        cheat = fam.forward(p, ob, np.full(len(ob), q), free_read=True)
        rows += len(ob); elig += int(el.sum()); caught += int(((cheat != ref.argmax(1)) & el).sum())
    # cost oracle: numpy recount from the logged live mask
    live_st = L["live"].reshape(L["live"].shape[0], P, k, -1).sum(axis=(0, 2, 3))
    cost_ref = np.rint(BETA * 4 * p[3].sum(1).astype(np.float64) * live_st)
    cost_bad = int((cost_ref != np.rint(o["cost"])).sum())
    half_bad = int((np.rint(0.5 * BETA * 4 * p[3].sum(1) * live_st) != np.rint(o["cost"]))[p[3].sum(1) > 0].sum())
    half_elig = int((p[3].sum(1) > 0).sum())
    return {"rows": rows, "honest_mismatched_clear_rows": honest_bad, "free_read_eligible_rows": elig,
            "free_read_share": round(caught / elig, 4) if elig else 0.0, "cost_mismatch_elites": cost_bad,
            "half_cost_cheat_caught_elites": half_bad, "half_cost_cheat_eligible_elites": half_elig}


def job(ctx, gens: int = GENS, run_seeds: str = "0-7", port: int = 6392, audit_gens: int = AUDIT_GENS):
    import redis
    from primordial.cohorts.e.oracles import brain_verdict
    from primordial.qd.archive import LuaArchive
    lo, hi = (int(x) for x in run_seeds.split("-"))
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=port)
    g7 = make_g7()
    arms = (("cell", True, CELL), ("control", False, CELL_CTRL))
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref_emitted": False}
    if not st["ref_emitted"]:
        ctx.emit({"kind": "reference", "floor": FLOOR, "baseline_median": BASE_MED, "baseline_bytes": BASE_BYTES,
                  "beta": BETA, "genome_bytes": g7.glen, "status": "control"})
        st["ref_emitted"] = True
    todo = [(rs, ai) for rs in range(lo, hi + 1) for ai in range(2)]
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st)
        rs, ai = todo[st["next"]]
        arm, metered, cell = arms[ai]
        t0, c0 = time.perf_counter(), time.process_time()
        arch = LuaArchive(r, f"c-r4-05-{arm}-{rs}", g7.glen, sampler_seed=[9505, rs, ai])
        arch.clear()
        rng = np.random.Generator(np.random.PCG64([4505, rs, ai]))
        offers = offer_bad = 0
        for gen in range(gens):
            par = arch.sample(BATCH)
            g = g7.init(rng, BATCH) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
            if not metered:
                g = force_read_all(g)
            o = gpu_rollout(g7, g, F.TRAIN128, metered)
            if rs == lo and gen < audit_gens:
                offers += BATCH
                offer_bad += int((E7.rollout(g7, g, F.TRAIN128)[0].astype(np.int64) != o["fit"]).sum())
            arch.insert(o["cells"], o["sel"], g7.pack(g), np.zeros((BATCH, 2), np.uint32))
        el = arch.dump()
        arch.clear()
        order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
        raw = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, g7.glen)
        np.save(HOT / f"{arm}_r{rs}_top16.npy", raw)
        top = g7.unpack(raw)
        tr = gpu_rollout(g7, top, F.TRAIN128, metered)
        hd = gpu_rollout(g7, top, F.HELD64, metered)
        np_tr = E7.rollout(g7, top, F.TRAIN128)[0].astype(np.int64)
        np_hd = E7.rollout(g7, top, F.HELD64)[0].astype(np.int64)
        mask = top[0][3]
        row = {"kind": "run", "arm": arm, "cell": cell, "run_seed": rs, "gens": gens, "genomes": gens * BATCH,
               "genome_bytes": g7.glen, "archive_cells": len(el),
               "sel_top16_matches_archive": int(sum(int(a) == int(b[0]) for a, b in zip(tr["sel"], order[:TOP]))),
               "train128_per_seed": float(tr["fit"].mean() / len(F.TRAIN128)),
               "held64_per_seed": float(hd["fit"].mean() / len(F.HELD64)),
               "cost_per_seed_train": float(tr["cost"].mean() / len(F.TRAIN128)),
               "bits_read_median": float(np.median(4 * mask.sum(1))), "bits_read_top1": int(4 * mask[0].sum()),
               "features_read_top1": sorted({int(c // 4) for c in np.nonzero(mask[0])[0]}),
               "numpy_top16_mismatch_train": int((np_tr != tr["fit"]).sum()),
               "numpy_top16_mismatch_held": int((np_hd != hd["fit"]).sum()),
               "offers_audited_numpy": offers, "offers_numpy_mismatch": offer_bad,
               "status": "record" if metered else "control"}
        if rs == lo:
            wo = world_oracle(g7, top, E7.HELD8)
            wc = world_oracle(g7, top, E7.HELD8, "skip_lin")
            bv = brain_verdict(g7, top, E7.HELD8)
            row["world_oracle_honest"], row["world_oracle_skip_lin"] = wo, wc
            row["brain_verdict"] = {"clean": bv["clean"], "rule": bv["rule"],
                                    "cheats": {kk: vv for kk, vv in bv["cheats"].items() if kk != "ablate_top_features"}}
            ok = wo["elites_failing"] == 0 and wc["elites_failing"] >= 14 and bv["clean"]
            if metered:
                mo = meter_oracle(g7, top, E7.HELD8)
                row["meter_oracle"] = mo
                ok = (ok and mo["honest_mismatched_clear_rows"] == 0 and mo["free_read_eligible_rows"] > 0
                      and mo["free_read_share"] >= 0.9 and mo["cost_mismatch_elites"] == 0
                      and (mo["half_cost_cheat_eligible_elites"] == 0
                           or mo["half_cost_cheat_caught_elites"] == mo["half_cost_cheat_eligible_elites"]))
            st["clean"] = st["clean"] and ok
            row["oracle_ok"] = ok
        row["cpu_s"] = round(time.process_time() - c0, 2)
        row["wall_s"] = round(time.perf_counter() - t0, 2)
        st["held"][arm].append(row["held64_per_seed"])
        ctx.emit(row)
        st["next"] += 1
    s = {a: tuple(float(x) for x in np.percentile(st["held"][a], [25, 50, 75])) for a in st["held"]}
    bar = s["control"][1] - 0.5 * (s["control"][2] - s["control"][0])
    n = min(len(st["held"]["cell"]), len(st["held"]["control"]))
    ctx.emit({"kind": "summary", "cell": CELL, "n_runs": n,
              "held64_median_cell": round(s["cell"][1], 3), "iqr_cell": round(s["cell"][2] - s["cell"][0], 3),
              "held64_median_control": round(s["control"][1], 3),
              "iqr_control": round(s["control"][2] - s["control"][0], 3), "bar": round(bar, 3),
              "oracle_clean": st["clean"],
              "primary": "INDETERMINATE" if not st["clean"] else ("PASS" if n >= 8 and s["cell"][1] >= bar else "FAIL"),
              "progress_report_only": {a: round((s[a][1] - FLOOR) / (BASE_MED - FLOOR), 4) for a in s},
              "clause_a": "none: pressure bit_metering != train128_held64 and 11,640 B > 200 B baseline",
              "status": "record" if st["clean"] else "cheat"})


def qd() -> None:
    from primordial.fabric.rows import RowWriter
    from primordial.ops import qd_ledger
    rows = [json.loads(x) for x in ROWS.read_text(encoding="utf-8").splitlines() if x.strip()]
    summ = [x for x in rows if x.get("kind") == "summary"][-1]
    runs = [x for x in rows if x.get("kind") == "run"]
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        for arm, cell, status in (("cell", CELL, summ["status"]), ("control", CELL_CTRL, "control")):
            v = [x["held64_per_seed"] for x in runs if x["arm"] == arm]
            p25, p50, p75 = np.percentile(v, [25, 50, 75])
            q.write({"cell": cell, "mechanism": f"closed_loop_tt_digits_read_mask_{arm}_train128_{GENS}gens_gpu_world",
                     "fitness": {"held64_median": round(float(p50), 3), "iqr": round(float(p75 - p25), 3),
                                 "n_runs": len(v)},
                     "footprint": {"genome_bytes": runs[0]["genome_bytes"]},
                     "oracle": ("clean (GPU episodes trace+obs hash == wforge, skip_lin caught; E powered brain verdict; "
                                "free_read + cost oracles)") if summ["oracle_clean"] else "NOT clean",
                     "baseline": False, "cohort": "C", "status": status,
                     "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


def dev() -> None:
    """No rows: random genomes -- oracle eligibility, GPU==numpy, pack round trip, per-gen CPU."""
    from primordial.cohorts.e.oracles import brain_verdict
    g7 = make_g7()
    rng = np.random.Generator(np.random.PCG64(77))
    g = g7.init(rng, TOP)
    rt = g7.unpack(g7.pack(g))
    out = {"glen": g7.glen, "beta": BETA,
           "pack_roundtrip": all(np.array_equal(a, b) for a, b in zip(g[0], rt[0])) and np.array_equal(g[1], rt[1])}
    o = gpu_rollout(g7, g, F.TRAIN8, True)
    out["gpu_vs_numpy_fit_mismatch_train8"] = int((E7.rollout(g7, g, F.TRAIN8)[0].astype(np.int64) != o["fit"]).sum())
    out["world_honest"] = world_oracle(g7, g, E7.HELD8)
    out["world_skip_lin"] = world_oracle(g7, g, E7.HELD8, "skip_lin")
    bv = brain_verdict(g7, g, E7.HELD8)
    out["brain_verdict_clean"] = bv["clean"]
    out["brain_cheats"] = {kk: vv for kk, vv in bv["cheats"].items() if kk != "ablate_top_features"}
    out["meter"] = meter_oracle(g7, g, E7.HELD8)
    gg = g7.init(rng, BATCH)
    gpu_rollout(g7, gg, F.TRAIN128, True)
    c, t = time.process_time(), time.perf_counter()
    for _ in range(5):
        gg = g7.mutate(rng, gg)
        gpu_rollout(g7, gg, F.TRAIN128, True)
    out["train128_cpu_s_per_gen"] = round((time.process_time() - c) / 5, 4)
    out["train128_wall_s_per_gen"] = round((time.perf_counter() - t) / 5, 4)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"qd": qd, "dev": dev}[sys.argv[1]]()
