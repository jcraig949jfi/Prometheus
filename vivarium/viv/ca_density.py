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
#: distinguishes. `cellwise_majority_match` is Herakles's third, added
#: 2026-09-10, and it is HIS definition and his analytic expectations -- see
#: core.cellwise_majority_match. Nothing here invents a reading.
#:
#: WHY A THIRD ONE EXISTS. Under both masks, 40 of 40 random tables in cs-c3-2
#: scored exactly 0.0 with 100/100 ICs incorrect. A criterion whose attainable
#: range for random rules is a single point cannot rank anything, and cannot
#: tell a rule that is slightly better than chance from one that is not. The
#: per-cell measure has an interval around 0.5 instead.
#:
#: IT IS NOT A DROP-IN REPLACEMENT AND MUST NOT BE READ AS ONE. It equals at_T
#: accuracy only for a rule that always reaches a uniform configuration by
#: `steps`, and Herakles is explicit that the two CONSTANT rules land on the
#: same mean as a random table and are separated only by dispersion. So a
#: ranking built on the mean alone inherits that blind spot; the dispersion
#: travels in the result for exactly that reason.
SUCCESS_CRITERIA = ("at_T", "stable", "cellwise_majority_match")

#: The two mask criteria. `accuracy` under the third is a MEAN over cells, not
#: a fraction of ICs, so the mask-shaped fields below do not apply to it and
#: are reported as what they are rather than coerced.
MASK_CRITERIA = ("at_T", "stable")

#: The four EXACT symmetries of the density task (Track B, packet v2.1 2.1).
#: Applied inside the executor to three things together -- the rule table, the
#: REALISED IC sample, and the majority target that follows from it -- because
#: applying them to fewer than all three is a different experiment.
TRANSFORMS = ("none", "reflect", "complement", "reflect_complement")

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


def _reflect_table(table, np):
    """T'[k] = T[reverse7(k)]. The spatial mirror of a radius-3 rule.

    WHY THIS IS THE MIRROR AND NOT A GUESS. The library pins the neighbourhood
    order: offset -3 occupies bit 6 and offset +3 occupies bit 0
    (`core.neighbourhood_index`). Mirroring the lattice therefore reverses the
    seven bits of every neighbourhood index, and the rule that reproduces the
    mirrored dynamics is the one whose entries are permuted by that reversal.
    Nothing here decides a convention -- the reversal is READ OFF the order
    core.py already declares, and the test asserts the commutation
    step(reverse(s), T') == reverse(step(s, T)) over random lattices rather
    than trusting this paragraph.
    """
    width = 7
    perm = np.empty(table.shape[0], dtype=np.int64)
    for k in range(table.shape[0]):
        r = 0
        for j in range(width):
            if (k >> j) & 1:
                r |= 1 << (width - 1 - j)
        perm[k] = r
    return table[perm]


def _complement_table(table, np):
    """T'[k] = 1 - T[~k]. Exchanging 0 and 1 everywhere.

    The index complement is 127 - k (all seven bits flipped) and the OUTPUT is
    complemented too; doing only one of the two would not be a symmetry of
    anything.
    """
    n = table.shape[0]
    idx = (n - 1) - np.arange(n)
    return (1 - table[idx]).astype(table.dtype)


