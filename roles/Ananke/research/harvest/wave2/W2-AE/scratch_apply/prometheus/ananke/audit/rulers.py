"""C1/C1b rulers re-expressed as explib Ruler measures, plus the proposed competence-class rulers.

Each measure mirrors the executable semantics it names (file:line in the docstring as of W2-B) and edits no
frozen code. A measure is (ph, env, genome, seeds, sched_fn) -> {"value", "passed", optional "pairs"}; feed it
to prometheus.explib.attainable.certify_family (audit.certify wraps the common families).

Recorded C1 semantics (W2-B rulers_c1.py):
  SIGNAL, ZERO_COMM, COMM_DEPENDENT, INTEGRATION_MAJ, REACH_BEYOND_HOP (legacy), ENV_PERM_OK
Proposed (drafts; NOT frozen semantics; each needs its own power analysis before a prereg uses it):
  REACH_BEYOND_HOP_NEAREST  twin_assay from the nearest perturbed sensor (W2-B; assays key beyond_hop_nearest)
  XOR_PIVOT                 SIGNAL and min_j pivotality_j > .5 + margin (W2-B rulers_extra)
  XOR_SYM                   SIGNAL and conditional pivotality min_{j,s} p_j(other = s) > .5 * max_{j,s} p_j(s)
                            (W2-J pivot.py, REPORT s266; XOR_PIVOT has false negatives at partial reach because
                            parity pivotality scales like 2 acc - 1; the conditional symmetry does not)
  FLIP_FEEDBACK             SIGNAL and lo99(normal - teachers-removed-after-trial-0) > drop (W2-B)
  FLIP_B                    B = (same + changed-cue accuracy)/2, lo99 > .75 (W2-S; see audit.flip_b)

per_sensor_pivotality known answers (W2-B REPORT): XOR parity (1, 1); any non-parity 2-input readout
min_j p_j <= .5 (AND/OR types (.5, .5)); single-input (1, 0); 5-sensor majority with flip .3: .2646 each;
single-sensor MAJ reader (1, 0, 0, 0, 0). Under parity p_j(other=+) == p_j(other=-); under a NOR-type
readout one of them is ~0.
"""
from __future__ import annotations

import numpy as np

from prometheus.ananke import assays, envs
from prometheus.ananke.engine import Controls, Schedule, World
from prometheus.explib.attainable import Ruler

from . import flip_b, runner


def _run(ph, env, g, seeds, ctrl=None, sched_fn=None):
    pairs, _, ep, tr = runner.run(ph, g, env, seeds, ctrl=ctrl, sched_fn=sched_fn)
    return pairs, ep, tr


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


def m_beyond_hop(key: str = "beyond_hop", n_worlds: int = 16):
    def f(ph, env, g, seeds, sched_fn=None):
        """REACH_BEYOND_HOP: twin_assay beyond_hop >= .5 (campaign.py:439; assays.py:233-302)."""
        if sched_fn is not None:
            raise ValueError("twin_assay builds its own schedule; a world edit cannot be applied")
        tw = assays.twin_assay(ph, g[None], env, seeds[:n_worlds], device="cpu")
        v = float(tw[key][0])
        return {"value": v, "passed": bool(v >= 0.5)}
    return f


