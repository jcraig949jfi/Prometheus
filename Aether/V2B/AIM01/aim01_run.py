"""AETH-V2B-AIM01 unit runner: frozen-aim causal test.

Operator order roles/Aether/prompts/2026-10-05_aim01. Two laws x three initial
WRITE densities, B_balanced energy, perturbation OFF.

LAWS
  L0  aeth01.v1        the frozen kernel, unmodified.
  L1  aeth01.reaim1    aeth01.v1 plus ONE rule: after the frozen tick, every
                       WRITE source whose proposal WON its target contest this
                       tick (any field, including an energy transfer) advances
                       its own arg0 byte by 1 (mod 256), which advances its
                       direction (arg0 mod 4) by exactly 1 (mod 4). If the
                       source's own arg0 was itself the target of a winning
                       write this tick, the written value stands and no
                       re-aim is applied (replacement dominates).
  The law is implemented as a wrapper: the frozen kernel runs with its own
  observer side channel (best_slot per target per field), winners are read
  from it, and arg0 is post-adjusted. Under L0 the same observer runs and the
  adjustment is empty, so L0 instrumentation is checked bit-identical to the
  ER01 runner (aim01_conformance.py).

INITIAL DENSITY (paired construction)
  observatory.aeth01_run.build_initial(sparse_soup, write_density=d) with the
  SAME rng seed for d in {0.25, 0.50, 0.75}. The generator draws background
  opcode, then one uniform u per site (WRITE iff u < d), then arg0, arg1,
  payload, energy, in a fixed order and size independent of d. Hence within a
  seed every byte is identical across densities except the opcode of sites
  with u in [d_lo, d_hi), which are WRITE at the higher density and keep their
  background (non-WRITE) opcode at the lower one; WRITE sets are nested
  D25 < D50 < D75. Checked per seed by aim01_conformance.py.
  Seed namespace = ER01's (rng 0xE2010000+k, physics 0xE2011000+k), so L0 D50
  seed k IS ER01 R0 P0 seed k (continuity).

RAW vs EFFECT
  RAW    template fields as stored.
  EFFECT the same, except arg0 is read as (arg0 - c) mod 256, where c is the
         per-site count of re-aims the law has applied. A re-aim therefore
         never registers as an EFFECT change; a write that lands on arg0 does.
         Under L0, c = 0 and EFFECT == RAW.
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
sys.path.insert(0, AETHER)
sys.path.insert(0, os.path.join(AETHER, "test"))
sys.path.insert(0, os.path.join(AETHER, "runpod", "aeth01_canary"))

from observatory import aeth01_run as R  # noqa: E402

RUNNER_VERSION = "aim01_run.v1"
LAWS = {"L0": "aeth01.v1", "L1": "aeth01.reaim1"}
DENSITIES = {"D25": 0.25, "D50": 0.50, "D75": 0.75}
ENERGY = dict(label="B_balanced", write_cost=1, maintenance_cost=1,
              replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8)
MUT_NUMER = 0
RNG_SEED_BASE = 0xE2010000
PHYS_SEED_BASE = 0xE2011000
TAIL = 64
DEPTH = 16


def table_hash():
    blob = json.dumps({"laws": LAWS, "dens": DENSITIES, "energy": ENERGY, "mut": MUT_NUMER,
                       "rng": RNG_SEED_BASE, "phys": PHYS_SEED_BASE}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def load_backend(name):
    if name == "gpu":
        import aeth01_gpu_kernel as K
        if K.BACKEND != "cupy":
            raise SystemExit("gpu backend requested but CuPy is not importable")
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def host(x):
    return np.asarray(getattr(x, "get", lambda: x)())


def digest(fields):
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(host(f)).tobytes())
    return h.hexdigest()[:32]


# ----------------------------------------------------------------- the law

def law_step(xp, K, law, n, seed, tick, state):
    """One tick of L0 or L1. Returns (next_state, reaim_mask, targeted[5])."""
    obs = []
    out = K.gpu_step(n, n, seed, tick, ENERGY["write_cost"], ENERGY["maintenance_cost"],
                     ENERGY["replenish_numer"], ENERGY["replenish_amount"], MUT_NUMER,
                     *state, observer=obs)
    nxt = list(out[:5])
    targeted = [o[0] != 255 for o in obs]          # (site, field) received an executed write
    if law == "L0":
        return nxt, None, targeted
    won = xp.zeros((n, n), dtype=bool)
    for f in range(5):
        best_slot = obs[f][0]
        for s, (dr, dc, _req) in enumerate(K._NEIGHBOR_SLOTS):
            # slot s at target t gathers from source t + (dr, dc)
            won |= xp.roll(best_slot == s, (dr, dc), axis=(0, 1))
    reaim = won & ~targeted[1]
    nxt[1] = xp.where(reaim, (nxt[1].astype(xp.uint16) + 1).astype(xp.uint8), nxt[1])
    return nxt, reaim, targeted


def initial_support(xp, K, state):
    """(site, field) targets implied by every initial WRITE site's aim (energy-blind)."""
    is_write = state[0] == K.WRITE_OPCODE
    direction = state[1] % 4
    field = state[2] % 5
    sf = []
    for f in range(5):
        acc = xp.zeros(is_write.shape, dtype=bool)
        for (dr, dc, req) in K._NEIGHBOR_SLOTS:
            # source at t+(dr,dc) with direction req points at t
            src_ok = is_write & (direction == req) & (field == f)
            acc |= xp.roll(src_ok, (-dr, -dc), axis=(0, 1))
        sf.append(acc)
    return sf


