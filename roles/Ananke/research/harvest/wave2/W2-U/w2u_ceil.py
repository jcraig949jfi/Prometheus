"""W2-U: joint light-cone + async cue-loss + actuator-wake ceilings for XOR and FLIP (extends W2-P task2_timing).

Imports W2-P's task2_timing READ-ONLY (earliest/next_awake/poisson_binom/ceilings); writes only under W2-U/out.
CPU only, 2 threads (inherited from w2p_common, which asserts torch.cuda.is_available() is False).

Engine facts (same as W2-P): SENSE only at an awake tick of the sensed site (not latched); packets wait in Acc;
S changes only on awake ticks; readout = actuator S0 at ro; delay >= max(1, lat_base + lat_hop*dist);
sync wake = t % period == 0; async wake iid per (site, tick) with p = p16(update_p)/65536.

XOR (y = c1*c2, c1 and c2 independent fair coins): any information set missing either cue gives exactly 1/2
per trial, so acc_k <= 1/2 + 1/2 * P(both cues causally precede an awake actuator tick <= ro_k).
  sync : indicator [arr1 <= ro and arr2 <= ro]  (== H-PLANT lightcone.bound, both sensors).
  async: condition on L = actuator's last awake tick in [t0, ro]; given L the two sensors' first awake
         ticks in their cue windows are independent; P = sum_L P(L) * ps1(L) * ps2(L).
  Combining en route (s1 -> s2 -> a) cannot beat the direct fastest path, so this is still an upper bound.

FLIP (x_k cue at s; y_k = m_k x_k; teacher y_k at the ACTUATOR during [t0+delta+1, t0+delta+1+cl), after ro_k;
m constant in a block of `block` trials and alternating between blocks; trial 0 of each block unscored):
  y_k = y_j * x_j * x_k * s_jk with s_jk = (-1)^{#block boundaries between j and k}  (known constant).
  Without information about x_k at the actuator by ro_k, y_k is a fresh fair coin -> 1/2.
  With it, y_k is determined iff some earlier pair (x_j, y_j) is available: x_j sensed at the sensor
  (S_j: sensor awake in cue window j) and y_j sensed at the actuator (Tch_j: actuator awake in teacher
  window j); the product x_j*x_k can be formed at the sensor (least restrictive route), so no extra
  transport of x_j is required. Otherwise m is a fair coin independent of the observed cues -> 1/2.
  => acc_k <= 1/2 + 1/2 * P(A_k) * P(M_k),   A_k = RELAY joint event for x_k (W2-P model),
     P(M_k) = 1 - prod_{j in scope(k)} (1 - P(S_j) P(Tch_j)).
  All windows (cue j at s, teacher j at a, cue k at s, actuator ticks in [t0_k, ro_k]) are disjoint in
  (site, tick), so under async wake they are independent; under sync with period <= cue_len every window
  contains an awake tick (P = 1), so sync FLIP == H-PLANT light cone.
  scope 'episode' (strict, any program): every j < k (m tracked across blocks; needs a clock).
  scope 'block' (no cross-block tracking): j in the same block, j < k  (k mod block of them).
  Assumed optimistic: perfect memory (no decay), no loss/caps/collisions/jitter, any route,
  intermediate relays fire on arrival, the actuator knows which pairs it holds.
  Copy-class (W2-L F5) ceiling under the same losses: on changed-cue trials (prob 1/2, independent of every
  wake/transport event) a copy policy is exactly 1/2, so copy <= 1/2 + (joint - 1/2)/2.
"""
from __future__ import annotations
import pathlib, sys, json
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-P"))
import task2_timing as T2          # noqa: E402  read-only reuse
from w2p_common import np, envs, assays, hc, Physics, H_int, HELD_NS  # noqa: E402,F401

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p


def _ps(base, L, p, cl):
    """P(sensor's first awake tick j in the cue window with base+j <= L)."""
    return sum(p * (1 - p) ** j for j in range(cl) if base + j <= L)


def ceilings(ph, env, seeds, terms=("cue", "wake", "teacher")):
    """Per-trial means of: lc (H-PLANT model), joint (all async terms), and for FLIP joint_block /
    joint_episode / copy_block. `terms` lets the known-answer test switch async terms off."""
    fam = env.family
    assert fam in ("XOR", "FLIP", "RELAY")
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    Pd, cl = env.period(), env.cue_len
    sync = ph.update_mode == "sync"
    per = ph.update_period if sync else 1
    p = 1.0 if sync else ph.p16(ph.update_p) / 65536.0
    nsens = 2 if fam == "XOR" else 1
    cache = {}

    def rel(s, phase):
        key = (int(s), phase)
        if key not in cache:
            cache[key] = T2.earliest(ph, int(s), phase, cl) - phase
        return cache[key]

    def awake_in(t_start):
        """P(site awake at >= 1 tick of a cue_len window starting at t_start)."""
        if sync:
            return 1.0 if T2.next_awake(t_start, ph) < t_start + cl else 0.0
        return 1 - (1 - p) ** cl if "teacher" in terms else 1.0

    lc, joint, jblk, jepi, cblk = [], [], [], [], []
    for b in range(0, len(seeds), 2):
        a = int(ridx[b])
        ss = [int(x) for x in sidx[b][:nsens]]
        for k in range(env.trials):
            if not ep.scored[b, k]:
                continue
            t0 = k * Pd
            ro_rel = int(ep.ro_tick[b, k]) - t0
            arr = [int(rel(s, t0 % per)[a]) for s in ss]
            inr = all(x <= ro_rel for x in arr)
            lc.append(0.5 + 0.5 * inr)
            # ---- P(all needed cues reach an awake actuator tick <= ro)
            if sync or not ({"cue", "wake"} & set(terms)):
                pa = float(inr)
            else:
                pc_cue = p if "cue" in terms else 1.0          # cue loss on/off
                pa = 0.0 if "wake" in terms else None
                if "wake" in terms:
                    for m in range(ro_rel + 1):
                        L = ro_rel - m
                        pL = p * (1 - p) ** m
                        prod = 1.0
                        for s, base in zip(ss, arr):
                            if s == a:
                                continue                        # optimistic, as W2-P
                            prod *= (_ps(base, L, pc_cue, cl) if pc_cue < 1 else float(base <= L))
                        pa += pL * prod
                else:   # cue loss only, actuator always awake
                    prod = 1.0
                    for s, base in zip(ss, arr):
                        prod *= _ps(base, ro_rel, pc_cue, cl)
                    pa = prod
            if fam != "FLIP":
                joint.append(0.5 + 0.5 * pa)
                continue
            # ---- FLIP: availability of an earlier (x_j, y_j) pair
            def pm(js):
                q = 1.0
                for j in js:
                    tj = j * Pd
                    q *= 1 - awake_in(tj) * awake_in(tj + env.delta + 1)
                return 1 - q
            blk0 = k - (k % env.block)
            pmb = pm(range(blk0, k))
            pme = pm(range(0, k))
            jblk.append(0.5 + 0.5 * pa * pmb)
            jepi.append(0.5 + 0.5 * pa * pme)
            cblk.append(0.5 + 0.25 * pa * pmb)
        # end trials
    out = {"lc": float(np.mean(lc)), "n_trials": len(lc)}
    if fam == "FLIP":
        out.update(joint=float(np.mean(jepi)), joint_episode=float(np.mean(jepi)),
                   joint_block=float(np.mean(jblk)), copy_block=float(np.mean(cblk)))
    else:
        out["joint"] = float(np.mean(joint))
    return out
