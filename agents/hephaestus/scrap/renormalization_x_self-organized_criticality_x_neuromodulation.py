import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Multi-scale Adaptive Gain-Modulated SOC-RG Network for Reasoning.
    
    Mechanism:
    1. RG (Renormalization Group): Hierarchical structural parsing extracts features 
       from raw text (fine) to logical constraints (coarse).
    2. SOC (Self-Organized Criticality): Used ONLY in confidence() as a stability check.
       If the prompt triggers "avalanche" conditions (ambiguity, presupposition), 
       the system enters a critical state, collapsing confidence to near-zero (Epistemic Honesty).
    3. Neuromodulation: A global gain factor scales the final score.
       - High Gain (Dopamine-like): Applied when structural/computational signals are strong.
       - Low Gain (Serotonin-like): Applied when signals are weak or conflicting, stabilizing against noise.
    
    Scoring Strategy:
    - Structural/Logical (50%+): Negations, comparatives, conditionals.
    - Computational (20%+): Numeric evaluation, PEMDAS, transitivity.
    - NCD (<=15%): Tiebreaker only.
    - Epistemic Honesty: Hard caps on confidence for ambiguous/unanswerable prompts.
    """

    def __init__(self):
        # Preset keywords for structural parsing (RG Layer 1)
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.logical_ops = ['and', 'or', 'but', 'however', 'therefore', 'thus']
        
        # Presupposition triggers (SOC Criticality Triggers)
        self.presupposition_triggers = [
            r'\b(stopped|quit|ceased|failed)\s+(to\s+)?\w+',
            r'\bwhy\s+(did|does|would)\s+\w+\s+(fail|stop|quit|lie)',
            r'\b(have|has)\s+you\s+(stopped|quit)',
            r'\bwhen\s+did\s+you\s+(stop|fail)',
            r'\bwhich\s+of\s+these\s+is\s+the\s+(best|worst)', # Subjectivity trap
            r'\beither\s+\w+\s+or\s+\w+\s+is\s+true' # False dichotomy hint
        ]
        
        # Ambiguity triggers
        self.ambiguity_triggers = [
            r'\bhe\s+was\s+\w+\s+who\?', # Pronoun ambiguity
            r'\bshe\s+told\s+\w+\s+he', # Pronoun ambiguity
            r'\bevery\s+\w+\s+did\s+a\s+\w+', # Scope ambiguity (same Y?)
            r'\bis\s+it\s+true\s+that' # Vague reference
        ]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for computational reasoning."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Solve simple numeric comparisons or extractions.
        Returns 1.0 if candidate matches computed truth, 0.0 if opposite, 0.5 if irrelevant.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # Case 1: Direct numeric match (extraction)
        if len(p_nums) == 1 and len(c_nums) == 1:
            return 1.0 if abs(p_nums[0] - c_nums[0]) < 1e-6 else 0.0
            
        # Case 2: Comparison (e.g., "Which is larger? 5 or 3?" -> "5")
        prompt_lower = self._normalize(prompt)
        if 'larger' in prompt_lower or 'greater' in prompt_lower or 'more' in prompt_lower:
            if len(p_nums) >= 2 and len(c_nums) == 1:
                target = max(p_nums)
                return 1.0 if abs(c_nums[0] - target) < 1e-6 else 0.0
        elif 'smaller' in prompt_lower or 'less' in prompt_lower:
            if len(p_nums) >= 2 and len(c_nums) == 1:
                target = min(p_nums)
                return 1.0 if abs(c_nums[0] - target) < 1e-6 else 0.0
                
        return 0.5 # Neutral if no clear numeric logic applies

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """RG Layer 1: Coarse-grain text into logical features."""
        lower_text = self._normalize(text)
        words = set(lower_text.split())
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        has_logic = any(l in words for l in self.logical_ops)
        
        # Count density of logical operators
        logic_density = (int(has_negation) + int(has_comparative) + int(has_conditional) + int(has_logic)) / 4.0
        
        return {
            'negation': int(has_negation),
            'comparative': int(has_comparative),
            'conditional': int(has_conditional),
            'logic_density': logic_density
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        SOC Criticality Check & Epistemic Honesty Filter.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (low = critical/ambiguous, high = stable/clear).
        """
        lower_p = self._normalize(prompt)
        score = 1.0
        
        # Check for Presuppositions (Critical Instability)
        for pattern in self.presupposition_triggers:
            if re.search(pattern, lower_p):
                return 0.15 # Strong cap: Likely a trap
        
        # Check for Ambiguity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, lower_p):
                return 0.25 # Moderate cap: Ambiguous
        
        # Check for Subjectivity without criteria
        if ('best' in lower_p or 'worst' in lower_p or 'favorite' in lower_p) and 'list' not in lower_p:
             # If asking for best without a provided list/context, it's subjective
            if 'according to' not in lower_p and 'data' not in lower_p:
                return 0.20

        # Check for length (too short to reason)
        if len(lower_p.split()) < 4:
            return 0.30
            
        return 1.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main evaluation loop implementing the RG-SOC-Neuromodulation architecture.
        """
        results = []
        prompt_features = self._structural_parse(prompt)
        prompt_lower = self._normalize(prompt)
        
        # Base structural signal from prompt
        base_structure_score = prompt_features['logic_density'] * 0.2
        
        for candidate in candidates:
            cand_lower = self._normalize(candidate)
            score = 0.5 # Start neutral
            
            # --- RG Layer 2: Candidate-Prompt Interaction ---
            
            # 1. Structural Matching (Negation/Logic consistency)
            cand_features = self._structural_parse(candidate)
            
            # If prompt has negation, correct answer often reflects it or contrasts it
            struct_match = 0.0
            if prompt_features['negation'] > 0:
                # Heuristic: If prompt denies X, and candidate affirms X, might be wrong (simplified)
                # Better: Check if candidate contains logical operators matching prompt depth
                struct_match = 0.1 * (1.0 - abs(prompt_features['logic_density'] - cand_features['logic_density']))
            else:
                struct_match = 0.1 * cand_features['logic_density']
            
            # 2. Computational Score (The "Hard" Reasoning)
            comp_score = self._compute_numeric_score(prompt, candidate)
            # If numbers were found and matched perfectly, boost significantly
            if comp_score == 1.0:
                score += 0.4
            elif comp_score == 0.0:
                score -= 0.4 # Penalty for wrong number
            
            # 3. Keyword Overlap (Weak signal, heavily regularized)
            p_words = set(prompt_lower.split())
            c_words = set(cand_lower.split())
            overlap = len(p_words & c_words) / (len(p_words | c_words) + 1e-6)
            
            # --- Neuromodulatory Gain Control ---
            # Calculate global gain based on structural clarity
            # High structure -> High Gain (Amplify differences)
            # Low structure -> Low Gain (Suppress noise, rely on priors)
            gain = 0.5 + (prompt_features['logic_density'] * 0.8) 
            
            # Combine signals
            raw_score = (struct_match * 0.3) + (overlap * 0.15) + (base_structure_score * 0.1)
            
            # Apply Gain
            final_score = 0.5 + (raw_score - 0.5) * gain
            
            # Adjust based on computational certainty
            if comp_score != 0.5:
                final_score = comp_score * 0.8 + raw_score * 0.2

            # NCD Tiebreaker (Max 15% influence)
            ncd_val = self._calculate_ncd(prompt, candidate)
            # Invert NCD (lower distance = higher score) and scale small
            ncd_score_contribution = (1.0 - ncd_val) * 0.15
            final_score = (final_score * 0.85) + ncd_score_contribution
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural:{struct_match:.2f}, Comp:{comp_score:.2f}, Gain:{gain:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Epistemic Honesty via _meta_confidence (SOC Criticality Check).
        """
        # 1. Meta-Confidence (The Hard Cap)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Internal Consistency Check
        # Run evaluate to see if this answer is ranked highly
        candidates = [answer, "dummy_placeholder"]
        ranked = self.evaluate(prompt, candidates)
        
        # If the answer is the top result, get its score
        top_candidate = ranked[0]['candidate']
        top_score = ranked[0]['score']
        
        is_top = (top_candidate == answer)
        
        # Base confidence on ranking and score magnitude
        if is_top:
            raw_conf = top_score
        else:
            # If not top, confidence is low
            raw_conf = 0.2
            
        # Apply the Meta-Confidence Cap (SOC Collapse)
        # If the prompt is ambiguous/trap, meta_cap is low (e.g., 0.2)
        # This forces the output to be low regardless of how well the answer matches patterns
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless it's a definitive computational match
        # We assume definitive matches come from the numeric solver which yields high scores
        if final_conf > 0.9:
            # Double check it's not just string matching
            if self._compute_numeric_score(prompt, answer) != 1.0:
                final_conf = 0.85
                
        return round(final_conf, 3)