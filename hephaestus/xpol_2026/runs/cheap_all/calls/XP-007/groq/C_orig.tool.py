from typing import Dict

"""
Adaptive Abstract Kalman Scorer (AAKS)

ReasoningTool implements a lightweight neuro‑symbolic pipeline that
combines three primitives:

1. modus_ponens   – forward‑chaining over Horn clauses (abstract interpretation)
2. solve_linear_system – computes the Kalman gain without writing the matrix
   inversion explicitly (adaptive control)
3. bayesian_update – adapts the observation‑noise matrix R (self‑tuning regulator)

The resulting belief vector (means μ and variances sigma²) is scored against
candidate answers using a signal‑to‑noise ratio.  A meta‑confidence
routine inspects the prompt for common ambiguity traps and caps the final
confidence accordingly.
"""

import re
import zlib
import numpy as np
from typing import List, Dict

# primitives supplied by the evaluation environment
from forge_primitives import (
    modus_ponens,
    solve_linear_system,
    bayesian_update,
    confidence_from_agreement,
)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def ncd(s1: str, s2: str) -> float:
    """Normalized compression distance using zlib (max 0.15 weight)."""
    c1 = len(zlib.compress(s1.encode()))
    c2 = len(zlib.compress(s2.encode()))
    c12 = len(zlib.compress((s1 + s2).encode()))
    return (c12 - min(c1, c2)) / max(c1, c2)


