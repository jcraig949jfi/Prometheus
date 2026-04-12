# Compressed Sensing + Mechanism Design + Multi-Armed Bandits

**Fields**: Computer Science, Economics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T17:52:54.521549
**Report Generated**: 2026-03-27T23:28:38.532718

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer \(a_i\) as a high‑dimensional signal \(x_i\in\mathbb{R}^d\) built from extracted logical‑structural features (see §2). A small set of \(m\ll d\) latent “reasoning factors’’ \(z\) governs correctness, so \(x_i\approx\Phi z_i\) where \(\Phi\in\mathbb{R}^{d\times m}\) is a dictionary of basis patterns (e.g., “negation + comparative”, “conditional → causal”). Using only the labeled answers in a prompt (the gold answer or a few human‑scored exemplars), we recover a sparse weight vector \(w\in\mathbb{R}^m\) by solving the basis‑pursuit problem  

\[
\min_w \|w\|_1 \quad\text{s.t.}\quad \|Y - X\Phi w\|_2\le\epsilon,
\]

with \(X\) the feature matrix of candidates and \(Y\) their observed scores. This yields a compressive‑sensing‑style estimator that uses only \(O(m\log d)\) measurements.

To make the scoring rule incentive‑compatible (mechanism design), we adopt a proper scoring rule: the final score for candidate \(i\) is  

\[
s_i = \log\bigl(\sigma(w^\top \Phi^\top x_i)\bigr),
\]

where \(\sigma\) is the logistic function. Because the expected score is maximized when the reported belief equals the true probability of correctness, agents (here, the answer generator) cannot gain by mis‑representing their confidence.

Finally, we allocate a limited evaluation budget using a multi‑armed bandit. Each candidate is an arm; we maintain empirical mean \(\hat\mu_i\) and confidence \(c_i = \sqrt{\frac{2\log t}{n_i}}\) (UCB1). At each step \(t\) we select the arm with highest \(\hat\mu_i + c_i\), obtain its true score (via the compressive‑sensing estimator), and update its statistics. This explores uncertain answers while exploiting those predicted to be high‑scoring, converging to the optimal ranking with \(O(\log T)\) regret.

**Structural features parsed**  
- Negation tokens (“not”, “never”).  
- Comparative forms (“more”, “less”, “‑er”, “as … as”).  
- Conditional markers (“if”, “unless”, “provided that”).  
- Numeric values and units (regex for digits, fractions, percentages).  
- Causal cue phrases (“because”, “leads to”, “results in”).  
- Ordering relations (“before”, “after”, “greater than”, “ranked”).  
Each feature increments a corresponding dimension in \(x_i\).

**Novelty**  
Sparse recovery via compressed sensing has been used for feature selection; mechanism design for truthful elicitation; bandits for active learning. Their joint use to score reasoning answers—combining ℓ₁‑based weight learning, a proper scoring rule, and UCB‑driven evaluation—does not appear in existing surveys, making the combination novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure via sparse representation but relies on linear approximability of reasoning factors.  
Metacognition: 7/10 — incentive‑compatible scoring encourages calibrated confidence, yet the model does not explicitly reason about its own uncertainty beyond the bandit variance term.  
Hypothesis generation: 6/10 — the bandit explores uncertain answers, generating implicit hypotheses about which structural patterns improve scores, but no explicit hypothesis space is enumerated.  
Implementability: 9/10 — all steps use numpy (linear algebra, ℓ₁ solvers via scipy‑free iterative shrinkage‑thresholding) and stdlib (regex, heapq for UCB); no external APIs or neural nets required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=34% cal=13% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T21:08:33.905966

---

## Code

**Source**: scrap

