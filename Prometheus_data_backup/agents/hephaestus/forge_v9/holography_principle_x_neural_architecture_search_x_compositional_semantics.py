"""Holography Principle x Neural Architecture Search x Compositional Semantics.

Compositional: parse prompt into semantic atoms (entities, relations, quantities).
NAS: search for best primitive composition per problem type via surface features.
Holographic: surface keyword features predict optimal architecture.
Architecture selection via confidence_from_agreement across candidates.
"""

import re
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'forge_v3'))

from forge_primitives import (
    bayesian_update, entropy, modus_ponens, check_transitivity,
    temporal_order, solve_constraints, confidence_from_agreement,
    bat_and_ball, modular_arithmetic, all_but_n, fencepost_count,
    coin_flip_independence, parity_check, pigeonhole_check,
    direction_composition, information_sufficiency, negate,
)
from _caitl_parsers import (
    run_all_parsers, _nums, _has, _affirm, _deny,
    numeric_float_comparison, algebraic_word_problem,
    all_but_N_survivor_counting, transitive_ordering,
    modus_tollens_contrapositive, pigeonhole_principle,
    statistical_independence, number_parity, mathematical_identity,
    trick_question_equal_weight, positional_logic,
    universal_quantifier_converse_error, negation_scope_insufficiency,
    stated_premise_usage, subject_object_verb_parsing,
)

# Architecture registry: surface features -> primitive pipeline
ARCHITECTURES = {
    "logic_chain": ["modus_ponens", "check_transitivity"],
    "probability": ["bayesian_update", "coin_flip_independence"],
    "temporal": ["temporal_order", "direction_composition"],
    "arithmetic": ["bat_and_ball", "all_but_n", "fencepost_count"],
    "constraint": ["pigeonhole_check", "solve_constraints"],
    "comparison": ["numeric_comparison"],
    "parity": ["parity_check"],
}

# Surface feature detectors for holographic projection
FEATURE_MAP = {
    "logic_chain": ["if", "then", "therefore", "implies", "all", "every", "must"],
    "probability": ["probability", "chance", "likely", "coin", "flip", "dice", "random"],
    "temporal": ["before", "after", "first", "last", "order", "sequence", "north", "south"],
    "arithmetic": ["cost", "price", "total", "more than", "all but", "how many", "fence"],
    "constraint": ["must", "at least", "pigeonhole", "guarantee", "people", "months"],
    "comparison": ["larger", "smaller", "greater", "less", "heavier", "lighter", "bigger"],
    "parity": ["odd", "even", "parity", "sum of"],
}


class ReasoningTool:
    """Holographic NAS Compositional Reasoner (HNCR)."""

    def _extract_atoms(self, text):
        """Parse text into semantic atoms: entities, relations, quantities."""
        atoms = {
            "entities": re.findall(r"\b[A-Z][a-z]+\b", text),
            "quantities": _nums(text),
            "relations": [],
            "negations": [],
        }
        tl = text.lower()
        for rel in ["taller", "shorter", "heavier", "lighter", "faster", "older",
                     "bigger", "smaller", "larger", "greater", "less", "more"]:
            if rel in tl:
                atoms["relations"].append(rel)
        if re.search(r"\bnot\b|\bnever\b|\bno\b|\bcannot\b", tl):
            atoms["negations"].append("negation_present")
        return atoms

    def _select_architecture(self, prompt):
        """Holographic projection: surface features -> best architecture."""
        pl = prompt.lower()
        scores = {}
        for arch, keywords in FEATURE_MAP.items():
            score = sum(1 for kw in keywords if kw in pl)
            scores[arch] = score
        if not scores or max(scores.values()) == 0:
            return "logic_chain"  # default
        return max(scores, key=scores.get)

    def _run_architecture(self, arch, prompt, candidate):
        """Execute the selected primitive pipeline and return a score."""
        agg, tags = run_all_parsers(prompt, candidate)
        if tags:
            return (agg + 1) / 2  # map [-1,1] to [0,1]
        return 0.5  # no signal

    def _compositional_score(self, prompt, candidate):
        """Build meaning bottom-up from atoms."""
        atoms = self._extract_atoms(prompt)
        c_atoms = self._extract_atoms(candidate)
        score = 0.0
        # Entity overlap bonus
        p_ents = set(e.lower() for e in atoms["entities"])
        c_ents = set(e.lower() for e in c_atoms["entities"])
        if p_ents and c_ents:
            overlap = len(p_ents & c_ents) / max(len(p_ents), 1)
            score += overlap * 0.1
        # Quantity relevance
        if atoms["quantities"] and c_atoms["quantities"]:
            score += 0.05
        return score

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        arch = self._select_architecture(prompt)
        results = []
        arch_scores = []
        for cand in candidates:
            arch_score = self._run_architecture(arch, prompt, cand)
            comp_score = self._compositional_score(prompt, cand)
            combined = arch_score * 0.85 + comp_score * 0.15
            arch_scores.append(arch_score)
            results.append({"candidate": cand, "score": float(max(0, min(1, combined)))})

        # NAS: use confidence_from_agreement to validate architecture choice
        agreement = confidence_from_agreement(arch_scores)
        if agreement < 0.3:
            # Low agreement -> try alternate architecture
            alt_archs = [a for a in ARCHITECTURES if a != arch]
            for alt in alt_archs[:2]:
                alt_scores = []
                for cand in candidates:
                    s = self._run_architecture(alt, prompt, cand)
                    alt_scores.append(s)
                alt_agree = confidence_from_agreement(alt_scores)
                if alt_agree > agreement:
                    # Override with better architecture
                    for i, cand in enumerate(candidates):
                        comp = self._compositional_score(prompt, cand)
                        results[i]["score"] = float(max(0, min(1,
                            alt_scores[i] * 0.85 + comp * 0.15)))
                    break

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _meta_confidence(self, prompt, answer):
        """Detect ambiguous/insufficient problems."""
        pl = prompt.lower()
        agg, tags = run_all_parsers(prompt, answer)
        if not tags:
            return 0.4  # no parser fired - uncertain
        parser_conf = (agg + 1) / 2
        # Detect insufficiency
        if _has(pl, "cannot be determined", "not enough information"):
            if _has(answer.lower(), "cannot", "not enough", "insufficient"):
                return 0.8
        return parser_conf

    def _ncd(self, s1, s2):
        import zlib
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + " \n " + s2).encode()))
        mx = max(z1, z2)
        return (z12 - min(z1, z2)) / mx if mx > 0 else 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        agg, tags = run_all_parsers(prompt, answer)
        if tags:
            parser_conf = 0.05 + 0.9 * (agg + 1) / 2
            return float(max(0.0, min(1.0, parser_conf)))
        # Fallback: NCD-based (never worse than baseline)
        ncd_val = self._ncd(prompt, answer)
        conf = 1.0 - float(min(1.0, max(0.0, ncd_val)))
        return float(conf ** 2)
