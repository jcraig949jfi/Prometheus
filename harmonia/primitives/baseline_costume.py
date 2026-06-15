"""baseline_costume.py — Proposal A primitive (v0, contract FROZEN 2026-06-10).

The reusable falsification gate every "we found structure" claim must clear.
Attacks the recurrent Prometheus failure mode: apparent structure that is just a
baseline wearing a hat (Erebos Layer 2 = per-plugin majority counter; Theseus
kill-topography = catalog volume; etc.).

It reports, for a structural claim, the STRONGEST cheap baseline that reproduces
it — i.e. the most embarrassing imposter you are indistinguishable from. This is
the inverse of a fit metric: it does not credit the gap over the weakest baseline,
it names the strongest baseline that ties you.

------------------------------------------------------------------------------
CONTRACT (frozen — Harmonia C/E code their validation calls against this)
------------------------------------------------------------------------------
v0 claim shape = a *recommendation map* {key: label} derived from `rows`.
Each baseline is a callable `rows -> {key: label}` competing with the claim.
Non-map claim shapes (e.g. Proposal B's per-cell hold-rate vs null) attach via a
custom `comparator` (interface present; default = map comparator). Proposal B is
expected to pass its own comparator; Proposal E uses the default map comparator
(claim = {parent_subpopulation: subclass}, baseline = marginal_majority).

    costume_check(claim, rows, baselines, *, key_fn, label_fn,
                  signature_fn=None, comparator=None, null=None,
                  n_null_trials=20, seed=0) -> CostumeVerdict

Returns CostumeVerdict with, per baseline: agreement_rate, actionable_deltas,
ties_claim, vacuous; plus the z-score of the claim vs a shuffle null, and a
headline verdict in {DISTINCT, COSTUME_OF:<baseline>, INCONCLUSIVE,
INCONCLUSIVE_DEGENERATE}.

DEGENERACY GUARD (added 2026-06-15, filed by Harmonia D): a within-key
aggregating baseline (marginal_majority, pair_aware) collapses to an identity
label-copier when every key has one row, so it ties ANY unique-key claim and
certifies nothing -> such ties are marked `vacuous` and excluded; if no
non-vacuous baseline remains, or the claim is imbalanced under the default
comparator (majority-class tie), the verdict is INCONCLUSIVE_DEGENERATE with a
message to supply cross-key/set-level baselines or an imbalance-aware comparator.
The guard does NOT detect caller-side circular construction (a claim DEFINED as
its own marginal — e.g. Proposal E's Q4); that remains usage discipline.

Catalog shipped in v0 (per the sequencing decision — three only; add more only
when a real claim shape needs them): marginal_majority, volume_weighted,
pair_aware. If only one baseline ever fires across real use, collapse the catalog
rather than ornament it (Proposal A §4 falsifier).
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional


# ----------------------------------------------------------------------------
# Types
# ----------------------------------------------------------------------------
RecMap = dict           # {key: label}
Baseline = Callable[[list], RecMap]


class InapplicableBaseline(Exception):
    """Raised by a baseline that cannot run on the given rows (e.g. pair_aware
    with no signature_fn). costume_check skips it rather than failing."""


@dataclass(frozen=True)
class BaselineResult:
    name: str
    agreement_rate: float          # fraction of shared keys where baseline == claim
    actionable_deltas: int         # shared keys where they differ substantively
    ties_claim: bool               # agreement_rate >= TIE_THRESHOLD
    n_shared_keys: int
    vacuous: bool = False          # tie is structurally meaningless (see degeneracy guard)


@dataclass(frozen=True)
class CostumeVerdict:
    verdict: str                   # DISTINCT | COSTUME_OF:<baseline> | INCONCLUSIVE
    headline: str
    strongest_tie: Optional[str]   # name of strongest baseline that ties, or None
    per_baseline: tuple            # tuple[BaselineResult]
    z_vs_null: float
    n_claim_keys: int
    notes: str = ""
    diagnostics: dict = field(default_factory=dict)


# Agreement at/above this fraction = the baseline reproduces the claim.
TIE_THRESHOLD = 0.90
MIN_KEYS_FOR_VERDICT = 5


# ----------------------------------------------------------------------------
# The v0 baseline catalog (three only)
# ----------------------------------------------------------------------------
def marginal_majority(rows: list, *, key_fn, label_fn) -> RecMap:
    """Per-key argmax label. The counter that caught Erebos (ITER-56)."""
    by_key: dict = defaultdict(Counter)
    for r in rows:
        by_key[key_fn(r)][label_fn(r)] += 1
    return {k: c.most_common(1)[0][0] for k, c in by_key.items()}


def volume_weighted(rows: list, *, key_fn, label_fn) -> RecMap:
    """Global mode assigned to EVERY key. Catches 'your per-key structure is just
    the globally dominant class by sheer volume' (kill-topography Finding 1)."""
    labels = [label_fn(r) for r in rows]
    if not labels:
        return {}
    global_mode = Counter(labels).most_common(1)[0][0]
    return {key_fn(r): global_mode for r in rows}