# ----------------------------------------------------------------- the meter

class Meter:
    """Measurement only. Fed (state, next, reaim, targeted) every tick; never writes state.

    Synthetic known-answer fixtures drive it directly (Aether/test/test_aim01_meter.py)."""

    def __init__(self, xp, n, ticks, bin_ticks, late, init_sf, write_cost=1):
        self.xp, self.n, self.N, self.T = xp, n, n * n, ticks
        self.bin, self.late, self.w = bin_ticks, late, write_cost
        z = lambda dt=bool: xp.zeros((n, n), dtype=dt)  # noqa: E731
        self.c = z(xp.uint8)
        self.init_sf = init_sf
        self.init_site = init_sf[0] | init_sf[1] | init_sf[2] | init_sf[3] | init_sf[4]
        self.init_tmpl_sf = init_sf[:4]
        self.ever_eff = z()
        self.ever_raw = z()
        self.ever_eff_sf = [z() for _ in range(4)]
        self.ever_tgt_sf = [z() for _ in range(5)]
        self.late_eff = z(xp.int32)
        self.late_out_init = xp.zeros((), dtype=xp.int64)
        self.late_raw = xp.zeros((), dtype=xp.int64)
        self.late_field = [xp.zeros((), dtype=xp.int64) for _ in range(4)]
        self.subset_violations = xp.zeros((), dtype=xp.int64)
        self.ring = []
        self.nonaim_tail = []
        self.periodic = None
        self.tail_changed = z()
        self.tail_changes = 0
        self.tail_novel = 0
        self.snap64 = None
        self.series = []
        self.t = 0
        self._new_acc()

    def _new_acc(self):
        z = lambda: self.xp.zeros((), dtype=self.xp.int64)  # noqa: E731
        self.acc = dict(eff_site=z(), raw_site=z(), eff_f=[z() for _ in range(4)], reaim=z(),
                        active=z(), write=z(), starved=z(), ticks=0)

    def eff_fields(self, s, c):
        xp = self.xp
        a0 = (s[1].astype(xp.int16) - c.astype(xp.int16)) % 256
        return [s[0], a0.astype(xp.uint8), s[2], s[3]]

    def pack(self, e):
        xp = self.xp
        return (e[0].astype(xp.uint32) << 24) | (e[1].astype(xp.uint32) << 16) | \
               (e[2].astype(xp.uint32) << 8) | e[3].astype(xp.uint32)

    def pack_nonaim(self, e):
        xp = self.xp
        return (e[0].astype(xp.uint32) << 16) | (e[2].astype(xp.uint32) << 8) | e[3].astype(xp.uint32)

    def update(self, state, nxt, reaim, targeted):
        xp, t, T = self.xp, self.t, self.T
        e_prev = self.eff_fields(state, self.c)
        c_next = self.c if reaim is None else (self.c + reaim.astype(xp.uint8))
        e_next = self.eff_fields(nxt, c_next)
        ch_eff = [e_next[i] != e_prev[i] for i in range(4)]
        ch_raw = [nxt[i] != state[i] for i in range(4)]
        any_eff = ch_eff[0] | ch_eff[1] | ch_eff[2] | ch_eff[3]
        any_raw = ch_raw[0] | ch_raw[1] | ch_raw[2] | ch_raw[3]
        is_write = state[0] == 1
        active = is_write & (state[4].astype(xp.int16) >= self.w)

        a = self.acc
        cnt = [c.sum(dtype=xp.int64) for c in ch_eff]
        a["eff_f"] = [x + y for x, y in zip(a["eff_f"], cnt)]
        a["eff_site"] += any_eff.sum(dtype=xp.int64)
        a["raw_site"] += any_raw.sum(dtype=xp.int64)
        if reaim is not None:
            a["reaim"] += reaim.sum(dtype=xp.int64)
        a["active"] += active.sum(dtype=xp.int64)
        a["write"] += is_write.sum(dtype=xp.int64)
        a["starved"] += (is_write & ~active).sum(dtype=xp.int64)
        a["ticks"] += 1

        self.ever_eff |= any_eff
        self.ever_raw |= any_raw
        for f in range(4):
            self.ever_eff_sf[f] |= ch_eff[f]
            self.subset_violations += (ch_eff[f] & ~targeted[f]).sum(dtype=xp.int64)
        for f in range(5):
            self.ever_tgt_sf[f] |= targeted[f]

        if t >= T - self.late:
            self.late_eff += any_eff.astype(xp.int32)
            self.late_out_init += (any_eff & ~self.init_site).sum(dtype=xp.int64)
            self.late_raw += any_raw.sum(dtype=xp.int64)
            self.late_field = [x + y for x, y in zip(self.late_field, cnt)]

        # tail attack on EFFECT state (ring holds S_{t-DEPTH+1}..S_t)
        if t >= T - TAIL - DEPTH:
            self.ring = (self.ring + [self.pack(e_prev)])[-DEPTH:]
        if t == T - TAIL:
            self.snap64 = [x.copy() for x in e_prev]
            self.periodic = xp.ones((DEPTH, self.n, self.n), dtype=bool)
            self.nonaim_tail = [self.pack_nonaim(e_prev)]
        if t >= T - TAIL:
            cur = self.pack(e_next)
            for p in range(1, DEPTH + 1):
                self.periodic[p - 1] &= (cur == self.ring[-p])
            seen = xp.zeros((self.n, self.n), dtype=bool)
            for r in self.ring:
                seen |= (r == cur)
            self.tail_changes += int(any_eff.sum())
            self.tail_novel += int((any_eff & ~seen).sum())
            self.tail_changed |= any_eff
            self.nonaim_tail.append(self.pack_nonaim(e_next))
        self.c = c_next
        self.t += 1
        tick = self.t
        if tick % self.bin == 0 or tick == T:
            self._emit(tick, nxt)
        if tick == T:
            self.final_eff = e_next

    def _emit(self, tick, nxt):
        xp, a, N = self.xp, self.acc, self.N
        k = a["ticks"] * N
        be = xp.bincount(nxt[4].ravel(), minlength=256)
        he = host(be)
        cum = np.cumsum(he)
        tgt_t = sum(int(x.sum()) for x in self.ever_tgt_sf[:4])
        init_t = sum(int(x.sum()) for x in self.init_tmpl_sf)
        tgt_site = self.ever_tgt_sf[0] | self.ever_tgt_sf[1] | self.ever_tgt_sf[2] | self.ever_tgt_sf[3]
        self.series.append({
            "tick": tick,
            "eff_turnover": int(a["eff_site"]) / k,
            "raw_turnover": int(a["raw_site"]) / k,
            "eff_field": [int(x) / k for x in a["eff_f"]],
            "reaim_rate": int(a["reaim"]) / k,
            "active_density": int(a["active"]) / k,
            "write_density": int(a["write"]) / k,
            "starved_density": int(a["starved"]) / k,
            "energy_mean": float((he * np.arange(256)).sum() / N),
            "energy_median": int(np.searchsorted(cum, (N + 1) // 2)),
            "energy_zero_frac": float(he[0] / N),
            "ever_changed_eff": int(self.ever_eff.sum()) / N,
            "ever_changed_raw": int(self.ever_raw.sum()) / N,
            "ever_targeted_tmpl_sf": tgt_t / (4 * N),
            "ever_targeted_site": int(tgt_site.sum()) / N,
            "target_support_growth_sf": (tgt_t - init_t) / (4 * N),
        })
        self._new_acc()

    def finalize(self):
        xp, N, late = self.xp, self.N, self.late
        lc = host(self.late_eff)
        changed_sites = int((lc > 0).sum())
        net = self.snap64[0] != self.final_eff[0]
        for i in range(1, 4):
            net |= self.snap64[i] != self.final_eff[i]
        per = self.periodic.any(axis=0) & self.tail_changed
        ntc = int(self.tail_changed.sum())
        lf = [int(x) for x in self.late_field]
        lt = sum(lf)
        # unique non-AIM states over the final TAIL+1 states, among sites that changed (EFFECT)
        stack = xp.sort(xp.stack(self.nonaim_tail), axis=0)
        uniq = 1 + (stack[1:] != stack[:-1]).sum(axis=0)
        uniq_changed = host(uniq[self.tail_changed]) if ntc else np.array([])
        tgt_sf_t = [x for x in self.ever_tgt_sf[:4]]
        new_t = [tgt_sf_t[f] & ~self.init_tmpl_sf[f] for f in range(4)]
        new_n = sum(int(x.sum()) for x in new_t)
        new_ch = sum(int((new_t[f] & self.ever_eff_sf[f]).sum()) for f in range(4))
        init_n = sum(int(x.sum()) for x in self.init_tmpl_sf)
        init_ch = sum(int((self.init_tmpl_sf[f] & self.ever_eff_sf[f]).sum()) for f in range(4))
        tgt_site = tgt_sf_t[0] | tgt_sf_t[1] | tgt_sf_t[2] | tgt_sf_t[3]
        ev = self.ever_eff
        n_ev = int(ev.sum())
        return {
            "frozen_strict_eff": 1.0 - changed_sites / N,
            "frozen_net64_eff": 1.0 - int(net.sum()) / N,
            "late_turnover_eff": float(lc.sum()) / (late * N),
            "late_turnover_raw": int(self.late_raw) / (late * N),
            "late_out_init_share": (int(self.late_out_init) / float(lc.sum())) if lc.sum() else None,
            "late_field_share_eff": [x / lt if lt else 0.0 for x in lf],
            "tail64_changed_sites": ntc,
            "tail64_periodic_le16_frac": int(per.sum()) / ntc if ntc else None,
            "tail64_novel_change_frac": self.tail_novel / self.tail_changes if self.tail_changes else None,
            "tail64_unique_nonaim_mean": float(uniq_changed.mean()) if ntc else None,
            "ever_changed_eff": n_ev / N,
            "ever_changed_raw": int(self.ever_raw.sum()) / N,
            "ever_targeted_site": int(tgt_site.sum()) / N,
            "ever_targeted_tmpl_sf": sum(int(x.sum()) for x in tgt_sf_t) / (4 * N),
            "init_support_site": int(self.init_site.sum()) / N,
            "init_support_tmpl_sf": init_n / (4 * N),
            "change_given_new_target": new_ch / new_n if new_n else None,
            "change_given_init_target": init_ch / init_n if init_n else None,
            "overlap_changed_in_targeted": int((ev & tgt_site).sum()) / n_ev if n_ev else None,
            "overlap_changed_in_init": int((ev & self.init_site).sum()) / n_ev if n_ev else None,
            "subset_violations": int(self.subset_violations),
        }


def run_unit(backend, law, dens, k, n, ticks, bin_ticks, late, digest_every=0):
    xp, K = load_backend(backend)
    rng_seed, phys = RNG_SEED_BASE + k, PHYS_SEED_BASE + k
    fields, recipe = R.build_initial(R.SPARSE_SOUP, n, n, rng_seed,
                                     write_density=DENSITIES[dens], energy_mode=R.ENERGY_UNIFORM)
    state = [xp.asarray(f) for f in fields]
    meter = Meter(xp, n, ticks, bin_ticks, late, initial_support(xp, K, state), ENERGY["write_cost"])
    digests = []
    t0 = time.time()
    for t in range(ticks):
        nxt, reaim, targeted = law_step(xp, K, law, n, phys, t + 1, state)
        meter.update(state, nxt, reaim, targeted)
        state = nxt
        if digest_every and (t + 1) % digest_every == 0:
            digests.append([t + 1, digest(state)])
    res = {
        "schema": "aether.aim01.unit.v1", "runner": RUNNER_VERSION, "table_hash": table_hash(),
        "backend": backend, "law": law, "semantics_id": LAWS[law], "density_id": dens,
        "write_density": DENSITIES[dens], "write_density_realized": recipe["write_density_realized"],
        "seed_index": k, "rng_seed": rng_seed, "phys_seed": phys, "n": n, "ticks": ticks,
        "bin_ticks": bin_ticks, "late": late, "initial_digest": recipe["initial_state_digest"],
        "final_digest": digest(state), "digests": digests, "series": meter.series,
        "summary": meter.finalize(), "wall_seconds": time.time() - t0,
    }
    if backend == "gpu":
        import cupy
        res["gpu"] = {"device": cupy.cuda.runtime.getDeviceProperties(0)["name"].decode(),
                      "mempool_total_bytes": int(cupy.get_default_memory_pool().total_bytes())}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--law", choices=sorted(LAWS), required=True)
    ap.add_argument("--dens", choices=sorted(DENSITIES), required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--ticks", type=int, required=True)
    ap.add_argument("--bin", type=int, default=50)
    ap.add_argument("--late", type=int, default=2000)
    ap.add_argument("--digest-every", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        print("exists, skipping: %s" % a.out, file=sys.stderr)
        return 0
    res = run_unit(a.backend, a.law, a.dens, a.seed_index, a.n, a.ticks, a.bin, a.late, a.digest_every)
    try:
        import psutil
        res["host_rss_bytes"] = int(psutil.Process().memory_info().rss)
    except ImportError:
        res["host_rss_bytes"] = None
    tmp = a.out + ".partial"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(res, fh, separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done %s %s s%d %s %.1fs" % (a.law, a.dens, a.seed_index, res["final_digest"], res["wall_seconds"]),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
