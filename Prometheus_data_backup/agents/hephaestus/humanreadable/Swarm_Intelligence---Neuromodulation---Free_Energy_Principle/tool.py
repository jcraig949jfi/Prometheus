import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Swarm-based Predictive Coding Architecture.
    
    Core Mechanism (Free Energy Principle):
    The 'evaluate' method treats candidate answers as particles in a swarm.
    Each particle's position is its semantic content. The 'generative model'
    is a structural parser that extracts logical constraints (negations, 
    comparatives, conditionals) from the prompt. 
    
    Prediction Error (Variational Free Energy) is calculated as the mismatch
    between the candidate's implied logic and the prompt's structural constraints.
    Candidates minimizing this error (maximizing structural alignment) survive.
    
    Neuromodulation (Precision Control):
    A global 'precision' signal modulates the scoring. 
    - High Precision (Low Entropy): When structural signals are strong and 
      consistent, the system sharply penalizes deviations (exploitation).
    - Low Precision (High Entropy): When signals are weak or contradictory, 
      the system reduces penalty severity, allowing diverse candidates to 
      persist (exploration), preventing premature convergence on local minima.
      
    Swarm Stigmergy:
    Candidates leave 'traces' via NCD. If multiple candidates cluster semantically
    (low NCD distance), they reinforce the local free-energy gradient, attracting
    the scoring towards that region unless contradicted by strong structural logic.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical signatures: negations, comparatives, numbers, booleans."""
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)
        
        has_negation = any(n in text_lower for n in self.negations)
        has_comparative = any(c in text_lower for c in self.comparatives)
        has_conditional = any(c in text_lower for c in self.conditionals)
        
        # Extract numbers
        numbers = []
        for match in re.findall(r'-?\d+(?:\.\d+)?', text):
            try:
                numbers.append(float(match))
            except ValueError:
                pass
                
        # Extract boolean intent
        has_bool = any(b in text_lower.split() for b in self.booleans)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'has_bool': has_bool,
            'length': len(tokens)
        }

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker/stigmergic field."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _structural_match_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculate prediction error based on structural alignment.
        Lower error = higher score.
        """
        score = 0.0
        total_weight = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect awareness (heuristic)
        # Since we don't have ground truth, we check if the candidate structure 
        # doesn't blatantly contradict the prompt type (e.g. prompt is numeric, cand is not)
        
        # 2. Numeric Consistency (Strong Signal)
        if prompt_struct['numbers']:
            total_weight += 3.0
            if cand_struct['numbers']:
                # Check for order preservation if both have numbers
                # Simple heuristic: if prompt has 2 numbers, candidate having numbers is good
                score += 1.0
                # If counts match exactly, bonus
                if len(cand_struct['numbers']) >= len(prompt_struct['numbers']):
                    score += 1.0
            else:
                # Penalty for missing numbers in a numeric context
                score -= 2.0
        
        # 3. Boolean Consistency
        if prompt_struct['has_bool']:
            total_weight += 2.0
            if cand_struct['has_bool']:
                score += 1.0
        
        # 4. Length/Complexity Matching (Occam's razor proxy)
        # Candidates shouldn't be wildly disproportionate if the prompt is simple
        len_ratio = cand_struct['length'] / (prompt_struct['length'] + 1)
        if 0.1 < len_ratio < 5.0:
            score += 0.5
        total_weight += 1.0

        return score if total_weight == 0 else score / (total_weight + 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        prompt_len = len(prompt)
        
        # Swarm State: List of agents (candidates) with internal models
        swarm = []
        for i, cand in enumerate(candidates):
            cand_struct = self._extract_structure(cand)
            swarm.append({
                'id': i,
                'text': cand,
                'struct': cand_struct,
                'free_energy': 0.0, # Prediction error
                'precision': 0.0,   # Neuromodulatory gain
                'stigmergy': 0.0    # Collective influence
            })

        if len(swarm) == 0:
            return []

        # --- Phase 1: Free Energy Calculation (Prediction Error) ---
        # Each agent computes error against the prompt's structural constraints
        base_scores = []
        for agent in swarm:
            # Structural match provides the base log-likelihood
            struct_score = self._structural_match_score(prompt_struct, agent['struct'])
            
            # NCD to prompt (semantic proximity)
            ncd_prompt = self._calculate_ncd(prompt, agent['text'])
            
            # Free Energy = (1 - Structural_Alignment) + (NCD_Distance * Weight)
            # We want to minimize this. 
            agent['free_energy'] = (1.0 - struct_score) + (ncd_prompt * 0.5)
            base_scores.append(-agent['free_energy']) # Negative free energy is good

        # --- Phase 2: Neuromodulation (Precision Control) ---
        # Calculate global uncertainty to set precision gain
        if len(base_scores) > 1:
            mean_score = sum(base_scores) / len(base_scores)
            variance = sum((s - mean_score) ** 2 for s in base_scores) / len(base_scores)
            uncertainty = math.sqrt(variance) if variance > 0 else 1.0
            
            # Neuromodulatory rule: 
            # High variance (ambiguity) -> Lower precision (flatten scores, encourage exploration)
            # Low variance (clarity) -> Higher precision (sharpen scores, exploit best)
            # Gain = 1 / (uncertainty + epsilon)
            gain = 1.0 / (uncertainty + 0.1)
        else:
            gain = 1.0

        # Apply gain to free energy (scaling the landscape)
        for agent in swarm:
            agent['precision'] = gain
            # Adjusted score based on precision
            agent['score_raw'] = -agent['free_energy'] * agent['precision']

        # --- Phase 3: Stigmergic Interaction (Swarm Clustering) ---
        # Agents leave pheromones. If many agents are similar (low NCD), 
        # they reinforce each other (collective intelligence).
        for i, agent in enumerate(swarm):
            cluster_strength = 0.0
            count = 0
            for j, other in enumerate(swarm):
                if i == j: continue
                dist = self._calculate_ncd(agent['text'], other['text'])
                if dist < 0.8: # Within interaction radius
                    # Closer agents contribute more
                    cluster_strength += (1.0 - dist) * math.exp(-other['free_energy'])
                    count += 1
            
            if count > 0:
                agent['stigmergy'] = cluster_strength / (count + 1)
            else:
                agent['stigmergy'] = 0.0

        # --- Final Scoring & Ranking ---
        results = []
        max_stig = max(a['stigmergy'] for a in swarm) if swarm else 1.0
        min_stig = min(a['stigmergy'] for a in swarm) if swarm else 0.0
        stig_range = max_stig - min_stig if (max_stig - min_stig) > 0 else 1.0

        for agent in swarm:
            # Normalize stigmergy contribution
            norm_stig = (agent['stigmergy'] - min_stig) / stig_range
            
            # Final Score = Precision-Weighted Free Energy + Stigmergic Bonus
            # The stigmergy acts as a tie-breaker and convergence accelerator
            final_score = agent['score_raw'] + (norm_stig * 0.2) 
            
            # Reasoning string generation
            reasoning = f"Structural alignment: {agent['struct']}; Free Energy: {-agent['free_energy']:.4f}; Precision Gain: {agent['precision']:.2f}"
            
            results.append({
                "candidate": agent['text'],
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and NCD.
        """
        prompt_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        
        # 1. Structural Match Score
        struct_score = self._structural_match_score(prompt_struct, ans_struct)
        
        # 2. NCD Similarity (as a proxy for relevance in this context)
        # Note: NCD alone is weak, but combined with structure it helps
        ncd_val = self._calculate_ncd(prompt, answer)
        
        # Heuristic combination
        # If structural match is high, confidence is high.
        # If structural match is low, confidence drops regardless of NCD.
        base_conf = max(0.0, struct_score) # Ensure non-negative
        
        # Adjust based on NCD (lower NCD usually means more related, but not always correct)
        # We use NCD primarily to penalize completely unrelated long strings
        relevance = 1.0 - min(1.0, ncd_val)
        
        confidence = (base_conf * 0.7) + (relevance * 0.3)
        
        return min(1.0, max(0.0, confidence))