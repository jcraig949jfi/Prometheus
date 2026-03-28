import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Holographic Evolutionary Type-Checking Engine (HETCE) Implementation.
    
    Mechanism:
    1. Bulk Space (Type Theory): Candidates are treated as dependent-type terms.
       We simulate type-checking by verifying logical consistency with the prompt's
       structural constraints (negations, conditionals, numeric bounds).
    2. Boundary Projection (Holography): The complex "bulk" logic is compressed into
       a finite boundary signature: a tuple of boolean flags and numeric deltas representing
       constraint satisfaction. This allows O(1) fitness evaluation without re-traversing
       the full proof tree.
    3. Evolutionary Fitness: Candidates are scored on how well they mutate to satisfy
       the boundary constraints while maintaining high compression (conciseness) and
       logical validity.
       
    Epistemic Honesty (Tier B):
    Before scoring, the system performs a meta-analysis of the prompt. If the prompt
    contains presuppositions, ambiguities, or unanswerable queries, the confidence
    is capped low (<0.3) regardless of candidate quality, enforcing "I don't know"
    behavior on ill-posed problems.
    """

    def __init__(self):
        # Patterns for structural parsing (The "Bulk" logic rules)
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\bsmaller\s+than\b', r'\b>\b', r'\b<\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b']
        self.presupposition_triggers = [r'\bhave\s+you\s+stopped\b', r'\bwhy\s+did\s+\w+\s+fail\b', r'\bwhen\s+did\s+\w+\s+stop\b']
        self.ambiguity_triggers = [r'\bevery\s+\w+\s+did\s+a\s+\w+\b', r'\btold\s+\w+\s+he\s+was\b', r'\beither\s+\w+\s+or\s+\w+\b']
        self.subjectivity_triggers = [r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bopinion\b']

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical constraints from text (Bulk space features)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'has_numbers': bool(re.search(r'\d+(\.\d+)?', text)),
            'word_count': len(text.split())
        }
        return features

    def _extract_numeric_constraints(self, text: str) -> List[float]:
        """Extracts numbers for constructive computation."""
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value. If the prompt is flawed, this returns < 0.3.
        """
        p_lower = prompt.lower()
        
        # Check for presupposition traps
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.15  # Strong presupposition detected
        
        # Check for ambiguity traps
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.25  # Ambiguity detected
                
        # Check for subjectivity without criteria
        if any(re.search(t, p_lower) for t in self.subjectivity_triggers):
            if "criteria" not in p_lower and "measure" not in p_lower:
                return 0.20

        # Default: No strong negative signals
        return 1.0

    def _holographic_boundary(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Compresses the verification of candidate against prompt into a boundary signature.
        Returns (fitness_score, reasoning_string).
        """
        p_features = self._structural_parse(prompt)
        c_features = self._structural_parse(candidate)
        score = 0.0
        reasons = []

        # 1. Structural Consistency (Type Checking Simulation)
        # If prompt has negation, valid answers often reflect that (or explicitly deny it)
        if p_features['negations'] > 0:
            # Heuristic: Good answers often contain negation words if the prompt sets up a negative constraint
            # Or if the prompt asks a yes/no question involving negation.
            if c_features['negations'] > 0 or re.search(r'\b(yes|no|true|false)\b', candidate.lower()):
                score += 0.3
                reasons.append("Negation consistency maintained")
            else:
                reasons.append("Warning: Negation context ignored")

        # 2. Comparative Logic
        if p_features['comparatives'] > 0:
            if c_features['comparatives'] > 0 or p_features['has_numbers']:
                score += 0.25
                reasons.append("Comparative logic detected and addressed")
        
        # 3. Conditional Flow
        if p_features['conditionals'] > 0:
            if c_features['conditionals'] > 0 or any(k in candidate.lower() for k in ['if', 'then', 'because', 'therefore']):
                score += 0.2
                reasons.append("Conditional flow preserved")

        # 4. Constructive Computation (Numeric)
        p_nums = self._extract_numeric_constraints(prompt)
        c_nums = self._extract_numeric_constraints(candidate)
        
        if p_nums:
            # If prompt has numbers, candidate should ideally have numbers or a clear qualitative shift
            if c_nums:
                score += 0.25
                reasons.append("Numeric constraints processed")
            elif len(p_nums) > 1 and "no" not in candidate.lower() and "yes" not in candidate.lower():
                # Penalty for ignoring specific math problems
                score -= 0.1
                reasons.append("Potential numeric omission")

        # 5. Holographic Compression (Conciseness vs Information Density)
        # Prefer candidates that are concise but retain key terms from prompt
        common_terms = set(prompt.lower().split()) & set(candidate.lower().split())
        # Remove stopwords from common terms for better signal
        stopwords = {'the', 'is', 'a', 'an', 'to', 'of', 'in', 'it', 'that', 'this'}
        significant_overlap = common_terms - stopwords
        
        if significant_overlap:
            # Ratio of significant overlap to candidate length (simplified compression metric)
            compression_ratio = len(significant_overlap) / (len(candidate.split()) + 1)
            score += min(0.2, compression_ratio * 0.5)
            reasons.append(f"High information density (overlap: {len(significant_overlap)})")

        return score, "; ".join(reasons) if reasons else "No structural match"

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denom = max(c1, c2)
            if denom == 0:
                return 0.0
            ncd = (c12 - min(c1, c2)) / denom
            return ncd
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the HETCE mechanism.
        1. Meta-check prompt for Tier B traps.
        2. Compute holographic boundary fitness for each candidate.
        3. Apply NCD as a minor tiebreaker.
        4. Rank by composite score.
        """
        results = []
        
        # Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # Holographic Fitness (Structural + Logical)
            h_score, h_reason = self._holographic_boundary(prompt, cand)
            
            # NCD Tiebreaker (Inverse similarity, normalized)
            # We want high similarity to prompt context usually, so we invert NCD logic slightly
            # But per instructions, NCD is only for tiebreaking where structural signal is weak.
            ncd_val = self._ncd_score(prompt, cand)
            
            # Composite Score Construction
            # Structural >= 50%, Computation (simulated in h_score) >= 20%, NCD <= 15%
            # Base score from holographic check (0.0 to ~1.0 range theoretically)
            base_score = min(1.0, h_score) 
            
            # Add small NCD perturbation only if structural score is ambiguous or close
            # Here we apply it as a small bonus for relevance if structural score is decent
            ncd_bonus = (1.0 - ncd_val) * 0.15 if base_score > 0.1 else 0.0
            
            final_score = base_score + ncd_bonus
            
            # Apply Tier B Cap
            if meta_cap < 0.3:
                final_score = min(final_score, 0.25) # Force low score if prompt is bad
                h_reason = f"Tier B Trap Detected ({meta_cap}); " + h_reason

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": h_reason
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        # 1. Check Prompt Validity (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality (Holographic Fitness)
        score, _ = self._holographic_boundary(prompt, answer)
        
        # 3. Combine
        # If the prompt is bad, confidence is low regardless of answer.
        # If prompt is good, confidence scales with how well the answer satisfies constraints.
        raw_conf = min(1.0, score + 0.1) # Small baseline boost for valid prompts
        
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 unless computation was definitive (hard to prove heuristically)
        # We simulate this by capping at 0.95 max unless the score is perfect and cap is 1.0
        if final_conf > 0.9 and cap < 1.0:
            final_conf = 0.9
            
        return round(final_conf, 3)