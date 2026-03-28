import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Organizing Description-Length Guided Swarm (SODL-GS).
    
    Mechanism:
    1. Agents (candidates) are evaluated on structural reasoning tasks (negation, logic, math).
    2. Network Science: Candidates form a dynamic graph where edge weights represent 
       'pheromone' strength based on structural agreement and complexity penalties.
    3. Kolmogorov Complexity: Approximated via LZ78 (zlib) compression length. 
       Shorter valid explanations receive higher 'pheromone' deposits.
    4. Swarm Dynamics: Scores are updated iteratively. Candidates gain score from 
       neighbors with high structural validity and low complexity.
    5. Community Detection: Implicitly handled by clustering candidates with similar 
       structural signatures; the global selector picks the highest scoring cluster representative.
    
    This approach prioritizes structural correctness (Reasoning) while using compression 
    (Kolmogorov) as a tie-breaking regularizer to prevent overfitting (Occam's Razor).
    """

    def __init__(self):
        self._structure_cache = {}

    def _get_complexity(self, text: str) -> int:
        """Approximate Kolmogorov complexity using zlib compression length."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _extract_structure(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, numbers, conditionals."""
        t_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none|cannot)\b', t_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', t_lower)),
            'numbers': re.findall(r'\d+(?:\.\d+)?', t_lower),
            'length': len(text)
        }
        # Normalize numbers for comparison logic
        try:
            features['numeric_value'] = float(features['numbers'][0]) if features['numbers'] else None
        except ValueError:
            features['numeric_value'] = None
        return features

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring based on structural parsing and constraint propagation.
        Returns a score between 0.0 and 1.0 based on logical consistency.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        score = 0.5  # Base prior
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation, valid answers often acknowledge it or flip logic
        if p_feat['negations'] > 0:
            # Reward candidates that also show logical awareness (not just echoing)
            if c_feat['negations'] > 0 or c_feat['conditionals'] > 0:
                score += 0.2
            else:
                # Penalty for ignoring explicit negation constraints in prompt
                score -= 0.1
        
        # 2. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            p_nums = [float(n) for n in p_feat['numbers']]
            c_nums = [float(n) for n in c_feat['numbers']]
            
            # Check for direct answer match or logical derivation
            if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                score += 0.3 # Direct numeric hit
            elif len(c_nums) == 1 and len(p_nums) == 2:
                # Simple arithmetic check (e.g., prompt "2 2", candidate "4")
                if abs(sum(p_nums) - c_nums[0]) < 1e-6 or abs(p_nums[0] * p_nums[1] - c_nums[0]) < 1e-6:
                    score += 0.4

        # 3. Comparative Logic
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0 or c_feat['numbers']:
                score += 0.15
        
        # 4. Length Constraint (Occam's razor heuristic)
        # Heavily penalize if candidate is just a copy-paste of prompt
        if candidate.strip() == prompt.strip():
            score = 0.0
            
        return max(0.0, min(1.0, score))

    def _swarm_interaction(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Simulate swarm interaction on an adaptive graph.
        Nodes = candidates. Edges formed by structural similarity.
        Pheromone = Structural Score / Complexity.
        """
        n = len(candidates)
        if n == 0:
            return []
        
        # Step 1: Initialize Node States (Structural Scores & Complexity)
        node_data = []
        for cand in candidates:
            struct_score = self._structural_score(prompt, cand)
            complexity = self._get_complexity(cand)
            # Avoid division by zero; add small epsilon
            k_penalty = 1.0 / (complexity + 1) 
            node_data.append({
                'candidate': cand,
                'struct_score': struct_score,
                'complexity': complexity,
                'pheromone': struct_score * k_penalty, # Initial deposit
                'neighbors': []
            })

        # Step 2: Network Rewiring (Preferential Attachment based on structural similarity)
        # Build adjacency based on feature overlap
        for i in range(n):
            for j in range(i + 1, n):
                feat_i = self._extract_structure(node_data[i]['candidate'])
                feat_j = self._extract_structure(node_data[j]['candidate'])
                
                # Simple similarity: shared number presence or negation status
                sim = 0
                if (feat_i['numbers'] and feat_j['numbers']): sim += 0.5
                if (feat_i['negations'] > 0) == (feat_j['negations'] > 0): sim += 0.5
                
                if sim > 0.5:
                    node_data[i]['neighbors'].append(j)
                    node_data[j]['neighbors'].append(i)

        # Step 3: Iterative Swarm Update (Diffusion of Pheromones)
        # Agents update their score based on neighbors with high utility/low complexity
        iterations = 2
        for _ in range(iterations):
            new_pheromones = [d['pheromone'] for d in node_data]
            for i, node in enumerate(node_data):
                if node['neighbors']:
                    neighbor_scores = [node_data[n_idx]['pheromone'] for n_idx in node['neighbors']]
                    avg_neighbor_quality = sum(neighbor_scores) / len(neighbor_scores)
                    
                    # Update rule: Blend own score with neighborhood consensus
                    # High complexity nodes are dampened faster if neighbors are good
                    decay = 0.8 if node['complexity'] > 50 else 0.95
                    node_data[i]['pheromone'] = (decay * node['pheromone']) + (0.2 * avg_neighbor_quality)
                else:
                    # Isolated nodes rely purely on structural score but decay slightly
                    node_data[i]['pheromone'] *= 0.9 

        # Step 4: Aggregation and Ranking
        results = []
        for i, node in enumerate(node_data):
            # Final Score combines structural validity and swarm consensus
            final_score = (0.6 * node['struct_score']) + (0.4 * node['pheromone'])
            
            reasoning = f"Structural:{node['struct_score']:.2f} | Complexity:{node['complexity']} | Swarm:{node['pheromone']:.2f}"
            results.append((node['candidate'], final_score, reasoning))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        ranked = self._swarm_interaction(prompt, candidates)
        return [
            {"candidate": cand, "score": score, "reasoning": reason}
            for cand, score, reason in ranked
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses structural alignment and complexity penalty.
        """
        struct_score = self._structural_score(prompt, answer)
        complexity = self._get_complexity(answer)
        
        # Normalize complexity penalty (assume typical answer < 500 chars is good)
        complexity_penalty = min(1.0, complexity / 500.0)
        
        # Confidence is high if structural score is high AND complexity is reasonable
        base_conf = struct_score * (1.0 - (complexity_penalty * 0.5))
        
        return max(0.0, min(1.0, base_conf))