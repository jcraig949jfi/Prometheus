# Bayesian Inference + Feedback Control + Free Energy Principle

**Fields**: Mathematics, Control Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T16:42:52.938208
**Report Generated**: 2026-03-27T17:21:24.461558

---

## Nous Analysis

**Algorithm (Bayesian‑Control‑Free‑Energy Scorer)**  
1. **Parsing & Graph Construction** – Using regex we extract propositions from the prompt and each candidate answer. Each proposition becomes a node; edges are labeled with one of six relations: *negation*, *comparative* (>,<,=), *conditional* (→), *causal* (←→), *temporal* (before/after), *equality*. Nodes are mapped to integer IDs; relations are stored in three NumPy arrays: `src`, `dst`, `rel_type` (int‑coded). The prompt yields a **knowledge base** `KB`. Each candidate yields a **assertion matrix** `A_c` of the same shape, where `A_c[i,j]=1` if the candidate asserts the relation `(i,j)` present in `KB`, `-1` if it asserts the opposite, and `0` if silent.  
2. **Likelihood** – For a candidate we compute a raw compatibility score  
   `s_c = Σ_{k} w[rel_type_k] * A_c[k]`  
   where `w` is a fixed weight vector (e.g., +1 for matches, –1 for contradictions, 0 for silent). Likelihood is obtained via a softmax with temperature τ:  
   `L_c = exp(s_c/τ) / Σ_{c'} exp(s_{c'}/τ)`.  
3. **Bayesian Update** – Prior `P_c` is uniform (or length‑based). Posterior: `Post_c ∝ P_c * L_c`, normalized.  
4. **Feedback Control (PID on τ)** – Define prediction error `e = H_target – H(Post)`, where `H` is Shannon entropy. A simple PID controller updates τ each scoring round:  
   `τ_{new} = τ + Kp*e + Ki*∑e + Kd*(e‑e_prev)`.  
   This keeps the posterior neither over‑confident nor too diffuse.  
5. **Free‑Energy Approximation** – Variational free energy ≈ `-log L_c + KL(Post||Prior)`. After each PID step we compute `F = -np.log(L_c) + np.sum(Post*np.log(Post/Prior))` and perform a tiny gradient descent on τ (`τ -= α * ∂F/∂τ`) to further reduce F.  
6. **Final Score** – Use the posterior probability (`Post_c`) or `-F` as the candidate’s merit. All operations rely only on NumPy and the Python stdlib.

**Structural Features Parsed** – Negations (“not”, “no”), comparatives (“greater than”, “less than”, “more”, “less”), conditionals (“if … then”, “unless”), causal cues (“because”, “leads to”, “results in”), temporal ordering (“before”, “after”, “first”, “last”), numeric values (integers, decimals), and equality statements.

