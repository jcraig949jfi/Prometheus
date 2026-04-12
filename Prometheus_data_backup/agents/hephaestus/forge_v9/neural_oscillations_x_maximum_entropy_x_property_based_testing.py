"""Neural Oscillations x Maximum Entropy x Property-Based Testing.

Oscillation: run multiple evaluation passes with different parser weightings,
like oscillating between interpretations. MaxEnt: when oscillation doesn't
converge, default to uniform. Property-based testing: verify structural
invariants (type, range, consistency). Confidence = inverse of amplitude.
"""

import re
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'forge_v3'))

from forge_primitives import (
    bayesian_update, entropy, solve_constraints, confidence_from_agreement,
    bat_and_ball, modular_arithmetic, all_but_n, fencepost_count,
    coin_flip_independence, parity_check, pigeonhole_check, modus_ponens,
    check_transitivity, temporal_order, direction_composition,
    information_sufficiency, solve_sat, negate,
)
from _caitl_parsers import (
    run_all_parsers, numeric_float_comparison, trick_question_equal_weight,
    positional_logic, algebraic_word_problem, universal_quantifier_converse_error,
    mathematical_identity, pigeonhole_principle, statistical_independence,
    number_parity, all_but_N_survivor_counting, transitive_ordering,
    negation_scope_insufficiency, stated_premise_usage,
    subject_object_verb_parsing, modus_tollens_contrapositive, _nums,
)

_NUM = re.compile(r"[-+]?\d*\.?\d+")


class ReasoningTool:
    """Oscillatory MaxEnt Property-Checked Reasoner (OMPCR)."""

    # Three oscillation phases with different parser weight profiles
    PHASE_WEIGHTS = [
        {"structural": 1.0, "numeric": 0.6, "logical": 0.4},
        {"structural": 0.4, "numeric": 1.0, "logical": 0.6},
        {"structural": 0.6, "numeric": 0.4, "logical": 1.0},
    ]

    def _classify_parsers(self, prompt, candidate):
        """Run parsers and classify scores into structural/numeric/logical."""
        scores = {"structural": [], "numeric": [], "logical": []}
        structural = [trick_question_equal_weight, positional_logic,
                      subject_object_verb_parsing, stated_premise_usage]
        numeric = [numeric_float_comparison, algebraic_word_problem,
                   all_but_N_survivor_counting, number_parity,
                   pigeonhole_principle, mathematical_identity,
                   statistical_independence]
        logical = [universal_quantifier_converse_error, transitive_ordering,
                   negation_scope_insufficiency, modus_tollens_contrapositive]
        for fn in structural:
            s, m = fn(prompt, candidate)
            if m:
                scores["structural"].append(s)
        for fn in numeric:
            s, m = fn(prompt, candidate)
            if m:
                scores["numeric"].append(s)
        for fn in logical:
            s, m = fn(prompt, candidate)
            if m:
                scores["logical"].append(s)
        return scores

    def _oscillate(self, prompt, candidate):
        """Run 3 oscillation phases, return per-phase scores."""
        cat_scores = self._classify_parsers(prompt, candidate)
        phase_scores = []
        for weights in self.PHASE_WEIGHTS:
            total, count = 0.0, 0
            for cat, slist in cat_scores.items():
                w = weights.get(cat, 0.5)
                for s in slist:
                    total += s * w
                    count += 1
            phase_scores.append(total / count if count > 0 else 0.0)
        return phase_scores

    def _property_check(self, prompt, candidate):
        """Verify structural invariants on the candidate answer."""
        pl = prompt.lower()
        cl = candidate.lower().strip()
        score = 0.0
        # Type check: if prompt asks for a number, candidate should have one
        if re.search(r"how many|how much|what is the|cost|price", pl):
            if _nums(candidate):
                score += 0.1
            else:
                score -= 0.05
        # Range check: if candidate has a number, check non-negative for counts
        if re.search(r"how many|how much|left|remain", pl):
            nums = _nums(candidate)
            if nums and nums[0] < 0:
                score -= 0.3
        # Consistency: yes/no question should get yes/no answer
        if pl.strip().endswith("?"):
            is_yn = re.search(r"^(is |are |does |do |can |will |was |should |must |has )", pl)
            if is_yn:
                if cl in ("yes", "no", "true", "false"):
                    score += 0.05
        return score

    def _maxent_fallback(self, n_candidates):
        """Uniform distribution when oscillation diverges."""
        return [1.0 / n_candidates] * n_candidates

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        all_phase_scores = []
        for cand in candidates:
            phases = self._oscillate(prompt, cand)
            all_phase_scores.append(phases)

        # Check convergence via entropy of phase score variance
        for i, cand in enumerate(candidates):
            phases = all_phase_scores[i]
            prop = self._property_check(prompt, cand)
            # Oscillation amplitude
            amplitude = max(phases) - min(phases) if phases else 0.0
            mean_phase = sum(phases) / len(phases) if phases else 0.0
            # If amplitude is high (divergence), trust MaxEnt fallback more
            if amplitude > 0.5:
                fallback = self._maxent_fallback(len(candidates))
                score = fallback[i] * 0.3 + mean_phase * 0.3 + prop * 0.4
            else:
                score = mean_phase * 0.7 + prop * 0.3
            # Bayesian update: use aggregate parser score as likelihood
            agg, _ = run_all_parsers(prompt, cand)
            if agg != 0:
                prior = 0.5
                likelihood = max(0.01, min(0.99, (agg + 1) / 2))
                posterior = bayesian_update(prior, likelihood, 1 - likelihood)
                score = score * 0.3 + posterior * 0.7
            results.append({"candidate": cand, "score": float(max(0, min(1, score)))})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _meta_confidence(self, prompt, answer):
        """Internal meta-confidence: detect ambiguity/insufficiency."""
        pl = prompt.lower()
        # Detect insufficient info
        if re.search(r"cannot be determined|not enough|insufficient", pl):
            return 0.3
        phases = self._oscillate(prompt, answer)
        amplitude = max(phases) - min(phases) if phases else 0.0
        agreement = confidence_from_agreement(phases) if phases else 0.5
        # High amplitude = low confidence
        conf = agreement * (1.0 - min(1.0, amplitude))
        return max(0.0, min(1.0, conf))

    def _ncd(self, s1, s2):
        """NCD between two strings."""
        import zlib
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + " \n " + s2).encode()))
        mx = max(z1, z2)
        return (z12 - min(z1, z2)) / mx if mx > 0 else 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        agg, tags = run_all_parsers(prompt, answer)
        if tags:
            # Parser signal dominates: map [-1,1] -> [0.05, 0.95]
            parser_conf = 0.05 + 0.9 * (agg + 1) / 2
            return float(max(0.0, min(1.0, parser_conf)))
        # Fallback: NCD-based similarity (matches NCD baseline behavior)
        ncd_val = self._ncd(prompt, answer)
        conf = 1.0 - float(min(1.0, max(0.0, ncd_val)))
        return float(conf ** 2)
