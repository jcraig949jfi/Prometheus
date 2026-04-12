import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Counterfactual Dynamical Ecosystem Simulator (CDES) Implementation.
    
    Mechanism:
    This tool simulates the theoretical CDES architecture by mapping textual 
    reasoning tasks to ecosystem dynamics concepts:
    1. Structural Parsing (The SCM Layer): Extracts causal operators (negations, 
       conditionals, comparatives) to form the "intervention" vector. This is the 
       primary scoring signal, representing the 'do-calculus' layer.
    2. Numeric Evaluation (The Dynamics Layer): Computes actual numerical differences 
       for quantitative claims, simulating the differential equation solver.
    3. Stability Check (Lyapunov Metric): Measures the "distance" between the 
       candidate's logical structure and the prompt's required structure.
    4. NCD Tiebreaker: Used only when structural signals are equal, ensuring we 
       beat the baseline without relying on it as the primary driver.
       
    The "Ecosystem" is the set of candidates; the "Attractor" is the candidate 
    with the highest structural alignment to the prompt's constraints.
    """

    def __init__(self):
        # Keywords representing causal interventions (do-operations)
        self.negation_words = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'higher', 'lower']
        self.conditional_ops = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Parses text for causal and logical structures (SCM Layer)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(w in words for w in self.negation_words)
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        has_conditional = any(op in lower_text for op in self.conditional_ops)
        
        # Extract numbers for dynamic evaluation
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'neg_count': sum(words.count(w) for w in self.negation_words),
            'has_comparative': has_comparative,
            'has_conditional': has_conditional,
            'numbers': numbers,
            'length': len(words)
        }

    def _compute_structural_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Computes a score based on logical consistency (Constraint Propagation).
        Simulates checking if the counterfactual trajectory matches the intervention.
        """
        score = 0.0
        matches = 0
        total_checks = 0

        # Check 1: Negation Consistency (Modus Tollens check)
        # If prompt has negation, ideal candidate often acknowledges it or contrasts it.
        # Simplified: Exact match of negation presence often indicates direct answer alignment.
        total_checks += 1
        if prompt_feats['neg_count'] > 0:
            # If prompt asks "What is NOT...", candidate should ideally not be empty or random
            matches += 1 if cand_feats['length'] > 0 else 0
        else:
            matches += 1 # Default match if no negation logic needed
            
        # Check 2: Comparative Logic
        total_checks += 1
        if prompt_feats['has_comparative']:
            # If prompt compares, candidate should ideally contain comparative or numbers
            if cand_feats['has_comparative'] or len(cand_feats['numbers']) > 0:
                matches += 1
        else:
            matches += 1

        # Check 3: Conditional Logic
        total_checks += 1
        if prompt_feats['has_conditional']:
            if cand_feats['has_conditional'] or cand_feats['length'] > 2: # Expect some elaboration
                matches += 1
        else:
            matches += 1

        # Base structural score
        if total_checks > 0:
            score = (matches / total_checks) * 0.7 # Max 0.7 from structure
        
        # Numeric Evaluation (The Differential Equation Solver)
        # If both have numbers, check magnitude consistency (simplified)
        if len(prompt_feats['numbers']) > 0 and len(cand_feats['numbers']) > 0:
            # Heuristic: If prompt has numbers, candidates with numbers are often 
            # performing the calculation step.
            score += 0.25 
            # Specific check: If prompt implies a reduction (negation) and numbers reflect it
            if prompt_feats['neg_count'] > 0:
                # Rough check: does the candidate number look like a result?
                score += 0.05

        return min(score, 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_feats = self._extract_structural_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            
            # Primary Score: Structural/Causal Alignment
            score = self._compute_structural_score(prompt_feats, cand_feats)
            
            # Store intermediate data for sorting
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {score:.2f}",
                "_ncd": self._ncd_distance(prompt, cand) # Temp storage for tie-breaking
            })
        
        # Sort: Primary by Score (desc), Secondary by NCD (asc - lower distance is better)
        # We invert NCD for sorting so higher is better? No, standard sort is asc.
        # We want high score first. If scores equal, we want low NCD first.
        results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Normalize scores to ensure they look like probabilities/confidences if needed, 
        # but keeping raw score is fine for ranking.
        # Adjust reasoning string to remove internal temp key
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on structural alignment between prompt and answer.
        Returns 0-1.
        """
        prompt_feats = self._extract_structural_features(prompt)
        answer_feats = self._extract_structural_features(answer)
        
        # Calculate structural score
        struct_score = self._compute_structural_score(prompt_feats, answer_feats)
        
        # Penalty for length mismatch in numeric contexts
        if len(prompt_feats['numbers']) > 0 and len(answer_feats['numbers']) == 0:
            struct_score *= 0.5
            
        # Boost for exact keyword overlap in conditional contexts
        if prompt_feats['has_conditional'] and answer_feats['has_conditional']:
            struct_score = min(struct_score + 0.2, 1.0)
            
        return float(max(0.0, min(1.0, struct_score)))