def m_env_perm_ok(ph, env, g, seeds, sched_fn=None):
    """CAUSAL_SUPPORT's env-permutation clause: mean over pair rotations in [.40, .60]
    (assays.py:214-228, campaign.py:447). 'passed' = the clause is satisfied. Raw seeds, as C1."""
    ep = envs.build(ph, env, seeds)
    M = len(seeds)
    w = World(ph, np.repeat(g[None], M, 0), seeds, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    vals = []
    for k in range(1, M // 2):
        perm = np.roll(np.arange(M), 2 * k)
        ep2 = envs.Episode(ep.schedule, ep.ro_tick, ep.ro_slot, ep.y[perm], ep.scored[perm], ep.meta)
        vals.append(float(envs.score(ep2, tr).mean()))
    v = float(np.mean(vals))
    return {"value": v, "passed": bool(0.40 <= v <= 0.60)}


def per_sensor_pivotality(ph, genome, env, seeds, trials, device: str = "cpu"):
    """Per-sensor cue-twin census: for sensor column j and trial k, a twin world equal to the normal one except
    that ONLY column j's cue in trial k is negated. p_j = P(decision sign(S0) at trial k's readout differs).
    -> ({j: p_j}, {j: [M, len(trials)] float indicator array})."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    K = ep.schedule.sense_idx.shape[1]
    Pd = env.period()
    cols = [j for j in range(K) if (ep.schedule.sense_val[:, :, j] != 0).any()]
    if env.family == "FLIP":
        cols = [0]                                     # column 1 is the teacher, not a cue
    arms = [(None, None)] + [(j, k) for j in cols for k in trials]
    n_arm = len(arms)
    sv = ep.schedule.sense_val.repeat(1, n_arm, 1).clone()
    for a, (j, k) in enumerate(arms):
        if j is None:
            continue
        t0 = k * Pd
        sv[t0:t0 + env.cue_len, a * M:(a + 1) * M, j] *= -1
    sch = Schedule(ep.schedule.sense_idx.repeat(n_arm, 1), sv, ep.schedule.read_idx.repeat(n_arm, 1))
    w = World(ph, np.repeat(genome[None], M * n_arm, 0), runner.mirrored(seeds) * n_arm, device=device,
              schedule=sch)
    T = int(ep.ro_tick[:, max(trials)].max()) + 1
    w.run(T, graph=False)
    tr = w.trace.cpu().numpy()[:, :, 0]
    base = np.sign(tr[:, :M])
    out = {}
    for a, (j, k) in enumerate(arms):
        if j is None:
            continue
        rt = ep.ro_tick[:, k]
        d = np.sign(tr[rt, np.arange(M) + a * M]) != base[rt, np.arange(M)]
        out.setdefault(j, []).append(d.astype(float))
    return {j: float(np.mean(v)) for j, v in out.items()}, {j: np.stack(v, 1) for j, v in out.items()}


def conditional_pivotality(ph, genome, env, seeds, trials, device: str = "cpu") -> dict:
    """W2-J: split sensor j's flip indicator by the OTHER sensor's cue sign in that trial (2-sensor families).
    -> {"pivot": {j: p_j}, "cond": {j: {"other+": p, "other-": p}}}."""
    piv, arr = per_sensor_pivotality(ph, genome, env, seeds, trials, device)
    if len(arr) != 2:
        raise ValueError("conditional pivotality needs exactly two cue columns")
    ep = envs.build(ph, env, seeds)
    Pd = env.period()
    cond = {}
    for j, a in arr.items():
        oth = 1 - j
        sg = np.stack([np.sign(ep.schedule.sense_val[k * Pd, :, oth].numpy()) for k in trials], 1)
        cond[j] = {"other+": float(a[sg > 0].mean()) if (sg > 0).any() else None,
                   "other-": float(a[sg < 0].mean()) if (sg < 0).any() else None}
    return {"pivot": piv, "cond": cond}


def m_xor_pivot(margin: float = 0.10, trials=(2, 5, 8)):
    def f(ph, env, g, seeds, sched_fn=None):
        """PROPOSED XOR ruler: SIGNAL and min_j pivotality_j > .5 + margin."""
        pairs, _, _ = _run(ph, env, g, seeds)
        _, lo, _ = assays.pair_ci(pairs)
        piv, _ = per_sensor_pivotality(ph, g, env, seeds, trials)
        v = min(piv.values())
        return {"value": float(v), "passed": bool(lo > 0.55 and v > 0.5 + margin)}
    return f


def m_xor_sym(ratio: float = 0.5, trials=(2, 5, 8)):
    def f(ph, env, g, seeds, sched_fn=None):
        """PROPOSED XOR ruler (W2-J): SIGNAL and min_{j,s} p_j(other=s) > ratio * max_{j,s} p_j(s). Value =
        min/max (0 when max = 0). Threshold and power are NOT fixed (C2 prereg draft s5.2)."""
        pairs, _, _ = _run(ph, env, g, seeds)
        _, lo, _ = assays.pair_ci(pairs)
        c = conditional_pivotality(ph, g, env, seeds, trials)["cond"]
        vals = [v for d in c.values() for v in d.values()]
        if any(v is None for v in vals):
            return {"value": float("nan"), "passed": False}
        mx = max(vals)
        v = min(vals) / mx if mx > 0 else 0.0
        return {"value": float(v), "passed": bool(lo > 0.55 and mx > 0 and min(vals) > ratio * mx)}
    return f


def m_flip_feedback(drop: float = 0.10):
    def f(ph, env, g, seeds, sched_fn=None):
        """PROPOSED FLIP control: lo99(normal - teachers-removed-after-trial-0) > drop, with SIGNAL.
        'passed' = feedback is used after trial 0."""
        Pd = env.period()

        def abl(ep):
            ep.schedule.sense_val[Pd:, :, 1] = 0
        a, _, _ = _run(ph, env, g, seeds)
        b, _, _ = _run(ph, env, g, seeds, sched_fn=abl)
        _, dlo, _ = assays.pair_ci(a - b)
        _, lo, _ = assays.pair_ci(a)
        return {"value": float(dlo), "passed": bool(lo > 0.55 and dlo > drop)}
    return f


def m_flip_b(bar: float = flip_b.B_BAR):
    def f(ph, env, g, seeds, sched_fn=None):
        """PROPOSED FLIP inference certificate (W2-S): B lo99 > .75. Undefined B never passes."""
        if sched_fn is not None:
            raise ValueError("FLIP_B evaluates the unedited schedule")
        o = flip_b.flip_eval(ph, g, env, seeds)
        lo = o.get("bal_lo99", float("nan"))
        return {"value": float(lo), "passed": bool(lo > bar)}
    return f


SIGNAL = Ruler("SIGNAL", "competence on the family's task", m_signal)
ZERO_COMM = Ruler("zero_comm control", "communication is necessary", m_zero_comm)
COMM_DEPENDENT = Ruler("COMM_DEPENDENT", "competence depends on communication", m_comm_dependent)
INTEGRATION_MAJ = Ruler("INTEGRATION(MAJ)", "integrates more than one sensor", m_integration_maj)
REACH_BEYOND_HOP = Ruler("REACH_BEYOND_HOP", "a cue's influence travels beyond one hop", m_beyond_hop("beyond_hop"))
REACH_BEYOND_HOP_NEAREST = Ruler("REACH_BEYOND_HOP_NEAREST", "as above, from the nearest perturbed sensor",
                                 m_beyond_hop("beyond_hop_nearest"))
REACH_NEAREST = REACH_BEYOND_HOP_NEAREST
ENV_PERM_OK = Ruler("env_permutation clause", "the readout is not a target-free artefact", m_env_perm_ok)
XOR_PIVOT = Ruler("XOR_PIVOT (proposed)", "computes parity of the two inputs", m_xor_pivot())
XOR_SYM = Ruler("XOR_SYM (proposed)", "computes parity of the two inputs (conditional symmetry)", m_xor_sym())
FLIP_FEEDBACK = Ruler("FLIP_FEEDBACK (proposed)", "tracks the mapping from feedback", m_flip_feedback())
FLIP_B = Ruler("FLIP_B (proposed)", "infers the mapping (beats every copy-class policy)", m_flip_b())

RECORDED = (SIGNAL, ZERO_COMM, COMM_DEPENDENT, INTEGRATION_MAJ, REACH_BEYOND_HOP, ENV_PERM_OK)
PROPOSED = (REACH_BEYOND_HOP_NEAREST, XOR_PIVOT, XOR_SYM, FLIP_FEEDBACK, FLIP_B)
