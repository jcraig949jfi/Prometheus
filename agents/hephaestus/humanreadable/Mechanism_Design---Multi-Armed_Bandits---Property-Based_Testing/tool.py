import re
import math
import zlib
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    Bandit-Driven Property-Based Scoring with Proper-Scoring Incentives.
    
    Mechanism:
    1. Parses prompts for logical constraints (negations, comparatives, conditionals).
    2. Generates synthetic test cases (hypotheses) based on detected patterns.
    3. Uses UCB1 (Multi-Armed Bandit) to allocate evaluation budget across candidates.
    4. Scores based on constraint satisfaction (Property-Based Testing) with Mechanism Design incentives.
    5. Integrates Epistemic Honesty (Tier B) to cap confidence on ambiguous/unanswerable prompts.
    """

    def __init__(self):
        # Patterns for structural parsing
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'>', r'<', r'>=', r'<=', r'more than', r'less than', r'greater', r'smaller'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly if\b'],
            'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', r'\bpreceded\b'],
            'numeric': r'\d+(\.\d+)?',
            'presupposition': [r'have you stopped', r'why did .+ fail', r'why did .+ stop', r'when did .+ stop'],
            'ambiguity': [r'every .+ (a|an) .+', r'told .+ he', r'told .+ she', r'either .+ or'],
            'subjectivity': [r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bopinion\b']
        }
        self.budget = 200  # Total bandit pulls per evaluation

    def _extract_constraints(self, prompt: str) -> List[str]:
        """Extract atomic logical predicates from the prompt."""
        constraints = []
        p_lower = prompt.lower()
        
        if any(re.search(p, p_lower) for p in self.patterns['negation']):
            constraints.append('negation_present')
        if any(re.search(p, p_lower) for p in self.patterns['comparative']):
            constraints.append('comparative_present')
        if any(re.search(p, p_lower) for p in self.patterns['conditional']):
            constraints.append('conditional_present')
        if any(re.search(p, p_lower) for p in self.patterns['causal']):
            constraints.append('causal_present')
        if any(re.search(p, p_lower) for p in self.patterns['ordering']):
            constraints.append('ordering_present')
        
        # Numeric extraction
        nums = re.findall(self.patterns['numeric'], prompt)
        if len(nums) >= 2:
            constraints.append('numeric_comparison')
            
        return constraints if constraints else ['default_logic']

    def _generate_test_case(self, prompt: str, constraints: List[str]) -> Dict[str, Any]:
        """Generate a synthetic input scenario based on constraints."""
        # Simplified hypothesis generation: creates a scenario dict
        # In a full system, this would use Hypothesis library logic
        import random
        random.seed(hash(prompt) % (2**32)) # Deterministic per prompt
        
        case = {
            'values': [random.uniform(1, 100) for _ in range(5)],
            'flags': [random.choice([True, False]) for _ in range(3)],
            'order': list(range(5))
        }
        random.shuffle(case['order'])
        return case

    def _evaluate_candidate_on_case(self, candidate: str, prompt: str, case: Dict, constraints: List[str]) -> float:
        """
        Evaluate if a candidate answer holds up against a generated test case.
        Returns 1.0 if consistent, 0.0 if violation found.
        """
        violations = 0
        total_checks = 0
        
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        # 1. Negation Check
        if 'negation_present' in constraints:
            total_checks += 1
            # Heuristic: If prompt says "not", answer should not strongly affirm without qualification
            # This is a simplified logical check
            if 'yes' in c_lower and 'not' not in c_lower and 'no' not in c_lower:
                # Potential violation if the logic requires negation
                if any(re.search(p, p_lower) for p in self.patterns['negation']):
                    violations += 0.5 # Soft penalty for now, relies on context

        # 2. Comparative Check
        if 'comparative_present' in constraints:
            total_checks += 1
            # Extract numbers from candidate
            c_nums = re.findall(self.patterns['numeric'], candidate)
            if len(c_nums) >= 2:
                try:
                    v1, v2 = float(c_nums[0]), float(c_nums[1])
                    if 'greater' in p_lower or '>' in p_lower or 'more than' in p_lower:
                        if v1 <= v2: violations += 1
                    elif 'less' in p_lower or '<' in p_lower:
                        if v1 >= v2: violations += 1
                except: pass

        # 3. Structural Consistency (Basic)
        # If prompt asks for order, check if candidate has list-like structure or numbers
        if 'ordering_present' in constraints:
            total_checks += 1
            if not re.search(r'\d', candidate) and len(candidate.split()) < 3:
                violations += 0.5 # Suspiciously short for ordering task

        # Default: If no specific violations found in this random projection, assume pass
        if total_checks == 0:
            return 1.0
            
        return max(0.0, 1.0 - (violations / total_checks))

    def _bandit_scoring(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """Run UCB1 bandit algorithm to score candidates."""
        if not candidates:
            return []
            
        constraints = self._extract_constraints(prompt)
        n_arms = len(candidates)
        counts = [1] * n_arms  # Initialize with 1 to avoid div-by-zero
        rewards = [0.0] * n_arms
        total_pulls = n_arms
        
        # Initial pull: evaluate each once
        for i, cand in enumerate(candidates):
            case = self._generate_test_case(prompt, constraints)
            r = self._evaluate_candidate_on_case(cand, prompt, case, constraints)
            rewards[i] = r
            
        # Bandit loop
        while total_pulls < self.budget:
            ucb_values = []
            for i in range(n_arms):
                if counts[i] == 0:
                    ucb_values.append(float('inf'))
                else:
                    avg = rewards[i] / counts[i]
                    exploration = math.sqrt((2 * math.log(total_pulls + 1)) / counts[i])
                    ucb_values.append(avg + exploration)
            
            arm = max(range(n_arms), key=lambda i: ucb_values[i])
            
            # Pull arm
            case = self._generate_test_case(prompt, constraints)
            r = self._evaluate_candidate_on_case(candidates[arm], prompt, case, constraints)
            
            rewards[arm] += r
            counts[arm] += 1
            total_pulls += 1
            
        # Final scores
        final_scores = [(candidates[i], rewards[i]/counts[i]) for i in range(n_arms)]
        return final_scores

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if any(re.search(p, p_lower) for p in self.patterns['presupposition']):
            return 0.2
            
        # 2. Ambiguity traps (Pronouns, Scope)
        if any(re.search(p, p_lower) for p in self.patterns['ambiguity']):
            # Only penalize if question asks for clarification or identity
            if 'who' in p_lower or 'which' in p_lower or 'same' in p_lower:
                return 0.25
                
        # 3. False Dichotomy
        if 'either' in p_lower and 'or' in p_lower and 'possible' not in p_lower:
             if 'must' in p_lower or 'choose' in p_lower:
                return 0.3

        # 4. Subjectivity without criteria
        if any(re.search(p, p_lower) for p in self.patterns['subjectivity']):
            if 'fact' not in p_lower and 'calculate' not in p_lower:
                return 0.3

        # 5. Unanswerability (Missing info heuristic)
        # If prompt is very short and lacks numbers/logic keywords
        words = re.findall(r'\b\w+\b', prompt)
        if len(words) < 4 and not any(k in p_lower for k in ['is', 'are', 'do', 'does']):
            return 0.1

        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Scoring (Bandit)
        scored_candidates = self._bandit_scoring(prompt, candidates)
        
        results = []
        for cand, raw_score in scored_candidates:
            # Apply meta cap
            final_score = min(raw_score, meta_cap)
            
            # NCD Tiebreaker (Max 15% influence)
            # If scores are very close, prefer candidate with lower NCD to prompt (more relevant)
            ncd_val = self._ncd_score(prompt, cand)
            # Normalize NCD to be a small bonus (lower NCD = higher similarity = better)
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            # Weighted combination: 85% Bandit, 15% NCD
            composite_score = (final_score * 0.85) + (ncd_bonus * 0.15)
            
            # Ensure we don't exceed the meta_cap even with bonus if cap is low (honesty)
            if meta_cap < 0.5:
                composite_score = min(composite_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": composite_score,
                "reasoning": f"Bandit Score: {raw_score:.2f}, Meta Cap: {meta_cap:.2f}, NCD Bonus applied."
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by meta-analysis of the prompt for ambiguity.
        """
        # 1. Check Prompt Properties (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. If prompt is clean, check structural match
        if cap > 0.8:
            # Run a mini-evaluation
            constraints = self._extract_constraints(prompt)
            # If we have strong structural signals, confidence can be higher
            if len(constraints) > 1:
                # Simulate one bandit pull
                case = self._generate_test_case(prompt, constraints)
                raw_score = self._evaluate_candidate_on_case(answer, prompt, case, constraints)
                base_conf = raw_score
            else:
                # Weak structure, moderate confidence max
                base_conf = 0.6
        else:
            base_conf = 0.1 # Low base if prompt is bad
            
        # Apply cap
        final_conf = min(base_conf, cap)
        
        # Never return > 0.9 unless computation was definitive (hard to prove in general case)
        # So we hard cap at 0.95 for safety
        return min(final_conf, 0.95)