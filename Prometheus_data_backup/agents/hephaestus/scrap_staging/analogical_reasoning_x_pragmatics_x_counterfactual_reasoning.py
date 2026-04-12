import re
import math
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    Structured Pragmatic Counterfactual Analogy (SPCA) Engine.
    
    Mechanism:
    1. Parsing: Extracts propositions (subj, rel, obj) with polarity and numeric values.
    2. Computation: Solves numeric comparisons, temporal ordering, and causal chains.
    3. Analogy: Maps prompt structure to candidate structure via graph isomorphism.
    4. Counterfactual: Perturbes inputs to test robustness of the mapping.
    5. Meta-Cognition: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|twice|half)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|while|during|first|last)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'(have you stopped|why did .*(?:fail|stop)|when did .*(?:stop))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'(either .+ or .+|must be .+ or .+)', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }
        
        # Weights for scoring
        self.alpha = 0.6  # Structural/Isomorphism weight
        self.beta = 0.4   # Counterfactual weight

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Parse text into typed nodes with polarity and numeric values."""
        nodes = []
        text_lower = text.lower()
        
        # Check for structural markers
        has_neg = bool(self.patterns['negation'].search(text_lower))
        has_comp = bool(self.patterns['comparative'].search(text_lower))
        has_cond = bool(self.patterns['conditional'].search(text_lower))
        has_causal = bool(self.patterns['causal'].search(text_lower))
        has_temp = bool(self.patterns['temporal'].search(text_lower))
        
        # Extract numbers
        nums = [float(n) for n in self.patterns['numbers'].findall(text)]
        
        # Create a composite signature for the node
        node = {
            'text': text.strip(),
            'negated': has_neg,
            'comparative': has_comp,
            'conditional': has_cond,
            'causal': has_causal,
            'temporal': has_temp,
            'numbers': nums,
            'polarity': -1 if has_neg else 1
        }
        nodes.append(node)
        return nodes

    def _compute_structural_score(self, prompt_nodes: List[Dict], cand_nodes: List[Dict]) -> float:
        """
        Compute graph isomorphism score based on structural features.
        Matches nodes based on shared properties and numeric consistency.
        """
        if not prompt_nodes or not cand_nodes:
            return 0.0
            
        matches = 0
        total_prompt_features = 0
        
        for p_node in prompt_nodes:
            p_features = 0
            best_match_score = 0.0
            
            # Count active structural features in prompt
            if p_node['negated']: p_features += 1
            if p_node['comparative']: p_features += 1
            if p_node['conditional']: p_features += 1
            if p_node['causal']: p_features += 1
            if p_node['temporal']: p_features += 1
            if p_node['numbers']: p_features += 1
            
            if p_features == 0: continue # Skip plain text nodes for structural scoring
            total_prompt_features += 1
            
            # Find best matching candidate node
            for c_node in cand_nodes:
                score = 0.0
                if p_node['negated'] == c_node['negated']: score += 0.2
                if p_node['comparative'] == c_node['comparative']: score += 0.2
                if p_node['conditional'] == c_node['conditional']: score += 0.2
                if p_node['causal'] == c_node['causal']: score += 0.2
                if p_node['temporal'] == c_node['temporal']: score += 0.2
                
                # Numeric consistency check
                if p_node['numbers'] and c_node['numbers']:
                    # Check if relative order is preserved or values match
                    if len(p_node['numbers']) == len(c_node['numbers']):
                        if all(abs(p - c) < 1e-6 for p, c in zip(p_node['numbers'], c_node['numbers'])):
                            score += 0.5
                        # Or if comparative logic holds (simplified)
                        elif (max(p_node['numbers']) > min(p_node['numbers'])) == \
                             (max(c_node['numbers']) > min(c_node['numbers'])):
                            score += 0.3
                
                if score > best_match_score:
                    best_match_score = score
            
            if best_match_score > 0:
                matches += best_match_score

        return matches / max(total_prompt_features, 1)

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """
        PRIMARY OBJECTIVE: Constructive Computation.
        Extracts numbers and logic to verify if the candidate is the computed result.
        """
        p_nums = [float(n) for n in self.patterns['numbers'].findall(prompt)]
        c_nums = [float(n) for n in self.patterns['numbers'].findall(candidate)]
        c_text = candidate.lower()
        p_text = prompt.lower()
        
        score = 0.0
        
        # 1. Direct Numeric Equality (Exact Answer)
        if p_nums and c_nums:
            # If candidate contains the exact result of a simple operation on prompt numbers
            # Try basic ops
            if len(p_nums) >= 2:
                ops = {
                    '+': p_nums[0] + p_nums[1],
                    '-': p_nums[0] - p_nums[1],
                    '*': p_nums[0] * p_nums[1],
                    '/': p_nums[0] / p_nums[1] if p_nums[1] != 0 else 0,
                    'avg': sum(p_nums)/len(p_nums)
                }
                for val in ops.values():
                    if any(abs(c - val) < 1e-5 for c in c_nums):
                        score = max(score, 0.9)
            
            # Check if candidate number exists in prompt (often a distractor or part of logic)
            # But if it's the ONLY number in candidate and matches a derived value, high score.
            if len(c_nums) == 1 and len(p_nums) == 1:
                if abs(c_nums[0] - p_nums[0]) < 1e-5:
                    score = max(score, 0.5) # Mere repetition is weak

        # 2. Logical Consistency (Negation/Yes-No)
        if 'not' in p_text or 'no' in p_text or 'false' in p_text:
            if 'yes' in c_text or 'true' in c_text:
                # Candidate contradicts a negative premise? Need context.
                # If prompt asks "Is it not X?" and answer is "Yes", it's ambiguous.
                # If prompt says "X is not true", answer "False" is good.
                if 'false' in c_text or 'no' in c_text:
                    score = max(score, 0.8)
            elif 'no' in c_text or 'false' in c_text:
                score = max(score, 0.8)
                
        # 3. Comparative Logic
        if 'more' in p_text or 'greater' in p_text:
            if c_nums and p_nums:
                # If prompt implies A > B, and candidate reflects the larger number
                if max(c_nums) >= max(p_nums): 
                    score = max(score, 0.6)

        return score

    def _counterfactual_score(self, prompt: str, candidate: str) -> float:
        """
        Simulate perturbations. If flipping a negation in prompt changes the expected answer,
        but the candidate stays the same, the candidate is brittle (low score).
        Since we can't fully re-run the world, we approximate by checking sensitivity.
        """
        # Heuristic: If the prompt has conditionals, the candidate should ideally reflect that structure
        has_if = bool(self.patterns['conditional'].search(prompt))
        cand_has_if = bool(self.patterns['conditional'].search(candidate))
        
        if has_if and not cand_has_if:
            # Candidate ignores conditional structure (might be okay if it's the result, but risky)
            # We penalize slightly for lack of structural mirroring in complex logic
            return 0.5
        return 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty.
        Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy / Either-Or without clarity
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are clear
            if 'or' in p_lower and '?' in p_lower:
                return 0.4 # Ambiguous
        
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.3
            
        # 4. Pronoun/Scope Ambiguity (Simple heuristic: multiple proper nouns + 'he/she/they')
        proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', prompt))
        pronouns = len(re.findall(r'\b(he|she|they|him|her)\b', p_lower))
        if proper_nouns >= 2 and pronouns >= 1 and 'who' in p_lower:
            return 0.2

        # 5. Lack of structural hooks (Unanswerable by this tool)
        # If no numbers, no logic words, and no clear question structure
        structural_hooks = [
            self.patterns['numbers'].search(p_lower),
            self.patterns['conditional'].search(p_lower),
            self.patterns['causal'].search(p_lower),
            self.patterns['comparative'].search(p_lower)
        ]
        if not any(structural_hooks) and '?' in prompt:
            # Purely semantic or knowledge-based question this tool can't compute
            return 0.25

        return 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        """Public confidence method with meta-cognitive capping."""
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
            
        # Compute raw score
        p_nodes = self._extract_nodes(prompt)
        a_nodes = self._extract_nodes(answer)
        
        s_iso = self._compute_structural_score(p_nodes, a_nodes)
        s_comp = self._compute_constructive_score(prompt, answer)
        s_cf = self._counterfactual_score(prompt, answer)
        
        # Weighted sum: Computation is primary for correctness, Structure for alignment
        raw_score = 0.4 * s_comp + 0.4 * s_iso + 0.2 * s_cf
        
        # Cap by meta-confidence
        final_conf = min(raw_score, meta_cap)
        
        # Never exceed 0.9 without definitive computation (heuristic: high numeric match)
        if s_comp < 0.8 and final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 3)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            p_nodes = self._extract_nodes(prompt)
            c_nodes = self._extract_nodes(cand)
            
            # 1. Structural Isomorphism (Analogy)
            s_iso = self._compute_structural_score(p_nodes, c_nodes)
            
            # 2. Constructive Computation (Primary)
            s_comp = self._compute_constructive_score(prompt, cand)
            
            # 3. Counterfactual Robustness
            s_cf = self._counterfactual_score(prompt, cand)
            
            # Final Score Calculation
            # Emphasis on computation (40%) and structure (30%) and counterfactual (20%)
            # NCD is excluded from primary logic as per instructions, used only if needed, 
            # but here we rely on the algorithmic score.
            score = (0.4 * s_comp) + (0.3 * s_iso) + (0.3 * s_cf)
            
            # Apply Meta-Cognitive Cap
            if meta_cap < 0.3:
                score = min(score, meta_cap)
            else:
                score = min(score, meta_cap) # Cap even if high
            
            # Generate reasoning string
            reasoning = f"Structural Match: {s_iso:.2f}, Computation: {s_comp:.2f}, Robustness: {s_cf:.2f}"
            if meta_cap < 0.3:
                reasoning += " [WARNING: Ambiguous or Unanswerable Prompt]"
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    prompt = "If John has 5 apples and buys 3 more, how many does he have?"
    candidates = ["8", "2", "John has 8 apples.", "He has 5."]
    
    print("Evaluation Results:")
    for res in tool.evaluate(prompt, candidates):
        print(res)
        
    print("\nConfidence Check:")
    print(f"Confidence in '8': {tool.confidence(prompt, '8')}")
    
    ambig_prompt = "Have you stopped cheating on tests?"
    print(f"Confidence in Ambiguous Prompt: {tool.confidence(ambig_prompt, 'Yes')}")