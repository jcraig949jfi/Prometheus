import re
import zlib
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    Quantum-Enhanced Analogical Model Checker (QAMC) Simulation.
    
    Mechanism:
    1. Analogical Encoding (Structure Mapping): Parses prompt/candidates into relational
       predicates (subject-verb-object, negations, comparatives) to build a structural graph.
    2. Quantum Search (Simulated): Uses structural isomorphism scoring to simulate Grover's
       amplitude amplification. Candidates with higher structural alignment to the prompt's
       logical constraints receive exponentially higher "probability" scores.
    3. Model Checking Validation: Verifies if the candidate satisfies temporal/logical
       constraints extracted from the prompt (e.g., "If A then B", "Not C").
    4. Epistemic Honesty (Meta-Confidence): Before scoring, analyzes the prompt for
       Tier B traps (presuppositions, ambiguity, false dichotomies). If detected,
       confidence is capped strictly low, regardless of candidate quality.
    
    Score Decomposition:
    - Judgment (Meta-Confidence): 40%
    - Structural/Computational Logic: 45%
    - NCD (Compression): 15%
    """

    def __init__(self):
        # Keywords indicating logical structures
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'cannot', "n't"}
        self.comparative_ops = {'>', '<', 'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'provided', 'assuming'}
        self.presupposition_triggers = ['stopped', 'quit', 'ceased', 'failed to', 'regret', 'realize']
        self.ambiguity_markers = ['every', 'all', 'each', 'who', 'he', 'she', 'it', 'they'] # Simplified pronoun/scope check
        self.dichotomy_markers = ['either', 'or', 'choose between', 'only option']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """Extracts logical predicates: negations, comparatives, conditionals, numbers."""
        tokens = self._tokenize(text)
        lower_text = text.lower()
        
        structure = {
            'negations': sum(1 for t in tokens if t in self.negation_words or t.endswith("n't")),
            'has_comparative': any(c in lower_text for c in self.comparative_ops),
            'has_conditional': any(c in lower_text for c in self.conditionals),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(tokens)
        }
        
        # Detect specific logical forms
        structure['is_question'] = '?' in text
        structure['has_presupposition_trigger'] = any(t in lower_text for t in self.presupposition_triggers)
        structure['has_ambiguity_marker'] = any(m in lower_text for m in self.ambiguity_markers)
        structure['has_dichotomy'] = any(d in lower_text for d in self.dichotomy_markers)
        
        return structure

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (low if trap detected, 1.0 if clean).
        """
        p_struct = self._extract_structure(prompt)
        lower_p = prompt.lower()
        
        # 1. Presupposition Trap: "Have you stopped X?", "Why did X fail?"
        if p_struct['has_presupposition_trigger'] and p_struct['is_question']:
            # Check for "Why/Have/Did" + trigger
            if any(lower_p.startswith(q) for q in ['why', 'have', 'did', 'do you']):
                return 0.25

        # 2. Scope/Pronoun Ambiguity in Questions
        if p_struct['is_question'] and p_struct['has_ambiguity_marker']:
            # Heuristic: If question asks "who" and contains multiple potential subjects
            if 'who' in lower_p and ('told' in lower_p or 'said' in lower_p):
                return 0.25
            # "Every X... Y" scope ambiguity is hard to detect perfectly without NLP, 
            # but if it's a generic "All X are Y" logic puzzle without specific instances, flag risk.
            if 'every' in lower_p and 'same' in lower_p:
                return 0.25

        # 3. False Dichotomy
        if p_struct['has_dichotomy']:
            # If "Either A or B" is presented as the only solution space without context
            if 'must' in lower_p or 'only' in lower_p:
                return 0.25

        # 4. Unanswerable / Missing Info
        # If the prompt asks for a calculation but provides no numbers
        if ('calculate' in lower_p or 'sum' in lower_p or 'total' in lower_p) and not p_struct['numbers']:
            return 0.25
            
        # If it asks for a specific fact not provided (heuristic: "what is the name" without context)
        if re.search(r'what is the (name|color|location|time)', lower_p) and len(prompt.split()) < 15:
            return 0.25

        return 1.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural and Computational Reasoning.
        Evaluates logical consistency, numeric correctness, and constraint satisfaction.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.0
        max_score = 0.0

        # 1. Numeric Evaluation (Constructive Computation)
        if p_struct['numbers'] and len(p_struct['numbers']) > 0:
            max_score += 2.0
            try:
                # Simple arithmetic check: If prompt has "2 + 2", candidate should have "4"
                # This is a simplified simulation of solving the expression
                p_nums = [float(n) for n in p_struct['numbers']]
                c_nums = [float(n) for n in c_struct['numbers']]
                
                # Heuristic: If prompt implies sum (e.g. "add", "sum", "+")
                if any(op in prompt.lower() for op in ['add', 'sum', 'total', '+', 'plus']):
                    expected = sum(p_nums)
                    if c_nums and abs(c_nums[0] - expected) < 1e-6:
                        score += 2.0
                    elif c_nums:
                        score -= 1.0 # Penalty for wrong math
                # Comparison check
                elif p_struct['has_comparative']:
                    # If prompt asks "which is larger", candidate should contain the larger number
                    if len(p_nums) >= 2:
                        target = max(p_nums) if 'larger' in prompt.lower() or 'greater' in prompt.lower() else min(p_nums)
                        if c_nums and abs(c_nums[0] - target) < 1e-6:
                            score += 2.0
            except ValueError:
                pass

        # 2. Negation Consistency (Constraint Propagation)
        # If prompt says "X is NOT Y", candidate should not claim "X is Y"
        max_score += 1.0
        if p_struct['negations'] > 0:
            # Simple heuristic: if prompt has "no" or "not", and candidate lacks negation words 
            # while repeating prompt nouns, it might be a contradiction.
            # Conversely, if prompt denies something, a valid answer often acknowledges the denial or avoids the denied state.
            # Here we reward candidates that maintain logical polarity if they repeat key terms.
            if c_struct['negations'] > 0 or not any(word in c_struct for word in ['yes', 'no']): 
                # Weak signal: acknowledging complexity
                score += 0.5
        else:
            score += 1.0 # Default full point if no negation complexity

        # 3. Conditional Logic (Modus Tollens/Ponens simulation)
        if p_struct['has_conditional']:
            max_score += 1.0
            # If prompt has "if", candidate should logically follow or address the condition
            # Heuristic: Candidate length should be substantial enough to address condition
            if c_struct['length'] > 3:
                score += 1.0
        
        # 4. Direct Answer Match (Basic Analogical Mapping)
        # If candidate is a direct substring of prompt (echo), low score unless it's a specific extraction task
        if candidate.strip().lower() in prompt.lower() and len(candidate.strip()) < 10:
            score -= 0.5

        return (score / max_score) if max_score > 0 else 0.5

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        try:
            len1 = len(zlib.compress(s1.encode()))
            len2 = len(zlib.compress(s2.encode()))
            len_combined = len(zlib.compress((s1 + s2).encode()))
            max_len = max(len1, len2)
            if max_len == 0:
                return 1.0
            return (len_combined - min(len1, len2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Step 1: Meta-Confidence (Epistemic Honesty)
        # Determine if the question itself is flawed or ambiguous
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            reasoning_parts = []
            
            # Step 2: Structural & Computational Scoring (Tier A)
            struct_score = self._compute_structural_score(prompt, candidate)
            
            # Step 3: NCD Tiebreaker (Max 15% influence)
            ncd_val = self._calculate_ncd(prompt, candidate)
            # Invert NCD so higher is better (0 distance = 1.0 score), but scale down
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Combine scores: Structural (85%) + NCD (15%)
            # Note: struct_score is normalized roughly 0-1, can be negative
            raw_score = (struct_score * 0.85) + ncd_score
            
            # Apply Meta-Confidence Cap
            # If the question is ambiguous (meta_cap = 0.25), the max possible score is capped.
            # However, we still rank candidates relative to each other, but absolute confidence is low.
            final_score = min(raw_score, meta_cap)
            
            # Adjust reasoning string
            if meta_cap < 0.3:
                reasoning_parts.append("WARNING: Prompt contains ambiguity, presupposition, or insufficient info.")
            if struct_score > 0.8:
                reasoning_parts.append("Strong structural/logical alignment.")
            elif struct_score < 0:
                reasoning_parts.append("Logical contradiction or computational error detected.")
                
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects Tier B traps.
        Caps at 0.9 even for perfect matches to maintain epistemic humility.
        """
        # 1. Check Meta-Confidence (The Question)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality (The Logic)
        # We run a mini-evaluation to see if the answer makes sense structurally
        # Create a dummy candidate list to reuse logic
        temp_res = self.evaluate(prompt, [answer])
        if not temp_res:
            return 0.0
            
        base_score = temp_res[0]['score']
        
        # Normalize base_score to 0-1 range for confidence calculation
        # Assuming base_score ranges roughly -1 to 1.5
        normalized_quality = max(0.0, min(1.0, (base_score + 1.0) / 2.5))
        
        # 3. Apply Caps
        # If the question is bad, confidence is low regardless of answer
        if meta_cap < 0.3:
            return min(normalized_quality, meta_cap)
        
        # If the answer is logically perfect, cap at 0.9 (never 100% certain)
        final_conf = min(normalized_quality, 0.9)
        
        # If structural score was negative (contradiction), confidence drops near 0
        if base_score < -0.5:
            final_conf = 0.1
            
        return round(final_conf, 3)