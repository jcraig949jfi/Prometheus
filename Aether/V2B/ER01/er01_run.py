"""AETH-V2B-ER01 unit runner: one world, one energy regime, one perturbation arm.

Operator order AETH-V2B-ER01 (2026-10-05): is the frozen medium a property of
aeth01.v1's local physics, or of the single B-balanced energy economy it was
studied under? The ONLY axis changed between regimes is the energy economy
(write cost, maintenance, replenishment amount/probability). Topology, opcode
semantics, arbitration, radius, schedule and the initial-condition family are
aeth01.v1 unchanged.

Physics: the FROZEN aeth01.v1 kernel, not modified and not re-implemented.
  --backend gpu  runpod/aeth01_canary/aeth01_gpu_kernel.py (CuPy)
  --backend cpu  test/reference/gpu_aeth01.py (independent NumPy text)
The two are compared state-digest-for-state-digest by er01_conformance.py.

Measurement only. This file assigns no disposition; er01_reduce.py applies
the preregistered rules. Every observable is computed from the lattice before
and after each tick; nothing is fed back into the dynamics.

Observables (directive s7), per bin of --bin ticks:
  tmpl_change_site   fraction of sites whose 4 template fields changed this tick
  tmpl_change_byte   fraction of template bytes changed per tick (4 per site)
  field_change       per-field byte change fraction per tick (opcode..payload)
  active_density     sites with opcode==WRITE and energy>=write_cost (pre-tick)
  write_density      sites with opcode==WRITE
  starved_density    WRITE sites with energy<write_cost
  energy mean / median / zero fraction (end of bin)
  rain_events        replenishment triggers per site per tick (keyed rho, exact)
  starve_events      active->starved transitions per site per tick
  revive_events      starved->active transitions per site per tick
  ever_changed       cumulative fraction of sites whose template ever changed
Late window (last --late ticks):
  frozen_strict      sites with NO template change at any tick in the window
  frozen_net64       historical H1b definition: no NET template change over the
                     final 64 ticks (end state == state 64 ticks earlier)
  per-site change-count distribution (gini, top-decile share)
  trivial-mobility attack (s8): among sites that changed in the final 64
  ticks, the fraction whose packed template state is exactly periodic with
  some period p<=16 over those 64 ticks; novelty = fraction of changes that
  produce a template state not held in the previous 16 ticks; field share.
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

SEMANTICS_ID = "aeth01.v1"
RUNNER_VERSION = "er01_run.v1"
P32 = 1 << 32


def prob(p):
    return int(round(p * P32))


# Energy-regime panel. Frozen in Aether/V2B/ER01/PREREGISTRATION.md; any edit
# here after the freeze SHA invalidates the run (the reducer checks the table
# hash recorded in every unit).
REGIMES = {
    # Historical reference (aeth02_falsifiers.B_BALANCED, scout round 2):
    # inflow 8 x 1/8 = 1.0/site/tick == maintenance.
    "R0": dict(label="B_balanced", write_cost=1, maintenance_cost=1,
               replenish_numer=prob(0.125), replenish_amount=8),
    # Historical ECONOMICS.md regime C (aeth01_scout / first light).
    "R1": dict(label="C_free_compute", write_cost=0, maintenance_cost=0,
               replenish_numer=0, replenish_amount=0),
    # Energy-rich, costs unchanged: rain probability x2 -> inflow 2.0/site/tick
    # = maintenance + one write per tick for an active site.
    "R2": dict(label="rich_rain_x2", write_cost=1, maintenance_cost=1,
               replenish_numer=prob(0.25), replenish_amount=8),
    # Scarcity, costs unchanged: rain probability /2 -> inflow 0.5/site/tick.
    "R3": dict(label="scarce_rain_half", write_cost=1, maintenance_cost=1,
               replenish_numer=prob(0.0625), replenish_amount=8),
}
PERTURBATION = {"P0": 0, "P1": prob(0.1)}

# Initial-condition family: historical sparse soup, 50% WRITE, uniform energy
# (aeth01_firstlight / aeth02 trajectories). Energy initialization is NOT
# coupled to the regime: every regime starts from the identical lattice for a
# given seed index (common random numbers).
INIT = dict(regime=R.SPARSE_SOUP, write_density=0.50, energy_mode=R.ENERGY_UNIFORM)
RNG_SEED_BASE = 0xE2010000      # ER01 namespace, initial lattice
PHYS_SEED_BASE = 0xE2011000     # ER01 namespace, keyed physics hash
HIST_SEEDS = (0xA37E01, 0x5C011701)   # continuity cell (aeth02 B_RNG0, B_SEED0)


def regime_table_hash():
    blob = json.dumps({"regimes": REGIMES, "pert": PERTURBATION, "init": INIT,
                       "rng_base": RNG_SEED_BASE, "phys_base": PHYS_SEED_BASE},
                      sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def seeds_for(seed_index):
    if seed_index < 0:
        return HIST_SEEDS
    return RNG_SEED_BASE + seed_index, PHYS_SEED_BASE + seed_index


def load_backend(name):
    if name == "gpu":
        import aeth01_gpu_kernel as K
        if K.BACKEND != "cupy":
            raise SystemExit("gpu backend requested but CuPy is not importable")
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def digest(fields):
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(np.asarray(getattr(f, "get", lambda: f)())).tobytes())
    return h.hexdigest()[:32]


def gini(counts_hist):
    """Gini of a non-negative integer distribution given as a histogram."""
    vals = np.arange(len(counts_hist), dtype=np.float64)
    n = counts_hist.sum()
    if n == 0:
        return 0.0
    cum = np.cumsum(counts_hist)
    mean = (vals * counts_hist).sum() / n
    if mean == 0:
        return 0.0
    # Gini = 1 - 2 * area under Lorenz curve (discrete, exact for histograms).
    share = np.cumsum(vals * counts_hist) / (vals * counts_hist).sum()
    pop = cum / n
    pop_prev = np.concatenate([[0.0], pop[:-1]])
    share_prev = np.concatenate([[0.0], share[:-1]])
    area = ((pop - pop_prev) * (share + share_prev) / 2.0).sum()
    return float(1.0 - 2.0 * area)


def run_unit(backend, regime, pert, seed_index, n, ticks, bin_ticks, late,
             digest_every=0, progress_every=0):
    xp, K = load_backend(backend)
    reg = REGIMES[regime]
    rng_seed, phys_seed = seeds_for(seed_index)
    fields, recipe = R.build_initial(INIT["regime"], n, n, rng_seed,
                                     write_density=INIT["write_density"],
                                     energy_mode=INIT["energy_mode"])
    state = [xp.asarray(f) for f in fields]
    w, m = reg["write_cost"], reg["maintenance_cost"]
    rn, ra = reg["replenish_numer"], reg["replenish_amount"]
    mut = PERTURBATION[pert]
    N = n * n
    packed_coords = K.pack_coords_vec(xp.arange(n).reshape(n, 1),
                                      xp.arange(n).reshape(1, n))

    def pack_template(s):
        return (s[0].astype(xp.uint32) << 24) | (s[1].astype(xp.uint32) << 16) | \
               (s[2].astype(xp.uint32) << 8) | s[3].astype(xp.uint32)

    ever = xp.zeros((n, n), dtype=bool)
    late_start = ticks - late
    tail = 64
    depth = 16
    late_count = xp.zeros((n, n), dtype=xp.int32)
    late_field = [0, 0, 0, 0]
    ring = None
    periodic = None
    tail_changed = xp.zeros((n, n), dtype=bool)
    tail_changes = 0
    tail_novel = 0
    snap64 = None

    series, digests = [], []
    acc = None
    t0 = time.time()

    def new_acc():
        return dict(tmpl_site=0, tmpl_byte=0, f=[0, 0, 0, 0], active=0, write=0,
                    starved=0, rain=0, starve=0, revive=0, ticks=0)

    acc = new_acc()
    for t in range(ticks):
        tick = t + 1          # aeth02 convention: first tick index is 1
        is_write = state[0] == K.WRITE_OPCODE
        active = is_write & (state[4].astype(xp.int16) >= w)
        out = K.gpu_step(n, n, phys_seed, tick, w, m, rn, ra, mut, *state)
        nxt = list(out[:5])
        ch = [nxt[i] != state[i] for i in range(4)]
        any_ch = ch[0] | ch[1] | ch[2] | ch[3]
        nxt_active = (nxt[0] == K.WRITE_OPCODE) & (nxt[4].astype(xp.int16) >= w)
        rain = K.rho_vec(phys_seed, tick, packed_coords, rn) if rn else None

        cnt = [int(c.sum()) for c in ch]
        acc["f"] = [a + b for a, b in zip(acc["f"], cnt)]
        acc["tmpl_byte"] += sum(cnt)
        acc["tmpl_site"] += int(any_ch.sum())
        acc["active"] += int(active.sum())
        acc["write"] += int(is_write.sum())
        acc["starved"] += int((is_write & ~active).sum())
        acc["rain"] += int(rain.sum()) if rain is not None else 0
        acc["starve"] += int((active & ~nxt_active & (nxt[0] == K.WRITE_OPCODE)).sum())
        acc["revive"] += int((~active & is_write & nxt_active).sum())
        acc["ticks"] += 1
        ever |= any_ch

        if t >= late_start:
            late_count += any_ch.astype(xp.int32)
            late_field = [a + b for a, b in zip(late_field, cnt)]
        # Ring of packed template states S_{t-depth+1} .. S_t (S_t = `state`,
        # the lattice before this tick's step; S_{t+1} = `nxt`).
        if t >= ticks - tail - depth:
            ring = (ring or []) + [pack_template(state)]
            ring = ring[-depth:]
        if t == ticks - tail:
            snap64 = [s.copy() for s in state[:4]]
            periodic = xp.ones((depth, n, n), dtype=bool)
        if t >= ticks - tail:
            cur_new = pack_template(nxt)
            # period p over the tail: S_{t+1} == S_{t+1-p} == ring[-p], every tick
            for p in range(1, depth + 1):
                periodic[p - 1] &= (cur_new == ring[-p])
            seen = xp.zeros((n, n), dtype=bool)
            for r in ring:
                seen |= (r == cur_new)
            novel = any_ch & ~seen
            tail_changes += int(any_ch.sum())
            tail_novel += int(novel.sum())
            tail_changed |= any_ch

        state = nxt

        if digest_every and (tick % digest_every == 0):
            digests.append([tick, digest(state)])
        if (tick % bin_ticks == 0) or tick == ticks:
            be = xp.bincount(state[4].ravel(), minlength=256)
            hist_e = np.asarray(getattr(be, "get", lambda: be)())
            cum = np.cumsum(hist_e)
            k = acc["ticks"] * N
            row = {
                "tick": tick,
                "tmpl_change_site": acc["tmpl_site"] / k,
                "tmpl_change_byte": acc["tmpl_byte"] / (4 * k),
                "field_change": [x / k for x in acc["f"]],
                "active_density": acc["active"] / k,
                "write_density": acc["write"] / k,
                "starved_density": acc["starved"] / k,
                "rain_events": acc["rain"] / k,
                "starve_events": acc["starve"] / k,
                "revive_events": acc["revive"] / k,
                "energy_mean": float((hist_e * np.arange(256)).sum() / N),
                "energy_median": int(np.searchsorted(cum, (N + 1) // 2)),
                "energy_zero_frac": float(hist_e[0] / N),
                "ever_changed": float(int(ever.sum()) / N),
            }
            series.append(row)
            acc = new_acc()
            if progress_every and tick % progress_every == 0:
                print("[%s %s s%d] tick %d tmpl_site %.6f active %.4f E %.1f  %.1fs"
                      % (regime, pert, seed_index, tick, row["tmpl_change_site"],
                         row["active_density"], row["energy_mean"], time.time() - t0),
                      file=sys.stderr, flush=True)

    # Late-window summaries.
    lc = np.asarray(getattr(late_count, "get", lambda: late_count)())
    hist_c = np.bincount(lc.ravel(), minlength=late + 1)
    changed_sites = int((lc > 0).sum())
    sorted_c = np.sort(lc.ravel())[::-1]
    top = sorted_c[: max(1, N // 10)].sum()
    tot = sorted_c.sum()
    net64 = snap64[0] != state[0]
    for i in range(1, 4):
        net64 |= snap64[i] != state[i]
    per = periodic.any(axis=0) & tail_changed
    n_tail_changed = int(tail_changed.sum())
    late_tot = sum(late_field)
    result = {
        "schema": "aether.er01.unit.v1",
        "runner": RUNNER_VERSION,
        "semantics_id": SEMANTICS_ID,
        "regime_table_hash": regime_table_hash(),
        "backend": backend,
        "regime": regime, "regime_label": reg["label"],
        "energy": {k: reg[k] for k in ("write_cost", "maintenance_cost",
                                       "replenish_numer", "replenish_amount")},
        "perturbation": pert, "mut_numer": mut,
        "seed_index": seed_index, "rng_seed": rng_seed, "phys_seed": phys_seed,
        "n": n, "ticks": ticks, "bin_ticks": bin_ticks, "late": late,
        "initial_digest": recipe["initial_state_digest"],
        "final_digest": digest(state),
        "digests": digests,
        "series": series,
        "late_window": {
            "frozen_strict": 1.0 - changed_sites / N,
            "frozen_net64": 1.0 - float(int(net64.sum())) / N,
            "tmpl_change_site_per_tick": float(lc.sum()) / (late * N),
            "field_share": [x / late_tot if late_tot else 0.0 for x in late_field],
            "change_count_gini_changed_sites": gini(hist_c[1:]) if changed_sites else 0.0,
            "top_decile_share": float(top / tot) if tot else 0.0,
            "changed_sites": changed_sites,
            "tail64_changed_sites": n_tail_changed,
            "tail64_periodic_le16_frac": (float(int(per.sum())) / n_tail_changed
                                          if n_tail_changed else None),
            "tail64_novel_change_frac": (tail_novel / tail_changes
                                         if tail_changes else None),
            "tail64_changes": tail_changes,
        },
        "wall_seconds": time.time() - t0,
    }
    if backend == "gpu":
        import cupy
        result["gpu"] = {
            "device": cupy.cuda.runtime.getDeviceProperties(0)["name"].decode(),
            "mempool_used_bytes": int(cupy.get_default_memory_pool().used_bytes()),
            "mempool_total_bytes": int(cupy.get_default_memory_pool().total_bytes()),
        }
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--regime", choices=sorted(REGIMES), required=True)
    ap.add_argument("--pert", choices=sorted(PERTURBATION), required=True)
    ap.add_argument("--seed-index", type=int, required=True,
                    help="-1 = historical aeth02 seeds (continuity cell)")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--ticks", type=int, required=True)
    ap.add_argument("--bin", type=int, default=100)
    ap.add_argument("--late", type=int, default=1000)
    ap.add_argument("--digest-every", type=int, default=0)
    ap.add_argument("--progress-every", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        print("exists, skipping: %s" % a.out, file=sys.stderr)
        return 0
    res = run_unit(a.backend, a.regime, a.pert, a.seed_index, a.n, a.ticks,
                   a.bin, a.late, a.digest_every, a.progress_every)
    try:
        import psutil
        res["host_rss_bytes"] = int(psutil.Process().memory_info().rss)
    except ImportError:
        res["host_rss_bytes"] = None
    tmp = a.out + ".partial"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(res, fh, separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done %s %s s%d final %s %.1fs" % (a.regime, a.pert, a.seed_index,
                                            res["final_digest"], res["wall_seconds"]),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
