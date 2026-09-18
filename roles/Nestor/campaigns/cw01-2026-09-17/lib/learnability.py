"""The learnability gate: prove the effect COULD be found, before spending budget.

Why this exists. Across the first three experiments, the single most common failure
was not a wrong result -- it was an instrument that could not have shown the effect
even if it existed:

  e01 D009  the measured mechanism never fired (re_entries = 0 for a whole run)
  e01 D010  arms were never matched; a seed artifact read as a +40% advantage
  e02 D019  a capability flag desynchronised the arms' random streams
  e02 D025  the gain detector was blind exactly where all the improvement was
  e03 D029  the world's latent facts were redrawn every episode, so the phenomenon
            was unlearnable IN PRINCIPLE

Five defects, three experiments, one shape. Each was caught only because I happened
to look. Q10 -- promoted from D010 into an executable gate -- caught D019 in brand
new code within the hour, which is the campaign's clearest evidence that gates
transfer and memos do not. So this is a gate, not a note.

The contract: before EXECUTE, hand-build a COMPETENT organism and an INCOMPETENT
one, and prove that (a) they differ, (b) the competent one wins by a real margin,
and (c) the mechanism actually fires in the competent case. If a hand-built best
case cannot achieve the effect, evolution will not either, and any NULL the
experiment returns is about the instrument rather than the world.
"""
from __future__ import annotations

import numpy as np


class NotLearnable(AssertionError):
    """Raised when a hand-built best case cannot achieve the effect."""


def assert_distinct(probes):
    """Probe suites must not silently contain duplicates (CW01-D023).

    In e02 two 'different' probe genomes were identical because one was built by
    copying the other and re-setting a gene it already had. The comparison then
    tested a genome against itself and produced a spurious FAIL.
    """
    keys = list(probes)
    dupes = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if _signature(probes[a]) == _signature(probes[b]):
                dupes.append((a, b))
    return {"distinct": not dupes, "duplicates": dupes, "n": len(keys)}


def _signature(g):
    if isinstance(g, dict):
        return tuple(sorted((k, _signature(v)) for k, v in g.items()))
    if isinstance(g, np.ndarray):
        return ("nd", g.shape, float(np.sum(g)), float(np.sum(np.abs(g))))
    return g


def probe(probes, evaluate, best, worst, mechanism_key=None,
          min_advantage_pct=5.0, min_mechanism=0.0, n=24):
    """Run every probe, check distinctness, advantage, and that the mechanism fires.

    probes          name -> organism
    evaluate        organism -> dict of mean metrics (caller supplies the world)
    best, worst     names that must be separated by min_advantage_pct
    mechanism_key   metric that must exceed min_mechanism in `best`

    Returns a verdict dict. `learnable` false means: do not spend budget.
    """
    dist = assert_distinct(probes)
    results = {name: evaluate(g) for name, g in probes.items()}

    b = results[best].get("score", 0.0)
    w = results[worst].get("score", 0.0)
    adv = 100.0 * (b - w) / w if w else float("inf")

    mech_ok, mech_val = True, None
    if mechanism_key is not None:
        mech_val = results[best].get(mechanism_key)
        mech_ok = (mech_val is not None) and (mech_val > min_mechanism)

    learnable = bool(dist["distinct"] and adv >= min_advantage_pct and mech_ok)
    return {
        "learnable": learnable,
        "distinct": dist,
        "results": results,
        "best": best, "worst": worst,
        "advantage_pct": adv, "min_advantage_pct": min_advantage_pct,
        "mechanism_key": mechanism_key, "mechanism_value": mech_val,
        "min_mechanism": min_mechanism, "mechanism_fires": mech_ok,
        "verdict": ("LEARNABLE" if learnable else "NOT LEARNABLE - do not spend budget"),
        "_reading": "a NULL from an experiment that fails this gate is a statement about the "
                    "instrument, not about the world",
    }


def require(verdict):
    """Fail closed. EXECUTE must not proceed on an unlearnable world."""
    if not verdict.get("learnable"):
        raise NotLearnable(verdict.get("verdict", "not learnable"))
    return verdict


class VacuousCheck(AssertionError):
    """Raised when a comparison would pass because nothing happened."""


def assert_live(metrics, required, label=""):
    """A comparison is only meaningful if the thing being compared actually occurred.

    This family keeps recurring across the campaign:
      e01  close_sweep recorded {checks_run: 0, ok: true} -- a pass over no checks
      e01  Q4 'passed' by comparing three EMPTY strings from crashed subprocesses
      e04  Q10 'passed' with info=0.0 on both arms: two arms agreeing that the world
           was empty, which is no evidence they are matched

    So identity and equality checks must be gated on liveness. `required` names the
    metrics that must be non-zero for the comparison to mean anything -- e.g.
    ("info", "placements") for a channel arm, ("ordered",) for an ordering claim.

    Returns a verdict dict; `live` false means the check proves nothing.
    """
    dead = [k for k in required
            if k not in metrics or metrics[k] == 0 or metrics[k] is False]
    return {"live": not dead, "dead_metrics": dead, "label": label,
            "checked": {k: metrics.get(k) for k in required},
            "verdict": ("LIVE" if not dead
                        else "VACUOUS - these were zero: %s" % dead)}


def require_live(metrics, required, label=""):
    """Fail closed on a vacuous comparison rather than recording a hollow PASS."""
    v = assert_live(metrics, required, label)
    if not v["live"]:
        raise VacuousCheck("%s %s" % (label, v["verdict"]))
    return v
