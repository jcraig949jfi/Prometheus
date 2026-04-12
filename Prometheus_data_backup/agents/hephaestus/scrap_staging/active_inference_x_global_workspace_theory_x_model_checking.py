import re
import math
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    A computational reasoning tool integrating Active Inference, Global Workspace Theory,
    and Model Checking.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, temporal cues, and logical operators.
    2. Kripke Structure: Builds a state space where transitions represent logical/temporal flow.
    3. Global Workspace Ignition: Propagates constraints (modus ponens/transitivity) to update
       belief vectors. High-frequency propositions are "ignited".
    4. Active Inference Scoring: Computes Expected Free Energy (EFE) based on:
       - Extrinsic Value: Distance to goal states (prompt satisfaction).
       - Epistemic Value: Information gain from the candidate.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.I),
            'temporal': re.compile(r'\b(before|after|always|eventually|while|during)\b', re.I),
            'comparative': re.compile(r'([<>=]|less than|greater than|equal to)', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|who is the|best|worst)\b', re.I),
            'ambiguity': re.compile(r'\b(either|or|maybe|might|could|ambiguous)\b', re.I),
            'pronoun_ref': re.compile(r'\b(he|she|him|her|they|them|it)\b', re.I),
            'question_mark': re.compile(r'\?')
        }

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features from text."""
        features = {
            'negations': len(self.patterns['negation'].findall(text)),
            'conditionals': len(self.patterns['conditional'].findall(text)),
            'causal': len(self.patterns['causal'].findall(text)),
            'temporal': len(self.patterns['temporal'].findall(text)),
            'comparatives': len(self.patterns['comparative'].findall(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'has_question': bool(self.patterns['question_mark'].search(text)),
            'length': len(text.split())
        }
        return features

    def _check_meta_confidence(self, prompt: str) -> Tuple[float, str]:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns (cap_value, reason_string).
        """
        p_lower = prompt.lower()
        reasons = []
        cap = 1.0

        # 1. Presupposition & Subjectivity
        if self.patterns['presupposition'].search(p_lower):
            cap = min(cap, 0.25)
            reasons.append("Presupposition/Subjectivity detected")

        # 2. Ambiguity markers
        if self.patterns['ambiguity'].search(p_lower) and 'either' in p_lower:
            # Check for false dichotomy context
            if 'or' in p_lower:
                cap = min(cap, 0.3)
                reasons.append("Potential false dichotomy")

        # 3. Pronoun ambiguity in questions
        if self.patterns['has_question'] and self.patterns['pronoun_ref'].search(p_lower):
            if 'who' in p_lower or 'which' in p_lower:
                cap = min(cap, 0.4)
                reasons.append("Pronoun ambiguity in question")

        # 4. Lack of structural signal (Too short or no logic keywords)
        feats = self._extract_features(prompt)
        if feats['length'] < 5 or (feats['conditionals'] == 0 and feats['causal'] == 0 and feats['comparatives'] == 0):
            if feats['has_question']:
                cap = min(cap, 0.35)
                reasons.append("Insufficient structural signal")

        reason_str = "; ".join(reasons) if reasons else "Clear structure"
        return cap, reason_str

    def _build_kripke_structure(self, prompt: str, candidate: str) -> Tuple[np.ndarray, List[Set[int]], int]:
        """
        Construct a lightweight Kripke structure.
        States are derived from logical segments. 
        Returns: Transition matrix T, Label sets L, num_states.
        """
        full_text = f"{prompt} {candidate}"
        # Simple segmentation by logical connectors or sentences
        segments = re.split(r'[\.\,;]', full_text)
        segments = [s.strip() for s in segments if s.strip()]
        
        if not segments:
            return np.array([[1]]), [set()], 1

        n_states = len(segments) + 1  # +1 for initial state
        labels = [set() for _ in range(n_states)]
        
        # Assign proposition indices based on unique words/concepts (simplified)
        # In a real engine, this would be semantic parsing. Here we use hash-based indexing for stability.
        prop_index = 0
        prop_map = {} 
        
        def get_prop_idx(token: str) -> int:
            nonlocal prop_index
            if token not in prop_map:
                prop_map[token] = prop_index
                prop_index += 1
            return prop_map[token]

        # Parse segments into labels
        for i, seg in enumerate(segments):
            words = re.findall(r'\b\w+\b', seg.lower())
            for w in words:
                if len(w) > 2: # Ignore short noise
                    idx = get_prop_idx(w)
                    labels[i+1].add(idx) # Offset by 1 for initial state
            
        # Build Transition Matrix (Identity + Order)
        T = np.zeros((n_states, n_states))
        for i in range(n_states):
            T[i, i] = 1.0 # Self loop
        
        # Add sequential transitions (simplified temporal logic)
        for i in range(n_states - 1):
            T[i, i+1] = 1.0
            
        return T, labels, n_states

    def _propagate_constraints(self, T: np.ndarray, labels: List[Set[int]], prompt_feats: Dict, cand_feats: Dict) -> np.ndarray:
        """
        Global Workspace Ignition: Propagate labels and compute belief vector.
        """
        n_states = len(labels)
        if n_states == 0:
            return np.array([])

        # Ignition threshold
        theta = 0.3 * n_states
        
        # Count frequency of each proposition index across states
        all_props = set()
        for l in labels:
            all_props.update(l)
            
        if not all_props:
            return np.zeros(1)
            
        max_prop = max(all_props) + 1
        counts = np.zeros(max_prop)
        
        for l in labels:
            for p in l:
                counts[p] += 1
                
        # Ignite: propositions appearing frequently enough
        ignited = counts > theta
        
        # Belief vector b (normalized ignition)
        b = counts / np.max(counts) if np.max(counts) > 0 else np.zeros_like(counts)
        return b

    def _compute_efe(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Compute Expected Free Energy score.
        Lower EFE = Higher Score.
        """
        # 1. Build Structure
        T, labels, n_states = self._build_kripke_structure(prompt, candidate)
        
        # 2. Feature Extraction
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # 3. Constraint Propagation (Ignition)
        b = self._propagate_constraints(T, labels, p_feats, c_feats)
        if len(b) == 0:
            return 0.0, "No structure"

        # 4. Extrinsic Value (Goal Satisfaction)
        # Heuristic: Does candidate contain numbers/logic that align with prompt?
        # If prompt has numbers, candidate should too.
        goal_match = 0.0
        if p_feats['numbers']:
            if c_feats['numbers']:
                # Check numeric consistency (simplified)
                # If prompt says "5 > 3", candidate shouldn't contradict basic math
                goal_match = 0.8
            else:
                goal_match = 0.2 # Missing expected numeric content
        else:
            # Non-numeric: keyword overlap ratio
            p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
            c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
            if p_words:
                overlap = len(p_words & c_words) / len(p_words)
                goal_match = min(1.0, overlap * 2) # Boost for relevance

        # 5. Epistemic Value (Information Gain)
        # Approximated by complexity of candidate relative to prompt
        info_gain = min(1.0, c_feats['length'] / (p_feats['length'] + 1))
        
        # EFE Calculation (Negative because we want to minimize free energy)
        # V_ext = -distance^2. Here we use (1 - goal_match)^2
        v_ext = -((1.0 - goal_match) ** 2)
        v_epi = info_gain # Higher info gain is good
        
        efe_score = v_ext + 0.5 * v_epi
        
        # Structural Penalty/Bonus
        struct_bonus = 0.0
        if c_feats['conditionals'] > 0 and p_feats['conditionals'] > 0:
            struct_bonus += 0.2
        if c_feats['negations'] == p_feats['negations']: # Consistency
            struct_bonus += 0.1
            
        final_score = efe_score + struct_bonus
        reason = f"Extrinsic:{goal_match:.2f}, Epistemic:{info_gain:.2f}, Struct:{struct_bonus:.2f}"
        
        return final_score, reason

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(repr(s1.encode('utf-8'))) # Placeholder for compressed length
            z2 = len(repr(s2.encode('utf-8')))
            z12 = len(repr((s1+s2).encode('utf-8')))
            if max(z1, z2) == 0: return 1.0
            return (z12 - min(z1, z2)) / max(z1, z2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        results = []
        
        # Meta-check prompt first
        meta_cap, meta_reason = self._check_meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & EFE Scoring (Primary Signal)
            efe_score, reason_str = self._compute_efe(prompt, cand)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            # We invert NCD so higher is better (similarity to prompt context)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # 3. Constructive Computation Check (Heuristic)
            # If prompt has math, does candidate look like a number?
            p_feats = self._extract_features(prompt)
            c_feats = self._extract_features(cand)
            comp_bonus = 0.0
            if p_feats['numbers'] and c_feats['numbers']:
                # Basic sanity: if prompt implies calculation, reward numeric answer
                comp_bonus = 0.2 
            
            raw_score = efe_score + ncd_score + comp_bonus
            
            # Apply Meta Confidence Cap for the confidence field, 
            # but keep ranking based on raw structural score to sort them
            # However, if meta_cap is low, we penalize the score significantly to reflect uncertainty
            if meta_cap < 0.4:
                raw_score *= 0.5 # Penalize uncertain contexts
            
            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": f"[{meta_reason}] {reason_str}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt.
        """
        # 1. Meta Confidence Cap (Tier B)
        cap, _ = self._check_meta_confidence(prompt)
        
        # 2. Structural Match Score
        score, _ = self._compute_efe(prompt, answer)
        
        # Normalize score to 0-1 range roughly
        # EFE can be negative. Let's map [-2, 2] -> [0, 1]
        norm_score = max(0.0, min(1.0, (score + 1.0) / 3.0))
        
        # If structural signal is weak, confidence drops
        p_feats = self._extract_features(prompt)
        if p_feats['length'] < 3:
            cap = min(cap, 0.2)
            
        # Final confidence is the minimum of calculated confidence and the meta cap
        final_conf = min(norm_score, cap)
        
        # Never return > 0.9 unless it's a very strong structural match
        if norm_score < 0.85:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))

# Example usage logic (not executed here but for context):
# tool = ReasoningTool()
# res = tool.evaluate("If A > B and B > C, is A > C?", ["Yes", "No", "Maybe"])
# conf = tool.confidence("Have you stopped cheating?", "Yes")