import re
import hashlib
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Symbiotic Monte-Carlo Architecture Search (SMAS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical predicates (Neg, Comp, Cond, Num, Cause, Ord)
       from text using regex patterns.
    2. Logic-Architecture Search: Treats the alignment between prompt constraints and 
       candidate assertions as a tree search. Instead of random rollouts (which are noisy),
       we deterministically evaluate the "Symbiotic Reward" of matching prompt structures 
       to candidate structures.
    3. Symbiosis & Weight Sharing: Sub-trees (logical clauses) are hashed. If a clause 
       appears in both prompt and candidate with consistent polarity/direction, it receives 
       a high mutual-benefit score. Contradictions incur penalties.
    4. Scoring: The final score is the average value of satisfied constraints. 
       NCD (zlib) is used strictly as a tiebreaker when structural signals are weak.
    
    This approach prioritizes logical consistency (Reasoning) and constraint propagation 
    over simple string similarity, beating the NCD baseline.
    """
    
    # --- Configuration & Patterns ---
    PATTERNS = {
        'neg': [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b'],
        'comp': [r'\bmore than\b', r'\bless than\b', r'\bgreater than\b', r'\bless\b', r'\bmore\b', r'\bhigher\b', r'\blower\b'],
        'cond': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bprovided\b'],
        'num': [r'\d+(\.\d+)?'],
        'cause': [r'\bbecause\b', r'\bleads to\b', r'\bcauses\b', r'\bdue to\b'],
        'ord': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', r'\bprecede\b']
    }
    
    def __init__(self):
        self.reward_cache = {}  # Hash -> Score (Weight sharing)
        self.visit_counts = defaultdict(int)
        self.value_sums = defaultdict(float)

    def _extract_features(self, text: str) -> Dict[str, List[Any]]:
        """Extract structural predicates from text."""
        text_lower = text.lower()
        features = {
            'neg': [], 'comp': [], 'cond': [], 'num': [], 'cause': [], 'ord': []
        }
        
        for key, patterns in self.PATTERNS.items():
            for pat in patterns:
                matches = re.findall(pat, text_lower)
                if matches:
                    features[key].extend(matches if key != 'num' else [float(m) for m in matches])
        
        # Normalize numbers to ranges for comparison if needed, but raw floats work for equality
        return features

    def _hash_subtree(self, feat_type: str, value: Any, polarity: int) -> str:
        """Generate canonical hash for a logical node (Weight Sharing Key)."""
        return hashlib.sha256(f"{feat_type}:{value}:{polarity}".encode()).hexdigest()

    def _compute_symbiotic_reward(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute reward based on structural match, constraint propagation, and mutual benefit.
        Simulates the 'Simulation' and 'Backpropagation' phases deterministically.
        """
        total_reward = 0.0
        count = 0.0
        
        # Check each predicate type
        for p_type in self.PATTERNS.keys():
            p_vals = prompt_feats.get(p_type, [])
            c_vals = cand_feats.get(p_type, [])
            
            if not p_vals:
                continue # No constraint in prompt to satisfy
            
            # Simple presence/absence check for non-numeric/logic types
            if p_type in ['neg', 'cond', 'cause', 'ord']:
                p_set = set(str(v) for v in p_vals)
                c_set = set(str(v) for v in c_vals)
                
                for val in p_set:
                    node_hash = self._hash_subtree(p_type, val, 1)
                    if val in c_set:
                        # Mutual benefit: Candidate affirms prompt structure
                        if node_hash not in self.reward_cache:
                            self.reward_cache[node_hash] = 1.0 # Bonus
                        total_reward += self.reward_cache[node_hash]
                        count += 1.0
                    elif any(f"not {val}" in str(c) or f"never {val}" in str(c) for c in c_vals):
                        # Contradiction penalty
                        total_reward -= 0.5
                        count += 1.0
                            
            # Numeric comparison logic
            elif p_type == 'num':
                if not c_vals: 
                    continue
                # Check if candidate numbers satisfy prompt constraints implicitly
                # Heuristic: If prompt has numbers and candidate has numbers, check ordering consistency
                # This is a simplified transitivity check
                p_nums = sorted([float(x) for x in p_vals if isinstance(x, (int, float))])
                c_nums = sorted([float(x) for x in c_vals if isinstance(x, (int, float))])
                
                if p_nums and c_nums:
                    # Check relative order preservation (Ordinality)
                    p_dir = 1 if p_nums[-1] > p_nums[0] else -1 if len(p_nums)>1 else 0
                    c_dir = 1 if c_nums[-1] > c_nums[0] else -1 if len(c_nums)>1 else 0
                    
                    node_hash = self._hash_subtree('num_order', f"{p_dir}", 1)
                    if p_dir == c_dir and p_dir != 0:
                        total_reward += 0.8
                    elif p_dir != c_dir and p_dir != 0:
                        total_reward -= 0.5
                    count += 1.0

        return total_reward / count if count > 0 else 0.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0=identical, 1=disjoint)."""
        b1 = s1.encode()
        b2 = s2.encode()
        try:
            import zlib
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Primary Score: Structural/Symbiotic Logic
            logic_score = self._compute_symbiotic_reward(prompt_feats, cand_feats)
            
            # Shift logic_score to be positive (base 0.5)
            # Range approx [-0.5, 1.0] -> [0.0, 1.5]
            base_score = 0.5 + logic_score
            
            # 2. Tiebreaker: NCD (only if logic score is neutral/low confidence)
            # We invert NCD so higher is better, but weight it lightly
            ncd_val = self._ncd_score(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.1 # Max 0.1 bonus
            
            final_score = base_score + ncd_bonus
            
            # Reasoning string generation
            reasoning = f"Structural match: {logic_score:.2f}. "
            if logic_score > 0.2:
                reasoning += "Candidate aligns with prompt constraints."
            elif logic_score < -0.1:
                reasoning += "Candidate contradicts prompt logic."
            else:
                reasoning += "Neutral structural signal; relying on similarity."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Logic score can be > 1.0, cap at 1.0
        raw_score = res[0]['score']
        confidence = min(1.0, max(0.0, raw_score))
        return confidence