def apply_transform(name, table, ics, np):
    """Return (table', ics') under one declared symmetry. The majority target
    is NOT returned: it is recomputed from ics' by the library, which is the
    only way it stays consistent with the sample that was actually run."""
    if name == "none":
        return table, ics
    if name == "reflect":
        return _reflect_table(table, np), ics[:, ::-1].copy()
    if name == "complement":
        return _complement_table(table, np), (1 - ics).astype(ics.dtype)
    if name == "reflect_complement":
        t, s = _reflect_table(table, np), ics[:, ::-1].copy()
        return _complement_table(t, np), (1 - s).astype(s.dtype)
    raise ValueError("unknown transform %r" % (name,))


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
    transform = payload["transform"]
    if transform not in TRANSFORMS:
        raise core.EvcaError(
            "transform must be one of %s, got %r; these are the four EXACT "
            "symmetries of the density task, so a transformed arm is a NULL "
            "arm -- accuracy that moves under one is a defect, not a result"
            % (list(TRANSFORMS), transform))
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

    # THE TRANSFORM IS APPLIED TO THE REALISED SAMPLE, not by re-drawing under
    # a different seed. That is what makes a transformed arm the exact IMAGE of
    # its untransformed twin rather than an independent run that happens to be
    # related -- and it is the whole reason the arm can serve as an exact null.
    # The majority target is recomputed downstream from these ICs by the
    # library, so it follows the transform automatically and cannot drift from
    # the sample it describes.
    ics_raw = ics
    table, ics = apply_transform(transform, table, ics, np)
    # F-20. The two facts Herakles's c3_null_check needs and cannot infer.
    # Both are MEASURED from the arrays rather than declared from the
    # transform name: a wrapper that answered these from a lookup table would
    # be asserting that it applied the transform correctly, which is the very
    # thing the null check exists to verify independently.
    ic_transformed = bool(not np.array_equal(ics, ics_raw))
    target_before = core.majority_target(ics_raw)
    target_after = core.majority_target(ics)
    majority_target_flipped = bool(np.array_equal(target_after,
                                                  1 - target_before))
    transformed_rule_hex = (rule_hex if transform == "none"
                            else core.encode_table(table))

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

    # THE THIRD CRITERION. Its accuracy is a per-cell mean and its "witness"
    # is not a set of failed ICs -- there is no pass/fail per IC to collect.
    # Rather than coerce it into a mask shape it does not have, the mask-keyed
    # fields report the at_T mask (unchanged, still true of the run) and the
    # result says which reading `accuracy` came from.
    cellwise = None
    if criterion == "cellwise_majority_match":
        cellwise = core.cellwise_majority_match(table, ics, steps)

    chosen = correct_at_t if criterion in ("at_T", "cellwise_majority_match") \
        else correct_stable
    wrong = np.flatnonzero(~chosen)
    witness = [int(i) for i in wrong[:WITNESS_LIMIT].tolist()]
    truncated = bool(wrong.size > WITNESS_LIMIT)

    # One fully declared space-time diagram for this rule and lattice: the
    # family's raster and its replay check. ic_index 0 of the FIRST block, so
    # it is a diagram of an initial condition this run actually used.
    # The diagram is of the rule ACTUALLY RUN. Under a transform that is the
    # transformed rule, on the library's own declared IC draw for this seed --
    # so it is a faithful diagram of what ran, and it is NOT the image of the
    # untransformed run's diagram (the library re-draws its own IC and does not
    # see the transform). `spacetime_is_image_of_untransformed` says so rather
    # than leaving a reader to assume the two are related.
    traj = core.selected_trajectory(transformed_rule_hex, n_cells, steps,
                                    int(seed), ic_index=0)

    out = {
        "accuracy": (float(cellwise["mean_cell_match"]) if cellwise is not None
                     else float(chosen.mean())),
        "misclassified_ic": witness,
        # F-20. The SAME rule `accuracy` already follows, applied to the two
        # fields a symmetry check actually compares: under the declared
        # criterion, this is THE mask and THIS is the witness. The per-criterion
        # names below stay, so nothing is renamed and both readings remain
        # available -- but a consumer should not have to reconstruct which of
        # two digests the row was scored under before it can compare anything.
        "mask_digest": (at_t["correct_mask_digest"] if criterion == "at_T"
                        else core.mask_digest(correct_stable)),
        "witness": witness,
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
        # Present on every row so a reader never has to infer which shape
        # `accuracy` has from the criterion string.
        "accuracy_is_per_cell_mean": criterion == "cellwise_majority_match",
        "transform": transform,
        "transformed_rule_hex": transformed_rule_hex,
        # MEASURED, not declared. Under `reflect` on a palindromic sample
        # ic_transformed can legitimately be false, and saying so is the
        # honest reading -- the null check then reports a scope fact rather
        # than a break, which is what it is for.
        "ic_transformed": ic_transformed,
        "majority_target_flipped": majority_target_flipped,
        "spacetime_is_image_of_untransformed": transform == "none",
        "executor": "ca_density_v0",
        "reproducibility": "BIT_DETERMINISTIC",
    }
    if cellwise is not None:
        # Herakles's own fields, carried through unchanged and under his names.
        # The dispersion is NOT optional: he states that the two constant rules
        # land on the same MEAN as a random table and are told apart only by
        # it, so a row that reported the mean alone would hide the one thing
        # that makes the mean usable.
        for key in ("sd_across_ics", "min_cell_match", "max_cell_match",
                    "fraction_all_cells_match", "fraction_no_cells_match"):
            out["cellwise_" + key] = float(cellwise[key])
        out["cellwise_comparable_to_published_P"] = bool(
            cellwise["comparable_to_published_P"])
    if truncated:
        out["_truncated"] = {"misclassified_ic": True, "witness": True}
    return out
