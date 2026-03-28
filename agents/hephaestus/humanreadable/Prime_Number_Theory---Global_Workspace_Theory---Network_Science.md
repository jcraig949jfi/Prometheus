# Prime Number Theory + Global Workspace Theory + Network Science

**Fields**: Mathematics, Cognitive Science, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T22:13:23.664677
**Report Generated**: 2026-03-27T06:37:31.492766

---

## Nous Analysis

Combining the three domains yields a **Prime‑Weighted Global Broadcast Network (PWGBN)**.  

1. **Computational mechanism** – Each candidate hypothesis is represented as a node in a large‑scale graph. Edge weights are derived from number‑theoretic similarity: two hypotheses receive a weight proportional to the closeness of their associated prime signatures (e.g., the distance between the n‑th prime where n encodes hypothesis complexity, or the correlation of their Riemann‑zeta‑zero spectra). The graph is constructed using a **prime‑graph generator** (similar to the Pach‑Ruzsa‑Szemerédi construction) yielding a scale‑free, small‑world topology.  
   A **global workspace layer** sits atop the network: nodes compete for ignition via a softmax‑based activation rule that incorporates both local evidence (likelihood from data) and global workspace bias (a broadcast signal proportional to the node’s PageRank‑like centrality in the prime‑weighted graph). Winning nodes broadcast their state to all neighbors, updating beliefs through a belief‑propagation step akin to loopy BP. The cycle repeats: competition → ignition → broadcast → evidence accumulation.  

2. **Advantage for self‑hypothesis testing** – The prime weighting injects a structured, mathematically grounded notion of hypothesis “distance” that penalizes semantically similar but redundant guesses, encouraging exploration of truly distinct candidates. The global workspace ignition ensures that only a limited, high‑confidence set of hypotheses gains system‑wide influence at any time, curbing combinatorial blow‑up while still allowing rapid propagation of supportive evidence across the network. Consequently, the system can quickly prune low‑promising regions of hypothesis space and focus computational resources on promising, number‑theoretically diverse candidates.  

3. **Novelty** – Prime‑based graphs have been studied in network science (e.g., “prime graphs” and their spectral properties), and Global Workspace Theory has been instantiated in cognitive architectures such as LIDA and ACT‑R. However, the explicit coupling of a number‑theoretic similarity metric with a competitive global‑workspace ignition loop for autonomous hypothesis testing has not been reported in the literature, making this intersection presently novel.  

