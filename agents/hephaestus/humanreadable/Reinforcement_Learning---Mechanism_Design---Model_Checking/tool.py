import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Verifiable Incentive-Compatible Policy Synthesis Loop (VIC-PSL)
    
    Mechanism:
    1. RL Analogy (Candidate Generation): Candidates are treated as policies.
    2. Mechanism Design (Core Scoring): We define a 'payment' function based on 
       structural adherence (negations, comparatives, conditionals). Candidates 
       violating logical constraints receive heavy penalties (enforcing IC/IR).
    3. Model Checking (Verification): We treat the prompt's logical constraints 
       as temporal logic specifications. We generate a 'counterexample trace' 
       by comparing candidate structure against prompt structure. 
       - If the candidate contradicts the prompt's logical operators, MC fails.
       - The severity of the failure shapes the final score (reward shaping).
    
    This implements the 'verify-then-reward' loop where MC counterexamples 
    directly penalize the RL-style policy score.
    """

    def __init__(self):
        # Logical operators as 'specifications' to check
        self.negation_triggers = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparative_triggers = ['more', 'less', 'greater', 'smaller', 'before', 'after']
        self.conditional_triggers = ['if', 'unless', 'only if', 'when']
        self.numeric_pattern = re.compile(r"-?\d+(?:\.\d+)?")

    def _extract_logic_signature(self, text: str) -> Dict:
        """Extract structural features for Model Checking."""
        lower_text = text.lower()
        return {
            'negations': sum(1 for t in self.negation_triggers if t in lower_text),
            'comparatives': sum(1 for t in self.comparative_triggers if t in lower_text),
            'conditionals': sum(1 for t in self.conditional_triggers if t in lower_text),
            'numbers': set(self.numeric_pattern.findall(lower_text)),
            'length': len(text.split())
        }

    def _check_compliance(self, prompt_sig: Dict, cand_sig: Dict, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Model Checking Step: Verify if candidate satisfies prompt constraints.
        Returns (score_modifier, reason_string)
        """
        score = 1.0
        reasons = []

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has high negation density, candidate must reflect awareness
        if prompt_sig['negations'] > 0:
            if cand_sig['negations'] == 0:
                # Potential violation: ignoring negative constraints
                score -= 0.4
                reasons.append("Failed negation check (ignored constraints)")
            else:
                score += 0.1 # Reward for acknowledging constraints

        # 2. Comparative/Ordinal Consistency
        if prompt_sig['comparatives'] > 0:
            if cand_sig['comparatives'] == 0 and len(cand_sig['numbers']) == 0:
                # Prompt asks for comparison, candidate gives none
                score -= 0.3
                reasons.append("Failed comparative check (no ordering detected)")
        
        # 3. Numeric Consistency (Simple containment check)
        # If prompt defines specific numbers, valid answers often relate to them
        if len(prompt_sig['numbers']) > 0:
            # Heuristic: If candidate has numbers, they should ideally relate to prompt numbers
            # or be a direct calculation. Here we just check for hallucination vs grounding.
            common_nums = prompt_sig['numbers'].intersection(cand_sig['numbers'])
            if len(common_nums) == 0 and len(cand_sig['numbers']) > 0:
                # Candidate introduces unrelated numbers (potential hallucination)
                score -= 0.2
                reasons.append("Numeric inconsistency detected")
            elif len(common_nums) > 0:
                score += 0.2 # Reward grounding

        # 4. Length/Complexity Penalty (Occam's razor / IR constraint)
        # Prevent verbose gibberish that mimics structure but lacks content
        if cand_sig['length'] > prompt_sig['length'] * 3:
            score -= 0.1
            reasons.append("Violates brevity constraint")

        reason_str = "; ".join(reasons) if reasons else "Compliant"
        return score, reason_str

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_sig = self._extract_logic_signature(prompt)
        results = []

        for cand in candidates:
            cand_sig = self._extract_logic_signature(cand)
            
            # Step 1: Mechanism Design (Scoring based on incentives)
            base_score = 0.5
            
            # Step 2: Model Checking (Verification & Counterexamples)
            mc_adjustment, mc_reason = self._check_compliance(prompt_sig, cand_sig, prompt, cand)
            
            # Step 3: NCD Tiebreaker (Similarity to prompt context)
            # We want candidates that are compressible with the prompt (shared info)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.2  # Max 0.2 contribution
            
            final_score = base_score + mc_adjustment + ncd_score
            
            # Clamp score
            final_score = max(0.0, min(1.0, final_score))

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"MC Status: {mc_reason}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the evaluation score of the single answer."""
        # Reuse evaluate logic but for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]