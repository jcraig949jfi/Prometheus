# Genetic Algorithms + Immune Systems + Cognitive Load Theory

**Fields**: Computer Science, Biology, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T00:17:51.878842
**Report Generated**: 2026-03-27T06:37:32.665293

---

## Nous Analysis

Combining the three ideas yields a **Cognitive‑Load‑Regulated Clonal Selection Algorithm (CL‑CSA)**. A population of candidate hypotheses is treated as an antibody repertoire. Each hypothesis receives a fitness score based on how well it predicts observed data (affinity). High‑affinity hypotheses undergo clonal expansion; the number of clones is inversely proportional to an estimated intrinsic cognitive load — when the system’s working memory is already taxed, fewer clones are made to avoid overload. Somatic hypermutation rates are modulated by extraneous load: high extraneous load (irrelevant noise) triggers higher mutation to explore alternatives, whereas low extraneous load preserves promising patterns. Germane load guides crossover: when load estimates indicate capacity for meaningful recombination, pairs of high‑affinity hypotheses undergo crossover to build schemata that integrate useful features (chunking). Memory cells store the best‑affinity hypotheses for rapid recall, providing a self/non‑self discriminative filter that rejects hypotheses conflicting with established background knowledge (self). The algorithm thus continuously self‑tunes its exploration‑exploitation balance according to the learner’s current cognitive load.

**Advantage for hypothesis testing:** The system can test many hypotheses without exceeding its working‑memory limits, automatically shifting from broad search (high mutation) when load is low to focused refinement (high selection, low mutation) when load is high. This reduces wasted computation, mitigates overfitting, and yields faster convergence to robust hypotheses.

**Novelty:** Artificial Immune Systems (AIS) and Genetic Algorithms have been fused before (e.g., opt‑aiNET, Clonal Selection Algorithm). Cognitive‑load‑aware evolutionary methods exist but are scarce and usually treat load as a static parameter. Dynamically regulating clonal selection, hypermutation, and crossover based on real‑time intrinsic, extraneous, and germane load estimates is not widely reported, making the combination largely novel.

**Ratings**  
Reasoning: 7/10 — provides adaptive, fitness‑driven hypothesis evaluation but still relies on heuristic load estimation.  
Metacognition: 8/10 — the system monitors and adjusts to its own cognitive load, a clear metacognitive loop.  
Hypothesis generation: 7/10 — immune‑inspired diversity plus load‑regulated crossover yields rich, structured hypothesis pools.  
Implementability: 5/10 — requires real‑time load measurement and integration into an AIS framework, which adds non‑trivial engineering overhead.

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

