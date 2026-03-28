import re
import zlib
import math

class ReasoningTool:
    """
    Wavelet-Dialectical Pragmatic Reasoner (WDPR) - Structural Implementation
    
    Mechanism:
    1. Wavelet Decomposition (Multi-resolution): Simulated via recursive substring 
       scaling and structural depth analysis (nested parentheses, conditionals).
    2. Dialectics (Thesis-Antithesis-Synthesis): 
       - Thesis: Candidate matches prompt constraints (structural parse).
       - Antithesis: Candidate contradicts prompt negations or logical operators.
       - Synthesis: Weighted fusion based on coherence.
    3. Pragmatics (Gricean Maxims): Penalizes candidates that are too short (Quantity),
       irrelevant (no keyword overlap), or ambiguous (low structural distinctness).
       
    Primary scoring relies on structural parsing (negations, comparatives, numerics).
    NCD is used strictly as a tiebreaker for low-discrimination cases.
    """

    def __init__(self):
        # Gricean thresholds
        self.min_relevance_ratio = 0.2
        self.quantity_penalty_factor = 0.5

    def _structural_parse(self, text):
        """Extract logical structures: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'depth': text.count('(') + text.count('['), # Proxy for wavelet scale depth
        }
        return features

    def _evaluate_numeric(self, prompt_nums, candidate_nums, prompt_text):
        """Check numeric consistency if numbers are present."""
        if not prompt_nums or not candidate_nums:
            return 0.0
        
        try:
            p_vals = [float(x) for x in prompt_nums]
            c_vals = [float(x) for x in candidate_nums]
            
            # Simple heuristic: if prompt implies comparison, check order
            if any(k in prompt_text for k in ['greater', 'larger', 'more', 'max']):
                # Expect candidate to highlight larger number or be the larger number
                if c_vals and max(c_vals) >= max(p_vals):
                    return 0.5
            elif any(k in prompt_text for k in ['less', 'smaller', 'min']):
                if c_vals and min(c_vals) <= min(p_vals):
                    return 0.5
            
            # Exact match bonus for numeric problems
            if set(p_vals) == set(c_vals):
                return 1.0
                
        except ValueError:
            pass
        return 0.0

    def _dialectical_score(self, prompt, candidate):
        """
        Compute Thesis (support), Antithesis (contradiction), and Synthesis (fusion).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # --- THESIS: Structural Alignment ---
        # Does the candidate respect the logical operators found in the prompt?
        thesis_score = 0.0
        
        # Negation consistency: If prompt has negation, candidate should reflect it or answer appropriately
        if p_feat['negations'] > 0:
            # Reward if candidate also acknowledges negation context (simplified)
            if c_feat['negations'] > 0 or len(c_feat['numbers']) > 0:
                thesis_score += 0.3
        
        # Comparative consistency
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                thesis_score += 0.3
                
        # Conditional depth matching (Wavelet scale analogy)
        if p_feat['depth'] > 0:
            if c_feat['depth'] > 0 or len(candidate) > len(prompt) * 0.5:
                thesis_score += 0.2

        # Base lexical overlap (Pragmatic Relevance)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
            thesis_score += overlap * 0.4
        
        # --- ANTITHESIS: Contradiction Detection ---
        # Penalize if candidate ignores strong prompt signals
        antithesis_penalty = 0.0
        if p_feat['negations'] > 0 and c_feat['negations'] == 0 and len(c_feat['numbers']) == 0:
            # Risk of ignoring negation
            if any(w in c_words for w in ['yes', 'true', 'is']):
                antithesis_penalty += 0.5
        
        # --- SYNTHESIS: Gated Fusion ---
        # Combine thesis and antithesis
        raw_score = max(0, thesis_score - antithesis_penalty)
        
        # Add numeric evaluation component
        num_score = self._evaluate_numeric(p_feat['numbers'], c_feat['numbers'], prompt)
        
        synthesis = (raw_score * 0.6) + (num_score * 0.4)
        return min(1.0, synthesis)

    def _pragmatic_gate(self, prompt, candidate, base_score):
        """
        Apply Gricean Maxims as a gating mechanism.
        - Quantity: Is it too short/vague?
        - Quality: Does it look like random noise?
        - Relation: Is it relevant?
        """
        if not candidate.strip():
            return 0.0
            
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        
        # Quantity Maxim: Avoid extreme brevity unless prompt is tiny
        if p_len > 5 and c_len < 2:
            base_score *= 0.5
            
        # Relation Maxim: Keyword check (simplified)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        # Remove stop words for better signal
        stop = {'the', 'a', 'an', 'is', 'are', 'it', 'to', 'of', 'in', 'for'}
        p_sig = p_words - stop
        c_sig = c_words - stop
        
        if p_sig and not (p_sig & c_sig):
            # No significant word overlap, reduce confidence unless numeric
            if not re.search(r'\d', candidate):
                base_score *= 0.7
                
        return base_score

    def _ncd_distance(self, s1, s2):
        """Normalized Compression Distance (tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        prompt_features = self._structural_parse(prompt)
        
        # Pre-calculate prompt complexity for normalization
        prompt_complexity = len(prompt_features['numbers']) + prompt_features['negations'] + prompt_features['comparatives']
        
        for cand in candidates:
            # 1. Dialectical Score (Primary)
            score = self._dialectical_score(prompt, cand)
            
            # 2. Pragmatic Gate (Modifier)
            score = self._pragmatic_gate(prompt, cand, score)
            
            # 3. Structural Boost for High-Complexity Prompts
            if prompt_complexity > 0:
                # If prompt has logic, boost candidates that show logical markers
                cand_feat = self._structural_parse(cand)
                logic_markers = cand_feat['negations'] + cand_feat['comparatives'] + len(cand_feat['numbers'])
                if logic_markers > 0:
                    score = min(1.0, score + 0.1)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Dialectical synthesis: {score:.2f}, Pragmatic fit applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within 0.01)
        # This ensures determinism and handles edge cases where structural parse is ambiguous
        final_results = []
        for i, res in enumerate(results):
            if i > 0:
                prev = final_results[-1]
                if abs(res['score'] - prev['score']) < 0.01:
                    # Use NCD to break tie relative to prompt
                    ncd_curr = self._ncd_distance(prompt, res['candidate'])
                    ncd_prev = self._ncd_distance(prompt, prev['candidate'])
                    if ncd_curr < ncd_prev:
                        # Swap
                        final_results[-1], res = res, final_results[-1]
                        # Adjust reasoning note
                        res['reasoning'] += " (NCD tiebreak)"
            final_results.append(res)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the dialectical score as a proxy for confidence in the answer's validity.
        """
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        # The score generated is effectively the confidence metric
        # Calibrate slightly to ensure 0.5 isn't default for random strings
        base_score = res_list[0]['score']
        
        # Strong negative signal check (Antithesis dominance)
        if re.search(r'\b(no|false|incorrect|impossible)\b', answer.lower()):
            if re.search(r'\b(yes|true|correct)\b', prompt.lower()):
                return 0.1 # Direct contradiction
        
        return float(min(1.0, max(0.0, base_score)))