"""Category Theory x Error Correcting Codes x Adaptive Control.

Category theory: functorial mapping between problem representations.
Error correcting: redundant parsers that cross-check (2-of-3 majority vote).
Adaptive control: adjust parser weights based on prompt structure fit.
"""

import re
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'forge_v3'))

from forge_primitives import (
    bayesian_update, entropy, solve_sat, check_transitivity,
    confidence_from_agreement, modus_ponens, parity_check,
    pigeonhole_check, bat_and_ball, all_but_n, fencepost_count,
    coin_flip_independence, modular_arithmetic, temporal_order,
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


class ReasoningTool:
    """Functorial Error-Corrected Adaptive Reasoner (FECAR)."""

    # Three redundant "channels" (parser banks) for error correction
    CHANNEL_A = [  # structural/linguistic
        trick_question_equal_weight, positional_logic,
        subject_object_verb_parsing, stated_premise_usage,
        negation_scope_insufficiency,
    ]
    CHANNEL_B = [  # numeric/algebraic
        numeric_float_comparison, algebraic_word_problem,
        all_but_N_survivor_counting, number_parity,
        pigeonhole_principle, mathematical_identity,
        statistical_independence,
    ]
    CHANNEL_C = [  # logical/relational
        universal_quantifier_converse_error, transitive_ordering,
        modus_tollens_contrapositive,
    ]

    def _run_channel(self, parsers, prompt, candidate):
        """Run a channel of parsers. Returns (score, n_fired)."""
        total, n = 0.0, 0
        for fn in parsers:
            try:
                s, m = fn(prompt, candidate)
                if m:
                    total += s
                    n += 1
            except Exception:
                pass
        return (total / n if n > 0 else 0.0), n

    def _adaptive_weights(self, prompt):
        """Adaptive control: adjust channel weights based on prompt structure."""
        pl = prompt.lower()
        w_a, w_b, w_c = 1.0, 1.0, 1.0
        # Boost numeric channel if numbers present
        if _nums(prompt):
            w_b += 0.5
        # Boost logical channel if conditionals present
        if _has(pl, "if ", "then", "therefore", "implies", "all ", "every"):
            w_c += 0.5
        # Boost structural if SVO or trick question markers
        if _has(pl, "pound of", "overtake", "pass", "chased", "who was"):
            w_a += 0.5
        # Normalize
        total = w_a + w_b + w_c
        return w_a / total, w_b / total, w_c / total

    def _error_correct(self, scores, n_fired):
        """Error correction: 2-of-3 majority vote among channels.
        If 2 channels agree on sign, override the third."""
        signs = []
        for s, n in zip(scores, n_fired):
            if n > 0:
                signs.append(1 if s > 0 else (-1 if s < 0 else 0))
            else:
                signs.append(0)
        # Count active channels
        active = [(s, n, sign) for s, n, sign in zip(scores, n_fired, signs) if n > 0]
        if len(active) >= 2:
            pos = sum(1 for _, _, sign in active if sign > 0)
            neg = sum(1 for _, _, sign in active if sign < 0)
            if pos >= 2:
                # Override any negative channel
                corrected = [abs(s) if sign < 0 else s for s, n, sign in zip(scores, n_fired, signs)]
                return corrected
            elif neg >= 2:
                corrected = [-abs(s) if sign > 0 else s for s, n, sign in zip(scores, n_fired, signs)]
                return corrected
        return scores

    def _functorial_map(self, prompt, candidate):
        """Category theory: map problem to canonical form, then evaluate."""
        # The functor maps prompt+candidate -> (channel_scores, weights)
        sa, na = self._run_channel(self.CHANNEL_A, prompt, candidate)
        sb, nb = self._run_channel(self.CHANNEL_B, prompt, candidate)
        sc, nc = self._run_channel(self.CHANNEL_C, prompt, candidate)
        raw_scores = [sa, sb, sc]
        n_fired = [na, nb, nc]
        # Error correction
        corrected = self._error_correct(raw_scores, n_fired)
        # Adaptive weights
        wa, wb, wc = self._adaptive_weights(prompt)
        weights = [wa, wb, wc]
        # Weighted combination
        weighted_sum = sum(s * w for s, w in zip(corrected, weights))
        total_fired = sum(n_fired)
        return weighted_sum, total_fired

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        raw_scores = []
        for cand in candidates:
            score, n_fired = self._functorial_map(prompt, cand)
            raw_scores.append(score)
            results.append({"candidate": cand, "score": 0.0, "_n_fired": n_fired})

        # If parsers fired, use Bayesian update to convert to [0,1]
        any_fired = any(r["_n_fired"] > 0 for r in results)
        if any_fired:
            for i, cand in enumerate(candidates):
                s = raw_scores[i]
                likelihood = max(0.01, min(0.99, (s + 1) / 2))
                posterior = bayesian_update(0.5, likelihood, 1 - likelihood)
                results[i]["score"] = float(posterior)
        else:
            # No parsers fired: uniform (MaxEnt default)
            for r in results:
                r["score"] = 1.0 / len(candidates)

        # Cross-check via confidence_from_agreement
        all_scores = [r["score"] for r in results]
        agreement = confidence_from_agreement(all_scores)
        # If low agreement and entropy is high, nudge toward max-scoring
        if agreement < 0.5 and len(candidates) > 1:
            probs = [max(0.01, s) for s in all_scores]
            total_p = sum(probs)
            probs = [p / total_p for p in probs]
            h = entropy(probs)
            max_h = math.log2(len(candidates))
            if max_h > 0 and h / max_h > 0.9:
                # Near-uniform -> amplify differences
                best_idx = all_scores.index(max(all_scores))
                for i in range(len(results)):
                    if i == best_idx:
                        results[i]["score"] = min(1.0, results[i]["score"] + 0.05)

        # Clean up internal fields
        for r in results:
            r.pop("_n_fired", None)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _meta_confidence(self, prompt, answer):
        """Detect ambiguity and insufficiency."""
        score, n_fired = self._functorial_map(prompt, answer)
        if n_fired == 0:
            return 0.35  # no parser signal = low confidence
        # Cross-channel agreement as confidence
        sa, na = self._run_channel(self.CHANNEL_A, prompt, answer)
        sb, nb = self._run_channel(self.CHANNEL_B, prompt, answer)
        sc, nc = self._run_channel(self.CHANNEL_C, prompt, answer)
        active = [s for s, n in [(sa, na), (sb, nb), (sc, nc)] if n > 0]
        if active:
            return confidence_from_agreement([(s + 1) / 2 for s in active])
        return 0.35

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
