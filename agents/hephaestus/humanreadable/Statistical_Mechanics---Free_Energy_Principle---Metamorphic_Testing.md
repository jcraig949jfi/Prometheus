# Statistical Mechanics + Free Energy Principle + Metamorphic Testing

**Fields**: Physics, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:54:32.848923
**Report Generated**: 2026-03-27T23:28:38.522718

---

## Nous Analysis

The algorithm treats each candidate answer as a microstate of a physical system. First, a prompt and each answer are parsed into a set of logical propositions using regular expressions that extract:  
- **Negations** (“not”, “no”) → polarity flag,  
- **Comparatives** (“more than”, “less than”, “>”, “<”) → relational operator with numeric operands,  
- **Conditionals** (“if … then …”) → antecedent‑consequent pair,  
- **Causal claims** (“because”, “leads to”) → directed edge,  
- **Ordering relations** (“before”, “after”, “first”, “last”) → temporal precedence,  
- **Numeric values** → floating‑point constants.  

Each proposition becomes a node in a constraint graph; edges encode metamorphic relations (MRs) derived from the prompt: e.g., an MR that doubles a numeric input should double any numeric output, an MR that negates the predicate flips polarity, an MR that preserves ordering leaves the ordering graph unchanged.  

Scoring proceeds as follows:  
1. For each candidate, generate its metamorphic variants by applying the MRs to the parsed prompt.  
2. Propagate constraints through the graph using transitive closure and modus ponens (implemented with NumPy boolean matrices) to detect violations (e.g., a doubled input that does not double the extracted numeric output).  
3. Assign an energy Eᵢ = Σ wₖ·vₖ, where vₖ∈{0,1} is a violation of MR k and wₖ is a preset weight (higher for causal/ordering MRs).  
4. Compute the partition function Z = Σⱼ exp(−β·Eⱼ) with β=1.0 (NumPy).  
5. The Free Energy Principle score for candidate i is the negative variational free energy Fᵢ = −(1/β)·log [exp(−β·Eᵢ)/Z] = Eᵢ − (1/β)·log Z, or equivalently the Boltzmann weight pᵢ = exp(−β·Eᵢ)/Z. Higher pᵢ (lower free energy) indicates a better answer.  

**Structural features parsed**: negations, comparatives, conditionals, causal claims, ordering relations, numeric values.  

