# Bayesian Inference + Wavelet Transforms + Free Energy Principle

**Fields**: Mathematics, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T12:29:27.875605
**Report Generated**: 2026-04-02T10:55:58.004212

---

## Nous Analysis

**Algorithm – Wavelet‑Guided Bayesian Belief Propagation with Free‑Energy Scoring**  
1. **Parsing & proposition extraction** – Using a small set of regex patterns we pull out atomic propositions (e.g., “X > Y”, “if A then B”, “not C”) and attach to each a token‑position list `pos[p]` (the indices of sentences where the proposition appears).  
2. **Evidence signal construction** – For every proposition `p` we build a binary time‑series `e_p[t]` of length `T` (number of sentences) where `e_p[t]=1` if `p` occurs in sentence `t`, else `0`.  
3. **Wavelet transform** – Apply an orthogonal Haar wavelet transform (implemented with numpy’s `np.kron` and cumulative sums) to obtain coefficients `w_p = WT(e_p)`. The detail coefficients at scale `s` capture localized bursts of evidence; we keep the absolute sum `|w_p|_1` as a scalar evidence strength `E_p`.  
4. **Bayesian belief update** – Treat each proposition as a Bernoulli variable with a Beta prior `Beta(α0,β0)`. The likelihood is modeled as `Bernoulli(σ(E_p))` where `σ` is a logistic squashing of the evidence strength into `[0,1]`. Because Beta is conjugate to Bernoulli, the posterior after seeing the evidence is `Beta(α0 + k_p, β0 + n_p - k_p)` where `k_p = round(E_p)` and `n_p = T`.  
5. **Free‑energy computation** – The variational free energy for proposition `p` is  
   `F_p = KL[Beta(α_post,β_post) ‖ Beta(α0,β0)] - E[log likelihood]`  
   which reduces (using numpy’s `betaln`) to a closed‑form expression. Lower `F_p` means the proposition is better explained by the evidence.  
6. **Constraint propagation** – Rules extracted from regex (e.g., “if A then B” → `A ⇒ B`) are stored as a directed graph. We iteratively apply modus ponens: if the posterior mean of `A` exceeds a threshold `τ`, we add its mean to the belief of `B` (simple additive update). After convergence we recompute free energy for all nodes.  
7. **Answer scoring** – For each candidate answer we compute the average free energy of the propositions it entails (after propagation). The score is `-mean(F)`; higher scores indicate answers that are more probable and less surprising given the text.

**Structural features parsed** – Negations (`not`), comparatives (`>`, `<`, `>=`, `<=`), conditionals (`if … then …`), causal verbs (`cause`, `lead to`), numeric values (detected with `\d+(\.\d+)?`), and ordering relations (`first`, `last`, `before`, `after`). These are turned into the propositions and rule edges above.

**Novelty** – Bayesian belief networks have been used for QA, wavelets for text denoising, and the free‑energy principle for cognitive modeling, but the tight coupling of a wavelet‑derived evidence likelihood with conjugate Bayesian updates and free‑energy‑based scoring in a single, numpy‑only pipeline has not been reported in the literature.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on simple heuristic thresholds.  
Metacognition: 6/10 — free‑energy term offers a rudimentary surprise monitor, yet no explicit self‑reflection on confidence.  
Hypothesis generation: 5/10 — generates new beliefs via rule chaining, but does not propose novel hypotheses beyond those implied by the text.  
Implementability: 8/10 — all steps use regex, numpy vector ops, and standard library; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:forbidden_import: scipy

**Forge Timestamp**: 2026-04-02T10:24:36.781338

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Wavelet_Transforms---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import scipy
from typing import Dict, Tuple

