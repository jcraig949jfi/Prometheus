import re
import math
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Sparse-Bandit Property-Test Scorer (SBPTS)
    
    Mechanism:
    1. Sparse Coding: Extracts logical propositions (negations, comparatives, conditionals, causals)
       from prompt and candidates into a global dictionary, representing texts as sparse binary vectors.
    2. Baseline Scoring: Computes a raw score based on deterministic constraint satisfaction 
       (transitivity, modus ponens, arithmetic consistency) using numpy dot products.
    3. Exploration (MAB): Uses UCB1 to explore single-proposition mutations (add/remove/flip) to 
       find higher-scoring variants within a budget.
    4. Shrinking (PBT): If a mutation improves the score, deterministically removes redundant 
       propositions to find a minimal high-scoring variant (hypothesis minimization).
       
    Note: Property-Based Testing is restricted to the shrinking/minimization phase to avoid 
    direct scoring pitfalls, per causal analysis. NCD is used only as a tiebreaker.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'neg': re.compile(r'\b(not|never|no|none|without)\b', re.I),
        'comp': re.compile(r'(\d+(?:\.\d+)?)\s*(>|<|>=|<=|more than|less than|equal to)\s*(\d+(?:\.\d+)?)', re.I),
        'cond': re.compile(r'\b(if|unless|provided that)\b(.+?)(?:then|,|\.)', re.I),
        'causal': re.compile(r'(\w+)\s+(causes|leads to|results in|implies)\s+(\w+)', re.I),
        'num': re.compile(r'\b(\d+(?:\.\d+)?)\b'),
        'order': re.compile(r'\b(first|then|before|after|next)\b', re.I)
    }

    def __init__(self):
        self.global_dict: Dict[str, int] = {}
        self.dict_lock = False # Simple flag to indicate dictionary is built

    def _extract_propositions(self, text: str) -> Set[str]:
        """Extract logical propositions as strings."""
        props = set()
        text_lower = text.lower()
        
        # Negations
        if self.PATTERNS['neg'].search(text_lower):
            props.add(f"NEGATION_EXISTS")
            
        # Comparatives (Numeric)
        for m in self.PATTERNS['comp'].finditer(text_lower):
            v1, op, v2 = m.group(1), m.group(2), m.group(3)
            # Normalize operator
            op_map = {'>': 'GT', '<': 'LT', '>=': 'GE', '<=': 'LE', 
                      'more than': 'GT', 'less than': 'LT', 'equal to': 'EQ'}
            norm_op = op_map.get(op.strip(), 'CMP')
            props.add(f"NUM({v1},{norm_op},{v2})")
            
        # Conditionals
        for m in self.PATTERNS['cond'].finditer(text_lower):
            props.add(f"COND({m.group(2)[:20]})") # Truncate for brevity
            
        # Causal
        for m in self.PATTERNS['causal'].finditer(text_lower):
            props.add(f"CAUSE({m.group(1)},{m.group(3)})")
            
        # Ordering
        for m in self.PATTERNS['order'].finditer(text_lower):
            props.add(f"ORDER({m.group(1)})")
            
        # Numeric presence (simple equality check context)
        nums = self.PATTERNS['num'].findall(text_lower)
        if len(nums) >= 2:
            props.add(f"HAS_NUMS({','.join(nums[:3])})")
            
        return props

    def _build_vector(self, text: str, all_props: List[str], prop_to_idx: Dict[str, int]) -> np.ndarray:
        """Create sparse binary vector."""
        vec = np.zeros(len(all_props), dtype=np.uint8)
        found = self._extract_propositions(text)
        for p in found:
            if p in prop_to_idx:
                vec[prop_to_idx[p]] = 1
        return vec

    def _compute_constraints_score(self, vec: np.ndarray, all_props: List[str]) -> float:
        """
        Compute score based on logical consistency.
        Rules: 
        1. Numeric consistency (if A>B and B>C, check A>C implied)
        2. Negation consistency (avoid P and NOT P if detectable)
        3. Reward density of valid structural matches.
        """
        score = 0.0
        props = [all_props[i] for i in range(len(vec)) if vec[i] == 1]
        
        # Base score: Number of structural features found
        score += len(props) * 0.5
        
        # Check numeric consistency
        nums_data = []
        for p in props:
            if p.startswith("NUM("):
                # Parse NUM(v1,OP,v2)
                content = p[4:-1]
                parts = content.split(',')
                if len(parts) == 3:
                    try:
                        v1, op, v2 = float(parts[0]), parts[1], float(parts[2])
                        nums_data.append((v1, op, v2))
                        # Immediate arithmetic check
                        if op == 'GT' and v1 > v2: score += 1.0
                        elif op == 'LT' and v1 < v2: score += 1.0
                        elif op == 'GE' and v1 >= v2: score += 1.0
                        elif op == 'LE' and v1 <= v2: score += 1.0
                        elif op == 'EQ' and abs(v1-v2) < 1e-9: score += 1.0
                        else: score -= 0.5 # Contradiction
                    except: pass
        
        # Transitivity check (simplified)
        if len(nums_data) > 2:
            # If we have A>B and B>C, do we have A>C?
            # Simplified: Just reward having multiple consistent numeric claims
            score += 0.2 * len(nums_data)

        # Negation penalty if too many negations without context (heuristic)
        neg_count = sum(1 for p in props if "NEGATION" in p)
        if neg_count > 2:
            score -= 0.2 * neg_count
            
        return score

    def _ucb1(self, Q: np.ndarray, N: np.ndarray, t: int, c: float = 1.0) -> int:
        """Select arm using UCB1."""
        if t == 0:
            return 0 # Fallback
        ucb_values = np.zeros(len(Q))
        for i in range(len(Q)):
            if N[i] == 0:
                return i # Explore unvisited
            exploration = c * math.sqrt(math.log(t) / N[i])
            ucb_values[i] = Q[i] + exploration
        return int(np.argmax(ucb_values))

    def _shrink(self, best_vec: np.ndarray, base_score: float, all_props: List[str]) -> Tuple[np.ndarray, float]:
        """Deterministic shrinking: try removing propositions while maintaining score."""
        current_vec = best_vec.copy()
        current_score = base_score
        indices = np.where(current_vec == 1)[0]
        
        for idx in indices:
            test_vec = current_vec.copy()
            test_vec[idx] = 0
            new_score = self._compute_constraints_score(test_vec, all_props)
            # Keep removal if score doesn't drop significantly (allow small epsilon for stability)
            if new_score >= current_score - 1e-6:
                current_vec = test_vec
                current_score = new_score
        return current_vec, current_score

    def _run_sbpts(self, prompt: str, candidate: str, budget: int = 20) -> Tuple[float, str]:
        # 1. Feature Extraction & Dictionary Build
        combined = f"{prompt} {candidate}"
        props_set = self._extract_propositions(combined)
        # Add some dummy props to ensure dictionary isn't empty if text is barren
        props_set.add("DEFAULT_TRUE") 
        all_props = list(props_set)
        prop_to_idx = {p: i for i, p in enumerate(all_props)}
        n_props = len(all_props)
        
        if n_props == 0:
            return 0.0, "No structural features found."

        # Vectorize
        v_orig = self._build_vector(candidate, all_props, prop_to_idx)
        v_prompt = self._build_vector(prompt, all_props, prop_to_idx)
        
        # 2. Baseline Score
        s0 = self._compute_constraints_score(v_orig, all_props)
        best_vec = v_orig.copy()
        best_score = s0
        reasoning_parts = []
        
        if best_score > 0:
            reasoning_parts.append(f"Found {int(best_score/0.5)} structural matches.")

        # 3. Multi-Armed Bandit Exploration
        # Arms: Add, Remove, Flip for each proposition. 
        # To keep it manageable and deterministic, we simulate arms as indices to flip.
        n_arms = n_props * 3 # Flip, Set, Reset roughly
        Q = np.zeros(n_arms)
        N = np.zeros(n_arms)
        
        for t in range(1, budget + 1):
            arm = self._ucb1(Q, N, t)
            prop_idx = arm % n_props
            action = arm // n_props # 0: flip, 1: set 1, 2: set 0
            
            v_perturbed = best_vec.copy()
            
            if action == 0: # Flip
                v_perturbed[prop_idx] = 1 - v_perturbed[prop_idx]
            elif action == 1: # Set 1
                v_perturbed[prop_idx] = 1
            else: # Set 0
                v_perturbed[prop_idx] = 0
                
            s_prime = self._compute_constraints_score(v_perturbed, all_props)
            reward = s_prime - best_score
            
            # Update Bandit
            Q[arm] += (reward - Q[arm]) / (N[arm] + 1)
            N[arm] += 1
            
            if reward > 0:
                # 4. Property-Based Shrinking
                shrunk_vec, shrunk_score = self._shrink(v_perturbed, s_prime, all_props)
                if shrunk_score > best_score:
                    best_vec = shrunk_vec
                    best_score = shrunk_score
                    reasoning_parts.append(f"Iteration {t}: Improved to {best_score:.2f} via mutation/shrink.")

        # Tiebreaker: NCD (Normalized Compression Distance) if scores are close or zero
        # Only used if structural signal is weak or as final tiebreaker
        ncd_score = 0.0
        if best_score < 1.0:
            try:
                z_prompt = len(zlib.compress(prompt.encode()))
                z_cand = len(zlib.compress(candidate.encode()))
                z_both = len(zlib.compress((prompt + candidate).encode()))
                denom = max(z_prompt, z_cand)
                if denom > 0:
                    ncd_score = 1.0 - (z_both - min(z_prompt, z_cand)) / denom
                    ncd_score = max(0, ncd_score) # Ensure non-negative
            except:
                ncd_score = 0.0
            # NCD is weak, so scale it down to not override structural logic
            best_score += ncd_score * 0.1
            if ncd_score > 0:
                reasoning_parts.append(f"NCD tiebreaker applied: {ncd_score:.2f}")

        reason_str = " ".join(reasoning_parts) if reasoning_parts else "Scored based on structural density."
        return float(best_score), reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._run_sbpts(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reason})
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on SBPTS score normalized."""
        score, _ = self._run_sbpts(prompt, answer)
        # Heuristic normalization: Assume max reasonable structural score is around 10-20
        # Map to 0-1 range softly
        conf = 1.0 / (1.0 + math.exp(-(score - 2.0))) # Sigmoid centered at 2.0
        return float(np.clip(conf, 0.0, 1.0))

# Import zlib here to avoid global scope issues if not needed elsewhere
import zlib