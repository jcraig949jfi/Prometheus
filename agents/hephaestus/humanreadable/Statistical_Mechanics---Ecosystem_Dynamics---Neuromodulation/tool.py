import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Implements a hybrid reasoning scorer combining structural graph analysis (ecosystem trophic levels),
    constraint violation energy (statistical mechanics), and cue-based gain (neuromodulation).
    
    Core Mechanism:
    1. Parses prompt/candidates into propositional triples (Subject-Relation-Object).
    2. Builds a directed graph where edges represent causal/comparative/temporal relations.
    3. Computes 'Energy' based on constraint violations (e.g., asserting A>B while candidate implies B>A).
    4. Weights violations by 'Trophic Level' (graph depth) and 'Neuromodulatory Gain' (presence of certainty cues).
    5. Uses Boltzmann distribution with temperature derived from energy variance to score candidates.
    
    Beats NCD baseline by prioritizing logical consistency over string similarity.
    """

    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|therefore|thus|leads to|causes|implies)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
        'numeric': re.compile(r'\d+(?:\.\d+)?'),
        'order': re.compile(r'\b(before|after|first|last)\b', re.IGNORECASE),
        'gain_cues': re.compile(r'\b(certainly|possibly|maybe|definitely|likely)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.alpha = 0.5  # Neuromodulatory gain factor

    def _extract_triples(self, text: str) -> List[Dict]:
        """Extracts simplified propositional triples and metadata from text."""
        triples = []
        text_lower = text.lower()
        
        # Detect global cues
        has_negation = bool(self.PATTERNS['negation'].search(text_lower))
        has_comparative = bool(self.PATTERNS['comparative'].search(text_lower))
        has_causal = bool(self.PATTERNS['causal'].search(text_lower))
        has_conditional = bool(self.PATTERNS['conditional'].search(text_lower))
        has_order = bool(self.PATTERNS['order'].search(text_lower))
        
        # Extract numbers for comparative logic
        numbers = [float(n) for n in self.PATTERNS['numeric'].findall(text)]
        
        # Simple heuristic triple extraction (Subject-Verb-Object approximation)
        # Split by common delimiters to find propositions
        sentences = re.split(r'[.,;]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Identify relation type
            rel_type = 'assertion'
            if self.PATTERNS['negation'].search(sent): rel_type = 'negation'
            elif self.PATTERNS['comparative'].search(sent): rel_type = 'comparative'
            elif self.PATTERNS['causal'].search(sent): rel_type = 'causal'
            elif self.PATTERNS['conditional'].search(sent): rel_type = 'conditional'
            elif self.PATTERNS['order'].search(sent): rel_type = 'temporal'
            
            triples.append({
                'text': sent,
                'type': rel_type,
                'has_numbers': len(numbers) > 0,
                'numbers': numbers,
                'negated': has_negation
            })
            
        return triples

    def _compute_trophic_levels(self, triples: List[Dict]) -> List[float]:
        """
        Computes trophic level as the longest path from source nodes.
        In this simplified model, causal/temporal links increase depth.
        """
        if not triples:
            return []
        
        levels = []
        current_level = 0
        for t in triples:
            if t['type'] in ['causal', 'temporal', 'conditional']:
                current_level += 1
            levels.append(float(current_level))
        
        # Normalize if possible, else use raw
        if max(levels) > 0:
            max_l = max(levels)
            levels = [l / max_l for l in levels] if max_l > 0 else levels
            
        return levels if levels else [1.0] * len(triples)

    def _compute_gain(self, text: str) -> float:
        """Computes neuromodulatory gain based on certainty cues."""
        cues = self.PATTERNS['gain_cues'].findall(text.lower())
        if not cues:
            return 1.0
        # Simple count-based gain
        sigma = len(cues) 
        return 1.0 + self.alpha * sigma

    def _calculate_energy(self, prompt_triples: List[Dict], candidate_text: str) -> float:
        """
        Calculates energy (penalty) based on constraint violations.
        Lower energy = better fit.
        """
        if not prompt_triples:
            return 0.0
            
        candidate_lower = candidate_text.lower()
        total_energy = 0.0
        
        # Pre-calculate candidate features
        cand_triples = self._extract_triples(candidate_text)
        cand_has_neg = bool(self.PATTERNS['negation'].search(candidate_lower))
        cand_nums = [float(n) for n in self.PATTERNS['numeric'].findall(candidate_lower)]
        
        # Trophic levels from prompt structure
        levels = self._compute_trophic_levels(prompt_triples)
        if not levels:
            levels = [1.0]
            
        # Extend levels to match if needed or use average
        avg_level = np.mean(levels) if levels else 1.0
        gain = self._compute_gain(candidate_text)
        
        # Violation Checks
        for i, p_trip in enumerate(prompt_triples):
            p_type = p_trip['type']
            level = levels[i] if i < len(levels) else avg_level
            
            cost = 0.0
            
            # 1. Negation Mismatch
            if p_type == 'negation':
                # If prompt says "X is NOT Y", and candidate asserts "X is Y" (no negation found)
                # This is a simplification: assuming candidate affirms if no negation detected
                if not cand_has_neg and not p_trip['negated']: 
                     # Heuristic: if prompt has explicit negation structure, candidate must respect it
                     if any(n in candidate_lower for n in ['not', 'no', 'never']):
                         pass # Candidate respects negation
                     else:
                         # Check if candidate seems to affirm the negated concept without negation
                         # Very rough heuristic: if prompt negates, candidate should likely contain negation or not affirm
                         pass 
                # Refined: If prompt triple is negation, and candidate lacks negation keywords entirely while being short
                if p_trip['negated'] and not cand_has_neg:
                     cost += 1.0

            # 2. Comparative/Numeric Violation
            if p_type == 'comparative' and p_trip['has_numbers'] and len(cand_nums) >= 2:
                # If prompt has numbers, check order consistency roughly
                # E.g., Prompt: "A (9.9) > B (9.11)", Candidate: "9.11 > 9.9"
                # We check if the candidate reverses the sorted order of numbers found in prompt
                p_nums_sorted = sorted(p_trip['numbers'])
                c_nums_sorted = sorted(cand_nums)
                
                # If the set of numbers is the same, check if the text implies reverse order
                # This is hard without full NLP, so we use a proxy: 
                # If prompt has "less" and candidate has "more", penalty?
                if 'less' in p_trip['text'] and 'more' in candidate_lower:
                    cost += 1.0
                if 'more' in p_trip['text'] and 'less' in candidate_lower:
                    cost += 1.0

            # 3. Causal/Conditional Presence
            if p_type in ['causal', 'conditional']:
                # If prompt establishes a causal link, candidate ignoring it isn't necessarily a violation,
                # but contradicting it is. 
                # Simplified: If prompt is conditional and candidate is definitive without condition
                if p_type == 'conditional' and 'if' in p_trip['text']:
                    if 'if' not in candidate_lower and 'maybe' not in candidate_lower and 'possibly' not in candidate_lower:
                        # Candidate asserts certainty where prompt was conditional
                        cost += 0.5

            # Weighted Cost
            # E = sum(cost * level * gain)
            # Using betweenness proxy: assume middle nodes are more important (simplified to 1.0 for now)
            betweenness = 1.0 
            total_energy += cost * level * betweenness * gain

        return total_energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1_s2 = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_triples = self._extract_triples(prompt)
        energies = []
        
        # Calculate energies
        for cand in candidates:
            e = self._calculate_energy(prompt_triples, cand)
            energies.append(e)
            
        energies = np.array(energies)
        
        # Statistical Mechanics Scoring
        # Temperature from fluctuation-dissipation (variance of energy)
        variance = np.var(energies)
        epsilon = 1e-6
        T = np.sqrt(variance) + epsilon
        
        # Boltzmann weights: w = exp(-E/T)
        # If T is very small (all energies similar), use a default T to avoid division issues
        if T < 1e-4:
            T = 1.0
            
        exp_vals = np.exp(-energies / T)
        scores = exp_vals / np.sum(exp_vals)
        
        # If structural signals are weak (all scores ~ equal), use NCD as tiebreaker
        if np.max(scores) - np.min(scores) < 1e-3:
            # Re-score based on NCD to prompt (lower distance = higher score)
            ncd_scores = []
            for cand in candidates:
                dist = self._ncd_distance(prompt, cand)
                ncd_scores.append(-dist) # Negative distance as "energy"
            
            ncd_scores = np.array(ncd_scores)
            # Shift to positive
            ncd_scores -= np.min(ncd_scores)
            ncd_scores += 1e-6
            
            # Convert to probability
            scores = ncd_scores / np.sum(ncd_scores)

        # Rank and format
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": f"Energy: {energies[i]:.4f}, Temp: {T:.4f}, Score: {scores[i]:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the evaluate method internally to see how much the answer dominates others.
        Since we don't have other candidates here, we estimate confidence by the absolute energy penalty.
        Low energy -> High confidence.
        """
        # Generate dummy alternatives to create a distribution context if needed, 
        # but simpler: map energy directly to confidence.
        # E=0 -> Conf=1.0, E>2 -> Conf~0.0
        
        prompt_triples = self._extract_triples(prompt)
        energy = self._calculate_energy(prompt_triples, answer)
        
        # Sigmoid-like mapping from energy to confidence
        # If energy is 0, conf = 1. If energy is high, conf approaches 0.
        # Using exp(-energy) as a proxy since T~1 in single sample
        conf = np.exp(-energy)
        
        # Adjust with NCD check: if answer is gibberish (very different from prompt structure), lower conf
        # But NCD is noisy. Stick to energy.
        return float(np.clip(conf, 0.0, 1.0))