def pair_aware(rows: list, *, key_fn, label_fn, signature_fn=None) -> RecMap:
    """Per-key recommendation from its most-common co-occurrence context.
    Erebos's 'sophisticated counter' (ITER-59) reduced to the claim's key space:
    for each key, count labels within each signature group it appears in; pick the
    label that dominates its richest co-occurrence context. Requires signature_fn;
    raises InapplicableBaseline otherwise."""
    if signature_fn is None:
        raise InapplicableBaseline("pair_aware requires signature_fn")
    by_sig: dict = defaultdict(list)
    for r in rows:
        sig = signature_fn(r)
        if sig is not None:
            by_sig[sig].append(r)
    # key -> Counter(label) accumulated over the multi-row signature groups it's in
    key_ctx: dict = defaultdict(Counter)
    for sig, grp in by_sig.items():
        if len(grp) < 2:
            continue  # no co-occurrence partner
        for r in grp:
            key_ctx[key_fn(r)][label_fn(r)] += 1
    if not key_ctx:
        raise InapplicableBaseline("pair_aware: no multi-row signature groups")
    return {k: c.most_common(1)[0][0] for k, c in key_ctx.items()}


CATALOG: dict = {
    "marginal_majority": marginal_majority,
    "volume_weighted": volume_weighted,
    "pair_aware": pair_aware,
}
DEFAULT_BASELINES = ("marginal_majority", "volume_weighted", "pair_aware")


# ----------------------------------------------------------------------------
# Comparison + null
# ----------------------------------------------------------------------------
def _default_comparator(claim: RecMap, baseline_map: RecMap) -> tuple:
    """Compare two recommendation maps on their shared keys.
    Returns (agreement_rate, actionable_deltas, n_shared)."""
    shared = set(claim) & set(baseline_map)
    if not shared:
        return 0.0, 0, 0
    agree = sum(1 for k in shared if claim[k] == baseline_map[k])
    deltas = len(shared) - agree
    return agree / len(shared), deltas, len(shared)


def _shuffle_null_z(rows, claim, key_fn, label_fn, n_trials, seed) -> float:
    """Cheap structure-vs-noise leg: how concentrated is the claim's agreement
    with marginal_majority on real labels vs label-shuffled rows? z over trials.
    A claim that only matches the marginal because the marginal is itself
    structured will still beat shuffle; this leg is necessary, not sufficient —
    the baseline ties below are the decisive test."""
    real_map = marginal_majority(rows, key_fn=key_fn, label_fn=label_fn)
    real_agr, _, _ = _default_comparator(claim, real_map)
    rng = random.Random(seed)
    labels = [label_fn(r) for r in rows]
    trials = []
    for _ in range(n_trials):
        shuf = labels[:]
        rng.shuffle(shuf)
        srows = [dict(r, **{"__shuf_label__": lbl}) for r, lbl in zip(rows, shuf)]
        smap = marginal_majority(srows, key_fn=key_fn,
                                 label_fn=lambda r: r["__shuf_label__"])
        a, _, _ = _default_comparator(claim, smap)
        trials.append(a)
    if not trials:
        return 0.0
    mean = sum(trials) / len(trials)
    var = sum((t - mean) ** 2 for t in trials) / len(trials)
    std = var ** 0.5
    return (real_agr - mean) / std if std > 0 else 0.0


