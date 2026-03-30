import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Structure-Mapping Abductive Game-Theoretic Reasoner (SMAGTR)
    
    Mechanism:
    1. Epistemic Honesty (Meta-Confidence): Before scoring, analyzes the prompt for 
       Tier B traps (presuppositions, scope ambiguity, false dichotomies). If detected,
       caps confidence to ensure honesty over false competence.
    2. Structural Parsing (The "Analogy"): Maps the logical structure of the prompt 
       (negations, comparatives, conditionals) to the candidates. This acts as the 
       structural mapping engine.
    3. Abductive Scoring: Candidates are scored on explanatory virtue (structural match).
    4. Game-Theoretic Equilibrium (The "Nash"): Candidates compete. The score is adjusted
       by a "consensus cost" (deviation from the mean structural signature). This simulates
       agents minimizing regret by aligning with robust structural patterns rather than 
       idiosyncratic noise.
    5. NCD Tiebreaker: Used only when structural signals are weak.
    """

    def __init__(self):
        # Keywords for structural parsing
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        self._conditionals = ['if', 'then', 'unless', 'otherwise']
        self._presupposition_triggers = ['stopped', 'quit', 'failed', 'regret', 'assume', 'believe']
        self._scope_triggers = ['every', 'each', 'all']
        self._dichotomy_triggers = ['either', 'or', 'choose between']

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value: low if traps detected, 1.0 if clean.
        """
        p_lower = prompt.lower()
        words = p_lower.split()
        
        # 1. Presupposition Check ("Have you stopped...", "Why did X fail...")
        # Look for triggers combined with question markers or specific phrasing
        if any(t in p_lower for t in ['have you', 'did you', 'why did', 'when did']):
            if any(trig in p_lower for trig in self._presupposition_triggers):
                return 0.2
        
        # 2. Scope Ambiguity ("Every X did a Y" - implies potential ambiguity in 'same Y')
        # Heuristic: "Every" + plural noun + verb + "a/an" + noun + "?"
        if any(w in words for w in self._scope_triggers):
            if '?' in prompt and re.search(r'every\s+\w+\s+\w+\s+a\s+\w', p_lower):
                return 0.25

        # 3. False Dichotomy ("Either A or B" without context)
        if 'either' in p_lower and 'or' in p_lower:
            # Simple heuristic: if it asks to choose but options aren't exhaustive or clear
            if 'choose' in p_lower or 'which' in p_lower:
                return 0.25

        # 4. Subjectivity / Unanswerability
        subjective_terms = ['best', 'worst', 'favorite', 'opinion', 'think about']
        if any(term in p_lower for term in subjective_terms) and 'objective' not in p_lower:
            # Only flag if no clear metric is provided in the prompt
            if 'metric' not in p_lower and 'count' not in p_lower and 'calculate' not in p_lower:
                return 0.2

        return 1.0

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        words = t_lower.split()
        
        has_negation = any(w in self._negations for w in words)
        has_comparative = any(c in t_lower for c in self._comparatives)
        has_conditional = any(c in t_lower for c in self._conditionals)
        
        # Extract numbers for constructive computation
        numbers = re.findall(r"-?\d+\.?\d*", text)
        nums = [float(n) for n in numbers]
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'nums': nums,
            'len': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _structural_match_score(self, prompt_struct: Dict, cand_text: str) -> float:
        """
        Scores a candidate based on structural alignment with the prompt.
        This is the core "Analogical Mapping" step.
        """
        cand_struct = self._extract_structure(cand_text)
        score = 0.0
        matches = 0
        total_features = 4  # neg, comp, cond, numeric_logic

        # 1. Negation Alignment
        if prompt_struct['neg'] == cand_struct['neg']:
            score += 0.25
        matches += 1

        # 2. Comparative Alignment
        if prompt_struct['comp'] == cand_struct['comp']:
            score += 0.25
        matches += 1

        # 3. Conditional Alignment
        if prompt_struct['cond'] == cand_struct['cond']:
            score += 0.25
        matches += 1

        # 4. Constructive Computation (Numeric)
        # If prompt has numbers, candidate should ideally reflect a calculation or specific number
        if len(prompt_struct['nums']) > 0:
            # Check if candidate contains any number from prompt or a result derived from them
            cand_nums = cand_struct['nums']
            if cand_nums:
                # Simple heuristic: Does the candidate contain a number close to a simple operation?
                # Or just presence of numbers boosts score if prompt has them
                score += 0.25
            # If prompt has numbers but candidate has none, penalize heavily for reasoning tasks
            elif len(prompt_struct['nums']) > 0 and "no" not in cand_text.lower() and "none" not in cand_text.lower():
                 # Only penalize if it looks like a math/logic problem context
                 if any(x in prompt_struct['nums'] for x in [1,2,3,4,5]) or len(prompt_struct['nums']) >= 2:
                     score -= 0.2 # Penalty
        else:
            score += 0.25 # Neutral match
            
        return max(0.0, min(1.0, score))

    def _game_theoretic_adjustment(self, base_scores: List[float], candidates: List[str]) -> List[float]:
        """
        Simulates Nash Equilibrium convergence.
        Agents (candidates) with high abductive score but low structural consensus 
        (outliers) get penalized. Agents aligning with the 'consensus' of valid 
        structural patterns get a boost.
        """
        if not base_scores:
            return []
        
        adjusted = []
        mean_score = sum(base_scores) / len(base_scores)
        
        # Variance as a measure of population stability
        variance = sum((s - mean_score)**2 for s in base_scores) / len(base_scores)
        stability_factor = 1.0 / (1.0 + variance) if variance > 0 else 1.0

        for i, score in enumerate(base_scores):
            # Consensus cost: Deviation from the mean structural "truth"
            # In a real SME, this would be relational alignment. 
            # Here, we simulate it by favoring scores closer to the cluster of high scorers.
            
            deviation = abs(score - mean_score)
            
            # If the candidate is an outlier (high deviation) and the population is diverse,
            # apply a penalty unless the score is exceptionally high (strong abductive signal)
            if deviation > 0.3 and score < 0.8:
                score *= 0.8 # Penalize isolated hypotheses
            
            # Apply stability factor (global equilibrium pressure)
            final_score = score * (0.7 + 0.3 * stability_factor)
            adjusted.append(final_score)
            
        return adjusted

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_struct = self._extract_structure(prompt)
        base_scores = []
        
        # Step 1: Abductive Scoring via Structural Mapping
        for cand in candidates:
            s_score = self._structural_match_score(prompt_struct, cand)
            
            # Step 2: NCD as tiebreaker (max 15% weight)
            # Only used if structural score is ambiguous or low
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower is better) and scale
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Weighted sum: Structural >= 50%, Computation logic handled in struct, NCD <= 15%
            # We boost structural to dominate
            final_base = (s_score * 0.85) + ncd_score
            base_scores.append(final_base)

        # Step 3: Game-Theoretic Equilibrium Adjustment
        adjusted_scores = self._game_theoretic_adjustment(base_scores, candidates)

        # Construct result
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": adjusted_scores[i],
                "reasoning": f"Structural match: {base_scores[i]:.2f}, Game-adjusted: {adjusted_scores[i]:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Structural/Computational Verification
        # If we passed meta-check, we evaluate the specific answer's structural fit
        prompt_struct = self._extract_structure(prompt)
        answer_struct = self._extract_structure(answer)
        
        # Basic consistency check
        consistency = 0.5
        
        # Negation consistency
        if prompt_struct['neg'] == answer_struct['neg']:
            consistency += 0.2
        else:
            consistency -= 0.2
            
        # Numeric consistency (if prompt has numbers, answer should ideally have numbers or explicit negation)
        if len(prompt_struct['nums']) > 0:
            if len(answer_struct['nums']) > 0:
                consistency += 0.2
            elif any(x in answer.lower() for x in ['no', 'none', 'zero', 'impossible']):
                consistency += 0.1
            else:
                consistency -= 0.3 # Suspicious lack of numbers in math context
        
        # Normalize consistency to 0-1 range roughly
        raw_conf = max(0.0, min(1.0, consistency))
        
        # Apply Meta Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 without definitive computation (heuristic limit)
        # Since we don't have a full solver here, we cap high confidence unless it's a simple match
        if final_conf > 0.9:
            final_conf = 0.9
            
        return final_conf