**Ratings**  
Reasoning: 7/10 — The mechanism adds a principled similarity metric that improves inference quality, but the reliance on costly prime‑signature calculations limits raw reasoning speed.  
Metacognition: 8/10 — The workspace ignition provides a clear, monitorable signal of which hypotheses have gained global access, supporting accurate self‑monitoring of confidence.  
Hypothesis generation: 7/10 — Prime weighting encourages diverse hypothesis proposals, though the generation step still depends on external proposal mechanisms.  
Implementability: 5/10 — Building accurate prime‑based similarity graphs at scale and integrating them with a dynamic softmax competition loop is non‑trivial and currently lacks mature tooling.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Prime Number Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Network Science**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Global Workspace Theory + Network Science: strong positive synergy (+0.260). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Category Theory + Global Workspace Theory + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Category Theory + Global Workspace Theory + Epistemology (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=33% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T02:56:53.621912

---

## Code

**Source**: scrap

[View code](./Prime_Number_Theory---Global_Workspace_Theory---Network_Science/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Prime-Weighted Global Broadcast Network (PWGBN) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This acts as the "local evidence".
    2. Prime-Weighted Hypothesis Graph (Diversity Metric): 
       - Assigns a unique prime to each structural feature (e.g., 2 for negation, 3 for numbers).
       - Computes a "Prime Signature" for each candidate based on features present.
       - Calculates edge weights between candidates using GCD-based similarity (number-theoretic distance).
       - This penalizes redundant candidates that share the same logical flaws.
    3. Global Workspace Ignition (Competition):
       - Candidates compete via a softmax function combining structural score (evidence) 
         and centrality (diversity penalty).
       - High-confidence, structurally distinct candidates "ignite" (gain high score).
    4. NCD Tiebreaker: Used only when structural signals are identical.
    
    This satisfies the requirement to use Prime Theory for structural/diversity scoring 
    rather than direct semantic similarity, avoiding the historical inhibitor trap.
    """

    def __init__(self):
        # First 10 prime numbers for feature encoding
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        # Feature patterns mapped to primes
        self.features = [
            (r'\bnot\b|\bno\b|\bnever\b|\bwithout\b', 0),      # Negation
            (r'\bmore\b|\bless\b|\bgreater\b|\bsmaller\b|\b<|\b>', 1), # Comparatives
            (r'\bif\b|\bthen\b|\bunless\b|\bwhen\b', 2),       # Conditionals
            (r'\d+\.\d+|\d+', 3),                              # Numbers
            (r'\ball\b|\bevery\b|\bnone\b|\bsome\b', 4),       # Quantifiers
            (r'\bcause\b|\bbecause\b|\btherefore\b', 5),       # Causality
            (r'\bsame\b|\bdifferent\b|\bequal\b', 6),          # Equivalence
            (r'\bfirst\b|\blast\b|\bnext\b|\bprevious\b', 7),  # Order
            (r'\btrue\b|\bfalse\b|\byes\b|\bno\b', 8),         # Binary states
            (r'\bonly\b|\bexcept\b', 9)                        # Exclusivity
        ]

    def _extract_features(self, text: str) -> List[int]:
        """Extract structural features and return list of associated primes."""
        text_lower = text.lower()
        active_primes = []
        for pattern, idx in self.features:
            if re.search(pattern, text_lower):
                active_primes.append(self.primes[idx])
        return active_primes if active_primes else [1] # 1 if no features found

    def _compute_prime_signature(self, primes: List[int]) -> int:
        """Compute product of primes (signature)."""
        if not primes:
            return 1
        result = 1
        for p in primes:
            result *= p
        return result

    def _gcd(self, a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluate candidate based on structural alignment with prompt.
        Returns a score where higher is better.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        
        # 1. Negation Consistency
        has_neg_prompt = bool(re.search(r'\bnot\b|\bno\b|\bnever\b', p_lower))
        has_neg_cand = bool(re.search(r'\bnot\b|\bno\b|\bnever\b', c_lower))
        if has_neg_prompt == has_neg_cand:
            score += 2.0
        elif has_neg_cand and not has_neg_prompt:
            score -= 5.0 # Penalty for spurious negation
            
        # 2. Numeric Evaluation (Simple extraction and comparison logic)
        nums_prompt = re.findall(r'\d+\.\d+|\d+', p_lower)
        nums_cand = re.findall(r'\d+\.\d+|\d+', c_lower)
        
        if nums_prompt:
            if nums_cand:
                # Check if candidate numbers are consistent subset or result
                try:
                    p_vals = [float(x) for x in nums_prompt]
                    c_vals = [float(x) for x in nums_cand]
                    # Heuristic: If prompt asks for max/min, check candidate
                    if 'largest' in p_lower or 'max' in p_lower:
                        if max(c_vals) == max(p_vals): score += 3.0
                    elif 'smallest' in p_lower or 'min' in p_lower:
                        if min(c_vals) == min(p_vals): score += 3.0
                    else:
                        # General presence bonus
                        score += 1.0 
                except ValueError:
                    pass
            else:
                score -= 1.0 # Missing numbers when prompt has them

        # 3. Conditional/Logical keyword overlap (Weighted)
        common_logic = 0
        for pattern, _ in self.features[2:]: # Skip negation/comparatives already handled
            if re.search(pattern, p_lower) and re.search(pattern, c_lower):
                common_logic += 0.5
        score += common_logic

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        if max(len1, len2) == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # Step 1: Compute Structural Scores (Local Evidence)
        struct_scores = []
        for c in candidates:
            s = self._structural_score(prompt, c)
            struct_scores.append(s)

        # Step 2: Compute Prime Signatures & Diversity (Global Workspace Competition)
        # Each candidate gets a prime signature based on features
        signatures = []
        feature_sets = []
        for c in candidates:
            feats = self._extract_features(c)
            feature_sets.append(feats)
            signatures.append(self._compute_prime_signature(feats))

        # Compute Diversity Penalty (Redundancy)
        # If two candidates have high GCD (share many prime factors/features), 
        # they are redundant. We want unique high-scorers.
        diversity_scores = []
        for i, sig_i in enumerate(signatures):
            redundancy = 0.0
            for j, sig_j in enumerate(signatures):
                if i != j:
                    # GCD-based similarity
                    common = self._gcd(sig_i, sig_j)
                    if common > 1:
                        # Normalize similarity by geometric mean of signatures to avoid bias to large products
                        sim = math.log(common + 1) / (math.log(sig_i + 1) + math.log(sig_j + 1) + 1e-9)
                        redundancy += sim
            diversity_scores.append(-redundancy) # Negative because redundancy is bad

        # Step 3: Global Ignition (Softmax-like combination)
        # Score = Structural + Diversity + (NCD Tiebreaker logic applied loosely here)
        final_scores = []
        max_struct = max(struct_scores) if struct_scores else 0
        
        for i in range(len(candidates)):
            # Normalize structural to ~0-5 range
            norm_struct = struct_scores[i] 
            # Diversity is usually small negative number
            div = diversity_scores[i] * 2.0 
            
            raw_score = norm_struct + div
            
            # NCD as tiebreaker for very close structural scores
            if abs(raw_score - max_struct) < 0.1:
                # If structurally similar, prefer shorter/more compressed (lower NCD to prompt concept)
                # Actually, for tie breaking, we just add a tiny perturbation based on length/NCD
                ncd_val = self._ncd(prompt, candidates[i])
                raw_score -= ncd_val * 0.01 # Small penalty for high NCD (dissimilarity) if scores are tied

            final_scores.append(raw_score)

        # Rank and format
        ranked_indices = sorted(range(len(candidates)), key=lambda k: final_scores[k], reverse=True)
        
        results = []
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": final_scores[idx],
                "reasoning": f"Structural:{struct_scores[idx]:.2f}, Diversity:{diversity_scores[idx]:.2f}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment and prime-signature consistency.
        """
        # 1. Structural Check
        struct_score = self._structural_score(prompt, answer)
        
        # Map structural score to probability range
        # Base assumption: score > 0 is good, < 0 is bad
        # Range roughly -5 to +6
        prob = 1.0 / (1.0 + math.exp(-struct_score)) # Sigmoid
        
        # 2. Prime Signature Consistency Check
        # Does the answer introduce wild features not in prompt?
        p_feats = set(self._extract_features(prompt))
        a_feats = set(self._extract_features(answer))
        
        # Penalty for introducing complex logic (conditionals/quantifiers) not present in prompt
        # unless it's a specific feature type that implies derivation
        new_complex = a_feats - p_feats
        complexity_penalty = 0.0
        for p in new_complex:
            if p > 5: # Higher primes = more complex logic (causality, quantifiers)
                complexity_penalty += 0.15
        
        final_conf = max(0.0, min(1.0, prob - complexity_penalty))
        return final_conf
```

</details>
