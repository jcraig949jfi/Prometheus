"""Logical Consistency Checker — Symbolic reasoning via constraint propagation.

Hand-crafted reference implementation. Extracts structured facts from text
using regex patterns, builds a constraint graph, and checks for entailment,
contradiction, and compositional consistency.

Concepts: Proof Theory x Constraint Satisfaction x Compositional Semantics
"""

import re
import math
import numpy as np
from collections import defaultdict


class ReasoningTool:

    # --- Relation extraction patterns ---
    COMPARATIVE_PATTERNS = [
        # "X is larger/greater/more/taller/heavier than Y"
        (r"(\w[\w\s]*?)\s+(?:is|are)\s+(?:larger|greater|bigger|more|taller|heavier|faster|older|longer|higher)\s+than\s+(\w[\w\s]*?)(?:[.,;!?\s]|$)", ">"),
        # "X is smaller/less/shorter/lighter than Y"
        (r"(\w[\w\s]*?)\s+(?:is|are)\s+(?:smaller|less|fewer|shorter|lighter|slower|younger|lower)\s+than\s+(\w[\w\s]*?)(?:[.,;!?\s]|$)", "<"),
        # "X > Y" or "X < Y" (numeric)
        (r"([\d.]+)\s*(?:is\s+)?(?:less|smaller)\s+than\s+([\d.]+)", "<"),
        (r"([\d.]+)\s*(?:is\s+)?(?:greater|larger|more)\s+than\s+([\d.]+)", ">"),
    ]

    NEGATION_PATTERNS = [
        r"\bnot\s+(?:the\s+case\s+that\s+)?(.+?)(?:[.,;]|$)",
        r"\bnever\b\s+(.+?)(?:[.,;]|$)",
        r"\bno\s+(\w+)\s+(?:can|do|does|is|are)\b",
    ]

    CONDITIONAL_PATTERNS = [
        r"[Ii]f\s+(.+?),?\s+(?:then\s+)?(.+?)(?:[.,;]|$)",
    ]

    QUANTIFIER_PATTERNS = [
        (r"[Aa]ll\s+(\w+)\s+(?:are|is)\s+(\w+)", "FORALL"),
        (r"[Ss]ome\s+(\w+)\s+(?:are|is)\s+(\w+)", "EXISTS"),
        (r"[Nn]ot\s+all\s+(\w+)\s+(?:are|is)\s+(\w+)", "NOT_FORALL"),
    ]

    IDENTITY_PATTERNS = [
        r"(\w[\w\s]*?)\s+(?:is|are|equals?|=)\s+(?:a\s+|an\s+)?(\w[\w\s]*?)(?:[.,;!?\s]|$)",
    ]

    VERB_ACTION_PATTERNS = [
        # "X verbed Y" - extract agent, action, patient
        (r"[Tt]he\s+(\w+)\s+(chased|bit|hit|pushed|pulled|followed|caught|ate|saw)\s+the\s+(\w+)", "action"),
    ]

    def __init__(self):
        self.hedging_words = {"probably", "might", "maybe", "perhaps", "possibly",
                              "could", "likely", "unlikely", "uncertain"}

    def _extract_facts(self, text: str) -> list[tuple]:
        """Extract structured facts from natural language text."""
        facts = []
        text_lower = text.lower().strip()

        # Comparatives
        for pattern, rel in self.COMPARATIVE_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                a, b = m.group(1).strip(), m.group(2).strip()
                facts.append((a.lower(), rel, b.lower()))

        # Negations
        for pattern in self.NEGATION_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                facts.append(("NOT", m.group(1).strip().lower()))

        # Conditionals
        for pattern in self.CONDITIONAL_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                antecedent = m.group(1).strip().lower()
                consequent = m.group(2).strip().lower()
                facts.append((antecedent, "IMPLIES", consequent))

        # Quantifiers
        for pattern, qtype in self.QUANTIFIER_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                facts.append((qtype, m.group(1).lower(), m.group(2).lower()))

        # Identity/equality
        for pattern in self.IDENTITY_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                a, b = m.group(1).strip().lower(), m.group(2).strip().lower()
                if a != b and len(a) > 1 and len(b) > 1:
                    facts.append((a, "ISA", b))

        # Verb actions (compositional word order)
        for pattern, _ in self.VERB_ACTION_PATTERNS:
            for m in re.finditer(pattern, text):
                agent, verb, patient = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
                facts.append(("AGENT", agent, verb))
                facts.append(("PATIENT", patient, verb))

        return facts

    def _check_transitivity(self, facts: list[tuple]) -> tuple[int, int]:
        """Check transitive consistency. Returns (satisfied, violated)."""
        # Build ordering graph
        greater = defaultdict(set)  # a > b
        for fact in facts:
            if len(fact) == 3 and fact[1] == ">":
                greater[fact[0]].add(fact[2])
            elif len(fact) == 3 and fact[1] == "<":
                greater[fact[2]].add(fact[0])

        satisfied = 0
        violated = 0

        # Check: if a > b and b > c, then a > c should hold (or not a < c)
        for a in greater:
            for b in greater[a]:
                for c in greater.get(b, set()):
                    # a > b > c, so a > c
                    if c in greater.get(a, set()):
                        satisfied += 1
                    elif a in greater.get(c, set()):
                        violated += 1  # contradiction: a > c and c > a
                    else:
                        satisfied += 1  # no contradiction, just missing

        return satisfied, violated

    def _check_modus_ponens(self, facts: list[tuple]) -> tuple[int, int]:
        """Check modus ponens / modus tollens. Returns (satisfied, violated)."""
        implications = [(f[0], f[2]) for f in facts
                        if len(f) == 3 and f[1] == "IMPLIES"]
        asserted = set()
        negated = set()

        for f in facts:
            if len(f) == 2 and f[0] == "NOT":
                negated.add(f[1])
            elif len(f) >= 2 and f[0] not in ("NOT", "FORALL", "EXISTS", "NOT_FORALL",
                                                "AGENT", "PATIENT"):
                # Treat non-negated statements as asserted
                asserted.add(f[0] if len(f) == 2 else str(f))

        satisfied = 0
        violated = 0

        for antecedent, consequent in implications:
            # Modus ponens: P and P->Q, check Q not negated
            if antecedent in asserted:
                if consequent in negated:
                    violated += 1
                else:
                    satisfied += 1

            # Modus tollens: not-Q and P->Q, check not-P
            if consequent in negated:
                if antecedent in asserted:
                    violated += 1
                else:
                    satisfied += 1

        return satisfied, violated

    def _check_quantifier_consistency(self, facts: list[tuple]) -> tuple[int, int]:
        """Check quantifier logic. Returns (satisfied, violated)."""
        satisfied = 0
        violated = 0

        forall_claims = {}
        not_forall_claims = {}
        exists_claims = {}

        for f in facts:
            if len(f) == 3:
                if f[0] == "FORALL":
                    forall_claims[(f[1], f[2])] = True
                elif f[0] == "NOT_FORALL":
                    not_forall_claims[(f[1], f[2])] = True
                elif f[0] == "EXISTS":
                    exists_claims[(f[1], f[2])] = True

        # "all X are Y" contradicts "not all X are Y"
        for key in forall_claims:
            if key in not_forall_claims:
                violated += 1
            else:
                satisfied += 1

        # "all X are Y" entails "some X are Y"
        for key in forall_claims:
            if key in exists_claims:
                satisfied += 1

        return satisfied, violated

    def _hedging_score(self, text: str) -> float:
        """Measure hedging language. More hedging = lower confidence signal."""
        words = text.lower().split()
        if not words:
            return 0.0
        hedge_count = sum(1 for w in words if w in self.hedging_words)
        return hedge_count / len(words)

    def _score_candidate(self, prompt: str, candidate: str) -> tuple[float, str]:
        """Score a single candidate against the prompt constraints."""
        # Extract facts from both prompt and candidate
        prompt_facts = self._extract_facts(prompt)
        cand_facts = self._extract_facts(candidate)
        combined = prompt_facts + cand_facts

        if not combined:
            # No extractable structure — fall back to length parsimony
            parsimony = 1.0 / (1.0 + len(candidate))
            return 0.5 + parsimony * 0.1, "no_structure_extracted"

        # Check consistency constraints
        trans_sat, trans_viol = self._check_transitivity(combined)
        mp_sat, mp_viol = self._check_modus_ponens(combined)
        quant_sat, quant_viol = self._check_quantifier_consistency(combined)

        total_sat = trans_sat + mp_sat + quant_sat
        total_viol = trans_viol + mp_viol + quant_viol

        # Score: +1 per satisfaction, -2 per violation (asymmetric)
        raw_score = total_sat - 2 * total_viol
        total_constraints = total_sat + total_viol
        if total_constraints > 0:
            normalized = raw_score / (total_constraints * 2)  # scale to roughly [-1, 1]
        else:
            normalized = 0.0

        # Parsimony bonus: shorter answers with same constraint satisfaction
        parsimony = 1.0 / (1.0 + math.log1p(len(candidate)))

        # Hedging penalty in candidate
        hedge = self._hedging_score(candidate)

        score = 0.5 + normalized * 0.3 + parsimony * 0.1 - hedge * 0.1

        reasoning = (f"constraints={total_constraints} sat={total_sat} viol={total_viol} "
                     f"parsimony={parsimony:.3f} hedge={hedge:.3f}")
        return max(0.0, min(1.0, score)), reasoning

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by logical consistency with the prompt."""
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning,
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on constraint satisfaction."""
        score, _ = self._score_candidate(prompt, answer)
        return float(score)
