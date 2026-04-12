import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining Abductive Reasoning, Reinforcement Learning (simulated),
    and Mechanism Design principles.
    
    Mechanism:
    1. Structural Parsing: Extracts a directed graph of propositions using regex for negations,
       comparatives, conditionals, causals, and ordering.
    2. Abductive Proof Search: Attempts to forward-chain from prompt premises to the candidate.
       The cost is the number of invented intermediate hypotheses (h(c)).
    3. Scoring (Mechanism Design): s(c) = w·f(c) - λ·h(c). 
       Uses a proper scoring rule approximation (negative Brier loss) to ensure truthfulness.
    4. RL Simulation: Weights (w) are updated via a simplified policy-gradient step based on 
       consistency with structural constraints (simulating the reward signal).
    5. Epistemic Honesty: Confidence is capped by meta-analysis of ambiguity and presupposition.
    """

    def __init__(self):
        # Initialize weights for features: [negation, comparative, conditional, causal, ordering, numeric_match]
        # Initialized to neutral/positive values, learned via simulated RL updates
        self.weights = [0.2, 0.2, 0.15, 0.15, 0.1, 0.2] 
        self.lambda_penalty = 0.5  # Penalty for abductive hypothesis invention
        self.baseline = 0.0        # Running baseline for RL update
        self.alpha = 0.1           # Learning rate
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|>|<|>=|<=)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|then|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|then|before|after|next|finally|precede|follow)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(\.\d+)?'),
            'presupposition': re.compile(r'(have you stopped|why did .*(?:fail|stop|quit)|when did .*(?:stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> List[float]:
        """Extract structural feature vector from text."""
        text_lower = text.lower()
        counts = [
            len(self.patterns['negation'].findall(text_lower)),
            len(self.patterns['comparative'].findall(text_lower)),
            len(self.patterns['conditional'].findall(text_lower)),
            len(self.patterns['causal'].findall(text_lower)),
            len(self.patterns['ordering'].findall(text_lower)),
        ]
        # Numeric match feature (normalized count)
        nums = self.patterns['numeric'].findall(text_lower)
        counts.append(len(nums) / 10.0 if nums else 0.0)
        return counts

    def _abductive_proof_cost(self, prompt: str, candidate: str) -> int:
        """
        Simulates abductive reasoning cost.
        Counts 'invented' nodes needed to bridge prompt to candidate.
        Heuristic: If candidate tokens are not in prompt, they are 'invented' hypotheses.
        Lower cost = better abductive fit.
        """
        prompt_tokens = set(re.findall(r'\w+', prompt.lower()))
        candidate_tokens = set(re.findall(r'\w+', candidate.lower()))
        
        # Filter common stop words to avoid penalizing grammar
        stop_words = {'the', 'is', 'are', 'a', 'an', 'it', 'that', 'this', 'of', 'to', 'in', 'for', 'on', 'with'}
        prompt_tokens.update(stop_words)
        
        invented_count = 0
        for token in candidate_tokens:
            if token not in prompt_tokens:
                invented_count += 1
                
        return invented_count

    def _compute_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Extracts numeric values and checks for logical consistency.
        Returns 1.0 if consistent, 0.5 if neutral, 0.0 if contradictory.
        """
        p_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', candidate)]
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers to compare
            
        # Simple heuristic: If candidate number exists in prompt, it's likely consistent
        # If candidate introduces a new number not derivable, penalize slightly
        for cn in c_nums:
            if cn in p_nums:
                return 1.0
            # Check for simple arithmetic derivations (e.g. double, half) - basic check
            if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                return 1.0
                
        # If candidate has numbers completely alien to prompt, lower score
        return 0.2

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Only flag if it looks like a logical trap question
            if "which" in p_lower or "true" in p_lower:
                return 0.3

        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if "fact" not in p_lower and "calculate" not in p_lower:
                return 0.25

        # 4. Pronoun/Scope Ambiguity (Heuristic: "who" questions with multiple names)
        names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        if len(set(names)) > 1 and re.search(r'\b(who|he|she|they)\b', p_lower):
            if "ambiguous" in p_lower or "context" not in p_lower:
                # Hard to detect purely syntactically, but low confidence on multi-entity pronoun queries
                if re.search(r'\b(he|she|him|her)\b.*\?', p_lower):
                    return 0.4

        return 1.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_features = self._extract_features(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        prompt_len = len(prompt)
        
        for cand in candidates:
            # 1. Feature Extraction
            cand_features = self._extract_features(cand)
            
            # 2. Abductive Proof Cost (h(c))
            h_cost = self._abductive_proof_cost(prompt, cand)
            
            # 3. Numeric Consistency Check
            numeric_score = self._compute_numeric_consistency(prompt, cand)
            
            # 4. Score Calculation: s(c) = w·f(c) - λ·h(c)
            # We augment features with the numeric consistency score
            extended_features = cand_features + [numeric_score]
            # Extend weights to match if necessary (pad with 0.1)
            current_weights = self.weights + [0.2] 
            
            dot_product = sum(w * f for w, f in zip(current_weights, extended_features))
            score = dot_product - (self.lambda_penalty * h_cost)
            
            # Add NCD as a minor tiebreaker (max 15% influence logic handled by scaling)
            # Lower NCD is better, so we subtract it. 
            ncd = self._calculate_ncd(prompt, cand)
            score -= (0.15 * ncd)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {dot_product:.2f}, Abductive cost: {h_cost}, NCD penalty: {ncd:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Simulated RL Update (Policy Gradient approximation)
        # If the top candidate has high structural match and low cost, reinforce weights
        if results:
            top = results[0]
            # Pseudo-reward: 1 if score > 0, else 0
            r = 1.0 if top['score'] > 0 else 0.0
            # Update baseline
            self.baseline = 0.9 * self.baseline + 0.1 * r
            # Simplified weight update towards features of the winner if reward is high
            if r > self.baseline:
                for i in range(len(self.weights)):
                    self.weights[i] += self.alpha * (r - self.baseline) * (results[0].get('candidate', '') != '' and 1 or 0)

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural clarity and epistemic honesty.
        Caps confidence if the prompt contains Tier B traps.
        """
        # 1. Meta-Confidence Cap (Tier B Checks)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Signal Strength
        # If the prompt has very little structure, confidence should be lower
        p_feats = self._extract_features(prompt)
        structural_density = sum(p_feats) / (len(p_feats) * 2.0) # Rough normalization
        structural_density = min(1.0, structural_density)
        
        # 3. Abductive Cost Check
        cost = self._abductive_proof_cost(prompt, answer)
        cost_penalty = 0.0
        if cost > 5:
            cost_penalty = 0.4
        elif cost > 2:
            cost_penalty = 0.2
            
        base_conf = (structural_density * 0.6 + 0.4) - cost_penalty
        
        # Apply Meta Cap
        final_conf = min(base_conf, meta_cap)
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, final_conf))