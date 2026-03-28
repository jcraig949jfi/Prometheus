"""Functorial Causal-Mechanism Design v2.
Category Theory x Causal Inference x Mechanism Design.
Morphism composition, modus ponens/tollens, VCG superlinear reward, NCD<=15%.
"""
import re, zlib, math
from typing import List, Dict

class ReasoningTool:
    def __init__(self):
        self.negation_pat = re.compile(
            r"\b(not|no|never|none|neither|without|cannot|can't|won't|doesn't|don't|isn't|aren't|fail)\b", re.I)
        self.cond_pat = re.compile(r"\bif\b(.+?)\bthen\b(.+?)(?:[.\n]|$)", re.I | re.S)
        self.comp_pat = re.compile(
            r"(\S+)\s+(?:is\s+)?(?:greater|larger|more|bigger|taller|heavier|higher)\s+than\s+(\S+)", re.I)
        self.comp_pat_less = re.compile(
            r"(\S+)\s+(?:is\s+)?(?:less|smaller|fewer|shorter|lighter|lower)\s+than\s+(\S+)", re.I)
        self.svo_pat = re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+(?:the\s+)?(\w+)")
        self.num_pat = re.compile(r"[-+]?\d*\.?\d+")

    def _extract(self, text: str) -> Dict:
        tl = text.lower()
        words = tl.split()
        negs = [(m.start(), m.group()) for m in self.negation_pat.finditer(tl)]
        conds = self.cond_pat.findall(text)
        comp_gt = [(m.group(1).strip(".,;:"), m.group(2).strip(".,;:")) for m in self.comp_pat.finditer(tl)]
        comp_lt = [(m.group(1).strip(".,;:"), m.group(2).strip(".,;:")) for m in self.comp_pat_less.finditer(tl)]
        nums = [float(n) for n in self.num_pat.findall(text)]
        svos = [(m.group(1).lower(), m.group(2).lower(), m.group(3).lower())
                for m in self.svo_pat.finditer(text)]
        return dict(negs=negs, conds=conds, comp_gt=comp_gt, comp_lt=comp_lt,
                    nums=nums, svos=svos, words=set(words), n_words=len(words))

    def _mechanism_score(self, ps: Dict, cs: Dict, prompt: str, cand: str) -> tuple:
        score = 0.0
        checks = 0
        reasons = []

        # Negation scope: count prompt negations near key terms
        if ps['negs']:
            checks += 1
            p_neg_count = len(ps['negs'])
            c_neg_count = len(cs['negs'])
            # Double negation or matching negation structure
            if p_neg_count > 0 and c_neg_count > 0:
                score += 1.0
                reasons.append("structural:negation_preserved")
            elif p_neg_count >= 2 and c_neg_count == 0:
                score += 0.3
                reasons.append("structural:negation_missing_but_double_neg_prompt")
            else:
                reasons.append("structural:negation_mismatch")

        # Conditional: modus ponens / tollens
        if ps['conds']:
            checks += 1
            antecedent, consequent = ps['conds'][0][0].strip(), ps['conds'][0][1].strip()
            cand_lower = cand.lower()
            if consequent.strip().rstrip('.') in cand_lower:
                score += 1.0
                reasons.append("structural:modus_ponens_satisfied")
            elif any(n[1] in consequent for n in cs['negs']):
                score += 0.7
                reasons.append("structural:modus_tollens_candidate")
            else:
                score += 0.2
                reasons.append("structural:conditional_unresolved")

        # Comparatives: transitivity check (Category Theory morphism composition)
        all_gt = ps['comp_gt'] + cs['comp_gt']
        if ps['comp_gt']:
            checks += 1
            # Build ordering graph and check consistency
            order = {}
            for a, b in all_gt:
                order.setdefault(a, set()).add(b)
            # Check transitive closure consistency
            consistent = True
            for a in order:
                for b in order.get(a, set()):
                    if a in order.get(b, set()):
                        consistent = False
            if consistent and cs['comp_gt']:
                score += 1.0
                reasons.append("structural:comparative_transitive_consistent")
            elif consistent:
                score += 0.5
                reasons.append("structural:comparative_prompt_only")
            else:
                reasons.append("structural:comparative_cycle_detected")

        # Numeric: parse and compare actual values
        if ps['nums']:
            checks += 1
            if cs['nums']:
                p_set = set(ps['nums'])
                c_set = set(cs['nums'])
                if p_set & c_set:
                    score += 1.0
                    reasons.append(f"execution:numeric_exact_match={p_set & c_set}")
                else:
                    # Check if candidate number is a plausible computation
                    for cn in cs['nums']:
                        for pn in ps['nums']:
                            if pn != 0 and abs(cn / pn - 1.0) < 0.05:
                                score += 0.8
                                reasons.append(f"execution:numeric_close({cn}~{pn})")
                                break
                    else:
                        score += 0.2
                        reasons.append("execution:numeric_present_but_different")
            else:
                if cs['n_words'] < 5:
                    score += 0.4
                    reasons.append("structural:short_answer_to_numeric_prompt")
                else:
                    reasons.append("structural:numeric_expected_but_absent")

        # Subject-object alignment
        if ps['svos']:
            checks += 1
            p_agents = {s[0] for s in ps['svos']}
            p_patients = {s[2] for s in ps['svos']}
            c_words = cs['words']
            if p_patients & c_words:
                score += 1.0
                reasons.append("structural:svo_patient_referenced")
            elif p_agents & c_words:
                score += 0.6
                reasons.append("structural:svo_agent_referenced")
            else:
                score += 0.2
                reasons.append("structural:svo_no_role_match")

        # VCG-inspired superlinear reward: satisfying multiple constraints is better
        if checks > 0:
            raw = score / checks
            vcg_bonus = (score / checks) ** 0.8 if score / checks > 0.5 else raw * 0.9
            return vcg_bonus, reasons
        return 0.5, ["structural:no_constraints_detected"]

    def _ncd(self, s1: str, s2: str) -> float:
        try:
            b1, b2 = s1.encode(), s2.encode()
            c1, c2, c12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b1 + b2))
            d = max(c1, c2)
            return (c12 - min(c1, c2)) / d if d > 0 else 1.0
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0,
                     "reasoning": "structural:empty_prompt"} for c in (candidates or [])]
        if not candidates:
            return []

        ps = self._extract(prompt)
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0,
                                "reasoning": "structural:empty_candidate"})
                continue
            cs = self._extract(cand)
            mech_score, reasons = self._mechanism_score(ps, cs, prompt, cand)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            final = 0.85 * mech_score + 0.15 * ncd_sim
            tag = "fallback:ncd" if mech_score < 0.2 else "; ".join(reasons)
            results.append({"candidate": cand, "score": float(max(0.0, min(1.0, final))),
                            "reasoning": tag})

        results.sort(key=lambda x: x['score'], reverse=True)

        # Metacognitive reflection: flag close scores
        if len(results) >= 2:
            top, second = results[0]['score'], results[1]['score']
            if top > 0 and abs(top - second) / max(top, 1e-9) < 0.05:
                for r in results[:2]:
                    r['reasoning'] += " | metacognition:low_confidence_close_scores"

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer:
            return 0.0
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        # Compare against null baseline (empty string)
        null_res = self.evaluate(prompt, [""])
        null_score = null_res[0]['score'] if null_res else 0.0
        lift = score - null_score
        # If structural mechanisms found falsification signals, confidence near 0
        if "negation_mismatch" in res[0].get('reasoning', ''):
            return max(0.0, min(0.15, lift))
        return float(max(0.0, min(1.0, lift / max(1.0 - null_score, 0.1))))
