"""Shared predicate strength lattice for G13 (Relation-Weakening) and
G14 (Relation-Strengthening).

Per pivot/erebos_g13_relation_weakening_research_2026-05-27.md +
pivot/erebos_g14_relation_strengthening_research_2026-05-27.md.

Each tier is (strength_rank, canonical_name, regex_for_detection,
human_form). Strength_rank: higher = stronger / more specific
predicate. G13 walks rank downward (relax); G14 walks upward (sharpen).

The detection regexes operate on lowercased claim text. Whole-word
or symbol matches; deliberately conservative (false negatives OK,
false positives drive bad emissions).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PredicateTier:
    """One rung of the predicate strength lattice."""
    rank: int                         # higher = stronger
    canonical_name: str               # short id, e.g., "exact_equality"
    detection_regex: str              # regex over lowercased text
    human_form: str                   # display string for the predicate
    weakening_replacement: str        # text used when emitting weaker form
    strengthening_replacement: str    # text used when emitting stronger form


# Strongest at top (rank 5); weakest at bottom (rank 1).
PREDICATE_LATTICE: list[PredicateTier] = [
    PredicateTier(
        rank=5,
        canonical_name="exact_equality",
        # `=` matches standalone equality but NOT when it's the `=`
        # inside sign(A) = sign(B) (preceded by `)` + optional space).
        # Fixed-width lookbehind: `=` not preceded by `)\s`.
        detection_regex=r"\b(equals?|is equal to|exactly equal)\b|(?<!\)\s)(?<!\))=(?![<>=])",
        human_form="exact equality (=)",
        weakening_replacement="approximately equal to (within rounding tolerance)",
        strengthening_replacement="exactly equal under ALL representations",  # rank 6 isn't in lattice
    ),
    PredicateTier(
        rank=4,
        canonical_name="approximate_equality",
        detection_regex=r"\b(approximately equal|approx equal|≈|within rounding tolerance|within \w+ tolerance)\b",
        human_form="approximate equality (~=)",
        weakening_replacement="congruent mod N (small N)",
        strengthening_replacement="exact equality",
    ),
    PredicateTier(
        rank=3,
        canonical_name="congruence_mod_n",
        detection_regex=r"\b(congruent mod \w+|≡ \w+ mod|equal mod \w+)\b",
        human_form="congruent modulo N",
        weakening_replacement="divides",
        strengthening_replacement="approximately equal to",
    ),
    PredicateTier(
        rank=2,
        canonical_name="divides",
        detection_regex=r"\b(divides|divisible by)\b|\bA \| B\b",
        human_form="divides (A | B)",
        weakening_replacement="has same sign as",
        strengthening_replacement="congruent mod N",
    ),
    PredicateTier(
        rank=1,
        canonical_name="sign_equality",
        # \b around sign(\w+) breaks because ) is non-word; use \b only
        # around the word-form variants and rely on literal specificity
        # for the sign(A)=sign(B) form.
        detection_regex=r"\b(same sign|sign-equal)\b|sign\(\w+\)\s*=\s*sign\(\w+\)",
        human_form="sign-equality (sign(A) = sign(B))",
        weakening_replacement="both non-zero",
        strengthening_replacement="divides",
    ),
]


def find_strongest_predicate(text: str) -> Optional[PredicateTier]:
    """Scan text for any registered predicate; return the highest-rank
    one detected (or None if none matched)."""
    text_lower = (text or "").lower()
    matched: list[PredicateTier] = []
    for tier in PREDICATE_LATTICE:
        if re.search(tier.detection_regex, text_lower):
            matched.append(tier)
    if not matched:
        return None
    return max(matched, key=lambda t: t.rank)


def find_weakest_predicate(text: str) -> Optional[PredicateTier]:
    """Inverse of find_strongest -- used by G14 to find which predicate
    to strengthen."""
    text_lower = (text or "").lower()
    matched: list[PredicateTier] = []
    for tier in PREDICATE_LATTICE:
        if re.search(tier.detection_regex, text_lower):
            matched.append(tier)
    if not matched:
        return None
    return min(matched, key=lambda t: t.rank)


def tier_below(tier: PredicateTier) -> Optional[PredicateTier]:
    """Return the tier one rank weaker than `tier` (G13 step). None if
    `tier` is already at rank 1."""
    for t in PREDICATE_LATTICE:
        if t.rank == tier.rank - 1:
            return t
    return None


def tier_above(tier: PredicateTier) -> Optional[PredicateTier]:
    """Return the tier one rank stronger than `tier` (G14 step). None
    if `tier` is already at the top rank."""
    for t in PREDICATE_LATTICE:
        if t.rank == tier.rank + 1:
            return t
    return None
