import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Self-Maintaining Causal-Topological Learner (SMCTL) Implementation.
    
    Mechanism:
    1. Structural Parsing (Topology Proxy): Extracts logical skeleton (negations, comparatives,
       conditionals) to form a stable "topological" signature of the prompt. This avoids the 
       "Topology inhibitor" trap by using topology only for structure, not direct scoring.
    2. Autopoietic Repair (Metacognition): The _meta_confidence method acts as the repair loop.
       It scans for logical inconsistencies (presuppositions, ambiguities, false dichotomies).
       If detected, it "repairs" the confidence score downward to prevent false positives,
       maintaining the system's epistemic integrity.
    3. Causal Inference: Performs constructive computation (math, logic propagation) on the
       extracted structure.
    4. Scoring: Structural match >= 50%, Computation >= 20%, NCD <= 15%.
    """

    def __init__(self):
        # Patterns for structural parsing (The "Topological" signature)
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.quantifiers = {'every', 'all', 'some', 'none', 'each'}
        
        # Patterns for Metacognitive Repair (Autopoiesis)
        self.presupposition_triggers = ['have you stopped', 'have you quit', 'why did', 'when did', 'how often did']
        self.ambiguity_triggers = ['who is', 'which one', 'what does he', 'what does she', 'what does it']
        self.dichotomy_triggers = ['either', 'or not', 'is it a or b']
        self.subjectivity_triggers = ['best', 'worst', 'favorite', 'most beautiful', 'ugliest']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical skeleton (Topology Proxy)."""
        lower_text = self._normalize(text)
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        has_quantifier = bool(words & self.quantifiers)
        
        # Detect numbers for constructive computation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'quantifier': has_quantifier,
            'numbers': numbers,
            'word_count': len(words),
            'char_count': len(text)
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Autopoietic Repair Loop.
        Scans prompt for logical traps. If found, returns low confidence to preserve system integrity.
        """
        lower_prompt = self._normalize(prompt)
        
        # 1. Presupposition Check
        for trigger in self.presupposition_triggers:
            if trigger in lower_prompt:
                return 0.15  # Strong signal of trap
        
        # 2. Scope/Pronoun Ambiguity
        if (' he ' in lower_prompt or ' she ' in lower_prompt) and 'who' in lower_prompt:
            return 0.20
        if 'every' in lower_prompt and 'same' in lower_prompt:
            return 0.25
            
        # 3. False Dichotomy
        if 'either' in lower_prompt and 'or' in lower_prompt:
            # Check if options are exhaustive (simplified heuristic)
            if 'other' not in lower_prompt and 'possible' not in lower_prompt:
                return 0.30
                
        # 4. Subjectivity
        for trigger in self.subjectivity_triggers:
            if trigger in lower_prompt:
                # Unless context implies objective metric (e.g., "best score")
                if 'score' not in lower_prompt and 'value' not in lower_prompt:
                    return 0.25

        # 5. Unanswerability (Missing info heuristic)
        if 'calculate' in lower_prompt and len(re.findall(r'\d+', lower_prompt)) < 2:
            return 0.20

        return 1.0  # No structural defects detected

    def _compute_constructive(self, prompt: str, candidate: str) -> float:
        """
        Performs constructive computation (Math/Logic).
        Returns 1.0 if candidate matches computed result, 0.0 otherwise.
        """
        lower_prompt = self._normalize(prompt)
        lower_cand = self._normalize(candidate)
        
        # Numeric Evaluation (PEMDAS simplified)
        numbers = re.findall(r'-?\d+\.?\d*', prompt)
        if len(numbers) >= 2:
            try:
                # Simple arithmetic check: if prompt has "2 + 2", check candidate "4"
                # We attempt to eval simple expressions if present
                if '+' in prompt or '-' in prompt or '*' in prompt or '/' in prompt:
                    # Extract expression (very naive extraction for demo)
                    # Focus on checking if candidate is the result of standard ops
                    vals = [float(n) for n in numbers]
                    if len(vals) == 2:
                        expected = None
                        if '+' in prompt: expected = vals[0] + vals[1]
                        elif '-' in prompt: expected = vals[0] - vals[1]
                        elif '*' in prompt or 'x' in lower_prompt: expected = vals[0] * vals[1]
                        elif '/' in prompt: expected = vals[0] / vals[1]
                        
                        if expected is not None:
                            cand_val = float(lower_cand.replace(',', ''))
                            if abs(cand_val - expected) < 0.01:
                                return 1.0
                            else:
                                return 0.0
            except (ValueError, ZeroDivisionError):
                pass

        # Logic Constraint Propagation (Modus Tollens/Ponens simplified)
        # If prompt says "If A then B" and "A is true", candidate should imply B
        if 'if' in lower_prompt and 'then' in lower_prompt:
            # Heuristic: If candidate repeats the consequent logically
            # This is a placeholder for complex logic graphs
            pass
            
        return 0.5  # Neutral if no constructive computation triggered

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _structural_match_score(self, prompt: str, candidate: str) -> float:
        """
        Computes score based on structural alignment (Topology Proxy).
        Checks if candidate preserves the logical invariants of the prompt.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        matches = 0
        total = 0
        
        # Check Negation Consistency
        total += 1
        if p_struct['negation'] == c_struct['negation']:
            matches += 1
            
        # Check Number Presence (if prompt has numbers, valid answer usually involves logic on them)
        if p_struct['numbers']:
            total += 1
            if c_struct['numbers']:
                matches += 1
        
        # Check Comparative/Conditional alignment
        if p_struct['comparative']:
            total += 1
            if c_struct['comparative']:
                matches += 1
                
        if total == 0:
            return 0.5
            
        return matches / total

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence (Autopoietic guard)
        # If the prompt itself is flawed, all candidates get penalized, 
        # but we still rank them based on how well they handle the flaw or match structure.
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (>= 50% weight)
            struct_score = self._structural_match_score(prompt, cand)
            
            # 2. Constructive Computation (>= 20% weight)
            comp_score = self._compute_constructive(prompt, cand)
            
            # 3. NCD (<= 15% weight, tiebreaker)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd  # Convert distance to similarity
            
            # Weighted Sum
            # Weights: Structural 0.55, Computation 0.30, NCD 0.15
            raw_score = (struct_score * 0.55) + (comp_score * 0.30) + (ncd_score * 0.15)
            
            # Apply Autopoietic Meta-Confidence Cap
            # If the prompt is ambiguous/trap (meta_conf < 0.3), the max possible score is capped
            # to reflect uncertainty, preventing overconfidence.
            final_score = min(raw_score, meta_conf * 1.2) # Allow slight buffer but cap heavily
            
            # Generate Reasoning String
            reasoning_parts = []
            if meta_conf < 0.3:
                reasoning_parts.append("Flagged as logical trap/ambiguous (Autopoietic Repair).")
            if comp_score == 1.0:
                reasoning_parts.append("Constructive computation verified.")
            if struct_score > 0.8:
                reasoning_parts.append("Structural invariants preserved.")
            if not reasoning_parts:
                reasoning_parts.append("Ranked by structural alignment and NCD.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence level to ensure epistemic honesty.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Evaluate the specific pair
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        pair_score = eval_results[0]['score']
        
        # The confidence is the minimum of the pair's quality and the prompt's safety
        final_conf = min(pair_score, meta_conf)
        
        # Hard cap for non-computational answers on ambiguous prompts
        if meta_conf < 0.3 and pair_score > 0.5:
            final_conf = 0.25 # Force low confidence if prompt is bad but answer looks "good" structurally
            
        return round(final_conf, 4)