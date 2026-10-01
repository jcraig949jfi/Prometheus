"""W2-B: C1/C1b rulers re-expressed as attain.Ruler measures (CPU, eager), plus proposed rulers.
Each measure mirrors the executable semantics it names (file:line in the docstring); none edits frozen code."""
from __future__ import annotations

import numpy as np

from prometheus.ananke import assays, envs
from prometheus.ananke.engine import Controls, World

from attain import Ruler
from rulers_extra import per_sensor_pivotality


def _run(ph, env, g, seeds, ctrl=None, sched_fn=None):
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    if sched_fn is not None:
        sched_fn(ep)
    w = World(ph, np.repeat(g[None], M, 0), [seeds[m - (m % 2)] for m in range(M)], device="cpu",
              ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    return envs.score(ep, tr).reshape(M // 2, 2).mean(-1), ep, tr


def m_signal(ph, env, g, seeds, sched_fn=None):
    """campaign.classify SIGNAL: held lo99 > .55 (campaign.py:430, search.py:133)."""
    pairs, _, _ = _run(ph, env, g, seeds, sched_fn=sched_fn)
    m, lo, hi = assays.pair_ci(pairs)
    return {"value": float(lo), "passed": bool(lo > 0.55), "pairs": pairs}


def m_zero_comm(ph, env, g, seeds, sched_fn=None):
    """The zero_comm control's accuracy (search.py:129); 'passed' = the control shows dependence
    (zero_comm pair mean <= .55, causal_label campaign.py:457)."""
    pairs, _, _ = _run(ph, env, g, seeds, ctrl=Controls(zero_comm=True), sched_fn=sched_fn)
    return {"value": float(pairs.mean()), "passed": bool(pairs.mean() <= 0.55), "pairs": pairs}


def m_comm_dependent(ph, env, g, seeds, sched_fn=None):
    """COMM_DEPENDENT: SIGNAL and lo99(held - zero_comm) > .03 (campaign.py:431-433)."""
    a, _, _ = _run(ph, env, g, seeds, sched_fn=sched_fn)
    z, _, _ = _run(ph, env, g, seeds, ctrl=Controls(zero_comm=True), sched_fn=sched_fn)
    _, lo, _ = assays.pair_ci(a)
    _, dlo, _ = assays.pair_ci(a - z)
    return {"value": float(dlo), "passed": bool(lo > 0.55 and dlo > 0.03)}


def m_integration_maj(ph, env, g, seeds, sched_fn=None):
    """INTEGRATION_BEYOND_ONE_SENSOR: MAJ lo99 > .70 (campaign.py:437)."""
    pairs, _, _ = _run(ph, env, g, seeds, sched_fn=sched_fn)
    _, lo, _ = assays.pair_ci(pairs)
    return {"value": float(lo), "passed": bool(lo > 0.70)}


def m_beyond_hop(key):
    def f(ph, env, g, seeds, sched_fn=None):
        """REACH_BEYOND_HOP: twin_assay beyond_hop >= .5 (campaign.py:439; assays.py:233-302)."""
        assert sched_fn is None, "twin_assay builds its own schedule"
        tw = assays.twin_assay(ph, g[None], env, seeds[:16], device="cpu")
        v = float(tw[key][0])
        return {"value": v, "passed": bool(v >= 0.5)}
    return f


def m_env_perm_ok(ph, env, g, seeds, sched_fn=None):
    """CAUSAL_SUPPORT's env-permutation clause: mean over pair rotations in [.40, .60]
    (assays.py:214-228, campaign.py:447). 'passed' = the clause is satisfied."""
    ep = envs.build(ph, env, seeds)
    M = len(seeds)
    w = World(ph, np.repeat(g[None], M, 0), seeds, device="cpu", schedule=ep.schedule)   # raw seeds, as C1
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    vals = []
    for k in range(1, M // 2):
        perm = np.roll(np.arange(M), 2 * k)
        ep2 = envs.Episode(ep.schedule, ep.ro_tick, ep.ro_slot, ep.y[perm], ep.scored[perm], ep.meta)
        vals.append(float(envs.score(ep2, tr).mean()))
    v = float(np.mean(vals))
    return {"value": v, "passed": bool(0.40 <= v <= 0.60)}


def m_xor_pivot(margin=0.10, trials=(2, 5, 8)):
    def f(ph, env, g, seeds, sched_fn=None):
        """PROPOSED XOR ruler: SIGNAL and min_j pivotality_j > .5 + margin (rulers_extra)."""
        pairs, _, _ = _run(ph, env, g, seeds)
        _, lo, _ = assays.pair_ci(pairs)
        piv, _ = per_sensor_pivotality(ph, g, env, seeds, trials)
        v = min(piv.values())
        return {"value": float(v), "passed": bool(lo > 0.55 and v > 0.5 + margin)}
    return f


def m_flip_feedback(drop=0.10):
    def f(ph, env, g, seeds, sched_fn=None):
        """PROPOSED FLIP control: the champion must DROP when every teacher after trial 0 is removed:
        lo99(normal - ablated) > drop. 'passed' = feedback is used after trial 0."""
        Pd = env.period()

        def abl(ep):
            ep.schedule.sense_val[Pd:, :, 1] = 0
        a, _, _ = _run(ph, env, g, seeds)
        b, _, _ = _run(ph, env, g, seeds, sched_fn=abl)
        _, dlo, _ = assays.pair_ci(a - b)
        _, lo, _ = assays.pair_ci(a)
        return {"value": float(dlo), "passed": bool(lo > 0.55 and dlo > drop)}
    return f


SIGNAL = Ruler("SIGNAL", "competence on the family's task", m_signal)
ZERO_COMM = Ruler("zero_comm control", "communication is necessary", m_zero_comm)
COMM_DEPENDENT = Ruler("COMM_DEPENDENT", "competence depends on communication", m_comm_dependent)
INTEGRATION_MAJ = Ruler("INTEGRATION(MAJ)", "integrates more than one sensor", m_integration_maj)
REACH_BEYOND_HOP = Ruler("REACH_BEYOND_HOP", "a cue's influence travels beyond one hop", m_beyond_hop("beyond_hop"))
REACH_BEYOND_HOP_NEAREST = Ruler("REACH_BEYOND_HOP_NEAREST", "as above, from the nearest perturbed sensor",
                                 m_beyond_hop("beyond_hop_nearest"))
ENV_PERM_OK = Ruler("env_permutation clause", "the readout is not a target-free artefact", m_env_perm_ok)
XOR_PIVOT = Ruler("XOR_PIVOT (proposed)", "computes parity of the two inputs", m_xor_pivot())
FLIP_FEEDBACK = Ruler("FLIP_FEEDBACK (proposed)", "tracks the mapping from feedback", m_flip_feedback())
