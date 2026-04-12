import math
import hashlib

class ReasoningTool:
    """
    Compositional Active Neural Architecture Search (CAN-NAS) Simulator.
    
    Mechanism:
    This tool simulates the 'Compositional Active Neural Architecture Search' 
    by treating candidate answers as architectural hypotheses composed of modular tokens.
    
    1. Compositionality: Answers are parsed into token sequences. A 'compositional score'
       is derived from the structural complexity and recurrence of tokens (simulating 
       Neural Module Networks).
    2. Active Inference (Epistemic Foraging): Instead of static accuracy, the system 
       calculates an 'Expected Free Energy' (G) score. It favors candidates that minimize 
       uncertainty (entropy) while maximizing information gain relative to the prompt context.
       Candidates with moderate complexity (high information, low surprise) are ranked higher,
       simulating the drive to resolve uncertainty about the best architecture.
    3. NAS Weight Sharing: A deterministic hash-based pseudo-random generator seeded by 
       the prompt simulates a shared supernet state, ensuring consistent scoring across 
       evaluations for the same context.
       
    The result is a ranked list where the 'best' answer is the one that represents the 
    most efficient compositional explanation of the data, minimizing free energy.
    """

    def __init__(self):
        self._state_seed = 0

    def _hash_to_float(self, s: str) -> float:
        """Deterministic hash to float [0, 1]."""
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def _tokenize(self, text: str) -> list:
        """Simple tokenizer splitting by non-alphanumeric chars."""
        return [t.lower() for t in text.split() if t.isalnum()]

    def _compute_compositional_score(self, text: str) -> float:
        """
        Simulates compositionality by analyzing token structure.
        Rewards recurrence (modularity) and penalizes excessive length (complexity cost).
        """
        tokens = self._tokenize(text)
        if not tokens:
            return 0.0
        
        # Count frequency (modularity)
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        
        # Modular bonus: repeated patterns suggest reusable modules
        modular_bonus = sum((c - 1) for c in freq.values() if c > 1) * 0.1
        
        # Length penalty (Occam's razor): simpler is better, but needs capacity
        length = len(tokens)
        length_penalty = math.log(length + 1) * 0.05
        
        # Unique token ratio (diversity)
        diversity = len(freq) / (length + 1)
        
        return (modular_bonus + diversity) - length_penalty

    def _compute_free_energy(self, prompt: str, candidate: str, seed_val: float) -> float:
        """
        Computes a proxy for Expected Free Energy G.
        G = Complexity - Accuracy (approximated here as Fit - Uncertainty).
        We want to minimize G, so we maximize (Fit - Complexity).
        """
        # Contextual fit: How much does the candidate share vocabulary with prompt?
        p_tokens = set(self._tokenize(prompt))
        c_tokens = self._tokenize(candidate)
        
        if not c_tokens:
            return -10.0

        overlap = len([t for t in c_tokens if t in p_tokens])
        fit_score = (overlap + 1) / (len(p_tokens) + 1)
        
        # Epistemic value: Deterministic noise based on content to simulate 
        # the 'surprise' or 'uncertainty' reduction potential.
        # High overlap reduces uncertainty (lowers free energy).
        compositional_val = self._compute_compositional_score(candidate)
        
        # The 'Active Inference' term: 
        # We prefer candidates that have high compositional value and high contextual fit.
        # seed_val adds a slight bias based on the 'supernet' state for this prompt.
        epistemic_gain = (fit_score * 0.6) + (compositional_val * 0.4) + (seed_val * 0.1)
        
        return epistemic_gain

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not prompt or not candidates:
            return []

        # Initialize supernet state seed based on prompt
        prompt_seed = self._hash_to_float(prompt)
        
        scored = []
        for cand in candidates:
            # Deterministic variation per candidate based on content + prompt
            candidate_seed = self._hash_to_float(prompt + cand)
            
            # Calculate Free Energy proxy (higher is better in this maximization formulation)
            score = self._compute_free_energy(prompt, cand, candidate_seed)
            
            # Generate reasoning string
            comp_score = self._compute_compositional_score(cand)
            reasoning = (
                f"Compositional modularity: {comp_score:.4f}; "
                f"Contextual fit: active inference minimizes uncertainty by aligning "
                f"tokens with prompt; Net epistemic value: {score:.4f}"
            )
            
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized free energy score.
        """
        if not prompt or not answer:
            return 0.0
            
        prompt_seed = self._hash_to_float(prompt)
        raw_score = self._compute_free_energy(prompt, answer, self._hash_to_float(prompt + answer))
        
        # Normalize roughly to [0, 1] using sigmoid-like mapping
        # Assuming typical scores range between -0.5 and 1.5
        normalized = 1.0 / (1.0 + math.exp(-5.0 * (raw_score - 0.5)))
        
        return max(0.0, min(1.0, normalized))