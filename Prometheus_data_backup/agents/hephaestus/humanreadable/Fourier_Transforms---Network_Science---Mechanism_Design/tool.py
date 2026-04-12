import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Mechanism Design Reasoning Tool.
    
    Core Logic (Mechanism Design):
    The evaluate() method acts as a VCG-style mechanism. It parses structural constraints
    (negations, comparatives, conditionals) from the prompt. Candidates are scored based
    on adherence to these 'rules'. Violations incur heavy penalties (high-frequency noise),
    while satisfaction yields base utility. This incentivizes 'truthful' reporting of logic.
    
    Secondary Validation (Network Science):
    Concepts in the prompt and candidates are treated as nodes. We check for semantic 
    proximity (substring overlap/keyword matching) to boost scores of coherent answers.
    
    Confidence Wrapper (Fourier Transform Analogy):
    Per historical constraints, Fourier logic is restricted to the confidence() wrapper.
    We simulate a 'spectral check' by analyzing the frequency distribution of character 
    n-grams. High variance in high-frequency n-grams indicates 'noise' (low confidence),
    while smooth distributions suggest stable, high-confidence signals.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'valid']
        self.bool_no = ['no', 'false', 'incorrect', 'invalid']

    def _structural_parse(self, prompt: str) -> dict:
        """Extract logical constraints from the prompt."""
        p_lower = prompt.lower()
        has_neg = any(n in p_lower for n in self.negations)
        has_comp = any(c in p_lower for c in self.comparatives)
        has_cond = any(c in p_lower for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r"-?\d+\.?\d*", prompt)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'negation': has_neg,
            'comparative': has_comp,
            'conditional': has_cond,
            'numbers': numbers,
            'prompt_len': len(prompt)
        }

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric constraints explicitly."""
        p_nums = re.findall(r"-?\d+\.?\d*", prompt)
        if not p_nums:
            return 0.0 # No numeric logic to check
        
        try:
            p_vals = [float(n) for n in p_nums]
            c_nums = re.findall(r"-?\d+\.?\d*", candidate)
            if not c_nums:
                return -0.5 # Missing number in answer where expected
            
            c_val = float(c_nums[0])
            
            # Simple heuristic: If prompt has two numbers and asks for comparison implicitly
            if len(p_vals) >= 2:
                # Check if candidate respects order if keywords present
                p_low = min(p_vals)
                p_high = max(p_vals)
                
                if 'greater' in prompt.lower() or '>' in prompt:
                    return 1.0 if c_val == p_high else -1.0
                if 'less' in prompt.lower() or '<' in prompt:
                    return 1.0 if c_val == p_low else -1.0
                # Default to max if just listing numbers? No, penalize guesswork
                return 0.0 
        except ValueError:
            return -0.5
        return 0.0

    def _network_synergy(self, prompt: str, candidate: str) -> float:
        """Network Science component: Check concept overlap (synergy)."""
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Remove stopwords for better signal
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        p_words -= stopwords
        c_words -= stopwords
        
        if not p_words:
            return 0.0
            
        overlap = len(p_words & c_words)
        return overlap / (len(p_words) + 0.1) # Normalized overlap score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        structure = self._structural_parse(prompt)
        
        # Determine baseline expectation based on negation
        # If negation present, 'No' answers might be correct, etc.
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            c_lower = cand.lower()
            
            # 1. Mechanism Design: Structural Compliance (Primary Driver)
            # Check boolean consistency
            yes_in_c = any(y in c_lower for y in self.bool_yes)
            no_in_c = any(n in c_lower for n in self.bool_no)
            
            # Simple logical consistency check based on negation presence
            # This is a heuristic approximation of incentive compatibility
            if structure['negation']:
                # If prompt has negation, often the 'No' or negative implication is key
                # But without full NLP, we reward candidates that acknowledge complexity or specific negation words
                if any(n in c_lower for n in self.negations):
                    score += 2.0
                    reasoning_parts.append("Aligns with negation structure")
                elif yes_in_c and not no_in_c:
                    # Potential trap: answering Yes to a negative constraint without qualification
                    score -= 1.0 
                    reasoning_parts.append("Potential negation trap")
            else:
                if yes_in_c:
                    score += 1.0
                    reasoning_parts.append("Positive affirmation detected")

            # 2. Numeric Evaluation (Constraint Propagation)
            num_score = self._check_numeric_logic(prompt, cand)
            if num_score != 0:
                score += num_score * 3.0 # High weight for numeric correctness
                if num_score > 0:
                    reasoning_parts.append("Numeric constraint satisfied")
                else:
                    reasoning_parts.append("Numeric constraint violated")

            # 3. Network Synergy (Secondary Validation)
            net_score = self._network_synergy(prompt, cand)
            score += net_score * 2.0
            if net_score > 0.3:
                reasoning_parts.append(f"High concept overlap ({net_score:.2f})")
            
            # 4. NCD Tiebreaker (Only if scores are close/neutral)
            # We add a tiny epsilon based on NCD to break ties, but it's not primary
            try:
                import zlib
                p_comp = len(zlib.compress(prompt.encode()))
                c_comp = len(zlib.compress(cand.encode()))
                joint_comp = len(zlib.compress((prompt + cand).encode()))
                # Normalized Compression Distance approx
                ncd = (joint_comp - min(p_comp, c_comp)) / max(p_comp, c_comp) if max(p_comp, c_comp) > 0 else 1
                score += (1.0 - ncd) * 0.1 # Very small bonus for compressibility
            except:
                pass

            if not reasoning_parts:
                reasoning_parts.append("Structural analysis neutral")
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Fourier-inspired spectral check on character frequencies.
        Analyzes the 'smoothness' of the text signal. 
        High frequency noise (random chars) -> Low confidence.
        Smooth signal (repeating patterns/words) -> High confidence.
        """
        if not answer:
            return 0.0
        
        # Convert to ASCII codes as signal
        signal = np.array([ord(c) for c in answer], dtype=float)
        if len(signal) == 0:
            return 0.0
            
        # Center signal
        signal -= np.mean(signal)
        
        # Discrete Fourier Transform (using numpy FFT which is allowed as it's numpy standard)
        # We look at the energy in high frequencies vs low frequencies
        fft_vals = np.fft.fft(signal)
        magnitudes = np.abs(fft_vals)
        
        # Split spectrum
        mid = len(magnitudes) // 2
        if mid == 0: mid = 1
        
        low_freq_energy = np.sum(magnitudes[:mid]) 
        high_freq_energy = np.sum(magnitudes[mid:])
        
        total_energy = low_freq_energy + high_freq_energy
        if total_energy == 0:
            return 0.5
            
        # Ratio of low frequency (structure) to total
        # A pure constant string has all energy at DC (index 0), so ratio ~ 1.0
        # Random noise spreads energy, lowering the ratio.
        spectral_ratio = low_freq_energy / total_energy
        
        # Map to 0-1. 
        # We also penalize very short answers slightly unless they are perfect matches
        length_factor = min(1.0, len(answer) / 3.0) 
        
        # Combine with a basic correctness heuristic (does it look like an answer?)
        # If the prompt asks a question, does the answer contain key terms?
        # (Simplified for this wrapper to just use spectral ratio + length)
        
        confidence_score = spectral_ratio * 0.7 + length_factor * 0.3
        
        return float(np.clip(confidence_score, 0.0, 1.0))