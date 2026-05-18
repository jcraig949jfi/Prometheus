"""TunerLite — Bayesian-flavored hyperparameter tuner for generators.

v0.1: random search + best-tracking. Designed to be swapped with Optuna
in Tier 2 — TunerLite.run_study() signature is intentionally
Optuna-compatible (`study.optimize(objective_fn, n_trials)`).

Objective per trial:
  1. Instantiate the generator with the trial's hyperparameter config
  2. Emit N evaluation records
  3. Score: mean(info_density × diversity) — yield-aligned proxy for
     generator value
  4. Return scalar score; tuner maximizes

Random search is adequate for small spaces (2-3 enumerable params,
5-10 values each; 25-300 configs). For continuous spaces or higher
dimensionality, swap in Optuna.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from theseus.emit.record_schema import TheseusRecord
from theseus.optimization.config_overrides import (
    load_overrides,
    save_overrides,
    update_overrides_for,
)
from theseus.optimization.spaces import GENERATOR_SPACES
from theseus.registry import get_generator_class
from theseus.scoring.diversity import diversity_score, use_jaccard_only
from theseus.scoring.info_density import info_density_score


@dataclass
class TunerResult:
    generator_id: str
    n_trials: int
    best_params: Dict[str, Any]
    best_score: float
    trials: List[Dict[str, Any]] = field(default_factory=list)
    wall_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _score_generator_with_params(
    generator_id: str,
    params: Dict[str, Any],
    n_records: int,
    seed: int,
) -> Tuple[float, int]:
    """Instantiate gen with params overlay; emit n_records; return
    (mean info_density * diversity, n_actual_records).
    """
    cls = get_generator_class(generator_id)
    # Build kwargs: filter to those the constructor accepts
    import inspect
    sig = inspect.signature(cls.__init__)
    accepted = set(sig.parameters.keys()) - {"self"}
    kwargs = {"batch_id": "tune", "seed": seed}
    for k, v in params.items():
        if k in accepted:
            kwargs[k] = v
        # Else: param is a module-level constant we'd need to override —
        # handled by direct module-attribute patching below.

    # Module-level constants override (for A4 STRONG_R2 / WEAK_R2 etc)
    module_overrides: List[Tuple[Any, str, Any]] = []
    try:
        module = inspect.getmodule(cls)
        for k, v in params.items():
            if k in accepted:
                continue
            if hasattr(module, k):
                module_overrides.append((module, k, getattr(module, k)))
                setattr(module, k, v)
    except Exception:
        pass

    try:
        g = cls(**kwargs)
        records: List[TheseusRecord] = []
        for _ in range(n_records * 3):  # retry budget
            if len(records) >= n_records:
                break
            try:
                r = g.next()
            except Exception:
                continue
            if r is None:
                continue
            records.append(r)

        if not records:
            return 0.0, 0

        # Score: mean info_density × mean diversity (Jaccard for speed)
        use_jaccard_only()
        info_scores = [info_density_score(r) for r in records]
        # Pairwise diversity vs first record (cheap proxy)
        if len(records) >= 2:
            div_scores = [diversity_score(r, records[:i] + records[i + 1:][:20])
                          for i, r in enumerate(records[:30])]
            mean_div = sum(div_scores) / len(div_scores)
        else:
            mean_div = 1.0
        mean_info = sum(info_scores) / len(info_scores)
        return mean_info * mean_div, len(records)
    finally:
        # Restore module constants
        for module, name, orig in module_overrides:
            setattr(module, name, orig)


class TunerLite:
    """Random + best-tracking tuner. Optuna-compatible signature."""

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    def _sample_config(self, space: Dict[str, List[Any]]) -> Dict[str, Any]:
        return {k: self._rng.choice(v) for k, v in space.items()}

    def _grid_configs(self, space: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        keys = list(space.keys())
        product = list(itertools.product(*(space[k] for k in keys)))
        return [dict(zip(keys, vals)) for vals in product]

    def run_study(
        self,
        generator_id: str,
        n_trials: int = 30,
        n_records_per_trial: int = 50,
        mode: str = "random",  # "random" or "grid"
    ) -> TunerResult:
        """Run a tuning study. `mode='grid'` exhaustively enumerates
        small spaces; `mode='random'` samples n_trials configs."""
        if generator_id not in GENERATOR_SPACES:
            raise KeyError(
                f"No tunable space defined for '{generator_id}'. "
                f"Available: {sorted(GENERATOR_SPACES.keys())}"
            )
        space = GENERATOR_SPACES[generator_id]

        if mode == "grid":
            configs = self._grid_configs(space)
            if len(configs) > n_trials:
                # Sample n_trials uniformly from the grid
                self._rng.shuffle(configs)
                configs = configs[:n_trials]
        else:
            configs = [self._sample_config(space) for _ in range(n_trials)]

        start = time.monotonic()
        trials: List[Dict[str, Any]] = []
        best_score = -1.0
        best_params: Dict[str, Any] = {}
        for i, params in enumerate(configs):
            score, n_actual = _score_generator_with_params(
                generator_id, params, n_records_per_trial, seed=i
            )
            trials.append({
                "trial_id": i,
                "params": params,
                "score": score,
                "n_records": n_actual,
            })
            if score > best_score:
                best_score = score
                best_params = dict(params)

        wall = time.monotonic() - start
        return TunerResult(
            generator_id=generator_id,
            n_trials=len(configs),
            best_params=best_params,
            best_score=best_score,
            trials=trials,
            wall_seconds=wall,
        )


def main() -> None:
    parser = argparse.ArgumentParser(prog="theseus.optimization.bayes_tuner")
    parser.add_argument(
        "--generator",
        required=True,
        help=f"Generator id to tune. Available: {sorted(GENERATOR_SPACES.keys())}",
    )
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--records-per-trial", type=int, default=50)
    parser.add_argument(
        "--mode", choices=("random", "grid"), default="random"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Save best params to tuned_hyperparams.json on completion",
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    tuner = TunerLite(seed=args.seed)
    print(f"[tuner] Starting study: {args.generator}, "
          f"trials={args.trials}, mode={args.mode}")
    result = tuner.run_study(
        generator_id=args.generator,
        n_trials=args.trials,
        n_records_per_trial=args.records_per_trial,
        mode=args.mode,
    )
    print(
        f"[tuner] Done in {result.wall_seconds:.1f}s. "
        f"Best score: {result.best_score:.4f}"
    )
    print(f"[tuner] Best params: {json.dumps(result.best_params, sort_keys=True)}")
    if args.apply:
        update_overrides_for(args.generator, result.best_params)
        print(f"[tuner] Applied to overrides file.")


if __name__ == "__main__":
    main()