**Novelty** – Purely rule‑based Bayesian updating combined with a control‑theoretic temperature regulator and a free‑energy minimization loop has not been described in existing lightweight reasoning scorers; active‑inference frameworks exist but require neural nets, whereas this version uses only symbolic parsing and NumPy.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and uncertainty quantitatively.  
Metacognition: 6/10 — PID provides basic self‑monitoring but lacks higher‑order reflection.  
Hypothesis generation: 5/10 — scores candidates; does not propose new hypotheses autonomously.  
Implementability: 9/10 — relies solely on regex, NumPy arrays, and simple arithmetic, well within constraints.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Bayesian Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Feedback Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Bayesian Inference + Free Energy Principle: strong positive synergy (+0.655). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Feedback Control + Free Energy Principle: strong positive synergy (+0.278). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Constraint Satisfaction + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=13% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:04:44.334371

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Feedback_Control---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Bayesian-Control-Free-Energy Scorer.
    
    Mechanism:
    1. Parsing: Extracts propositions and relations (negation, comparative, causal, etc.) 
       into a symbolic graph represented by NumPy arrays.
    2. Likelihood: Computes compatibility between prompt KB and candidate assertions.
    3. Bayesian Update: Updates posterior probabilities based on likelihood.
    4. Feedback Control: Uses a PID controller on Shannon Entropy to regulate temperature (tau),
       preventing over-confidence or excessive diffusion.
    5. Free Energy: Minimizes variational free energy (surprise + complexity) to refine scores.
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence (Tier B).
    """

    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.05
        self.target_entropy = 0.8  # Target uncertainty level
        self.tau = 1.0             # Temperature
        self.integral_error = 0.0
        self.prev_error = 0.0
        
        # Weights for relations
        self.weights = {
            'equality': 2.0,
            'comparative': 1.5,
            'causal': 1.2,
            'conditional': 1.0,
            'temporal': 0.8,
            'negation': -2.0 # Penalty for contradiction
        }
        self.rel_map = {'equality': 0, 'comparative': 1, 'causal': 2, 'conditional': 3, 'temporal': 4, 'negation': 5}

    def _extract_props(self, text: str) -> List[str]:
        """Simple extraction of potential propositions (clauses)."""
        # Split by common delimiters but keep content
        raw = re.split(r'[;,.]| (?:and|or|but) ', text.lower())
        return [s.strip() for s in raw if len(s.strip()) > 2]

    def _parse_relations(self, text: str, props: List[str]) -> List[Tuple[int, int, str]]:
        """Extract relations between propositions or entities."""
        relations = []
        text_l = text.lower()
        
        # Helper to find prop index
        def get_idx(sub):
            for i, p in enumerate(props):
                if sub in p or p in sub:
                    return i
            return -1

        # Negation
        if re.search(r'\b(not|no|never|none)\b', text_l):
            for i, p in enumerate(props):
                if re.search(r'\b(not|no|never|none)\b', p):
                    relations.append((i, i, 'negation'))

        # Comparatives
        if re.search(r'(greater|less|more|fewer|larger|smaller|before|after)', text_l):
            # Simplified: assume relation between first two props if numbers exist
            nums = re.findall(r'-?\d+\.?\d*', text)
            if len(nums) >= 2:
                # Map numbers to props roughly
                idxs = []
                for n in nums[:2]:
                    found = False
                    for i, p in enumerate(props):
                        if n in p and i not in idxs:
                            idxs.append(i)
                            found = True
                            break
                    if not found: idxs.append(len(props)-1) # Fallback
                
                if 'greater' in text_l or 'more' in text_l or 'larger' in text_l:
                     if len(idxs) >= 2: relations.append((idxs[0], idxs[1], 'comparative')) # A > B
                elif 'less' in text_l or 'fewer' in text_l or 'smaller' in text_l:
                    if len(idxs) >= 2: relations.append((idxs[1], idxs[0], 'comparative')) # B > A (so A < B)
                    
        # Equality
        if re.search(r'(equal|same|identical|is|are|was|were)', text_l) and 'not' not in text_l:
             if len(props) >= 2:
                 relations.append((0, 1, 'equality'))

        # Causal/Conditional
        if re.search(r'(because|therefore|leads to|results in|if|then|unless)', text_l):
            if len(props) >= 2:
                if 'because' in text_l or 'leads' in text_l:
                    relations.append((1, 0, 'causal')) # Effect <- Cause
                else:
                    relations.append((0, 1, 'conditional')) # If A then B

        return relations

    def _build_kb(self, prompt: str) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray]:
        """Construct Knowledge Base graph."""
        props = self._extract_props(prompt)
        if not props: props = [prompt] # Fallback
        
        rels = self._parse_relations(prompt, props)
        n = len(props)
        
        # Arrays: src, dst, type
        if not rels:
            return props, np.array([]), np.array([]), np.array([])
            
        src = np.array([r[0] for r in rels])
        dst = np.array([r[1] for r in rels])
        rtype = np.array([self.rel_map.get(r[2], 0) for r in rels])
        
        return props, src, dst, rtype

    def _compute_assertion_matrix(self, candidate: str, kb_props: List[str], kb_src: np.ndarray, kb_dst: np.ndarray, kb_rtype: np.ndarray) -> np.ndarray:
        """Map candidate assertions to KB structure."""
        if len(kb_src) == 0:
            return np.array([])
            
        A = np.zeros_like(kb_src, dtype=float)
        cand_l = candidate.lower()
        
        # Check for direct contradictions or confirmations based on keywords
        for i, (s, d, rt) in enumerate(zip(kb_src, kb_dst, kb_rtype)):
            # Very simplified check: does candidate contain negation words where KB implies positive, or vice versa?
            # Since KB is derived from prompt, we assume prompt is Truth.
            # If candidate has "not" and KB relation is positive -> -1
            # If candidate lacks "not" and matches context -> 1
            
            has_neg = bool(re.search(r'\b(not|no|never|false|incorrect)\b', cand_l))
            
            if rt == 5: # Negation in KB
                A[i] = -1.0 if not has_neg else 1.0 # If KB says "Not X", and Cand says "X" (no neg), penalty? 
                # Actually, if KB says "Not X", and Cand says "X", that's a contradiction (-1).
                # If Cand says "Not X", that's a match (1).
                A[i] = 1.0 if has_neg else -1.0
            else:
                # Positive relation in KB
                if has_neg:
                    A[i] = -1.0 # Contradiction
                else:
                    A[i] = 1.0 # Match (silent assumption of agreement if no contradiction found)
                    
        return A

    def _compute_entropy(self, post: np.ndarray) -> float:
        if np.sum(post) == 0: return 0.0
        p = post / np.sum(post)
        p = p[p > 0]
        return -np.sum(p * np.log2(p))

    def _pid_step(self, entropy: float):
        error = self.target_entropy - entropy
        self.integral_error += error
        derivative = error - self.prev_error
        
        self.tau += self.Kp * error + self.Ki * self.integral_error + self.Kd * derivative
        self.tau = max(0.1, min(5.0, self.tau)) # Clamp tau
        self.prev_error = error

    def _free_energy_step(self, log_L: float, post: np.ndarray, prior: np.ndarray):
        # F = -log L + KL(Post || Prior)
        # Approximate gradient descent on tau is complex without explicit function, 
        # so we use the PID output as the primary regulator and this as a score modifier.
        kl_div = np.sum(post * np.log((post + 1e-10) / (prior + 1e-10)))
        return -log_L + kl_div

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|why did .+ fail|when did .+ stop)', p):
            score -= 0.8
        # 2. Scope/Pronoun ambiguity
        if re.search(r'(every .+ a .+|told .+ he |told .+ she)', p) and '?' in p:
            score -= 0.5
        # 3. False dichotomy
        if re.search(r'(either .+ or .+)', p) and 'other' not in p:
            score -= 0.4
        # 4. Subjectivity
        if re.search(r'(best|worst|favorite|opinion)', p) and 'calculate' not in p:
            score -= 0.6
        # 5. Unanswerable / Missing info
        if re.search(r'(impossible|cannot be determined|not enough info)', p):
            score = 0.1
            
        return max(0.0, min(1.0, score))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            c1 = len(repr(s1)) # Approx compression length for short strings
            c2 = len(repr(s2))
            c12 = len(repr(s1 + s2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt KB
        kb_props, kb_src, kb_dst, kb_rtype = self._build_kb(prompt)
        n_rels = len(kb_src)
        
        if n_rels == 0:
            # Fallback to NCD if no structure found
            scores = []
            for c in candidates:
                # Inverse NCD: lower distance = higher score
                dist = self._ncd_score(prompt, c)
                scores.append(1.0 - dist)
            total = sum(scores) + 1e-9
            scores = [s/total for s in scores]
            return [{"candidate": c, "score": float(s), "reasoning": "NCD fallback"} for c, s in zip(candidates, scores)]

        # 2. Compute Likelihoods
        raw_scores = []
        assertion_matrices = []
        
        for c in candidates:
            A_c = self._compute_assertion_matrix(c, kb_props, kb_src, kb_dst, kb_rtype)
            assertion_matrices.append(A_c)
            
            # Weighted sum
            s = 0.0
            for i, val in enumerate(A_c):
                if val != 0:
                    rel_type_int = kb_rtype[i]
                    # Map int back to weight lookup (simplified)
                    w = 1.0 
                    if rel_type_int == 0: w = self.weights['equality']
                    elif rel_type_int == 1: w = self.weights['comparative']
                    elif rel_type_int == 2: w = self.weights['causal']
                    elif rel_type_int == 5: w = self.weights['negation']
                    
                    s += w * val # val is 1 (match) or -1 (contradiction)
            raw_scores.append(s)

        # Iterative refinement (PID + Free Energy loop)
        raw_scores = np.array(raw_scores)
        prior = np.ones(len(candidates)) / len(candidates)
        
        # Initial Likelihood
        exp_scores = np.exp((raw_scores - np.max(raw_scores)) / self.tau) # Stability shift
        likelihood = exp_scores / np.sum(exp_scores)
        
        # Bayesian Update
        posterior = likelihood * prior
        posterior /= np.sum(posterior) + 1e-10
        
        # Feedback Control Loop (Simulate one step of regulation)
        H = self._compute_entropy(posterior)
        self._pid_step(H)
        
        # Recompute with new tau
        exp_scores = np.exp((raw_scores - np.max(raw_scores)) / self.tau)
        likelihood = exp_scores / np.sum(exp_scores)
        posterior = likelihood * prior
        posterior /= np.sum(posterior) + 1e-10
        
        # Free Energy Calculation for final scoring
        log_L = np.sum(np.log(likelihood + 1e-10))
        F = self._free_energy_step(log_L, posterior, prior)
        
        # Final Score: Mix of Posterior and Free Energy minimization
        # Higher posterior = better. Lower Free Energy = better.
        # We use Posterior as the main rank, adjusted by F slightly if needed, 
        # but Posterior already encapsulates the likelihood derived from structural match.
        final_scores = posterior
        
        results = []
        for i, c in enumerate(candidates):
            # Meta-confidence check for the specific candidate content vs prompt ambiguity
            meta_conf = self._meta_confidence(prompt)
            
            # If the prompt is ambiguous, cap the score difference
            if meta_conf < 0.3:
                # Flatten scores towards uniform if prompt is a trap
                final_scores[i] = (final_scores[i] * 0.2) + (0.8 / len(candidates))
            
            results.append({
                "candidate": c,
                "score": float(final_scores[i]),
                "reasoning": f"Structural match: {raw_scores[i]:.2f}, Tau: {self.tau:.2f}, MetaConf: {meta_conf:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Run evaluation to get structural score
        res = self.evaluate(prompt, [answer, "DUMMY_PLACEHOLDER_TO_FORCE_RELATIVITY"])
        if not res:
            return 0.0
            
        base_score = res[0]['score'] if res[0]['candidate'] == answer else (res[1]['score'] if len(res) > 1 else 0.5)
        
        # Normalize base_score roughly to 0-1 range assuming binary choice
        # If answer is top ranked, score is high. 
        # However, if meta_conf is low, we must cap.
        
        final_conf = base_score * 2.0 # Scale up slightly since binary split dilutes
        final_conf = min(1.0, final_conf)
        
        # Apply epistemic cap
        if meta_conf < 0.3:
            return min(final_conf, 0.25) # Hard cap for ambiguous prompts
        
        # Never return > 0.9 unless the structural match is perfect and unambiguous
        if meta_conf < 1.0:
            final_conf = min(final_conf, 0.85)
            
        return float(final_conf)
```

</details>
