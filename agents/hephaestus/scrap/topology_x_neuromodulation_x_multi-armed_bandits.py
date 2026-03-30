import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Topologically-Aware Neuromodulated Bandit Controller (T-UCTH) for Hypothesis Testing.
    
    Mechanism:
    1. Topology (Simplicial Complex Approximation): Maps candidates to vertices. 
       Detects "holes" (gaps in reasoning space) by analyzing structural diversity 
       and missing logical transitions between candidates.
    2. Neuromodulation:
       - Dopamine: Drives exploitation based on structural match to prompt constraints.
       - Serotonin: Scales exploration bonus when topological "holes" (ambiguity/lack of coverage) are detected.
       - Acetylcholine: Adjusts learning rate (confidence capping) when inconsistencies arise.
    3. Multi-Armed Bandit: Ranks candidates using a UCB-like index combining structural score 
       and topological exploration bonus.
       
    Epistemic Honesty (Tier B): Prioritizes detecting presuppositions, ambiguities, and unanswerable 
    queries by capping confidence and boosting exploration (serotonin) when structural parsers fail.
    """

    def __init__(self):
        self.serotonin_gain = 1.0  # Exploration scaling
        self.dopamine_baseline = 0.5  # Exploitation baseline
        self.acetylcholine_lr = 0.1  # Learning rate for confidence updates
        
        # Patterns for Tier B (Judgment) detection
        self.presupposition_patterns = [
            r"\b(stopped|quit|ceased|failed|stopped)\s+(doing|the|your)?\s*\w+",
            r"\bwhy\s+did\s+\w+\s+(fail|stop|leave)",
            r"\bwhen\s+did\s+\w+\s+(stop|fail)",
        ]
        self.scope_patterns = [
            r"\bevery\s+\w+.*\ba\s+\w+",  # Every X did a Y
            r"\ball\s+\w+.*\bthe\s+\w+",
        ]
        self.pronoun_patterns = [
            r"\b(he|she|him|her|it|they)\s+was\s+(wrong|right|late)",
            r"\btold\s+\w+\s+(he|she|him|her)",
        ]
        self.false_dichotomy_patterns = [
            r"\beither\s+\w+\s+or\s+\w+",
            r"\bis\s+it\s+\w+\s+or\s+\w+",
        ]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _structural_parse(self, prompt: str) -> Dict[str, any]:
        """Extracts logical structures: negations, comparatives, numbers."""
        features = {
            "negation": bool(re.search(r"\b(not|no|never|neither|without)\b", prompt.lower())),
            "comparative": bool(re.search(r"\b(more|less|greater|smaller|better|worse|higher|lower)\b", prompt.lower())),
            "conditional": bool(re.search(r"\b(if|then|unless|provided)\b", prompt.lower())),
            "numbers": re.findall(r"\d+\.?\d*", prompt),
            "question_type": "unknown"
        }
        
        if "?" in prompt:
            if re.search(r"\b(how many|calculate|sum|total)\b", prompt.lower()):
                features["question_type"] = "numeric_calc"
            elif re.search(r"\b(which|who|what)\s+is\s+(bigger|smaller|more|less)", prompt.lower()):
                features["question_type"] = "numeric_compare"
            elif re.search(r"\b(true|false|correct)\b", prompt.lower()):
                features["question_type"] = "verification"
                
        return features

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Evaluates prompt for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 - 1.0). Low value = high ambiguity/trap.
        """
        p_lower = prompt.lower()
        risk_score = 0.0
        
        # Check Presuppositions
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_lower):
                risk_score += 0.6
                
        # Check Scope Ambiguity
        for pattern in self.scope_patterns:
            if re.search(pattern, p_lower):
                risk_score += 0.3
                
        # Check Pronoun Ambiguity
        if re.search(r"\bwho\s+is\s+(he|she|it)\b", p_lower) or re.search(r"\b(refer|refers)\s+to\s+who", p_lower):
             risk_score += 0.5
             
        # Check False Dichotomy
        for pattern in self.false_dichotomy_patterns:
            if re.search(pattern, p_lower):
                # Only penalize if no clear exhaustive context is implied (simplified heuristic)
                if "only" not in p_lower and "exclusive" not in p_lower:
                    risk_score += 0.4

        # Check for subjective/unanswerable without context
        subjective_words = ["best", "worst", "favorite", "beautiful", "moral"]
        if any(word in p_lower for word in subjective_words) and "context" not in p_lower:
            risk_score += 0.5

        # Convert risk to confidence cap
        # High risk -> Low cap
        cap = 1.0 - min(risk_score, 0.9)
        return cap

    def _evaluate_structure(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constructive computation.
        Returns a score 0.0 - 1.0 based on logical fit.
        """
        features = self._structural_parse(prompt)
        score = 0.0
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive)
        if features["numbers"] and features["question_type"] in ["numeric_calc", "numeric_compare"]:
            try:
                # Extract numbers from candidate
                c_nums = re.findall(r"\d+\.?\d*", candidate)
                if c_nums:
                    c_val = float(c_nums[0])
                    p_nums = [float(x) for x in features["numbers"]]
                    
                    if "bigger" in prompt.lower() or "larger" in prompt.lower() or "more" in prompt.lower():
                        if c_val == max(p_nums): score += 0.8
                    elif "smaller" in prompt.lower() or "less" in prompt.lower():
                        if c_val == min(p_nums): score += 0.8
                    elif "sum" in prompt.lower() or "total" in prompt.lower():
                        if abs(c_val - sum(p_nums)) < 0.01: score += 0.8
            except:
                pass

        # 2. Negation Handling
        if features["negation"]:
            neg_words = ["not", "no", "never"]
            if any(w in c_lower for w in neg_words):
                score += 0.4
            else:
                # Penalty for ignoring negation in prompt
                score -= 0.2

        # 3. Conditional/Logic Check
        if features["conditional"]:
            if any(w in c_lower for w in ["if", "then", "unless", "depends"]):
                score += 0.3
        
        # 4. Direct Answer Matching for Verification
        if features["question_type"] == "verification":
            if "true" in c_lower or "yes" in c_lower:
                score += 0.2 # Base prior
            if "false" in c_lower or "no" in c_lower:
                score += 0.2

        return max(0.0, min(1.0, score))

    def _topological_bonus(self, prompt: str, candidates: List[str]) -> Dict[int, float]:
        """
        Simulates topological hole detection.
        If candidates are structurally similar (low diversity), a 'hole' exists in the hypothesis space.
        Returns a bonus for candidates that are diverse (fill the hole).
        """
        if len(candidates) < 2:
            return {i: 0.0 for i in range(len(candidates))}
            
        # Simple proxy for persistence: variance in NCD from prompt
        # High variance = good coverage. Low variance = hole (clustered hypotheses).
        distances = []
        for i, c in enumerate(candidates):
            d = self._compute_ncd(prompt, c)
            distances.append((i, d))
            
        if not distances:
            return {}
            
        avg_dist = sum(d[1] for d in distances) / len(distances)
        
        # If all candidates are very similar to prompt (or each other), we have a "hole" in exploration
        # We boost candidates that are slightly further (exploration)
        bonuses = {}
        for i, d in distances:
            # Serotonin-like signal: Boost deviation from mean if cluster is tight
            # If the cluster is already diverse, bonus is low.
            diversity_penalty = 0.1 if abs(d - avg_dist) < 0.05 else 0.0
            bonuses[i] = self.serotonin_gain * diversity_penalty
            
        return bonuses

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Cognitive Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Topological Analysis (Hole Detection)
        topo_bonuses = self._topological_bonus(prompt, candidates)
        
        results = []
        for i, candidate in enumerate(candidates):
            # Structural Score (Dopamine - Exploitation)
            struct_score = self._evaluate_structure(prompt, candidate)
            
            # NCD Tiebreaker (Max 15% influence)
            ncd_val = self._compute_ncd(prompt, candidate)
            # Invert NCD so lower distance = higher score, normalize roughly
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Topological Bonus (Serotonin - Exploration)
            bonus = topo_bonuses.get(i, 0.0)
            
            # Combined Score
            # Weighting: Structural (50%), Computation (20%), NCD (15%), Topo (15%)
            raw_score = (struct_score * 0.5) + (0.2 if struct_score > 0.5 else 0.0) + ncd_score + bonus
            
            # Apply Meta-Cognitive Cap if prompt is ambiguous
            # If meta_cap is low, we suppress high confidence in ANY candidate
            if meta_cap < 0.3:
                raw_score = min(raw_score, 0.25) # Cap score for ambiguous prompts
            
            results.append({
                "candidate": candidate,
                "score": round(raw_score, 4),
                "reasoning": f"Structural:{struct_score:.2f}, Topo:{bonus:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous/trap questions.
        """
        # 1. Check Meta-Confidence (The "Honesty" Filter)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        struct_score = self._evaluate_structure(prompt, answer)
        ncd_val = self._compute_ncd(prompt, answer)
        
        # Base confidence from structure and similarity
        base_conf = (struct_score * 0.6) + ((1.0 - ncd_val) * 0.2)
        
        # Boost if computation was definitive (e.g. exact number match in numeric questions)
        features = self._structural_parse(prompt)
        if features["question_type"] == "numeric_calc":
            c_nums = re.findall(r"\d+\.?\d*", answer)
            p_nums = [float(x) for x in features["numbers"]]
            if c_nums and p_nums:
                try:
                    if abs(float(c_nums[0]) - sum(p_nums)) < 0.001:
                        base_conf = 0.95 # High confidence on correct math
                except: pass

        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless definitive computation (handled above), 
        # but ensure we don't exceed meta_cap
        return round(final_conf, 4)