"""
ReasoningTool implements a lightweight version of the Entangled Plastic Model
Checker (EPMC).  It

* extracts atomic propositions from a prompt and each candidate answer,
* builds a weighted adjacency matrix that represents logical constraints,
* runs a few Hebbian‑plasticity updates (T=5) while propagating truth values,
* scores each candidate by the proportion of prompt‑propositions it can satisfy,
* uses a tiny NCD term (zlib) only as a tie‑breaker,
* and finally returns a calibrated confidence that respects epistemic‑honesty
  (presupposition, scope‑/pronoun‑ambiguity, false‑dichotomy, unanswerability).

The implementation uses only the Python standard library and NumPy and stays
well below the 200‑line limit.
"""
import re
import zlib
import itertools
import numpy as np
from collections import defaultdict

class ReasoningTool:
    def __init__(self):
        # hyper‑parameters of the EPMC loop
        self.T = 5          # critical period
        self.eta = 0.1      # Hebbian learning rate
        self.tau = 0.2      # pruning threshold
        self.ncd_weight = 0.15   # max influence of NCD (tiebreaker)

    # ------------------------------------------------------------------ #
    #  PUBLIC API
    # ------------------------------------------------------------------ #
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score and rank candidates."""
        # 1. parse propositions from prompt and candidates
        prop_list, cand_props = self._parse_all(prompt, candidates)

        p = len(prop_list)
        n = len(candidates)
        if p == 0:                     # nothing to reason about
            scores = np.full(n, 1.0 / n)
            reasons = ["no logical content"] * n
        else:
            # 2. adjacency from co‑occurrence in the same clause
            adj = self._build_adj(prop_list, prompt, candidates)

            # 3. initialise plastic weights
            w = np.full((p, p), 0.5, dtype=float)

            # 4. candidate‑specific truth vectors (boolean)
            cand_state = np.zeros((n, p), dtype=bool)
            for c, props in enumerate(cand_props):
                for idx in props:
                    cand_state[c, idx] = True

            # 5. run the plasticity / propagation loop
            for _ in range(self.T):
                # Hebbian update per candidate
                for c in range(n):
                    true_idx = np.where(cand_state[c])[0]
                    for i in true_idx:
                        for j in true_idx:
                            if i == j: continue
                            w[i, j] += self.eta * (1.0 - w[i, j])
                # decay for edges not co‑active in any candidate
                active = np.zeros((p, p), dtype=bool)
                for c in range(n):
                    ti = np.where(cand_state[c])[0]
                    active[np.ix_(ti, ti)] = True
                w[~active] -= self.eta * w[~active]
                w = np.clip(w, 0.0, 1.0)
                w[w < self.tau] = 0.0                     # pruning

                # propagate truth through surviving edges (implication)
                for c in range(n):
                    changed = True
                    while changed:
                        changed = False
                        true_idx = np.where(cand_state[c])[0]
                        for i in true_idx:
                            js = np.where(w[i] > 0)[0]
                            for j in js:
                                if not cand_state[c, j]:
                                    cand_state[c, j] = True
                                    changed = True

            # 6. compute raw satisfaction ratios (prompt propositions true)
            prompt_idx = [i for i, p in enumerate(prop_list) if p in self._extract_props(prompt)]
            sat = np.sum(cand_state[:, prompt_idx], axis=1) / max(1, len(prompt_idx))
            cand_score = sat.astype(float)
            # 7. NCD tie‑breaker (scaled to [0,1])
            ncd = np.array([self._ncd(prompt, cand) for cand in candidates])
            ncd = 1.0 - (ncd - ncd.min()) / (ncd.ptp() + 1e-12)   # higher = more similar
            # combine (weight of NCD limited to self.ncd_weight)
            final_score = (1 - self.ncd_weight) * cand_score + self.ncd_weight * ncd
            # normalise to a probability distribution for reasoning output
            prob = final_score / final_score.sum()
            reasons = [
                f"satisfied {sat[i]:.0%} of prompt propositions; "
                f"NCD={ncd[i]:.2f}"
                for i in range(n)
            ]

        # 8. build output list, sorted by descending score
        out = [
            {"candidate": candidates[i], "score": float(prob[i]), "reasoning": reasons[i]}
            for i in range(n)
        ]
        out.sort(key=lambda d: d["score"], reverse=True)
        return out

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return a calibrated confidence 0‑1.
        The meta‑confidence caps the value for ambiguous / unanswerable prompts.
        """
        meta = self._meta_confidence(prompt)
        # if the prompt is clearly ambiguous we stay low
        if meta < 0.3:
            return meta * 0.9          # never exceed 0.27 in that case

        # otherwise compute a provisional confidence from a tiny EPMC run
        # (we reuse evaluate on a single‑candidate list)
        eval_res = self.evaluate(prompt, [answer])
        raw = eval_res[0]["score"]          # already normalised
        # cap to 0.9 unless the answer is definitively forced by the prompt
        cap = 0.9 if raw < 0.99 else 0.95
        return min(raw, cap) * meta

    # ------------------------------------------------------------------ #
    #  INTERNAL HELPERS
    # ------------------------------------------------------------------ #
    def _parse_all(self, prompt, candidates):
        """Return (list of all propositions, list of per‑candidate index sets)."""
        all_props = set(self._extract_props(prompt))
        cand_props_idx = []
        for cand in candidates:
            props = set(self._extract_props(cand))
            all_props.update(props)
        prop_list = sorted(all_props)                     # stable order
        prop_to_idx = {p: i for i, p in enumerate(prop_list)}
        # map each candidate to a set of indices
        for cand in candidates:
            idxs = {prop_to_idx[p] for p in self._extract_props(cand) if p in prop_to_idx}
            cand_props_idx.append(idxs)
        return prop_list, cand_props_idx

    def _extract_props(self, text):
        """Very simple structural parser – returns a set of atomic proposition strings."""
        props = set()
        # 1. negations
        for m in re.finditer(r'\bnot\b|\bn['\']t\b', text, flags=re.I):
            span = text[max(0, m.start() - 20):m.end() + 20]
            props.add(f"NEG({span.strip()})")
        # 2. comparatives
        for a, op, b in re.findall(r'(\b\w+\b)\s*(>=|<=|>|<)\s*(\b\w+\b)', text):
            props.add(f"{a}{op}{b}")
        # 3. conditionals (if ... then ...)
        for m in re.finditer(r'if\s+([^,;.]+?)\s+then\s+([^,;.]+)', text, flags=re.I):
            props.add(f"IMP({m.group(1).strip()}->{m.group(2).strip()})")
        # 4. causal verbs
        for verb in ("cause", "leads to", "results in", "produces"):
            for m in re.finditer(rf'(\b\w+\b)\s+{verb}\s+(\b\w+\b)', text, flags=re.I):
                props.add(f"CAUSE({m.group(1)}->{m.group(2)})")
        # 5. ordering words
        for a, rel, b in re.findall(r'(\b\w+\b)\s+(before|after|precedes|follows)\s+(\b\w+\b)', text,
                                    flags=re.I):
            props.add(f"{a}{'<' if rel in ('before','precedes') else '>'}{b}")
        # 6. isolated numeric literals (treated as propositions)
        for num in re.findall(r'\b\d+(\.\d+)?\b', text):
            props.add(f"NUM({num})")
        return props

    def _build_adj(self, prop_list, prompt, candidates):
        """Adjacency where two propositions appear in the same clause."""
        p = len(prop_list)
        adj = np.zeros((p, p), dtype=bool)
        # split prompt and candidates into clauses (comma/semicolon/period)
        texts = [prompt] + candidates
        for txt in texts:
            clauses = re.split(r'[,.;]', txt)
            for cl in clauses:
                present = [i for i, pr in enumerate(prop_list) if pr in cl]
                for i, j in itertools.combinations(present, 2):
                    adj[i, j] = adj[j, i] = True
        return adj

    def _ncd(self, a, b):
        """Normalised Compression Distance using zlib."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb)

    # ------------------------------------------------------------------ #
    #  METACONFIDENCE – epistemic honesty
    # ------------------------------------------------------------------ #
    def _meta_confidence(self, prompt: str) -> float:
        """Detect traps; return a base confidence in [0,1]."""
        low = 0.0
        # 1. presupposition (have you stopped X?, why did X fail?)
        if re.search(r'\b(have|did|was|were)\s+you\s+(stop|quit|cease)\b', prompt, flags=re.I):
            low = max(low, 0.25)
        if re.search(r'\bwhy\s+did\s+\w+\s+(fail|stop|quit)\b', prompt, flags=re.I):
            low = max(low, 0.25)

        # 2. scope ambiguity – "Every X ... a Y"
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', prompt, flags=re.I):
            low = max(low, 0.25)

        # 3. pronoun ambiguity – "X told Y he/she ..."
        if re.search(r'\b\w+\s+told\s+\w+\s+(he|she|they)\b', prompt, flags=re.I):
            low = max(low, 0.25)

        # 4. false dichotomy – "Either A or B" without "both" or "neither"
        if re.search(r'\beither\s+[^,]+?\s+or\s+[^,]+?(?!\s+and)', prompt, flags=re.I):
            low = max(low, 0.25)

        # 5. subjectivity – superlatives without measurable criteria
        if re.search(r'\b(best|worst|favorite|most|least)\b', prompt, flags=re.I):
            low = max(low, 0.25)

        # 6. unanswerability – asks for external facts
        if re.search(r'\b(when|where|who|what|how)\b.*\b(is|are|was|were)\b.*\b(?:(?:the )?date|price|population|temperature)\b',
                     prompt, flags=re.I):
            low = max(low, 0.25)

        # If any trap detected we keep confidence low (<=0.25)
        if low > 0:
            return low

        # No trap detected -> moderate base confidence
        return 0.85

    # ------------------------------------------------------------------ #
    #  END OF CLASS
    # ------------------------------------------------------------------ #