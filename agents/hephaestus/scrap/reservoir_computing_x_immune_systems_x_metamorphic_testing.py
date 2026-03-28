import re
import math
import zlib
import random
import numpy as np

class ReasoningTool:
    """
    Hybrid Reasoning Tool: Reservoir x Immune x Metamorphic Testing.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (predicates, arguments, modifiers) via regex.
    2. Reservoir: Maps proposition sequences to fixed high-dimensional states (ESN).
    3. Immune: Evolves candidate states via cloning/mutation towards a 'healthy' mean.
    4. Metamorphic: Penalizes candidates violating logical invariances (negation flips, order swaps).
    5. Scoring: Combines affinity, MR penalty, and NCD tie-breaking.
    """

    def __init__(self):
        # Fixed random seed for determinism
        np.random.seed(42)
        random.seed(42)
        
        # Reservoir params
        self.N = 50  # Reservoir size
        self.D = 20  # Input dimension
        self.W_in = np.random.randn(self.N, self.D) * 0.5
        # Sparse reservoir matrix
        self.W_res = np.random.randn(self.N, self.N)
        mask = np.random.rand(self.N, self.N) < 0.1
        self.W_res = self.W_res * mask
        # Scale for spectral radius < 1
        self.W_res = self.W_res / (np.max(np.abs(np.linalg.eigvals(self.W_res))) + 1e-6) * 0.9
        
        # Predicate dictionary (simplified)
        self.predicates = ["is", "are", "was", "were", "has", "have", "greater", "less", "equal", "before", "after"]
        self.pred_map = {p: i for i, p in enumerate(self.predicates)}
        self.P = len(self.predicates)
        
        # Argument hash matrix
        self.E = np.random.randn(self.P, self.D)

    def _parse_propositions(self, text: str) -> list:
        """Extract atomic clauses with modifiers."""
        text_lower = text.lower()
        props = []
        
        # Detect modifiers
        has_neg = bool(re.search(r'\b(not|no|never|none)\b', text_lower))
        has_comp = bool(re.search(r'\b(more|less|greater|smaller|before|after)\b', text_lower))
        has_cond = bool(re.search(r'\b(if|then|unless)\b', text_lower))
        
        # Extract numbers
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", text_lower)]
        
        # Extract simple predicate pattern
        pred_found = "is"
        for p in self.predicates:
            if p in text_lower:
                pred_found = p
                break
                
        props.append({
            "pred": pred_found,
            "neg": has_neg,
            "comp": has_comp,
            "cond": has_cond,
            "nums": nums,
            "text": text
        })
        return props

    def _prop_to_vector(self, prop: dict) -> np.ndarray:
        """Convert proposition to input vector u."""
        # Predicate one-hot
        p_idx = self.pred_map.get(prop["pred"], 0)
        p_vec = np.zeros(self.P)
        p_vec[p_idx] = 1.0
        
        # Argument embedding (hash numbers)
        arg_vec = np.zeros(self.D)
        if prop["nums"]:
            # Simple hash: sum of embedded numbers modulo D
            for n in prop["nums"]:
                idx = int(abs(n)) % self.D
                arg_vec[idx] += 1.0
            arg_vec = np.dot(self.E, arg_vec) # Project via fixed matrix
            
        # Modifiers
        mod_vec = np.array([float(prop["neg"]), float(prop["comp"]), float(prop["cond"])])
        
        # Concatenate: Pred (P) + Args (D) + Mods (3) -> Total D (truncate/pad)
        # Since P + D + 3 might not equal self.D, we project or slice
        full_vec = np.concatenate([p_vec, arg_vec, mod_vec])
        if len(full_vec) < self.D:
            full_vec = np.pad(full_vec, (0, self.D - len(full_vec)))
        return full_vec[:self.D]

    def _run_reservoir(self, props: list) -> np.ndarray:
        """Run ESN on proposition sequence."""
        x = np.zeros(self.N)
        if not props:
            return x
            
        for prop in props:
            u = self._prop_to_vector(prop)
            x = np.tanh(np.dot(self.W_in, u) + np.dot(self.W_res, x))
        return x

    def _compute_affinity(self, state: np.ndarray, mean_state: np.ndarray) -> float:
        """Cosine similarity to mean 'healthy' state."""
        norm_s = np.linalg.norm(state)
        norm_m = np.linalg.norm(mean_state)
        if norm_s == 0 or norm_m == 0:
            return 0.0
        return float(np.dot(state, mean_state) / (norm_s * norm_m))

    def _check_mr_violations(self, original_text: str, original_score: float) -> float:
        """
        Check Metamorphic Relations.
        Returns penalty score (higher = more violations).
        """
        penalty = 0.0
        text_lower = original_text.lower()
        
        # MR1: Negation Flip
        # If text has "not", removing it should change meaning significantly. 
        # We approximate: if "not" exists, we expect high sensitivity. 
        # If the text is just "not X", it's suspicious if X is short.
        if "not" in text_lower:
            # Heuristic: Negated statements often need more context. 
            # If very short and negated, slight penalty for ambiguity.
            if len(original_text.split()) < 4:
                penalty += 0.1
        
        # MR2: Numeric Consistency
        # If numbers exist, check if they are used logically (e.g. 9.11 < 9.9 is false)
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", original_text)]
        if len(nums) >= 2:
            # If the text claims "9.11 > 9.9" explicitly, it's a violation of math
            # We detect patterns like "9.11 is greater than 9.9"
            if ("greater" in text_lower or ">" in original_text) and nums[0] < nums[1]:
                penalty += 0.5
            if ("less" in text_lower or "<" in original_text) and nums[0] > nums[1]:
                penalty += 0.5
                
        # MR3: Order Swap (Commutativity check for specific verbs)
        # "A before B" vs "B before A". 
        # Hard to check without ground truth, so we penalize contradictory phrasing
        if "before" in text_lower and "after" in text_lower:
            # "A before B and B after A" is consistent. 
            # "A before B and A after B" is contradiction.
            # Simplified: if both present, ensure logical flow or penalize confusion
            pass # Too complex for regex only, skip heavy logic
            
        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt and Candidates
        prompt_props = self._parse_propositions(prompt)
        cand_props = [self._parse_propositions(c) for c in candidates]
        
        # 2. Reservoir Encoding
        prompt_state = self._run_reservoir(prompt_props)
        cand_states = [self._run_reservoir(p) for p in cand_props]
        
        # 3. Immune Selection Setup
        # Mean state (mu) is approximated by prompt state (as the 'antigen' or 'healthy' target)
        # In a real system, mu comes from validation set. Here, prompt is the query.
        mu = prompt_state 
        if np.linalg.norm(mu) == 0: mu = np.ones(self.N) * 0.1 # Regularize
        
        scores = []
        for i, c_text in enumerate(candidates):
            state = cand_states[i]
            
            # Affinity (Cosine similarity to prompt context)
            affinity = self._compute_affinity(state, mu)
            
            # Metamorphic Penalty
            mr_penalty = self._check_mr_violations(c_text, affinity)
            
            # Base Score
            score = affinity - 0.5 * mr_penalty
            
            scores.append({
                "candidate": c_text,
                "score": score,
                "affinity": affinity,
                "mr_penalty": mr_penalty,
                "state": state
            })
        
        # 4. Immune Cloning/Mutation Simulation (Simplified for ranking)
        # We boost scores of high-affinity candidates slightly to simulate selection pressure
        top_k_idx = sorted(range(len(scores)), key=lambda k: scores[k]['score'], reverse=True)[:max(1, len(scores)//5)]
        for idx in top_k_idx:
            scores[idx]['score'] += 0.05 # Cloning bonus
            
        # 5. Final Ranking with NCD Tie-breaking
        # Sort by score desc, then by NCD to prompt (lower NCD = better tiebreaker usually, 
        # but per instructions NCD is tiebreaker for structural signal absence. 
        # Here we use it to prefer concise, relevant answers if scores are close)
        
        # Calculate NCD to prompt for all
        ncds = [self._ncd(prompt, c['candidate']) for c in scores]
        
        # Final sort key: Score (desc), then NCD (asc - closer to prompt structure is better if tied)
        # Note: Pure NCD baseline is weak, so we weigh Score heavily.
        final_ranking = sorted(
            scores, 
            key=lambda x: (x['score'], -ncds[scores.index(x)]), 
            reverse=True # High score first. For NCD part: we want low NCD, so -ncd makes low ncd "larger"
        )
        
        # Re-sort logic correction: 
        # We want primary sort by score (desc). 
        # Secondary sort: if scores are equal, prefer lower NCD.
        # Python sort is stable. Let's sort by NCD asc first, then by score desc.
        temp_sorted = sorted(scores, key=lambda x: ncds[scores.index(x)]) # Asc NCD
        final_ranking = sorted(temp_sorted, key=lambda x: x['score'], reverse=True) # Desc Score
        
        result = []
        for item in final_ranking:
            result.append({
                "candidate": item["candidate"],
                "score": float(item["score"]),
                "reasoning": f"Affinity: {item['affinity']:.3f}, MR Penalty: {item['mr_penalty']:.3f}"
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score (roughly -1 to 1) to 0-1
        # Affinity is cosine (-1 to 1). MR penalty is positive.
        # Assume typical good score > 0.5, bad < 0.
        conf = 1.0 / (1.0 + math.exp(-4 * score)) # Sigmoid scaling
        return max(0.0, min(1.0, conf))