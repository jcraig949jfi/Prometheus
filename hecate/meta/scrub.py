"""Deterministic blinding scrubber for the gravity detector and the matcher
(meta-experiment v1 PREREG, M1/M2). Applied identically to every arm and to
the calibration controls.

Removes: the 95 Nous dictionary concept names (with plural/singular,
hyphen/space and case variants), distinctive eponyms and stems of those
names, the 20 Nous field names, all-caps acronyms (2+ letters, which also
removes invented architecture acronyms), "Capitalised Invented Name (ACRO)"
coinages, and novelty words. check() then asserts that no dictionary name
or field name survives; a failing item is a scrubber defect, not data.
"""

from __future__ import annotations

import functools
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EPONYMS_AND_STEMS = (
    "Kalman", "Hebbian", "Hebb", "Nash", "Hoare", "Kolmogorov", "Fourier",
    "Bayesian", "Bayes", "autoencoder", "autoencoders", "wavelet", "wavelets",
    "free energy", "free-energy", "active inference", "predictive coding",
    "sparse code", "sparse codes", "reservoir computer", "echo state",
    "liquid state", "sandpile", "sand pile", "self-organised criticality",
    "error-correcting code", "error correcting code", "renormalisation",
    "holographic", "autopoietic", "epigenetic", "morphogen", "morphogens",
    "phenomenological", "dialectical", "abductive", "counterfactual",
    "metacognitive", "metamorphic", "category-theoretic", "categorical",
    "functor", "functors", "Nyquist", "Turing pattern", "Turing patterns",
    "Markov blanket", "Markov blankets", "Grice", "Gricean", "Jaynes",
    "Pontryagin", "Hamilton-Jacobi-Bellman", "Olshausen", "Lewis", "Pearl",
    "Shannon", "Lebesgue", "Riemann", "Hausdorff", "Hamming", "Reed-Solomon",
)
NOVELTY = ("novel", "new", "newly", "unprecedented", "groundbreaking",
           "innovative", "revolutionary", "first-ever", "unique", "uniquely")
MASK = "[X]"


@functools.lru_cache(maxsize=1)
def vocab():
    sys.path.insert(0, os.path.join(ROOT, "agents", "nous", "src"))
    try:
        from concepts import CONCEPTS  # type: ignore
    finally:
        sys.path.pop(0)
    names = [c["name"] for c in CONCEPTS]
    fields = sorted({c["field"] for c in CONCEPTS})
    return names, fields


def _variants(term):
    out = {term}
    for t in list(out):
        out.add(t.replace("-", " "))
        out.add(t.replace(" ", "-"))
    for t in list(out):
        if t.endswith("s") and not t.endswith("ss"):
            out.add(t[:-1])
        else:
            out.add(t + "s")
    return out


@functools.lru_cache(maxsize=1)
def _pattern():
    names, fields = vocab()
    terms = set()
    for t in list(names) + list(fields) + list(EPONYMS_AND_STEMS):
        terms |= _variants(t)
    alts = sorted((re.escape(t) for t in terms), key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z])(?:" + "|".join(alts) + r")(?![A-Za-z])", re.I)


COINAGE = re.compile(r"(?:[A-Z][\w-]+\s+){1,7}\(\s*[A-Z][A-Za-z0-9-]{1,}\s*\)")
ACRONYM = re.compile(r"(?<![A-Za-z])[A-Z][A-Z0-9]{1,}s?(?![A-Za-z])")
NOVEL = re.compile(r"(?<![A-Za-z])(?:" + "|".join(NOVELTY) + r")(?![A-Za-z])", re.I)


def scrub(text: str) -> str:
    t = COINAGE.sub("[NAME]", text)
    t = _pattern().sub(MASK, t)
    t = ACRONYM.sub(MASK, t)
    t = NOVEL.sub("", t)
    return re.sub(r"[ \t]{2,}", " ", t)


def check(text: str) -> list[str]:
    names, fields = vocab()
    low = text.lower()
    return [n for n in list(names) + list(fields)
            if re.search(r"(?<![a-z])" + re.escape(n.lower()) + r"(?![a-z])", low)]


def mechanism_text(m: dict) -> str:
    """The detector's view of one arm mechanism: its structured content, in a
    fixed order, with no arm, unit or concept metadata."""
    keys = ("statement", "what_exists", "what_changes", "what_persists",
            "what_is_selected", "what_can_reproduce", "what_can_learn",
            "what_can_transfer", "distinguishing_observable", "minimal_world")
    parts = []
    for k in keys:
        v = m.get(k)
        if isinstance(v, list):
            v = "; ".join(str(x) for x in v)
        if v:
            parts.append(f"{k.replace('_', ' ')}: {v}")
    return scrub("\n".join(parts))
