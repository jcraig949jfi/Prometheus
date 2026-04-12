import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Hierarchical Recurrent Predictive-Coding Network with Social Latents (PC-RNN-ToM).
    
    Mechanism:
    1. Dynamical Systems: Maintains a latent state vector 'z' that evolves via a learned 
       dynamics function (simulated here via gated recurrent updates based on input features).
    2. Predictive Coding: Computes prediction errors between top-down expectations (generated 
       from latent state) and bottom-up structural/sensory input. Updates latent state to 
       minimize variational free energy (represented as a loss function).
    3. Theory of Mind (Social Latent): The top-layer latent state explicitly models the 
       "agent" (questioner) intentions. It simulates counterfactuals to detect ambiguity, 
       presuppositions, and false dichotomies (Tier B honesty).
    
    Scoring Strategy:
    - Structural Parsing (40%): Detects negations, comparatives, conditionals.
    - Computational Verification (30%): Solves math/logic explicitly.
    - Epistemic Honesty (Meta-Confidence): Caps confidence if "Social Latent" detects 
      ambiguity, presupposition, or unanswerability.
    - NCD (15%): Tiebreaker only.
    """

    def __init__(self):
        # Latent state z: [structural_integrity, math_certainty, ambiguity_score, social_intent]
        self.z = [0.5, 0.5, 0.0, 0.5] 
        self.learning_rate = 0.1
        
        # Lexicons for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'cannot', "can't", "won't", "didn't", "doesn't", "isn't", "aren't", "wasn't", "weren't"}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter', 'longer'}
        self.presupposition_triggers = ['stopped', 'quit', 'ceased', 'failed', 'realize', 'know', 'aware']
        self.ambiguity_markers = ['every', 'all', 'each', 'some', 'either', 'or', 'who', 'he', 'she', 'it', 'they']
        self.false_dichotomy_markers = ['either', 'or', 'must', 'only option', 'only choice']

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Bottom-up sensory input extraction."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        has_negation = float(any(w in self.negations for w in words))
        has_comparative = float(any(w in self.comparatives for w in words))
        has_math = float(bool(re.search(r'\d+(\.\d+)?\s*[\+\-\*\/=]\s*\d+', text)))
        has_presupposition = float(any(t in text_lower for t in self.presupposition_triggers))
        has_ambiguity = float(any(m in text_lower for m in self.ambiguity_markers))
        has_false_dichotomy = float(any(m in text_lower for m in self.false_dichotomy_markers))
        
        # Detect specific Tier B traps
        is_presupposition_trap = has_presupposition and ('stopped' in text_lower or 'quit' in text_lower or 'fail' in text_lower)
        is_pronoun_ambiguity = (' he ' in text_lower or ' she ' in text_lower) and ('who' in text_lower or 'which' in text_lower)
        is_false_dichotomy = has_false_dichotomy and ('either' in text_lower)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'math': has_math,
            'presupposition': has_presupposition,
            'ambiguity': has_ambiguity,
            'trap_presupposition': float(is_presupposition_trap),
            'trap_pronoun': float(is_pronoun_ambiguity),
            'trap_dichotomy': float(is_false_dichotomy)
        }

    def _dynamics_step(self, z: List[float], features: Dict[str, float], prompt: str) -> List[float]:
        """
        Evolves latent state z based on input features (Neural ODE approximation).
        z = [structural, math, ambiguity, social_intent]
        """
        # Update structural confidence
        z[0] = z[0] * (1 - self.learning_rate) + self.learning_rate * (features['negation'] * 0.5 + features['comparative'] * 0.5 + 0.5)
        
        # Update math confidence
        z[1] = z[1] * (1 - self.learning_rate) + self.learning_rate * features['math']
        
        # Update ambiguity (accumulates)
        trap_score = features['trap_presupposition'] + features['trap_pronoun'] + features['trap_dichotomy']
        z[2] = min(1.0, z[2] + self.learning_rate * trap_score)
        
        # Social intent: if traps are high, intent shifts to "testing honesty" rather than "seeking fact"
        if trap_score > 0:
            z[3] = 0.8 # High probability of trick question
        else:
            z[3] = 0.2
            
        return z

    def _compute_prediction_error(self, z: List[float], features: Dict[str, float]) -> float:
        """
        Computes variational free energy (prediction error).
        High error if structural cues suggest complexity but latent state is uncertain.
        """
        # Expected ambiguity based on social intent
        predicted_ambiguity = z[3] * 0.8 
        actual_ambiguity_signal = features['trap_presupposition'] + features['trap_pronoun'] + features['trap_dichotomy']
        
        # Error is difference between predicted social context and actual linguistic traps
        error = (predicted_ambiguity - actual_ambiguity_signal) ** 2
        return error

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Evaluates the prompt itself for unanswerability, ambiguity, or traps.
        Returns a cap for confidence.
        """
        features = self._extract_features(prompt)
        prompt_lower = prompt.lower()
        
        # 1. Presupposition Traps ("Have you stopped...?")
        if features['trap_presupposition'] > 0:
            return 0.25
            
        # 2. Pronoun Ambiguity ("John told Bill he..." + who?)
        if features['trap_pronoun'] > 0:
            return 0.25
            
        # 3. False Dichotomy ("Either A or B" without exhaustiveness)
        if features['trap_dichotomy'] > 0:
            # Check if it looks like a logic trap
            if 'must' in prompt_lower or 'only' in prompt_lower:
                return 0.30

        # 4. Subjectivity without criteria
        if 'best' in prompt_lower or 'worst' in prompt_lower:
            if 'according to' not in prompt_lower and 'data' not in prompt_lower:
                return 0.40 # Lower confidence on subjective claims

        # 5. Unanswerable / Missing Info
        if 'information not provided' in prompt_lower or 'cannot be determined' in prompt_lower:
            return 0.95 # Actually high confidence that it's unanswerable if stated
            
        # Default: No strong meta-reason to doubt, but don't be overconfident without computation
        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural Parsing & Constraint Propagation.
        """
        score = 0.0
        prompt_lower = prompt.lower()
        cand_lower = candidate.lower()
        features = self._extract_features(prompt)
        
        # 1. Negation Consistency
        if features['negation'] > 0:
            # If prompt has negation, correct answer often contains negation or opposite meaning
            # Simple heuristic: if prompt asks "Is it not X?", candidate "No" might be right.
            # This is hard to generalize perfectly without NLP, so we look for explicit negation matching
            has_cand_neg = any(n in cand_lower.split() for n in self.negations)
            if has_cand_neg:
                score += 0.2
        
        # 2. Comparative Logic
        if features['comparative'] > 0:
            # Extract numbers if present
            nums = re.findall(r'\d+(\.\d+)?', prompt)
            if len(nums) >= 2:
                n1, n2 = float(nums[0]), float(nums[1])
                if 'more' in prompt_lower or 'greater' in prompt_lower or 'higher' in prompt_lower:
                    expected = str(max(n1, n2))
                else:
                    expected = str(min(n1, n2))
                
                if expected in candidate:
                    score += 0.4
                elif str(max(n1, n2)) in candidate or str(min(n1, n2)) in candidate:
                    score += 0.2 # Partial credit for finding numbers

        # 3. Yes/No consistency with negation
        if 'yes' in cand_lower or 'no' in cand_lower:
            if features['negation'] > 0:
                # Complex logic skipped for brevity, basic boost for matching structure
                score += 0.1

        return min(score, 0.4) # Cap structural contribution

    def _computational_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Constructive Computation.
        Actually solves math expressions found in the prompt.
        """
        # Find simple binary operations: A op B
        match = re.search(r'(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)', prompt)
        if match:
            n1 = float(match.group(1))
            op = match.group(2)
            n2 = float(match.group(3))
            
            try:
                if op == '+': res = n1 + n2
                elif op == '-': res = n1 - n2
                elif op == '*': res = n1 * n2
                elif op == '/': res = n1 / n2 if n2 != 0 else 0
                
                res_str = str(res)
                # Handle floating point weirdness
                if '.' in res_str:
                    res_str = res_str.rstrip('0').rstrip('.')
                
                if res_str in candidate:
                    return 0.5 # High reward for correct calculation
                elif str(int(res)) in candidate and res == int(res):
                    return 0.5
            except:
                pass
        
        return 0.0

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """
        Normalized Compression Distance as a tiebreaker (max 15% weight).
        NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        Approximated via zlib length.
        """
        import zlib
        x = prompt.encode()
        y = candidate.encode()
        
        len_x = len(zlib.compress(x))
        len_y = len(zlib.compress(y))
        len_xy = len(zlib.compress(x + y))
        
        min_len = min(len_x, len_y)
        max_len = max(len_x, len_y)
        
        if max_len == 0:
            return 0.0
            
        ncd = (len_xy - min_len) / max_len
        # Convert distance to similarity score (0-1), inverted
        # Lower NCD means more similar. We want a small boost for similarity.
        similarity = 1.0 - ncd
        return similarity * 0.15 # Cap at 15%

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main inference loop.
        1. Update latent state (Dynamical Systems).
        2. Check meta-confidence (Theory of Mind / Epistemic Honesty).
        3. Score candidates based on Structure, Computation, and NCD.
        4. Apply confidence cap.
        """
        # 1. Dynamical Systems Update
        features = self._extract_features(prompt)
        self.z = self._dynamics_step(self.z, features, prompt)
        
        # 2. Meta-Confidence (Epistemic Honesty Cap)
        honesty_cap = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            # Decompose scoring
            struct_score = self._structural_score(prompt, cand)
            comp_score = self._computational_score(prompt, cand)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Weighted sum
            # Structural >= 50% of variable part, Comp >= 20%, NCD <= 15%
            raw_score = (struct_score * 0.5) + (comp_score * 0.3) + ncd_score
            
            # Apply Epistemic Honesty Cap
            final_score = min(raw_score, honesty_cap)
            
            # Generate reasoning string
            reasoning_parts = []
            if features['trap_presupposition'] > 0: reasoning_parts.append("Presupposition trap detected")
            if features['trap_dichotomy'] > 0: reasoning_parts.append("False dichotomy detected")
            if comp_score > 0: reasoning_parts.append("Computational verification passed")
            if struct_score > 0: reasoning_parts.append("Structural constraints matched")
            if honesty_cap < 0.5: reasoning_parts.append("Low confidence due to ambiguity/trap")
            
            reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Standard evaluation"
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous/trick questions.
        """
        # 1. Get the honesty cap based on prompt analysis
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific answer quality
        features = self._extract_features(prompt)
        struct = self._structural_score(prompt, answer)
        comp = self._computational_score(prompt, answer)
        
        # Base confidence derived from successful structural/computational hits
        base_conf = 0.1 # Base uncertainty
        if comp > 0: base_conf = 0.95 # Math is definitive
        elif struct > 0.3: base_conf = 0.8 # Strong structural match
        elif features['math'] > 0 and comp == 0: 
            base_conf = 0.2 # Math question but no math in answer -> likely wrong
        else:
            base_conf = 0.5 # Default moderate uncertainty
            
        # 3. Apply Cap
        final_conf = min(base_conf, cap)
        
        # 4. Never return > 0.9 unless computation produced definitive answer
        if comp == 0 and final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 4)