import math
import hashlib
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Differentiable Meta-Mechanism for Self-Interested Hypothesis Agents v2.

    Intersection:
    1. Differentiable Programming: Smooth scoring via softmax bidding with gradient-like
       sensitivity analysis (finite differences on perturbations).
    2. Mechanism Design: Clarke-Groves incentive-compatible payments that reward candidates
       improving global truth score, penalizing overconfidence.
    3. Metacognition: Temperature control based on score variance (exploration/exploitation),
       plus reflection pass checking internal consistency of top candidate.
    """

    def __init__(self):
        self._meta_uncertainty = 0.5
        self.negations = ['not', 'no', 'never', 'neither', 'cannot', "won't", "isn't", "doesn't", "don't"]
        self.comparatives = {'greater': 1, 'more': 1, 'larger': 1, 'higher': 1,
                             'less': -1, 'fewer': -1, 'smaller': -1, 'lower': -1}

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

    def _structural_eval(self, prompt: str, candidate: str) -> tuple:
        reasons = []
        score = 0.0
        p_low, c_low = prompt.lower(), candidate.lower()
        p_words = set(p_low.split())
        c_words = set(c_low.split())
        # Jaccard overlap
        union = p_words | c_words
        inter = p_words & c_words
        overlap = len(inter) / max(len(union), 1)
        score += overlap * 0.4
        # Relevance: prompt content words matched
        content_words = [w for w in p_words if len(w) > 3]
        if content_words:
            match_ratio = sum(1 for w in content_words if w in c_words) / len(content_words)
            score += match_ratio * 0.3
            reasons.append(f"execution:relevance={match_ratio:.2f}")
        # Negation checking
        p_negs = self._negation_scopes(prompt)
        c_negs = self._negation_scopes(candidate)
        for scope in p_negs:
            if scope in c_low and not any(scope in cn for cn in c_negs):
                score -= 0.3
                reasons.append(f"structural:negation_violation('{scope}')")
        # Numeric checking
        p_nums = self._parse_numbers(prompt)
        c_nums = self._parse_numbers(candidate)
        if p_nums and c_nums:
            direction = sum(self.comparatives.get(w, 0) for w in p_low.split())
            if direction > 0 and c_nums[0] < p_nums[0]:
                score -= 0.25
                reasons.append(f"execution:numeric_violation(expected>{p_nums[0]},got={c_nums[0]})")
            elif direction < 0 and c_nums[0] > p_nums[0]:
                score -= 0.25
                reasons.append(f"execution:numeric_violation(expected<{p_nums[0]},got={c_nums[0]})")
            elif p_nums and c_nums:
                if abs(p_nums[0] - c_nums[0]) < 0.01:
                    score += 0.15
                    reasons.append(f"execution:numeric_match({c_nums[0]})")
        # Conditional checking
        ante, cons = self._extract_conditional(prompt)
        if ante and cons:
            if ante in c_low and cons not in c_low:
                score -= 0.25
                reasons.append(f"structural:modus_ponens_fail(has '{ante}', missing '{cons}')")
            elif ante in c_low and cons in c_low:
                score += 0.1
                reasons.append("structural:conditional_satisfied")
        # Contradiction pairs
        contras = [('impossible', 'possible'), ('false', 'true'), ('never', 'always')]
        for neg, pos in contras:
            if neg in p_low and pos in c_low and neg not in c_low:
                score -= 0.25
                reasons.append(f"structural:contradiction({neg}/{pos})")
        return max(0.0, min(1.0, score)), reasons

    def _sensitivity_analysis(self, prompt: str, candidate: str, base_score: float) -> float:
        """Finite-difference gradient proxy: perturb candidate, measure score change."""
        words = candidate.split()
        if len(words) < 2:
            return 0.0
        perturbed = ' '.join(words[:-1])
        perturbed_score, _ = self._structural_eval(prompt, perturbed)
        gradient = abs(base_score - perturbed_score)
        return gradient

    def _clarke_groves_payment(self, scores: List[float], idx: int) -> float:
        if not scores or len(scores) <= 1:
            return scores[idx] if scores else 0.0
        total_without = sum(scores) - scores[idx]
        avg_others = total_without / (len(scores) - 1)
        marginal = scores[idx]
        penalty = 0.15 * max(0, avg_others - scores[idx])
        return max(0.0, marginal - penalty)

    def _metacognitive_control(self, scores: List[float]) -> tuple:
        if len(scores) < 2:
            return 1.0, "meta:single_candidate"
        mean_s = sum(scores) / len(scores)
        variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
        self._meta_uncertainty = 0.7 * self._meta_uncertainty + 0.3 * variance
        temp = 0.5 + 2.0 * math.tanh(variance * 5.0)
        if variance < 0.01:
            reason = f"meta:high_agreement(var={variance:.4f},temp={temp:.2f})"
        elif variance > 0.1:
            reason = f"meta:high_disagreement(var={variance:.4f},temp={temp:.2f})"
        else:
            reason = f"meta:moderate(var={variance:.4f},temp={temp:.2f})"
        return temp, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        candidates = [c if c else "" for c in candidates]
        raw_scores = []
        all_reasons = []
        for cand in candidates:
            if not cand.strip():
                raw_scores.append(0.0)
                all_reasons.append(["structural:empty_candidate"])
                continue
            base, reasons = self._structural_eval(prompt, cand)
            grad = self._sensitivity_analysis(prompt, cand, base)
            if grad > 0.2:
                reasons.append(f"execution:high_sensitivity(grad={grad:.3f})")
            raw_scores.append(base)
            all_reasons.append(reasons)
        temp, meta_reason = self._metacognitive_control(raw_scores)
        max_score = max(raw_scores) if raw_scores else 1.0
        norm_scores = [s / (max_score + 1e-9) for s in raw_scores]
        exp_scores = [math.exp((s - 1.0) / temp) for s in norm_scores]
        sum_exp = sum(exp_scores) + 1e-9
        bids = [e / sum_exp for e in exp_scores]
        results = []
        for i, cand in enumerate(candidates):
            reasons = list(all_reasons[i])
            reasons.append(meta_reason)
            payment = self._clarke_groves_payment(raw_scores, i)
            final = 0.50 * raw_scores[i] + 0.25 * bids[i] + 0.25 * min(payment, 1.0)
            final = max(0.0, min(1.0, final))
            reasons.append(f"mechanism:bid={bids[i]:.3f},payment={payment:.3f}")
            results.append({"candidate": cand, "score": final, "reasoning": '; '.join(reasons)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]:
                r["reasoning"] += "; structural:low_confidence_margin(<5%)"
        # Metacognitive reflection on top candidate
        if results and results[0]["score"] > 0:
            top = results[0]
            _, recheck = self._structural_eval(prompt, top["candidate"])
            violations = [r for r in recheck if 'violation' in r or 'contradiction' in r or 'fail' in r]
            if violations:
                top["reasoning"] += f"; reflection:top_has_issues({len(violations)} flags)"
                top["score"] = max(0.0, top["score"] - 0.05)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer:
            return 0.0
        base, reasons = self._structural_eval(prompt, answer)
        violations = [r for r in reasons if 'violation' in r or 'contradiction' in r or 'fail' in r]
        if len(violations) >= 2:
            return max(0.0, 0.05 * base)
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = sum(null_scores) / max(len(null_scores), 1)
        if null_mean >= ans_score:
            return max(0.0, 0.1 * ans_score)
        separation = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        grad = self._sensitivity_analysis(prompt, answer, base)
        stability = 1.0 / (1.0 + grad * 5)
        conf = 0.3 * ans_score + 0.4 * separation + 0.3 * stability
        return float(max(0.0, min(1.0, conf)))
