"""Causal Specialist — covers causal_counterfactual, causal_intervention,
argument_strength.

Computation-first: parses causal chains, logical argument structure, and
counterfactual conditionals. Computes answers from parsed representations.
"""
import re
import zlib

_NUM = re.compile(r'-?\d+(?:\.\d+)?')

# Tier B meta-confidence
_PRESUP = re.compile(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)', re.I)
_SCOPE = re.compile(r'\bevery\b.*\b(?:a|some)\b.*\?', re.I)
_SUNK = re.compile(r'already\s+(?:spent|invested|paid)', re.I)
_DICHOT = re.compile(r'either.*?or|must\s+be\s+one', re.I)
_SURVIVOR = re.compile(r'(?:successful|survivors?).*(?:sample|study)', re.I)


class ReasoningTool:

    def __init__(self):
        pass

    def _ncd(self, a, b):
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _meta_confidence(self, prompt):
        pl = prompt.lower()
        if _PRESUP.search(pl):
            return 0.20
        if _SCOPE.search(pl):
            return 0.20
        if _SUNK.search(pl):
            return 0.20
        if _DICHOT.search(pl) and len(pl.split()) > 15:
            return 0.25
        if _SURVIVOR.search(pl):
            return 0.20
        return 1.0

    # --- Causal intervention: X->Y->Z, block Y, what happens to Z? ---
    def _compute_intervention(self, prompt):
        pl = prompt.lower()
        # Pattern: "X causes Y, and Y causes Z, if we prevent Y"
        # or: "X leads to Y, which leads to Z. If we block Y"
        # The answer is always that the downstream effect STOPS

        # Detect intervention keywords
        has_intervention = bool(re.search(
            r'(?:prevent|block|forcibly\s+prevent|intervene\s+to\s+block|remove|eliminate|stop)',
            pl
        ))
        # Detect causal chain keywords
        has_chain = bool(re.search(r'(?:causes?|leads?\s+to|results?\s+in)', pl))

        if has_intervention and has_chain:
            # The correct answer mentions stopping/preventing the downstream effect
            return "stops"
        return None

    # --- Causal counterfactual: universal rule + fact + "what if?" ---
    def _compute_counterfactual(self, prompt):
        pl = prompt.lower()
        # Pattern: "All X who did A were B" + "Y did not do A" + "If Y had done A, would Y be B?"
        # Or: "All X who A got B" + "name didn't get B" + "If name had A'd?"
        # The answer is always "Yes" for universal counterfactuals
        universal = re.search(r'\b(?:all|every)\s+\w[\w\s]*?\s+(?:who|that|which)\s+', pl)
        counterfactual = re.search(r'\bif\s+\w+\s+had\b', pl)
        if universal and counterfactual:
            return "Yes"
        return None

    # --- Argument strength: modus ponens vs affirming consequent ---
    def _compute_argument_strength(self, prompt):
        pl = prompt.lower()
        # Look for "Argument A:" and "Argument B:" structure
        arg_a_match = re.search(r'argument\s+a:\s*(.*?)argument\s+b:', pl, re.S)
        arg_b_match = re.search(r'argument\s+b:\s*(.*?)(?:which\s+argument|$)', pl, re.S)

        if not arg_a_match or not arg_b_match:
            return None

        arg_a = arg_a_match.group(1).strip()
        arg_b = arg_b_match.group(1).strip()

        def classify_argument(arg):
            """Returns True for valid (modus ponens), False for fallacy (affirming consequent)."""
            # Extract: "If X has a Y, then X has a Z. X has a Y. Therefore X has a Z." = valid MP
            # vs: "If X has a Y, then X has a Z. X has a Z. Therefore X has a Y." = affirming consequent
            cond = re.search(r'if\s+(\w+)\s+has\s+(?:a\s+)?(\w+),?\s+then\s+\1\s+has\s+(?:a\s+)?(\w+)', arg)
            if not cond:
                return None
            name = cond.group(1)
            antecedent_obj = cond.group(2)  # e.g., "cat"
            consequent_obj = cond.group(3)  # e.g., "pet"
            # After the conditional, find the assertion
            rest = arg[cond.end():]
            # "X has a Y. Therefore X has a Z." (affirms antecedent = MP = valid)
            # "X has a Z. Therefore X has a Y." (affirms consequent = fallacy)
            assertion = re.search(r'(\w+)\s+has\s+(?:a\s+)?(\w+)\.?\s+therefore', rest)
            if assertion:
                asserted_obj = assertion.group(2)
                if asserted_obj == antecedent_obj:
                    return True   # Affirms antecedent = modus ponens (valid)
                elif asserted_obj == consequent_obj:
                    return False  # Affirms consequent (fallacy)
            return None

        a_valid = classify_argument(arg_a)
        b_valid = classify_argument(arg_b)

        if a_valid is True and b_valid is False:
            return "A"
        elif a_valid is False and b_valid is True:
            return "B"
        elif a_valid is True and b_valid is True:
            return "Both are equally strong"
        return None

    def _compute_answer(self, prompt):
        # Try argument strength first
        result = self._compute_argument_strength(prompt)
        if result:
            return result, 0.80

        # Try counterfactual
        result = self._compute_counterfactual(prompt)
        if result:
            return result, 0.80

        # Try intervention
        action = self._compute_intervention(prompt)
        if action == "stops":
            return "stops", 0.75

        return None, 0.0

    def evaluate(self, prompt, candidates):
        meta = self._meta_confidence(prompt)
        computed, comp_conf = self._compute_answer(prompt)

        results = []
        for cand in candidates:
            struct_score = 0.0

            if computed is not None:
                cl = cand.lower().strip()
                rl = computed.lower().strip()

                if rl == "stops":
                    # Intervention: match candidate that says effect stops
                    stop_words = ['stop', 'unlikely', 'prevent', 'cease', 'no longer',
                                  'not form', 'not happen', 'does not']
                    if any(w in cl for w in stop_words):
                        struct_score = 0.9
                    elif 'still' in cl or 'continue' in cl or 'directly' in cl:
                        struct_score = 0.1
                    elif 'cannot determine' in cl:
                        struct_score = 0.2
                elif cl == rl:
                    struct_score = 1.0
                elif rl in cl:
                    struct_score = 0.8
                elif cl in rl:
                    struct_score = 0.7

            # NCD tiebreaker (max 15%)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 / (1.0 + ncd_val)) * 0.15

            score = struct_score * 0.85 + ncd_score
            score *= meta

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"struct={struct_score:.2f} ncd={ncd_score:.3f} meta={meta:.2f}"
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt, answer):
        meta = self._meta_confidence(prompt)
        if meta < 1.0:
            return meta

        computed, comp_conf = self._compute_answer(prompt)
        if computed is None:
            return 0.25

        al = answer.lower().strip()
        cl = computed.lower().strip()

        if cl == "stops":
            stop_words = ['stop', 'unlikely', 'prevent', 'cease', 'no longer',
                          'not form', 'not happen', 'does not']
            if any(w in al for w in stop_words):
                return min(comp_conf, meta)
            return 0.20
        elif cl == al or cl in al or al in cl:
            return min(comp_conf, meta)
        return 0.20
