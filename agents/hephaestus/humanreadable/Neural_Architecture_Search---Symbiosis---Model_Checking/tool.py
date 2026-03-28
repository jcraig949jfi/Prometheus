import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Verified Architecture Search (SVAS) Simulator.
    
    Mechanism:
    1. Architecture Agents (Candidates): Evaluated via structural parsing (negations, 
       comparatives, conditionals) and numeric consistency against the prompt.
    2. Verification Symbionts: A formal check that prunes candidates violating 
       logical constraints (e.g., answering 'No' when the prompt implies 'Yes', 
       or numeric contradictions). 
    3. Mutualistic Feedback: Candidates passing verification receive a 'robustness margin' 
       boost. The final score combines structural alignment (performance) with 
       verification status (safety), using NCD only as a tiebreaker for semantic 
       similarity when structural signals are ambiguous.
    """

    def __init__(self):
        self.ncd_cache = {}

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|higher|lower)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text_lower),
            'booleans': re.findall(r'\b(true|false|yes|no)\b', text_lower)
        }
        return features

    def _verify_constraint(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Verification Symbiont: Checks for logical contradictions.
        Returns (is_valid, robustness_margin).
        """
        margin = 0.0
        
        # Check 1: Numeric Consistency (Simple magnitude check if numbers exist)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            try:
                p_nums = [float(n) for n in prompt_feats['numbers']]
                c_nums = [float(n) for n in cand_feats['numbers']]
                # If prompt has numbers and candidate has numbers, check for gross contradictions
                # Heuristic: If prompt implies "less" and candidate number is huge, penalize
                if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if c_nums and p_nums:
                        if max(c_nums) > max(p_nums) * 10: # Gross violation
                            return False, 0.0
            except ValueError:
                pass

        # Check 2: Boolean/Logic Contradiction
        # If prompt asks a yes/no question and candidate contradicts known patterns
        p_bools = prompt_feats['booleans']
        c_bools = cand_feats['booleans']
        
        if p_bools and c_bools:
            # Simple contradiction detection: Prompt says "True", Candidate says "False"
            # This is a simplification for the simulator
            if 'true' in p_bools and 'false' in c_bools:
                 # Only flag if it looks like a direct answer
                 if len(p_bools) == 1 and len(c_bools) == 1:
                    return False, 0.0

        # Calculate Robustness Margin based on feature overlap (Symbiotic benefit)
        # More shared logical operators imply the candidate "understands" the prompt's logic
        shared_logic = 0
        if prompt_feats['negations'] > 0 and cand_feats['negations'] > 0:
            shared_logic += 0.2
        if prompt_feats['comparatives'] > 0 and cand_feats['comparatives'] > 0:
            shared_logic += 0.2
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] > 0:
            shared_logic += 0.2
            
        # Normalize margin
        margin = min(1.0, shared_logic)
        return True, margin

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        key = (s1, s2)
        if key in self.ncd_cache:
            return self.ncd_cache[key]
        
        l1 = len(zlib.compress(s1.encode()))
        l2 = len(zlib.compress(s2.encode()))
        l12 = len(zlib.compress((s1 + s2).encode()))
        
        denom = max(l1, l2)
        if denom == 0:
            return 0.0
        dist = (l12 - min(l1, l2)) / denom
        self.ncd_cache[key] = dist
        return dist

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # Verification Step
            is_valid, robustness_margin = self._verify_constraint(prompt_feats, cand_feats, prompt, cand)
            
            if not is_valid:
                # Verification failed: severe penalty
                score = 0.0
                reason = "Failed verification symbiont: Logical contradiction detected."
            else:
                # Scoring: Structural Alignment + Robustness Margin + NCD Tiebreaker
                # 1. Structural Alignment (Binary match for simplicity in this sim)
                struct_score = 0.0
                if prompt_feats['negations'] > 0:
                    struct_score += (0.2 if cand_feats['negations'] > 0 else -0.2)
                if prompt_feats['comparatives'] > 0:
                    struct_score += (0.2 if cand_feats['comparatives'] > 0 else -0.2)
                if prompt_feats['conditionals'] > 0:
                    struct_score += (0.2 if cand_feats['conditionals'] > 0 else -0.2)
                
                # 2. Mutualistic Benefit (Robustness)
                mutual_benefit = robustness_margin * 0.3
                
                # 3. NCD as tiebreaker (inverted to be a similarity score)
                # If prompt and candidate are very different structurally, NCD might be high, 
                # but if they share logic, NCD should be lower (more compressible together?)
                # Actually, for reasoning, we want semantic similarity. 
                # Let's use NCD to penalize gibberish or total mismatch.
                ncd_val = self._ncd(prompt, cand)
                ncd_score = (1.0 - ncd_val) * 0.1 # Small weight for tie-breaking
                
                base_score = 0.5 + struct_score + mutual_benefit + ncd_score
                score = max(0.0, min(1.0, base_score))
                reason = f"Verified. Structural match: {struct_score:.2f}, Robustness: {robustness_margin:.2f}"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on verification pass and structural alignment.
        """
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map score to confidence
        # If score is high, confidence is high. 
        # If verification failed, score is 0, confidence 0.
        return res[0]['score']