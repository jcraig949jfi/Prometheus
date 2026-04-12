import numpy as np
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Swarm-Abductive Neuromodulated Scorer (SANS) with Structural Primacy.
    
    Mechanism:
    1. Structural Parsing: Extracts binary/numeric features (negations, comparatives, 
       conditionals, causality, quantifiers) from prompt and candidates.
    2. Abductive Swarm: Agents sample feature masks based on pheromone trails (accumulated 
       support) modulated by a neuromodulatory gain factor.
    3. Evaluation: Agents score candidates based on how well their sampled features explain 
       the candidate's structural alignment with the prompt.
    4. Scoring: Final scores are derived from pheromone-weighted feature alignment, 
       falling back to NCD only when structural signals are weak.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(seed=42)
        self.rho = 0.1  # Evaporation rate
        self.g0 = 1.0   # Baseline gain
        self.kappa = 2.0 # Gain sensitivity
        self.T = 20     # Iterations
        
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|n\'t|never|no)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>=|<=|>|<)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|then|else)\b', re.I),
            'causal': re.compile(r'\b(cause|lead to|result in|because|therefore)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|none|every|each)\b', re.I),
            'ordering': re.compile(r'\b(before|after|first|last|next)\b', re.I),
            'number': re.compile(r'\d+\.?\d*')
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into a binary/numeric vector."""
        text_lower = text.lower()
        features = []
        
        # Binary flags
        features.append(1.0 if self.patterns['negation'].search(text_lower) else 0.0)
        features.append(1.0 if self.patterns['comparative'].search(text_lower) else 0.0)
        features.append(1.0 if self.patterns['conditional'].search(text_lower) else 0.0)
        features.append(1.0 if self.patterns['causal'].search(text_lower) else 0.0)
        features.append(1.0 if self.patterns['quantifier'].search(text_lower) else 0.0)
        features.append(1.0 if self.patterns['ordering'].search(text_lower) else 0.0)
        
        # Numeric magnitude (normalized simple count for stability)
        nums = self.patterns['number'].findall(text_lower)
        features.append(min(len(nums) / 10.0, 1.0)) 
        
        return np.array(features, dtype=np.float64)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        denom = max(len_s1, len_s2)
        if denom == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_feat = self._extract_features(prompt)
        n_feat = len(prompt_feat)
        n_agents = 10
        
        # Initialize swarm state
        # Pheromones start uniform
        pheromone = np.ones(n_feat) * 0.5
        agents = [
            {
                'pos': self.rng.integers(0, 2, size=n_feat).astype(float),
                'belief': 0.0,
                'gain': self.g0
            } for _ in range(n_agents)
        ]
        
        # Candidate feature matrix
        cand_feats = np.array([self._extract_features(c) for c in candidates])
        
        # Swarm Iterations
        for t in range(self.T):
            beliefs = []
            
            # 1. Abductive Proposal & 2. Evaluation
            for agent in agents:
                # Sample mask based on pheromone and gain
                prob = 1.0 / (1.0 + np.exp(-pheromone * agent['gain']))
                agent['pos'] = (self.rng.random(n_feat) < prob).astype(float)
                
                # Compute fit against all candidates (vectorized dot product)
                # We want candidates that match the prompt's structural profile
                # Fit = similarity between (agent_mask * prompt_feat) and (agent_mask * cand_feat)
                weighted_prompt = agent['pos'] * prompt_feat
                weighted_cands = cand_feats * agent['pos']
                
                # Dot product similarity normalized by mask weight
                fits = np.dot(weighted_cands, np.ones(n_feat)) / (np.sum(agent['pos']) + 1e-6)
                
                # Belief is average fit across candidates weighted by how well they match prompt structure
                # Simplified: Agent believes in features that appear in both prompt and candidate
                match_mask = (weighted_prompt > 0) & (weighted_cands > 0)
                agent['belief'] = np.sum(match_mask.astype(float)) / (np.sum(agent['pos']) + 1e-6)
                beliefs.append(agent['belief'])
            
            # 3. Pheromone Update (Stigmergy)
            pheromone *= (1 - self.rho)
            belief_arr = np.array(beliefs)
            # Normalize beliefs for deposition
            if np.max(belief_arr) > 0:
                norm_beliefs = belief_arr / (np.max(belief_arr) + 1e-6)
            else:
                norm_beliefs = belief_arr
                
            deposit = np.zeros(n_feat)
            for i, agent in enumerate(agents):
                deposit += norm_beliefs[i] * agent['pos']
            pheromone += deposit / n_agents
            
            # 4. Neuromodulation
            var = np.var(beliefs) if len(beliefs) > 1 else 0.0
            new_gain = self.g0 * np.exp(-self.kappa * var)
            for agent in agents:
                agent['gain'] = new_gain

        # Final Scoring
        scores = []
        for i, cand in enumerate(candidates):
            # Score = normalized pheromone-weighted feature sum
            raw_score = np.dot(pheromone, cand_feats[i])
            norm_factor = np.linalg.norm(pheromone) + 1e-6
            score = raw_score / norm_factor
            
            # NCD Tiebreaker logic: If structural score is very low/ambiguous, use NCD
            # But primarily, we want high structural alignment.
            # Invert NCD (0=identical, 1=different) to be a positive signal
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Hybrid score: Structural is primary. If structural signal is weak (< 0.1), 
            # rely more on NCD to avoid random noise dominating.
            if score < 0.1:
                final_score = 0.5 * score + 0.5 * ncd_score
            else:
                final_score = score
            
            scores.append({
                'candidate': cand,
                'score': float(final_score),
                'reasoning': f"Structural alignment score: {score:.4f}, NCD support: {ncd_score:.4f}"
            })
            
        # Rank descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural consistency."""
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Check for critical structural mismatches (e.g., negation flip)
        # If prompt has negation and answer doesn't (or vice versa), penalize
        neg_mismatch = abs(p_feat[0] - a_feat[0])
        cond_mismatch = abs(p_feat[2] - a_feat[2])
        
        base_conf = 0.8
        if neg_mismatch > 0:
            base_conf -= 0.4
        if cond_mismatch > 0:
            base_conf -= 0.2
            
        # Boost if numeric magnitudes align roughly
        if p_feat[6] > 0 and a_feat[6] > 0:
            ratio = min(p_feat[6], a_feat[6]) / max(p_feat[6], a_feat[6])
            base_conf = min(1.0, base_conf + 0.2 * ratio)
            
        return max(0.0, min(1.0, base_conf))