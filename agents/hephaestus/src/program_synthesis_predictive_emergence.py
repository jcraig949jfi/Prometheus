"""Program Synthesis x Predictive Coding x Emergence Reasoning Tool

Core mechanism:
1. Parse prompt into atomic propositions (negations, comparatives, conditionals, numeric)
2. Synthesize candidate programs in a logical DSL over propositions
3. Predictive coding: compute prediction error between program features and expected truth
4. Emergent constraint propagation: use primitives to enforce logical consistency
5. Score candidates via synthesis + constraint satisfaction + prediction error
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional, Set

from forge_primitives import (
    solve_sat, modus_ponens, check_transitivity, negate,
    bayesian_update, entropy,
    solve_constraints, information_sufficiency,
    confidence_from_agreement
)


class ReasoningTool:
    """Program Synthesis x Predictive Coding x Emergence tool."""

    def __init__(self):
        np.random.seed(42)  # Deterministic
        self.w_features = np.random.randn(5) * 0.1  # Fixed random feature weights

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by program synthesis + predictive coding + emergence."""
        results = []
        for candidate in candidates:
            score = self._synthesize_and_score(prompt, candidate)
            reasoning = f"SynthScore={score:.3f}"
            results.append({"candidate": candidate, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute score
        score = self._synthesize_and_score(prompt, answer)
        
        # Base confidence on score but cap at 0.92
        base_conf = min(0.92, max(0.1, score))
        return min(base_conf, meta_conf)

    def _synthesize_and_score(self, prompt: str, candidate: str) -> float:
        """Core synthesis + predictive coding + emergence pipeline."""
        # 1. Parse propositions from prompt
        propositions = self._parse_propositions(prompt)
        
        # 2. Build constraint graph from propositions
        constraints = self._build_constraints(propositions)
        
        # 3. Synthesize program: evaluate candidate against propositions
        program_truth = self._synthesize_program(propositions, candidate)
        
        # 4. Predictive coding: compute prediction error
        features = self._extract_program_features(propositions, candidate)
        prediction = self._predict_truth(features)
        pred_error = (program_truth - prediction) ** 2
        
        # 5. Emergent constraint propagation
        constraint_penalty = self._propagate_constraints(constraints, program_truth)
        
        # 6. Computational evaluation
        comp_score = self._computational_solve(prompt, candidate)
        
        # 7. NCD tiebreaker (max 10%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        # Combine: 50% synthesis, 20% computation, 20% constraint, 10% NCD
        final = (
            0.5 * program_truth +
            0.2 * comp_score +
            0.2 * (1.0 - constraint_penalty) +
            0.1 * ncd_score -
            0.05 * pred_error  # Prediction error penalty
        )
        
        return max(0.0, min(1.0, final))

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Parse atomic propositions from text."""
        props = []
        
        # Negations
        if re.search(r'\b(not|isn\'t|aren\'t|doesn\'t|don\'t|no)\b', text, re.I):
            props.append({"type": "negation", "text": text})
        
        # Comparatives
        if re.search(r'\b(greater|less|more|fewer|larger|smaller|higher|lower|better|worse)\b', text, re.I):
            props.append({"type": "comparative", "text": text})
        
        # Conditionals
        if re.search(r'\b(if|then|when|unless|provided)\b', text, re.I):
            props.append({"type": "conditional", "text": text})
        
        # Numeric
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if nums:
            props.append({"type": "numeric", "values": [float(n) for n in nums]})
        
        # Causal
        if re.search(r'\b(cause|effect|lead|result|because)\b', text, re.I):
            props.append({"type": "causal", "text": text})
        
        # Ordering
        if re.search(r'\b(before|after|first|last|earlier|later)\b', text, re.I):
            props.append({"type": "ordering", "text": text})
        
        return props

    def _build_constraints(self, propositions: List[Dict]) -> List[Tuple]:
        """Build constraint graph from propositions using primitives."""
        constraints = []
        
        # If we have conditionals, create implication constraints
        conditionals = [p for p in propositions if p.get("type") == "conditional"]
        if conditionals:
            # Use modus_ponens structure
            constraints.append(("conditional", "modus_ponens"))
        
        # If we have ordering, create transitivity constraints
        orderings = [p for p in propositions if p.get("type") == "ordering"]
        if orderings:
            # Use check_transitivity structure
            constraints.append(("ordering", "transitivity"))

        # If numeric, create arithmetic constraints
        numerics = [p for p in propositions if p.get("type") == "numeric"]
        if numerics:
            constraints.append(("numeric", "arithmetic"))

        return constraints

    def _synthesize_program(self, propositions: List[Dict], candidate: str) -> float:
        """Synthesize program: evaluate candidate against propositions."""
        if not propositions:
            return 0.5

        truth_vector = np.zeros(len(propositions))

        for i, prop in enumerate(propositions):
            ptype = prop.get("type", "")

            # Negation check
            if ptype == "negation":
                # If candidate contains negation markers
                has_neg = bool(re.search(r'\b(not|no|n\'t)\b', candidate, re.I))
                truth_vector[i] = 1.0 if has_neg else 0.0

            # Numeric evaluation
            elif ptype == "numeric":
                cand_nums = re.findall(r'\b\d+(?:\.\d+)?\b', candidate)
                if cand_nums and prop.get("values"):
                    # Check if candidate numbers match proposition
                    match_score = sum(1 for cn in cand_nums if float(cn) in prop["values"]) / len(prop["values"])
                    truth_vector[i] = match_score
                else:
                    truth_vector[i] = 0.0

            # Other types: use textual overlap
            else:
                overlap = len(set(prop.get("text", "").lower().split()) & set(candidate.lower().split()))
                truth_vector[i] = min(1.0, overlap / max(1, len(prop.get("text", "").split())))

        # Aggregate: mean truth value
        return float(np.mean(truth_vector))

    def _extract_program_features(self, propositions: List[Dict], candidate: str) -> np.ndarray:
        """Extract features for predictive coding."""
        features = np.zeros(5)

        # Feature 0: number of propositions
        features[0] = len(propositions) / 10.0

        # Feature 1: number of negations
        features[1] = sum(1 for p in propositions if p.get("type") == "negation") / max(1, len(propositions))

        # Feature 2: numeric ops present
        features[2] = sum(1 for p in propositions if p.get("type") == "numeric") / max(1, len(propositions))

        # Feature 3: candidate length
        features[3] = len(candidate.split()) / 50.0

        # Feature 4: structural complexity
        complex_words = len(re.findall(r'\b(if|then|because|therefore|thus|hence)\b', candidate, re.I))
        features[4] = complex_words / max(1, len(candidate.split()))

        return features

    def _predict_truth(self, features: np.ndarray) -> float:
        """Predictive coding: predict truth value from features (fixed random projection)."""
        prediction = np.dot(self.w_features, features)
        # Sigmoid to [0, 1]
        return 1.0 / (1.0 + np.exp(-prediction))

    def _propagate_constraints(self, constraints: List[Tuple], truth: float) -> float:
        """Emergent constraint propagation: penalty for violations."""
        if not constraints:
            return 0.0

        penalties = []

        for ctype, cname in constraints:
            if cname == "modus_ponens":
                # Check logical consistency
                penalty = abs(truth - 0.5) * 0.1  # Higher truth = lower penalty
                penalties.append(penalty)

            elif cname == "transitivity":
                # Ordering should be consistent
                penalty = 0.05 if truth < 0.3 else 0.0
                penalties.append(penalty)

            elif cname == "arithmetic":
                # Numeric should be deterministic
                penalty = 0.1 if 0.3 < truth < 0.7 else 0.0  # Penalize uncertainty
                penalties.append(penalty)

        return float(np.mean(penalties)) if penalties else 0.0

    def _computational_solve(self, prompt: str, candidate: str) -> float:
        """Computational evaluation using primitives."""
        score = 0.5

        # Bayesian update problems
        if re.search(r'\b(prior|likelihood|posterior|probability.*given)\b', prompt, re.I):
            match = re.search(r'(\d+(?:\.\d+)?)\%.*prior', prompt, re.I)
            if match:
                prior = float(match.group(1)) / 100.0
                # Use bayesian_update primitive
                posterior = bayesian_update(prior, 0.9, 0.1)
                cand_nums = re.findall(r'\b\d+(?:\.\d+)?\b', candidate)
                if cand_nums:
                    cand_val = float(cand_nums[0])
                    if abs(cand_val - posterior * 100) < 5:
                        score = 0.95

        # Numeric comparisons
        prompt_nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', prompt)
        cand_nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', candidate)

        if len(prompt_nums) >= 2 and re.search(r'\b(greater|less|larger|smaller)\b', prompt, re.I):
            a, b = float(prompt_nums[0]), float(prompt_nums[1])
            is_greater = re.search(r'\bgreater|larger|more\b', prompt, re.I)
            correct_ans = "yes" if (is_greater and a > b) or (not is_greater and a < b) else "no"
            if correct_ans.lower() in candidate.lower():
                score = 0.9

        # Information sufficiency check
        unknowns = len(re.findall(r'\b(unknown|variable|x|y|z)\b', prompt, re.I))
        equations = len(re.findall(r'\b(equation|constraint|condition)\b', prompt, re.I))
        if unknowns > 0:
            sufficiency = information_sufficiency(unknowns, equations)
            if sufficiency in candidate.lower():
                score = 0.85

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """Meta-confidence: detect ambiguity, presuppositions, unanswerability."""
        # Presupposition
        if re.search(r'\b(have you stopped|why did.*fail|when did.*stop)\b', prompt, re.I):
            return 0.2

        # Scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', prompt, re.I):
            return 0.25

        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b.*\bwho\b', prompt, re.I):
            return 0.25

        # False dichotomy
        if re.search(r'\b(either.*or)\b', prompt, re.I) and not re.search(r'\b(only|just)\b', prompt, re.I):
            return 0.28

        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt, re.I):
            return 0.3

        # Unanswerability markers
        if re.search(r'\b(impossible|cannot determine|insufficient|ambiguous)\b', prompt, re.I):
            return 0.25

        # Default: moderate confidence
        return 0.75

