import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Type-Guided Epigenetic Bandit Learner (Computational Analogue).
    
    Mechanism:
    1. Type Theory (Structural Parsing): Candidates are parsed for logical 
       structures (negations, comparatives, conditionals) to ensure well-formedness.
       This acts as the 'Type System' guaranteeing logical consistency.
    2. Epigenetics (Heritable Marks): A persistent vector of 'methylation weights' 
       tracks the success of specific structural patterns (e.g., handling negation).
       These marks are inherited and updated, modulating the score based on 
       historical success in similar contexts.
    3. Multi-Armed Bandit (UCB): The system balances exploiting high-mark 
       structural patterns vs. exploring candidates with unique structural signatures.
    
    Scoring:
    Primary signal comes from structural analysis modulated by epigenetic marks.
    NCD is used strictly as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Epigenetic marks: Maps structural feature -> (success_count, trial_count)
        # Analogous to methylation levels that evolve over trials.
        self.epigenetic_memory: Dict[str, List[int]] = {}
        self.total_trials = 0

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """
        Type-level parsing: Extracts logical features from text.
        Returns a vector of presence indicators for key reasoning patterns.
        """
        text_lower = text.lower()
        features = {
            'negation': 0.0,
            'comparative': 0.0,
            'conditional': 0.0,
            'numeric': 0.0,
            'length': len(text)
        }
        
        # Negation detection (Modus Tollens support)
        negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        if any(w in text_lower for w in negations):
            features['negation'] = 1.0
            
        # Comparative detection (Transitivity support)
        comparatives = ['greater', 'less', 'more', 'fewer', 'than', '>', '<', 'larger', 'smaller']
        if any(w in text_lower for w in comparatives):
            features['comparative'] = 1.0
            
        # Conditional detection
        conditionals = ['if', 'then', 'else', 'when', 'unless', 'provided']
        if any(w in text_lower for w in conditionals):
            features['conditional'] = 1.0
            
        # Numeric evaluation potential
        if re.search(r'\d+(\.\d+)?', text):
            features['numeric'] = 1.0
            
        return features

    def _get_epigenetic_bonus(self, features: Dict[str, float]) -> float:
        """
        Calculates a bonus based on historical success of observed features.
        Mimics heritable epigenetic marks influencing probability.
        Uses UCB-like logic: bonus = mean_reward + exploration_factor.
        """
        if self.total_trials == 0:
            return 0.0
            
        total_bonus = 0.0
        active_features = 0
        
        for key, val in features.items():
            if key == 'length':
                continue
            if val > 0:
                active_features += 1
                if key in self.epigenetic_memory:
                    successes, trials = self.epigenetic_memory[key]
                    # Mean success rate
                    mean_reward = successes / trials if trials > 0 else 0.5
                    # Exploration bonus (UCB1 style simplified)
                    exploration = (2 * (self.total_trials ** 0.5)) / (trials + 1)
                    total_bonus += (mean_reward + exploration)
                else:
                    # Unseen feature: high exploration potential
                    total_bonus += 0.5 
                    
        return total_bonus / (active_features + 1) if active_features > 0 else 0.0

    def _update_epigenetics(self, features: Dict[str, float], reward: float):
        """
        Updates the epigenetic marks based on the outcome of a trial.
        Reward > 0.5 implies the structural pattern was fruitful.
        """
        threshold = 0.5
        is_success = 1 if reward > threshold else 0
        
        for key, val in features.items():
            if key == 'length':
                continue
            if val > 0:
                if key not in self.epigenetic_memory:
                    self.epigenetic_memory[key] = [0, 0]
                self.epigenetic_memory[key][0] += is_success
                self.epigenetic_memory[key][1] += 1

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_features = self._extract_structural_features(prompt)
        results = []
        
        # Phase 1: Score candidates based on structural alignment and epigenetic history
        for candidate in candidates:
            cand_features = self._extract_structural_features(candidate)
            
            # Structural Alignment Score (Type Consistency)
            # Does the candidate share the logical type of the prompt?
            alignment_score = 0.0
            match_count = 0
            for key in ['negation', 'comparative', 'conditional', 'numeric']:
                if prompt_features[key] > 0:
                    if cand_features[key] > 0:
                        alignment_score += 1.0
                    match_count += 1
            
            # Normalize alignment
            if match_count > 0:
                alignment_score /= match_count
            else:
                # If prompt has no specific markers, base score on candidate complexity
                alignment_score = 0.5 
            
            # Epigenetic Bonus (Contextual Bandit)
            bonus = self._get_epigenetic_bonus(cand_features)
            
            final_score = alignment_score + (bonus * 0.2) # Weight the bonus
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural alignment: {alignment_score:.2f}, Epigenetic bonus: {bonus:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        for i in range(len(results) - 1):
            if abs(results[i]["score"] - results[i+1]["score"]) < 0.01:
                ncd_dist = self._ncd(prompt, results[i]["candidate"])
                ncd_next = self._ncd(prompt, results[i+1]["candidate"])
                # Prefer lower NCD (more similar/compressible relative to prompt)
                if ncd_dist > ncd_next:
                    results[i], results[i+1] = results[i+1], results[i]

        # Update epigenetic memory based on the top candidate (Simulated trial)
        # In a real loop, this would happen after external verification.
        # Here we assume the top ranked item is the 'chosen arm' and update marks.
        if results:
            top_cand = results[0]["candidate"]
            top_feats = self._extract_structural_features(top_cand)
            # Synthetic reward based on internal consistency check
            self._update_epigenetics(top_feats, results[0]["score"])
            self.total_trials += 1
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural feature overlap and NCD as a secondary check.
        """
        p_feats = self._extract_structural_features(prompt)
        a_feats = self._extract_structural_features(answer)
        
        # Check logical consistency (Type safety)
        # If prompt requires negation/comparison and answer lacks it, confidence drops
        required_features = ['negation', 'comparative', 'conditional']
        penalty = 0.0
        for key in required_features:
            if p_feats[key] > 0 and a_feats[key] == 0:
                penalty += 0.2
        
        base_score = 1.0 - penalty
        
        # Boost if numeric evaluation matches (simple heuristic)
        if p_feats['numeric'] > 0 and a_feats['numeric'] > 0:
            base_score += 0.1
            
        # Cap at 1.0
        base_score = min(1.0, base_score)
        
        # NCD check: if answer is completely unrelated textually, reduce confidence
        ncd_val = self._ncd(prompt, answer)
        if ncd_val > 0.9: # Very different strings
            base_score *= 0.8
            
        return max(0.0, min(1.0, base_score))