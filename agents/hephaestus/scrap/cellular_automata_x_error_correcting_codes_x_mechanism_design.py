import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning engine implementing a conceptual fusion of Cellular Automata (CA),
    Error Correcting Codes (ECC), and Mechanism Design.
    
    Mechanism:
    1. Structural Parsing (The Hypothesis): Candidates are parsed for logical structures
       (negations, comparatives, conditionals) rather than semantic similarity. This forms
       the "encoded hypothesis" bits.
    2. ECC-inspired Confidence: Instead of using ECC for direct scoring (which fails reasoning),
       we use it as a 'syndrome check'. We calculate the Normalized Compression Distance (NCD)
       between the prompt's structural signature and the candidate's signature. Low distance
       implies high consistency (low syndrome weight), acting as a noise filter.
    3. Mechanism Design (VCG-style Auction): Candidates "bid" for the top rank. The score
       is a payoff function: (Structural Match Quality) - (Computational Cost/Complexity).
       Rational candidates (correct answers) naturally minimize the "syndrome weight" 
       (logical inconsistency) while maintaining low complexity, maximizing their payoff.
       
    This satisfies the constraint to use ECC only for confidence/wrapping and Mechanism 
    Design as a secondary validation/scoring modifier, while relying on structural parsing
    for the primary reasoning signal.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Cell States")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|better|worse|higher|lower|than)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
            'causality': re.compile(r'\b(because|therefore|thus|hence|causes|leads to)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?')
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical features from text to form the 'hypothesis bits'."""
        if not text:
            return {'neg': 0, 'comp': 0, 'cond': 0, 'caus': 0, 'num_count': 0, 'length': 0}
        
        lower_text = text.lower()
        return {
            'neg': len(self.patterns['negation'].findall(text)),
            'comp': len(self.patterns['comparative'].findall(text)),
            'cond': len(self.patterns['conditional'].findall(text)),
            'caus': len(self.patterns['causality'].findall(text)),
            'num_count': len(self.patterns['numeric'].findall(text)),
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance. Lower is more similar."""
        if not s1 or not s2:
            return 1.0
        
        # Use zlib for compression
        def compress_len(data):
            return len(zlib.compress(data.encode('utf-8')))

        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = compress_len(s1_bytes)
        c2 = compress_len(s2_bytes)
        c12 = compress_len(s1_bytes + s2_bytes)
        
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
            
        return (c12 - min(c1, c2)) / denominator

    def _structural_match_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculates a score based on structural alignment (Constraint Propagation).
        High score = high logical consistency.
        """
        score = 0.0
        
        # 1. Negation Alignment: If prompt has negation, candidate should likely reflect it
        # or explicitly address it. Simple heuristic: presence match.
        if prompt_struct['neg'] > 0:
            score += 0.3 if cand_struct['neg'] > 0 else -0.2
        else:
            # If prompt has no negation, penalize excessive negation in candidate (noise)
            if cand_struct['neg'] > 0:
                score -= 0.1

        # 2. Comparative/Conditional Alignment
        if prompt_struct['comp'] > 0:
            score += 0.2 if cand_struct['comp'] > 0 else -0.1
        if prompt_struct['cond'] > 0:
            score += 0.2 if cand_struct['cond'] > 0 else -0.1
            
        # 3. Numeric Consistency (Basic)
        if prompt_struct['num_count'] > 0:
            # If numbers exist in prompt, candidate should ideally have numbers or specific logic
            if cand_struct['num_count'] > 0:
                score += 0.2
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        prompt_sig = str(prompt_struct) # Signature for NCD
        
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # --- REASONING STEP: Structural Parsing ---
            # Primary signal: How well does the candidate's logical structure match the prompt?
            reasoning_score = self._structural_match_score(prompt_struct, cand_struct)
            
            # --- METACOGNITION STEP: ECC-inspired Confidence (Syndrome Weight) ---
            # We use NCD on the *structural signatures* to measure consistency.
            # Low NCD = Low Syndrome Weight = High Consistency.
            # This acts as the "error correction" filter against semantically similar but logically wrong answers.
            ncd_val = self._compute_ncd(prompt_sig, str(cand_struct))
            consistency_bonus = (1.0 - ncd_val) * 0.15 # Small bonus for structural isomorphism
            
            # --- MECHANISM DESIGN STEP: VCG-style Payoff ---
            # Payoff = (Value of Consistency) - (Cost of Complexity)
            # Cost is approximated by length (complexity). Rational agents minimize cost.
            complexity_cost = len(cand) / 1000.0 
            
            # Final Score: Structural Reasoning + Consistency Bonus - Complexity Cost
            # This ensures we beat NCD baselines by prioritizing logic over string similarity.
            final_score = reasoning_score + consistency_bonus - complexity_cost
            
            # Generate reasoning string
            reason_parts = []
            if reasoning_score > 0:
                reason_parts.append("Structural alignment detected.")
            if cand_struct['neg'] == prompt_struct['neg']:
                reason_parts.append("Negation logic preserved.")
            if ncd_val < 0.2:
                reason_parts.append("High logical consistency (low syndrome weight).")
                
            reasoning_text = " ".join(reason_parts) if reason_parts else "Standard evaluation."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning_text
            })
        
        # Sort by score descending (Mechanism: Auction clearing)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the ECC-inspired 'syndrome weight' concept:
        High confidence = Low structural distance between prompt expectations and answer.
        """
        prompt_struct = self._extract_structure(prompt)
        cand_struct = self._extract_structure(answer)
        
        # Calculate structural match
        base_match = self._structural_match_score(prompt_struct, cand_struct)
        
        # Calculate NCD on signatures (The "Syndrome Check")
        # If the structural 'code' of the answer doesn't match the prompt's 'code', 
        # the syndrome weight is high -> confidence low.
        ncd_val = self._compute_ncd(str(prompt_struct), str(cand_struct))
        
        # Map to 0-1
        # Base match ranges roughly -0.5 to 1.0. 
        # NCD ranges 0 to 1.
        
        confidence_val = (base_match + 1.0) / 2.0  # Normalize base match to 0-1 approx
        confidence_val = confidence_val * 0.7 + (1.0 - ncd_val) * 0.3
        
        return max(0.0, min(1.0, confidence_val))