- **Genetic Algorithms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Immune Systems**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Genetic Algorithms + Immune Systems: negative interaction (-0.064). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Cellular Automata + Cognitive Load Theory + Phenomenology (accuracy: 0%, calibration: 0%)
- Chaos Theory + Cognitive Load Theory + Kalman Filtering (accuracy: 0%, calibration: 0%)
- Chaos Theory + Cognitive Load Theory + Neuromodulation (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T03:59:43.668704

---

## Code

**Source**: scrap

[View code](./Genetic_Algorithms---Immune_Systems---Cognitive_Load_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Cognitive-Load-Regulated Clonal Selection Algorithm (CL-CSA) Implementation.
    
    Mechanism:
    1. Structural Parsing (Antigen Recognition): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values from the prompt and candidates.
    2. Affinity Calculation (Fitness): Scores candidates based on structural alignment 
       with the prompt (e.g., matching negation flips, correct numeric inequality).
    3. Cognitive Load Regulation:
       - Intrinsic Load: Complexity of the prompt's logical structure.
       - Extraneous Load: Noise/length mismatch between prompt and candidate.
       - Germane Load: Capacity for recombination (crossover) of logical features.
    4. Clonal Selection & Hypermutation:
       - High affinity + Low Load -> Clonal Expansion (boost score).
       - High Extraneous Load -> Hypermutation penalty (lower score unless structure matches).
       - Memory Cells: Prioritizes candidates that preserve "self" (prompt constraints).
    5. Scoring: Final score is a weighted sum of structural adherence (primary) and 
       NCD compression (tiebreaker), dynamically adjusted by load estimates.
    """

    def __init__(self):
        self.memory_cells = []  # Stores high-affinity structural patterns

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric signatures from text."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Evaluates numeric logic if numbers are present."""
        if not prompt_nums or not cand_nums:
            return 1.0  # Neutral if no numbers to compare
        
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
            
            # Simple heuristic: If prompt implies order, does candidate follow?
            # Since we don't have full semantic parse, we check magnitude alignment
            # if the candidate repeats numbers with comparative words.
            if len(p_vals) >= 2 and len(c_vals) >= 2:
                # Check if relative order is preserved or logically flipped by negation
                p_diff = p_vals[0] - p_vals[1]
                c_diff = c_vals[0] - c_vals[1]
                if abs(p_diff) > 0 and abs(c_diff) > 0:
                    return 1.0 if (p_diff * c_diff) > 0 else 0.5
            return 1.0
        except ValueError:
            return 1.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        denom = max(len(b1), len(b2))
        if denom == 0: return 1.0
        return (len(b12) - min(len(b1), len(b2))) / denom

    def _estimate_load(self, prompt_feat: dict, cand_feat: dict) -> Tuple[float, float, float]:
        """
        Estimates Cognitive Loads.
        Intrinsic: Complexity of prompt structure.
        Extraneous: Mismatch in length/complexity between prompt and candidate.
        Germane: Potential for meaningful integration (similarity in structure).
        """
        # Intrinsic: Weighted sum of logical operators in prompt
        intrinsic = (prompt_feat['negations'] * 2 + prompt_feat['comparatives'] * 2 + 
                     prompt_feat['conditionals'] * 3) / 10.0
        
        # Extraneous: Deviation in length and feature presence (Noise)
        len_diff = abs(prompt_feat['length'] - cand_feat['length']) / max(prompt_feat['length'], 1)
        feat_mismatch = abs(prompt_feat['negations'] - cand_feat['negations']) * 0.5
        extraneous = min(1.0, len_diff + feat_mismatch)
        
        # Germane: Inverse of extraneous when structural alignment is high
        germane = max(0.0, 1.0 - extraneous - (intrinsic * 0.2))
        
        return intrinsic, extraneous, germane

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt signature for memory
        prompt_sig = (prompt_feat['negations'], prompt_feat['comparatives'], prompt_feat['conditionals'])
        if not self.memory_cells:
            self.memory_cells.append(prompt_sig)

        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            
            # 1. Affinity (Structural Fitness)
            # Check logical consistency (e.g., if prompt has 'not', valid answer might need 'not' or opposite meaning)
            # Heuristic: Candidates mirroring prompt structure get base affinity
            affinity = 0.5
            if prompt_feat['negations'] > 0:
                # If prompt negates, candidate should ideally reflect that or be a direct contradiction check
                affinity += 0.2 if cand_feat['negations'] > 0 else 0.0
            else:
                affinity += 0.2 if cand_feat['negations'] == 0 else -0.2
            
            if prompt_feat['comparatives'] > 0:
                affinity += 0.2 if cand_feat['comparatives'] > 0 else 0.0
            
            # Numeric consistency boost
            num_score = self._check_numeric_consistency(prompt_feat['numbers'], cand_feat['numbers'])
            affinity *= num_score

            # 2. Cognitive Load Regulation
            intrinsic, extraneous, germane = self._estimate_load(prompt_feat, cand_feat)
            
            # Clonal Expansion Factor (Inverse to Intrinsic Load to prevent overload)
            # If intrinsic load is high, we penalize complex candidates unless affinity is very high
            expansion_factor = 1.0 / (1.0 + intrinsic) if intrinsic > 0 else 1.0
            
            # Hypermutation Penalty (Driven by Extraneous Load)
            # High noise (extraneous) suggests we should explore, but for scoring, 
            # high extraneous load usually means the candidate is "noisy" or irrelevant -> Lower score
            mutation_penalty = extraneous * 0.3
            
            # Germane Load Bonus (Crossover/Chunking)
            # If germane load is high, we reward the integration of features
            germane_bonus = germane * 0.2
            
            # Final Score Calculation
            base_score = affinity * expansion_factor
            final_score = base_score + germane_bonus - mutation_penalty
            
            # NCD Tiebreaker (Only if structural signals are weak)
            if abs(affinity - 0.5) < 0.1: 
                ncd = self._calculate_ncd(prompt, cand)
                final_score -= (ncd * 0.1) # Prefer lower NCD (higher similarity) slightly

            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, final_score)), # Clamp 0-1
                "reasoning": f"Affinity:{affinity:.2f}, Load(Int:{intrinsic:.2f}, Ext:{extraneous:.2f}, Ger:{germane:.2f})"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0
```

</details>
