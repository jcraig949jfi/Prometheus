# Embodied Cognition + Hebbian Learning + Neuromodulation

**Fields**: Cognitive Science, Neuroscience, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:44:53.754962
**Report Generated**: 2026-03-27T17:21:23.810572

---

## Nous Analysis

Combining embodied cognition, Hebbian learning, and neuromodulation yields a **Neuromodulated Embodied Hebbian Predictive Coding (NEHPC)** architecture. In NEHPC, a hierarchical predictive‑coding network processes multimodal sensorimotor streams from an embodied agent (e.g., a simulated robot with proprioception, vision, and touch). Each layer learns via spike‑timing‑dependent plasticity (STDP) that is **gated by neuromodulatory signals**: dopamine encodes prediction‑error‑based reward and strengthens synapses when the agent’s prediction matches sensory feedback (confirming a hypothesis); serotonin adjusts the gain of error units, biasing the network toward exploration versus exploitation; acetylcholine modulates the precision of sensory inputs, allowing the agent to re‑weight affordances based on bodily state. The Hebbian updates are thus **state‑dependent**, wiring together neurons that fire together only when the body‑environment context signals relevance via neuromodulators.

For a reasoning system testing its own hypotheses, NEHPC provides an intrinsic metacognitive loop: when a hypothesis (top‑down prediction) is violated, the resulting prediction error drives dopaminergic teaching signals that weaken the synapses supporting that hypothesis, while correct predictions reinforce them. Simultaneously, serotonin‑mediated gain control shifts the system into a hypothesis‑generation mode when confidence is low, prompting the agent to sample novel actions that generate fresh sensorimotor data. This tight coupling of action, perception, and synaptic plasticity lets the system **self‑evaluate** hypotheses without external labels, using its own embodied experience as the ground truth.

The combination is **partially novel**. Dopamine‑modulated STDP and neuromodulatory gating of Hebbian plasticity appear in reinforcement‑learning models (e.g., ReSuME, DOPAMINE‑STDP), and predictive coding with embodied agents has been explored (e.g., active inference models). However, few works explicitly integrate all three — embodied affordance grounding, bidirectional Hebbian plasticity, and multiple neuromodulators — into a single unified architecture for hypothesis testing, making NEHPC a relatively underexplored niche.

**Ratings**

Reasoning: 7/10 — The architecture yields concrete, biologically plausible mechanisms for context‑sensitive inference, though scalability to high‑dimensional reasoning remains unproven.  
Metacognition: 8/10 — Dopamine‑driven error signaling and serotonin‑gain modulation give the system explicit confidence‑like signals that directly modulate hypothesis strength.  
Hypothesis generation: 7/10 — Neuromodulatory shifts between exploitation and exploration promote adaptive generation of alternatives grounded in sensorimotor affordances.  
Implementability: 5/10 — Requires spiking or deep‑predictive‑coding implementations with multi‑timescale neuromodulatory dynamics, which are still challenging to engineer robustly in hardware or large‑scale simulations.

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

