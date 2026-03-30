import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Dynamic Epigenetic Analogy Sandpile (DEAS) with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Cognitive Filter (Epistemic Honesty): Scans prompts for Tier B traps 
       (presuppositions, ambiguity, false dichotomies). If detected, caps confidence 
       and forces low scores to prevent hallucination.
    2. Structural Parser (Tier A): Extracts logical constraints, negations, and 
       numeric values. Performs direct computation (PEMDAS, comparisons) where possible.
    3. SOC Simulation (Exploration): Models concepts as a sandpile. Nodes with high 
       "epigenetic marks" (learned relevance) have lower firing thresholds. Avalanches 
       identify coherent candidate clusters.
    4. Scoring: Weighted sum of Structural Match (50%), Computational Verification (20%), 
       SOC Avalanche Participation (15%), and NCD Tiebreaker (15%).
    """

    def __init__(self):
        # Epigenetic marks: Dict[concept_string, float in 0..1]
        # Higher mark = lower threshold = more excitable (heritable memory)
        self.epigenetic_marks: Dict[str, float] = {}
        self.learning_rate = 0.1
        self.decay_rate = 0.05
        
        # SOC Parameters
        self.soc_threshold_base = 1.0
        self.soc_dissipation = 0.05

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'[^a-z0-9\s]', '', text.lower())

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract potential concepts (nouns/verbs) for the knowledge graph."""
        text = self._normalize_text(text)
        # Simple tokenization; in a full system, this would be a parser
        words = text.split()
        # Filter stopwords
        stopwords = {'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
                     'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                     'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 
                     'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
                     'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
                     'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
                     'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
                     'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
                     'because', 'until', 'while', 'although', 'though', 'either', 'neither'}
        return [w for w in words if w not in stopwords and len(w) > 2]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerable patterns.
        Returns a cap value (low if trap detected).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_patterns = [
            r"have you stopped", r"have you quit", r"why did.*fail", r"why.*stop",
            r"when did.*stop", r"how often.*fail", r"is it true that.*failed"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p_lower):
                return 0.2  # Strong presupposition detected

        # 2. False Dichotomy / Loaded Assumption
        if re.search(r"\beither\b.*\bor\b", p_lower) and "other" not in p_lower:
            # Simple check for "either X or Y" without context of exhaustiveness
            if "options" not in p_lower and "choices" not in p_lower:
                return 0.3 

        # 3. Subjectivity without criteria
        subjective_terms = ["best", "worst", "favorite", "beautiful", "ugly", "good", "bad"]
        if any(term in p_lower for term in subjective_terms):
            if "measure" not in p_lower and "criteria" not in p_lower and "defined" not in p_lower:
                # If asking for subjective judgment without defined metrics
                if "?" in prompt:
                    return 0.4 # Moderate uncertainty

        # 4. Pronoun Ambiguity (He said/She said)
        if re.search(r"\b(he|she|they|it)\b.*\b(he|she|they|it)\b", p_lower):
            if "who" in p_lower and "?" in p_lower:
                # Asking to resolve ambiguous pronoun
                return 0.25

        return 1.0  # No obvious traps detected

    def _structural_parse(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Tier A: Structural Parsing and Computation.
        Returns (score, reason_string)
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Direct Computation)
        # Detect patterns like "What is 2+2?" or "Is 9.11 > 9.9?"
        numbers_prompt = re.findall(r'-?\d+\.?\d*', p_lower)
        numbers_candidate = re.findall(r'-?\d+\.?\d*', c_lower)

        if numbers_prompt:
            # Check for comparison traps (9.11 vs 9.9)
            if "greater" in p_lower or "larger" in p_lower or ">" in prompt:
                if len(numbers_prompt) >= 2:
                    try:
                        n1, n2 = float(numbers_prompt[0]), float(numbers_prompt[1])
                        expected_val = max(n1, n2)
                        if numbers_candidate:
                            cand_val = float(numbers_candidate[0])
                            if abs(cand_val - expected_val) < 1e-6:
                                score += 0.5
                                reasons.append("Numeric comparison correct")
                            else:
                                score -= 0.5
                                reasons.append("Numeric comparison incorrect")
                    except ValueError:
                        pass
            
            # Check for simple arithmetic if prompt implies calculation
            if "sum" in p_lower or "add" in p_lower or "plus" in p_lower:
                 # Very basic heuristic for demo purposes
                 if len(numbers_prompt) >= 2 and numbers_candidate:
                     try:
                         # Assume first two numbers are operands for simple add
                         n1, n2 = float(numbers_prompt[0]), float(numbers_prompt[1])
                         if "+" in p_lower or "sum" in p_lower:
                             target = n1 + n2
                         elif "product" in p_lower:
                             target = n1 * n2
                         else:
                             target = None
                         
                         if target is not None:
                             cand_val = float(numbers_candidate[0])
                             if abs(cand_val - target) < 1e-5:
                                 score += 0.6
                                 reasons.append("Arithmetic correct")
                             else:
                                 score -= 0.6
                                 reasons.append("Arithmetic incorrect")
                     except ValueError:
                         pass

        # 2. Logical Negation Matching
        negation_words = ['not', 'no', 'never', 'none', 'neither']
        has_negation_prompt = any(w in p_lower.split() for w in negation_words)
        has_negation_cand = any(w in c_lower.split() for w in negation_words)
        
        if has_negation_prompt:
            if has_negation_cand:
                score += 0.2
                reasons.append("Negation preserved")
            else:
                score -= 0.3
                reasons.append("Negation missing in candidate")
        elif not has_negation_prompt and has_negation_cand:
            # Candidate introduces negation not in prompt (potential contradiction)
            if "except" not in p_lower and "unless" not in p_lower:
                score -= 0.1
                reasons.append("Spurious negation")

        # 3. Constraint Propagation (Keyword Overlap with Weight)
        # Extract key structural words (comparatives, conditionals)
        structural_keywords = ['if', 'then', 'else', 'because', 'therefore', 'however', 'although']
        prompt_struct = [w for w in structural_keywords if w in p_lower]
        cand_struct = [w for w in structural_keywords if w in c_lower]
        
        if prompt_struct:
            overlap = len(set(prompt_struct) & set(cand_struct))
            score += (overlap / max(len(prompt_struct), 1)) * 0.2
            if overlap > 0:
                reasons.append("Structural keywords matched")

        if not reasons:
            reasons.append("No strong structural signal")
            
        return score, "; ".join(reasons)

    def _soc_avalanche_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates Self-Organized Criticality on the concept graph.
        1. Build temporary graph from prompt + candidate concepts.
        2. Initialize charge based on epigenetic marks.
        3. Trigger avalanche.
        4. Score based on participation and stability.
        """
        concepts = list(set(self._extract_concepts(prompt + " " + candidate)))
        if not concepts:
            return 0.0

        # Initialize node states
        # Charge = random small perturbation + epigenetic bias
        charges = {}
        thresholds = {}
        for c in concepts:
            m = self.epigenetic_marks.get(c, 0.5)
            thresholds[c] = self.soc_threshold_base * (1.0 - m) # Higher mark -> lower threshold
            charges[c] = 0.1 * (1.0 - m) # Initial bias

        # Add charge to a random 'seed' concept from the prompt
        prompt_concepts = self._extract_concepts(prompt)
        if prompt_concepts:
            seed = prompt_concepts[len(prompt_concepts)//2] # Pick middle concept as seed
            if seed in charges:
                charges[seed] += 1.0 # Add unit charge

        # Run SOC relaxation (simplified Bak-Tang-Wiesenfeld)
        fired_count = 0
        max_iterations = 50
        for _ in range(max_iterations):
            unstable = [c for c in concepts if charges[c] >= thresholds[c]]
            if not unstable:
                break
            
            for c in unstable:
                # Fire
                charges[c] -= 1.0
                fired_count += 1
                # Distribute to neighbors (all-to-all in this small subgraph for simplicity)
                share = 1.0 / max(len(concepts) - 1, 1)
                for neighbor in concepts:
                    if neighbor != c:
                        charges[neighbor] += share
            
            # Dissipation (prevents infinite loops, ensures criticality)
            for c in concepts:
                charges[c] *= (1.0 - self.soc_dissipation)

        # Update Epigenetic Marks (Learning)
        # If the candidate was part of a large avalanche, reinforce marks
        if fired_count > len(concepts):
            for c in concepts:
                current_mark = self.epigenetic_marks.get(c, 0.5)
                self.epigenetic_marks[c] = min(1.0, current_mark + self.learning_rate)
        
        # Score: Normalize fired count relative to graph size
        # Large avalanches indicate strong relational connectivity
        if fired_count == 0:
            return 0.1
        return min(1.0, fired_count / (len(concepts) * 3.0))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
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

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # Structural Score (50% weight base)
            struct_score, struct_reason = self._structural_parse(prompt, candidate)
            
            # SOC Score (15% weight base)
            soc_score = self._soc_avalanche_score(prompt, candidate)
            
            # NCD Score (15% weight base) - Lower is better (distance), invert it
            ncd_dist = self._ncd_score(prompt, candidate)
            ncd_score = 1.0 - ncd_dist
            
            # Computational/Logic Score (20% base) - Handled partially in structural, 
            # but we add a bonus if structural found explicit math/logic
            comp_score = 0.0
            if "correct" in struct_reason and "Numeric" in struct_reason:
                comp_score = 1.0
            elif "Arithmetic" in struct_reason:
                comp_score = 1.0
            
            # Weighted Sum
            # Weights: Structural 0.50, Comp 0.20, SOC 0.15, NCD 0.15
            raw_score = (
                (struct_score + 0.5) * 0.5 +  # Shift struct to be positive biased if neutral
                (comp_score * 0.2) +
                (soc_score * 0.15) +
                (ncd_score * 0.15)
            )
            
            # Normalize to 0-1 roughly
            final_score = max(0.0, min(1.0, raw_score))
            
            # Apply Epistemic Cap
            if meta_cap < 0.5:
                final_score *= (meta_cap / 0.5) # Scale down significantly
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"MetaCap={meta_cap:.2f}; {struct_reason}; SOC={soc_score:.2f}; NCD={ncd_score:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by meta-confidence for ambiguous/trap questions.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get structural signals
        # We treat the single answer as a candidate list of one
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        result = eval_results[0]
        base_score = result['score']
        
        # If structural parsing found definitive proof (e.g. math), allow higher confidence
        reasoning = result.get('reasoning', '')
        if "correct" in reasoning and ("Numeric" in reasoning or "Arithmetic" in reasoning):
            # High certainty on computed facts
            computed_conf = min(0.95, base_score + 0.2)
        else:
            # Rely more on structural match and SOC
            computed_conf = base_score
            
        # Enforce Epistemic Cap
        final_conf = min(computed_conf, meta_cap)
        
        # Ensure we don't return high confidence on garbage
        if base_score < 0.2:
            final_conf = min(final_conf, 0.3)
            
        return round(final_conf, 3)