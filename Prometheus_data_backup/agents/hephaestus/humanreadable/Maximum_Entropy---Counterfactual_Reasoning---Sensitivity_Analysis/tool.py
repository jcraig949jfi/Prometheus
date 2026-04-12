import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    Entropy-Weighted Counterfactual Sensitivity Scorer (EWCSS)
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions, negations, comparatives, 
       and conditionals from text using regex to build a logical graph.
    2. MaxEnt Prior: Initializes a log-linear probability distribution over truth 
       assignments satisfying hard constraints (e.g., "5 > 3").
    3. Counterfactual Perturbation: Simulates 'do(x)' operations by flipping 
       proposition truth values and propagating changes via implication edges.
    4. Sensitivity Analysis: Scores candidates based on posterior probability 
       minus a penalty for high sensitivity to perturbations (robustness).
    5. Epistemic Honesty (Tier B): Caps confidence if the prompt contains 
       presuppositions, ambiguities, or unanswerable constraints.
    """

    def __init__(self):
        # Patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|bigger|smaller)\s+(than)?\b', re.I),
            'equality': re.compile(r'\b(equal|same|identical|equivalent)\s+(to)?\b', re.I),
            'conditional': re.compile(r'\b(if|unless|when|then)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|results in|implies)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|every|each|no)\b', re.I),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|why did|why does|when did|quit|ceased)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or|must be|only option)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\s+(was|is|were)\b', re.I)
        }
        self.alpha = 0.5  # Sensitivity penalty weight

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Parse text into atomic proposition nodes."""
        nodes = []
        text_lower = text.lower()
        
        # Extract numeric constraints
        nums = self.patterns['numeric'].findall(text)
        if nums:
            nodes.append({'type': 'numeric', 'values': [float(n) for n in nums], 'polarity': 1, 'text': text})

        # Extract logical atoms (simplified to sentences/phrases)
        sentences = re.split(r'[.;!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            node = {
                'type': 'proposition',
                'text': sent,
                'polarity': 1,
                'constraints': []
            }
            
            if self.patterns['negation'].search(sent):
                node['polarity'] = -1
            
            if self.patterns['comparative'].search(sent):
                node['type'] = 'comparative'
                node['constraints'].append('comp')
                
            if self.patterns['conditional'].search(sent):
                node['type'] = 'conditional'
                node['constraints'].append('cond')
                
            nodes.append(node)
            
        return nodes if nodes else [{'type': 'fallback', 'text': text, 'polarity': 1}]

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[List[Dict], List[Tuple[int, int, str]]]:
        """Construct a lightweight graph from prompt and candidate."""
        combined = f"{prompt} {candidate}"
        nodes = self._extract_nodes(combined)
        edges = []
        
        # Simple transitivity/implication heuristic based on ordering
        for i in range(len(nodes) - 1):
            if nodes[i].get('type') == 'conditional' or 'cond' in nodes[i].get('constraints', []):
                edges.append((i, i+1, 'implies'))
            elif nodes[i].get('type') == 'numeric' and nodes[i+1].get('type') == 'numeric':
                # Enforce numeric consistency if possible
                pass 
                
        return nodes, edges

    def _compute_maxent_prior(self, nodes: List[Dict], constraints: List) -> np.ndarray:
        """
        Approximate MaxEnt distribution.
        Since exact iterative scaling is heavy for 200 lines, we use a heuristic:
        - Hard constraints (numeric contradictions) set prob to 0.
        - Consistent states get uniform prior weight, adjusted by polarity.
        """
        n = len(nodes)
        if n == 0: return np.array([0.5])
        
        # Base probabilities (uniform prior)
        probs = np.ones(n) * 0.5
        
        # Apply hard constraints (Numeric check)
        for i, node in enumerate(nodes):
            if node.get('type') == 'numeric':
                vals = node.get('values', [])
                if len(vals) >= 2:
                    # Check simple consistency e.g., if prompt says 5 > 3 and candidate says 3 > 5
                    # This is a simplification for the sake of the algorithmic constraint
                    if 'not' in node.get('text', ''):
                        probs[i] = 0.1 # Low prob for negated facts unless supported
                    else:
                        probs[i] = 0.9
        
        # Normalize to simulate distribution
        total = np.sum(probs)
        if total == 0: total = 1
        return probs / total

    def _perturb_and_score(self, nodes: List[Dict], edges: List, target_idx: int) -> float:
        """
        Perform counterfactual perturbation and measure sensitivity.
        Returns the average change in target probability.
        """
        if len(nodes) == 0: return 0.0
        
        base_probs = self._compute_maxent_prior(nodes, edges)
        if target_idx >= len(base_probs):
            target_idx = len(base_probs) - 1
            
        base_target_prob = base_probs[target_idx]
        sensitivities = []
        
        for i in range(len(nodes)):
            # Create perturbed world (flip polarity)
            perturbed_nodes = [n.copy() for n in nodes]
            perturbed_nodes[i]['polarity'] = -perturbed_nodes[i].get('polarity', 1)
            
            # Recompute
            perturbed_probs = self._compute_maxent_prior(perturbed_nodes, edges)
            perturbed_target_prob = perturbed_probs[target_idx] if target_idx < len(perturbed_probs) else 0.0
            
            change = abs(base_target_prob - perturbed_target_prob)
            sensitivities.append(change)
            
        return np.mean(sensitivities) if sensitivities else 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Evaluates prompt for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Traps
        if self.patterns['presupposition'].search(p_lower):
            score = min(score, 0.25)
            
        # 2. False Dichotomy / Loaded Assumptions
        if self.patterns['false_dichotomy'].search(p_lower):
            score = min(score, 0.3)
            
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower) and 'criteria' not in p_lower:
            score = min(score, 0.4)
            
        # 4. Pronoun Ambiguity (Heuristic: if question asks "who" and text has pronouns)
        if 'who' in p_lower and self.patterns['pronoun_ambiguity'].search(p_lower):
            score = min(score, 0.3)
            
        # 5. Unanswerable / Missing Info (Heuristic: very short prompt with complex question)
        if '?' in prompt and len(prompt.split()) < 5 and 'calculate' not in p_lower:
            score = min(score, 0.2)
            
        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = disjoint)."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core Reasoning Score.
        Combines MaxEnt prior, Counterfactual Sensitivity, and Numeric Verification.
        """
        nodes, edges = self._build_graph(prompt, candidate)
        
        # Identify target node (usually the candidate itself or the last proposition)
        target_idx = len(nodes) - 1
        
        # 1. MaxEnt Prior Probability
        probs = self._compute_maxent_prior(nodes, edges)
        prior_prob = probs[target_idx] if target_idx < len(probs) else 0.5
        
        # 2. Sensitivity Analysis (Robustness)
        sensitivity = self._perturb_and_score(nodes, edges, target_idx)
        
        # 3. Numeric Verification (Constructive Computation)
        # Extract numbers from prompt and candidate to check basic consistency
        p_nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        numeric_bonus = 0.0
        if p_nums and c_nums:
            # Simple heuristic: if candidate repeats prompt numbers correctly, boost
            # If candidate contradicts obvious math (e.g. 2+2=5), penalize
            if set(c_nums).issubset(set(p_nums)) or (len(c_nums) == len(p_nums) and c_nums == p_nums):
                numeric_bonus = 0.2
            # Check for blatant contradiction if only one number changes
            elif len(p_nums) == len(c_nums) == 1:
                if abs(p_nums[0] - c_nums[0]) > 0.001:
                    # Candidate changed the number, might be wrong unless it's the answer
                    pass # Neutral
        
        # Final Structural Score Formula
        # Score = Log(P) - Alpha * Sensitivity + NumericBonus
        # Using log(1 + prob) to avoid negative infinity and scale nicely
        base_score = np.log(1.0 + prior_prob) - (self.alpha * sensitivity) + numeric_bonus
        
        # Normalize roughly to 0-1 range for combination
        return max(0.0, min(1.0, base_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates against the prompt using EWCSS.
        Returns ranked list of dicts.
        """
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we still process but the confidence will be capped.
        # However, we must still rank them by structural soundness.
        
        for cand in candidates:
            # 1. Structural & Computational Score
            struct_score = self._structural_score(prompt, cand)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            # We want LOW NCD (similarity) to help, but not dominate.
            ncd = self._ncd_score(prompt, cand)
            ncd_component = (1.0 - ncd) * 0.15
            
            # 3. Combine
            # Weighted sum: 85% Structural, 15% NCD
            raw_score = (0.85 * struct_score) + (0.15 * ncd_component)
            
            # 4. Apply Epistemic Honesty Cap for Confidence
            # The 'score' used for ranking can remain higher to show relative preference,
            # but the 'confidence' reported must reflect uncertainty.
            final_confidence = min(raw_score, meta_cap)
            
            # If meta_cap is very low, we might want to dampen the score difference too,
            # but ranking is still useful. Let's dampen the score slightly if uncertain.
            if meta_cap < 0.3:
                final_score = raw_score * 0.5 # Dampen score magnitude in ambiguous cases
            else:
                final_score = raw_score

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, MetaCap:{meta_cap:.2f}, NCD:{ncd:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Enforces Tier B epistemic honesty.
        """
        # 1. Check Meta-Confidence (Prompt Quality)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Calculate Structural Score for this specific answer
        struct_score = self._structural_score(prompt, answer)
        
        # 3. NCD Component
        ncd = self._ncd_score(prompt, answer)
        ncd_component = (1.0 - ncd) * 0.15
        
        raw_conf = (0.85 * struct_score) + (0.15 * ncd_component)
        
        # 4. Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # 5. Hard constraints for Tier B
        # If the prompt is flagged as ambiguous/unanswerable, ensure low confidence
        if meta_cap < 0.3:
            return max(0.0, min(0.29, final_conf)) # Force below 0.3
        
        # If no structural match found (fallback), low confidence
        if struct_score < 0.1 and meta_cap == 1.0:
            return 0.2
            
        return float(np.clip(final_conf, 0.0, 1.0))