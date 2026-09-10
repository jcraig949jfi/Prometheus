"""`ca_density_v0` -- a thin wrapper around Herakles's EvCA library.

The library is `herakles/evca/` (WP-C1, `3466481b9`). Vivarium OWNS the kind
contract; Herakles owns the semantics. Nothing in this file decides anything
about cellular automata: every convention is taken from `core.py`, and where
the library refuses, this refuses with it.

CONVENTIONS TAKEN, NOT MADE (addendum correction 1)
  The rule-table encoding is `core.decode_table`: 32 hex digits, 128 bits,
  bit k counting from the LEFT is the output for neighbourhood index k. The
  neighbourhood bit order (i-3 the most significant) and the periodic boundary
  come from the same module. This wrapper never parses a rule itself -- it
  passes `rule_hex` to `decode_table` and uses what comes back. Radius is
  passed to `core.require_radius`, which implements r=3 only and refuses
  anything else; the refusal is the library's and is not softened here.

BOTH SUCCESS MASKS (addendum correction 2)
  at_T     the lattice IS in the correct uniform configuration after `steps`
           updates. This is exactly `core.classify`.
  stable   it is in that configuration AND one further update leaves it
           there. MEASURED by taking one more step, not inferred.

  The two coincide precisely when the relevant uniform configuration is a
  fixed point of the rule, which is decided by table entries 0 and 127 --
  `core.fixes_uniform_states`. Both per-rule facts are reported, both
  accuracies are reported, and `accuracy` is the one the payload's declared
  `success_criterion` names. A caller who never looks at the other still
  cannot be misled about which question was answered, because the criterion
  is echoed in the result.

  The at_T mask is recomputed here to derive `stable`, and its digest is
  checked against the digest `core.classify` returns. A disagreement raises:
  a wrapper that has quietly drifted from its library must not report a
  number.

INITIAL CONDITIONS
  `ic_density_set` is an ordered list. `null` is the UNBIASED ensemble
  (`core.make_ics(density=None)`, each cell iid uniform) -- the ensemble the
  published figures are defined over. A float is iid Bernoulli(density),
  which the library states is a DIFFERENT ensemble and not comparable with
  published numbers; that warning is the library's and is repeated here
  rather than paraphrased away.

  `n_ic` is ICs PER DENSITY. The blocks are concatenated in declared order,
  so witness indices are global across the whole ensemble and unambiguous.
  Block j is seeded `seed + j`, so a single-element set uses the run's seed
  unchanged and reproduces the library called directly.

STATELESS ACROSS EXECUTIONS. The lattice state lives inside one execution;
nothing carries between repeats. `stateful=False`, so `repeat.state=persist`
is refused for this kind, as it is for every stateless one.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent

#: Closed. `at_T` and `stable` are the two masks the library's own docstring
#: distinguishes; no third reading is invented here.
SUCCESS_CRITERIA = ("at_T", "stable")

#: Matches core.WITNESS_LIMIT. Declared here too so the result schema's vector
#: bound and the library's truncation point are the same number.
WITNESS_LIMIT = 64


class CaLibraryUnavailable(RuntimeError):
    """herakles.evca is not importable on this host."""


def _evca():
    """Import the library, or say exactly what is missing.

    Vivarium does not vendor a copy: a second implementation of a pinned
    convention is the drift this wrapper exists to avoid."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    try:
        from herakles import evca                      # noqa: PLC0415
        from herakles.evca import core                 # noqa: PLC0415
    except Exception as exc:                           # noqa: BLE001
        raise CaLibraryUnavailable(
            "ca_density_v0 needs Herakles's herakles/evca library (WP-C1, "
            "3466481b9). Refusing to reimplement its pinned conventions: %s"
            % exc) from exc
    return evca, core


def _require_density_set(value, core):
    if not isinstance(value, list) or not value:
        raise core.EvcaError(
            "ic_density_set must be a non-empty list; use [null] for the "
            "unbiased ensemble the published figures are defined over")
    out = []
    for d in value:
        if d is None:
            out.append(None)
            continue
        if isinstance(d, bool) or not isinstance(d, (int, float)):
            raise core.EvcaError(
                "ic_density_set entries must be null or a number, got %r" % (d,))
        out.append(core.require_density(float(d)))
    return out


