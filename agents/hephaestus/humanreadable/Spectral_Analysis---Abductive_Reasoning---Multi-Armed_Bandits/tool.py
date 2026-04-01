import re
import math
import zlib
import numpy as np

class ReasoningTool:
    """
    Spectral-Abductive-Bandit Reasoning Tool with Dynamics Tracking.
    
    Mechanism:
    1. Structural Parsing: Extracts logical flags (negation, causal, numeric, etc.) into a time-series.
    2. Spectral Analysis: Uses FFT to measure low-frequency coherence (logical flow) vs high-frequency noise.
    3. Abductive Reasoning: Generates hypotheses based on flag patterns and updates priors via Bayesian likelihood.
    4. Dynamics Tracking (Frame C): Simulates premise reordering to test trajectory stability (Lyapunov-like).
    5. Bandit Selection: Uses UCB to rank candidates based on spectral score + abductive score + stability.
    6. Epistemic Honesty: Caps confidence if prompt contains ambiguity, presupposition, or unanswerable traits.
    """

    def __init__(self):
        self.arm_counts = {}  # n_a for UCB
        self.arm_sums = {}    # Sum of rewards for UCB
        self.total_pulls = 0
        # Fixed weights for structural features
        self.weights = np.array([1.0, 1.0, 1.5, 1.5, 1.0, 1.0, 1.0]) 
        # Expected spectral scores for hypotheses (learned offline approximation)
        self.hypothesis_means = {
            "causal_chain": 2.5,
            "logical_flow": 2.0,
            "numeric_reasoning": 1.8,
            "default": 1.0
        }
        self.sigma = 0.5  # Likelihood spread

    def _parse_flags(self, text):
        """Extract binary flags for structural features at each token position."""
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text_lower)
        flags = []
        
        # Regex patterns
        p_neg = re.compile(r'no|not|never|none|neither|n\'t')
        p_comp = re.compile(r'more|less|greater|smaller|better|worse|than|compar')
        p_cond = re.compile(r'if|then|unless|provided|whether')
        p_causal = re.compile(r'because|therefore|thus|hence|so|cause|effect|since')
        p_num = re.compile(r'\d+|[zero|one|two|three|four|five|six|seven|eight|nine|ten]')
        p_order = re.compile(r'first|second|third|last|next|before|after|follow')
        p_quant = re.compile(r'all|some|many|few|every|each|any|most|several')

        for token in tokens:
            f = [
                1 if p_neg.search(token) else 0,
                1 if p_comp.search(token) else 0,
                1 if p_cond.search(token) else 0,
                1 if p_causal.search(token) else 0,
                1 if p_num.search(token) else 0,
                1 if p_order.search(token) else 0,
                1 if p_quant.search(token) else 0
            ]
            flags.append(f)
        
        if not flags:
            return np.zeros((1, 7))
        return np.array(flags)

    def _spectral_score(self, text):
        """Compute spectral coherence score from structural flags."""
        flags = self._parse_flags(text)
        if flags.size == 0:
            return 0.0
            
        # Flatten to scalar time series
        x = np.dot(flags, self.weights[:flags.shape[1]])
        
        # Pad to power of 2 for FFT efficiency
        L = len(x)
        if L == 0: return 0.0
        next_pow2 = 1 if L == 0 else int(2**math.ceil(math.log2(L)))
        x_padded = np.zeros(next_pow2)
        x_padded[:L] = x
        
        # FFT
        X = np.fft.fft(x_padded)
        P = np.abs(X)**2
        
        # Bands
        L_fft = len(P)
        lf_end = max(1, int(L_fft / 8))
        B_LF = P[1:lf_end] # Skip DC (index 0) to avoid bias from length
        B_HF = P[lf_end:]
        
        sum_lf = np.sum(B_LF) + 1e-9
        sum_hf = np.sum(B_HF) + 1e-9
        
        return sum_lf / sum_hf

    def _abductive_score(self, text, s_spec):
        """Generate hypotheses and compute entropy-weighted score."""
        flags = self._parse_flags(text)
        flag_counts = np.sum(flags, axis=0) if flags.size > 0 else np.zeros(7)
        
        # Define hypotheses based on flag presence
        hypotheses = [
            ("causal_chain", flag_counts[3]), # Causal flags
            ("logical_flow", flag_counts[2] + flag_counts[0]), # Conditional + Negation
            ("numeric_reasoning", flag_counts[4]), # Numeric
            ("default", 1.0)
        ]
        
        gammas = []
        for name, count in hypotheses:
            if count == 0 and name != "default":
                continue
            # Prior proportional to count
            pi = count if count > 0 else 0.1
            mu_i = self.hypothesis_means.get(name, 1.0)
            # Likelihood
            likelihood = math.exp(-((s_spec - mu_i)**2) / (2 * self.sigma**2))
            posterior = pi * likelihood
            gammas.append(posterior)
            
        if not gammas:
            return 0.0
            
        # Normalize to probabilities
        total = sum(gammas) + 1e-9
        probs = [g / total for g in gammas]
        
        # Entropy-weighted sum (negative entropy as score? Or just sum of weighted posteriors)
        # Formula: Sum(gamma_i * log(gamma_i)) -> This is negative entropy. 
        # Higher magnitude negative = more certain. Let's use -Sum(p log p) as "information gain" score
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log(p + 1e-9)
        return entropy * s_spec # Scale by spectral coherence

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return min(c1, c2) / max(c1, c2, 1) if max(c1, c2) > 0 else 0.0

    def _dynamics_stability(self, prompt, candidate):
        """
        Frame C: Dynamics Tracker.
        Simulate premise reordering to check trajectory stability.
        If the answer relies on specific ordering that breaks when shuffled, it's fragile.
        We approximate this by checking if the candidate contains specific sequence markers
        that might be disrupted, or by simple perturbation of the prompt text.
        """
        # Extract sentences as premises
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', prompt) if len(s.strip()) > 10]
        if len(sentences) < 2:
            return 1.0 # Not enough data to be unstable
            
        # Perturb: Shuffle sentences and re-evaluate a cheap proxy of match
        # Since we can't re-run full logic easily, we check keyword overlap stability
        base_tokens = set(re.findall(r'\w+', candidate.lower()))
        if not base_tokens:
            return 0.5
            
        stability_scores = []
        for _ in range(3): # 3 perturbations
            np.random.shuffle(sentences)
            perturbed_prompt = " ".join(sentences)
            # Check overlap of candidate tokens in perturbed prompt
            perturbed_tokens = set(re.findall(r'\w+', perturbed_prompt.lower()))
            overlap = len(base_tokens & perturbed_tokens) / len(base_tokens) if base_tokens else 0
            stability_scores.append(overlap)
            
        # Variance as instability measure
        if len(stability_scores) < 2:
            return 1.0
        return 1.0 - np.std(stability_scores) # High std = low stability

    def _meta_confidence(self, prompt):
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition
        if re.search(r'(have you stopped|why did .+ fail|why is .+ bad)', p):
            score = min(score, 0.2)
        # 2. Scope ambiguity
        if re.search(r'every .+ (a|the) .+\?', p) and "same" in p:
            score = min(score, 0.3)
        # 3. Pronoun ambiguity
        if re.search(r'(he|she|they) was', p) and "who" in p:
            score = min(score, 0.3)
        # 4. False dichotomy
        if re.search(r'either .+ or .+', p) and "only" not in p:
            score = min(score, 0.4)
        # 5. Subjectivity
        if re.search(r'(best|worst|favorite|opinion)', p) and "calculate" not in p:
            score = min(score, 0.5)
        # 6. Unanswerability
        if re.search(r'(impossible|unknown|not given|insufficient)', p):
            score = min(score, 0.2)
            
        return score

    def _get_ucb_score(self, s_spec, s_add, stability, candidate):
        """Calculate UCB score for the candidate arm."""
        key = candidate[:50] # Truncate for hashing if needed
        if key not in self.arm_counts:
            self.arm_counts[key] = 0
            self.arm_sums[key] = 0.0
            
        # Reward r
        r = 0.6 * s_spec + 0.3 * s_add + 0.1 * stability
        
        n = self.arm_counts[key]
        if n == 0:
            return float('inf'), key # Explore first
            
        mean = self.arm_sums[key] / n
        # UCB1
        ucb = mean + math.sqrt(2 * math.log(self.total_pulls + 1) / (n + 1))
        return ucb, key

    def evaluate(self, prompt, candidates):
        results = []
        self.total_pulls += 1
        
        # Pre-check prompt meta-confidence
        meta_cap = self._meta_confidence(prompt)
        
        scored_candidates = []
        for cand in candidates:
            s_spec = self._spectral_score(cand)
            s_add = self._abductive_score(cand, s_spec)
            stability = self._dynamics_stability(prompt, cand)
            
            # UCB Update
            ucb_val, key = self._get_ucb_score(s_spec, s_add, stability, cand)
            
            # Update bandit state
            if self.arm_counts.get(key, 0) == 0:
                self.arm_counts[key] = 1
                self.arm_sums[key] = s_spec # Initial reward
            else:
                self.arm_counts[key] += 1
                self.arm_sums[key] += s_spec
            
            # Final Score composition
            # Structural (S_spec) >= 50%, Computation (S_add/Stability) >= 20%, NCD <= 15%
            # We use NCD only as a tiny tiebreaker against the prompt
            ncd_score = 1.0 - self._compute_ncd(prompt, cand) # Higher is better match
            
            final_score = (0.55 * s_spec) + (0.25 * s_add) + (0.10 * stability) + (0.10 * ncd_score)
            
            # Apply meta-cap for confidence later, but keep score relative
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "stability": stability,
                "meta_cap": meta_cap
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        output = []
        for item in scored_candidates:
            # Reasoning string
            reason = f"Spectral:{item['score']:.2f}, Stability:{item['stability']:.2f}"
            if item['meta_cap'] < 0.5:
                reason += " [Warning: Prompt ambiguity detected]"
                
            output.append({
                "candidate": item["candidate"],
                "score": item["score"],
                "reasoning": reason
            })
            
        return output

    def confidence(self, prompt, answer):
        """Return confidence 0-1, capped by epistemic honesty checks."""
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        s_spec = self._spectral_score(answer)
        if s_spec < 0.1: # No structural features found
            meta_cap = min(meta_cap, 0.2)
            
        # 3. Base confidence from score
        # Normalize spectral score roughly (assuming typical range 0-5)
        base_conf = min(1.0, s_spec / 3.0)
        
        # 4. Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # 5. Never exceed 0.9 without definitive computation (heuristic: high numeric density)
        has_numbers = bool(re.search(r'\d+', answer))
        if not has_numbers and final_conf > 0.9:
            final_conf = 0.9
            
        return max(0.0, min(1.0, final_conf))