# ----------------------------------------------------------------------------
# The gate
# ----------------------------------------------------------------------------
def costume_check(
    claim: RecMap,
    rows: list,
    baselines=DEFAULT_BASELINES,
    *,
    key_fn,
    label_fn,
    signature_fn=None,
    comparator=None,
    null=None,            # reserved; v0 uses the built-in shuffle null
    n_null_trials=20,
    seed=0,
) -> CostumeVerdict:
    """Run the claim against the baseline catalog. See module docstring for the
    frozen contract."""
    cmp = comparator or _default_comparator

    # Degeneracy guard (filed by Harmonia D 2026-06-10, a3 generic_catalog_control).
    # Within-key aggregating baselines (marginal_majority, pair_aware) collapse to
    # IDENTITY label-copiers when every key has exactly one row: they then tie ANY
    # unique-key claim at 100%, certifying nothing. Detect "no aggregation happened"
    # via key multiplicity and mark such ties vacuous so they cannot drive a COSTUME
    # verdict. (Does NOT detect caller-side circular construction — a claim DEFINED
    # as its own marginal; that is usage discipline, see Proposal E review S1.)
    _key_mult = Counter(key_fn(r) for r in rows)
    _n_multi_keys = sum(1 for v in _key_mult.values() if v > 1)
    _AGGREGATING = {"marginal_majority", "pair_aware"}

    results: list = []
    for name in baselines:
        fn = CATALOG[name]
        try:
            if name == "pair_aware":
                bmap = fn(rows, key_fn=key_fn, label_fn=label_fn,
                          signature_fn=signature_fn)
            else:
                bmap = fn(rows, key_fn=key_fn, label_fn=label_fn)
        except InapplicableBaseline:
            continue
        agr, deltas, n_shared = cmp(claim, bmap)
        vacuous = (name in _AGGREGATING and _n_multi_keys == 0)
        results.append(BaselineResult(
            name=name, agreement_rate=agr, actionable_deltas=deltas,
            ties_claim=(agr >= TIE_THRESHOLD and n_shared >= MIN_KEYS_FOR_VERDICT),
            n_shared_keys=n_shared, vacuous=vacuous,
        ))

    z = _shuffle_null_z(rows, claim, key_fn, label_fn, n_null_trials, seed)

    real_ties = [r for r in results if r.ties_claim and not r.vacuous]
    non_vacuous = [r for r in results if not r.vacuous]
    n_vacuous_ties = sum(1 for r in results if r.ties_claim and r.vacuous)

    # Imbalance warning: with the DEFAULT comparator, a near-constant claim is tied
    # by any majority-class baseline (this is what bit the a3 binary VOID/NONVOID
    # control). Recommend an imbalance-aware comparator rather than silently COSTUMING.
    _label_share = Counter(claim.values())
    _imbalanced = bool(_label_share) and (
        _label_share.most_common(1)[0][1] / len(claim) >= TIE_THRESHOLD)
    _imbalance_note = (
        " [imbalanced claim + default comparator: supply an imbalance-aware "
        "comparator (e.g. minority-class Jaccard) before trusting a tie]"
        if _imbalanced and comparator is None else "")

    if len(claim) < MIN_KEYS_FOR_VERDICT or not results:
        verdict = "INCONCLUSIVE"
        strongest = None
        headline = (f"INCONCLUSIVE: claim has {len(claim)} keys "
                    f"(need >= {MIN_KEYS_FOR_VERDICT}) or no applicable baseline.")
    elif not non_vacuous:
        verdict = "INCONCLUSIVE_DEGENERATE"
        strongest = None
        headline = (
            "INCONCLUSIVE_DEGENERATE: claim has unique keys (no within-key "
            "aggregation), so every catalog baseline is an identity label-copier "
            "and ties vacuously. Supply a baseline that uses cross-key structure, "
            "or a custom comparator + set-level baselines (cf. Proposal B).")
    elif real_ties and _imbalanced and comparator is None:
        # Tie may be a pure majority-class artifact: the default comparator cannot
        # tell "real majority-class structure" from "imbalance" without a
        # minority-aware comparator. This is what bit D's binary VOID/NONVOID control.
        verdict = "INCONCLUSIVE_DEGENERATE"
        strongest = None
        headline = (
            f"INCONCLUSIVE_DEGENERATE: claim is imbalanced "
            f"({_label_share.most_common(1)[0][1] / len(claim):.1%} one label) and "
            f"the default comparator ties any majority-class baseline. Supply an "
            f"imbalance-aware comparator (e.g. minority-class Jaccard) to discriminate.")
    elif real_ties:
        strongest = max(real_ties, key=lambda r: r.agreement_rate).name
        verdict = f"COSTUME_OF:{strongest}"
        headline = (f"COSTUME: claim is indistinguishable from '{strongest}' "
                    f"({max(r.agreement_rate for r in real_ties):.1%} agreement). "
                    f"This structure is a baseline wearing a hat.")
    else:
        strongest = None
        verdict = "DISTINCT"
        best = max(non_vacuous, key=lambda r: r.agreement_rate)
        _vac = (f" ({n_vacuous_ties} vacuous tie(s) excluded by the unique-key guard)"
                if n_vacuous_ties else "")
        headline = (f"DISTINCT: no non-vacuous catalog baseline reproduces the claim "
                    f"(strongest {best.name} at {best.agreement_rate:.1%} "
                    f"< {TIE_THRESHOLD:.0%}); z_vs_shuffle={z:.2f}.{_vac}")

    return CostumeVerdict(
        verdict=verdict,
        headline=headline,
        strongest_tie=strongest,
        per_baseline=tuple(results),
        z_vs_null=z,
        n_claim_keys=len(claim),
        notes=(f"v0 contract; baselines={list(baselines)}; "
               f"TIE_THRESHOLD={TIE_THRESHOLD}; seed={seed}."),
        diagnostics={"per_baseline_agreement":
                     {r.name: round(r.agreement_rate, 4) for r in results}},
    )