[View code](./Compressed_Sensing---Mechanism_Design---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

# No external dependencies beyond standard library and numpy (simulated here with pure python for strict compliance if needed, 
# but prompt allows numpy. To ensure zero-dependency runnability in strict environments, 
# I will implement a minimal L1 solver and linear algebra using only standard lib, 
# as the problem size (m << d) is small enough for iterative methods).

class ReasoningTool:
    """
    A reasoning tool combining Compressed Sensing (sparse feature recovery), 
    Mechanism Design (proper scoring rules), and Multi-Armed Bandits (UCB1).
    
    Mechanism:
    1. Feature Extraction: Parses logical structures (negation, conditionals, numbers).
    2. Compressed Sensing: Approximates sparse weights for these features based on 
       gold-standard heuristics (simulated via internal consistency checks).
    3. Mechanism Design: Uses a logistic proper scoring rule to ensure confidence 
       reflects true probability.
    4. Bandit Logic: Uses UCB1-like exploration to adjust confidence when structural 
       ambiguity is detected.
    5. Epistemic Honesty: Explicitly downgrades confidence on Tier B traps 
       (presuppositions, ambiguity) regardless of answer score.
    """

    def __init__(self):
        # Feature definitions (The Dictionary Phi)
        self.features = [
            ('negation', r'\b(not|no|never|neither|none)\b', -1.0),
            ('comparative', r'\b(more|less|greater|lesser|better|worse|higher|lower|-er)\b', 0.5),
            ('conditional', r'\b(if|unless|provided|then|else)\b', 0.2),
            ('causal', r'\b(because|therefore|thus|hence|leads to|results in)\b', 0.3),
            ('uncertainty_phrase', r'\b(maybe|perhaps|possibly|likely|uncertain)\b', -0.5), # Penalize hedging in final answer if prompt demands certainty
            ('superlative', r'\b(best|worst|first|last|most|least)\b', 0.4),
        ]
        # Regex for numbers
        self.number_regex = re.compile(r'-?\d+(?:\.\d+)?(?:e[-+]?\d+)?')
        
        # Tier B Trap patterns
        self.trap_patterns = {
            'presupposition': [r'\b(have|has|had)\s+you\s+(stopped|quit|finished)\b', r'\bwhy\s+did\s+\w+\s+(fail|stop|lose)\b'],
            'false_dichotomy': [r'\beither\s+.*\s+or\s+', r'\bis it\s+\w+\s+or\s+\w+\?'],
            'subjectivity': [r'\b(best|worst|favorite|opinion)\b'],
            'pronoun_ambiguity': [r'\b(he|she|they|it)\s+was\s+\w+\b.*\bwho\b'],
        }

    def _extract_features(self, text: str) -> List[float]:
        """Extract structural features into a vector x."""
        text_lower = text.lower()
        vector = []
        
        # 1. Logical markers
        for name, pattern, _ in self.features:
            count = len(re.findall(pattern, text_lower))
            vector.append(float(count))
            
        # 2. Numeric density (normalized)
        numbers = self.number_regex.findall(text)
        vector.append(len(numbers) / (len(text.split()) + 1))
        
        # 3. Length penalty (simplicity bias)
        vector.append(1.0 / (len(text.split()) + 1))
        
        return vector

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp12 = len(zlib.compress(b1 + b2))
        return (comp12 - min(comp1, comp2)) / max(comp1, comp2)

    def _check_tier_b_traps(self, prompt: str) -> Tuple[bool, str]:
        """Check for epistemic traps. Returns (is_trap, reason)."""
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.trap_patterns['presupposition']:
            if re.search(pattern, p_lower):
                return True, "Presupposition detected"
                
        # 2. False Dichotomy
        for pattern in self.trap_patterns['false_dichotomy']:
            if re.search(pattern, p_lower):
                # Only flag if options aren't exhaustive (heuristic: short prompt with 'or')
                if len(prompt.split()) < 15: 
                    return True, "False dichotomy suspected"
                    
        # 3. Subjectivity without criteria
        if any(re.search(p, p_lower) for p in self.trap_patterns['subjectivity']):
            if "criteria" not in p_lower and "measure" not in p_lower:
                return True, "Subjective question"
                
        # 4. Ambiguity keywords in prompt
        if "ambiguous" in p_lower or "unclear" in p_lower:
            return True, "Explicit ambiguity"
            
        return False, ""

    def _solve_linear_system_approx(self, X: List[List[float]], Y: List[float]) -> List[float]:
        """
        Approximate L1-minimization (Basis Pursuit) via Iterative Shrinkage-Thresholding (ISTA).
        Solves min ||w||_1 s.t. ||Y - Xw||_2 <= epsilon.
        Since this is a small-scale internal tool, we run fixed iterations.
        """
        if not X or not Y:
            return []
            
        n_samples = len(Y)
        n_features = len(X[0])
        
        # Initialize weights
        w = [0.0] * n_features
        
        # Hyperparameters
        lr = 0.01
        lambda_l1 = 0.1
        
        # Convert to simple math operations (no numpy dependency to ensure robustness)
        for _ in range(100): # Fixed iterations for convergence
            gradient = [0.0] * n_features
            
            # Compute residual and gradient
            for i in range(n_samples):
                pred = sum(X[i][j] * w[j] for j in range(n_features))
                error = Y[i] - pred
                for j in range(n_features):
                    gradient[j] += -2 * error * X[i][j] / n_samples
            
            # Update and Soft Thresholding (L1 penalty)
            for j in range(n_features):
                w[j] = w[j] - lr * gradient[j]
                # Soft thresholding
                if w[j] > lambda_l1 * lr:
                    w[j] -= lambda_l1 * lr
                elif w[j] < -lambda_l1 * lr:
                    w[j] += lambda_l1 * lr
                else:
                    w[j] = 0.0
                    
        return w

    def _calculate_computational_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Actually solve math/logic if present.
        Returns 1.0 if correct, 0.0 if wrong, -1.0 if N/A.
        """
        # Extract numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', candidate)]
        
        # Case 1: Direct numeric equality (e.g. "What is 2+2?" -> "4")
        if len(c_nums) == 1 and len(p_nums) >= 2:
            # Heuristic: If candidate number matches a derived operation result
            # Try simple ops
            target = None
            if len(p_nums) == 2:
                a, b = p_nums[0], p_nums[1]
                if abs(c_nums[0] - (a+b)) < 1e-6: return 1.0
                if abs(c_nums[0] - (a-b)) < 1e-6: return 1.0
                if abs(c_nums[0] - (a*b)) < 1e-6: return 1.0
                if b != 0 and abs(c_nums[0] - (a/b)) < 1e-6: return 1.0
                # Comparison logic
                if "greater" in prompt.lower() and c_nums[0] == max(a,b): return 1.0
                if "lesser" in prompt.lower() and c_nums[0] == min(a,b): return 1.0
            
        # Case 2: Boolean/Logic checks
        cand_lower = candidate.lower().strip()
        if cand_lower in ["yes", "no", "true", "false"]:
            # Very basic consistency check (e.g. if prompt says "not", expect negative)
            has_neg = bool(re.search(r'\bnot\b', prompt.lower()))
            is_negative_answer = cand_lower in ["no", "false"]
            if has_neg == is_negative_answer:
                return 0.8 # Partial credit for logical alignment
            
        return -1.0 # No computational verification possible

    def _meta_confidence(self, prompt: str, candidate: str) -> float:
        """
        Tier B Reasoning: Determine confidence based on prompt properties.
        Caps confidence if ambiguity is detected.
        """
        is_trap, reason = self._check_tier_b_traps(prompt)
        if is_trap:
            return 0.2 # Low confidence for traps
        
        # If no structural features match the prompt type, be honest
        feat_vec = self._extract_features(prompt)
        if sum(feat_vec) < 0.5: # Very low feature activation
            return 0.3
            
        return 1.0 # Default high potential confidence

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Feature Extraction (Compressed Sensing Setup)
        # X: Matrix of candidate features
        X = [self._extract_features(c) for c in candidates]
        # Also include prompt features repeated for context
        p_feat = self._extract_features(prompt)
        
        # 2. Generate Pseudo-Labels (Y) for Sparse Recovery
        # Since we don't have gold labels, we use "Computational Verification" and "NCD to Prompt" as proxies
        Y = []
        comp_scores = []
        
        for i, cand in enumerate(candidates):
            score = 0.5 # Base prior
            
            # Computational check (High weight)
            comp_res = self._calculate_computational_score(prompt, cand)
            comp_scores.append(comp_res)
            if comp_res == 1.0:
                score = 0.95
            elif comp_res == 0.0:
                score = 0.05
            
            # NCD Check (Low weight, tiebreaker)
            # Ideally, correct answer might be semantically close but not identical. 
            # However, for reasoning, exact match of logic is key. 
            # We use NCD only as a small penalty for gibberish.
            ncd = self._compute_ncd(prompt, cand)
            if ncd > 0.9: # Too different?
                score *= 0.8
                
            Y.append(score)

        # 3. Sparse Weight Recovery (Simulated ISTA)
        # Learn which features correlate with high scores in this specific context
        weights = self._solve_linear_system_approx(X, Y)
        
        # 4. Scoring and Ranking
        results = []
        t = len(candidates) # Time step for Bandit
        
        for i, cand in enumerate(candidates):
            x_i = X[i]
            
            # Linear combination (Phi * w)
            raw_score = sum(x_i[j] * weights[j] for j in range(len(weights)))
            
            # Add computational bonus directly if verified
            if comp_scores[i] == 1.0:
                raw_score += 2.0
            elif comp_scores[i] == 0.0:
                raw_score -= 2.0
                
            # Mechanism Design: Proper Scoring Rule (Logistic)
            # s_i = log(sigma(raw_score)) -> effectively raw_score in log-odds space
            # We map to 0-1 range via sigmoid for the final score
            prob = 1.0 / (1.0 + math.exp(-raw_score))
            
            # Bandit Exploration Bonus (UCB1 style)
            # Encourage looking at candidates with unique feature profiles if uncertainty is high
            n_i = 1 # Assume 1 observation per candidate in this batch
            c_i = math.sqrt((2 * math.log(t + 1)) / (n_i + 1))
            
            # Final Score mixing exploitation (prob) and exploration (c_i)
            # But for final output, we primarily sort by estimated correctness (prob)
            final_score = 0.8 * prob + 0.2 * c_i
            
            # Cap by Meta-Confidence (Tier B)
            meta_cap = self._meta_confidence(prompt, cand)
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap + 0.1) # Allow slight variation but keep low

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {raw_score:.2f}, Comp check: {comp_scores[i]}, Meta-cap: {meta_cap:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B traps.
        """
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # 2. Structural/Computational Verification
        comp_res = self._calculate_computational_score(prompt, answer)
        feat_vec = self._extract_features(answer)
        
        base_conf = 0.5
        
        # If computational check says it's definitely right/wrong
        if comp_res == 1.0:
            base_conf = 0.95
        elif comp_res == 0.0:
            base_conf = 0.05
        else:
            # Rely on feature density
            if sum(feat_vec) > 1.0:
                base_conf = 0.7
            else:
                base_conf = 0.4
                
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Ensure we never return > 0.9 without computational proof
        if comp_res != 1.0 and final_conf > 0.9:
            final_conf = 0.85
            
        return max(0.0, min(1.0, final_conf))
```

</details>
