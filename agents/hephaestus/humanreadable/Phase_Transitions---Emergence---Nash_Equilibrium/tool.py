import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Criticality-Driven Emergent Equilibrium Learner (CEEL) Approximation.
    
    Mechanism:
    1. Agents (Candidates): Each candidate is an agent holding a hypothesis.
    2. Potential Game (Payoff): Payoff is derived from structural alignment with the prompt
       (negations, comparatives, numeric logic) rather than semantic similarity.
    3. Order Parameter (Entropy): Measures the diversity of the candidate pool's structural scores.
    4. Phase Transition: If entropy indicates a "frozen" state (low diversity/high consensus on wrong logic)
       or "chaos" (no consensus), the system triggers a reconfiguration:
       - Increases weight of structural constraints (Modus Tollens, Numeric checks).
       - Penalizes simple NCD-only matches to escape local minima.
    5. Equilibrium: Candidates are re-ranked based on the hybrid score of structural validity 
       and compressed consensus, simulating a shift to a higher-order consensus.
    """

    def __init__(self):
        self.critical_threshold = 0.85  # Entropy threshold for phase transition
        self.exploration_factor = 0.3   # Weight for novelty/diversity during criticality

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical structures: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|none|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for logic checks
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums if n]
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Scores candidate based on structural logic consistency with prompt.
        Returns a score 0.0 to 1.0.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.5  # Base prior
        
        # 1. Negation Consistency (Modus Tollens approximation)
        # If prompt has strong negation, candidate should reflect it or explicitly counter it
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0:
                score += 0.2
            else:
                # Penalty for ignoring negation unless candidate is very short (e.g., "No")
                if c_feat['length'] > 10: 
                    score -= 0.3
        
        # 2. Numeric Logic
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if candidate numbers are consistent with prompt logic (simplified)
            # E.g., if prompt asks for max, candidate should contain larger numbers
            p_max = max(p_feat['numbers'])
            c_max = max(c_feat['numbers'])
            if 'max' in prompt.lower() or 'largest' in prompt.lower():
                if c_max >= p_max:
                    score += 0.2
                else:
                    score -= 0.2
            elif 'min' in prompt.lower() or 'smallest' in prompt.lower():
                if c_max <= p_max:
                    score += 0.2
            
        # 3. Comparative Alignment
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0:
                score += 0.15
            elif c_feat['numbers']:
                score += 0.1 # Numbers often satisfy comparatives
        
        # 4. Conditional/Length Heuristic (Avoiding echo)
        if p_feat['conditionals'] > 0 and c_feat['conditionals'] == 0:
            if c_feat['length'] < 20: # Short answers might be valid conclusions
                pass
            else:
                score -= 0.1 # Long answers ignoring conditionals are suspect

        return max(0.0, min(1.0, score))

    def _calculate_entropy(self, scores: List[float]) -> float:
        """Calculates normalized entropy of the score distribution."""
        if not scores or sum(scores) == 0:
            return 0.0
        total = sum(scores)
        probs = [s / total for s in scores if s > 0]
        if not probs:
            return 0.0
        entropy = -sum(p * math.log2(p) for p in probs)
        max_entropy = math.log2(len(probs)) if len(probs) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Layer 1: Initial Belief Distribution (Structural + NCD)
        agents = []
        for cand in candidates:
            logic_score = self._evaluate_logic(prompt, cand)
            # NCD as a baseline similarity measure (inverse distance)
            ncd = self._compute_ncd(prompt, cand)
            # Initial belief: weighted mix, favoring logic
            belief = 0.7 * logic_score + 0.3 * (1.0 - ncd)
            agents.append({
                'candidate': cand,
                'belief': belief,
                'logic_score': logic_score,
                'ncd': ncd
            })
        
        # Layer 2: Order Parameter Calculation (Entropy of beliefs)
        beliefs = [a['belief'] for a in agents]
        entropy = self._calculate_entropy(beliefs)
        
        # Layer 3: Phase Transition & Reconfiguration
        # If entropy is too low (frozen consensus) or too high (chaos), trigger reconfiguration
        # Here we simulate the "Critical Point" by boosting structural rigor if consensus is weak
        # or if the top candidate has low logic score.
        
        sorted_agents = sorted(agents, key=lambda x: x['belief'], reverse=True)
        top_agent = sorted_agents[0]
        
        # Criticality Check: If the best answer isn't logically strong, force exploration
        if top_agent['logic_score'] < 0.6 or entropy < 0.3:
            # Reconfiguration: Increase exploration rate
            # Reweight agents: Penalize high NCD (echoing) and boost structural logic
            for agent in agents:
                # New payoff function emphasizing logic over similarity
                new_payoff = 0.9 * agent['logic_score'] + 0.1 * (1.0 - agent['ncd'])
                
                # Inject novelty bonus for diverse structural features (simplified)
                if agent['logic_score'] > 0.5 and agent['ncd'] > 0.5:
                    new_payoff += self.exploration_factor
                
                agent['belief'] = min(1.0, new_payoff)
                agent['reasoning'] = "Criticality triggered: Structural logic prioritized over similarity."
        else:
            for agent in agents:
                agent['reasoning'] = "Stable equilibrium: Consensus aligned with structural logic."

        # Final Ranking (Nash Equilibrium State)
        final_ranking = sorted(agents, key=lambda x: x['belief'], reverse=True)
        
        result = []
        for agent in final_ranking:
            result.append({
                "candidate": agent['candidate'],
                "score": round(agent['belief'], 4),
                "reasoning": agent['reasoning']
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment and compression."""
        logic_score = self._evaluate_logic(prompt, answer)
        ncd = self._compute_ncd(prompt, answer)
        
        # Confidence is high if logic is strong AND (answer is concise OR highly relevant via NCD)
        # If logic is weak, confidence drops regardless of NCD
        base_conf = 0.6 * logic_score + 0.4 * (1.0 - ncd)
        
        # Penalty for contradictions detected by structure
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        if p_feat['negations'] > 0 and a_feat['negations'] == 0 and a_feat['length'] > 10:
            base_conf *= 0.5
            
        return max(0.0, min(1.0, base_conf))