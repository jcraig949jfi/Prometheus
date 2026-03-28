import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining Gauge Theory, Predictive Coding, and Hoare Logic.
    
    Mechanism:
    1. Parsing: Extracts logical structures (negation, comparatives, conditionals, causality) 
       into proposition objects using regex.
    2. Hoare Triples: Constructs pre/post-condition pairs to model state transitions.
    3. Predictive Coding: Computes error between believed facts and predicted consequences 
       based on logical independence assumptions.
    4. Gauge Curvature: Detects logical inconsistencies in cycles (e.g., A->B->C vs A->C) 
       by comparing path products.
    5. Scoring: Minimizes a loss function of prediction error and curvature.
    """
    
    def __init__(self):
        self.lambda_curv = 0.1
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>|<|=|equal to)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|else|unless)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }

    def _parse_sentence(self, s: str) -> Dict:
        """Tokenize and extract structural features from a sentence."""
        s_lower = s.lower()
        mods = 0
        features = []
        nums = []
        
        # Bit flags: 1=neg, 2=comp, 4=cond, 8=cause
        if self.patterns['negation'].search(s_lower): mods |= 1
        if self.patterns['comparative'].search(s_lower): mods |= 2
        if self.patterns['conditional'].search(s_lower): mods |= 4
        if self.patterns['causal'].search(s_lower): mods |= 8
        
        # Extract numbers
        num_matches = self.patterns['numbers'].findall(s)
        if num_matches:
            nums = [float(n) for n in num_matches]
            
        return {
            'text': s,
            'mods': mods,
            'nums': nums,
            'has_neg': bool(mods & 1),
            'has_comp': bool(mods & 2),
            'has_cond': bool(mods & 4),
            'has_cause': bool(mods & 8)
        }

    def _build_graph(self, text: str) -> Tuple[List[Dict], np.ndarray]:
        """Parse text into propositions and initialize belief vector."""
        # Split by sentence delimiters
        sentences = re.split(r'[.!?]', text)
        props = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3: continue
            props.append(self._parse_sentence(sent))
        
        n = len(props)
        if n == 0:
            return [], np.array([])
            
        # Initialize beliefs: 0.5 prior, boosted by presence of numeric certainty or lack of negation
        beliefs = np.full(n, 0.5)
        for i, p in enumerate(props):
            boost = 0.0
            if p['nums']: boost += 0.2
            if not p['has_neg']: boost += 0.1
            beliefs[i] = min(1.0, 0.5 + boost)
            
        return props, beliefs

    def _compute_hoare_errors(self, props: List[Dict], beliefs: np.ndarray) -> float:
        """
        Construct Hoare triples and compute predictive coding error.
        Assumption: If A implies B (via conditional or causal), belief(B) should match belief(A).
        """
        if len(props) < 2: return 0.0
        
        error_sum = 0.0
        count = 0
        
        # Simple heuristic: Connect causally/conditionally linked sentences if they share nouns
        # Since we don't have NLP, we approximate links by proximity and keyword presence
        for i in range(len(props) - 1):
            p1, p2 = props[i], props[i+1]
            
            # If p1 is conditional/causal, it predicts p2
            if p1['has_cond'] or p1['has_cause']:
                pred_belief = beliefs[i] # Simplified independence assumption
                actual_belief = beliefs[i+1]
                error_sum += (actual_belief - pred_belief) ** 2
                count += 1
                
            # Numeric consistency check
            if p1['nums'] and p2['nums']:
                # If p1 says "10" and p2 says "5" with "less than", check logic
                # Simplified: If numbers differ significantly, slight penalty unless comparative exists
                if abs(p1['nums'][0] - p2['nums'][0]) > 1.0 and not p1['has_comp'] and not p2['has_comp']:
                    error_sum += 0.1
                    count += 1

        return error_sum / (count + 1) if count > 0 else 0.0

    def _compute_gauge_curvature(self, props: List[Dict], beliefs: np.ndarray) -> float:
        """
        Compute curvature by checking consistency of transitive relations.
        Cycle: A->B, B->C vs A->C.
        """
        if len(props) < 3: return 0.0
        
        curvature_sum = 0.0
        cycles = 0
        
        # Look for triplets where logical flow might exist
        for i in range(len(props) - 2):
            p1, p2, p3 = props[i], props[i+1], props[i+2]
            
            # If all three have causal/conditional markers, check transitivity
            if (p1['has_cause'] or p1['has_cond']) and (p2['has_cause'] or p2['has_cond']):
                # Path belief: b1 * b2
                path_belief = beliefs[i] * beliefs[i+1]
                # Direct belief: b3 (approximating A->C link)
                direct_belief = beliefs[i+2]
                
                curvature_sum += abs(path_belief - direct_belief)
                cycles += 1
                
        return curvature_sum / (cycles + 1) if cycles > 0 else 0.0

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural consistency."""
        full_text = f"{prompt} {candidate}"
        props, beliefs = self._build_graph(full_text)
        
        if len(props) == 0:
            return -10.0 # Penalty for empty
            
        # 1. Predictive Coding Error (Hoare Logic violation)
        E = self._compute_hoare_errors(props, beliefs)
        
        # 2. Gauge Curvature (Logical inconsistency in cycles)
        C = self._compute_gauge_curvature(props, beliefs)
        
        # 3. Structural Bonus: Does the candidate contain necessary structural elements?
        # If prompt has a question mark, candidate should ideally have numbers or specific logic words
        prompt_feat = self._parse_sentence(prompt)
        cand_feat = self._parse_sentence(candidate)
        
        structural_bonus = 0.0
        if prompt_feat['has_comp'] and cand_feat['has_comp']: structural_bonus += 0.5
        if prompt_feat['has_cond'] and cand_feat['has_cond']: structural_bonus += 0.5
        if prompt_feat['nums'] and cand_feat['nums']: 
            # Check numeric match roughly
            if abs(prompt_feat['nums'][0] - cand_feat['nums'][0]) < 0.1:
                structural_bonus += 1.0

        # Score: Lower error/curvature is better. Maximize structural bonus.
        # S = -(E + lambda*C) + bonus
        score = -(E + self.lambda_curv * C) + structural_bonus
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            # Fallback to NCD if structural score is neutral (tie-breaker)
            if abs(score) < 0.01:
                combined = prompt + cand
                comp_len = len(combined) - len(re.sub(r'(.)(?=\1+)', '', combined)) # Simple compression proxy
                score -= comp_len * 0.0001 
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"E={self._compute_hoare_errors(self._build_graph(prompt+cand)[0], self._build_graph(prompt+cand)[1]):.2f}, C={self._compute_gauge_curvature(self._build_graph(prompt+cand)[0], self._build_graph(prompt+cand)[1]):.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        score = self._score_candidate(prompt, answer)
        # Map score to 0-1. 
        # Heuristic: Scores > 0 are good, < -1 are bad.
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid mapping
        return float(np.clip(conf, 0.0, 1.0))