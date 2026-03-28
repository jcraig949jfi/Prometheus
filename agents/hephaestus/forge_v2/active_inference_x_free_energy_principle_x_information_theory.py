import math
import hashlib
import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Information-Bottleneck Active Inference (IBAI) v2.

    Intersection:
    1. Active Inference: Candidates are scored by expected free energy minimization,
       balancing pragmatic value (accuracy) and epistemic value (uncertainty reduction).
    2. Free Energy Principle: Variational free energy computed as divergence between
       prompt-derived prior and candidate posterior feature distributions.
    3. Information Theory: Mutual information estimation, entropy of feature
       distributions, and information gain over null baseline.
    """

    def __init__(self):
        self.negations = ['not', 'no', 'never', 'neither', 'cannot', "won't", "isn't", "doesn't", "don't"]
        self.comparatives = {'greater': 1, 'more': 1, 'larger': 1, 'higher': 1, 'less': -1, 'fewer': -1, 'smaller': -1, 'lower': -1}

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

    def _char_distribution(self, text: str) -> List[float]:
        if not text:
            return [1.0 / 27] * 27
        counts = [0] * 27
        for c in text.lower():
            if 'a' <= c <= 'z':
                counts[ord(c) - ord('a')] += 1
            else:
                counts[26] += 1
        total = sum(counts) + 1e-9
        return [c / total for c in counts]

    def _entropy(self, dist: List[float]) -> float:
        return -sum(p * math.log(p + 1e-12) for p in dist if p > 0)

    def _kl_divergence(self, p: List[float], q: List[float]) -> float:
        return sum(pi * math.log((pi + 1e-12) / (qi + 1e-12)) for pi, qi in zip(p, q) if pi > 0)

    def _mutual_information(self, text1: str, text2: str) -> float:
        d1 = self._char_distribution(text1)
        d2 = self._char_distribution(text2)
        joint = [0.0] * 27
        combined = text1.lower() + text2.lower()
        joint = self._char_distribution(combined)
        h1 = self._entropy(d1)
        h2 = self._entropy(d2)
        h_joint = self._entropy(joint)
        mi = h1 + h2 - h_joint
        return max(0.0, mi)

    def _variational_free_energy(self, prompt: str, candidate: str) -> float:
        p_dist = self._char_distribution(prompt)
        c_dist = self._char_distribution(candidate)
        kl = self._kl_divergence(c_dist, p_dist)
        return kl

    def _ncd(self, s1: str, s2: str) -> float:
        z = zlib.compress
        l1, l2 = len(z(s1.encode())), len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        return (l12 - min(l1, l2)) / max(l1, l2, 1)

    def _structural_score(self, prompt: str, candidate: str) -> tuple:
        reasons = []
        penalty = 0.0
        p_low, c_low = prompt.lower(), candidate.lower()
        p_negs = self._negation_scopes(prompt)
        for scope in p_negs:
            if scope in c_low:
                c_negs = self._negation_scopes(candidate)
                if not any(scope in cn for cn in c_negs):
                    penalty += 0.35
                    reasons.append(f"structural:negation_violation('{scope}' affirmed despite prompt negation)")
        p_nums = self._parse_numbers(prompt)
        c_nums = self._parse_numbers(candidate)
        if p_nums and c_nums:
            direction = sum(self.comparatives.get(w, 0) for w in p_low.split())
            if direction > 0 and c_nums[0] < p_nums[0]:
                penalty += 0.3
                reasons.append(f"execution:numeric_mismatch(expected>{p_nums[0]},got={c_nums[0]})")
            elif direction < 0 and c_nums[0] > p_nums[0]:
                penalty += 0.3
                reasons.append(f"execution:numeric_mismatch(expected<{p_nums[0]},got={c_nums[0]})")
        ante, cons = self._extract_conditional(prompt)
        if ante and cons:
            if ante in c_low and cons not in c_low:
                penalty += 0.3
                reasons.append(f"structural:modus_ponens_fail(has '{ante}', missing '{cons}')")
            if ('not ' + cons) in c_low and ante in c_low:
                penalty += 0.3
                reasons.append("structural:modus_tollens_contradiction")
        contras = [('impossible', 'possible'), ('false', 'true'), ('never', 'always')]
        for neg, pos in contras:
            if neg in p_low and pos in c_low and neg not in c_low:
                penalty += 0.25
                reasons.append(f"structural:direct_contradiction({neg}/{pos})")
        return min(penalty, 1.0), reasons

    def _epistemic_value(self, prompt: str, candidate: str) -> float:
        mi = self._mutual_information(prompt, candidate)
        c_entropy = self._entropy(self._char_distribution(candidate))
        null_entropy = self._entropy([1.0 / 27] * 27)
        info_gain = null_entropy - c_entropy if c_entropy < null_entropy else 0.0
        return 0.6 * mi + 0.4 * info_gain

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        candidates = [c if c else "" for c in candidates]
        results = []
        for cand in candidates:
            if not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"})
                continue
            reasons = []
            vfe = self._variational_free_energy(prompt, cand)
            pragmatic = math.exp(-vfe)
            reasons.append(f"execution:free_energy={vfe:.3f},pragmatic={pragmatic:.3f}")
            epistemic = self._epistemic_value(prompt, cand)
            reasons.append(f"execution:epistemic_value={epistemic:.3f}")
            struct_pen, struct_reasons = self._structural_score(prompt, cand)
            reasons.extend(struct_reasons)
            ncd_val = 1.0 - self._ncd(prompt, cand)
            ncd_weight = 0.10
            use_ncd_fallback = (not struct_reasons and pragmatic < 0.3 and epistemic < 0.2)
            if use_ncd_fallback:
                ncd_weight = 0.15
                reasons.append("fallback:ncd")
            score = 0.35 * pragmatic + 0.25 * epistemic + 0.30 * (1.0 - struct_pen) + ncd_weight * ncd_val
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(reasons)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]:
                r["reasoning"] += "; structural:low_confidence_margin(<5%)"
        if results:
            top = results[0]
            _, re_check = self._structural_score(prompt, top["candidate"])
            if re_check:
                top["reasoning"] += "; reflection:top_candidate_has_structural_flags"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer:
            return 0.0
        struct_pen, _ = self._structural_score(prompt, answer)
        if struct_pen >= 0.65:
            return max(0.0, 0.08 * (1.0 - struct_pen))
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = sum(null_scores) / max(len(null_scores), 1)
        if null_mean >= ans_score:
            return max(0.0, 0.12 * ans_score)
        separation = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        mi = self._mutual_information(prompt, answer)
        mi_norm = min(mi / 3.0, 1.0)
        conf = 0.25 * ans_score + 0.50 * separation + 0.25 * mi_norm
        return float(max(0.0, min(1.0, conf)))
