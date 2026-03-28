import numpy as np
import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Tensor-based Active Falsification Inference (TAFI) v2.

    Intersection:
    1. Tensor Decomposition: SVD on candidate feature matrix for low-rank structure.
    2. Free Energy Principle: KL-divergence surprise between prompt and candidate distributions.
    3. Falsificationism: Active contradiction detection via negation scope, numeric
       inconsistency, and conditional modus tollens checking.
    """

    def __init__(self):
        self.negations = ['not', 'no', 'never', 'neither', 'nor', 'cannot', "won't", "isn't", "aren't", "doesn't", "don't"]
        self.comparatives = {'greater': 1, 'more': 1, 'larger': 1, 'higher': 1, 'above': 1,
                             'less': -1, 'fewer': -1, 'smaller': -1, 'lower': -1, 'below': -1}

    def _parse_numbers(self, text: str) -> List[float]:
        return [float(m) for m in re.findall(r'-?\d+\.?\d*', text)]

    def _negation_scope(self, text: str) -> List[str]:
        words = text.lower().split()
        scoped = []
        for i, w in enumerate(words):
            if w in self.negations and i + 1 < len(words):
                scope = words[i + 1: min(i + 4, len(words))]
                scoped.append(' '.join(scope))
        return scoped

    def _extract_conditionals(self, text: str):
        m = re.search(r'\bif\b(.+?)\bthen\b(.+?)(?:\.|$)', text.lower())
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return None, None

    def _extract_features(self, text: str) -> np.ndarray:
        words = text.lower().split()
        n_words = max(len(words), 1)
        neg_density = sum(1 for w in words if w in self.negations) / n_words
        nums = self._parse_numbers(text)
        num_mean = np.tanh(np.mean(nums) / 100.0) if nums else 0.0
        num_present = 1.0 if nums else 0.0
        comp_signal = sum(self.comparatives.get(w, 0) for w in words) / n_words
        cond_present = 1.0 if re.search(r'\bif\b', text.lower()) else 0.0
        length_norm = min(len(text) / 500.0, 1.0)
        uniq_ratio = len(set(words)) / n_words
        return np.array([neg_density, num_present, num_mean, comp_signal, cond_present, length_norm, uniq_ratio])

    def _tensor_svd_score(self, prompt: str, candidates: List[str]) -> np.ndarray:
        feats = np.array([self._extract_features(c) for c in candidates])
        p_feat = self._extract_features(prompt)
        if feats.shape[0] < 2:
            return np.array([float(np.dot(p_feat, feats[0])) / (np.linalg.norm(p_feat) * np.linalg.norm(feats[0]) + 1e-9)]) if len(candidates) == 1 else np.zeros(len(candidates))
        try:
            U, S, Vt = np.linalg.svd(feats, full_matrices=False)
            rank = min(3, len(S))
            proj = Vt[:rank]
            p_proj = proj @ p_feat
            c_projs = (feats @ proj.T)
            scores = np.array([float(np.dot(p_proj, c_projs[i])) / (np.linalg.norm(p_proj) * np.linalg.norm(c_projs[i]) + 1e-9) for i in range(len(candidates))])
            return scores
        except Exception:
            return np.array([float(np.dot(p_feat, self._extract_features(c))) / (np.linalg.norm(p_feat) * np.linalg.norm(self._extract_features(c)) + 1e-9) for c in candidates])

    def _free_energy(self, prompt: str, candidate: str) -> float:
        p = self._extract_features(prompt)
        c = self._extract_features(candidate)
        p_dist = np.abs(p) / (np.sum(np.abs(p)) + 1e-9)
        c_dist = np.abs(c) / (np.sum(np.abs(c)) + 1e-9)
        kl = float(np.sum(np.where(c_dist > 1e-9, c_dist * np.log((c_dist + 1e-9) / (p_dist + 1e-9)), 0.0)))
        return max(0.0, kl)

    def _falsify(self, prompt: str, candidate: str) -> tuple:
        reasons = []
        penalty = 0.0
        p_neg = self._negation_scope(prompt)
        c_neg = self._negation_scope(candidate)
        c_low = candidate.lower()
        for scope in p_neg:
            if scope and scope in c_low and not any(scope in cn for cn in c_neg):
                penalty += 0.4
                reasons.append(f"negation_scope_violation({scope})")
        p_nums = self._parse_numbers(prompt)
        c_nums = self._parse_numbers(candidate)
        if p_nums and c_nums:
            p_words = prompt.lower().split()
            direction = sum(self.comparatives.get(w, 0) for w in p_words)
            if direction > 0 and c_nums[0] < p_nums[0]:
                penalty += 0.3
                reasons.append(f"execution:numeric_order_violation({c_nums[0]}<{p_nums[0]})")
            elif direction < 0 and c_nums[0] > p_nums[0]:
                penalty += 0.3
                reasons.append(f"execution:numeric_order_violation({c_nums[0]}>{p_nums[0]})")
        ante, cons = self._extract_conditionals(prompt)
        if ante and cons:
            if ante in c_low and cons not in c_low:
                penalty += 0.35
                reasons.append(f"structural:modus_ponens_fail(has '{ante}' but missing '{cons}')")
            if cons not in c_low and ('not ' + cons) in c_low:
                penalty += 0.35
                reasons.append("structural:modus_tollens_contradiction")
        return min(penalty, 1.0), reasons

    def _ncd(self, s1: str, s2: str) -> float:
        z = zlib.compress
        l1, l2 = len(z(s1.encode())), len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        return (l12 - min(l1, l2)) / max(l1, l2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        candidates = [c if c else "" for c in candidates]
        svd_scores = self._tensor_svd_score(prompt, candidates)
        results = []
        raw_scores = []
        all_reasons = []
        for i, cand in enumerate(candidates):
            if not cand.strip():
                raw_scores.append(0.0)
                all_reasons.append(["structural:empty_candidate"])
                continue
            reasons = []
            fe = self._free_energy(prompt, cand)
            fe_score = np.exp(-fe)
            fals_pen, fals_reasons = self._falsify(prompt, cand)
            reasons.extend(fals_reasons)
            svd_s = float((svd_scores[i] + 1.0) / 2.0)
            ncd_val = 1.0 - self._ncd(prompt, cand)
            ncd_weight = 0.10
            score = 0.35 * svd_s + 0.30 * fe_score + 0.25 * (1.0 - fals_pen) + ncd_weight * ncd_val
            if ncd_weight >= 0.15 and not fals_reasons:
                reasons.append("fallback:ncd")
            if not reasons:
                reasons.append(f"execution:svd={svd_s:.3f},fe={fe_score:.3f},falsify_pen={fals_pen:.3f}")
            raw_scores.append(max(0.0, min(1.0, score)))
            all_reasons.append(reasons)
        for i, cand in enumerate(candidates):
            results.append({"candidate": cand, "score": raw_scores[i], "reasoning": '; '.join(all_reasons[i])})
        if len(results) >= 2:
            results.sort(key=lambda x: x["score"], reverse=True)
            if results[0]["score"] - results[1]["score"] < 0.05:
                for r in results[:2]:
                    r["reasoning"] += "; structural:low_confidence_margin(<5%)"
        # Metacognitive reflection on top candidate
        if results:
            top = results[0]
            _, fals_r = self._falsify(prompt, top["candidate"])
            if fals_r:
                top["reasoning"] += "; reflection:top_candidate_has_falsification_flags"
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer:
            return 0.0
        fals_pen, _ = self._falsify(prompt, answer)
        if fals_pen >= 0.7:
            return max(0.0, 0.1 * (1.0 - fals_pen))
        null_candidates = ["", "unknown", "42"]
        all_cands = [answer] + null_candidates
        res = self.evaluate(prompt, all_cands)
        answer_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = np.mean(null_scores) if null_scores else 0.5
        if null_mean >= answer_score:
            return max(0.0, 0.15 * answer_score)
        separation = (answer_score - null_mean) / (1.0 - null_mean + 1e-9)
        conf = 0.3 * answer_score + 0.7 * separation
        return float(max(0.0, min(1.0, conf)))
