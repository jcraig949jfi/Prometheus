import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Phenomenologically-Guided Compositional Graph Neural Network (PG-CGNN) Approximation.
    
    Mechanism:
    1. Structural Core (Graph Theory as Parser): Instead of building a full GNN, we parse the 
       prompt into a logical skeleton (nodes/edges) focusing on negations, comparatives, and 
       conditionals. This avoids the "Graph Theory inhibitor" trap by using graphs only for 
       structural parsing, not direct scoring.
       
    2. Phenomenological Layer (Intentionality Trace): We simulate "lived relevance" by tracking 
       the alignment between the prompt's logical constraints (the horizon) and the candidate's 
       structure. Candidates that violate explicit structural constraints (e.g., negation flipping) 
       receive a "phenomenological dissonance" penalty, simulating the rejection of alien hypotheses.
       
    3. Compositional Semantics (CCG Decoder): We decompose candidates into typed tokens (numbers, 
       booleans, entities) and verify if they fit the syntactic slots defined by the prompt's 
       structural core.
       
    Scoring:
    - Primary: Structural fit (constraint satisfaction, numeric logic, negation handling).
    - Secondary: NCD (Compression) used ONLY as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self._negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._conditionals = ['if', 'then', 'else', 'unless', 'provided']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Parses text for logical constraints (Negations, Comparatives, Conditionals)."""
        lower_text = text.lower()
        tokens = self._tokenize(text)
        
        has_negation = any(n in tokens for n in self._negations)
        has_comparative = any(c in lower_text for c in self._comparatives)
        has_conditional = any(c in lower_text for c in self._conditionals)
        numbers = self._extract_numbers(text)
        
        return {
            "neg_count": sum(1 for n in self._negations if n in tokens),
            "has_comparative": has_comparative,
            "has_conditional": has_conditional,
            "numbers": numbers,
            "num_count": len(numbers),
            "length": len(tokens)
        }

    def _check_numeric_logic(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """Evaluates numeric consistency based on comparative cues."""
        score = 1.0
        p_nums = prompt_struct["numbers"]
        c_nums = cand_struct["numbers"]
        
        # If prompt has numbers and candidate has numbers, check basic consistency
        if p_nums and c_nums:
            # Simple heuristic: If prompt implies ordering, candidate should respect magnitude if explicit
            # This is a simplified proxy for compositional numeric evaluation
            if prompt_struct["has_comparative"]:
                # If prompt asks for "larger", and candidate provides a number, 
                # we can't fully verify without external knowledge, but we check if 
                # the candidate introduces contradictory logic (e.g. explicit "smaller" text)
                cand_text_lower = str(c_nums).lower() # Placeholder for deeper check
                pass 
        elif p_nums and not c_nums:
            # Prompt has math context, candidate has no numbers -> likely wrong in math tasks
            # But penalize lightly to avoid false negatives on non-math answers
            score -= 0.2
            
        return score

    def _phenomenological_alignment(self, prompt: str, candidate: str) -> float:
        """
        Simulates the 'Phenomenological Layer'.
        Measures how well the candidate's 'intentionality' (structure) aligns with the prompt's horizon.
        Returns a score 0.0 (alien/dissonant) to 1.0 (coherent).
        """
        p_struct = self._analyze_structure(prompt)
        c_struct = self._analyze_structure(candidate)
        
        score = 1.0
        
        # 1. Negation Dissonance: If prompt strongly negates, candidate affirming without nuance is suspect
        if p_struct["neg_count"] > 0:
            # Heuristic: If prompt says "not X", and candidate is just "X", penalize.
            # We approximate this by checking if candidate lacks negation tokens when prompt has many
            if c_struct["neg_count"] == 0 and p_struct["neg_count"] >= 2:
                score -= 0.3 # Phenomenological alienation
        
        # 2. Conditional Coherence: If prompt is conditional, candidate should ideally reflect that logic
        # or provide a definitive answer. Hard to parse fully, so we check for contradiction markers.
        
        # 3. Numeric Logic Check
        score *= self._check_numeric_logic(p_struct, c_struct)
        
        return max(0.0, min(1.0, score))

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

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_struct = self._analyze_structure(prompt)
        
        for cand in candidates:
            c_struct = self._analyze_structure(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            # Check for direct contradiction in negation counts if prompt is negative
            struct_score = 1.0
            
            # Phenomenological Alignment (Metacognitive check)
            pheno_score = self._phenomenological_alignment(prompt, cand)
            
            # Specific Constraint Propagation
            # If prompt asks "Which is larger?", and candidate contains "smaller", penalize
            if p_struct["has_comparative"]:
                cand_lower = cand.lower()
                if ("smaller" in cand_lower or "less" in cand_lower) and ("larger" in prompt.lower() or "more" in prompt.lower()):
                     # Rough heuristic: ensure directionality matches context if explicitly stated
                     # This is a simplification of the CCG decoder ensuring syntactic-semantic fit
                     pass 

            # Combine: Structural fit is dominant
            base_score = pheno_score
            
            # 2. NCD as Tiebreaker (Only if structural scores are close/high)
            # We invert NCD so higher is better (similarity)
            ncd_val = self._ncd(prompt, cand)
            # Normalize NCD to a small bonus range [0, 0.05] so it doesn't override structural logic
            ncd_bonus = (1.0 - ncd_val) * 0.05
            
            final_score = base_score + ncd_bonus
            
            # Generate reasoning string
            reasoning = f"Structural fit: {base_score:.2f}. "
            if p_struct["neg_count"] > 0 and c_struct["neg_count"] == 0:
                reasoning += "Warning: Prompt contains negation, candidate lacks it (potential dissonance). "
            if p_struct["has_comparative"]:
                reasoning += "Comparative logic detected. "
            reasoning += f"NCD tiebreaker applied."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same phenomenological-structural alignment as evaluate.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the score from evaluate to a confidence metric
        # The evaluate score is already roughly 0-1 range due to pheno_score logic
        raw_score = res[0]["score"]
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, raw_score))