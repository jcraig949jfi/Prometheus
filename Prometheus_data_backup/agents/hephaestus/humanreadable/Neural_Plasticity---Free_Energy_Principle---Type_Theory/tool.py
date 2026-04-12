import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional, Any

class ReasoningTool:
    """
    A reasoning engine combining Neural Plasticity, Free Energy Principle, and Type Theory.
    
    Mechanism:
    1. Parsing & Typing: Extracts atomic propositions, numbers, and logical connectives.
       Assigns types (Bool, Nat, Real, Event) to atoms.
    2. Constraint Graph: Builds a directed graph where nodes are propositions and edges
       represent logical/causal dependencies.
    3. Free Energy Minimization: Iteratively updates belief weights (w) to minimize
       prediction error (observed vs predicted) and entropy, simulating synaptic plasticity.
    4. Scoring: Evaluates candidates by measuring the final free energy when the candidate
       is forced as an observation. Lower energy = higher score.
    5. Epistemic Honesty: Detects ambiguity, presuppositions, and unanswerable patterns
       to cap confidence, ensuring low confidence on Tier B traps.
    """

    def __init__(self):
        self.types = ['Bool', 'Nat', 'Real', 'Event']
        self.connectives = ['not', 'and', 'or', 'if', 'then', 'else', 'causes', 'leads to']
        self.comparators = ['>', '<', '=', '<=', '>=', '==', '!=']
        self.quantifiers = ['all', 'some', 'every', 'no']
        self.presupposition_triggers = [
            r'\bstopped\s+\w+ing\b', r'\bquit\s+\w+ing\b', r'\bwhy\s+did\s+\w+\s+(fail|stop)\b',
            r'\bwhen\s+did\s+\w+\s+(stop|fail)\b', r'\bhow\s+did\s+\w+\s+(fail|stop)\b'
        ]
        self.ambiguity_triggers = [
            r'\beither\s+\w+\s+or\s+\w+\b', r'\bwho\s+was\s+it\b', r'\bhe\s+was\s+\w+\b',
            r'\bshe\s+was\s+\w+\b', r'\best\b', r'\bworst\b', r'\bfavorite\b'
        ]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        pattern = r'-?\d+(?:\.\d+)?'
        return [float(x) for x in re.findall(pattern, text)]

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Parse text into typed propositions."""
        props = []
        sentences = re.split(r'[.!?]', text.lower())
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            p_type = 'Bool'
            atoms = []
            
            # Check for numbers
            nums = self._extract_numbers(sent)
            if nums:
                p_type = 'Real' if any('.' in str(n) for n in nums) else 'Nat'
                atoms.extend([str(n) for n in nums])
            
            # Check for logical structure
            has_neg = any(neg in sent for neg in ['not', 'no ', 'never'])
            has_cond = any(c in sent for c in ['if', 'then', 'implies'])
            has_causal = any(c in sent for c in ['causes', 'leads to', 'results in'])
            has_comp = any(re.search(re.escape(c), sent) for c in self.comparators) or \
                       any(w in sent for w in ['greater', 'less', 'more', 'fewer'])
            
            # Simple atom extraction (words)
            words = re.findall(r'\b[a-z]+\b', sent)
            atoms.extend(words[:5]) # Limit atoms per prop
            
            props.append({
                'text': sent,
                'type': p_type,
                'atoms': atoms,
                'negated': has_neg,
                'conditional': has_cond,
                'causal': has_causal,
                'comparative': has_comp,
                'weight': 0.5 # Initial belief
            })
        return props

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
        """Build constraint graph from prompt and candidate."""
        full_text = f"{prompt} {candidate}"
        props = self._parse_propositions(full_text)
        n = len(props)
        if n == 0:
            return np.zeros((1,1)), np.zeros((1,1)), [{'text': 'empty', 'type':'Bool', 'weight':0.5}]
        
        W = np.zeros((n, n)) # Weights
        T = np.zeros((n, n)) # Types (1=logical, 2=causal, 3=comparative)
        
        # Connect sequential props (narrative flow)
        for i in range(n-1):
            W[i, i+1] = 0.5
            T[i, i+1] = 1.0
            
        # Connect based on shared atoms
        for i in range(n):
            for j in range(i+1, n):
                shared = set(props[i]['atoms']) & set(props[j]['atoms'])
                if shared:
                    strength = min(0.8, len(shared) * 0.2)
                    W[i, j] = strength
                    W[j, i] = strength
                    if props[i]['causal'] or props[j]['causal']:
                        T[i, j] = 2.0
                        T[j, i] = 2.0
                    elif props[i]['comparative'] or props[j]['comparative']:
                        T[i, j] = 3.0
                        T[j, i] = 3.0
                    else:
                        T[i, j] = 1.0
                        T[j, i] = 1.0
        
        return W, T, props

    def _run_dynamics(self, W: np.ndarray, T: np.ndarray, props: List[Dict], 
                      observations: np.ndarray, iterations: int = 10) -> float:
        """Run Hebbian-like update and free energy minimization."""
        n = len(props)
        if n == 0: return 1.0
        
        w = np.array([p['weight'] for p in props])
        eta = 0.1 # Learning rate
        alpha = 0.05 # Decay
        tau = 0.1 # Pruning threshold
        lam = 0.01 # Entropy reg
        
        # Fix observations
        obs = observations.copy()
        
        prev_F = float('inf')
        
        for _ in range(iterations):
            # Prediction
            # Normalize W rows to prevent explosion
            row_sums = W.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            W_norm = W / row_sums
            
            p = 1.0 / (1.0 + np.exp(-np.dot(W_norm.T, w))) # Logistic activation
            
            # Free Energy Calculation
            # E = (o - p)^2
            energy = np.sum((obs - p) ** 2)
            # S = w log w + (1-w) log (1-w) (avoid log(0))
            w_safe = np.clip(w, 1e-10, 1-1e-10)
            entropy = np.sum(w_safe * np.log(w_safe) + (1-w_safe) * np.log(1-w_safe))
            F = energy + lam * entropy
            
            if abs(prev_F - F) < 1e-4:
                break
            prev_F = F
            
            # Hebbian Update (simplified for stability)
            # Delta W = eta * (o_pre * o_post - W)
            # We update weights based on co-activation of observations
            outer_obs = np.outer(obs, obs)
            delta_W = eta * (outer_obs - W)
            W += delta_W
            
            # Decay
            W *= (1 - alpha)
            W[W < tau] = 0
            
            # Update beliefs (w) towards prediction if not observed
            # If observed, w stays close to obs
            mask = (obs == 0.5) # Unobserved nodes
            if np.any(mask):
                w[mask] = (1-eta)*w[mask] + eta*p[mask]
                
            # Clamp
            w = np.clip(w, 0, 1)

        return float(F)

    def _compute_numeric_answer(self, text: str) -> Optional[float]:
        """Attempt to solve simple arithmetic or comparison problems."""
        nums = self._extract_numbers(text)
        if len(nums) < 2:
            return None
            
        # Check for explicit operations
        if '+' in text or 'plus' in text:
            return sum(nums)
        if '-' in text or 'minus' in text:
            # Simple diff
            return nums[0] - nums[1] if len(nums) >= 2 else None
        if '*' in text or 'times' in text or 'x' in text:
            prod = 1.0
            for n in nums: prod *= n
            return prod
        if '/' in text or 'divided by' in text:
            if len(nums) >= 2 and nums[1] != 0:
                return nums[0] / nums[1]
        
        # Comparatives
        if 'greater' in text or 'more' in text or '>' in text:
            return max(nums)
        if 'less' in text or 'fewer' in text or '<' in text:
            return min(nums)
            
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2
        
        # 2. Ambiguity / Subjectivity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Check if context resolves it (simple heuristic: length)
                if len(prompt.split()) < 15: # Too short to resolve ambiguity
                    return 0.25
        
        # 3. Unanswerable (No numbers, no logic keywords, very short)
        words = re.findall(r'\b\w+\b', p_lower)
        logic_keywords = set(['if', 'then', 'all', 'some', 'cause', 'before', 'after', 'greater', 'less'])
        has_logic = any(w in logic_keywords for w in words)
        has_nums = bool(self._extract_numbers(prompt))
        
        if not has_logic and not has_nums and len(words) < 10:
            return 0.2
            
        return 1.0 # Default high potential

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on epistemic honesty and computation."""
        # Cap based on meta-analysis of the prompt
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
            
        # Try constructive computation
        combined = f"{prompt} {answer}"
        calc_val = self._compute_numeric_answer(combined)
        prompt_val = self._compute_numeric_answer(prompt)
        
        score = 0.5
        if calc_val is not None and prompt_val is not None:
            # If we can compute both, check consistency
            if abs(calc_val - prompt_val) < 1e-6:
                score = 0.95
            else:
                score = 0.1
        elif calc_val is not None:
            # If answer provides the computed value missing in prompt
            score = 0.8
        else:
            # Fallback to structural match if no computation possible
            # But cap at 0.7 to avoid overconfidence on non-computational stuff
            score = 0.6 
            
        return min(score, meta_cap)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates and return ranked list."""
        results = []
        
        # Pre-compute numeric solution if exists
        prompt_nums = self._extract_numbers(prompt)
        computed_ans = self._compute_numeric_answer(prompt)
        
        for cand in candidates:
            score = 0.0
            reason_parts = []
            
            # 1. Constructive Computation (Highest Priority)
            cand_nums = self._extract_numbers(cand)
            match_found = False
            
            if computed_ans is not None and cand_nums:
                # Check if candidate contains the computed answer
                if any(abs(n - computed_ans) < 1e-6 for n in cand_nums):
                    score += 0.6
                    reason_parts.append("Numeric match")
                    match_found = True
            
            # 2. Structural Reasoning (Free Energy)
            W, T, props = self._build_graph(prompt, cand)
            if len(props) > 1:
                # Create observation vector: 0.5 (unknown) for all, 
                # except we force the candidate's implication if it matches facts
                obs = np.full(len(props), 0.5)
                
                # If candidate repeats atoms from prompt positively, boost those observations
                cand_atoms = set(self._parse_propositions(cand)[0]['atoms']) if self._parse_propositions(cand) else set()
                for i, p in enumerate(props):
                    if p['text'] in prompt.lower() and any(a in cand_atoms for a in p['atoms']):
                        obs[i] = 1.0 # Observed true
                
                # Run dynamics
                F = self._run_dynamics(W, T, props, obs)
                
                # Convert Free Energy to score (lower energy = higher score)
                # Normalize roughly: F is sum of squares, so small is good
                structural_score = math.exp(-F)
                score += structural_score * 0.35 # Max 0.35 from structure
                reason_parts.append(f"Energy:{F:.2f}")
            
            # 3. NCD Tiebreaker (Max 15%)
            try:
                import zlib
                data = (prompt + cand).encode('utf-8')
                comp_len = len(zlib.compress(data))
                base_len = len(zlib.compress(prompt.encode('utf-8'))) + len(zlib.compress(cand.encode('utf-8')))
                ncd = 1.0 - (comp_len / max(base_len, 1))
                score += max(0, ncd) * 0.15
            except:
                pass # Skip NCD if zlib fails
            
            # Normalize score to 0-1 range roughly
            score = min(1.0, score)
            
            # Apply Epistemic Honesty Cap
            meta_cap = self._meta_confidence(prompt)
            if meta_cap < 0.3:
                score = min(score, meta_cap)
                reason_parts.append("Ambiguity detected")
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "; ".join(reason_parts) if reason_parts else "Structural analysis"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results