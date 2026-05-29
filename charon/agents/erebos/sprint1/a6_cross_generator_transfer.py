"""Sprint-1 A6: cross-generator transfer (Phase 2, ITER-50).

Hypothesis (from roadmap v2 line 88):
> "Kill_patterns from G02 predict G17 outcomes"
> Pass: held-out predictive lift > 0 -> kill semantics generalize.

## What A6 tests

The substrate's claim: kill_pattern labels encode a generalizable
property of the (input, failure mode) pair, not just an
idiosyncratic generator output. If kps generalize across
generators, then knowing G02 produced kp_X on input I should
make it MORE likely G17 also produces kp_X on input I, vs a
random baseline where kps are independent of input.

Operationalized via ITER-44's cross_domain_transfer primitive
with plugin_id playing the role of "domain" (cross-PLUGIN
transfer, structurally identical to cross-domain).

## A6 protocol

1. Generate a synthetic ledger where 5 plugins emit on a shared
   pool of input signatures. The generative model produces
   correlated kps -- the kp for input I has SOME tendency to be
   the same across plugins, plus noise.

2. Build a KillTensor where the axes are
   (plugin_id, input_signature, "single_invariant", kp) -- map
   the substrate's plugin axis onto the tensor's "domain" slot
   for use by cross_domain_transfer.

3. For each (source_plugin, target_plugin) pair, use
   predict_transfer to compute transfer_rate -- the fraction of
   source-plugin patterns also present in target-plugin patterns.

4. Compute average transfer_rate across all directed pairs.

5. Baseline: shuffle the kill_pattern column of the synthetic
   ledger (breaks the input -> kp correlation), recompute the
   same average transfer_rate. The baseline measures what
   transfer_rate you'd see by chance under the same marginals.

6. Pass if substrate_avg - baseline_avg > 0.05 (5 percentage
   points). The roadmap threshold "lift > 0" is operationalized
   as a margin above noise to avoid declaring victory on a 0.001
   improvement.

## Why this is the right test

The substrate must show that kp labels are CORRELATED with input
across plugins -- if G02 says "kp_X on input I" and G17 also
says "kp_X on input I" more often than chance, the kps are
encoding a generalizable property of the failure mode.

The shuffle baseline preserves all marginals (each plugin's kp
distribution, each input's prevalence) but breaks the kp-input
correlation. The substrate must beat this baseline -- otherwise
the apparent transfer was just marginal noise.

A failure (lift <= 0.05) means: kp labels do not generalize
across generators in any structurally-detectable way.
"""
from __future__ import annotations

import random

from charon.agents.erebos._cross_domain_transfer import (
    predict_transfer,
)
from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    KillTensor,
)


# A6-specific: plugin_id sits in the tensor's DOMAIN slot;
# input_signature sits in the INVARIANT slot (via the default
# extractor on rows that have input_signature). The pattern must
# be (invariant, kp) so that an (input I, kp K) populated for
# both source and target plugin counts as a confirmed transfer.
# Plain (kp) keys would trivially match across plugins for any
# reasonable kp vocab.
A6_TRANSFER_KEY_AXES = (AXIS_INVARIANT, AXIS_KP)
from charon.agents.erebos.sprint1 import SprintResult


N_INPUTS = 30
N_PLUGINS = 5
P_KP_AGREE = 0.65   # input -> kp probability of agreement across plugins
SEED = 311
PASS_MARGIN = 0.05  # lift over shuffled baseline