def run(payload: dict, *, seed: int) -> dict:
    """Execute one CA density-classification measurement.

    `payload` is the kind's declared parameters, already contract-checked by
    `viv.kinds`. `seed` is the REPEAT's derived seed, so repeats of one world
    draw different initial conditions under a varying seed_derivation and the
    same ones under `constant`.
    """
    import numpy as np

    evca, core = _evca()

    rule_hex = payload["rule_hex"]
    radius = payload["radius"]
    n_cells = payload["n_cells"]
    steps = payload["steps"]
    n_ic = payload["n_ic"]
    criterion = payload["success_criterion"]
    if criterion not in SUCCESS_CRITERIA:
        raise core.EvcaError(
            "success_criterion must be one of %s, got %r; `accuracy` is scored "
            "under it and the choice is the requester's"
            % (list(SUCCESS_CRITERIA), criterion))

    core.require_radius(radius)          # r=3 only; the library's refusal
    core.require_lattice(n_cells)        # odd, so majority never ties
    core.require_steps(steps)
    densities = _require_density_set(payload["ic_density_set"], core)
    if not isinstance(n_ic, int) or isinstance(n_ic, bool) or n_ic < 1:
        raise core.EvcaError("n_ic must be a positive integer, got %r" % (n_ic,))

    table = core.decode_table(rule_hex)  # the encoding is the library's

    # One block per declared density, concatenated in order, so a witness
    # index means one thing across the whole ensemble.
    blocks = [core.make_ics(n_ic, n_cells, int(seed) + j, density=d)
              for j, d in enumerate(densities)]
    ics = np.concatenate(blocks, axis=0) if len(blocks) > 1 else blocks[0]

    # The library's own measurement: at_T.
    at_t = core.classify(table, ics, steps, witness_limit=WITNESS_LIMIT)

    # Recompute the at_T mask so `stable` can be derived, and CHECK it against
    # the library's digest. If these disagree the wrapper has drifted and must
    # not report a number.
    target = core.majority_target(ics)
    final = core.evolve(ics, table, steps)
    ones = final.sum(axis=1)
    correct_at_t = np.where(target == 1, ones == n_cells, ones == 0)
    if core.mask_digest(correct_at_t) != at_t["correct_mask_digest"]:
        raise core.EvcaError(
            "the wrapper's recomputed at_T mask disagrees with "
            "core.classify's; refusing to report a number from a wrapper that "
            "has drifted from its library")

    # stable: correct at T AND one further update leaves the lattice there.
    # Measured, not inferred from the fixed-point bits.
    after = core.step(final, table)
    unchanged = (after == final).all(axis=1)
    correct_stable = correct_at_t & unchanged

    fixed = core.fixes_uniform_states(table)
    chosen = correct_at_t if criterion == "at_T" else correct_stable
    wrong = np.flatnonzero(~chosen)
    witness = [int(i) for i in wrong[:WITNESS_LIMIT].tolist()]
    truncated = bool(wrong.size > WITNESS_LIMIT)

    # One fully declared space-time diagram for this rule and lattice: the
    # family's raster and its replay check. ic_index 0 of the FIRST block, so
    # it is a diagram of an initial condition this run actually used.
    traj = core.selected_trajectory(rule_hex, n_cells, steps, int(seed),
                                    ic_index=0)

    out = {
        "accuracy": float(chosen.mean()),
        "misclassified_ic": witness,
        "spacetime_digest": traj["digest"],
        "success_criterion": criterion,
        "accuracy_at_T": float(at_t["accuracy"]),
        "accuracy_stable": float(correct_stable.mean()),
        "n_incorrect_at_T": int(at_t["n_incorrect"]),
        "n_incorrect_stable": int((~correct_stable).sum()),
        "mask_digest_at_T": at_t["correct_mask_digest"],
        "mask_digest_stable": core.mask_digest(correct_stable),
        "all_zeros_fixed": bool(fixed["all_zeros_fixed"]),
        "all_ones_fixed": bool(fixed["all_ones_fixed"]),
        "criteria_agree": bool((correct_at_t == correct_stable).all()),
        "n_ic_total": int(ics.shape[0]),
        "n_cells": int(n_cells),
        "steps": int(steps),
        "witness_truncated": truncated,
        "executor": "ca_density_v0",
        "reproducibility": "BIT_DETERMINISTIC",
    }
    if truncated:
        out["_truncated"] = {"misclassified_ic": True}
    return out
