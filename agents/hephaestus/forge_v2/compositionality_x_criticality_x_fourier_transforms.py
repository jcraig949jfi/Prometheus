import numpy as np
import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Critical Spectral Compositional Architecture (CSCA) v2.

    Intersection:
    1. Compositionality: Text decomposed into syntactic primitives (negation, numeric,
       conditional, comparative, subject-object) that compose into a structured score.
    2. Criticality: Susceptibility metric from spectral mode variance amplifies small
       mismatches near critical thresholds, acting as gradient-free error signal.
    3. Fourier Transforms: Character-level DFT produces spectral representation;
       power spectrum analysis detects structural periodicity and frequency-domain
       similarity between prompt and candidate.
    """

    def __init__(self):
        self.basis_size = 64
        self.negations = ['not', 'no', 'never', 'neither', 'cannot', "won't", "isn't", "doesn't", "don't"]
        self.comparatives = {'greater': 1, 'more': 1, 'larger': 1, 'higher': 1, 'above': 1,
                             'less': -1, 'fewer': -1, 'smaller': -1, 'lower': -1, 'below': -1}

    def _parse_numbers(self, text: str) -> List[float]:
        return [float(m) for m in re.findall(r'-?\d+\.?\d*', text)]

    def _negation_scopes(self, text: str) -> List[str]:
        words = text.lower().split()
        scopes = []
        for i, w in enumerate(words):
            if w in self.negations and i + 1 < len(words):
                scopes.append(' '.join(words[i + 1:min(i + 4, len(words))]))
        return scopes

    def _extract_conditional(self, text: str):
        m = re.search(r'\bif\b(.+?)\bthen\b(.+?)(?:\.|,|$)', text.lower())
        return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)

    def _dft_spectrum(self, text: str) -> np.ndarray:
        if not text:
            return np.zeros(self.basis_size)
        signal = np.array([ord(c) / 256.0 for c in text[:512]])
        if len(signal) < self.basis_size:
            signal = np.pad(signal, (0, self.basis_size - len(signal)))
        elif len(signal) > self.basis_size:
            signal = signal[:self.basis_size]
        spectrum = np.fft.rfft(signal)
        power = np.abs(spectrum)
        norm = np.linalg.norm(power)
        return power / (norm + 1e-9)

    def _spectral_similarity(self, s1: np.ndarray, s2: np.ndarray) -> float:
        dot = float(np.dot(s1, s2))
        n1, n2 = float(np.linalg.norm(s1)), float(np.linalg.norm(s2))
        if n1 < 1e-9 or n2 < 1e-9:
            return 0.0
        return dot / (n1 * n2)

    def _susceptibility(self, spectrum: np.ndarray) -> float:
        return float(np.var(spectrum)) + 1e-9

    def _power_spectrum_distance(self, s1: np.ndarray, s2: np.ndarray) -> float:
        return float(np.sqrt(np.sum((s1 - s2) ** 2)))

    def _compositional_score(self, prompt: str, candidate: str) -> tuple:
        reasons = []
        penalty = 0.0
        bonus = 0.0
        p_low, c_low = prompt.lower(), candidate.lower()
        # Negation scope
        p_negs = self._negation_scopes(prompt)
        c_negs = self._negation_scopes(candidate)
        for scope in p_negs:
            if scope in c_low and not any(scope in cn for cn in c_negs):
                penalty += 0.35
                reasons.append(f"structural:negation_violation('{scope}')")
        # "not all X" vs "all not X" distinction
        if 'not all' in p_low:
            if 'all not' in c_low or ('all ' in c_low and 'not' not in c_low):
                penalty += 0.2
                reasons.append("structural:quantifier_negation_scope_error(not_all != all_not)")
        # Numeric consistency
        p_nums = self._parse_numbers(prompt)
        c_nums = self._parse_numbers(candidate)
        if p_nums and c_nums:
            direction = sum(self.comparatives.get(w, 0) for w in p_low.split())
            if direction > 0 and c_nums[0] < p_nums[0]:
                penalty += 0.3
                reasons.append(f"execution:numeric_order_fail(expected>{p_nums[0]},got={c_nums[0]})")
            elif direction < 0 and c_nums[0] > p_nums[0]:
                penalty += 0.3
                reasons.append(f"execution:numeric_order_fail(expected<{p_nums[0]},got={c_nums[0]})")
            if len(p_nums) >= 3 and len(c_nums) >= 3:
                if (sorted(p_nums) == sorted(sorted(p_nums))) != (sorted(c_nums) == sorted(sorted(c_nums))):
                    penalty += 0.15; reasons.append("execution:transitivity_violation")
            if p_nums and c_nums and abs(p_nums[0] - c_nums[0]) < 0.01:
                bonus += 0.1
                reasons.append(f"execution:numeric_match({c_nums[0]})")
        # Conditional (modus ponens / tollens)
        ante, cons = self._extract_conditional(prompt)
        if ante and cons:
            if ante in c_low and cons not in c_low:
                penalty += 0.3
                reasons.append(f"structural:modus_ponens_fail('{ante}'->'{cons}')")
            if ('not ' + cons) in c_low and ante in c_low:
                penalty += 0.3
                reasons.append("structural:modus_tollens_contradiction")
            if ante in c_low and cons in c_low:
                bonus += 0.1
                reasons.append("structural:conditional_satisfied")
        svo = re.search(r'(\w+)\s+(gave|sent|told|showed|built|did)\s+(\w+)\s+to\s+(\w+)', p_low)
        if svo:
            subj, verb = svo.group(1), svo.group(2)
            if subj in c_low: bonus += 0.05
            c_svo = re.search(r'(\w+)\s+' + re.escape(verb) + r'\s+(\w+)\s+to\s+(\w+)', c_low)
            if c_svo and c_svo.group(1) != subj:
                penalty += 0.2; reasons.append(f"structural:agent_swap({subj}->{c_svo.group(1)})")
        # Contradiction pairs
        contras = [('impossible', 'possible'), ('false', 'true'), ('never', 'always')]
        for neg, pos in contras:
            if neg in p_low and pos in c_low and neg not in c_low:
                penalty += 0.25
                reasons.append(f"structural:contradiction({neg}/{pos})")
        net = bonus - penalty
        return net, reasons

    def _ncd(self, s1: str, s2: str) -> float:
        z = zlib.compress
        l1, l2 = len(z(s1.encode())), len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        return (l12 - min(l1, l2)) / max(l1, l2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        candidates = [c if c else "" for c in candidates]
        p_spec = self._dft_spectrum(prompt)
        p_sus = self._susceptibility(p_spec)
        results = []
        for cand in candidates:
            if not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"})
                continue
            reasons = []
            c_spec = self._dft_spectrum(cand)
            spec_sim = self._spectral_similarity(p_spec, c_spec)
            reasons.append(f"execution:spectral_sim={spec_sim:.3f}")
            c_sus = self._susceptibility(c_spec)
            sus_gap = abs(p_sus - c_sus)
            if sus_gap > 0.01:
                reasons.append(f"execution:criticality_gap={sus_gap:.4f}")
            comp_net, comp_reasons = self._compositional_score(prompt, cand)
            reasons.extend(comp_reasons)
            ncd_val = 1.0 - self._ncd(prompt, cand)
            ncd_weight = 0.10
            has_structural = bool(comp_reasons)
            if not has_structural and spec_sim < 0.3:
                ncd_weight = 0.15
                reasons.append("fallback:ncd")
            crit_amplifier = 1.0 + min(sus_gap * 10, 0.5)
            structural_part = max(0.0, min(1.0, 0.5 + comp_net))
            score = (0.30 * spec_sim + 0.45 * structural_part + ncd_weight * ncd_val)
            score -= 0.10 * sus_gap * crit_amplifier
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(reasons)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]:
                r["reasoning"] += "; structural:low_confidence_margin(<5%)"
        # Metacognitive reflection
        if results and results[0]["score"] > 0:
            top = results[0]
            _, recheck = self._compositional_score(prompt, top["candidate"])
            violations = [r for r in recheck if 'violation' in r or 'contradiction' in r or 'fail' in r]
            if violations:
                top["reasoning"] += f"; reflection:top_has_issues({len(violations)} flags)"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer:
            return 0.0
        _, comp_reasons = self._compositional_score(prompt, answer)
        violations = [r for r in comp_reasons if 'violation' in r or 'contradiction' in r or 'fail' in r]
        if len(violations) >= 2:
            return max(0.0, 0.05)
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = np.mean(null_scores) if null_scores else 0.5
        if null_mean >= ans_score:
            return max(0.0, 0.1 * ans_score)
        separation = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        spec_sim = self._spectral_similarity(self._dft_spectrum(prompt), self._dft_spectrum(answer))
        conf = 0.25 * ans_score + 0.50 * separation + 0.25 * spec_sim
        return float(max(0.0, min(1.0, conf)))