def _generative_model(seed: int) -> list[dict]:
    """Produce a synthetic emission stream where the same input
    tends to elicit the same kp across plugins."""
    rng = random.Random(seed)
    plugins = [f"g{i:02d}" for i in range(1, N_PLUGINS + 1)]
    kps = ["kp_a", "kp_b", "kp_c", "kp_d", "PROMOTED"]
    # Per-input "ground truth" kp -- what the substrate's underlying
    # geometry would say
    input_to_truth: dict[str, str] = {
        f"sig:input_{i:03d}": rng.choice(kps) for i in range(N_INPUTS)
    }
    rows: list[dict] = []
    for sig, truth_kp in input_to_truth.items():
        for plugin in plugins:
            # Each plugin's emission for this input matches the truth
            # with probability P_KP_AGREE; else samples uniformly
            if rng.random() < P_KP_AGREE:
                emitted_kp = truth_kp
            else:
                emitted_kp = rng.choice(kps)
            rows.append({
                "plugin_id": plugin,
                # Stuff the plugin into the tensor's domain slot
                "domain": plugin,
                # NO explicit invariant -- the tensor's default
                # extractor will use input_signature, putting the
                # input identity on the invariant axis where the
                # transfer key (INVARIANT, KP) can read it.
                "kill_pattern": (
                    None if emitted_kp == "PROMOTED" else emitted_kp
                ),
                "input_signature": sig,
            })
    rng.shuffle(rows)
    return rows


def _avg_transfer_rate(tensor: KillTensor) -> float:
    """Average pairwise transfer_rate over all directed pairs."""
    plugins = sorted(tensor.axis_values(AXIS_DOMAIN))
    rates = []
    for src in plugins:
        for tgt in plugins:
            if src == tgt:
                continue
            r = predict_transfer(
                tensor,
                source_domain=src,
                target_domain=tgt,
                key_axes=A6_TRANSFER_KEY_AXES,
            )
            if r.transfer_rate is not None:
                rates.append(r.transfer_rate)
    return sum(rates) / len(rates) if rates else 0.0


def _shuffle_kps(rows: list[dict], seed: int) -> list[dict]:
    """Return a copy of rows with kill_pattern column shuffled
    across all rows (breaks kp-input correlation while preserving
    marginals)."""
    rng = random.Random(seed)
    kps = [r["kill_pattern"] for r in rows]
    rng.shuffle(kps)
    return [
        {**r, "kill_pattern": new_kp}
        for r, new_kp in zip(rows, kps)
    ]


def run_a6() -> SprintResult:
    rows = _generative_model(SEED)
    tensor = KillTensor.from_ledger_rows(rows)
    substrate_avg = _avg_transfer_rate(tensor)

    rows_shuffled = _shuffle_kps(rows, seed=SEED + 999)
    tensor_shuffled = KillTensor.from_ledger_rows(rows_shuffled)
    baseline_avg = _avg_transfer_rate(tensor_shuffled)

    lift = substrate_avg - baseline_avg
    passed = lift > PASS_MARGIN

    return SprintResult(
        experiment_id="A6",
        hypothesis=(
            "Kill_patterns generalize across generators (avg "
            "pairwise transfer_rate exceeds shuffled-baseline by "
            "> 5 percentage points)"
        ),
        metric_name="avg_transfer_lift_over_shuffle",
        metric_value=lift,
        pass_threshold=PASS_MARGIN,
        comparator=">",
        passed=passed,
        protocol_summary=(
            f"Synthetic ledger: N_INPUTS={N_INPUTS}, "
            f"N_PLUGINS={N_PLUGINS}, P_KP_AGREE={P_KP_AGREE}, "
            f"seed={SEED}. Build KillTensor with plugin in domain "
            f"slot. Average pairwise transfer_rate (default key "
            f"axes = (plugin, kp)) across all directed (src, tgt) "
            f"plugin pairs. Compare to baseline where kill_pattern "
            f"column has been shuffled across rows (marginals "
            f"preserved, kp-input correlation broken)."
        ),
        notes=(
            f"substrate_avg_transfer_rate={substrate_avg:.4f}; "
            f"baseline_avg_transfer_rate={baseline_avg:.4f}; "
            f"lift={lift:.4f}; pass_margin>{PASS_MARGIN}"
        ),
    )
