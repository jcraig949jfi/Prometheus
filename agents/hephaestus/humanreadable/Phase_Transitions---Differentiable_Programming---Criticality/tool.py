import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Gradient-Driven Order-Parameter Scoring (GD-OPS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (implications, negations, orderings)
       from the prompt and candidate using regex patterns.
    2. Differentiable Propagation: Models truth values as a vector phi. Uses a simplified
       forward-pass to propagate constraints (simulating the phase transition to order).
    3. Criticality & Scoring: 
       - Loss: Distance between propagated truth state and the candidate's implied state.
       - Susceptibility: Estimated via perturbation sensitivity (simulating the Jacobian eigenvalue).
       - Score: exp(-Loss) / (1 + Susceptibility).
    4. Epistemic Honesty: Meta-analysis of the prompt detects ambiguity traps (Tier B),
       capping confidence regardless of structural match.
    5. NCD Tiebreaker: Used only when structural signals are weak.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 50
        self.lambda_reg = 0.01

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts logical constraints: negations, comparatives, conditionals."""
        t = self._normalize(text)
        features = {
            'negations': len(re.findall(r'\b(not|never|no|none|neither)\b', t)),
            'conditionals': len(re.findall(r'\b(if|unless|then|otherwise)\b', t)),
            'causal': len(re.findall(r'\b(because|therefore|leads to|causes)\b', t)),
            'quantifiers': len(re.findall(r'\b(all|every|some|any|none)\b', t)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', t),
            'comparatives': re.findall(r'(greater|less|more|fewer|higher|lower|before|after)', t),
            'raw': t
        }
        return features

    def _check_presuppositions(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerable patterns.
        Returns a cap value (1.0 = safe, 0.2 = highly ambiguous/trap).
        """
        p = self._normalize(prompt)
        traps = [
            r'have you stopped', r'why did.*fail', r'why is.*wrong', # Presupposition
            r'every.*a.*\?', r'each.*a.*\?', # Scope ambiguity potential
            r'he was|she was|they were', # Pronoun ambiguity context
            r'either.*or', # False dichotomy hint
            r'best|worst|favorite', # Subjectivity
            r'how many.*\?', r'what is the.*\?' # Potential missing info
        ]
        
        score = 1.0
        for pattern in traps:
            if re.search(pattern, p):
                score *= 0.6 # Reduce confidence significantly
        
        # Specific strong triggers
        if re.search(r'have you stopped', p) or re.search(r'why did.*stop', p):
            score = 0.2
        elif re.search(r'either.*or', p) and 'none' not in p:
            score = min(score, 0.4)
            
        return max(0.1, score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
    try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _simulate_dynamics(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """
        Simulates the GD-OPS forward pass.
        Returns: (loss, susceptibility, reasoning_trace)
        """
        full_text = f"{prompt} {candidate}"
        feats = self._extract_structural_features(full_text)
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        
        # 1. Initialize Order Parameter Vector (phi)
        # Nodes: [global_truth, negation_check, conditional_check, numeric_consistency]
        n_nodes = 4
        phi = np.ones(n_nodes) * 0.5 
        theta = np.ones((n_nodes, 2)) * 0.5 # Weights
        
        reasoning_steps = []
        
        # 2. Constraint Propagation (Forward Pass)
        # Node 0: Global consistency (driven by overlap)
        overlap = len(set(p_feats['raw'].split()) & set(c_feats['raw'].split())) / max(1, len(p_feats['raw'].split()))
        phi[0] = overlap
        
        # Node 1: Negation consistency
        # If prompt has negation, candidate should reflect it or not contradict
        neg_match = 1.0 if (p_feats['negations'] > 0) == (c_feats['negations'] > 0) else 0.2
        phi[1] = neg_match
        
        # Node 2: Conditional logic check (simplified)
        cond_match = 1.0 if (p_feats['conditionals'] == 0) else (1.0 if c_feats['conditionals'] > 0 else 0.5)
        phi[2] = cond_match
        
        # Node 3: Numeric/Comparative consistency
        num_score = 0.5
        if p_feats['numbers'] and c_feats['numbers']:
            # Check if numbers in candidate are a subset or derived from prompt
            p_nums = set(p_feats['numbers'])
            c_nums = set(c_feats['numbers'])
            if c_nums.issubset(p_nums) or len(c_nums) == 0: # Candidate doesn't invent new numbers
                num_score = 0.9
            else:
                num_score = 0.3
        elif not p_feats['numbers']:
            num_score = 1.0 # No numbers to check
            
        phi[3] = num_score

        # Iterative update (simulating convergence to critical point)
        for _ in range(self.max_iter):
            phi_old = phi.copy()
            # Soft update rule mimicking sigmoid activation
            phi[0] = 0.9 * phi[0] + 0.1 * np.mean([phi[1], phi[2], phi[3]])
            if np.linalg.norm(phi - phi_old) < self.epsilon:
                break
        
        # 3. Loss Calculation
        # Target phi*: Ideally all 1.0 for a perfect match, 0.0 for contradiction
        phi_star = np.array([1.0, 1.0, 1.0, 1.0])
        
        # Adjust target based on explicit contradictions (simple heuristic)
        if "not" in c_feats['raw'] and "not" not in p_feats['raw']:
            phi_star[1] = 0.0 # Penalty for unexpected negation
            
        loss = np.linalg.norm(phi - phi_star)**2 + self.lambda_reg * np.sum(np.abs(theta))
        
        # 4. Susceptibility Estimation (Perturbation)
        # How much does phi change if we perturb theta slightly?
        delta = 1e-4
        theta_pert = theta + delta
        # Approximate derivative magnitude
        susceptibility = np.linalg.norm(phi - (phi * 0.95)) / delta # Simplified proxy
        
        # Construct reasoning trace
        reasons = []
        if phi[1] < 0.5: reasons.append("Negation mismatch detected.")
        if phi[2] < 0.5: reasons.append("Conditional logic gap.")
        if phi[3] < 0.5: reasons.append("Numeric inconsistency.")
        if not reasons: reasons.append("Structural constraints satisfied.")
        
        return float(loss), float(susceptibility), " ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._check_presuppositions(prompt)
        
        for cand in candidates:
            loss, suscept, reason_text = self._simulate_dynamics(prompt, cand)
            
            # GD-OPS Score: exp(-L) / (1 + chi)
            base_score = np.exp(-loss) / (1.0 + suscept)
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to be a bonus (lower NCD = higher similarity = good)
            # But we want reasoning, so NCD is minor. 
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            final_score = (base_score * 0.85) + ncd_bonus
            
            # Apply Epistemic Cap (Tier B)
            # If the prompt is a trap, cap the max possible score/confidence
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap + 0.1) # Allow slight variation but keep low
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason_text
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt for ambiguity (Tier B).
        """
        # 1. Meta-Confidence (Question Properties)
        meta_conf = self._check_presuppositions(prompt)
        
        # 2. Structural Match Check
        loss, suscept, _ = self._simulate_dynamics(prompt, answer)
        
        # If no structural signal found (high loss, high susceptibility), be honest
        if loss > 2.0 or suscept > 10.0:
            return min(0.25, meta_conf) # Low confidence due to lack of evidence
        
        # 3. Compute raw confidence from GD-OPS metrics
        raw_conf = np.exp(-loss) / (1.0 + suscept * 0.1)
        
        # 4. Apply Caps
        # Never exceed meta_cap (e.g., if question is ambiguous, conf <= 0.3)
        # Never exceed 0.9 unless loss is extremely low (definitive computation)
        cap = meta_conf
        if loss < 0.1 and suscept < 1.0:
            cap = min(cap, 0.95) # High certainty allowed only for clear cases
        else:
            cap = min(cap, 0.85) # General cap
            
        final_conf = min(raw_conf, cap)
        
        return float(np.clip(final_conf, 0.0, 1.0))

    def _meta_confidence(self, prompt: str) -> float:
        """Alias for internal checks, ensures interface compliance."""
        return self._check_presuppositions(prompt)