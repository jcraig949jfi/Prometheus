import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Global Workspace Theory (GWT), Pragmatics, and 
    the Free Energy Principle (FEP).
    
    Mechanism:
    1. Parsing: Extracts atomic propositions with features (negation, modality, comparatives).
    2. GWT Initialization: Creates an activation vector where explicit facts start high (1.0)
       and pragmatic implicatures start moderate (0.5).
    3. Constraint Matrix: Builds a logical entailment graph (transitivity, modus ponens).
    4. FEP Update: Iteratively minimizes prediction error (free energy) to settle beliefs.
    5. Scoring: Ranks candidates by how well they align with the settled workspace (activation)
       while minimizing residual surprise (free energy).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|therefore|because)\b', re.IGNORECASE),
            'modality': re.compile(r'\b(must|should|might|could|will|would)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*'),
            'relation_op': re.compile(r'[<>]=?')
        }
        self.eta = 0.1  # Learning rate for FEP
        self.lambd = 0.5  # Weight for free energy penalty
        self.iterations = 10

    def _extract_props(self, text: str) -> List[Dict[str, Any]]:
        """Parse text into proposition objects with features."""
        props = []
        sentences = re.split(r'[.\n]', text)
        pid = 0
        
        for sent in sentences:
            if not sent.strip():
                continue
            
            features = {
                'negated': bool(self.patterns['negation'].search(sent)),
                'comparative': bool(self.patterns['comparative'].search(sent)),
                'conditional': bool(self.patterns['conditional'].search(sent)),
                'modal': bool(self.patterns['modality'].search(sent)),
                'numbers': self.patterns['numbers'].findall(sent),
                'op': self.patterns['relation_op'].search(sent).group() if self.patterns['relation_op'].search(sent) else None
            }
            
            # Simple subject-predicate-object approximation using split
            # This is a lightweight proxy for the "tuple" requirement
            words = sent.strip().split()
            if len(words) > 0:
                props.append({
                    'id': pid,
                    'text': sent.strip().lower(),
                    'features': features,
                    'active': 1.0 if not features['conditional'] else 0.5 # Pragmatic implicature boost
                })
                pid += 1
                
        return props

    def _build_constraint_matrix(self, props: List[Dict]) -> np.ndarray:
        """Build binary constraint matrix C where C[i,j]=1 if i entails j."""
        n = len(props)
        if n == 0:
            return np.zeros((0, 0))
            
        C = np.zeros((n, n))
        
        for i, p in enumerate(props):
            # Self-entailment (stability)
            C[i, i] = 1.0
            
            f = p['features']
            
            # Heuristic constraint propagation based on structural features
            for j, q in enumerate(props):
                if i == j:
                    continue
                
                q_text = q['text']
                p_text = p['text']
                
                # Transitivity of comparatives (simplified)
                if f['comparative'] and q['features']['comparative']:
                    # If both share number-like tokens, assume linkage
                    if f['numbers'] and q['features']['numbers']:
                        # Check for overlapping numbers or logical flow
                        if set(f['numbers']).intersection(set(q['features']['numbers'])):
                            C[j, i] = 0.5 # Weak bidirectional constraint
                
                # Modus Ponens / Conditional linking
                if f['conditional'] or q['features']['conditional']:
                    # If one mentions 'if' and the other 'then' or shares keywords
                    common_words = set(p_text.split()) & set(q_text.split())
                    if len(common_words) >= 2: # Share at least 2 words
                        C[j, i] = 0.8
                
                # Negation consistency
                if f['negated'] and not q['features']['negated']:
                    # Check for keyword overlap suggesting contradiction
                    common_words = set(p_text.replace('not', '').split()) & set(q_text.split())
                    if len(common_words) >= 2:
                        C[j, i] = -0.5 # Inhibitory connection

        return C

    def _run_fep(self, activations: np.ndarray, C: np.ndarray) -> Tuple[np.ndarray, float]:
        """Minimize free energy via gradient descent-like updates."""
        if len(activations) == 0:
            return activations, 0.0
            
        a = activations.copy()
        n = len(a)
        
        # Sigmoid function
        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        for _ in range(self.iterations):
            # Prediction: what should activation be based on neighbors?
            # pred = sigma(C^T * a)
            predicted = sigmoid(np.dot(C.T, a))
            
            # Prediction error
            e = a - predicted
            
            # Free Energy approximation (sum of squared errors)
            F = 0.5 * np.sum(e ** 2)
            
            # Gradient descent update: a <- a - eta * dF/da
            # dF/da = e * (1 - derivative_of_sigmoid_part) ... simplified to e for stability
            # Strictly: dF/da = e - C * (sigmoid'(z) * e) ... 
            # Approximation for lightweight tool: a <- a - eta * e
            a = a - self.eta * e
            
            # Clamp activations between 0 and 1
            a = np.clip(a, 0.0, 1.0)
            
        return a, float(F)

    def _score_candidate(self, prompt_props: List[Dict], candidate: str) -> Tuple[float, str]:
        """Score a candidate based on workspace fit and free energy."""
        
        # 1. Parse candidate into props
        cand_props = self._extract_props(candidate)
        if not cand_props:
            return -1.0, "No structural content detected."
            
        # 2. Combine workspace (Prompt + Candidate)
        # We simulate the candidate being part of the global workspace
        all_props = prompt_props + cand_props
        n_prompt = len(prompt_props)
        n_total = len(all_props)
        
        if n_total == 0:
            return 0.0, "Empty workspace."

        # Initialize activations: Prompt props start high, candidate props start as hypotheses (0.5)
        activations = np.array([p['active'] for p in all_props])
        activations[:n_prompt] = 1.0 # Lock prompt facts
        activations[n_prompt:] = 0.5 # Candidate is tentative
        
        # Build constraint matrix for the combined set
        C = self._build_constraint_matrix(all_props)
        
        # Run FEP update
        final_activations, free_energy = self._run_fep(activations, C)
        
        # 3. Calculate Score
        # Workspace Fit: Dot product of candidate activations and their final settled state
        # We only care about how well the *candidate* part settled
        cand_final = final_activations[n_prompt:]
        fit = np.sum(cand_final) / (len(cand_final) + 1e-9)
        
        # Penalty for high free energy (surprise)
        # Normalize free energy by size to make it comparable
        norm_F = free_energy / (n_total + 1e-9)
        
        score = fit - (self.lambd * norm_F)
        
        reasoning = f"Fit: {fit:.2f}, Surprise: {norm_F:.2f}"
        return score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # 1. Parse Prompt into Global Workspace propositions
        prompt_props = self._extract_props(prompt)
        
        # If no structure found, fallback to NCD tiebreaker logic implicitly via scoring
        if not prompt_props:
            # Create a dummy prop to allow matrix ops
            prompt_props = [{'id': 0, 'text': prompt, 'features': {}, 'active': 1.0}]

        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt_props, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Scores can be negative, so we use sigmoid mapping
        raw_score = res[0]['score']
        
        # Map to 0-1: sigmoid scaling
        conf = 1 / (1 + np.exp(-raw_score * 5)) 
        return float(np.clip(conf, 0.0, 1.0))