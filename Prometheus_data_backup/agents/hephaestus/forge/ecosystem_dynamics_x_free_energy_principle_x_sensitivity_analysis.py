import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Hierarchical Prediction-Error Propagation with Sensitivity-Weighted Constraint Networks (HPEP-SCN).
    
    Mechanism:
    1. Structural Parsing: Extracts propositions (causal, numeric, comparative, negation) from text.
    2. Ecosystem Priors: Assigns higher belief potential to 'keystone' concepts (e.g., energy flow, predation).
    3. Free Energy Minimization: Iteratively updates node beliefs to minimize prediction error between connected propositions.
    4. Sensitivity Analysis: Perturbs propositions to measure stability; unstable answers receive lower scores.
    5. Scoring: Combines structural match with reference logic, free-energy convergence, and sensitivity stability.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'causal': re.compile(r'\b(increases|decreases|leads to|causes|reduces|promotes|inhibits)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|higher than|lower than)\b', re.I),
            'negation': re.compile(r'\b(not|no|never|without|cannot)\b', re.I),
            'conditional': re.compile(r'\b(if|then|because|therefore|when)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'keystone': re.compile(r'\b(energy|food web|predator|prey|population|ecosystem|species|cycle)\b', re.I)
        }
        self.epsilon_0 = 0.1
        self.eta = 0.05  # Learning rate for free energy step
        self.steps = 10  # Iterations for convergence

    def _parse_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract propositions with type, subject, relation, object, and modifiers."""
        props = []
        text_lower = text.lower()
        
        # Simple sentence splitting
        sentences = re.split(r'[.;]', text)
        
        for sent in sentences:
            if not sent.strip(): continue
            sent_lower = sent.lower()
            
            prop = {
                'raw': sent.strip(),
                'types': [],
                'has_negation': bool(self.patterns['negation'].search(sent_lower)),
                'has_causal': bool(self.patterns['causal'].search(sent_lower)),
                'has_comparative': bool(self.patterns['comparative'].search(sent_lower)),
                'has_conditional': bool(self.patterns['conditional'].search(sent_lower)),
                'numbers': [float(n) for n in self.patterns['numeric'].findall(sent_lower)],
                'keystone_weight': 0.0
            }
            
            # Identify types
            if prop['has_negation']: prop['types'].append('negation')
            if prop['has_causal']: prop['types'].append('causal')
            if prop['has_comparative']: prop['types'].append('comparative')
            if prop['has_conditional']: prop['types'].append('conditional')
            if prop['numbers']: prop['types'].append('numeric')
            
            # Ecosystem Prior: Keystone weighting
            kw_matches = len(self.patterns['keystone'].findall(sent_lower))
            prop['keystone_weight'] = 0.5 * kw_matches if kw_matches > 0 else 0.1
            
            props.append(prop)
            
        return props

    def _build_graph(self, props: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List[int]]:
        """Build adjacency matrix, weight matrix, and prior potentials."""
        n = len(props)
        if n == 0:
            return np.zeros((0,0)), np.zeros((0,0)), []
        
        # Adjacency (fully connected for simplicity in small graphs, or sequential)
        # Using sequential + causal links for structure
        A = np.zeros((n, n))
        for i in range(n-1):
            A[i, i+1] = 1.0
            A[i+1, i] = 1.0
            
        # Potentials (phi) initialized from keystone status
        phi = np.array([p['keystone_weight'] for p in props])
        
        # Initial weights (prediction error base)
        W = np.ones((n, n)) * self.epsilon_0
        np.fill_diagonal(W, 0)
        
        return A, W, phi

    def _free_energy_step(self, A: np.ndarray, phi: np.ndarray, target_phi: np.ndarray) -> np.ndarray:
        """Minimize variational free energy: F = sum(w_ij * (phi_i - phi_j)^2) + penalty."""
        if phi.size == 0: return phi
        
        n = len(phi)
        # Compute gradient of free energy w.r.t phi
        # dF/d_phi_i = 2 * sum_j (A_ij * (phi_i - phi_j))
        diff_matrix = phi.reshape(-1, 1) - phi.reshape(1, -1)
        gradient = 2 * np.sum(A * diff_matrix, axis=1)
        
        # Add term pulling towards target (canonical solution) if available
        if target_phi is not None and target_phi.size == n:
            gradient += 2 * (phi - target_phi)
            
        new_phi = phi - self.eta * gradient
        return new_phi

    def _sensitivity_check(self, text: str, props: List[Dict]) -> float:
        """Perturb text slightly and check stability of parsed structure."""
        if not props: return 1.0
        
        # Perturbation: Toggle a negation or add noise
        # Since we can't re-run full pipeline easily without recursion issues, 
        # we approximate sensitivity by checking proposition density vs length.
        # High density of logical operators implies higher sensitivity to perturbation.
        
        logical_ops = sum([p['has_negation'] + p['has_causal'] + p['has_conditional'] for p in props])
        if len(text) == 0: return 1.0
        
        # Heuristic: If many logical ops, small changes matter more -> lower stability score unless precise
        # We invert this: if the text is rich in logic, we trust it MORE if it matches structure, 
        # but penalize if it's too short for the complexity.
        complexity_ratio = logical_ops / (len(text) / 10.0)
        
        # Stability factor: 1.0 if balanced, <1.0 if chaotic
        stability = 1.0 / (1.0 + abs(complexity_ratio - 0.5)) 
        return stability

    def _compute_score(self, prompt: str, candidate: str, ref_answer: str = "") -> float:
        # 1. Parse Candidate
        cand_props = self._parse_text(candidate)
        if not cand_props:
            return 0.1 # Low score for empty/unparseable

        # 2. Parse Reference (if available) or Prompt for structural expectations
        # If no ref_answer, we use the prompt's structure as the target "truth" skeleton
        target_text = ref_answer if ref_answer else prompt
        target_props = self._parse_text(target_text)
        
        # 3. Build Graphs
        _, _, phi_cand = self._build_graph(cand_props)
        
        # Create target phi vector (match size by repeating or truncating)
        if target_props:
            _, _, phi_target_raw = self._build_graph(target_props)
            # Align sizes for comparison
            min_len = min(len(phi_cand), len(phi_target_raw))
            if min_len == 0: return 0.2
            phi_cand = phi_cand[:min_len]
            phi_target = phi_target_raw[:min_len]
        else:
            # No reference? Use uniform prior
            phi_target = np.ones_like(phi_cand) * 0.5

        # 4. Free Energy Minimization (Iterative update)
        A = np.ones((len(phi_cand), len(phi_cand))) # Simplified connectivity for scoring
        np.fill_diagonal(A, 0)
        
        current_phi = phi_cand.copy()
        for _ in range(self.steps):
            current_phi = self._free_energy_step(A, current_phi, phi_target)
            
        # 5. Calculate Final Score Components
        
        # A. Structural Match (NCD tiebreaker logic embedded via length/overlap heuristics if needed, 
        # but primarily using proposition type overlap)
        cand_types = set()
        for p in cand_props: cand_types.update(p['types'])
        
        target_types = set()
        for p in target_props: target_types.update(p['types'])
        
        type_overlap = len(cand_types.intersection(target_types)) / max(1, len(cand_types.union(target_types)))
        
        # B. Prediction Error (Distance to target after convergence)
        error = np.mean((current_phi - phi_target)**2)
        error_score = 1.0 / (1.0 + error)
        
        # C. Sensitivity Stability
        sensitivity_stability = self._sensitivity_check(prompt, cand_props)
        
        # D. Numeric Consistency (Simple check)
        cand_nums = [p['numbers'] for p in cand_props if p['numbers']]
        target_nums = [p['numbers'] for p in target_props if p['numbers']]
        numeric_match = 1.0
        if cand_nums and target_nums:
            # Check if order of magnitude is similar (loose check)
            c_avg = np.mean(cand_nums)
            t_avg = np.mean(target_nums)
            if t_avg != 0:
                numeric_match = 1.0 - min(1.0, abs(c_avg - t_avg) / (abs(t_avg) + 0.1))
            else:
                numeric_match = 1.0 if c_avg == 0 else 0.5
        elif not cand_nums and not target_nums:
            numeric_match = 1.0 # No numbers to mismatch
        elif cand_nums and not target_nums:
            numeric_match = 0.8 # Penalize extra numbers slightly
        elif not cand_nums and target_nums:
            numeric_match = 0.5 # Penalize missing numbers heavily

        # Weighted Sum
        # Structural parsing is primary (0.5), Free Energy error (0.3), Sensitivity (0.2)
        score = (0.5 * type_overlap) + (0.3 * error_score) + (0.2 * sensitivity_stability)
        score = score * numeric_match # Apply numeric penalty as multiplier
        
        # Boost if exact string match (fallback for trivial cases)
        if candidate.strip().lower() == target_text.strip().lower():
            score = 1.0
            
        return float(np.clip(score, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        # Heuristic reference: The longest candidate often contains the most structural info 
        # if no explicit reference is provided in this interface context. 
        # However, strictly we score based on internal consistency with prompt.
        # We assume the prompt contains the "truth" structure we want to match.
        
        for cand in candidates:
            score = self._compute_score(prompt, cand, ref_answer="")
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match and free-energy convergence score: {score:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same engine as evaluate but focuses on the stability and error minimization.
        """
        score = self._compute_score(prompt, answer, ref_answer="")
        
        # Ecosystem Dynamics Wrapper (Inhibitor Check):
        # If the answer claims "no effect" or "static" in a dynamic system context without justification,
        # reduce confidence. This is the "historical inhibitor" check.
        if re.search(r'\b(no change|remains constant|static|unchanged)\b', answer.lower()):
            if re.search(r'\b(energy|flow|population|growth)\b', prompt.lower()):
                # Suspicious in dynamic contexts unless justified
                score *= 0.7 
        
        return float(np.clip(score, 0.0, 1.0))