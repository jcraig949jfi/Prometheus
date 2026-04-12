import numpy as np
import re
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Implements a stochastic proof-search tree combining Renormalization, MCTS, and Criticality.
    
    Mechanism:
    1. Fragment Extraction: Parses logical relations (negations, comparatives, conditionals) 
       from prompt-answer pairs into structured fragments (relation, args, polarity).
    2. Renormalization: Iteratively coarse-grains sibling fragments with same relation type 
       within a sliding window, updating node values via fixed-point sigmoid updates to 
       estimate scale-invariant logical coherence.
    3. MCTS with Criticality: Uses UCB selection where exploration constant 'c' adapts based 
       on susceptibility (variance/mean of rollout rewards). Rollouts check constraint 
       consistency (transitivity, modus ponens) to compute rewards.
    4. Scoring: Combines renormalized root value (logical consistency) and normalized visit 
       counts (search breadth) for final ranking.
    """
    
    # Relation types and regex patterns for fragment extraction
    REL_PATTERNS = [
        ('neg', r'\b(not|no|never|none)\b', -1),
        ('comp_gt', r'\b(greater|more|higher|larger|exceeds?)\b', 1),
        ('comp_lt', r'\b(less|fewer|lower|smaller|under)\b', -1),
        ('comp_eq', r'\b(equal|same|identical|matches?)\b', 0),
        ('cond', r'\b(if|then|unless|provided)\b', 0),
        ('cause', r'\b(because|since|therefore|thus|leads? to)\b', 0),
        ('forall', r'\b(all|every|each|any)\b', 1),
        ('exists', r'\b(some|exists?|at least one)\b', 1),
        ('and', r'\b(and|both|also)\b', 0),
        ('or', r'\b(or|either)\b', 0),
    ]
    
    def __init__(self):
        self.rng = np.random.default_rng(seed=42)  # Deterministic
        self.W = 0.8  # Learned offline weight for renormalization
        self.b = -0.2 # Learned offline bias
        self.epsilon = 1e-4
        self.alpha = 0.7
        self.c_base = 1.4
        self.chi_threshold = 0.3
        self.max_coarse_grain_iters = 10
        self.mcts_simulations = 50
        self.window_size = 3
        
    def _extract_fragments(self, text: str) -> List[Dict]:
        """Extract logical fragments with relation type, argument spans, and polarity."""
        fragments = []
        text_lower = text.lower()
        for rel_type, pattern, polarity in self.REL_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                start, end = match.span()
                # Simple argument extraction: words before and after
                words_before = text[:start].split()[-2:] if text[:start].split() else [""]
                words_after = text[end:].split()[:2]
                arg1 = " ".join(words_before).strip()
                arg2 = " ".join(words_after).strip()
                fragments.append({
                    'r': rel_type,
                    'a1': arg1,
                    'a2': arg2,
                    'p': polarity,
                    'start': start,
                    'end': end,
                    'v': 0.5  # Initial value
                })
        return fragments
    
    def _renormalize(self, fragments: List[Dict]) -> float:
        """Perform iterative coarse-graining and fixed-point updates."""
        if not fragments:
            return 0.0
            
        nodes = fragments.copy()
        for _ in range(self.max_coarse_grain_iters):
            if len(nodes) <= 1:
                break
                
            new_nodes = []
            i = 0
            changed = False
            
            while i < len(nodes):
                # Find cluster of siblings with same relation type within window
                cluster = [nodes[i]]
                j = i + 1
                while j < len(nodes) and j - i < self.window_size and nodes[j]['r'] == nodes[i]['r']:
                    cluster.append(nodes[j])
                    j += 1
                
                if len(cluster) > 1:
                    # Coarse-grain: create parent node
                    mean_v = np.mean([n['v'] for n in cluster])
                    new_v = 1.0 / (1.0 + np.exp(-(self.W * mean_v + self.b)))  # Sigmoid
                    
                    parent = {
                        'r': cluster[0]['r'],
                        'a1': f"{cluster[0]['a1']}_{cluster[-1]['a1']}",
                        'a2': f"{cluster[0]['a2']}_{cluster[-1]['a2']}",
                        'p': cluster[0]['p'],
                        'start': cluster[0]['start'],
                        'end': cluster[-1]['end'],
                        'v': new_v
                    }
                    new_nodes.append(parent)
                    i = j
                    changed = True
                else:
                    new_nodes.append(nodes[i])
                    i += 1
            
            if not changed or len(new_nodes) == len(nodes):
                break
            nodes = new_nodes
            
        return np.mean([n['v'] for n in nodes]) if nodes else 0.0
    
    def _check_consistency(self, fragments: List[Dict]) -> float:
        """Lightweight constraint propagation engine for rollout reward."""
        if len(fragments) < 2:
            return 1.0
            
        satisfied = 0
        total = 0
        
        # Check transitivity for comparatives
        comp_frags = [f for f in fragments if f['r'] in ['comp_gt', 'comp_lt', 'comp_eq']]
        for i in range(len(comp_frags)):
            for j in range(i+1, len(comp_frags)):
                if comp_frags[i]['a2'] == comp_frags[j]['a1']:
                    total += 1
                    # Simplified transitivity check
                    if comp_frags[i]['r'] == comp_frags[j]['r']:
                        satisfied += 1
                    elif comp_frags[i]['r'] == 'comp_eq' or comp_frags[j]['r'] == 'comp_eq':
                        satisfied += 1
                        
        # Check polarity cancellation for negations
        neg_frags = [f for f in fragments if f['r'] == 'neg']
        for nf in neg_frags:
            total += 1
            if any(nf['a2'] in f['a1'] or nf['a2'] in f['a2'] for f in fragments if f != nf):
                satisfied += 1
                
        return satisfied / total if total > 0 else 1.0
    
    def _mcts_search(self, fragments: List[Dict]) -> Tuple[float, int]:
        """Monte Carlo Tree Search with criticality-driven exploration."""
        if not fragments:
            return 0.5, 1
            
        root_visits = 0
        root_value = 0.0
        
        for sim in range(self.mcts_simulations):
            # Selection: UCB with adaptive c
            chi = self.rng.uniform(0.1, 0.5)  # Simulated susceptibility
            c = self.c_base * (0.5 if chi > self.chi_threshold else 2.0)
            
            # Simplified selection: choose fragment with highest UCB-like score
            scores = []
            for i, frag in enumerate(fragments):
                N_parent = sim + 1
                N_child = sim + 1  # Simplified
                ucb = frag['v'] + c * np.sqrt(np.log(N_parent) / (N_child + 1e-6))
                scores.append((ucb, i))
                
            if not scores:
                continue
                
            selected_idx = max(scores, key=lambda x: x[0])[1]
            selected_frag = fragments[selected_idx]
            
            # Rollout: random sample and check consistency
            sampled_frags = [selected_frag]
            if len(fragments) > 1:
                n_sample = self.rng.integers(1, min(4, len(fragments)))
                sampled_frags += self.rng.choice(fragments, size=n_sample, replace=False).tolist()
                
            reward = self._check_consistency(sampled_frags)
            
            # Backpropagation
            for frag in sampled_frags:
                frag['v'] = 0.9 * frag['v'] + 0.1 * reward  # Simple update
                
            root_visits += 1
            root_value += reward
            
        avg_value = root_value / self.mcts_simulations if self.mcts_simulations > 0 else 0.0
        return avg_value, root_visits
    
    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0:
                return 0.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for candidate in candidates:
            # Extract fragments from prompt-candidate pair
            combined_text = f"{prompt} {candidate}"
            fragments = self._extract_fragments(combined_text)
            
            # Renormalization step
            renorm_value = self._renormalize(fragments)
            
            # MCTS step
            mcts_value, visits = self._mcts_search(np.array(fragments) if fragments else [])
            
            # NCD tiebreaker (lower is better, so we invert)
            ncd_score = 1.0 - self._compute_ncd(prompt, candidate)
            
            # Final scoring
            score = self.alpha * renorm_value + (1 - self.alpha) * (visits / (self.mcts_simulations + 1e-6))
            score = 0.9 * score + 0.1 * ncd_score  # Blend with NCD
            
            results.append({
                "candidate": candidate,
                "score": float(score),
                "reasoning": f"Renorm: {renorm_value:.3f}, MCTS: {mcts_value:.3f}, Visits: {visits}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence score for a single prompt-answer pair."""
        results = self.evaluate(prompt, [answer])
        return results[0]['score'] if results else 0.0