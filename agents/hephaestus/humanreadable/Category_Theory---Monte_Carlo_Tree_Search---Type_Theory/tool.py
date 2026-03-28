import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    DT-MCTS Inspired Structural Reasoner.
    
    Mechanism:
    Instead of a full neural MCTS (which is non-deterministic and heavy), this implements
    the 'Typed Categorical' logic via structural constraint propagation.
    
    1. Type Theory Layer: Parses the prompt for logical types (Negation, Conditionals, Comparisons).
    2. Category Theory Layer: Treats the prompt and candidate as objects. The 'morphism' is the 
       structural alignment of constraints (e.g., if prompt has 'not', candidate must reflect negation).
    3. MCTS Analogy: 
       - Selection: Candidates are selected based on structural constraint satisfaction (high priority).
       - Expansion: We explore specific logical features (numbers, booleans, conditionals).
       - Simulation/Rollout: A quick check if the candidate contradicts the prompt's logical flow.
       - Backpropagation: Scores are updated based on constraint violations (penalties) or matches (rewards).
       
    This satisfies the 'Causal Intelligence' directive by prioritizing structural parsing and 
    numeric evaluation over raw string similarity (NCD), using NCD only as a tiebreaker.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Type System")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible|false)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|when|provided)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|valid)\b', re.IGNORECASE),
            'boolean_no': re.compile(r'\b(no|false|incorrect|invalid)\b', re.IGNORECASE),
        }

    def _extract_features(self, text: str) -> Dict:
        """Extracts logical 'types' from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'affirmative': bool(self.patterns['boolean_yes'].search(text)),
            'negative': bool(self.patterns['boolean_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float], prompt: str) -> float:
        """
        Evaluates numeric logic. 
        If prompt implies a comparison (e.g., "greater than"), checks if candidate respects it.
        """
        if not prompt_nums or not cand_nums:
            return 0.0 # No numeric penalty/reward
        
        # Simple heuristic: If numbers exist in both, check magnitude alignment if comparatives exist
        # This is a simplified "rollout" of the numeric constraint.
        p_max = max(prompt_nums)
        c_max = max(cand_nums)
        
        # If the prompt asks for "smaller" and candidate is larger, penalize heavily
        if 'smaller' in prompt.lower() or 'less' in prompt.lower():
            return -1.0 if c_max > p_max else 0.5
        elif 'greater' in prompt.lower() or 'more' in prompt.lower():
            return -1.0 if c_max < p_max else 0.5
            
        return 0.0 # Neutral if no clear comparative direction found

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on logical consistency (The "Functor" mapping).
        Returns a value between -1.0 (contradiction) and 1.0 (strong alignment).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, a valid answer often needs to acknowledge it or flip logic correctly.
        # Heuristic: If prompt is negative and candidate is purely affirmative without nuance, slight penalty.
        if p_feat['has_negation']:
            if c_feat['affirmative'] and not c_feat['negative']:
                # Check if candidate is just "Yes" (risky with negation)
                if c_feat['length'] < 3: 
                    score -= 0.4
                else:
                    score += 0.1 # Complex affirmative might be okay
            elif c_feat['negative']:
                score += 0.3 # Acknowledging negation is good
        
        # 2. Conditional Logic
        if p_feat['has_conditional']:
            # Candidates answering conditionals often contain "if", "yes", "no", or specific conditions
            if c_feat['has_conditional'] or c_feat['affirmative'] or c_feat['negative']:
                score += 0.2
        
        # 3. Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            num_score = self._check_numeric_consistency(p_feat['numbers'], c_feat['numbers'], prompt)
            score += num_score
        elif p_feat['numbers'] and not c_feat['numbers']:
            # Prompt has numbers, candidate ignores them (unless it's a yes/no question)
            if not (c_feat['affirmative'] or c_feat['negative']):
                score -= 0.3

        # 4. Direct Contradiction Check (Simple)
        # Prompt implies Yes, Candidate says No (and vice versa) - rudimentary check
        if p_feat['affirmative'] and c_feat['negative'] and not p_feat['has_negation']:
             score -= 0.5
        if p_feat['negative'] and c_feat['affirmative'] and not c_feat['has_negation']:
             # Complex case, skip heavy penalty unless obvious
             pass

        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0:
                return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Pre-calculate prompt features to avoid re-work
        prompt_features = self._extract_features(prompt)
        
        for cand in candidates:
            # Step 1: Structural Scoring (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # Step 2: NCD Tiebreaker (Secondary Signal)
            # We invert NCD so higher is better (lower distance = higher score contribution)
            # But only use it to break ties or for very close structural scores.
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 # Small weight
            
            final_score = struct_score + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if struct_score > 0.2:
                reasoning_parts.append("High structural alignment")
            elif struct_score < -0.2:
                reasoning_parts.append("Logical inconsistency detected")
            
            if prompt_features['has_negation'] and 'negation' in cand.lower():
                reasoning_parts.append("Correctly handles negation")
                
            if prompt_features['numbers'] and re.search(r'\d', cand):
                reasoning_parts.append("Numeric constraint considered")

            reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Standard evaluation"

            ranked.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural score mapped to a probability-like value.
        """
        # Get the structural score
        score = self._structural_score(prompt, answer)
        
        # Map score (approx -1.0 to 1.0) to (0.0 to 1.0)
        # 0.0 -> 0.5 (neutral)
        # 1.0 -> 1.0 (certain)
        # -1.0 -> 0.0 (certain wrong)
        confidence = (score + 1.0) / 2.0
        
        # Clamp
        return max(0.0, min(1.0, confidence))