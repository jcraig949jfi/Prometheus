"""AETH-V2B-OFFER01 unit runner: value-repertoire release (composition experiment).

Semantic-equivalence audit (see SEMANTICS.md): the order's "displaced-value uptake" rule IS the V2-B TEST-3 exchange
switch (aeth03_variants mob_r?x1e?: "a winning template write hands the displaced byte back to the EMITTER's
payload", an incoming payload write standing). L2 = reaim1 + exchange is therefore a COMPOSITION of two existing
mechanisms, not new physics.

LAWS (B_balanced energy, perturbation OFF, D50 sparse soup; seeds rng 0xE2010000+k, physics 0xE2011000+k)
  L1  aeth01.reaim1           after the frozen aeth01.v1 tick, every WRITE source whose proposal WON (any field)
                              gets arg0 += 1 (mod 256), unless its own arg0 received a winning write that tick.
  X   aeth03.mob_r0x1e0       exchange only: every source whose TEMPLATE proposal (field 0-3) won gets
      (exact TEST-3 law)      payload := the target byte it displaced (pre-tick value), unless its own payload
                              received a winning write that tick. Bit-identical to aeth03_variants.step("mob_r0x1e0").
  L2  aeth01.reaim_offer1     L1's re-aim AND X's exchange, applied together after the frozen tick. They act on
                              different fields (arg0 / payload); each yields to a committed external write on its
                              own field. Ordering: (1) aeth01.v1 commits all writes; (2) re-aim on arg0;
                              (3) displaced-value uptake on payload.

CHANNELS (never a transformed/subtracted counter)
  DOWNSTREAM  opcode, arg1 held values: no rule touches them, so every change there is an ordinary committed write.
  DELIVERED   payload "delivered view": per site, the last payload value delivered by an ordinary winning write
              (initialised to the payload at window start). DIRECT_UPTAKE never changes it.
  RAW_PAYLOAD payload as stored (includes direct uptake): diagnostic only.
PROVENANCE
  acquired[site]: the site's payload byte originated in an uptake event (set on uptake; on an ordinary payload write
  the target inherits the SOURCE's flag). DELIVERED_CONTENT = winning template writes whose source payload was
  acquired; DOWNSTREAM_NONPAYLOAD = those landing in opcode/arg1.
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, AETHER, os.path.join(AETHER, "test"), os.path.join(AETHER, "runpod", "aeth01_canary"),
          os.path.join(AETHER, "V2B", "AIM02")):
    sys.path.insert(0, p)

import aim02_meter as MTR  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402

RUNNER_VERSION = "offer01_run.v1"
LAWS = {"L1": "aeth01.reaim1", "X": "aeth03.mob_r0x1e0", "L2": "aeth01.reaim_offer1"}
ENERGY = dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8)
DENSITY = 0.50
RNG_SEED_BASE = 0xE2010000
PHYS_SEED_BASE = 0xE2011000


def table_hash():
    blob = json.dumps({"laws": LAWS, "energy": ENERGY, "dens": DENSITY, "rng": RNG_SEED_BASE,
                       "phys": PHYS_SEED_BASE, "bins": MTR.BIN_EDGES}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def load_backend(name):
    if name == "gpu":
        import aeth01_gpu_kernel as K
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def digest(fields):
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(np.asarray(getattr(f, "get", lambda: f)())).tobytes())
    return h.hexdigest()[:32]


def law_step(xp, K, law, n, seed, tick, s):
    """Returns (next_state, obs, reaim_mask, uptake_mask, displaced)."""
    obs = []
    out = K.gpu_step(n, n, seed, tick, ENERGY["write_cost"], ENERGY["maintenance_cost"],
                     ENERGY["replenish_numer"], ENERGY["replenish_amount"], 0, *s, observer=obs)
    nxt = list(out[:5])
    won_any = xp.zeros((n, n), dtype=bool)
    won_tmpl = xp.zeros((n, n), dtype=bool)
    disp = xp.zeros((n, n), dtype=xp.uint8)
    for f in range(5):
        slot = obs[f][0]
        for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
            m = xp.roll(slot == sl, (dr, dc), axis=(0, 1))          # source positions that won into field f
            won_any |= m
            if f < 4:
                won_tmpl |= m
                disp = xp.where(m, xp.roll(s[f], (dr, dc), axis=(0, 1)), disp)   # pre-tick byte at its target
    reaim = uptake = None
    if law in ("L1", "L2"):
        reaim = won_any & ~(obs[1][0] != 255)
        nxt[1] = xp.where(reaim, (nxt[1].astype(xp.uint16) + 1).astype(xp.uint8), nxt[1])
    if law in ("X", "L2"):
        uptake = won_tmpl & ~(obs[3][0] != 255)
        nxt[3] = xp.where(uptake, disp, nxt[3])
    return nxt, obs, reaim, uptake, disp


def run_unit(backend, law, k, n, ticks, window, step=2, digest_every=0):
    xp, K = load_backend(backend)
    fields, recipe = R.build_initial(R.SPARSE_SOUP, n, n, RNG_SEED_BASE + k, write_density=DENSITY,
                                     energy_mode=R.ENERGY_UNIFORM)
    s = [xp.asarray(f) for f in fields]
    phys = PHYS_SEED_BASE + k
    start = ticks - window
    acquired = xp.zeros((n, n), dtype=bool)
    dv = None
    fr_down, fr_dv, fr_raw = [], [], []
    wpay = []                                   # raw payload of sample sites that are WRITE at window start
    c = {k2: xp.zeros((), dtype=xp.int64) for k2 in
         ("tmpl_writes", "deliv_acq", "deliv_acq_nonpay", "tmpl_changes", "uptake_changes", "uptake_events",
          "reaim_events", "dv_changes")}
    digests = []
    t0 = time.time()
    for t in range(ticks):
        nxt, obs, reaim, uptake, disp = law_step(xp, K, law, n, phys, t + 1, s)
        # provenance: source flag for each target (field f) = flag of the winning source
        new_acq = acquired.copy()
        tgt_flag = []
        for f in range(4):
            slot = obs[f][0]
            fl = xp.zeros((n, n), dtype=bool)
            for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
                fl |= (slot == sl) & xp.roll(acquired, (-dr, -dc), axis=(0, 1))
            tgt_flag.append(fl)
        pay_written = obs[3][0] != 255
        new_acq = xp.where(pay_written, tgt_flag[3], new_acq)
        if uptake is not None:
            new_acq = new_acq | uptake
        if t + 1 > start:
            for f in range(4):
                w = obs[f][0] != 255
                c["tmpl_writes"] += w.sum(dtype=xp.int64)
                c["deliv_acq"] += (w & tgt_flag[f]).sum(dtype=xp.int64)
                if f in (0, 2):
                    c["deliv_acq_nonpay"] += (w & tgt_flag[f]).sum(dtype=xp.int64)
                c["tmpl_changes"] += (nxt[f] != s[f]).sum(dtype=xp.int64)
            if uptake is not None:
                c["uptake_events"] += uptake.sum(dtype=xp.int64)
                c["uptake_changes"] += (uptake & (nxt[3] != s[3]) & ~pay_written).sum(dtype=xp.int64)
            if reaim is not None:
                c["reaim_events"] += reaim.sum(dtype=xp.int64)
        if t + 1 == start:
            dv = nxt[3].copy()
            wmask = (nxt[0] == K.WRITE_OPCODE)[::step, ::step].ravel()
        elif dv is not None:
            dv_new = xp.where(pay_written, nxt[3], dv)
            c["dv_changes"] += (dv_new != dv).sum(dtype=xp.int64)
            dv = dv_new
        if t + 1 >= start:
            if dv is None:
                dv = nxt[3].copy()
                wmask = (nxt[0] == K.WRITE_OPCODE)[::step, ::step].ravel()
            fr_down.append(xp.concatenate([nxt[0][::step, ::step].ravel(), nxt[2][::step, ::step].ravel()]))
            fr_dv.append(dv[::step, ::step].ravel())
            fr_raw.append(nxt[3][::step, ::step].ravel())
            wpay.append(nxt[3][::step, ::step].ravel()[wmask])
        acquired = new_acq
        s = nxt
        if digest_every and (t + 1) % digest_every == 0:
            digests.append([t + 1, digest(s)])
    res = {"schema": "aether.offer01.unit.v1", "runner": RUNNER_VERSION, "table_hash": table_hash(),
           "backend": backend, "law": law, "semantics_id": LAWS[law], "seed_index": k, "n": n, "ticks": ticks,
           "window": window, "step": step, "initial_digest": recipe["initial_state_digest"],
           "final_digest": digest(s), "digests": digests,
           "counts_late": {kk: int(v) for kk, v in c.items()},
           "downstream": MTR.analyze(xp, xp.stack(fr_down)),
           "delivered": MTR.analyze(xp, xp.stack(fr_dv)),
           "raw_payload_diag": MTR.analyze(xp, xp.stack(fr_raw)),
           "writer_payload_diag": MTR.analyze(xp, xp.stack(wpay)) if len(wpay) and wpay[0].size else None,
           "wall_seconds": time.time() - t0}
    if backend == "gpu":
        import cupy
        res["gpu"] = {"mempool_total_bytes": int(cupy.get_default_memory_pool().total_bytes())}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--law", choices=sorted(LAWS), required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--ticks", type=int, required=True)
    ap.add_argument("--window", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        return 0
    res = run_unit(a.backend, a.law, a.seed_index, a.n, a.ticks, a.window)
    try:
        import psutil
        res["host_rss_bytes"] = int(psutil.Process().memory_info().rss)
    except ImportError:
        res["host_rss_bytes"] = None
    tmp = a.out + ".partial"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(res, fh, separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done %s s%d %s %.1fs" % (a.law, a.seed_index, res["final_digest"], res["wall_seconds"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
