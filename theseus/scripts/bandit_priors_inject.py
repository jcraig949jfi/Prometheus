"""Inject lifetime-saturation-derived priors into bandit history.

Problem the Fire #62-#63 data exposed:
- The new lifetime-saturation yield_score formula only boosts gens
  whose lifetime_saturation < 1.0.
- c5 is the only such gen (~9% sat) but it hasn't been picked
  recently — n=2 history entries means UCB doesn't pull it into
  the top-5 strongly enough.
- Catch-22: c5 can't get picked → can't record new-formula score
  → bandit can't learn to prefer it.

This script breaks the catch-22 with a one-shot priors injection:
- For each gen with lifetime_saturation < threshold (default 0.5),
  compute a synthetic new-formula score using realistic base
  (info=0.5, div=0.5, steps=99) and append to history.
- This biases the next bandit hydration toward natural explorers.

Defensible: the synthetic score is what the formula WOULD produce
for that gen given its actual signature_index saturation. Not a
hack — it's making explicit the prior that the bandit can't
otherwise infer from its history sample.

Run before next fire:
    python -m theseus.scripts.bandit_priors_inject
    python -m theseus.scripts.bandit_priors_inject --threshold 0.7 --base 0.005
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from theseus.orchestration.bandit_state import load_history, save_history
from theseus.orchestration.signature_index import INSTANCE as SIGNATURE_INDEX
from theseus.registry import REGISTRY


def compute_priors(
    threshold: float = 0.5,
    base: float = 0.003,
) -> dict:
    """Return {gid: prior_score} for gens with lifetime_sat < threshold.

    Uses the Fire #62 formula:
        score = base × (1 + 5 × (1 - sat))
    No dup-rate penalty assumed (synthetic priors represent best-case
    new-formula scoring for the gen).
    """
    out: dict = {}
    for gid in sorted(REGISTRY.keys()):
        sat = SIGNATURE_INDEX.saturation_score(gid)
        if sat is None:
            continue
        if sat >= threshold:
            continue
        score = base * (1.0 + 5.0 * (1.0 - sat))
        out[gid] = score
    return out


def inject(
    threshold: float = 0.5,
    base: float = 0.003,
    n_copies: int = 3,
    dry_run: bool = False,
) -> int:
    """Inject priors into bandit history. Returns count of gens patched.

    `n_copies` controls how many synthetic entries to append per gen.
    More copies = stronger bias. 3 is enough to pull the mean
    meaningfully without erasing real history.
    """
    priors = compute_priors(threshold=threshold, base=base)
    if not priors:
        print(f"[priors] No gens below sat threshold {threshold:.2f}; "
              f"nothing to inject.")
        return 0
    history = load_history()
    print(f"[priors] Found {len(priors)} explorer gens:")
    for gid, score in priors.items():
        existing = history.get(gid, [])
        mean_before = sum(existing) / len(existing) if existing else 0.0
        n_before = len(existing)
        new_entries = [score] * n_copies
        if not dry_run:
            history.setdefault(gid, []).extend(new_entries)
        n_after = n_before + n_copies
        scores_after = existing + new_entries
        mean_after = sum(scores_after) / len(scores_after)
        print(
            f"  {gid}: sat={SIGNATURE_INDEX.saturation_score(gid)*100:.1f}%  "
            f"prior_score={score:.5f}  "
            f"mean: {mean_before:.5f} -> {mean_after:.5f}  "
            f"(n: {n_before} -> {n_after})"
        )
    if dry_run:
        print("[priors] DRY RUN — no changes persisted.")
    else:
        save_history(history)
        print(f"[priors] Persisted {len(priors)} × {n_copies} entries to bandit_history.json")
    return len(priors)


def main() -> int:
    p = argparse.ArgumentParser(
        description="One-shot bandit-priors injection for explorer gens."
    )
    p.add_argument(
        "--threshold", type=float, default=0.5,
        help="Inject priors for gens with lifetime_saturation < threshold. "
             "Default 0.5 (50%).",
    )
    p.add_argument(
        "--base", type=float, default=0.003,
        help="Base score (info_density × diversity / steps) used in synthetic "
             "calculation. Default 0.003 (matches observed batch averages).",
    )
    p.add_argument(
        "--copies", type=int, default=3,
        help="Copies of the synthetic score to inject per gen. Default 3.",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be injected without persisting.",
    )
    args = p.parse_args()
    n = inject(
        threshold=args.threshold,
        base=args.base,
        n_copies=args.copies,
        dry_run=args.dry_run,
    )
    return 0 if n >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
