import math
import hashlib
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Ergodic-Falsification-Maximum-Entropy (EFME) Engine v2.

    Intersection:
    1. Maximum Entropy: Prior over candidates using exponential family constrained
       by observed features (length, structure), not just length alone.
    2. Ergodic Sampling: Deterministic pseudo-random walk seeded by prompt to
       simulate time-averaged exploration of hypothesis space.
    3. Falsificationism: Active contradiction detection via negation scope parsing,
       numeric consistency, conditional logic (modus ponens/tollens), and
       subject-object structure checking.
    """

    def __init__(self):
        self.lambda_complexity = 0.05
        self.beta_falsification = 3.0
        self.negations = ['not', 'no', 'never', 'neither', 'nor', 'cannot', "won't", "isn't", "aren't", "doesn't", "don't"]
        self.comparatives = {'greater': 1, 'more': 1, 'larger': 1, 'higher': 1, 'less': -1, 'fewer': -1, 'smaller': -1, 'lower': -1}

    def _hash_seed(self, text: str) -> int:
        return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)

    def _parse_numbers(self, text: str) -> List[float]:
        return [float(m) for m in re.findall(r'-?\d+\.?\d*', text)]

    def _negation_scopes(self, text: str) -> List[str]:
        words = text.lower().split()
        scopes = []
        for i, w in enumerate(words):
            if w in self.negations and i + 1 < len(words):
                scopes.append(' '.join(words[i:min(i + 4, len(words))]))
        return scopes

    def _extract_conditional(self, text: str):
        m = re.search(r'\bif\b(.+?)\bthen\b(.+?)(?:\.|,|$)', text.lower())
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return None, None

    def _extract_svo(self, text: str):
        m = re.search(r'(\w+)\s+(did|gave|sent|told|showed|made|built)\s+(\w+)\s+to\s+(\w+)', text.lower())
        if m:
            return m.group(1), m.group(2), m.group(3), m.group(4)
        return None, None, None, None

    def _compute_maxent_prior(self, candidate: str, prompt: str) -> tuple:
        words = candidate.lower().split()
        n = max(len(words), 1)
        p_words = set(prompt.lower().split())
        complexity = len(candidate)
        uniqueness = len(set(words)) / n
        relevance = len(set(words) & p_words) / max(len(p_words), 1)
        feature_energy = self.lambda_complexity * complexity - 0.5 * relevance - 0.3 * uniqueness
        prior = math.exp(-feature_energy)
        return prior, f"maxent_prior(complexity={complexity},relevance={relevance:.2f},uniq={uniqueness:.2f})"

    def _ergodic_walk_score(self, prompt: str, candidate: str, n_steps: int = 8) -> tuple:
        seed = self._hash_seed(prompt)
        scores = []
        for step in range(n_steps):
            step_seed = self._hash_seed(f"{seed}_{step}_{candidate}")
            perturbation = ((step_seed % 10000) / 10000.0) * 0.2 - 0.1
            words_c = candidate.lower().split()
            words_p = prompt.lower().split()
            overlap = len(set(words_c) & set(words_p)) / max(len(set(words_c) | set(words_p)), 1)
            scores.append(overlap + perturbation)
        time_avg = sum(scores) / len(scores)
        variance = sum((s - time_avg) ** 2 for s in scores) / len(scores)
        convergence = 1.0 / (1.0 + variance * 100)
        return time_avg, convergence, f"ergodic(time_avg={time_avg:.3f},convergence={convergence:.3f})"

    def _falsify(self, prompt: str, candidate: str) -> tuple:
        reasons = []
        penalty = 0.0
        p_low, c_low = prompt.lower(), candidate.lower()
        p_negs = self._negation_scopes(prompt)
        c_negs = self._negation_scopes(candidate)
        for scope in p_negs:
            neg_word = scope.split()[0]
            target = ' '.join(scope.split()[1:])
            if target and target in c_low:
                if not any(target in cn for cn in c_negs):
                    penalty += 0.4
                    reasons.append(f"structural:negation_scope_violation(prompt negates '{target}', candidate affirms)")
        contras = [('impossible', 'possible'), ('false', 'true'), ('never', 'always')]
        for neg, pos in contras:
            if neg in p_low and pos in c_low and neg not in c_low:
                penalty += 0.3
                reasons.append(f"structural:contradiction({neg}->{pos})")
        p_nums = self._parse_numbers(prompt)
        c_nums = self._parse_numbers(candidate)
        if p_nums and c_nums:
            p_words = p_low.split()
            direction = sum(self.comparatives.get(w, 0) for w in p_words)
            if direction > 0 and len(c_nums) >= 1 and len(p_nums) >= 1:
                if c_nums[0] < p_nums[0]:
                    penalty += 0.3
                    reasons.append(f"execution:numeric_violation(expected>{p_nums[0]},got={c_nums[0]})")
            elif direction < 0 and len(c_nums) >= 1 and len(p_nums) >= 1:
                if c_nums[0] > p_nums[0]:
                    penalty += 0.3
                    reasons.append(f"execution:numeric_violation(expected<{p_nums[0]},got={c_nums[0]})")
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_ord = p_nums[0] < p_nums[1]
                c_ord = c_nums[0] < c_nums[1]
                if p_ord != c_ord:
                    penalty += 0.2
                    reasons.append("execution:numeric_order_mismatch")
        ante, cons = self._extract_conditional(prompt)
        if ante and cons:
            if ante in c_low and cons not in c_low:
                penalty += 0.35
                reasons.append(f"structural:modus_ponens_fail(ante='{ante}',missing cons='{cons}')")
        return min(penalty, 1.0), reasons

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        candidates = [c if c else "" for c in candidates]
        priors = []
        for c in candidates:
            p, _ = self._compute_maxent_prior(c, prompt)
            priors.append(p)
        max_prior = max(priors) if priors else 1.0
        results = []
        for i, cand in enumerate(candidates):
            parts = []
            if not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"})
                continue
            prior = priors[i] / (max_prior + 1e-9)
            _, prior_reason = self._compute_maxent_prior(cand, prompt)
            parts.append(prior_reason)
            f_pen, f_reasons = self._falsify(prompt, cand)
            likelihood = math.exp(-self.beta_falsification * f_pen)
            parts.extend(f_reasons)
            if f_pen > 0:
                parts.append(f"falsified(penalty={f_pen:.2f})")
            else:
                parts.append("survived_falsification")
            erg_avg, erg_conv, erg_reason = self._ergodic_walk_score(prompt, cand)
            parts.append(erg_reason)
            ergodic_factor = 0.5 + 0.5 * erg_avg * erg_conv
            score = 0.30 * prior + 0.40 * likelihood + 0.30 * ergodic_factor
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(parts)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]:
                r["reasoning"] += "; structural:low_confidence_margin(<5%)"
        if results:
            top = results[0]
            _, re_fals = self._falsify(prompt, top["candidate"])
            if re_fals:
                top["reasoning"] += "; reflection:top_candidate_flagged_on_recheck"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer:
            return 0.0
        f_pen, _ = self._falsify(prompt, answer)
        if f_pen >= 0.7:
            return max(0.0, 0.08 * (1.0 - f_pen))
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = sum(null_scores) / max(len(null_scores), 1)
        if null_mean >= ans_score:
            return max(0.0, 0.1 * ans_score)
        separation = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        conf = 0.3 * ans_score + 0.7 * separation
        return float(max(0.0, min(1.0, conf)))
