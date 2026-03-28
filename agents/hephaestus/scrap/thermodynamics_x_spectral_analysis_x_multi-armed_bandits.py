import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermo-Spectral Bandit Scorer.
    
    Mechanism:
    1. Structural Parsing: Extracts binary streams for logical cues (negation, conditional, etc.).
    2. Spectral Analysis: Uses FFT to measure global (low-freq) vs local (high-freq) cue density.
    3. Thermodynamics: Computes 'Energy' (deviation from ideal reference) and 'Entropy' (ambiguity).
    4. Multi-Armed Bandit: Simulates adaptive feature weighting via UCB1 to boost scores of 
       candidates with strong logical signals in critical areas.
    5. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.I),
            'comp': re.compile(r'\b(more|less|greater|smaller|better|worse|higher|lower|than|vs|versus)\b', re.I),
            'cond': re.compile(r'\b(if|unless|provided|assuming|then|else|otherwise)\b', re.I),
            'caus': re.compile(r'\b(because|therefore|thus|hence|since|so|causes|leads to)\b', re.I),
            'num': re.compile(r'\d+(\.\d+)?'),
            'ord': re.compile(r'\b(first|second|last|next|before|after|precede|follow)\b', re.I)
        }
        self.feature_keys = ['neg', 'comp', 'cond', 'caus', 'num', 'ord']
        self.n_features = len(self.feature_keys)
        
        # Reference mean (idealized correct answer spectrum - simplified)
        # Assumption: Correct answers have balanced structure, moderate entropy
        self.mu_ref = np.ones(2 * self.n_features) * 0.5 
        self.sigma_ref = np.ones(2 * self.n_features) * 0.2
        
        # Trap patterns for Tier B (Epistemic Honesty)
        self.trap_patterns = {
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ (fail|stop|die)|when did .+ stop)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every .+ (a|an) .+|each .+ (a|an) .+)\b', re.I), # Simplified
            'pronoun_ambiguity': re.compile(r'\b((.+)\s+(told|said|asked)\s+(.+)\s+(he|she|it|they)\b)', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.I),
            'unanswerable': re.compile(r'\b(unknown|impossible to know|not mentioned)\b', re.I)
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature streams."""
        tokens = text.lower().split()
        if not tokens:
            return np.zeros((self.n_features, 1))
        
        L = len(tokens)
        # Create binary matrix (features x length)
        F = np.zeros((self.n_features, L))
        
        for i, key in enumerate(self.feature_keys):
            pattern = self.patterns[key]
            for t_idx, token in enumerate(tokens):
                if pattern.search(token):
                    F[i, t_idx] = 1.0
        return F

    def _spectral_analysis(self, F: np.ndarray) -> np.ndarray:
        """Compute low and high frequency power for each feature."""
        n_feat, L = F.shape
        if L == 0:
            return np.zeros(2 * n_feat)
            
        S = []
        # Normalize signal to avoid DC dominance issues
        F_centered = F - np.mean(F, axis=1, keepdims=True)
        
        for i in range(n_feat):
            signal = F_centered[i, :]
            if L < 4:
                # Too short for meaningful FFT, use variance as proxy
                p_low = np.var(signal)
                p_high = np.var(signal)
            else:
                # FFT
                fft_vals = np.fft.rfft(signal)
                psd = np.abs(fft_vals) ** 2
                psd_norm = psd / np.sum(psd + 1e-9) # Normalize total power
                
                n_bins = len(psd_norm)
                low_cut = int(0.1 * n_bins)
                high_cut = int(0.4 * n_bins)
                
                p_low = np.sum(psd_norm[:max(1, low_cut)])
                p_high = np.sum(psd_norm[max(1, high_cut):min(n_bins, high_cut+5)]) # Ensure range exists
            
            S.append(p_low)
            S.append(p_high)
            
        return np.array(S)

    def _compute_thermo(self, s: np.ndarray) -> Tuple[float, float]:
        """Compute Energy and Entropy."""
        # Energy: Squared Euclidean distance from reference
        E = np.sum((s - self.mu_ref) ** 2)
        
        # Entropy: Softmax normalized spectral power
        exp_s = np.exp(-s)
        p = exp_s / (np.sum(exp_s) + 1e-9)
        H = -np.sum(p * np.log(p + 1e-9))
        
        return float(E), float(H)

    def _bandit_bonus(self, s: np.ndarray) -> float:
        """Simulate UCB1 bandit allocation to reward strong features."""
        # Treat each feature's spectral contribution as an arm
        # Reward = inverse deviation from ideal (simplified)
        rewards = []
        counts = np.ones(self.n_features) # Pseudo-counts
        means = np.zeros(self.n_features)
        
        # Pre-calculate idealized rewards based on reference
        # We assume higher spectral power in relevant bands is generally good if structured
        for i in range(self.n_features):
            val = s[2*i] + s[2*i+1] # Total power for feature i
            # Normalize reward 0-1 roughly
            r = min(1.0, val / 2.0) 
            means[i] = r
            counts[i] = 1.0
            rewards.append(r)
            
        # Simulate UCB pulls
        T = 2 * self.n_features
        total_bonus = 0.0
        c_param = 1.0
        
        for t in range(T):
            ucb_values = []
            for i in range(self.n_features):
                exploration = c_param * math.sqrt(math.log(t + 1) / counts[i])
                ucb_values.append(means[i] + exploration)
            
            best_arm = int(np.argmax(ucb_values))
            # Update (simplified: assume consistent reward)
            counts[best_arm] += 1
            # Running mean update
            means[best_arm] = means[best_arm] + (rewards[best_arm] - means[best_arm]) / counts[best_arm]
            
        return float(np.sum(means))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Check for Tier B traps and return a confidence cap."""
        p_lower = prompt.lower()
        
        # 1. Check for explicit trap keywords
        for key, pattern in self.trap_patterns.items():
            if pattern.search(p_lower):
                return 0.25 # Strong penalty for potential traps
        
        # 2. Check for ambiguity markers
        if '?' not in prompt and not prompt.strip().endswith('.'):
            # Unclear if question or statement
            return 0.5
            
        # 3. If answer is too short and generic
        if len(answer.split()) < 3 and answer.lower() in ['yes', 'no', 'maybe', 'i don\'t know']:
            # Low confidence unless prompt is trivial (heuristic)
            if any(k in p_lower for k in ['why', 'how', 'explain']):
                return 0.3
                
        return 1.0 # No obvious traps detected

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Core scoring logic."""
        # Combine prompt and candidate for context-aware feature extraction
        # But features are extracted primarily from the candidate's logic
        text = f"{prompt} {candidate}"
        F = self._extract_features(text)
        s = self._spectral_analysis(F)
        
        E, H = self._compute_thermo(s)
        B = self._bandit_bonus(s)
        
        # Score formula: -E + lambda*B - gamma*H
        # Tuned constants
        lam = 0.5
        gamma = 0.3
        
        raw_score = -E + lam * B - gamma * H
        
        # NCD Tiebreaker (max 15% influence)
        # Compare candidate structure to prompt structure
        ncd_val = self._compute_ncd(prompt, candidate)
        # Normalize NCD to be a small bonus for similarity, penalty for noise
        ncd_bonus = (1.0 - ncd_val) * 0.15 
        
        final_score = raw_score + ncd_bonus
        return final_score

    def _constructive_check(self, prompt: str, candidate: str) -> float:
        """Attempt to verify numeric/logic consistency if possible."""
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        # If prompt has numbers and candidate has none, slight penalty unless it's a yes/no
        if p_nums and not c_nums:
            if any(x in candidate.lower() for x in ['yes', 'no', 'true', 'false']):
                return 0.0 # Neutral
            return -0.5 # Penalty for ignoring numbers
        
        # If both have numbers, check magnitude consistency (heuristic)
        if p_nums and c_nums:
            try:
                p_max = max(float(x) for x in p_nums)
                c_max = max(float(x) for x in c_nums)
                # If candidate number is wildly different from prompt max, might be wrong
                # This is a weak heuristic but helps with "calculate" questions
                if p_max > 0 and (c_max > p_max * 10 or c_max < p_max * 0.01):
                    return -0.2
            except:
                pass
        return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._structural_score(prompt, cand)
            score += self._constructive_check(prompt, cand)
            
            # Generate reasoning string
            reasoning = f"Thermo-spectral analysis: Energy penalty applied based on cue distribution. Bandit bonus allocated to logical operators."
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check meta-constraints (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.3:
            return meta_cap
        
        # 2. Calculate base score
        score = self._structural_score(prompt, answer)
        
        # 3. Map score to 0-1 confidence
        # Assume score range is roughly [-5, 5] for typical inputs
        # Sigmoid mapping
        conf = 1.0 / (1.0 + math.exp(-score))
        
        # 4. Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # 5. Enforce strict upper bound unless computation was definitive
        # Since we don't have a full solver here, we cap at 0.85 to maintain epistemic humility
        # unless the constructive check passed perfectly (simulated by high structural score)
        if score < 2.0: # Arbitrary threshold for "definitive"
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))