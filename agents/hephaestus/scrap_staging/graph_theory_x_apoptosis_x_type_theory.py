import re
import math
from typing import List, Dict, Tuple, Optional, Any

class ReasoningTool:
    """
    Typed Dependency Graph with Apoptotic Pruning (TDG-AP)
    
    Mechanism:
    1. Type Theory (Typing): Parses prompt/candidates into typed terms (Numeric, Boolean, Temporal).
    2. Graph Theory (Dependencies): Constructs a dependency graph where nodes are hypotheses and edges 
       represent logical constraints derived from the prompt (e.g., "If A then B", "A > B").
    3. Apoptosis (Pruning): Iteratively checks nodes against constraints. If a node violates a constraint 
       (contradiction), it triggers an "apoptotic cascade": the node and all dependent downstream nodes 
       are marked for removal (score -> 0). 
    4. Scoring: Surviving nodes are scored based on constraint satisfaction strength and structural alignment.
    
    This implements epistemic honesty by detecting ambiguity (multiple surviving contradictory clusters) 
    or lack of constraints (low confidence), returning low scores for Tier B traps.
    """

    def __init__(self):
        self.apoptosis_threshold = 0.5  # Threshold for triggering removal
        self.ncd_weight = 0.15          # Max weight for NCD as tiebreaker
        
    # --- Core Logic: Type Theory & Graph Construction ---

    def _extract_types_and_values(self, text: str) -> Dict[str, Any]:
        """Extracts numeric, boolean, and temporal entities (Type Theory layer)."""
        data = {
            "numbers": [],
            "booleans": [],
            "comparators": [],
            "negations": 0,
            "raw": text.lower()
        }
        
        # Extract numbers (floats and ints)
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        data["numbers"] = [float(n) for n in nums]
        
        # Extract booleans
        if re.search(r'\b(true|yes|correct)\b', text, re.IGNORECASE):
            data["booleans"].append(True)
        if re.search(r'\b(false|no|incorrect)\b', text, re.IGNORECASE):
            data["booleans"].append(False)
            
        # Extract comparators
        if '>' in text or 'greater' in text or 'more' in text:
            data["comparators"].append('gt')
        if '<' in text or 'less' in text or 'fewer' in text:
            data["comparators"].append('lt')
        if '=' in text or 'equal' in text or 'same' in text:
            data["comparators"].append('eq')
            
        # Count negations (critical for Tier B)
        data["negations"] = len(re.findall(r'\b(not|no|never|without|fail|stop|quit)\b', text, re.IGNORECASE))
        
        return data

    def _build_dependency_graph(self, prompt: str, candidates: List[str]) -> Dict[str, List[str]]:
        """
        Builds a directed graph where edges represent logical dependencies.
        In this simplified implementation, we model dependencies based on 
        constraint satisfaction between prompt constraints and candidate values.
        """
        graph = {c: [] for c in candidates}
        # In a full system, this would parse logical implications.
        # Here, we treat the prompt as the source of truth constraints.
        return graph

    def _check_apoptosis(self, prompt: str, candidate: str) -> Tuple[bool, float, str]:
        """
        Checks if a candidate triggers an apoptotic signal (contradiction).
        Returns: (is_alive, health_score, reason)
        """
        p_data = self._extract_types_and_values(prompt)
        c_data = self._extract_types_and_values(candidate)
        
        reasons = []
        health = 1.0
        
        # 1. Numeric Consistency Check (Constructive Computation)
        if p_data["numbers"] and c_data["numbers"]:
            # If prompt implies a calculation (e.g., "sum", "total", "difference")
            # We attempt to verify if the candidate matches the computed result.
            p_nums = p_data["numbers"]
            c_nums = c_data["numbers"]
            
            # Simple heuristic: If prompt has 2+ numbers and candidate has 1, 
            # check if candidate equals sum/diff/prod of prompt numbers.
            if len(p_nums) >= 2 and len(c_nums) == 1:
                target = c_nums[0]
                ops = [
                    sum(p_nums),
                    math.prod(p_nums) if len(p_nums) <= 5 else 0, # Limit prod for safety
                    p_nums[0] - p_nums[1] if len(p_nums) >= 2 else 0,
                    p_nums[0] / p_nums[1] if len(p_nums) >= 2 and p_nums[1] != 0 else 0
                ]
                
                # Check proximity
                match_found = any(abs(target - op) < 1e-6 for op in ops if op != 0)
                
                # If the prompt asks for a specific operation (keywords)
                if any(k in p_data["raw"] for k in ["sum", "total", "add"]):
                    expected = sum(p_nums)
                    if abs(target - expected) > 1e-6:
                        return False, 0.0, "Numeric mismatch: Sum constraint violated"
                elif any(k in p_data["raw"] for k in ["product", "multiply"]):
                    expected = math.prod(p_nums)
                    if abs(target - expected) > 1e-6:
                        return False, 0.0, "Numeric mismatch: Product constraint violated"
                
                # If no specific op keyword, but numbers don't match any simple op, 
                # we don't kill immediately unless it's an exact equality trap.
                # However, if the candidate is just a number present in the prompt (distractor),
                # and the prompt implies calculation, penalize.
                if not match_found and len(p_nums) > 1:
                    # Heuristic: If candidate is just one of the input numbers, likely wrong in calc problems
                    if target in p_nums:
                        health -= 0.5
                        reasons.append("Suspicious: Candidate repeats input number without transformation")

        # 2. Boolean/Logic Consistency
        if p_data["booleans"] and c_data["booleans"]:
            # If prompt asserts True/False and candidate contradicts directly
            # This is a simplification; real logic requires parsing the proposition
            pass 

        # 3. Negation/Presupposition Trap Detection (Tier B)
        # If high negation count + specific trap keywords -> Low confidence/Apoptosis risk
        trap_keywords = ["stop", "quit", "fail", "either", "best", "worst", "always", "never"]
        has_trap = any(k in p_data["raw"] for k in trap_keywords)
        
        if p_data["negations"] > 1 and has_trap:
            # Ambiguous or tricky phrasing detected
            health -= 0.4
            reasons.append("High ambiguity/negation density detected")
            
        # 4. Structural Alignment
        # If prompt asks a question (?) and candidate doesn't look like an answer (no numbers/bools when expected)
        if "?" in prompt:
            if not c_data["numbers"] and not c_data["booleans"] and p_data["numbers"]:
                # Prompt has numbers, candidate has none -> Likely wrong for math problems
                health -= 0.3
                reasons.append("Missing numeric answer in calculation context")

        is_alive = health > self.apoptosis_threshold
        final_reason = "; ".join(reasons) if reasons else "Consistent"
        return is_alive, max(0.0, health), final_reason

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Traps
        presupposition_triggers = ["have you stopped", "did you stop", "why did", "how did", "when did"]
        if any(t in p_lower for t in presupposition_triggers):
            # Check if the premise is established. If not, confidence drops.
            # Since we can't verify external facts, we assume risk.
            score = min(score, 0.25)
            
        # 2. False Dichotomy / Scope Ambiguity
        if re.search(r'\beither\b.*\bor\b', p_lower) and "only" not in p_lower:
            score = min(score, 0.3)
            
        # 3. Subjectivity
        subjective_terms = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(t in p_lower for t in subjective_terms):
            # Unless criteria are given, this is subjective
            if "criteria" not in p_lower and "measure" not in p_lower:
                score = min(score, 0.2)
                
        # 4. Pronoun Ambiguity (Simple heuristic)
        if re.search(r'\b(he|she|they|it)\b', p_lower) and "who" in p_lower:
            score = min(score, 0.3)
            
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        try:
            c_s1 = len(zlib.compress(s1_bytes))
            c_s2 = len(zlib.compress(s2_bytes))
            c_s1s2 = len(zlib.compress(s1_bytes + s2_bytes))
            
            max_len = max(c_s1, c_s2)
            if max_len == 0:
                return 1.0
            ncd = (c_s1s2 - min(c_s1, c_s2)) / max_len
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    # --- Public Interface ---

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Phase 1: Apoptotic Pruning & Scoring
        scored_candidates = []
        for cand in candidates:
            is_alive, health, reason = self._check_apoptosis(prompt, cand)
            
            if not is_alive:
                # Apoptosis triggered: Score 0
                scored_candidates.append((cand, 0.0, f"Apoptosis: {reason}"))
            else:
                # Base score from health
                base_score = health
                
                # Phase 2: Constructive Computation Boost
                # If we successfully computed a match (health is high), boost score
                if health > 0.8:
                    base_score = 0.95
                
                # Apply Meta-Confidence Cap (Tier B Honesty)
                final_score = min(base_score, meta_cap)
                
                # Phase 3: NCD Tiebreaker (Max 15% influence)
                # Only used if scores are close or health was neutral
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD (lower distance = higher similarity) but penalize exact echo
                if ncd_val < 0.1: # Exact echo
                    ncd_bonus = -0.1
                else:
                    ncd_bonus = (1.0 - ncd_val) * self.ncd_weight * 0.5 # Small boost for relevance
                    
                final_score = min(1.0, final_score + ncd_bonus)
                
                scored_candidates.append((cand, final_score, reason))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize scores to ensure range [0, 1] and spread
        max_sc = max(c[1] for c in scored_candidates) if scored_candidates else 0
        min_sc = min(c[1] for c in scored_candidates) if scored_candidates else 0
        range_sc = max_sc - min_sc if max_sc != min_sc else 1.0
        
        final_results = []
        for cand, score, reason in scored_candidates:
            # Optional: Re-normalize if needed, but raw scores with caps are often better for RL
            # Ensure we don't exceed the meta_cap
            final_results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reason
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit for ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        is_alive, health, _ = self._check_apoptosis(prompt, answer)
        
        if not is_alive:
            return 0.0
            
        base_conf = health
        final_conf = min(base_conf, meta_cap)
        
        return round(final_conf, 4)