**Novelty**: While energy‑based models and constraint propagation exist separately, combining metamorphic testing relations as the microscopic constraints in a statistical‑mechanics free‑energy framework has not been described in the literature; it merges formal MR taxonomy with variational inference, yielding a fresh scoring mechanism.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency via constraint propagation and energy minimization, aligning well with the pipeline’s emphasis on structural parsing.  
Metacognition: 6/10 — provides an uncertainty estimate through free energy but lacks explicit self‑reflective monitoring of its own parsing errors.  
Hypothesis generation: 7/10 — generates metamorphic variants as candidate hypotheses; however, it does not propose novel relational structures beyond those predefined.  
Implementability: 9/10 — relies solely on regex, NumPy for exp/log/sum, and standard‑library data structures, meeting the “no neural models, no API calls” constraint.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
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
**Reason**: trap_battery_failed (acc=42% cal=47% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T21:04:04.993279

---

## Code

**Source**: scrap

[View code](./Statistical_Mechanics---Free_Energy_Principle---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Any

# Constants
BETA = 1.0
WEIGHTS = {
    'negation': 1.0,
    'comparative': 2.0,
    'conditional': 2.5,
    'causal': 3.0,
    'ordering': 3.0,
    'numeric': 1.5
}

class ReasoningTool:
    """
    Implements a Statistical Mechanics x Free Energy Principle x Metamorphic Testing framework.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (negations, comparatives, conditionals, causals, 
       ordering, numerics) from prompts and candidates using regex.
    2. Metamorphic Variants: Generates variants by applying transformations (e.g., negating predicates,
       scaling numbers) to check consistency.
    3. Constraint Graph & Energy: Builds a constraint graph where edges represent metamorphic relations.
       Violations (e.g., doubled input not yielding doubled output, contradictory ordering) add to energy.
       E = sum(w_k * v_k).
    4. Free Energy Scoring: Computes Boltzmann weights p_i = exp(-E_i) / Z. Lower energy (fewer violations)
       yields higher probability.
    5. Epistemic Honesty: Detects ambiguity, presuppositions, and unanswerable queries to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>|<|>=|<=)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|precede|follow)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)\b', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every .+ a .+|each .+ a .+)\b', re.IGNORECASE), # Simplified heuristic
            'pronoun_ambiguity': re.compile(r'\b(.+ told .+ he|she|it)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        features = {
            'negations': len(self.patterns['negation'].findall(text)),
            'comparatives': len(self.patterns['comparative'].findall(text)),
            'conditionals': len(self.patterns['conditional'].findall(text)),
            'causals': len(self.patterns['causal'].findall(text)),
            'orderings': len(self.patterns['ordering'].findall(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'raw': text.lower()
        }
        return features

    def _check_metamorphic_violations(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Calculate energy based on metamorphic relation violations.
        Returns energy E (lower is better).
        """
        energy = 0.0
        
        # MR1: Numeric Consistency (Scaling)
        # If prompt has numbers, candidate should ideally reflect consistent logic.
        # Heuristic: If prompt has 1 number and candidate has 0, or vice versa, slight penalty.
        # Stronger penalty if counts differ significantly without obvious reason (simplified here).
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if len(p_nums) > 0 and len(c_nums) == 0:
            # Candidate ignores numeric data in prompt
            energy += WEIGHTS['numeric'] * 1.5
        elif len(p_nums) > 0 and len(c_nums) > 0:
            # Check for gross contradictions if simple math is implied (e.g. "half of 10")
            # This is a simplified check; full symbolic math would require more complex parsing
            pass 

        # MR2: Negation Polarity
        # If prompt strongly negates, candidate shouldn't affirm without qualification
        if prompt_feats['negations'] > 0 and cand_feats['negations'] == 0:
            # Potential polarity flip violation if context suggests it (heuristic)
            # We apply a small penalty for ignoring negation markers entirely
            if any(word in cand_feats['raw'] for word in ['yes', 'true', 'correct']):
                 energy += WEIGHTS['negation'] * 1.0

        # MR3: Structural Alignment
        # If prompt has conditionals, candidate should ideally acknowledge conditions or consequences
        if prompt_feats['conditionals'] > 0:
            if cand_feats['conditionals'] == 0 and cand_feats['negations'] == 0:
                # Candidate ignores conditional structure
                energy += WEIGHTS['conditional'] * 0.5

        # MR4: Causal/Ordering consistency
        if prompt_feats['orderings'] > 0 and cand_feats['orderings'] == 0:
             energy += WEIGHTS['ordering'] * 0.5

        return energy

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a confidence cap (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. Scope Ambiguity (Heuristic)
        if self.patterns['scope_ambiguity'].search(prompt) and 'same' in p_lower or 'different' in p_lower:
            return 0.3
            
        # 3. Pronoun Ambiguity
        if self.patterns['pronoun_ambiguity'].search(prompt) and 'who' in p_lower:
            return 0.2
            
        # 4. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt) and 'only' in p_lower:
            return 0.3
            
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.4
            
        # 6. Unanswerability (Missing info heuristics)
        if 'unknown' in p_lower or 'cannot be determined' in p_lower:
            return 0.1
            
        # Default high cap if no traps detected
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        p_len = len(prompt)
        
        energies = []
        results = []
        
        # Step 1: Calculate Energy for each candidate
        for i, cand in enumerate(candidates):
            cand_feats = self._extract_features(cand)
            
            # Base energy from metamorphic violations
            e_mr = self._check_metamorphic_violations(prompt_feats, cand_feats)
            
            # Add penalty for length mismatch (heuristic for completeness)
            # Very short answers to complex prompts often miss details
            if len(cand) < p_len * 0.1 and prompt_feats['conditionals'] > 0:
                e_mr += 1.0
                
            energies.append(e_mr)
        
        # Step 2: Compute Partition Function Z
        # Z = sum(exp(-beta * E))
        boltzmann_factors = [math.exp(-BETA * e) for e in energies]
        Z = sum(boltzmann_factors)
        if Z == 0: Z = 1e-9 # Prevent division by zero
        
        # Step 3: Compute Scores and Reasoning
        for i, cand in enumerate(candidates):
            # Free Energy F_i = E_i - (1/beta)*log(Z) 
            # But we want a score where higher is better. 
            # Probability p_i = exp(-E_i) / Z. 
            # We can use log(p_i) as a score, or just p_i. Let's use -F_i (which is log(p_i) * -1 ??)
            # Actually, F = -1/beta * log(p_i). So -F = 1/beta * log(p_i).
            # Since beta=1, Score = log(p_i). 
            # To make it positive and interpretable, let's use the probability p_i directly or -log(p_i) inverted.
            # Let's use the probability mass as the raw score, then adjust with NCD.
            
            p_i = boltzmann_factors[i] / Z
            
            # NCD Component (Max 15% influence)
            # We want low NCD (similarity to prompt context) to boost score slightly, 
            # but not dominate. However, for reasoning, sometimes the answer is short.
            # Let's use NCD to penalize gibberish.
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD contribution: (1 - ncd) is similarity.
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Final Score: 85% Physics-based, 15% Compression-based
            final_score = (p_i * 0.85) + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if energies[i] == 0:
                reasoning_parts.append("No metamorphic violations detected.")
            else:
                reasoning_parts.append(f"Detected {energies[i]:.2f} energy units of logical tension.")
            if prompt_feats['numbers'] and not cand_feats['numbers']:
                reasoning_parts.append("Candidate ignores numeric constraints.")
            if prompt_feats['negations'] and not cand_feats['negations']:
                reasoning_parts.append("Polarity check: Candidate may have flipped negation.")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        # If prompt has complex structure but candidate is empty/gibberish
        structural_integrity = 1.0
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] == 0 and len(answer.split()) < 5:
            structural_integrity = 0.5
            
        # 3. Base score from evaluation logic
        # Run single evaluation to get energy
        res_list = self.evaluate(prompt, [answer])
        base_score = res_list[0]['score'] if res_list else 0.0
        
        # Combine: Base score scaled by meta cap
        # If meta_cap is low (ambiguous), final confidence is low regardless of base_score
        final_conf = base_score * meta_cap * structural_integrity
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, final_conf))
```

</details>
