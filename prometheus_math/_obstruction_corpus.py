"""prometheus_math._obstruction_corpus — synthetic OEIS-shaped battery.

This module is the GROUND TRUTH for ``ObstructionEnv``. It builds a
synthetic corpus of 150 OEIS-shaped records with two structurally
significant signatures planted explicitly. The env is a discovery
test: can an RL agent (re)discover those signatures from the lift
signal alone?

Synthetic-battery construction (so reviewers can audit what the env
'should find'):

  Each record has nine features simulating those that Charon's
  ``a149_obstruction.py`` extracts from OEIS step-set names:

    n_steps        in {3..7}    (length of the step set)
    neg_x, pos_x   in {0..7}    (count of steps with neg/pos x)
    neg_y, pos_y   in {0..7}    (count of steps with neg/pos y)
    neg_z, pos_z   in {0..7}    (count of steps with neg/pos z)
    has_diag_neg   bool         (presence of step (-1, -1, -1))
    has_diag_pos   bool         (presence of step (+1, +1, +1))

  Plus a kill_verdict (bool): does the falsification battery
  unanimously kill the sequence? (In live data, this is the
  F1+F6+F9+F11 union from ``battery_sweep_v2.jsonl``; here it is
  planted.)

  Two signatures are planted as deterministically-killed predicates:

    OBSTRUCTION_SIGNATURE = {
        n_steps: 5, neg_x: 4, pos_x: 1, has_diag_neg: True
    }
        - Mirror of Charon's a149_obstruction discovery.
        - 6 records match this signature exactly.
        - All 6 have kill_verdict = True (deterministic).

    SECONDARY_SIGNATURE = {n_steps: 7, has_diag_pos: True}
        - A second planted signature for diversity (so an agent might
          rediscover either; both yield positive lift).
        - 3 records match this signature exactly.
        - All 3 have kill_verdict = True (deterministic).

  Noise model:
    - Of the ~141 records that match neither signature, 2% have
      kill_verdict = True (random noise; ~3 records).
    - This gives a baseline kill rate ~ 2/141 ~ 1.4%; the planted
      match-group rate is ~100%, producing in-sample lift > 50x —
      well above any random-predicate's lift, so the RL agent has a
      huge gradient to climb.

  Total kill count: 6 + 3 + ~3 = ~12 records (out of 150).

Random seed: the corpus is generated deterministically by
``_build_corpus(seed=20260427)`` at import time, so every run sees
the same battery. Re-seed only by editing the literal in source
(this is a deliberate constant so the env's tests are reproducible).

The CorpusEntry dataclass is the public type the env consumes.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CorpusEntry:
    """A single synthetic OEIS-shaped record.

    Mirrors the structural-feature schema in
    ``sigma_kernel/a149_obstruction.py::features_of`` but adds the
    explicit ``kill_verdict`` ground-truth field. Numeric features are
    integer counts; booleans are presence flags.
    """

    n_steps: int
    neg_x: int
    pos_x: int
    neg_y: int
    pos_y: int
    neg_z: int
    pos_z: int
    has_diag_neg: bool
    has_diag_pos: bool
    kill_verdict: bool

    def features(self) -> Dict[str, Any]:
        """Return the feature dict (without kill_verdict). Mirrors the
        agent's observable predicate evaluation surface."""
        return {
            "n_steps": self.n_steps,
            "neg_x": self.neg_x,
            "pos_x": self.pos_x,
            "neg_y": self.neg_y,
            "pos_y": self.pos_y,
            "neg_z": self.neg_z,
            "pos_z": self.pos_z,
            "has_diag_neg": self.has_diag_neg,
            "has_diag_pos": self.has_diag_pos,
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Planted signatures — ground truth
# ---------------------------------------------------------------------------


# Mirror of the OBSTRUCTION_SHAPE found in Charon's live A149* analysis.
OBSTRUCTION_SIGNATURE: Dict[str, Any] = {
    "n_steps": 5,
    "neg_x": 4,
    "pos_x": 1,
    "has_diag_neg": True,
}

# A diversity-planted second signature (nothing astrophysical; just an
# alternative attractor for the RL agent so the env doesn't have a
# unique global optimum).
SECONDARY_SIGNATURE: Dict[str, Any] = {
    "n_steps": 7,
    "has_diag_pos": True,
}


# ---------------------------------------------------------------------------
# Corpus construction
# ---------------------------------------------------------------------------


# Generation seed — fixed so tests are reproducible.
_CORPUS_SEED = 20260427


def _matches(entry_features: Dict[str, Any], predicate: Dict[str, Any]) -> bool:
    """Conjunctive-AND match: every key in predicate must equal the
    corresponding feature in entry_features."""
    if not predicate:
        return True
    for key, value in predicate.items():
        if entry_features.get(key) != value:
            return False
    return True


def _make_obstruction_match(rng: random.Random) -> CorpusEntry:
    """Build a record that matches OBSTRUCTION_SIGNATURE.

    Free dimensions: neg_y/pos_y/neg_z/pos_z/has_diag_pos randomized;
    constrained: n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True.
    kill_verdict is forced True (deterministic plant).
    """
    return CorpusEntry(
        n_steps=5,
        neg_x=4,
        pos_x=1,
        neg_y=rng.randint(0, 4),
        pos_y=rng.randint(0, 4),
        neg_z=rng.randint(0, 4),
        pos_z=rng.randint(0, 4),
        has_diag_neg=True,
        has_diag_pos=rng.random() < 0.3,
        kill_verdict=True,
    )


def _make_secondary_match(rng: random.Random) -> CorpusEntry:
    """Build a record that matches SECONDARY_SIGNATURE.

    Constrained: n_steps=7, has_diag_pos=True. Other dims free.
    kill_verdict forced True. Must NOT also match OBSTRUCTION_SIGNATURE
    (n_steps=5 vs 7, so disjoint — guaranteed safe).
    """
    return CorpusEntry(
        n_steps=7,
        neg_x=rng.randint(0, 4),
        pos_x=rng.randint(0, 4),
        neg_y=rng.randint(0, 4),
        pos_y=rng.randint(0, 4),
        neg_z=rng.randint(0, 4),
        pos_z=rng.randint(0, 4),
        has_diag_neg=rng.random() < 0.3,
        has_diag_pos=True,
        kill_verdict=True,
    )


def _make_random_nonmatch(rng: random.Random, noise_kill_prob: float) -> CorpusEntry:
    """Build a random record that matches NEITHER planted signature.

    To make the discovery task non-trivial, we ALLOW n_steps in
    {5, 7} for non-matches (decoy records) but force their other
    features to disqualify the planted signatures:

    - For n_steps=5 decoys: neg_x is chosen from {0, 1, 2, 3, 5} so
      the OBSTRUCTION_SIGNATURE conjunct ``neg_x=4`` filters them out.
      This forces the agent to pick BOTH ``n_steps=5`` AND ``neg_x=4``
      to isolate the obstruction matches.
    - For n_steps=7 decoys: has_diag_pos=False so the SECONDARY
      conjunct filters them out.

    n_steps in {3, 4, 6} is unconstrained (these never match either
    planted signature).
    """
    n_steps = rng.choice([3, 3, 4, 4, 5, 6, 6, 7])
    if n_steps == 5:
        # Force OBSTRUCTION non-match via neg_x.
        neg_x = rng.choice([0, 1, 2, 3, 5])
        pos_x = rng.randint(0, 5)
        has_diag_neg = rng.random() < 0.3
        has_diag_pos = rng.random() < 0.3
    elif n_steps == 7:
        # Force SECONDARY non-match via has_diag_pos.
        neg_x = rng.randint(0, 5)
        pos_x = rng.randint(0, 5)
        has_diag_neg = rng.random() < 0.3
        has_diag_pos = False
    else:
        neg_x = rng.randint(0, 5)
        pos_x = rng.randint(0, 5)
        has_diag_neg = rng.random() < 0.3
        has_diag_pos = rng.random() < 0.3
    return CorpusEntry(
        n_steps=n_steps,
        neg_x=neg_x,
        pos_x=pos_x,
        neg_y=rng.randint(0, 4),
        pos_y=rng.randint(0, 4),
        neg_z=rng.randint(0, 4),
        pos_z=rng.randint(0, 4),
        has_diag_neg=has_diag_neg,
        has_diag_pos=has_diag_pos,
        kill_verdict=(rng.random() < noise_kill_prob),
    )


def _build_corpus(
    seed: int = _CORPUS_SEED,
    n_total: int = 150,
    n_obstruction_matches: int = 8,
    n_secondary_matches: int = 4,
    noise_kill_prob: float = 0.015,
) -> List[CorpusEntry]:
    """Construct the synthetic corpus deterministically from a seed.

    Returns ``n_total`` entries, including ``n_obstruction_matches``
    OBSTRUCTION_SIGNATURE-matching records and ``n_secondary_matches``
    SECONDARY_SIGNATURE-matching records, with the remainder
    non-matching and noise-killed at rate ``noise_kill_prob``.

    All planted matches have kill_verdict=True deterministically;
    non-matches have kill_verdict=True with probability noise_kill_prob.
    """
    rng = random.Random(seed)
    entries: List[CorpusEntry] = []

    for _ in range(n_obstruction_matches):
        entries.append(_make_obstruction_match(rng))
    for _ in range(n_secondary_matches):
        entries.append(_make_secondary_match(rng))

    n_noise = n_total - n_obstruction_matches - n_secondary_matches
    for _ in range(n_noise):
        entries.append(_make_random_nonmatch(rng, noise_kill_prob))

    # Validate construction: assert match-group invariants. If something
    # in the random-nonmatch branch accidentally matched a planted
    # signature, drop it and resample.
    for i, e in enumerate(entries[n_obstruction_matches + n_secondary_matches:],
                          start=n_obstruction_matches + n_secondary_matches):
        feats = e.features()
        if _matches(feats, OBSTRUCTION_SIGNATURE) or _matches(feats, SECONDARY_SIGNATURE):
            # Resample until non-matching. (n_steps in {3,4,6} guarantees
            # no match; this branch should never fire, but defensive.)
            while True:
                replacement = _make_random_nonmatch(rng, noise_kill_prob)
                rfeats = replacement.features()
                if not _matches(rfeats, OBSTRUCTION_SIGNATURE) and not _matches(
                    rfeats, SECONDARY_SIGNATURE
                ):
                    entries[i] = replacement
                    break

    rng.shuffle(entries)
    return entries


# Module-level singleton: built once at import.
OBSTRUCTION_CORPUS: List[CorpusEntry] = _build_corpus()


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def corpus_summary() -> Dict[str, Any]:
    """Return a summary of the planted ground truth for review/audit."""
    n = len(OBSTRUCTION_CORPUS)
    n_kills = sum(1 for e in OBSTRUCTION_CORPUS if e.kill_verdict)
    n_obs = sum(
        1 for e in OBSTRUCTION_CORPUS if _matches(e.features(), OBSTRUCTION_SIGNATURE)
    )
    n_sec = sum(
        1 for e in OBSTRUCTION_CORPUS if _matches(e.features(), SECONDARY_SIGNATURE)
    )
    n_obs_killed = sum(
        1 for e in OBSTRUCTION_CORPUS
        if _matches(e.features(), OBSTRUCTION_SIGNATURE) and e.kill_verdict
    )
    n_sec_killed = sum(
        1 for e in OBSTRUCTION_CORPUS
        if _matches(e.features(), SECONDARY_SIGNATURE) and e.kill_verdict
    )
    n_other_kills = n_kills - n_obs_killed - n_sec_killed
    return {
        "n_total": n,
        "n_kills": n_kills,
        "baseline_kill_rate": n_kills / n,
        "obstruction_matches": n_obs,
        "obstruction_killed": n_obs_killed,
        "secondary_matches": n_sec,
        "secondary_killed": n_sec_killed,
        "noise_kills": n_other_kills,
    }


__all__ = [
    "CorpusEntry",
    "OBSTRUCTION_CORPUS",
    "OBSTRUCTION_SIGNATURE",
    "SECONDARY_SIGNATURE",
    "corpus_summary",
]