- **Embodied Cognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Embodied Cognition + Hebbian Learning + Neuromodulation (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Category Theory + Embodied Cognition + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Forged (passed trap battery)

| Metric | Score | vs NCD Baseline |
|--------|-------|-----------------|
| Accuracy | 27% | +7% |
| Calibration | 20% | +13% |

**Forge Timestamp**: 2026-03-27T04:39:57.875573

---

## Code

**Source**: forge

[View code](./Embodied_Cognition---Hebbian_Learning---Neuromodulation/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Embodied Hebbian Predictive Coding (NEHPC) Approximation.
    
    Mechanism:
    1. Embodied Cognition (Structural Grounding): Parses the prompt for logical 
       structures (negations, comparatives, conditionals) to form a 'sensory' 
       representation of constraints.
    2. Hebbian Learning (Association): Strengthens candidates that share 
       structural tokens (keywords, logic operators) with the prompt. 
       "Neurons firing together" = shared logical tokens.
    3. Neuromodulation (Gating & Confidence):
       - Dopamine (Reward): Boosts score if candidate matches prompt structure.
       - Serotonin (Exploration): If confidence is low (high uncertainty), 
         penalize extreme scores slightly to allow alternative ranking.
       - Acetylcholine (Precision): Weighs specific logical operators higher 
         than generic words.
    
    This creates a self-evaluating loop where the "body" (parser) validates 
    the hypothesis (candidate) against sensory input (prompt structure).
    """

    def __init__(self):
        # Logical operators act as high-precision sensory inputs (Acetylcholine)
        self.logic_ops = {'not', 'no', 'never', 'if', 'then', 'else', 'unless', 
                          'greater', 'less', 'more', 'fewer', 'equal', 'true', 'false'}
        self.comparators = {'>', '<', '>=', '<=', '==', '!='}
        
    def _extract_structure(self, text: str) -> Tuple[set, float, bool]:
        """Extract logical tokens, numeric values, and negation state."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Identify logical operators (High precision weights)
        logic_tokens = words.intersection(self.logic_ops)
        
        # Detect negation scope (Simple heuristic: presence of negation words)
        has_negation = bool(words.intersection({'no', 'not', 'never', 'neither', 'nobody'}))
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"-?\d+\.?\d*", lower_text)
        numeric_val = None
        if numbers:
            try:
                # Take the last number as the primary value for comparison contexts
                numeric_val = float(numbers[-1])
            except ValueError:
                pass
                
        return logic_tokens, numeric_val, has_negation

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
        
        # NCD formula
        ncd = (comp12 - min(comp1, comp2)) / max(comp1, comp2)
        return max(0.0, min(1.0, ncd))

    def _hebbian_update(self, prompt_tokens: set, cand_tokens: set, 
                        prompt_logic: set, has_negation: bool) -> float:
        """
        Simulates Hebbian learning: Strengthens connections between 
        co-occurring logical structures.
        """
        if not prompt_tokens:
            return 0.0
            
        # Base overlap (standard association)
        intersection = prompt_tokens.intersection(cand_tokens)
        base_score = len(intersection) / (len(prompt_tokens) + 1e-6)
        
        # Logic-gated reinforcement (Acetylcholine modulation)
        # If the prompt has logic ops, candidates sharing them get a massive boost
        logic_overlap = 0.0
        if prompt_logic:
            cand_logic = cand_tokens.intersection(self.logic_ops)
            if cand_logic:
                # Stronger weight for logical consistency
                logic_overlap = len(cand_logic) * 0.5
        
        # Negation consistency check
        # If prompt is negative, candidate should ideally reflect that or be evaluated carefully
        negation_bonus = 0.0
        if has_negation:
            cand_has_neg = bool(cand_tokens.intersection({'no', 'not', 'never', 'false'}))
            # In simple reasoning, if prompt negates, correct answer often acknowledges it
            if cand_has_neg:
                negation_bonus = 0.2
        
        return base_score + logic_overlap + negation_bonus

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_tokens = set(re.findall(r'\b\w+\b', prompt.lower()))
        p_logic, p_num, p_neg = self._extract_structure(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_tokens = set(re.findall(r'\b\w+\b', cand.lower()))
            c_logic, c_num, c_neg = self._extract_structure(cand)
            
            # 1. Hebbian Strength (Structural similarity)
            hebbian_score = self._hebbian_update(prompt_tokens, cand_tokens, p_logic, p_neg)
            
            # 2. Numeric Evaluation (Constraint Propagation)
            numeric_bonus = 0.0
            if p_num is not None and c_num is not None:
                # Check for comparative consistency if prompt implies it
                # Simple heuristic: if numbers are close, higher score (approximation)
                if abs(p_num - c_num) < 1e-6:
                    numeric_bonus = 0.3
                elif p_num > c_num and ('less' in prompt.lower() or 'smaller' in prompt.lower()):
                    numeric_bonus = 0.2
                elif p_num < c_num and ('greater' in prompt.lower() or 'larger' in prompt.lower()):
                    numeric_bonus = 0.2
            
            # 3. Neuromodulatory Gating (Dopamine/Serotonin)
            # Dopamine: Reward for structural match
            raw_score = hebbian_score + numeric_bonus
            
            # Serotonin: Exploration bonus for short, distinct answers if confidence is low
            # This prevents getting stuck on long, verbose, but incorrect matches
            exploration_bonus = 0.0
            if raw_score < 0.1 and len(cand_tokens) < 5:
                exploration_bonus = 0.05 # Slight boost to explore short hypotheses
            
            final_score = min(1.0, raw_score + exploration_bonus)
            
            # Reasoning string generation
            reasoning = f"Structural match: {hebbian_score:.2f}"
            if numeric_bonus > 0:
                reasoning += f"; Numeric alignment detected"
            if p_logic and not c_logic:
                reasoning += "; Warning: Missing logical operators"
                
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Fallback to NCD if all structural scores are zero (Tiebreaker)
        if all(c["score"] == 0.0 for c in scored_candidates):
            for i, item in enumerate(scored_candidates):
                ncd = self._compute_ncd(prompt, item["candidate"])
                # Invert NCD so lower distance = higher score
                item["score"] = 1.0 - ncd
                item["reasoning"] = "Fallback to NCD (structural signal weak)"
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        Uses the same NEHPC mechanism to self-evaluate the hypothesis.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        score = results[0]["score"]
        
        # Metacognitive thresholding
        # If the structural match is strong, confidence is high.
        # If it relied on NCD fallback, confidence is capped.
        if "NCD" in results[0]["reasoning"]:
            return max(0.0, min(0.4, score)) # Low confidence if structural parsing failed
        
        return max(0.0, min(1.0, score))
```

</details>