# ----------------------------------------------------------------------------
# Self-test: reproduce the Erebos "ties the counter" failure on synthetic data,
# and a genuinely-distinct claim, so the contract is demonstrably live.
# ----------------------------------------------------------------------------
def _selftest() -> None:
    # Synthetic ledger: 5 plugins, each with a dominant kp (the marginal).
    rows = []
    for pid in range(5):
        dominant = f"kp_{pid}"
        for i in range(20):
            kp = dominant if i < 15 else f"kp_other_{i % 3}"
            rows.append({"plugin": f"p{pid}", "kp": kp, "sig": f"s{i}"})

    kf = lambda r: r["plugin"]
    lf = lambda r: r["kp"]

    # Claim 1: a "substrate" that just reproduces the per-plugin majority.
    costume_claim = marginal_majority(rows, key_fn=kf, label_fn=lf)
    v1 = costume_check(costume_claim, rows, key_fn=kf, label_fn=lf,
                       signature_fn=lambda r: r["sig"])
    assert v1.verdict.startswith("COSTUME_OF:marginal_majority"), v1.headline

    # Claim 2: a genuinely different recommendation (some non-majority picks).
    distinct_claim = {f"p{pid}": f"kp_novel_{pid}" for pid in range(5)}
    v2 = costume_check(distinct_claim, rows, key_fn=kf, label_fn=lf,
                       signature_fn=lambda r: r["sig"])
    assert v2.verdict == "DISTINCT", v2.headline

    print("baseline_costume v0 self-test PASS")
    print(" ", v1.headline)
    print(" ", v2.headline)


if __name__ == "__main__":
    _selftest()
