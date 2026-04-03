import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Fractal Incentive-Compatible Chunked Hypothesis Engine (FICHE)
    
    Mechanism:
    1. Fractal Geometry: The evaluation space is treated as a self-similar tree. 
       We recursively decompose the prompt into chunks (cognitive load limit C=7).
       Leaf nodes handle atomic facts; internal nodes aggregate logic.
    2. Cognitive Load Theory: Each reasoning step is limited to ~7 items. 
       Complex prompts are chunked; if a chunk exceeds complexity limits without 
       clear structure, epistemic uncertainty rises.
    3. Mechanism Design (VCG-inspired): Candidates "bid" for validity based on 
       structural adherence. We penalize candidates that rely on surface similarity 
       (NCD) without structural support. True confidence is capped by the 
       meta-cognitive check of the prompt's own answerability.
       
    Epistemic Honesty:
    Before scoring, _meta_confidence analyzes the prompt for presuppositions, 
    ambiguities, and unanswerable constraints. If detected, global confidence 
    is capped strictly (< 0.3), overriding candidate scores.
    """

    def __init__(self):
        self.chunk_size = 7  # Miller's Law limit for working memory
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b",
            r"\bwhen did.*stop\b", r"\bquit\b", r"\bassum.*that\b"
        ]
        self.ambiguity_triggers = [
            r"\bevery.*a.*\b", r"\btold.*he\b", r"\btold.*she\b", r"\bwho\b.*\?",
            r"\beither.*or\b", r"\best\b", r"\bworst\b", r"\bfavorite\b"
        ]
        self.false_dichotomy_triggers = [r"\beither.*or\b", r"\bmust.*or\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt itself for epistemic traps.
        Returns a cap value: 1.0 if clear, < 0.3 if ambiguous/unanswerable.
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check for scope/pronoun ambiguity and subjectivity
        # Only flag if the question structure implies ambiguity (e.g., ends with ?)
        if "?" in prompt:
            for pattern in self.ambiguity_triggers:
                if re.search(pattern, p_lower):
                    # Heuristic: If it asks "who" after a pronoun usage, high ambiguity
                    if "who" in p_lower and ("he" in p_lower or "she" in p_lower):
                        return 0.20
                    # Subjective terms without criteria
                    if re.search(r"\b(best|worst|favorite)\b", p_lower):
                        return 0.25
        
        # Check for false dichotomy
        for pattern in self.false_dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Only if it implies exclusivity without proof
                if "only" in p_lower or "must" in p_lower:
                    return 0.30
                    
        return 1.0

    def _extract_structure(self, prompt: str) -> Dict:
        """
        Structural parsing: Extracts negations, comparatives, conditionals, numbers.
        Returns a dict of structural features used for scoring.
        """
        features = {
            "negations": len(re.findall(r"\b(not|no|never|neither|without)\b", prompt.lower())),
            "comparatives": len(re.findall(r"\b(more|less|greater|smaller|higher|lower|better|worse)\b", prompt.lower())),
            "conditionals": len(re.findall(r"\b(if|then|unless|provided)\b", prompt.lower())),
            "numbers": re.findall(r"\d+\.?\d*", prompt),
            "logic_ops": len(re.findall(r"\b(and|or|implies|therefore)\b", prompt.lower()))
        }
        return features

    def _compute_numeric_truth(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempts to solve numeric comparisons or simple math in the prompt.
        Returns a score boost if the candidate matches the computed truth.
        """
        # Extract numbers from prompt
        nums = re.findall(r"\d+\.?\d*", prompt)
        if len(nums) < 2:
            return None
            
        try:
            # Simple comparison trap detection (e.g., 9.11 vs 9.9)
            if len(nums) >= 2:
                n1 = float(nums[0])
                n2 = float(nums[1])
                
                # Check candidate for numeric content
                cand_nums = re.findall(r"\d+\.?\d*", candidate)
                if cand_nums:
                    c_val = float(cand_nums[0])
                    # If prompt asks which is larger/smaller
                    if "larger" in prompt.lower() or "greater" in prompt.lower():
                        expected = max(n1, n2)
                        return 1.0 if abs(c_val - expected) < 1e-6 else 0.0
                    if "smaller" in prompt.lower() or "less" in prompt.lower():
                        expected = min(n1, n2)
                        return 1.0 if abs(c_val - expected) < 1e-6 else 0.0
        except ValueError:
            pass
        return None

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _fractal_chunk_eval(self, prompt: str, candidate: str) -> float:
        """
        Simulates the fractal expert tree.
        1. Chunk the prompt into working-memory-sized segments.
        2. Evaluate candidate alignment with each chunk (Local Experts).
        3. Aggregate scores (Internal Nodes).
        """
        words = prompt.split()
        chunks = [words[i:i+self.chunk_size] for i in range(0, len(words), self.chunk_size)]
        
        if not chunks:
            return 0.0
            
        chunk_scores = []
        for chunk in chunks:
            chunk_text = " ".join(chunk)
            # Local expert: Does the candidate contain keywords from this chunk?
            # This mimics the 'leaf node' checking fine-grained hypothesis fit.
            overlap = 0
            for word in chunk:
                if word.lower() in candidate.lower():
                    overlap += 1
            # Normalize by chunk size to prevent bias towards longer chunks
            score = overlap / max(len(chunk), 1)
            chunk_scores.append(score)
            
        # Aggregation: Weighted average (coarser grain)
        # In a true fractal system, we'd recurse, but here we simulate the 
        # self-similar aggregation by weighing coherent chunks higher.
        if not chunk_scores:
            return 0.0
        return sum(chunk_scores) / len(chunk_scores)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main evaluation loop implementing FICHE logic.
        1. Meta-confidence check (Epistemic Honesty).
        2. Structural parsing.
        3. Numeric computation (Constructive).
        4. Fractal chunk evaluation.
        5. VCG-style scoring: Combine structural/computation (high weight) 
           with NCD (low weight tiebreaker).
        """
        results = []
        
        # 1. Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        is_ambiguous = meta_cap < 0.3
        
        # 2. Structural Analysis
        structure = self._extract_structure(prompt)
        has_structure = any([
            structure['negations'] > 0,
            structure['comparatives'] > 0,
            structure['conditionals'] > 0,
            len(structure['numbers']) >= 2
        ])
        
        for candidate in candidates:
            score = 0.0
            reasoning_parts = []
            
            # If the prompt is ambiguous, all candidates get low confidence
            if is_ambiguous:
                base_score = 0.1
                reasoning_parts.append("Epistemic warning: Prompt contains ambiguity or presupposition.")
            else:
                base_score = 0.5
                reasoning_parts = []
                
                # A. Constructive Computation (Highest Priority)
                comp_score = self._compute_numeric_truth(prompt, candidate)
                if comp_score is not None:
                    score += comp_score * 0.6  # 60% weight for hard math
                    reasoning_parts.append(f"Numeric verification: {'Pass' if comp_score == 1.0 else 'Fail'}")
                
                # B. Structural Parsing (High Priority)
                # Check if candidate respects negations/logic detected
                struct_match = 0.0
                if structure['negations'] > 0:
                    # Simple heuristic: if prompt has 'not', candidate should ideally reflect negation or contrast
                    # This is a simplification; real logic would parse AST
                    if any(neg in candidate.lower() for neg in ['not', 'no', 'false', 'never']):
                        struct_match += 0.3
                    else:
                        # Penalty for ignoring negation? Hard without full NLP. 
                        # Instead, rely on chunk overlap for semantic fit.
                        pass
                if structure['conditionals'] > 0:
                     if any(cond in candidate.lower() for cond in ['if', 'then', 'unless']):
                         struct_match += 0.2
                
                score += struct_match
                if struct_match > 0:
                    reasoning_parts.append("Structural logic alignment detected.")

                # C. Fractal Chunk Evaluation (Medium Priority)
                # Measures how well the candidate covers the 'chunks' of the prompt
                fractal_score = self._fractal_chunk_eval(prompt, candidate)
                score += fractal_score * 0.25
                if fractal_score > 0.3:
                    reasoning_parts.append(f"Fractal chunk alignment: {fractal_score:.2f}")

                # D. NCD Tiebreaker (Low Priority, max 15%)
                # Only used if other signals are weak or as a final tiebreaker
                ncd = self._ncd_score(prompt, candidate)
                # Invert NCD (lower distance = higher similarity = higher score)
                # But cap its influence to avoid bag-of-words gaming
                ncd_contribution = (1.0 - ncd) * 0.15 
                score += ncd_contribution
                
                # Normalize base score logic
                if has_structure or comp_score is not None:
                     # If we have structure or math, the score is driven by those.
                     # Ensure we don't double count too much.
                     score = min(score, 1.0)
                else:
                    # If no structure/math, rely mostly on fractal chunking and NCD
                    score = (fractal_score * 0.5) + (ncd_contribution * 2.0)
                    score = min(score, 0.8) # Cap non-structural answers

            # Apply Meta-Confidence Cap (The VCG "Truthfulness" constraint)
            final_score = min(score, meta_cap)
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Scored based on general alignment."
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt is ambiguous, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # Otherwise, evaluate the specific answer quality
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Never return > 0.9 unless it's a definitive computation
        # We assume if numeric truth was found and matched, it's definitive.
        # Otherwise, cap at 0.85 to allow for uncertainty.
        if self._compute_numeric_truth(prompt, answer) == 1.0:
            return min(base_score, 1.0)
        else:
            return min(base_score, 0.85)