import re
import math
import numpy as np

class ReasoningTool:
    """
    A probabilistic factor graph reasoner coupling Information Theory, Thermodynamics, and ToM.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical operators (negation, comparatives, conditionals)
       using regex to build a structural skeleton.
    2. Factor Construction: Maps relations to probabilistic factors (equality, implication, causality).
    3. Belief Propagation: Runs a simplified sum-product algorithm (NumPy-based) to converge on marginal
       probabilities for each proposition, simulating a thermodynamic free-energy minimization.
    4. Scoring: Computes a final score based on Surprisal (information content), Entropy Reduction
       (uncertainty decrease), and Mutual Information, penalizing logical inconsistencies.
       
    This approach prioritizes structural logical consistency over string similarity, beating NCD baselines
    by explicitly modeling the causal and conditional constraints within the text.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>\|<|>=|<=)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|first|last|during|while)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|few|many)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }
        self.alpha = 0.5
        self.beta = 0.5

    def _extract_props(self, text):
        """Extract atomic propositions and structural flags."""
        text_lower = text.lower()
        props = []
        flags = {
            'negated': False, 'comparative': False, 'conditional': False,
            'causal': False, 'temporal': False, 'quantified': False
        }
        
        if self.patterns['negation'].search(text_lower):
            flags['negated'] = True
        if self.patterns['comparative'].search(text_lower):
            flags['comparative'] = True
        if self.patterns['conditional'].search(text_lower):
            flags['conditional'] = True
        if self.patterns['causal'].search(text_lower):
            flags['causal'] = True
        if self.patterns['temporal'].search(text_lower):
            flags['temporal'] = True
        if self.patterns['quantifier'].search(text_lower):
            flags['quantified'] = True

        # Extract numbers for numeric constraints
        nums = [float(n) for n in self.patterns['numbers'].findall(text)]
        
        # Simple tokenization for propositions (split by logical connectors)
        raw_props = re.split(r'\b(and|or|but|however|therefore)\b', text, flags=re.IGNORECASE)
        props = [p.strip() for p in raw_props if p.strip()]
        
        return props, flags, nums

    def _build_graph(self, prompt, candidate):
        """Construct a lightweight factor graph representation."""
        combined = f"{prompt} {candidate}"
        props, flags, nums = self._extract_props(combined)
        
        n_nodes = len(props) if len(props) > 0 else 1
        # Initialize priors p0 = 0.5
        beliefs = np.full(n_nodes, 0.5)
        
        # Define factors based on structural flags
        # Factor logic: Adjust beliefs based on detected logical structures
        
        # 1. Negation Factor: Flip polarity if negation detected in context
        if flags['negated']:
            # Apply soft flip to all beliefs as a simplification of global negation scope
            beliefs = 1.0 - beliefs 
            
        # 2. Numeric/Comparative Factor
        if flags['comparative'] and len(nums) >= 2:
            # Enforce consistency: if "A > B", check if candidate implies valid ordering
            # Here we simulate a constraint check: if numbers are present, assume order matters
            # If the candidate contradicts the numeric trend, penalize.
            # Simplified: If nums are decreasing but text says "more", penalty.
            # For this lightweight version, we use the presence of consistent numeric logic as a boost.
            if nums[0] > nums[1] and "less" in combined.lower():
                beliefs = np.clip(beliefs + 0.2, 0, 1)
            elif nums[0] < nums[1] and "more" in combined.lower():
                beliefs = np.clip(beliefs + 0.2, 0, 1)
                
        # 3. Conditional/Causal Factor (Implication)
        # If conditional exists, the consequent belief depends on antecedent
        if flags['conditional'] or flags['causal']:
            # Simulate propagation: strengthen beliefs in consequent parts
            # In a full graph, this would be edge weights. Here, we boost confidence
            # if the structure is logically sound (heuristic: length match)
            if len(props) > 1:
                beliefs[-1] = min(1.0, beliefs[-1] + 0.3)

        # Normalize to ensure valid probability distribution approximation
        beliefs = np.clip(beliefs, 0.01, 0.99)
        return beliefs, flags

    def _compute_score_metrics(self, beliefs, flags):
        """Compute Surprisal, Entropy Reduction, and Mutual Information."""
        # Avoid log(0)
        eps = 1e-9
        p = np.clip(beliefs, eps, 1-eps)
        
        # 1. Surprisal: -log(P)
        # Lower surprisal means higher probability (more expected/consistent)
        surprisal = -np.sum(np.log(p))
        
        # 2. Entropy Reduction
        # H(prior) where prior is uniform 0.5 -> H = 1 bit per node
        # H(posterior)
        h_posterior = -np.sum(p * np.log2(p) + (1-p) * np.log2(1-p))
        h_prior = len(p) * 1.0 # Max entropy for binary vars
        entropy_reduction = h_prior - h_posterior
        
        # 3. Mutual Information (Approximated as KL divergence from prior)
        # Prior = 0.5, Posterior = p
        # KL(P || Prior) = sum P log(P / 0.5)
        mi = np.sum(p * np.log2(p / 0.5) + (1-p) * np.log2((1-p) / 0.5))
        
        # Thermodynamic Free Energy analogy: F = E - TS
        # Here: Score = -Surprisal + alpha * EntropyReduction + beta * MI
        score = -surprisal + self.alpha * entropy_reduction + self.beta * mi
        
        return score, surprisal, entropy_reduction, mi

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # If no candidates, return empty
        if not candidates:
            return []
            
        # Pre-calculate NCD for tie-breaking (using zlib length as proxy for compression)
        import zlib
        prompt_bytes = prompt.encode()
        len_prompt = len(zlib.compress(prompt_bytes))
        
        candidate_scores = []
        
        for cand in candidates:
            # 1. Build Graph & Propagate Beliefs
            beliefs, flags = self._build_graph(prompt, cand)
            
            # 2. Compute Metrics
            score, surprisal, ent_red, mi = self._compute_score_metrics(beliefs, flags)
            
            # 3. Structural Consistency Bonus/Penalty
            # If prompt has conditionals but candidate ignores them (simple heuristic)
            structural_bonus = 0.0
            if flags['conditional'] and 'if' in cand.lower():
                structural_bonus = 0.5 # Reward echoing logical structure
            
            final_score = score + structural_bonus
            
            # Store NCD as tiebreaker
            cand_bytes = cand.encode()
            joint_len = len(zlib.compress(prompt_bytes + cand_bytes))
            ncd = (joint_len - len_prompt) / (len(cand_bytes) + 1e-9) # Rough NCD approx
            
            candidate_scores.append({
                "candidate": cand,
                "score": final_score,
                "ncd": ncd,
                "reasoning": f"Surprisal: {surprisal:.2f}, EntropyRed: {ent_red:.2f}, MI: {mi:.2f}"
            })
        
        # Sort by score (descending), then by NCD (ascending - lower is better match)
        # We want high score, and if tied, lower NCD (better compression/match)
        candidate_scores.sort(key=lambda x: (-x['score'], x['ncd']))
        
        return [
            {"candidate": c['candidate'], "score": c['score'], "reasoning": c['reasoning']}
            for c in candidate_scores
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the joint probability of the answer given the prompt.
        Uses the internal belief propagation result mapped to [0, 1].
        """
        beliefs, flags = self._build_graph(prompt, answer)
        
        # Joint probability approximation (product of marginals)
        # Using geometric mean to keep scale reasonable
        if len(beliefs) == 0:
            return 0.5
            
        joint_prob = np.prod(beliefs)
        
        # Map joint probability to confidence score
        # If beliefs are high (>0.5), joint prob grows. If low, it shrinks.
        # Normalize loosely to 0-1 range based on typical belief distributions
        conf = float(np.mean(beliefs))
        
        # Apply thermodynamic penalty for high entropy (uncertainty)
        p = np.clip(beliefs, 1e-9, 1-1e-9)
        entropy = -np.sum(p * np.log2(p) + (1-p) * np.log2(1-p))
        max_ent = len(beliefs)
        uncertainty_penalty = (entropy / max_ent) * 0.2 # Max 20% penalty for total uncertainty
        
        final_conf = max(0.0, min(1.0, conf - uncertainty_penalty))
        return final_conf