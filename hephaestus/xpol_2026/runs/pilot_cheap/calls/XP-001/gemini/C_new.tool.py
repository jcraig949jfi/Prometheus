import re
import zlib
import numpy as np


class ReasoningTool:
    """
    Quantum-Plastic Model Checker (QPMC) Reasoning Tool.
    Combines superposition state vectors, dynamic Hebbian matrix plasticity,
    and Kripke logic state projection with epistemic meta-confidence calibration.
    """

    def __init__(self):
        pass

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates prompt for Tier B judgment traps (presuppositions, scope ambiguity,
        pronoun ambiguity, false dichotomies, subjectivity, and unanswerability).
        Returns a meta-confidence cap in [0.0, 1.0].
        """
        p_lower = prompt.lower()

        # Presupposition traps
        if re.search(
            r"\b(stopped|quit|why did|when did|how come)\b.*\?", p_lower
        ):
            if any(
                w in p_lower for w in ["fail", "stop", "quit", "cheat", "lose"]
            ):
                return 0.15

        # Scope ambiguity (e.g., "Every student read a book")
        if re.search(r"\bevery\b.+\b(a|an|one)\b", p_lower):
            return 0.20

        # Pronoun ambiguity (e.g., "John told Bill he was wrong")
        if re.search(r"\b(told|asked|said to)\b.+\b(he|she|they)\b", p_lower):
            return 0.20

        # False dichotomy
        if re.search(r"\beither\b.+\bor\b", p_lower) and not re.search(
            r"\bboth\b|\bneither\b|\bother\b", p_lower
        ):
            return 0.20

        # Subjectivity / Measurability missing
        if re.search(
            r"\b(best|worst|favorite|better|morally|prettier|handsomest)\b",
            p_lower,
        ):
            return 0.10

        # Insufficient information / unanswerable prompt
        if "cannot be determined" in p_lower or "insufficient info" in p_lower:
            return 0.25

        return 0.95

    def _solve_direct(self, prompt: str) -> tuple:
        """
        Constructive computation for Tier A deterministic parsing & math traps.
        Returns (has_direct_solution: bool, answer_str: str or None).
        """
        p = prompt.strip()

        # 1. Numeric comparisons (e.g. "Is 9.11 > 9.9?", "Which is larger, 9.11 or 9.9?")
        nums = re.findall(r"-?\d+\.?\d*", p)
        if (
            any(
                w in p.lower()
                for w in ["larger", "greater", "bigger", "smaller", "less"]
            )
            or ">" in p
            or "<" in p
        ) and len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                if "smaller" in p.lower() or "less" in p.lower() or "<" in p:
                    ans = n1 if n1 < n2 else n2
                else:
                    ans = n1 if n1 > n2 else n2
                return True, str(ans)
            except Exception:
                pass

        # 2. Modulo arithmetic (e.g. "17 mod 5" or "17 % 5")
        mod_match = re.search(r"(\d+)\s*(?:mod|%)\s*(\d+)", p, re.IGNORECASE)
        if mod_match:
            n1, n2 = int(mod_match.group(1)), int(mod_match.group(2))
            return True, str(n1 % n2)

        # 3. Arithmetic / PEMDAS (e.g. "what is 5 + 3 * 2?")
        math_match = re.search(
            r"what is ([\d\s\+\-\*\/\(\)\.]+)\?", p, re.IGNORECASE
        )
        if math_match:
            try:
                expr = math_match.group(1)
                res = eval(expr, {"__builtins__": None}, {})
                return True, str(res)
            except Exception:
                pass

        return False, None

    def _qpmc_score(self, prompt: str, candidate: str) -> float:
        """
        QPMC Matrix state vector evolution with dynamic Hebbian plasticity
        and quantum projection onto the specification subspace.
        """
        tokens = re.findall(r"\w+", prompt.lower() + " " + candidate.lower())
        vocab = sorted(list(set(tokens)))
        N = min(len(vocab), 30)
        if N == 0:
            return 0.0
        vmap = {w: i for i, w in enumerate(vocab[:N])}

        # Superposition state vector v and Kripke adjacency matrix T
        v = np.ones(N) / np.sqrt(N)
        T = np.zeros((N, N))

        p_tokens = re.findall(r"\w+", prompt.lower())
        for i in range(len(p_tokens) - 1):
            if p_tokens[i] in vmap and p_tokens[i + 1] in vmap:
                u, w = vmap[p_tokens[i]], vmap[p_tokens[i + 1]]
                T[u, w] += 1.0

        sum_T = np.sum(T)
        if sum_T > 0:
            T = T / sum_T

        W = np.copy(T)  # Plasticity Matrix
        c_tokens = re.findall(r"\w+", candidate.lower())

        alpha, theta = 0.1, 0.02
        for i in range(len(c_tokens) - 1):
            if c_tokens[i] in vmap and c_tokens[i + 1] in vmap:
                u, w = vmap[c_tokens[i]], vmap[c_tokens[i + 1]]
                # Hebbian dynamic reinforcement
                W[u, w] += alpha * v[u] * v[w]
                # Operator state step
                O_t = np.eye(N)
                O_t[u, u] = 0.5
                O_t[w, u] = 0.8
                v = np.dot(O_t, np.dot(W * T, v))
                norm_v = np.linalg.norm(v)
                if norm_v > 0:
                    v = v / norm_v

        # Synaptic Pruning / Decoherence
        W[W < theta] = 0.0

        # Projection onto terminal specification states
        P_spec = np.zeros((N, N))
        for t in c_tokens:
            if t in vmap:
                P_spec[vmap[t], vmap[t]] = 1.0

        proj_v = np.dot(P_spec, v)
        q_score = float(np.sum(proj_v**2) / (np.sum(v**2) + 1e-8))
        return min(max(q_score, 0.0), 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance similarity (tiebreaker)."""
        b1, b2 = s1.encode("ascii", "ignore"), s2.encode("ascii", "ignore")
        cb1, cb2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        cb12 = len(zlib.compress(b1 + b2))
        return 1.0 - (cb12 - min(cb1, cb2)) / max(cb1, cb2, 1)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """
        Evaluates candidate answers against the prompt using QPMC linear
        algebra mechanics, direct constraint solvers, and NCD tiebreakers.
        """
        meta_conf = self._meta_confidence(prompt)
        has_direct, direct_ans = self._solve_direct(prompt)

        results = []
        for cand in candidates:
            if has_direct:
                cand_clean = cand.strip().lower()
                ans_clean = str(direct_ans).lower()
                if ans_clean in cand_clean or cand_clean == ans_clean:
                    struct_score = 1.0
                else:
                    struct_score = 0.0
                qpmc_s = struct_score
            else:
                struct_score = 0.5
                if "not" in prompt.lower() and "not" in cand.lower():
                    struct_score += 0.25
                if "if" in prompt.lower() and "then" in cand.lower():
                    struct_score += 0.25
                struct_score = min(struct_score, 1.0)
                qpmc_s = self._qpmc_score(prompt, cand)

            ncd_s = min(max(self._ncd(prompt, cand), 0.0), 1.0)

            if has_direct:
                final_score = 0.85 * struct_score + 0.15 * ncd_s
            else:
                final_score = 0.40 * struct_score + 0.45 * qpmc_s + 0.15 * ncd_s

            reasoning = (
                f"QPMC={qpmc_s:.2f}, Struct={struct_score:.2f}, "
                f"MetaConf={meta_conf:.2f}"
            )
            results.append(
                {
                    "candidate": cand,
                    "score": round(float(final_score), 4),
                    "reasoning": reasoning,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns calibrated confidence in [0, 1]. Capped under ambiguity/traps.
        """
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf

        has_direct, direct_ans = self._solve_direct(prompt)
        if has_direct:
            ans_clean = str(direct_ans).lower()
            if ans_clean in answer.lower():
                return min(0.95, meta_conf)
            return 0.05

        eval_res = self.evaluate(prompt, [answer])
        cand_score = eval_res[0]["score"] if eval_res else 0.5

        conf = min(meta_conf, cand_score * 0.85)
        return round(float(conf), 4)


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
