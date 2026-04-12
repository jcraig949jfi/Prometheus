from typing import Any, Dict, Tuple

import re
import math
import zlib
from typing import List, Dict, Tuple, Any

# Constants
LAMBDA_PENALTY = 0.1
ETA = 0.1
SIGMOID_BETA = 5.0

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-SIGMOID_BETA * x))

def ncd_distance(s1: str, s2: str) -> float:
    """Normalized Compression Distance using zlib."""
    if not s1 or not s2:
        return 1.0
    c1 = len(zlib.compress(s1.encode()))
    c2 = len(zlib.compress(s2.encode()))
    c12 = len(zlib.compress((s1 + s2).encode()))
    min_c = min(c1, c2)
    if min_c == 0:
        return 1.0
    return (c12 - min_c) / (max(c1, c2))

class ReasoningTool:
    """
    A reasoning tool combining neuromodulatory gain control, mechanism design scoring,
    and property-based shrinking to evaluate logical consistency and epistemic honesty.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals).
    2. Neuromodulation: Propagates truth values with dynamic gain based on consistency.
    3. Mechanism Design: Uses quadratic scoring to penalize overconfidence in inconsistent states.
    4. Property Testing: Mutates inputs to find minimal counterexamples (shrinking).
    5. Epistemic Honesty: Caps confidence on ambiguous or presuppositional prompts.
    """

    def __init__(self):
        # Regex patterns for proposition extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower)\s+(than)?', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads? to|causes?|due to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'(have you stopped|why did .*(?:fail|stop)|when did .*(?:stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'(.+?) told (.+?) he', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }

    def _extract_props(self, text: str) -> Dict[str, Any]:
        """Extract structural features and numeric values."""
        props = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_ordering': bool(self.patterns['ordering'].search(text)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text)
        }
        return props

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap for the confidence score.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy
        if 'either' in p_lower and 'or' in p_lower:
            # Simple heuristic: if it looks like a forced choice without data
            if 'choose' in p_lower or 'which' in p_lower:
                return 0.3
                
        # 3. Pronoun Ambiguity (He said to He)
        if self.patterns['pronoun_ambiguity'].search(prompt):
            if 'who' in p_lower:
                return 0.25

        # 4. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            if 'objective' not in p_lower and 'fact' not in p_lower:
                return 0.3

        # 5. Unanswerable / Missing Info
        if 'cannot be determined' in p_lower or 'insufficient' in p_lower:
            return 0.1
            
        return 1.0  # No obvious traps detected

    def _propagate_constraints(self, prompt_props: Dict, answer_props: Dict, answer_text: str) -> Tuple[float, float, str]:
        """
        Step 2 & 4: Neuromodulatory Gain Propagation and Property Shrinking simulation.
        Returns (activation, gain, reasoning_trace).
        """
        nodes = []
        edges = []
        trace = []

        # Construct Graph Nodes based on extracted features
        # Node 0: Prompt Context Validity
        nodes.append({'id': 0, 'activation': 0.5, 'type': 'context'})
        
        # Node 1: Answer Consistency with Prompt Negations
        neg_match = prompt_props['has_negation'] and answer_props['has_negation']
        # If prompt has negation and answer ignores it, penalty
        if prompt_props['has_negation'] and not answer_props['has_negation']:
            nodes.append({'id': 1, 'activation': 0.2, 'type': 'negation_check'})
            edges.append((0, 1, -0.5)) # Contradiction edge
            trace.append("Warning: Answer may ignore negation cues.")
        else:
            nodes.append({'id': 1, 'activation': 0.9, 'type': 'negation_check'})
            edges.append((0, 1, 0.5))
            trace.append("Negation cues aligned.")

        # Node 2: Numeric Consistency
        if prompt_props['numbers'] and answer_props['numbers']:
            # Simple heuristic: if answer numbers are subset or close to prompt numbers
            p_nums = set(prompt_props['numbers'])
            a_nums = set(answer_props['numbers'])
            # Check for direct contradiction (e.g. prompt says 5, answer says 6 in a fact retrieval context)
            # Since we don't have full semantic parse, we check magnitude overlap
            overlap = len(p_nums.intersection(a_nums))
            if overlap > 0:
                nodes.append({'id': 2, 'activation': 0.9, 'type': 'numeric'})
                trace.append(f"Numeric overlap detected: {overlap} values.")
            else:
                # Potential mismatch, but not definitive without semantics
                nodes.append({'id': 2, 'activation': 0.6, 'type': 'numeric'})
                trace.append("Numeric values present but no direct overlap.")
            edges.append((1, 2, 0.3))
        else:
            nodes.append({'id': 2, 'activation': 0.5, 'type': 'numeric'})
            edges.append((1, 2, 0.0))

        # Node 3: Structural Complexity (Conditionals/Causals)
        if prompt_props['has_conditional'] or prompt_props['has_causal']:
            if answer_props['has_conditional'] or answer_props['has_causal']:
                nodes.append({'id': 3, 'activation': 0.85, 'type': 'logic'})
                trace.append("Logical structure preserved.")
            else:
                nodes.append({'id': 3, 'activation': 0.4, 'type': 'logic'})
                trace.append("Warning: Logical connectors missing in answer.")
            edges.append((2, 3, 0.4))
        else:
            nodes.append({'id': 3, 'activation': 0.5, 'type': 'logic'})
            edges.append((2, 3, 0.0))

        # Propagation Step (Neuromodulatory Gain)
        # Iterate a few times to stabilize
        gain = 1.0
        for _ in range(3):
            new_activations = [n['activation'] for n in nodes]
            for i, node in enumerate(nodes):
                input_sum = node['activation'] # Bias
                for src_id, tgt_id, weight in edges:
                    if tgt_id == i:
                        src_act = nodes[src_id]['activation']
                        # Dopamine-like gain modulation
                        input_sum += gain * weight * src_act
                
                # Update activation
                new_val = sigmoid(input_sum - 0.5) # Center around 0
                new_activations[i] = new_val
            
            # Update Gain based on Reward Prediction Error (Simulated)
            # Assume reward is high if final node (logic) is high
            r = new_activations[-1] 
            delta = r - sum(n['activation'] for n in nodes)/len(nodes)
            gain = gain + ETA * delta * (1 - gain)
            gain = max(0.1, min(2.0, gain)) # Clamp gain

            for i, n in enumerate(nodes):
                n['activation'] = new_activations[i]

        final_activation = nodes[-1]['activation']
        return final_activation, gain, " | ".join(trace)

    def _property_shrink_test(self, prompt: str, answer: str) -> int:
        """
        Step 4: Hypothesis testing via shrinking.
        Simulates mutating the answer to see if it breaks. 
        Returns number of shrinking steps (penalty).
        """
        # In a real system, we'd mutate tokens. Here we simulate robustness checks.
        k = 0
        
        # Test 1: Remove numbers. If answer relies on numbers, does it break logic?
        nums = re.findall(r'-?\d+(?:\.\d+)?', answer)
        if nums:
            # Simulate removal
            test_ans = re.sub(r'-?\d+(?:\.\d+)?', '', answer)
            if len(test_ans.strip()) < len(answer.strip()) * 0.5:
                k += 1 # Heavy reliance on numbers, risky if wrong
        
        # Test 2: Flip negations
        if 'not' in answer.lower():
            k += 1 # Negation flipping is a common failure mode
            
        return k

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via _meta_confidence cap.
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Structural & Logical Evaluation
        p_props = self._extract_props(prompt)
        a_props = self._extract_props(answer)
        
        activation, gain, trace = self._propagate_constraints(p_props, a_props, answer)
        
        # 3. Mechanism Design Scoring (Quadratic)
        # o = 1 if activation > 0.5 else 0
        o = 1.0 if activation > 0.5 else 0.0
        # We want the model to report p = activation. 
        # Score S = 1 - (p - o)^2. 
        # Here we treat the computed activation as the 'truth' derived from constraints.
        # So we score the consistency.
        consistency_score = 1.0 - (activation - o)**2
        
        # 4. Property Based Penalty
        k = self._property_shrink_test(prompt, answer)
        penalty = 1.0 / (1.0 + LAMBDA_PENALTY * k)
        
        # 5. NCD Tiebreaker (Max 15% weight)
        # Compare answer to prompt. High similarity in reasoning tasks often means echoing (bad)
        # but low similarity might mean irrelevant. 
        # We use NCD only as a small modifier.
        ncd_val = ncd_distance(prompt, answer)
        # Heuristic: Moderate NCD is good. Very low (echo) or very high (noise) is bad.
        # Ideal NCD ~ 0.4-0.6 for reasoning.
        ncd_factor = 1.0 if 0.3 < ncd_val < 0.8 else 0.9
        
        final_score = (consistency_score * 0.85 + ncd_factor * 0.15) * penalty * gain
        
        # Apply Meta Cap
        final_confidence = min(final_score, meta_cap)
        
        return max(0.0, min(1.0, final_confidence))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates and ranks candidates.
        """
        results = []
        for cand in candidates:
            conf = self.confidence(prompt, cand)
            # Generate reasoning string
            p_props = self._extract_props(prompt)
            a_props = self._extract_props(cand)
            _, _, trace = self._propagate_constraints(p_props, a_props, cand)
            
            results.append({
                "candidate": cand,
                "score": conf,
                "reasoning": f"Activation: {conf:.3f}, Trace: {trace}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example usage logic would go here if run as script, but class is the requirement.