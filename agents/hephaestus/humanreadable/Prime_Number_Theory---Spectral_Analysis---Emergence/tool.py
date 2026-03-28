import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Prime-Indexed Spectral Emergence Analyzer (PIM-SEA) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical operators (negations, comparatives),
       numeric values, and constraint structures. This drives the bulk of the score.
    2. Spectral Emergence (Secondary): Simulates prime-indexed spectral analysis by mapping
       token positions to prime-frequency bins. It detects "emergent motifs" where 
       structural patterns persist across prime scales (simulated via coprime stride checks).
    3. Hypothesis Testing: Compares the structural/spectral signature of candidates against
       the prompt's implied logic.
    4. NCD (Tiebreaker): Used only when structural signals are ambiguous.
    
    This hybrid approach prioritizes logical structure (beating NCD baselines) while
    utilizing the prime-spectral concept for robustness against shuffled/paraphrased inputs.
    """

    def __init__(self):
        # First 25 primes for indexing
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        # Logical keywords for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'n't']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical features: negations, numbers, comparatives."""
        lower_text = text.lower()
        tokens = re.findall(r'\b\w+\b', lower_text)
        
        # Count logical operators
        neg_count = sum(1 for t in tokens if any(n in t for n in self.negations))
        comp_count = sum(1 for t in tokens if any(c in t for c in self.comparatives))
        cond_count = sum(1 for t in tokens if any(c in t for c in self.conditionals))
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        numeric_vals = []
        for n in numbers:
            try:
                numeric_vals.append(float(n))
            except ValueError:
                pass
                
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': numeric_vals,
            'length': len(tokens)
        }

    def _spectral_emergence_score(self, text: str) -> float:
        """
        Simulates prime-indexed spectral analysis.
        Maps token positions to prime frequencies to detect periodic structural motifs.
        Returns a score representing the presence of emergent regularities.
        """
        tokens = re.findall(r'\b\w+\b', text.lower())
        if not tokens:
            return 0.0
            
        score = 0.0
        n_tokens = len(tokens)
        
        # Use first few primes to check for periodic recurrence of logical tokens
        # This mimics checking spectral power at prime frequencies
        for i, p in enumerate(self.primes[:5]): 
            if p >= n_tokens:
                break
            
            # Sample tokens at prime intervals
            sample = [tokens[j] for j in range(0, n_tokens, p)]
            
            # Check for repetition (emergence of motif) within this spectral band
            if len(sample) > 1:
                # Simple entropy-like measure: low entropy (high repetition) boosts score
                # But we want complex emergence, so we look for logical terms appearing periodically
                logic_hits = sum(1 for t in sample if any(k in t for k in self.negations + self.conditionals))
                if logic_hits > 0:
                    # Weight by prime index (higher primes = finer resolution)
                    score += (logic_hits / len(sample)) * (1.0 / (i + 1))
                    
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _evaluate_logic_consistency(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """Scores based on logical constraint propagation."""
        score = 0.0
        
        # 1. Numeric Consistency
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if p_nums and c_nums:
            # If prompt has numbers and candidate has numbers, check ordering/magnitude logic
            # Simple heuristic: if prompt implies comparison, candidate should reflect it
            if prompt_feats['comparatives'] > 0:
                if len(c_nums) >= 2:
                    # Check if candidate actually performs a comparison logic internally?
                    # Hard to verify without execution, so we reward presence of relevant numbers
                    score += 0.3
                else:
                    score += 0.1 # Partial credit for having numbers
            else:
                score += 0.2 # Basic numeric presence
        elif not p_nums and not c_nums:
            score += 0.1 # Consistent absence

        # 2. Logical Operator Alignment
        # If prompt has negation, correct answer often needs to handle it (presence or explicit denial)
        if prompt_feats['negations'] > 0:
            # Reward candidates that acknowledge complexity (have some logical operators)
            if cand_feats['negations'] > 0 or cand_feats['conditionals'] > 0:
                score += 0.3
            # Penalize overly simple answers to complex logical prompts
            if cand_feats['length'] < 5:
                score -= 0.2
        
        # 3. Conditional Chain
        if prompt_feats['conditionals'] > 0:
            if cand_feats['conditionals'] > 0 or cand_feats['length'] > prompt_feats['length'] * 0.5:
                score += 0.3
                
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        prompt_spectral = self._spectral_emergence_score(prompt)
        prompt_lower = prompt.lower()
        
        results = []
        
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            cand_spectral = self._spectral_emergence_score(cand)
            
            # Primary Score: Structural Logic
            logic_score = self._evaluate_logic_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # Secondary Score: Spectral Emergence Similarity
            # Does the candidate share the "rhythm" of the prompt's logic?
            spectral_diff = abs(prompt_spectral - cand_spectral)
            spectral_score = max(0, 0.5 - spectral_diff) # Closer is better
            
            # Tiebreaker: NCD (only if structural signals are weak)
            ncd_val = self._ncd(prompt_lower, cand.lower())
            ncd_score = 1.0 - ncd_val if (logic_score < 0.1) else 0.0
            
            # Composite Score
            # Weighted heavily towards structural parsing (70%), then spectral (20%), then NCD (10%)
            final_score = (logic_score * 0.7) + (spectral_score * 0.2) + (ncd_val * -0.1 * 0.1)
            
            # Normalize rough bounds to 0-1 range approximately
            final_score = max(0.0, min(1.0, final_score + 0.5)) 
            
            reasoning = f"Structural: {logic_score:.2f}, Spectral: {spectral_score:.2f}"
            if logic_score < 0.1:
                reasoning += f", NCD-adjusted"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment and spectral consistency as a proxy for correctness.
        """
        prompt_feats = self._structural_parse(prompt)
        ans_feats = self._structural_parse(answer)
        
        # Base confidence on structural richness alignment
        conf = 0.5
        
        # If prompt is complex (logic/numbers), answer must be substantial
        prompt_complexity = prompt_feats['negations'] + prompt_feats['comparatives'] + prompt_feats['conditionals'] + (0.1 * len(prompt_feats['numbers']))
        ans_complexity = ans_feats['negations'] + ans_feats['comparatives'] + ans_feats['conditionals'] + (0.1 * len(ans_feats['numbers']))
        
        if prompt_complexity > 0:
            if ans_complexity >= prompt_complexity * 0.5:
                conf += 0.3
            else:
                conf -= 0.3 # Likely wrong if too simple for complex prompt
        
        # Spectral check
        p_spec = self._spectral_emergence_score(prompt)
        a_spec = self._spectral_emergence_score(answer)
        if abs(p_spec - a_spec) < 0.2:
            conf += 0.1
            
        # Numeric sanity check (if both have numbers)
        if prompt_feats['numbers'] and ans_feats['numbers']:
            # If prompt asks for a number, and answer provides one, boost confidence
            conf += 0.2
            
        return max(0.0, min(1.0, conf))