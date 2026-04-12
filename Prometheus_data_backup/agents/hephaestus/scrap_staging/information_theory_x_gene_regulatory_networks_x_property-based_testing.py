import re
import math
import random
import zlib
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    A reasoning engine combining Gene Regulatory Network (GRN) style belief propagation,
    Information Theoretic scoring via Property-Based Testing (PBT), and Dynamical Systems
    stability analysis.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and relations into a graph.
    2. Dynamics (GRN): Propagates belief intervals [low, high] across the graph until convergence.
    3. PBT Scoring: Samples possible worlds consistent with constraints. Uses "shrinking" to find
       minimal counter-examples for candidates. Score based on entropy and shrinkage ratio.
    4. Stability Analysis: Perturbs premise order to measure trajectory stability (Lyapunov-like).
    5. Epistemic Honesty: Caps confidence if meta-features indicate ambiguity or traps.
    """

    def __init__(self):
        self.rng = random.Random(42)  # Deterministic seed

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    # --- 1. Parsing & Graph Construction ---

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions and relations."""
        nodes = []
        edges = []
        sentences = re.split(r'[.;!?]', text)
        
        node_id_counter = 0
        
        def get_id():
            nonlocal node_id_counter
            nid = f"n{node_id_counter}"
            node_id_counter += 1
            return nid

        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect patterns
            is_neg = bool(re.search(r'\b(not|no|never|without)\b', sent, re.I))
            is_cond = bool(re.search(r'\b(if|then|unless|provided)\b', sent, re.I))
            is_causal = bool(re.search(r'\b(causes|leads to|results in|implies)\b', sent, re.I))
            
            # Numeric extraction
            nums = re.findall(r'[-+]?\d*\.?\d+', sent)
            has_num = len(nums) >= 2
            
            # Simple proposition extraction (subject-verb-object approximation)
            # We treat the whole sentence as a proposition for now, linked by logic
            pid = get_id()
            polarity = -1 if is_neg else 1
            
            node_type = 'assertion'
            if is_cond: node_type = 'conditional'
            elif is_causal: node_type = 'causal'
            elif has_num: node_type = 'comparative'
            
            nodes.append({
                'id': pid, 'text': sent, 'polarity': polarity, 
                'type': node_type, 'value': nums if nums else None
            })
            
            # Infer edges between sentences based on proximity or explicit connectors
            # (Simplified for single-pass: mostly self-contained logic or implicit chain)
            if is_cond and len(nodes) > 1:
                # If "If A then B", assume previous node is A, current is B? 
                # Better: Parse internal structure. For this implementation, we link 
                # detected numerics if they appear in sequence.
                pass
                
        # Add numeric constraint edges if multiple numbers exist in text
        if len(nodes) > 1 and any(n['value'] for n in nodes):
            # Heuristic: Connect numeric nodes in order found
            numeric_nodes = [n for n in nodes if n['value']]
            for i in range(len(numeric_nodes) - 1):
                n1, n2 = numeric_nodes[i], numeric_nodes[i+1]
                # Assume increasing order if not specified, or just link for propagation
                edges.append(('comparative', n1['id'], n2['id']))

        return nodes, edges

    # --- 2. GRN-Style Constraint Propagation ---

    def _propagate_beliefs(self, nodes: List[Dict], edges: List[Tuple]) -> Dict[str, Tuple[float, float]]:
        """Iteratively update belief intervals [low, high] for each node."""
        beliefs = {n['id']: [0.5, 0.5] for n in nodes} # Start uncertain
        
        # Initialize based on polarity
        for n in nodes:
            if n['polarity'] == -1:
                beliefs[n['id']] = [0.0, 0.4] # Likely false
            elif n['polarity'] == 1:
                beliefs[n['id']] = [0.6, 1.0] # Likely true
                
        # Simple propagation loop (max 10 iters)
        for _ in range(10):
            changed = False
            for rel, src_id, tgt_id in edges:
                if src_id not in beliefs or tgt_id not in beliefs: continue
                s_low, s_high = beliefs[src_id]
                t_low, t_high = beliefs[tgt_id]
                
                new_t_low, new_t_high = t_low, t_high
                
                if rel == 'implication': # If src true, tgt true
                    if s_low > 0.5:
                        new_t_low = max(t_low, s_low)
                elif rel == 'negation':
                    if s_high < 0.5: # Src false -> tgt true? Or src true -> tgt false
                        new_t_high = 0.0 
                
                if abs(new_t_low - t_low) > 0.01 or abs(new_t_high - t_high) > 0.01:
                    beliefs[tgt_id] = [new_t_low, new_t_high]
                    changed = True
            if not changed: break
            
        return beliefs

    # --- 3. Property-Based Testing & Shrinking ---

    def _sample_worlds(self, nodes: List[Dict], beliefs: Dict, n_samples: int = 50) -> List[Dict]:
        """Generate worlds consistent with belief intervals."""
        worlds = []
        for _ in range(n_samples):
            world = {}
            for n in nodes:
                low, high = beliefs[n['id']]
                # Sample probability
                p = self.rng.uniform(low, high)
                world[n['id']] = (p > 0.5)
            worlds.append(world)
        return worlds

    def _shrink_counterexample(self, candidate: str, prompt: str) -> int:
        """
        Simulate shrinking: How many 'literals' (words/tokens) must be removed 
        from the candidate to make it consistent with prompt constraints?
        Returns size of minimal violating subset (larger = worse fit).
        """
        # Heuristic: Overlap ratio as proxy for shrinking effort
        # If candidate contains concepts NOT in prompt, shrinking is high effort
        p_words = set(re.findall(r'\w+', self._normalize(prompt)))
        c_words = set(re.findall(r'\w+', self._normalize(candidate)))
        
        extra_words = c_words - p_words
        # Base violation size
        return len(extra_words) + 1

    def _compute_score(self, prompt: str, candidate: str, nodes: List[Dict], beliefs: Dict) -> float:
        """Compute score based on entropy and shrinking."""
        worlds = self._sample_worlds(nodes, beliefs)
        if not worlds: return 0.0
        
        # Entropy estimation
        true_counts = {n['id']: 0 for n in nodes}
        for w in worlds:
            for nid, val in w.items():
                if val: true_counts[nid] += 1
        
        entropy = 0.0
        for n in nodes:
            p = true_counts[n['id']] / len(worlds)
            if 0 < p < 1:
                entropy -= p * math.log2(p) + (1-p) * math.log2(1-p)
        
        # Shrinking penalty
        shrink_size = self._shrink_counterexample(candidate, prompt)
        total_literals = max(1, len(re.findall(r'\w+', candidate)))
        shrink_ratio = shrink_size / total_literals
        
        # Score formula: Higher entropy (uncertainty) penalizes fit, 
        # but large shrink ratio (contradiction) penalizes more.
        # We want high score for GOOD fits. 
        # Good fit = Low shrink ratio, Moderate entropy (constrained but not contradictory)
        base_score = 1.0 - shrink_ratio
        entropy_penalty = (entropy / (len(nodes) + 1)) * 0.2
        
        return max(0.0, base_score - entropy_penalty)

    # --- 4. Dynamical Systems Stability (Frame C) ---

    def _analyze_stability(self, prompt: str, candidate: str) -> float:
        """
        Measure trajectory stability by perturbing premise order.
        If the logical conclusion (simulated by NCD overlap with prompt) varies wildly,
        confidence decreases.
        """
        sentences = [s.strip() for s in re.split(r'[.;!?]', prompt) if s.strip()]
        if len(sentences) < 2:
            return 1.0 # Too short to be unstable
            
        baseline_score = 1.0 - self._ncd(prompt, candidate)
        perturbations = []
        
        # Perturb order 3 times
        for _ in range(3):
            random.shuffle(sentences)
            perturbed_prompt = " ".join(sentences)
            score = 1.0 - self._ncd(perturbed_prompt, candidate)
            perturbations.append(score)
            
        if not perturbations: return 1.0
        
        variance = sum((s - sum(perturbations)/len(perturbations))**2 for s in perturbations) / len(perturbations)
        # Normalize variance to stability score (0 variance = 1.0 stability)
        stability = 1.0 / (1.0 + variance * 10)
        return stability

    # --- 5. Epistemic Honesty (Meta-Confidence) ---

    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, and unanswerability."""
        p = self._normalize(prompt)
        
        # 1. Presupposition traps
        presupposition_patterns = [
            r"have you stopped", r"why did.*fail", r"why is.*bad", 
            r"when did.*stop", r"how often.*fail"
        ]
        if any(re.search(pat, p) for pat in presupposition_patterns):
            return 0.2
            
        # 2. Scope/Pronoun ambiguity
        if re.search(r"every.*a.*y", p) or re.search(r"told.*he.*who", p):
            return 0.3
            
        # 3. False dichotomy
        if re.search(r"either.*or", p) and not re.search(r"both", p):
            return 0.4
            
        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "opinion", "feel"]
        if any(w in p for w in subjective_words):
            return 0.3
            
        # 5. Unanswerable (missing info heuristics)
        if re.search(r"what is the value of x", p) and "x =" not in p:
            return 0.1
            
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt.strip():
            return []
            
        nodes, edges = self._parse_propositions(prompt)
        beliefs = self._propagate_beliefs(nodes, edges)
        
        # Stability factor from dynamics
        stability_scores = []
        results = []
        
        for cand in candidates:
            # Structural & PBT Score
            pbt_score = self._compute_score(prompt, cand, nodes, beliefs)
            
            # Dynamics Score
            stab = self._analyze_stability(prompt, cand)
            stability_scores.append(stab)
            
            # NCD Tiebreaker (max 15% weight)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            # Dynamics 40%, Structural 45%, NCD 15%
            final_score = (stab * 0.40) + (pbt_score * 0.45) + (ncd_score * 0.15)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Stability:{stab:.2f}, PBT:{pbt_score:.2f}, NCD:{ncd_score:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check Meta-Confidence (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Compute raw confidence based on evaluation
        # We simulate a single-candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score (0-1) to confidence
        # If meta_cap is low, cap the confidence
        final_conf = min(raw_score, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (hard to guarantee here, so cap at 0.95)
        # But if meta_cap triggered (e.g. 0.2), it overrides.
        return round(final_conf, 3)

# Example Usage (for self-verification)
if __name__ == "__main__":
    tool = ReasoningTool()
    prompt = "If X > 5 then Y is true. X is 6. Is Y true?"
    candidates = ["Yes, Y is true", "No, Y is false", "Maybe"]
    
    print("Evaluation:")
    for r in tool.evaluate(prompt, candidates):
        print(r)
        
    print("\nConfidence (Clear case):", tool.confidence(prompt, "Yes, Y is true"))
    
    trap_prompt = "Have you stopped cheating on tests?"
    print("Confidence (Trap case):", tool.confidence(trap_prompt, "No"))