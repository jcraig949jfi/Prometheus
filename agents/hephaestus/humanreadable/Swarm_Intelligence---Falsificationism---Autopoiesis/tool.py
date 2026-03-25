import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Producing Falsification Swarm (SFS) Implementation.
    
    Mechanism:
    1. Swarm Intelligence: The 'candidates' act as a swarm of agents exploring the hypothesis space.
    2. Falsificationism: Each candidate is subjected to rigorous 'falsification probes' based on logical
       constraints extracted from the prompt (negations, comparatives, conditionals). Failures leave
       a strong negative trace (high penalty).
    3. Autopoiesis: Candidates that survive falsification undergo 'self-maintenance'. Their score is
       reinforced by their structural coherence (compression distance to the prompt's core constraints),
       ensuring the system maintains a coherent theory rather than drifting.
       
    This approach prioritizes logical constraint satisfaction (Falsification) while using 
    information density (NCD) as a secondary stigmergic signal for coherence.
    """

    def __init__(self):
        pass

    def _extract_constraints(self, prompt: str) -> List[Dict]:
        """Extract logical probes (negations, comparatives) from the prompt."""
        constraints = []
        p_lower = prompt.lower()
        
        # Probe 1: Negation detection (Modus Tollens proxy)
        # If prompt says "X is not Y", candidate claiming "X is Y" is falsified.
        neg_patterns = [
            (r"not\s+(\w+)", "not_{}"),
            (r"never\s+(\w+)", "not_{}"),
            (r"without\s+(\w+)", "not_{}")
        ]
        for pattern, fmt in neg_patterns:
            matches = re.findall(pattern, p_lower)
            for match in matches:
                constraints.append({"type": "negation", "target": match.lower(), "fmt": fmt})

        # Probe 2: Comparatives (Numeric or Lexical)
        if "greater than" in p_lower or "more than" in p_lower:
            constraints.append({"type": "comparative", "op": "gt"})
        if "less than" in p_lower or "fewer than" in p_lower:
            constraints.append({"type": "comparative", "op": "lt"})
            
        # Probe 3: Conditionals
        if "if" in p_lower and ("then" in p_lower or "?" in p_lower):
            constraints.append({"type": "conditional", "active": True})

        return constraints

    def _run_falsification_probe(self, candidate: str, prompt: str, constraints: List[Dict]) -> float:
        """
        Run falsification probes. Returns a penalty score (0.0 = passed, >0.0 = failed).
        High penalty indicates the hypothesis (candidate) is falsified by the environment (prompt).
        """
        penalty = 0.0
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        for const in constraints:
            if const["type"] == "negation":
                # If the prompt forbids a concept, and the candidate asserts it strongly
                target = const["target"]
                if target in c_lower and target not in p_lower.split(): # Simple heuristic
                    # Check if candidate is affirming the negated concept without negation context
                    if f"not {target}" not in c_lower and f"never {target}" not in c_lower:
                        penalty += 0.5
            
            if const["type"] == "comparative":
                # Extract numbers if present for numeric falsification
                nums_c = re.findall(r"[-+]?\d*\.?\d+", c_lower)
                nums_p = re.findall(r"[-+]?\d*\.?\d+", p_lower)
                
                if len(nums_c) > 0 and len(nums_p) > 0:
                    try:
                        val_c = float(nums_c[-1])
                        val_p = float(nums_p[-1]) # Reference value
                        
                        if const["op"] == "gt" and val_c <= val_p:
                            penalty += 0.4 # Falsified: should be greater
                        elif const["op"] == "lt" and val_c >= val_p:
                            penalty += 0.4 # Falsified: should be less
                    except ValueError:
                        pass
        
        # Stigmergic trace: If candidate length is suspiciously short (e.g., "Yes"/"No") 
        # in a complex prompt, add slight penalty unless constraints are sparse.
        if len(constraints) > 1 and len(candidate.split()) < 3:
            penalty += 0.1
            
        return min(penalty, 1.0)

    def _compute_autopoietic_coherence(self, candidate: str, prompt: str) -> float:
        """
        Compute self-maintenance score via Normalized Compression Distance (NCD).
        Lower NCD means the candidate is structurally coherent with the prompt's information content.
        Returns a coherence score between 0 (incoherent) and 1 (highly coherent).
        """
        def zlib_len(s):
            return len(zlib.compress(s.encode('utf-8')))

        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        
        try:
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            
            # NCD formula
            ncd = (c12 - min(c1, c2)) / max(c1, c2, 1)
            # Convert to coherence (1 - ncd), clamped
            coherence = max(0.0, 1.0 - ncd)
            return coherence
        except Exception:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        constraints = self._extract_constraints(prompt)
        
        # If no specific constraints found, rely heavily on coherence (NCD)
        # If constraints exist, Falsification is the primary driver.
        
        for cand in candidates:
            # 1. Falsification Phase (Popperian Probe)
            falsification_penalty = self._run_falsification_probe(cand, prompt, constraints)
            
            # 2. Autopoiesis Phase (Self-maintenance/Coherence)
            coherence = self._compute_autopoietic_coherence(cand, prompt)
            
            # 3. Swarm Scoring
            # Base score from coherence (structural integrity)
            base_score = coherence
            
            # Apply falsification penalty (drastic reduction if falsified)
            # If penalty is high, the hypothesis is discarded regardless of coherence
            if falsification_penalty > 0.3:
                final_score = base_score * (1.0 - falsification_penalty) * 0.5
            else:
                # Minor penalties just reduce confidence slightly
                final_score = base_score * (1.0 - (falsification_penalty * 0.2))
            
            # Boost for satisfying complex constraints explicitly
            if len(constraints) > 0 and falsification_penalty == 0.0:
                final_score = min(1.0, final_score + 0.15)

            results.append({
                "candidate": cand,
                "score": float(f"{final_score:.6f}"),
                "reasoning": f"Falsification Penalty: {falsification_penalty:.2f}, Coherence: {coherence:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation logic."""
        # Evaluate single candidate against itself to get relative score
        # We simulate a small candidate set to get a normalized view if needed, 
        # but direct scoring is faster and deterministic.
        
        constraints = self._extract_constraints(prompt)
        penalty = self._run_falsification_probe(answer, prompt, constraints)
        coherence = self._compute_autopoietic_coherence(answer, prompt)
        
        if penalty > 0.3:
            conf = coherence * (1.0 - penalty) * 0.5
        else:
            conf = coherence * (1.0 - (penalty * 0.2))
            
        if len(constraints) > 0 and penalty == 0.0:
            conf = min(1.0, conf + 0.15)
            
        return float(f"{max(0.0, min(1.0, conf)):.6f}")