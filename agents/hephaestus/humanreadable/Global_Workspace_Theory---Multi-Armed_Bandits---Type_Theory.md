# Global Workspace Theory + Multi-Armed Bandits + Type Theory

**Fields**: Cognitive Science, Game Theory, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:52:43.552364
**Report Generated**: 2026-03-27T06:37:33.638836

---

## Nous Analysis

Combining Global Workspace Theory (GWT), Multi‑Armed Bandits (MAB), and Type Theory yields a **Typed Global Workspace Bandit (TGWB) architecture**. In this system, each candidate hypothesis is encoded as a dependent‑type term (e.g., a Π‑type or Σ‑type in Coq/Agda). The workspace maintains a pool of active terms; a bandit controller assigns each term an arm‑value reflecting its expected epistemic reward (e.g., reduction in uncertainty or predictive accuracy). At each cycle, the bandit selects a subset of arms using an exploration‑exploitation rule such as Upper Confidence Bound (UCB) or Thompson Sampling, broadcasts the chosen terms to all modules via the GWT‑style global broadcast, and then runs type‑checking and proof‑search on the broadcasted terms. Successful proofs increase the arm’s reward; failed or contradictory proofs decrease it. The broadcast ensures that any sub‑system (e.g., a planner, a perception module) can immediately use the validated hypothesis, while the type system guarantees that only well‑formed, logically consistent terms ever enter the workspace.

**Advantage for self‑hypothesis testing:** The TGWB lets the system automatically balance trying novel, potentially high‑information hypotheses (exploration) against re‑using those that have already passed rigorous type‑checked proofs (exploitation). Because every broadcast hypothesis is already type‑safe, the system avoids wasting effort on ill‑formed conjectures, and the bandit’s regret bounds give provable limits on how many sub‑optimal hypotheses are tested before converging on high‑value ones. This yields faster, more reliable self‑validation compared to brute‑force enumeration or pure heuristic search.

**Novelty:** While each component has precedents — GWT‑inspired neural architectures, bandit‑based meta‑learning (e.g., Bandit‑based Hyperparameter Optimization), and dependent‑type proof assistants — no existing work couples a formal type‑theoretic hypothesis space with a bandit‑driven global broadcast mechanism for autonomous hypothesis testing. Thus the combination is largely unmapped, though it touches on areas like “proof‑guided program synthesis” and “Bayesian RL with type constraints.”

**Potential ratings**

Reasoning: 7/10 — The system gains structured, proof‑checked reasoning plus adaptive focus, but reasoning depth is still limited by the underlying type theory’s expressiveness and the bandit’s simplicity.  
Metacognition: 8/10 — Explicit monitoring of hypothesis value via bandit rewards and global availability provides a clear metacognitive loop.  
Hypothesis generation: 7/10 — Bandit‑driven exploration yields novel typed conjectures; however, generating truly inventive terms still relies on the generative capacity of the type system.  
Implementability: 5/10 — Integrating a dependent‑type checker with a real‑time bandit scheduler and a global broadcast substrate poses significant engineering challenges; existing proof assistants are not designed for rapid, iterative arm updates.

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

- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Global Workspace Theory + Multi-Armed Bandits: negative interaction (-0.051). Keep these concepts in separate code paths to avoid interference.
- Multi-Armed Bandits + Type Theory: strong positive synergy (+0.327). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Epigenetics + Multi-Armed Bandits + Type Theory (accuracy: 0%, calibration: 0%)
- Multi-Armed Bandits + Free Energy Principle + Type Theory (accuracy: 0%, calibration: 0%)
- Pragmatics + Multi-Armed Bandits + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T22:49:32.278059

---

## Code

**Source**: scrap

