"""ToM + Liar Specialist — covers tom_information_asymmetry, tom_strategic_deception,
liar_detection.

Computation-first: constraint satisfaction for liar puzzles, perspective tracking
for theory of mind. NCD as tiebreaker only.
"""
import re
import zlib
from itertools import product

_NUM = re.compile(r'-?\d+(?:\.\d+)?')
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

    # --- Liar detection: constraint satisfaction ---
    def _solve_liar(self, prompt):
        pl = prompt.lower()
        # Pattern: "X says 'Y always lies.'" or "X says 'Y always tells the truth.'"
        # Multiple quote styles and phrasings
        claims = re.findall(
            r"(\w+)\s+says\s+['\"\u2018\u2019\u201c\u201d]?(\w+)\s+always\s+(lies|tells\s+the\s+truth)",
            pl, re.I
        )
        if len(claims) < 2:
            return None

        # Extract names in order
        names = []
        for claimant, target, claim_type in claims:
            c = claimant.capitalize()
            if c not in names:
                names.append(c)
        # Also add targets
        for claimant, target, claim_type in claims:
            t = target.capitalize()
            if t not in names:
                names.append(t)

        if len(names) < 2:
            return None

        # Brute-force constraint satisfaction
        # For each assignment of truth-teller (exactly one), check consistency
        for truth_teller_idx in range(len(names)):
            # Assume names[truth_teller_idx] tells truth, all others lie
            consistent = True
            for claimant, target, claim_type in claims:
                claimant_c = claimant.capitalize()
                target_c = target.capitalize()
                is_truth_teller = (claimant_c == names[truth_teller_idx])
                target_is_truthful = (target_c == names[truth_teller_idx])

                claim_says_lies = 'lies' in claim_type.lower()
                claim_says_truth = 'truth' in claim_type.lower()

                if is_truth_teller:
                    # This person tells truth, so their claim must be correct
                    if claim_says_lies and target_is_truthful:
                        consistent = False
                        break
                    if claim_says_truth and not target_is_truthful:
                        consistent = False
                        break
                else:
                    # This person lies, so their claim must be wrong
                    if claim_says_lies and not target_is_truthful:
                        consistent = False
                        break
                    if claim_says_truth and target_is_truthful:
                        consistent = False
                        break

            if consistent:
                return names[truth_teller_idx]

        return None

    # --- ToM: information asymmetry ---
    def _solve_info_asymmetry(self, prompt):
        pl = prompt.lower()
        # Pattern: "You know X is rigged to Y. [Name] has no idea / does not know."
        # Answer: the naive/fair expectation
        rigged = re.search(r'rigged|tampered|fixed|loaded', pl)
        uninformed = re.search(r'(\w+)\s+(?:has\s+no\s+idea|does\s+not\s+know|doesn\'t\s+know)', pl)
        if rigged and uninformed:
            # The uninformed person assigns the FAIR probability
            # Look for fair/default expectations in candidates
            return "fair_expectation"
        return None

    # --- ToM: strategic deception ---
    def _solve_strategic_deception(self, prompt):
        pl = prompt.lower()
        # Pattern: "X wants Y to do A. X knows Y always does the opposite."
        # Answer: X should say the opposite of A
        wants = re.search(r'(\w+)\s+wants\s+(\w+)\s+to\s+(\w[\w\s]*?)(?:\.|,)', pl)
        opposite = re.search(r'(?:always\s+does?\s+the\s+opposite|reliably\s+does?\s+the\s+opposite)', pl)

        if wants and opposite:
            desired_action = wants.group(3).strip().lower()
            # The correct answer is to say the OPPOSITE of the desired action
            return "say_opposite", desired_action
        return None, None

    def _compute_answer(self, prompt):
        # Liar detection
        result = self._solve_liar(prompt)
        if result:
            return ("liar", result), 0.90

        # Info asymmetry
        result = self._solve_info_asymmetry(prompt)
        if result:
            return ("info_asym", result), 0.80

        # Strategic deception
        tag, detail = self._solve_strategic_deception(prompt)
        if tag:
            return ("strategic", detail), 0.85

        return None, 0.0

    def evaluate(self, prompt, candidates):
        meta = self._meta_confidence(prompt)
        computed, comp_conf = self._compute_answer(prompt)

        results = []
        for cand in candidates:
            struct_score = 0.0
            cl = cand.lower().strip()

            if computed is not None:
                tag = computed[0]
                detail = computed[1]

                if tag == "liar":
                    # Match candidate to the truth-teller name
                    if cl == detail.lower():
                        struct_score = 1.0
                    elif detail.lower() in cl:
                        struct_score = 0.8
                    elif 'none' in cl:
                        struct_score = 0.1

                elif tag == "info_asym":
                    # The correct answer is the FAIR/naive expectation
                    # Fair answers contain: "1/6", "50%", "equal", "equally likely"
                    fair_markers = ['1/6', '50%', 'equal', 'any face', 'any color',
                                    '1/52', 'any specific', 'roughly equal']
                    rigged_markers = ['100%', 'always']
                    if any(m in cl for m in fair_markers):
                        struct_score = 1.0
                    elif any(m in cl for m in rigged_markers):
                        struct_score = 0.1
                    elif 'cannot' in cl:
                        struct_score = 0.2

                elif tag == "strategic":
                    # The correct answer says the OPPOSITE of the desired action
                    desired = detail  # what they actually want
                    # The answer should NOT contain the desired action directly
                    # It should contain the opposite
                    if desired in cl:
                        # Candidate mentions the desired action = WRONG
                        # (telling them to do what you want means they do opposite)
                        struct_score = 0.1
                    elif 'nothing' in cl or "doesn't matter" in cl or "does not matter" in cl:
                        struct_score = 0.15
                    else:
                        # This candidate says something OTHER than the desired action
                        # This is likely the correct "say the opposite" answer
                        struct_score = 0.8

            # NCD tiebreaker
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
        tag = computed[0]
        detail = computed[1]

        if tag == "liar":
            if al == detail.lower() or detail.lower() in al:
                return min(comp_conf, meta)
            return 0.20
        elif tag == "info_asym":
            fair_markers = ['1/6', '50%', 'equal', 'any face', 'any color',
                            '1/52', 'any specific', 'roughly equal']
            if any(m in al for m in fair_markers):
                return min(comp_conf, meta)
            return 0.20
        elif tag == "strategic":
            if detail in al:
                return 0.15  # says the desired action = wrong
            return min(comp_conf, meta)

        return 0.25