import re
import zlib
import numpy as np
from scipy.special import betaln
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Guided Bayesian Belief Propagation with Free-Energy Scoring.
    
    Extracts propositions from text, builds evidence signals via wavelet transforms,
    performs conjugate Bayesian updates, propagates constraints via logical rules,
    and scores answers by variational free energy (lower = less surprising).
    """
    
    def __init__(self):
        self.alpha0 = 1.0  # Beta prior
        self.beta0 = 1.0
        self.threshold = 0.6  # Belief propagation threshold
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Meta-confidence check first
        meta_conf = self._meta_confidence(prompt)
        
        # Parse text into sentences
        sentences = self._split_sentences(prompt)
        T = len(sentences)
        
        # Extract propositions and build evidence signals
        props = self._extract_propositions(sentences)
        
        # Wavelet transform and evidence strength
        evidence = {}
        for p, positions in props.items():
            e_p = np.zeros(max(T, 4))  # Pad for wavelet
            for pos in positions:
                if pos < len(e_p):
                    e_p[pos] = 1.0
            w_p = self._haar_wavelet(e_p)
            evidence[p] = np.sum(np.abs(w_p))
        
        # Bayesian belief update
        beliefs = {}
        for p, E_p in evidence.items():
            k_p = min(int(E_p), T)
            alpha_post = self.alpha0 + k_p
            beta_post = self.beta0 + (T - k_p)
            beliefs[p] = (alpha_post, beta_post)
        
        # Extract rules and propagate
        rules = self._extract_rules(sentences)
        beliefs = self._propagate(beliefs, rules)
        
        # Compute free energy for each proposition
        free_energies = {}
        for p, (alpha_post, beta_post) in beliefs.items():
            F_p = self._free_energy(alpha_post, beta_post, self.alpha0, self.beta0)
            free_energies[p] = F_p
        
        # Score candidates
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(cand, free_energies, props, prompt, meta_conf)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence caps output
        meta_conf = self._meta_confidence(prompt)
        
        # Structural match confidence
        struct_conf = self._structural_confidence(prompt, answer)
        
        # Combine with cap from meta-analysis
        return min(meta_conf, struct_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, false dichotomy."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did \w+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either|or)\b.*\?', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and not re.search(r'\b(because|since|based on)\b', p_lower):
            return 0.3
        
        # Unanswerable: "what color" but no color mentioned
        if 'what color' in p_lower or 'which color' in p_lower:
            if not re.search(r'\b(red|blue|green|yellow|black|white|orange|purple|pink|brown)\b', p_lower):
                return 0.2
        
        return 0.95  # Default: question seems answerable
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        """Compute confidence based on structural matches."""
        # Numeric comparison
        if self._has_numeric_comparison(prompt):
            return 0.85
        
        # Boolean logic
        if re.search(r'\b(if|then|not|and|or|implies)\b', prompt.lower()):
            return 0.75
        
        # Comparatives
        if re.search(r'\b(greater|less|more|fewer|larger|smaller)\b', prompt.lower()):
            return 0.7
        
        # Default uncertainty
        return 0.5
    
    def _split_sentences(self, text: str) -> List[str]:
        return re.split(r'[.!?]+', text)
    
    def _extract_propositions(self, sentences: List[str]) -> Dict[str, List[int]]:
        """Extract atomic propositions with positions."""
        props = {}
        
        for i, sent in enumerate(sentences):
            s = sent.strip().lower()
            if not s:
                continue
            
            # Comparatives
            for match in re.finditer(r'(\w+)\s*(>|<|>=|<=|==)\s*(\w+)', s):
                p = f"{match.group(1)}{match.group(2)}{match.group(3)}"
                props.setdefault(p, []).append(i)
            
            # Negations
            for match in re.finditer(r'not\s+(\w+)', s):
                p = f"not_{match.group(1)}"
                props.setdefault(p, []).append(i)
            
            # Simple facts (subject-verb-object)
            words = s.split()
            if len(words) >= 2:
                p = "_".join(words[:2])
                props.setdefault(p, []).append(i)
        
        return props
    
    def _extract_rules(self, sentences: List[str]) -> List[Tuple[str, str]]:
        """Extract conditional rules."""
        rules = []
        
        for sent in sentences:
            s = sent.strip().lower()
            
            # If-then patterns
            match = re.search(r'if\s+(\w+).*then\s+(\w+)', s)
            if match:
                rules.append((match.group(1), match.group(2)))
            
            # Causal patterns
            match = re.search(r'(\w+)\s+(cause|lead to)\s+(\w+)', s)
            if match:
                rules.append((match.group(1), match.group(3)))
        
        return rules
    
    def _haar_wavelet(self, signal: np.ndarray) -> np.ndarray:
        """Simple Haar wavelet transform."""
        n = len(signal)
        if n < 2:
            return signal
        
        # Pad to power of 2
        n_pad = 2 ** int(np.ceil(np.log2(n)))
        s = np.pad(signal, (0, n_pad - n), mode='constant')
        
        coeffs = []
        while len(s) > 1:
            detail = (s[::2] - s[1::2]) / np.sqrt(2)
            approx = (s[::2] + s[1::2]) / np.sqrt(2)
            coeffs.append(detail)
            s = approx
        
        coeffs.append(s)
        return np.concatenate(coeffs)
    
    def _free_energy(self, alpha_post, beta_post, alpha_prior, beta_prior) -> float:
        """Variational free energy = KL divergence - expected log likelihood."""
        # KL[Beta(post) || Beta(prior)]
        kl = (betaln(alpha_prior, beta_prior) - betaln(alpha_post, beta_post) +
              (alpha_post - alpha_prior) * (np.digamma(alpha_post) - np.digamma(alpha_post + beta_post)) +
              (beta_post - beta_prior) * (np.digamma(beta_post) - np.digamma(alpha_post + beta_post)))
        
        # Expected log likelihood (approximation)
        mean_post = alpha_post / (alpha_post + beta_post)
        log_lik = mean_post * np.log(mean_post + 1e-9) + (1 - mean_post) * np.log(1 - mean_post + 1e-9)
        
        return kl - log_lik
    
    def _propagate(self, beliefs: Dict, rules: List[Tuple[str, str]]) -> Dict:
        """Propagate beliefs via modus ponens."""
        for _ in range(3):  # Max iterations
            for (antecedent, consequent) in rules:
                if antecedent in beliefs:
                    alpha_a, beta_a = beliefs[antecedent]
                    mean_a = alpha_a / (alpha_a + beta_a)
                    
                    if mean_a > self.threshold:
                        if consequent in beliefs:
                            alpha_c, beta_c = beliefs[consequent]
                            beliefs[consequent] = (alpha_c + mean_a, beta_c)
                        else:
                            beliefs[consequent] = (self.alpha0 + mean_a, self.beta0)
        
        return beliefs
    
    def _score_candidate(self, cand: str, free_energies: Dict, props: Dict, prompt: str, meta_conf: float) -> Tuple[float, str]:
        """Score candidate by average free energy of its propositions."""
        cand_lower = cand.lower()
        
        # Structural scoring (50%)
        struct_score = 0.0
        
        # Numeric comparison
        num_score = self._numeric_match(prompt, cand)
        struct_score += num_score * 0.3
        
        # Proposition overlap
        relevant_props = [p for p in props if any(word in p for word in cand_lower.split())]
        if relevant_props:
            avg_fe = np.mean([free_energies.get(p, 5.0) for p in relevant_props])
            struct_score += (1.0 / (1.0 + avg_fe)) * 0.2
        
        # Boolean logic match
        if self._boolean_match(prompt, cand):
            struct_score += 0.2
        
        # NCD tiebreaker (15%)
        ncd = self._ncd(prompt, cand)
        ncd_score = 1.0 - ncd
        
        # Combine
        final_score = struct_score * 0.7 + ncd_score * 0.15
        
        # Cap by meta-confidence
        final_score *= meta_conf
        
        reasoning = f"struct={struct_score:.2f}, ncd={ncd_score:.2f}, meta={meta_conf:.2f}"
        return final_score, reasoning
    
    def _numeric_match(self, prompt: str, cand: str) -> float:
        """Check numeric comparisons."""
        nums_p = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', prompt)]
        nums_c = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', cand)]
        
        if len(nums_p) >= 2:
            if 'greater' in prompt.lower() or '>' in prompt:
                if len(nums_c) > 0 and nums_c[0] == max(nums_p):
                    return 1.0
            elif 'less' in prompt.lower() or '<' in prompt:
                if len(nums_c) > 0 and nums_c[0] == min(nums_p):
                    return 1.0
        
        return 0.0
    
    def _boolean_match(self, prompt: str, cand: str) -> bool:
        """Simple boolean logic check."""
        if 'not' in prompt.lower() and 'not' in cand.lower():
            return True
        return False
    
    def _has_numeric_comparison(self, text: str) -> bool:
        nums = list(re.finditer(r'\d+\.?\d*', text))
        comparatives = re.search(r'\b(greater|less|more|fewer|>|<)\b', text.lower())
        return len(nums) >= 2 and comparatives is not None
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