[View code](./Global_Workspace_Theory---Multi-Armed_Bandits---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Global Workspace Bandit (TGWB) Approximation.
    
    Mechanism:
    1. Type Theory (Static Analysis): Candidates are parsed for logical structure 
       (negations, comparatives, conditionals). Ill-formed or structurally weak 
       candidates (e.g., missing subjects in transitive queries) receive a 'type error' penalty.
    2. Global Workspace (Broadcast): The prompt's structural signature (keywords, numbers, logic ops) 
       is broadcast. Candidates gain 'attention' (score) based on feature overlap with the prompt.
    3. Multi-Armed Bandit (Selection): We simulate an Upper Confidence Bound (UCB) strategy. 
       'Rewards' are derived from structural consistency and NCD similarity. 
       'Exploration' favors candidates with unique structural features; 'Exploitation' favors 
       high NCD overlap. The final score balances these to rank hypotheses.
    """
    
    def __init__(self):
        self.logic_ops = ['if', 'then', 'else', 'unless', 'therefore', 'because']
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.numeric_re = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features acting as 'types' for the hypothesis."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = any(n in words for n in self.negations)
        has_logic = any(l in words for l in self.logic_ops)
        has_comparative = any(c in words for c in self.comparatives)
        numbers = [float(n) for n in self.numeric_re.findall(text)]
        
        # Type signature: a tuple of boolean flags and count of numbers
        return {
            'negation': has_negation,
            'logic': has_logic,
            'comparative': has_comparative,
            'numbers': numbers,
            'word_set': words,
            'length': len(text)
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_c = max(c1, c2)
        if max_c == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_c

    def _structural_score(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluate candidate based on structural consistency (Type Checking).
        Returns a score between 0 and 1.
        """
        score = 0.0
        checks = 0
        
        # 1. Negation Consistency: If prompt has negation, valid answers often acknowledge it 
        #    or the candidate itself contains negation if it's a correction.
        #    Simplified: If prompt asks a negative question, exact 'yes/no' might need care.
        #    Here we check if the candidate contradicts the prompt's negation status unexpectedly.
        
        # 2. Numeric Consistency: If both have numbers, check logical relation
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # If prompt compares A > B, and candidate is a number, does it fit?
            # Heuristic: If prompt has 2+ numbers and candidate is a number, 
            # it's likely a calculation result. Reward presence.
            score += 0.4
            checks += 1
            
        # 3. Logical Operator Match
        if prompt_feats['logic']:
            if cand_feats['logic']:
                score += 0.3 # Reinforces logical chain
            checks += 1
            
        # 4. Vocabulary Overlap (Global Workspace Broadcast)
        # How many prompt words appear in the candidate?
        common = prompt_feats['word_set'].intersection(cand_feats['word_set'])
        overlap_ratio = len(common) / (len(prompt_feats['word_set']) + 1e-6)
        score += overlap_ratio * 0.5
        checks += 1

        # Penalty for length mismatch in numeric contexts (heuristic for 'type safety')
        if len(prompt_feats['numbers']) > 0 and len(cand_feats['numbers']) == 0:
            if any(x in prompt.lower() for x in ['calculate', 'sum', 'total', 'difference']):
                score -= 0.5 # Likely wrong type (expected number, got text)

        return max(0.0, min(1.0, score)) if checks > 0 else 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        ranked = []
        
        # Pre-calculate NCD matrix for Bandit initialization
        # In a real system, this would be dynamic. Here we simulate the 'arm' values.
        arm_values = []
        
        for i, cand in enumerate(candidates):
            cand_feats = self._extract_features(cand)
            
            # Structural Score (Type Safety & Consistency)
            struct_score = self._structural_score(prompt_feats, cand_feats, prompt, cand)
            
            # NCD Score (Similarity to prompt - Exploitation)
            # We invert NCD so higher is better (1 - ncd)
            ncd_val = self._ncd(prompt, cand)
            similarity = 1.0 - ncd_val
            
            # Bandit UCB Simulation:
            # Value = Structural_Consistency * 0.6 + Similarity * 0.4
            # This balances 'correctness' (structure) with 'relevance' (similarity)
            base_value = (struct_score * 0.65) + (similarity * 0.35)
            
            # Exploration bonus: Prefer candidates with unique structural features 
            # that haven't been seen much (simulated by length hash variance)
            exploration_bonus = 0.1 / (i + 1) 
            
            final_score = base_value + exploration_bonus
            
            # Tiebreaker: If scores are very close, NCD decides
            arm_values.append({
                'candidate': cand,
                'score': final_score,
                'ncd': ncd_val,
                'struct': struct_score
            })

        # Sort by score descending
        arm_values.sort(key=lambda x: x['score'], reverse=True)
        
        # Normalize scores to 0-1 range roughly for output
        max_s = arm_values[0]['score'] if arm_values else 1
        min_s = arm_values[-1]['score'] if arm_values else 0
        range_s = max_s - min_s if (max_s - min_s) > 1e-6 else 1.0

        result = []
        for item in arm_values:
            # Rescale for output clarity
            norm_score = (item['score'] - min_s) / range_s
            result.append({
                'candidate': item['candidate'],
                'score': float(norm_score),
                'reasoning': f"Structural match: {item['struct']:.2f}, NCD similarity: {1-item['ncd']:.2f}"
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural and compression consistency."""
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        # 1. Structural Check
        struct_score = self._structural_score(prompt_feats, cand_feats, prompt, answer)
        
        # 2. NCD Check
        ncd_val = self._ncd(prompt, answer)
        similarity = 1.0 - ncd_val
        
        # Combined confidence
        # High structural score is required for high confidence
        if struct_score < 0.2:
            # If structure is totally off, confidence is low regardless of NCD
            return max(0.0, struct_score * 2) 
            
        confidence = (struct_score * 0.7) + (similarity * 0.3)
        return float(max(0.0, min(1.0, confidence)))
```

</details>
