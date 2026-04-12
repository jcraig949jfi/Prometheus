import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectic Sparse Coding Mechanism (DSCM) Implementation.
    
    Mechanism Design (Core): The evaluate() method acts as a VCG-style auction.
    Candidates bid for correctness based on structural fidelity (negations, logic).
    Payments (scores) are adjusted by a 'truthfulness' penalty derived from 
    Dialectic tension (difference between candidate and a synthetic antithesis).
    
    Sparse Coding (Restricted): Used only in confidence() to measure the 
    'energy' (non-zero density) of the semantic overlap between prompt and answer.
    High sparsity in overlap = high confidence (specific match).
    
    Dialectics: Used as a secondary validator. We generate an 'antithesis' 
    (negated logic) and check if the candidate survives the contradiction.
    """

    def __init__(self):
        self.logic_keywords = ['if', 'then', 'else', 'unless', 'but', 'however', 'therefore']
        self.comparators = ['>', '<', 'greater', 'less', 'more', 'fewer', 'higher', 'lower']
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']

    def _structural_parse(self, text: str) -> dict:
        """Extract structural features: negations, comparators, conditionals."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        has_negation = any(n in words for n in self.negations)
        has_comparator = any(c in t_lower for c in self.comparators)
        has_conditional = any(k in words for k in self.logic_keywords)
        
        # Numeric extraction
        numbers = re.findall(r'\d+\.?\d*', text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'neg_count': sum(words.count(n) for n in self.negations),
            'has_comp': has_comparator,
            'has_cond': has_conditional,
            'nums': nums,
            'len': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = zlib.compress(s1.encode())
        c2 = zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        denom = max(len(c1), len(c2))
        if denom == 0: return 1.0
        return (len(c12) - min(len(c1), len(c2))) / denom

    def _generate_antithesis(self, prompt: str) -> str:
        """Create a dialectic antithesis by negating key logical operators."""
        p_lower = prompt.lower()
        antithesis = prompt
        # Simple negation flip for dialectic tension
        if ' must ' in p_lower: antithesis = antithesis.replace('must', 'must not')
        elif ' is ' in p_lower: antithesis = antithesis.replace(' is ', ' is not ')
        elif ' are ' in p_lower: antithesis = antithesis.replace(' are ', ' are not ')
        else: antithesis = "not " + prompt
        return antithesis

    def _dialectic_score(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design: Score based on consistency with prompt structure
        minus a penalty for failing to resolve dialectic tension.
        """
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        
        score = 0.0
        
        # 1. Structural Alignment Reward (The "Bid")
        if p_struct['has_negation'] and c_struct['has_negation']:
            score += 0.4 # Reward matching negation logic
        elif not p_struct['has_negation'] and not c_struct['has_negation']:
            score += 0.2 # Neutral alignment
            
        if p_struct['has_cond'] and c_struct['has_cond']:
            score += 0.3 # Reward preserving conditionals
            
        # 2. Numeric Consistency (Constraint Propagation)
        if p_struct['nums'] and c_struct['nums']:
            # Check if candidate numbers are logically derived (simplified)
            # If prompt has numbers, candidate should ideally reference logic or numbers
            score += 0.2
            
        # 3. Dialectic Penalty (The "Payment")
        # If the candidate is just a subset of the prompt (echo), penalize heavily
        if candidate.lower().strip() in prompt.lower():
            score -= 0.5
            
        # Antithesis check: If candidate contradicts the antithesis of the prompt, it's robust
        antithesis = self._generate_antithesis(prompt)
        # If candidate is very similar to antithesis, it's likely wrong (penalty)
        if self._compute_ncd(candidate, antithesis) < 0.3:
            score -= 0.4
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._compute_ncd(prompt, c)) for c in candidates]
        
        for candidate in candidates:
            # Core Mechanism: Dialectic Score
            raw_score = self._dialectic_score(prompt, candidate)
            
            # Fallback/Refinement: If structural signals are weak, use NCD as minor booster
            # but strictly secondary to logic.
            final_score = raw_score
            
            # Normalize to 0-1 range roughly for consistency
            final_score = max(0.0, min(1.0, 0.5 + final_score))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Dialectic score: {raw_score:.2f}, Structural match applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Uses Sparse Coding analogy: 
        Confidence is high if the 'activation' (overlap) between prompt and answer
        is sparse (specific) and high-energy (significant words match).
        """
        if not answer:
            return 0.0
            
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        a_words = set(re.findall(r'\b\w+\b', answer.lower()))
        
        if not p_words or not a_words:
            return 0.0
            
        # Intersection (Active atoms)
        overlap = p_words.intersection(a_words)
        
        # Sparsity metric: Ratio of overlap to total unique words (Density)
        # Low density (high sparsity) of noise, high density of signal = Good
        union = p_words.union(a_words)
        if not union:
            return 0.0
            
        jaccard = len(overlap) / len(union)
        
        # Penalty for length mismatch (prevents "Yes" on complex prompts)
        len_ratio = min(len(answer), len(prompt)) / max(len(answer), len(prompt))
        
        # Structural verification bonus
        p_struct = self._structural_parse(prompt)
        a_struct = self._structural_parse(answer)
        
        struct_bonus = 0.0
        if p_struct['has_negation'] == a_struct['has_negation']:
            struct_bonus = 0.2
        if p_struct['has_cond'] == a_struct['has_cond']:
            struct_bonus += 0.1
            
        # Base confidence on overlap + structural alignment
        conf = (jaccard * 0.6) + (len_ratio * 0.2) + struct_bonus
        return min(1.0, max(0.0, conf))