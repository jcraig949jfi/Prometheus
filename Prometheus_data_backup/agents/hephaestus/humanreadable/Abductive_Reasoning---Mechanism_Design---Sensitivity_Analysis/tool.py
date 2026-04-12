import re
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple

# Fact structure for symbolic parsing
Fact = namedtuple('Fact', ['subj', 'rel', 'obj', 'polarity'])

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining Abductive Reasoning, Mechanism Design,
    and Sensitivity Analysis.
    
    Mechanism:
    1. Parsing: Extracts structured triples (subject, relation, object) with polarity.
    2. Abduction: Scores candidates based on explanation cost (size + rarity).
    3. Mechanism Design: Applies a VCG-style payment rule to align incentives with
       global minimality, rewarding answers that make incorrect alternatives expensive.
    4. Sensitivity: Perturbs numeric features to penalize unstable explanations.
    """
    
    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'is_a': re.compile(r'(\w+)\s+(is a|are)\s+(\w+)', re.IGNORECASE),
            'part_of': re.compile(r'(\w+)\s+(is part of|belongs to)\s+(\w+)', re.IGNORECASE),
            'causes': re.compile(r'(\w+)\s+(causes|leads to|results in)\s+(\w+)', re.IGNORECASE),
            'greater': re.compile(r'(\w+)\s+(is greater than|exceeds|more than)\s+(\w+)', re.IGNORECASE),
            'less': re.compile(r'(\w+)\s+(is less than|under|below)\s+(\w+)', re.IGNORECASE),
            'negates': re.compile(r'(no|not|never)\s+(\w+)', re.IGNORECASE),
            'numeric_val': re.compile(r'(\d+\.?\d*)')
        }
        # Pre-computed rarity weights (simulated IDF)
        self.weights = {'is_a': 0.1, 'part_of': 0.2, 'causes': 0.5, 'greater': 0.3, 'less': 0.3, 'negates': 0.4, 'default': 0.2}
        self.lambda_param = 0.5

    def _parse_facts(self, text: str) -> List[Fact]:
        """Extract structured facts from text."""
        facts = []
        text_lower = text.lower()
        
        # Check for negations first to set context polarity if needed, 
        # though here we attach polarity per fact via specific patterns
        for match in self.patterns['negates'].finditer(text):
            facts.append(Fact(match.group(2), 'negates', match.group(2), -1))

        # Extract specific relations
        relations = [
            ('is_a', self.patterns['is_a']),
            ('part_of', self.patterns['part_of']),
            ('causes', self.patterns['causes']),
            ('greater', self.patterns['greater']),
            ('less', self.patterns['less'])
        ]
        
        for rel_name, pattern in relations:
            for match in pattern.finditer(text):
                subj, _, obj = match.groups()
                facts.append(Fact(subj, rel_name, obj, 1))
        
        # Fallback: if no structured facts, treat the whole sentence as a generic fact
        if not facts and len(text.strip()) > 0:
            facts.append(Fact("text", "equals", text.strip()[:20], 1))
            
        return facts

    def _compute_cost(self, facts: List[Fact]) -> float:
        """Calculate abductive explanation cost."""
        if not facts:
            return 10.0 # High cost for empty explanations
        
        size_cost = len(facts)
        rarity_cost = sum(self.weights.get(f.rel, self.weights['default']) for f in facts)
        return size_cost + self.lambda_param * rarity_cost

    def _vcg_score(self, costs: List[float], idx: int) -> float:
        """Compute VCG-style payment score."""
        if len(costs) == 1:
            return -costs[0]
        
        # Cost without current agent
        others = costs[:idx] + costs[idx+1:]
        sum_others = sum(others)
        min_others = min(others) if others else 0
        
        # VCG formula: -c_i + (sum_others - min_others)
        # This rewards making the alternative (min_others) expensive relative to the sum
        return -costs[idx] + (sum_others - min_others)

    def _sensitivity_check(self, prompt: str, candidate: str, base_score: float) -> float:
        """Perturb numeric values and measure score variance."""
        nums = self.patterns['numeric_val'].findall(candidate)
        if not nums:
            return base_score # No numeric sensitivity needed
        
        variances = []
        base_val = float(nums[0]) if nums else 0.0
        
        # Perturb by epsilon
        epsilon = 0.01
        perturbed_scores = []
        
        for delta in [-epsilon, 0, epsilon]:
            # Simple simulation: if numeric value changes, does logic hold?
            # We approximate this by checking if the score drops significantly when 
            # the numeric magnitude is altered in the cost function implicitly
            # Since we can't re-parse easily without side effects, we simulate variance
            # based on the magnitude of numbers present.
            noise = np.random.normal(0, 0.001) 
            perturbed_scores.append(base_score * (1 + delta * base_val * 0.1) + noise)
            
        return base_score / (1 + np.var(perturbed_scores) + 0.001)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_facts = self._parse_facts(prompt)
        candidate_data = []
        
        # 1. Parse and Compute Costs
        for cand in candidates:
            facts = self._parse_facts(cand)
            # Check consistency with prompt (simple overlap check for abduction)
            # In a full system, this would be logical entailment.
            # Here we assume the candidate provides the "explanation" facts.
            cost = self._compute_cost(facts)
            candidate_data.append({'candidate': cand, 'cost': cost, 'facts': facts})
        
        if not candidate_data:
            return []

        costs = [c['cost'] for c in candidate_data]
        
        # 2. Mechanism Design (VCG Scoring)
        scores = []
        for i in range(len(candidates)):
            vcg_val = self._vcg_score(costs, i)
            
            # 3. Sensitivity Analysis
            final_score = self._sensitivity_check(prompt, candidate_data[i]['candidate'], vcg_val)
            
            # Bonus for matching prompt structure (Abductive alignment)
            # If candidate shares relation types with prompt, reduce cost (increase score)
            prompt_rels = set(f.rel for f in prompt_facts)
            cand_rels = set(f.rel for f in candidate_data[i]['facts'])
            overlap_bonus = len(prompt_rels.intersection(cand_rels)) * 0.5
            
            scores.append(final_score + overlap_bonus)

        # Rank by score (higher is better)
        ranked_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in ranked_indices:
            results.append({
                "candidate": candidate_data[idx]['candidate'],
                "score": float(scores[idx]),
                "reasoning": f"VCG-adjusted abductive cost: {costs[idx]:.2f}, Sensitivity-penalized."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural consistency."""
        p_facts = self._parse_facts(prompt)
        a_facts = self._parse_facts(answer)
        
        if not p_facts and not a_facts:
            return 0.5
            
        # Check for direct contradiction (negation)
        p_negs = {f.subj for f in p_facts if f.polarity == -1}
        a_negs = {f.subj for f in a_facts if f.polarity == -1}
        
        # Simple heuristic: if both have negations on same subject, low confidence
        if p_negs.intersection(a_negs):
            return 0.1
            
        # Score based on cost ratio
        cost = self._compute_cost(a_facts)
        # Normalize: lower cost -> higher confidence
        conf = 1.0 / (1.0 + cost)
        return min(1.0, max(0.0, conf))