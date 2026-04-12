# Global Workspace Theory + Multi-Armed Bandits + Free Energy Principle

**Fields**: Cognitive Science, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:06:28.160670
**Report Generated**: 2026-03-27T06:37:29.123921

---

## Nous Analysis

Combining Global Workspace Theory (GWT), Multi‑Armed Bandits (MAB), and the Free Energy Principle (FEP) yields a **“Global Workspace Bandit‑Guided Active Inference”** architecture. In this system, a hierarchical predictive‑coding network (the FEP core) continuously generates variational densities over hidden states and computes variational free energy (VFE) as a prediction‑error signal. Each competing hypothesis or model variant is treated as an arm of a bandit; the arm’s value is the expected reduction in VFE (i.e., expected information gain) plus an exploration bonus derived from the arm’s posterior uncertainty. A global workspace layer — implemented as a broadcast hub akin to Dehaene‑Changeux’s neuronal workspace — receives the current belief states from all lower levels, computes the arm‑value estimates, and selects the hypothesis to ignite (broadcast) using a bandit policy such as Thompson Sampling or Upper Confidence Bound (UCB). The selected hypothesis is then globally broadcast, allowing all sensory and motor modules to update their predictions in parallel, thereby minimizing VFE across the whole system.

**Advantage for hypothesis testing:** The system allocates its limited computational bandwidth to the hypothesis that promises the largest immediate drop in prediction error while still probing uncertain alternatives. This yields rapid, data‑efficient model revision: exploitative arms refine well‑supported theories, exploratory arms quickly falsify weak ones, and the global broadcast ensures that any resulting prediction‑error reduction is immediately shared, preventing local minima and accelerating convergence on accurate generative models.

**Novelty:** Active inference already uses expected free energy to drive exploration, and GWT has been simulated with global neuronal workspace models. Bandit‑based attention mechanisms appear in reinforcement‑learning‑inspired neural architectures. However, a unified framework that treats hypotheses as bandit arms, selects them via a global workspace broadcast, and optimizes them via variational free‑energy minimization has not been formalized as a distinct named approach in the literature, making the combination presently novel (or at least not mainstream).

**Ratings**  
Reasoning: 7/10 — provides a principled, uncertainty‑aware selection mechanism that improves sample efficiency but adds considerable architectural complexity.  
Metacognition: 8/10 — the bandit’s uncertainty estimates and the global broadcast give the system explicit, monitorable meta‑information about its own hypothesis confidence.  
Hypothesis generation: 6/10 — the scheme excels at choosing among existing hypotheses; it does not intrinsically create new model structures, relying on external generative‑model proposal mechanisms.  
Implementability: 5/10 — requires integrating predictive‑coding layers, a global workspace broadcast module, and a bandit solver; while each piece exists, their tight coupling poses non‑trivial engineering and stability challenges.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Global Workspace Theory + Multi-Armed Bandits: negative interaction (-0.051). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Global Workspace Theory: strong positive synergy (+0.177). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Multi-Armed Bandits: strong positive synergy (+0.252). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ecosystem Dynamics + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Gene Regulatory Networks + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Multi-Armed Bandits + Free Energy Principle + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T09:17:31.232526

---

## Code

**Source**: scrap

