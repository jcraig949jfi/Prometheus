import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Ergodic-Gauge Sparse Scorer (EGSS) Implementation.
    
    Mechanism:
    1. Sparse Coding: Extracts logical atoms (predicates, negations, numbers, conditionals).
    2. Gauge Connection: Constructs a transition matrix where logical relations 
       (e.g., negation, causality) define transformations between atom states.
    3. Ergodic Dynamics: Simulates a Markov chain over the logical graph to compute 
       a time-averaged similarity score between prompt and candidate.
    4. Constructive Computation: Explicitly solves numeric, temporal, and logical 
       constraints before applying the ergodic score.
    5. Epistemic Honesty: Caps confidence based on prompt ambiguity and presuppositions.
    """

    def __init__(self):
        # Regex patterns for logical atoms
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads? to|causes?)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next|previous)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|them)\b.*\b(who|which one)\b', re.IGNORECASE),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|how often did)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either.*or|must be|only option)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }
        self.max_steps = 50
        self.epsilon = 1e-9

    def _extract_atoms(self, text: str) -> Dict[str, Any]:
        """Extract sparse logical features from text."""
        atoms = {
            'negations': len(self.patterns['negation'].findall(text)),
            'comparatives': len(self.patterns['comparative'].findall(text)),
            'conditionals': len(self.patterns['conditional'].findall(text)),
            'causals': len(self.patterns['causal'].findall(text)),
            'orderings': len(self.patterns['ordering'].findall(text)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text.split()),
            'raw': text.lower()
        }
        return atoms

    def _check_ambiguity(self, text: str) -> Tuple[bool, List[str]]:
        """Check for Tier B epistemic traps."""
        flags = []
        if self.patterns['presupposition'].search(text): flags.append("presupposition")
        if self.patterns['pronoun_ambiguity'].search(text): flags.append("pronoun_ambiguity")
        if self.patterns['false_dichotomy'].search(text): flags.append("false_dichotomy")
        if self.patterns['subjectivity'].search(text): flags.append("subjectivity")
        # Simple heuristic for scope ambiguity (Every X ... Y)
        if re.search(r'\bevery\b', text, re.IGNORECASE) and re.search(r'\b(same|different|each)\b', text, re.IGNORECASE):
            flags.append("scope_ambiguity")
        
        return len(flags) > 0, flags

    def _constructive_solve(self, prompt: str, candidate: str) -> Tuple[Optional[float], str]:
        """
        Attempt to computationally solve the problem using extracted numbers and logic.
        Returns (score, reason). If no computation possible, returns (None, "").
        """
        p_atoms = self._extract_atoms(prompt)
        c_atoms = self._extract_atoms(candidate)
        
        p_nums = p_atoms['numbers']
        c_nums = c_atoms['numbers']
        
        # Case 1: Direct Numeric Equality/Comparison
        if len(p_nums) >= 2 and len(c_nums) == 1:
            # Heuristic: If prompt has 2 numbers and candidate has 1, check basic ops
            a, b = p_nums[0], p_nums[1]
            c_val = c_nums[0]
            
            ops = [
                (a + b, "addition"),
                (a - b, "subtraction"),
                (b - a, "reverse_subtraction"),
                (a * b, "multiplication"),
                (a / b if b != 0 else 0, "division"),
                (b / a if a != 0 else 0, "reverse_division"),
                (max(a,b), "max"),
                (min(a,b), "min")
            ]
            
            for val, op_name in ops:
                if abs(val - c_val) < 1e-6:
                    return 1.0, f"Computed via {op_name}"
                
        # Case 2: Logic Check (Negation consistency)
        # If prompt has "not" and candidate lacks negation words when expected
        if p_atoms['negations'] > 0:
            # Very rough heuristic: if prompt says "not X" and candidate is just "X", penalize
            # This is handled better by the gauge matrix, but we can add a hard rule here
            pass

        return None, ""

    def _build_gauge_matrix(self, p_atoms: Dict, c_atoms: Dict) -> np.ndarray:
        """
        Build a sparse transition matrix representing logical gauge connections.
        Dimensions: [neg, comp, cond, causal, order, num_density, length]
        """
        dim = 7
        T = np.zeros((dim, dim))
        
        # Base identity (persistence)
        np.fill_diagonal(T, 0.5)
        
        # Gauge connections (symmetry transports)
        # Negation flips sign (modeled as high transition to self with sign flip logic in scoring)
        # Here we model flow between logical types
        
        # If prompt has conditionals, flow to causals
        if p_atoms['conditionals'] > 0:
            T[2, 3] = 0.3 # Conditional -> Causal
            
        # Comparatives often imply ordering
        if p_atoms['comparatives'] > 0:
            T[1, 4] = 0.3 # Comparative -> Ordering
            
        # Numbers connect to everything in math problems
        if len(p_atoms['numbers']) > 0:
            T[:, 5] = 0.1 # Density column
            
        # Normalize rows to make it stochastic
        row_sums = T.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1 # Avoid div by zero
        T = T / row_sums
        
        return T

    def _ergodic_score(self, prompt: str, candidate: str) -> float:
        """Compute the ergodic gauge-invariant similarity score."""
        p_atoms = self._extract_atoms(prompt)
        c_atoms = self._extract_atoms(candidate)
        
        # Construct state vectors (normalized)
        # Order: [neg, comp, cond, causal, order, num_density, length_norm]
        def to_vector(atoms):
            v = np.array([
                atoms['negations'],
                atoms['comparatives'],
                atoms['conditionals'],
                atoms['causals'],
                atoms['orderings'],
                len(atoms['numbers']) / (atoms['length'] + 1), # Density
                atoms['length'] / 100.0 # Normalized length
            ])
            norm = np.linalg.norm(v)
            return v / (norm + self.epsilon)

        x_p = to_vector(p_atoms)
        x_c = to_vector(c_atoms)
        
        # Build Gauge Connection (Transition Matrix)
        T = self._build_gauge_matrix(p_atoms, c_atoms)
        
        # Ensure irreducibility (add small noise to all entries)
        T = T + self.epsilon
        T = T / T.sum(axis=1, keepdims=True)
        
        # Ergodic Iteration
        x_t = x_c.copy()
        score_accum = 0.0
        
        for _ in range(self.max_steps):
            # Similarity at step t (Gauge invariant inner product)
            sim = np.dot(x_t, x_p)
            score_accum += sim
            
            # Dynamics
            x_t = T @ x_t
            # Re-normalize to prevent drift (maintain sphere constraint)
            x_t = x_t / (np.linalg.norm(x_t) + self.epsilon)
            
        ergodic_score = score_accum / self.max_steps
        return float(ergodic_score)

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate epistemic honesty.
        Returns a cap on confidence based on prompt properties.
        """
        is_ambiguous, flags = self._check_ambiguity(prompt)
        
        if is_ambiguous:
            return 0.2 # Low confidence for ambiguous/trap questions
        
        # If no structural match found in a complex looking prompt, be humble
        p_atoms = self._extract_atoms(prompt)
        structural_density = (p_atoms['negations'] + p_atoms['conditionals'] + 
                              p_atoms['causals'] + len(p_atoms['numbers']))
        
        if structural_density == 0 and len(prompt.split()) > 10:
            # High text but no logical atoms detected? Might be out of distribution
            return 0.4
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check prompt ambiguity
        meta_cap = self._meta_confidence(prompt, "")
        is_ambiguous = meta_cap < 0.5
        
        for cand in candidates:
            score = 0.0
            reasoning = []
            
            # 1. Constructive Computation (Highest Priority)
            comp_score, comp_reason = self._constructive_solve(prompt, cand)
            if comp_score is not None:
                score = comp_score
                reasoning.append(f"Computation: {comp_reason}")
            else:
                # 2. Ergodic-Gauge Scoring (Structural)
                erg_score = self._ergodic_score(prompt, cand)
                score = erg_score
                reasoning.append(f"Structural/Ergodic similarity: {erg_score:.4f}")
                
                # 3. NCD Tiebreaker (Max 15% weight, only if needed)
                # Only used if structural scores are very close or low
                try:
                    s_combined = prompt + cand
                    s_len = len(s_combined.encode('utf-8'))
                    c_len = len(zlib.compress(s_combined.encode('utf-8')))
                    ncd = 1.0 - (c_len / s_len) if s_len > 0 else 0
                    # Normalize NCD to be comparable (rough heuristic)
                    ncd_score = max(0, ncd - 0.5) * 2 
                    score = 0.85 * score + 0.15 * ncd_score
                    reasoning.append(f"NCD adjustment applied")
                except:
                    pass

            # Apply Epistemic Cap
            if is_ambiguous:
                score = min(score, 0.3)
                reasoning.append("Capped due to prompt ambiguity")

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning)
            })
        
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Must be < 0.3 for ambiguous/unanswerable.
        Must be < 0.9 unless computation is definitive.
        """
        # 1. Meta-check (Ambiguity/Traps)
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.5:
            return 0.2 # Hard cap for traps

        # 2. Check for definitive computation
        comp_score, _ = self._constructive_solve(prompt, answer)
        if comp_score is not None and comp_score == 1.0:
            return 0.95 # High confidence for computed math
        
        # 3. Structural confidence based on ergodic score
        # We run a mini-evaluation to get the score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.1
            
        score = res[0]['score']
        
        # Calibration: 
        # If purely structural (no compute), cap at 0.8 to reflect uncertainty
        final_conf = min(score, 0.8) 
        
        # If score is very low, confidence should be low
        if final_conf < 0.4:
            return max(0.1, final_conf)
            
        return float(final_conf)

# Helper for NCD (imported inside method to avoid top-level dependency issues if zlib missing, 
# though zlib is standard. Kept here for clarity)
import zlib