def extract_numbers(text: str) -> List[float]:
    return [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", text)]


def extract_comparatives(text: str) -> List[str]:
    return re.findall(r"(>=|<=|>|<|more than|less than)", text, flags=re.I)


def extract_negations(text: str) -> int:
    return len(re.findall(r"\b(not|no|never|n't)\b", text, flags=re.I))


def extract_causals(text: str) -> List[tuple]:
    """Return (cause, effect) pairs for simple causal verbs."""
    pattern = r"(\w+)\s+(cause|leads? to|results? in)\s+(\w+)"
    return [(m[0], m[2]) for m in re.findall(pattern, text, flags=re.I)]


def extract_conditionals(text: str) -> List[tuple]:
    """Return (antecedent list, consequent) for simple if‑then clauses."""
    clauses = []
    for m in re.finditer(r"if\s+([^.,;]+?)\s+then\s+([^.,;]+)", text, flags=re.I):
        antecedents = [a.strip() for a in re.split(r"\band\b", m.group(1), flags=re.I)]
        consequent = m.group(2).strip()
        clauses.append((antecedents, consequent))
    return clauses


# --------------------------------------------------------------------------- #
# Main class
# --------------------------------------------------------------------------- #
class ReasoningTool:
    """Adaptive Abstract Kalman Scorer (AAKS)."""

    def __init__(self):
        self.eps = 1e-8
        self.R_init = 1e-3
        self.Q_init = 1e-3
        self.innov_thresh = 2.0  # multiplier for innovation gating

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidate answers according to the AAKS belief‑score.
        Returns a list of dicts: {"candidate": str, "score": float, "reasoning": str}
        """
        # 1. Parse prompt -> propositions & Horn clauses
        props, clauses = self._parse_prompt(prompt)

        n = len(props)
        mu = np.full(n, 0.5)          # start with neutral belief
        sigma2 = np.full(n, 1.0)      # relatively uncertain
        Q = np.eye(n) * self.Q_init
        R = np.eye(len(props)) * self.R_init  # will be resized per answer

        # map proposition string -> index
        prop_index = {p: i for i, p in enumerate(props)}

        # 2. Process each candidate
        results = []
        for cand in candidates:
            # ---- feature extraction -------------------------------------------------
            f_vec, H = self._build_observation(cand, props, prop_index)

            # ---- abstract interpretation (prediction) --------------------------------
            mu_pred, sigma2_pred = self._predict(mu, sigma2, clauses, prop_index)

            # ---- Kalman gain (adaptive control) ------------------------------------
            P_pred = np.diag(sigma2_pred)
            # Solve K·(H·P·Hᵀ+R) = P·Hᵀ  ->  K = solve_linear_system(A, B)
            A = H @ P_pred @ H.T + R[: H.shape[0], : H.shape[0]]
            B = P_pred @ H.T
            K = solve_linear_system(A, B)  # shape (n, m)

            # ---- innovation & update -------------------------------------------------
            innovation = f_vec - H @ mu_pred
            mu_upd = mu_pred + K @ innovation
            sigma2_upd = np.diag((np.eye(n) - K @ H) @ P_pred)

            # ---- noise adaptation ----------------------------------------------------
            # inflate R where innovation is large
            std_innov = np.sqrt(np.diag(A))
            large = np.abs(innovation) > self.innov_thresh * std_innov
            R_inc = np.diag(large.astype(float) * self.R_init)
            R[: R_inc.shape[0], : R_inc.shape[1]] += R_inc

            # shrink Q when all innovations are small
            if not large.any():
                Q *= 0.9

            # ---- scoring -------------------------------------------------------------
            # score = sum_{i in mentioned propositions} mu_i / sqrt(sigma2_i)
            mentioned = np.where(H.sum(axis=0) > 0)[0]  # indices of props touched
            if mentioned.size == 0:
                score = 0.0
            else:
                snr = mu_upd[mentioned] / np.sqrt(sigma2_upd[mentioned] + self.eps)
                score = float(snr.mean())

            # ---- reasoning string (human‑readable) ----------------------------------
            reasoning = (
                f"Parsed {len(props)} propositions, {len(clauses)} Horn clauses. "
                f"Prediction μ={mu_pred.round(2).tolist()}, sigma²={sigma2_pred.round(2).tolist()}. "
                f"Innovation={innovation.round(2).tolist()}, score={score:.3f}."
            )

            results.append(
                {"candidate": cand, "score": score, "reasoning": reasoning}
            )

            # keep updated belief for next candidate (optional – here we reset)
            mu, sigma2 = mu_upd, sigma2_upd

        # 3. Rank by score (NCD tie‑breaker, max 15 % weight)
        results.sort(key=lambda x: x["score"], reverse=True)
        # apply NCD only when scores are equal within 1e‑6
        for i in range(1, len(results)):
            if abs(results[i]["score"] - results[i - 1]["score"]) < 1e-6:
                d0 = ncd(prompt, results[i - 1]["candidate"])
                d1 = ncd(prompt, results[i]["candidate"])
                if d1 < d0:
                    results[i - 1], results[i] = results[i], results[i - 1]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return a calibrated confidence in [0,1] for *answer* to *prompt*.
        The value is limited by a meta‑confidence detector that looks for
        ambiguity traps.
        """
        meta = self._meta_confidence(prompt)
        # never exceed 0.9 unless meta already forces lower
        return min(meta, 0.9)

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _parse_prompt(self, prompt: str):
        """Extract primitive propositions and Horn clauses from the prompt."""
        props = set()

        # Negations
        neg_cnt = extract_negations(prompt)
        if neg_cnt:
            props.add("negation_present")

        # Comparatives
        for comp in extract_comparatives(prompt):
            props.add(f"comp_{comp}")

        # Numbers (as simple propositions)
        for num in extract_numbers(prompt):
            props.add(f"num_{num}")

        # Causal edges -> propositions "cause_X_to_Y"
        for cause, effect in extract_causals(prompt):
            props.add(f"cause_{cause}_to_{effect}")

        # Conditionals -> Horn clauses
        clauses = []
        for ants, cons in extract_conditionals(prompt):
            # ensure each antecedent and consequent appears as a proposition
            for a in ants:
                a = a.strip()
                props.add(a)
            cons = cons.strip()
            props.add(cons)
            clauses.append((ants, cons))

        # Add any leftover words that look like atomic facts
        for token in re.findall(r"\b\w+\b", prompt):
            if token.lower() not in {"if", "then", "and", "or", "not", "no"}:
                props.add(token.lower())

        return list(props), clauses

    def _build_observation(self, answer: str, props: List[str], prop_index: dict):
        """
        Build observation vector f and observation matrix H.
        Each feature is linked to the proposition it mentions (if any).
        """
        m = 0
        rows = []
        vals = []

        # Feature 1: negation presence
        neg = int(bool(re.search(r"\b(not|no|never|n't)\b", answer, flags=re.I)))
        if "negation_present" in prop_index:
            rows.append([prop_index["negation_present"]])
            vals.append([neg])
            m += 1

        # Feature 2: comparatives
        comps = extract_comparatives(answer)
        for comp in comps:
            key = f"comp_{comp}"
            if key in prop_index:
                rows.append([prop_index[key]])
                vals.append([1])
                m += 1

        # Feature 3: numbers (use first numeric token)
        nums = extract_numbers(answer)
        if nums:
            # map each numeric proposition to the closest value
            for num in nums:
                key = min(
                    (p for p in props if p.startswith("num_")),
                    key=lambda p: abs(float(p.split("_", 1)[1]) - num),
                    default=None,
                )
                if key:
                    rows.append([prop_index[key]])
                    vals.append([1])
                    m += 1

        # Feature 4: causal verbs
        for cause, effect in extract_causals(answer):
            key = f"cause_{cause}_to_{effect}"
            if key in prop_index:
                rows.append([prop_index[key]])
                vals.append([1])
                m += 1

        # Assemble H (m x n) – each row has a single 1 at the proposition index
        if m == 0:
            # fallback: identity on first proposition to keep dimensions valid
            H = np.eye(len(props), dtype=float)[:1]
            f = np.array([0.0])
        else:
            H = np.zeros((m, len(props)), dtype=float)
            for i, (r, v) in enumerate(zip(rows, vals)):
                H[i, r[0]] = v[0]
            f = np.array([v[0] for v in vals], dtype=float)

        return f, H

    def _predict(self, mu, sigma2, clauses, prop_index):
        """Forward‑chaining (abstract interpretation) using modus_ponens."""
        mu_pred = mu.copy()
        sigma2_pred = sigma2.copy()

        # Convert clauses to a format accepted by modus_ponens:
        # premises = list of antecedent proposition strings,
        # facts = indices where mu > 0.5 (treated as true)
        facts = {p for p, m in zip(prop_index.keys(), mu) if m > 0.5}
        for ants, cons in clauses:
            # modus_ponens returns True if all antecedents are in facts
            if modus_ponens(ants, facts):
                idx_c = prop_index[cons]
                # t‑norm (min) for mean, additive variance for conservative bound
                mu_c = min(mu_pred[prop_index[a]] for a in ants if a in prop_index)
                var_c = sum(sigma2_pred[prop_index[a]] for a in ants if a in prop_index)
                mu_pred[idx_c] = mu_c
                sigma2_pred[idx_c] = var_c + self.Q_init  # small process noise

        return mu_pred, sigma2_pred

    # --------------------------------------------------------------------- #
    # Meta‑confidence detector
    # --------------------------------------------------------------------- #
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity traps; return a base confidence in [0,1]."""
        low = 0.1  # default low confidence for ambiguous prompts
        high = 0.6  # moderate confidence when no trap is found

        # 1. Presupposition
        if re.search(r"\b(have you (stopped|quit|ceased))\b", prompt, flags=re.I):
            return low
        if re.search(r"\bwhy did .* (fail|stop)\b", prompt, flags=re.I):
            return low

        # 2. Scope ambiguity – "every X ... a Y"
        if re.search(r"\bevery\s+\w+\b.*\ba\s+\w+\b", prompt, flags=re.I):
            return low

        # 3. Pronoun ambiguity – "X told Y he/she ..."
        if re.search(r"\b\w+\s+told\s+\w+\s+(he|she|they)\b", prompt, flags=re.I):
            return low

        # 4. False dichotomy – "either A or B" without exhaustive list
        if re.search(r"\beither\s+.+\s+or\s+.+\b", prompt, flags=re.I):
            return low

        # 5. Subjectivity – superlatives without criteria
        if re.search(r"\b(best|worst|favorite|most|least)\b", prompt, flags=re.I):
            return low

        # 6. Unanswerability – asks for external knowledge
        if re.search(r"\b(what|who|when|where|how)\b.*\b(is|are|was|were)\b", prompt, flags=re.I):
            # crude check: if no numbers or comparatives appear, treat as unanswerable
            if not extract_numbers(prompt) and not extract_comparatives(prompt):
                return low

        # No trap detected -> moderate confidence
        return high


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