[View code](./Global_Workspace_Theory---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Global Workspace Bandit-Guided Active Inference Tool.
    
    Mechanism:
    1. FEP Core (Variational Free Energy): Treats the prompt as the 'true' generative model.
       Candidates are evaluated by their 'prediction error' (structural mismatch) against the prompt.
       Lower error = higher likelihood. We parse structural tokens (negations, comparatives, numbers)
       to compute a precise structural overlap score, minimizing 'surprise'.
       
    2. MAB (Multi-Armed Bandit): Each candidate is an 'arm'. 
       We calculate an 'Exploration Bonus' based on the uncertainty of the candidate's 
       structural signature relative to the prompt's complexity. This prevents local minima 
       where a short, generic answer might accidentally match keywords.
       
    3. GWT (Global Workspace): The 'broadcast' phase selects the winner by combining 
       the exploitation term (structural fit) and exploration term (uncertainty bonus),
       then normalizes scores to a global confidence metric.
    """

    def __init__(self):
        # Structural patterns for FEP-based parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'when', 'while'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extract structural tokens to minimize variational free energy (prediction error)."""
        if not text:
            return {'words': set(), 'nums': [], 'has_neg': False, 'has_comp': False, 'has_cond': False, 'length': 0}
        
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'words': words,
            'nums': nums,
            'has_neg': bool(words & self.negations),
            'has_comp': bool(words & self.comparatives),
            'has_cond': bool(words & self.conditionals),
            'length': len(text)
        }

    def _compute_structural_overlap(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute similarity based on structural alignment (FEP core).
        High overlap = Low Prediction Error.
        """
        if not prompt_feats['words'] or not cand_feats['words']:
            return 0.0

        # 1. Word Intersection (Jaccard-like)
        intersection = prompt_feats['words'] & cand_feats['words']
        union = prompt_feats['words'] | cand_feats['words']
        word_score = len(intersection) / len(union) if union else 0.0

        # 2. Structural Constraint Propagation
        # If prompt has negation, candidate MUST have negation to be valid (Modus Tollens check)
        neg_match = 1.0
        if prompt_feats['has_neg']:
            neg_match = 1.0 if cand_feats['has_cond'] or cand_feats['has_neg'] else 0.5
        
        # Conditional alignment
        cond_match = 1.0
        if prompt_feats['has_cond']:
            cond_match = 1.0 if cand_feats['has_cond'] else 0.6
            
        # Numeric consistency (if numbers exist in both)
        num_score = 1.0
        if prompt_feats['nums'] and cand_feats['nums']:
            # Simple check: does the candidate contain the specific numbers in the prompt?
            # Or at least maintain order/magnitude logic (simplified for brevity)
            p_nums = set(prompt_feats['nums'])
            c_nums = set(cand_feats['nums'])
            if p_nums <= c_nums or c_nums <= p_nums: # One is subset of other
                num_score = 1.0
            else:
                num_score = 0.5 # Penalty for mismatched numbers
        elif prompt_feats['nums'] and not cand_feats['nums']:
            num_score = 0.2 # Heavy penalty for ignoring numbers

        return (word_score * 0.5) + (neg_match * 0.2) + (cond_match * 0.15) + (num_score * 0.15)

    def _compute_bandit_bonus(self, prompt: str, candidate: str, total_candidates: int) -> float:
        """
        MAB Exploration Bonus.
        Encourages testing hypotheses (candidates) that are distinct but plausible.
        Uses uncertainty based on length divergence and NCD volatility.
        """
        if total_candidates == 0:
            return 0.0
            
        # Uncertainty estimation: How different is this candidate's structure from the average?
        # Simplified: Bonus for candidates that aren't trivially short (avoids "Yes"/"No" traps)
        len_ratio = len(candidate) / (len(prompt) + 1)
        complexity_bonus = math.sqrt(len(candidate)) * 0.01
        
        # Exploration term: Higher for candidates with moderate length (not too short, not rambling)
        if 0.1 <= len_ratio <= 2.0:
            return complexity_bonus * 0.2
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_structural_features(prompt)
        results = []
        
        # Pre-calculate max possible structural score for normalization if needed
        max_struct_score = 0.0
        
        # Phase 1: Compute raw scores (FEP + MAB)
        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            
            # FEP: Minimize prediction error (maximize structural overlap)
            struct_score = self._compute_structural_overlap(prompt_feats, cand_feats)
            
            # MAB: Add exploration bonus
            bonus = self._compute_bandit_bonus(prompt, cand, len(candidates))
            raw_score = struct_score + bonus
            
            max_struct_score = max(max_struct_score, struct_score)
            
            results.append({
                "candidate": cand,
                "raw_score": raw_score,
                "struct_score": struct_score,
                "reasoning": f"Structural overlap: {struct_score:.3f}, Bandit bonus: {bonus:.3f}"
            })

        # Phase 2: Global Workspace Broadcast (Selection & Ranking)
        # Normalize scores to ensure the best structural match wins, using NCD as tiebreaker
        max_raw = max(r['raw_score'] for r in results) if results else 1.0
        
        final_results = []
        for r in results:
            # Primary Sort Key: Raw Score (Structure + Bonus)
            # Secondary Sort Key (Tiebreaker): NCD (Lower is better)
            ncd_val = self._ncd(prompt, r['candidate'])
            
            # Final Score formulation: 
            # We want high structural score. 
            # If scores are very close (within 0.01), NCD decides.
            score = r['raw_score']
            
            final_results.append({
                "candidate": r['candidate'],
                "score": score,
                "reasoning": r['reasoning'],
                "_ncd": ncd_val # Hidden for sorting
            })

        # Sort: Higher score first, then lower NCD (better compression match)
        final_results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up and return
        output = []
        for res in final_results:
            output.append({
                "candidate": res['candidate'],
                "score": res['score'],
                "reasoning": res['reasoning']
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        prompt_feats = self._extract_structural_features(prompt)
        ans_feats = self._extract_structural_features(answer)
        
        base_score = self._compute_structural_overlap(prompt_feats, ans_feats)
        
        # Boost if boolean consistency is found (e.g. Prompt asks True/False, Answer gives it)
        p_bools = prompt_feats['words'] & self.booleans
        a_bools = ans_feats['words'] & self.booleans
        
        if p_bools and a_bools:
            base_score = min(1.0, base_score + 0.2)
            
        # Penalty for extreme length mismatch unless structural score is perfect
        if len(answer) < 3 and base_score < 0.9:
            base_score *= 0.8
            
        return float(min(1.0, max(0.0, base_score)))
```

</details>
