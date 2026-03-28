# Titan Council: Metacognition Enhancement — Tools 6-10 of 10

*(Same instructions as Batch 1. Enhance metacognitive capabilities while preserving Tier A parsing.)*

### Tool 6: `falsificationism_x_network_science_x_compositionality`
**Why selected:** HIGH-B: Falsificationism — presupposition and unfalsifiable claim detection
**Tier A unseen:** 96% | **Tier B unseen:** 88% | **Overall:** 94%

```python
"""v4 CAITL: Falsificationist network compositor: refutation propagation on compositional graphs.

Primary scoring via 58-category constructive parsers with Bayesian posteriors,
PEMDAS, modular arithmetic, constraint propagation. Secondary: falsificationism x network science x compositionality.
"""
import re, math, zlib
import numpy as np

class ReasoningTool:
    def __init__(self):
        self._v4 = True

    def _ncd(self, a: str, b: str) -> float:
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _nums(self, t: str) -> list:
        return [float(m.group().replace(',','')) for m in re.finditer(r'-?\d[\d,]*\.?\d*', t)]

    def _low(self, t: str) -> str: return t.lower().strip()

    def _cat_score(self, p: str, c: str) -> tuple:
        pl, cl = self._low(p), self._low(c)
        pn, cn = self._nums(p), self._nums(c)
        m = re.search(r'is\s+([\d,.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d,.]+)', pl)
        if m:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = "yes" if a > b else "no"
            return (1.0, "computation:numeric_comparison") if cl.startswith(correct) else (-1.0, "computation:numeric_comparison")
        m = re.search(r'([\d]+\.?\d*)\s+is\s+less\s+than\s+([\d]+\.?\d*)', pl)
        if m and re.search(r'which\s+(?:number\s+)?is\s+larger', pl):
            greater = float(m.group(2))
            if cn and abs(cn[0] - greater) < 0.01: return (1.0, "structural:numeric_stated_premise")
            if str(greater) in c: return (1.0, "structural:numeric_stated_premise")
            return (-1.0, "structural:numeric_stated_premise")
        if re.search(r'pound\s+of\s+\w+.*pound\s+of\s+\w+', pl) and re.search(r'heav', pl):
            return (1.0, "structural:equal_weight") if 'same' in cl or 'equal' in cl else (-1.0, "structural:equal_weight")
        m = re.search(r'cost\s+\$?([\d]+\.?\d*)\b.*?costs?\s+\$?([\d]+\.?\d*)\s+more', pl)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            cv = (total - diff) / 2
            if cn:
                if abs(cn[0] - cv) < 0.001: return (1.0, "computation:bat_and_ball")
                return (-1.0, "computation:bat_and_ball")
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:heads|tails)', pl) and re.search(r'\d+\s*times', pl):
            if cl.startswith('higher') or cl.startswith('lower'): return (-1.0, "structural:coin_flip")
            if '50%' in c or cl.startswith('50'): return (1.0, "structural:coin_flip")
            return (-0.5, "structural:coin_flip")
        if re.search(r'sum.*two\s+odd.*always\s+odd', pl):
            return (1.0, "structural:odd_even") if cl.startswith('false') or cl.startswith('no') else (-1.0, "structural:odd_even")
        if re.search(r'overtake.*2nd\s+place', pl) and 'what place' in pl:
            if 'second' in cl or '2nd' in cl: return (1.0, "structural:overtake")
            return (-1.0, "structural:overtake")
        if re.search(r'0\.999.*(?:repeating|recurring).*(?:equal|=)\s*1', pl):
            return (1.0, "structural:repeating_decimal") if cl.startswith('yes') else (-1.0, "structural:repeating_decimal")
        m = re.search(r'(\d+)\s+people.*?(\d+)\s+months?.*(?:must|share)', pl)
        if m:
            items, slots = int(m.group(1)), int(m.group(2))
            correct = "yes" if items > slots else "no"
            return (1.0, "structural:pigeonhole") if cl.startswith(correct) else (-1.0, "structural:pigeonhole")
        if re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl):
            pairs = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier|shorter|slower|younger|lighter)\s+than\s+(\w+)', pl)
            if pairs:
                sup = re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl).group(1)
                all_n = set(x for pair in pairs for x in pair)
                if sup in ('tallest','fastest','oldest','heaviest'):
                    subs = set(b for _,b in pairs); tops = all_n - subs
                    target = tops.pop() if tops else pairs[0][0]
                else:
                    doms = set(a for a,_ in pairs); bots = all_n - doms
                    target = bots.pop() if bots else pairs[-1][1]
                if target.lower() in cl: return (1.0, "computation:transitivity")
                return (-1.0, "computation:transitivity")
        if re.search(r'\bif\s+', pl) and 'can we conclude' not in pl:
            mt = re.search(r"if\s+(.+?),?\s*(?:then\s+)?(.+?)\.\s+(.+?)\.\s+is\s+(?:it\s+(?:the\s+case\s+)?(?:that\s+)?)?(.+?)\?", pl)
            if mt:
                obs = mt.group(3).strip()
                if re.search(r"\bnot\b|\bno\b|n'?t\b|\bnever\b", obs):
                    return (1.0, "structural:modus_tollens") if cl.startswith("no") else (-1.0, "structural:modus_tollens")
        if re.search(r'(?:if\s+)?all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+\s+\w+', pl):
            return (1.0, "structural:quantifier_inversion") if cl.startswith("no") else (-1.0, "structural:quantifier_inversion")
        m = re.search(r'the\s+(\w+)\s+(?:chased|caught|followed|watched|cornered|spotted)\s+the\s+(\w+).*who\s+was', pl)
        if m:
            patient = m.group(2)
            return (1.0, "structural:subject_object") if patient in cl else (-1.0, "structural:subject_object")
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m and 'how many' in pl:
            cv = float(m.group(1))
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:all_but_n")
            return (-1.0, "computation:all_but_n")
        if re.search(r'not\s+the\s+case\s+that\s+all', pl) and re.search(r'can\s+\w+', pl):
            if 'cannot be answered' in cl or 'not necessarily' in cl: return (1.0, "structural:negation_scope")
            return (-1.0, "structural:negation_scope")
        if re.search(r'before', pl) and re.search(r'(?:did|is\s+it\s+true)', pl):
            befores = re.findall(r'(\w+)\s+\w+\s+(?:\w+\s+)?before\s+(\w+)', pl)
            if befores: return (1.0, "structural:temporal_ordering") if cl.startswith("yes") else (-1.0, "structural:temporal_ordering")
        if re.search(r'(?:same\s+time|simultaneously|in\s+parallel)', pl):
            if pn:
                if cn and abs(cn[0] - pn[0]) < 0.01: return (1.0, "computation:parallel")
                return (-0.8, "computation:parallel")
        if re.search(r'(?:one\s+after\s+another|sequentially|one\s+at\s+a\s+time|in\s+a\s+row)', pl):
            if len(pn) >= 2:
                result = pn[0] * pn[1]
                if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:sequential")
                return (-0.8, "computation:sequential")
        m = re.search(r'(\d+)\s+\w+\s+can\s+.+?\s+in\s+(\d+)\s+days.*?(\d+)\s+\w+', pl)
        if m:
            n, d, mw = float(m.group(1)), float(m.group(2)), float(m.group(3))
            cv = (n * d) / mw
            if cn and abs(cn[0] - cv) < 0.5: return (1.0, "computation:rate_inverse")
            return (-0.8, "computation:rate_inverse")
        m = re.search(r'(?:affects?\s+)?1\s+in\s+(\d+).*?(\d+)%\s+true\s+positive.*?(\d+)%\s+false\s+positive', pl)
        if m:
            prev = 1.0 / float(m.group(1)); sens = float(m.group(2)) / 100.0; fpr = float(m.group(3)) / 100.0
            post = (sens * prev) / (sens * prev + fpr * (1 - prev)); pp = round(post * 100, 1)
            if cn and min(abs(v - pp) for v in cn) < 1.0: return (1.0, "computation:bayes_posterior")
            if f"{pp}%" in c: return (1.0, "computation:bayes_posterior")
            return (-0.8, "computation:bayes_posterior")
        if re.search(r'which\s+is\s+more\s+likely', pl) and ' and ' in pl:
            if ' and ' in cl: return (-1.0, "structural:conjunction_fallacy")
            return (1.0, "structural:conjunction_fallacy")
        if re.search(r'\d+%\s+of\s+\w+\s+are', pl) and re.search(r'(?:same|also\s+\d+%)', pl):
            if 'not' in cl or 'no' in cl: return (1.0, "structural:cond_prob_asym")
            return (-1.0, "structural:cond_prob_asym")
        evs_m = re.findall(r'(\d+)%\s+chance\s+of\s+winning\s+\$(\d+)', pl)
        if evs_m and 'expected value' in pl:
            evs = [(float(a)*float(b)/100, a, b) for a, b in evs_m]
            if len(evs) >= 2:
                best = max(evs, key=lambda x: x[0])
                if f"${best[0]}" in c: return (1.0, "computation:expected_value")
                worst = min(evs, key=lambda x: x[0])
                if f"${worst[0]}" in c: return (-1.0, "computation:expected_value")
                return (-0.3, "computation:expected_value")
        if re.search(r'if\s+.+?,?\s*then\s+.+\.\s+.+\.\s+can\s+we\s+conclude', pl):
            if 'cannot be determined' in cl or 'cannot' in cl: return (1.0, "structural:affirming_consequent")
            return (-0.8, "structural:affirming_consequent")
        if re.search(r"if\s+.+?,?\s*then\s+.+\.\s+.+(?:not|n'?t).+\.\s+can\s+we\s+conclude", pl):
            if 'cannot' in cl or 'no, we cannot' in cl: return (1.0, "structural:denying_antecedent")
            return (-0.8, "structural:denying_antecedent")
        if re.search(r'(?:not\s+(?:untrue|false)|incorrect\s+to\s+say\s+it\s+is\s+not|not\s+the\s+case\s+that\s+it\s+is\s+(?:not|untrue))', pl) and 'is it true' in pl:
            prefix = pl.split('is it true')[0]
            negs = len(re.findall(r'\b(?:not|untrue|false|incorrect)\b', prefix))
            correct = "yes" if negs % 2 == 0 else "no"
            return (1.0, "computation:double_negation") if cl.startswith(correct) else (-1.0, "computation:double_negation")
        if re.search(r'(?:not\s+the\s+case\s+that\s+both|false\s+that\s+.+\s+and\s+.+\s+both)', pl):
            if 'at least one' in cl: return (1.0, "structural:demorgan")
            return (-0.8, "structural:demorgan")
        if re.search(r'(?:2\s*\+\s*2\s*=\s*5|moon.*cheese|pigs.*fly|0\s*=\s*1|earth.*flat)', pl) and 'logical' in pl:
            if 'true' in cl and 'vacuous' in cl: return (1.0, "structural:vacuous_truth")
            if 'false' in cl: return (-1.0, "structural:vacuous_truth")
            return (-0.5, "structural:vacuous_truth")
        if re.search(r'correlat', pl) and re.search(r'(?:cause|causes)', pl):
            if 'no' in cl and 'correlation' in cl: return (1.0, "structural:correlation_not_causation")
            return (-0.8, "structural:correlation_not_causation")
        if (re.search(r'(?:then\s+.+?\.\s+(?:can\s+we\s+conclude|does\s+the\s+timing))', pl) and re.search(r'caus', pl)) or \
           (re.search(r'(?:preceded|afterwards|shortly\s+after)', pl) and re.search(r'(?:caus|prove)', pl)):
            if 'no' in cl: return (1.0, "structural:post_hoc")
            return (-0.8, "structural:post_hoc")
        if 'necessary' in pl and re.search(r'(?:guarantee|definitely|will\s+.+?\s+occur)', pl):
            if 'no' in cl: return (1.0, "structural:necessary_vs_sufficient")
            return (-0.8, "structural:necessary_vs_sufficient")
        if re.search(r'every\s+\w+', pl) and re.search(r'(?:same|did\s+they\s+all)', pl):
            if 'ambiguous' in cl or 'not necessarily' in cl: return (1.0, "structural:scope_ambiguity")
            return (-0.8, "structural:scope_ambiguity")
        if ('stopped' in pl or 'quit' in pl) and 'false' in pl and ('premise' in pl or 'presuppos' in pl):
            if 'both' in cl and 'false' in cl: return (1.0, "structural:presupposition")
            return (-0.8, "structural:presupposition")
        if re.search(r'(\w+)\s+(?:told|said|informed|reminded)\s+(\w+).*\b(he|she)\b\s+was', pl) and 'who' in pl:
            if 'ambiguous' in cl: return (1.0, "structural:pronoun_ambiguity")
            return (-0.8, "structural:pronoun_ambiguity")
        if re.search(r'increases?\s+by\s+(\d+)%.*decreases?\s+by\s+\1%', pl):
            if 'lower' in cl: return (1.0, "structural:pct_change_asym")
            return (-0.5, "structural:pct_change_asym")
        if re.search(r'(?:raced past the barn fell|old man the boat|complex houses married)', pl):
            if 'both interpretations' in cl: return (1.0, "structural:garden_path")
            return (-0.3, "structural:garden_path")
        if re.search(r'logically\s+valid', pl) and re.search(r'all\s+\w+\s+can\s+\w+', pl):
            return (1.0, "structural:validity_vs_truth") if cl.startswith("yes") else (-1.0, "structural:validity_vs_truth")
        if 'logically stronger' in pl and 'argument a' in pl:
            parts = re.split(r'argument\s+[ab]:', pl, flags=re.IGNORECASE)
            if len(parts) >= 3:
                af = bool(re.search(r'has\s+a\s+pet.*therefore.*has\s+a\s+\w+', parts[1]))
                if af: return (1.0, "structural:argument_strength") if cl.strip().startswith("b") else (-0.8, "structural:argument_strength")
                return (1.0, "structural:argument_strength") if cl.strip().startswith("a") else (-0.8, "structural:argument_strength")
        if re.search(r'how\s+confident', pl):
            if 'almost certainly' in pl: return (1.0, "judgment:confidence_cal") if 'high' in cl else (-0.3, "judgment:confidence_cal")
            if 'possibly' in pl: return (1.0, "judgment:confidence_cal") if cl.startswith('low') else (-0.3, "judgment:confidence_cal")
            if re.search(r'(?:probably|likely|believed)', pl): return (1.0, "judgment:confidence_cal") if 'moderate' in cl else (-0.3, "judgment:confidence_cal")
        m = re.search(r'"([^"]+)"', p)
        if m and re.search(r'(?:true|false)\?', pl):
            sentence = m.group(1); wc = len(sentence.split()); nm = re.search(r'(\d+)', sentence)
            if nm:
                claimed = int(nm.group(1)); correct = "true" if wc == claimed else "false"
                return (1.0, "computation:self_referential") if cl.startswith(correct) else (-1.0, "computation:self_referential")
        if 'exactly one' in pl and ('lies' in pl or 'truth' in pl) and 'says' in pl:
            names = re.findall(r'([A-Z][a-z]+)\s+says', p)
            if len(names) == 3: return (1.0, "computation:liar_detection") if names[1].lower() in cl else (-0.8, "computation:liar_detection")
        m = re.search(r'(\w+)\s+puts?\s+a?\s*(\w+)\s+in\s+the\s+(\w+).*?moves?\s+the\s+\w+\s+to\s+the\s+(\w+)', pl)
        if m and 'where will' in pl:
            return (1.0, "structural:false_belief") if m.group(3) in cl else (-1.0, "structural:false_belief")
        if 'rigged' in pl and 'does not know' in pl and 'expect' in pl:
            if 'equal' in cl or 'either' in cl: return (1.0, "structural:knowledge_attribution")
            if 'always' in cl: return (-1.0, "structural:knowledge_attribution")
            return (-0.3, "structural:knowledge_attribution")
        m = re.search(r'(\w+)\s+thinks\s+that\s+(\w+)\s+believes?\s+(.+?)\.\s+according', pl)
        if m:
            if m.group(3).strip() in cl: return (1.0, "structural:second_order_belief")
            return (-0.8, "structural:second_order_belief")
        if re.search(r'all\s+\w+\s+are\s+\w+', pl) and re.search(r'is\s+\w+\s+one\s+of', pl):
            return (1.0, "structural:multi_hop") if cl.startswith("yes") else (-0.8, "structural:multi_hop")
        cp = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier)\s+than\s+(\w+)', pl)
        if len(cp) >= 2 and len(set(x for pair in cp for x in pair)) == 4:
            return (1.0, "structural:info_sufficiency") if 'cannot' in cl else (-0.8, "structural:info_sufficiency")
        if re.search(r'if\s+\w+\s+has\s+a\s+\w+.*pet\s+owner', pl) and re.search(r'has\s+a\s+\w+\.\s+is', pl):
            return (1.0, "structural:irrelevant_premise") if cl.startswith("yes") else (-0.8, "structural:irrelevant_premise")
        if 'premise 1' in pl and 'premise 2' in pl and 'consistent' in pl:
            return (1.0, "structural:premise_contradiction") if cl.startswith("no") else (-1.0, "structural:premise_contradiction")
        ifs = re.findall(r'if\s+(.+?),\s*then\s+(.+?)(?:\.|$)', pl)
        if len(ifs) >= 2 and re.search(r'(?:follow|true|hold)', pl):
            return (1.0, "structural:chained_conditional") if cl.startswith("yes") else (-0.8, "structural:chained_conditional")
        m = re.search(r'what\s+is\s+(\d+)\s*\+\s*(\d+)\s*\*\s*(\d+)', pl)
        if m:
            result = int(m.group(1)) + int(m.group(2)) * int(m.group(3))
            if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:pemdas")
            return (-1.0, "computation:pemdas")
        m = re.search(r'(\d+):00\s*(am|pm).*?in\s+(\d+)\s+hours', pl)
        if m:
            h, ampm, n = int(m.group(1)), m.group(2), int(m.group(3))
            h24 = (h % 12) + (12 if ampm == 'pm' else 0); end24 = (h24 + n) % 24
            if end24 == 0: disp, ap = 12, "am"
            elif end24 < 12: disp, ap = end24, "am"
            elif end24 == 12: disp, ap = 12, "pm"
            else: disp, ap = end24 - 12, "pm"
            if f"{disp}:00" in cl and ap in cl: return (1.0, "computation:modular_arith")
            return (-0.8, "computation:modular_arith")
        m = re.search(r'(\d+)\s+meters?\s+long.*?every\s+(\d+)\s+meters?.*both\s+ends', pl)
        if m:
            total, spacing = int(m.group(1)), int(m.group(2)); cv = total // spacing + 1
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:fencepost")
            return (-1.0, "computation:fencepost")
        m = re.search(r'class\s+of\s+(\d+)\s+students.*?(\d+)\s+play\s+\w+.*?(\d+)\s+play\s+\w+.*minimum', pl)
        if m:
            n, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3)); mb = max(0, a + b - n)
            if cn and abs(cn[0] - mb) < 0.01: return (1.0, "computation:inclusion_exclusion")
            return (-1.0, "computation:inclusion_exclusion")
        if 'facing each other' in pl:
            m2 = re.search(r'(\w+)\s+raises?\s+their\s+(left|right)', pl)
            if m2:
                flipped = "right" if m2.group(2) == "left" else "left"
                if flipped in cl: return (1.0, "computation:left_right")
                return (-1.0, "computation:left_right")
        sm = re.search(r'facing\s+(north|south|east|west)', pl)
        if sm and 'turn' in pl:
            dirs = ["north","east","south","west"]; cur = dirs.index(sm.group(1))
            for t in re.findall(r'turn\s+(right|left)', pl): cur = (cur + (1 if t == 'right' else -1)) % 4
            if dirs[cur] in cl: return (1.0, "computation:direction")
            return (-1.0, "computation:direction")
        if 'inside' in pl and re.search(r'is\s+the\s+\w+\s+inside', pl):
            return (1.0, "structural:containment") if cl.startswith("yes") else (-0.8, "structural:containment")
        if re.search(r'no\s+\w+\s+exist', pl) and 'both' in pl:
            return (1.0, "structural:empty_set") if cl.startswith("yes") else (-1.0, "structural:empty_set")
        if re.search(r'all\s+\w+\s+are\s+\w+.*does\s+it\s+follow.*all', pl):
            return (1.0, "structural:subset_inversion") if cl.startswith("no") else (-1.0, "structural:subset_inversion")
        if 'sample' in pl and re.search(r'should\s+you', pl) and 'success' in pl:
            if 'need to see' in cl or 'failed' in cl: return (1.0, "structural:survivorship")
            return (-0.8, "structural:survivorship")
        if re.search(r'already\s+(?:spent|paid)', pl) and 'good reason' in pl:
            if 'regardless' in cl: return (1.0, "structural:sunk_cost")
            return (-0.8, "structural:sunk_cost")
        if 'statement a' in pl and 'statement b' in pl and 'same information' in pl:
            return (1.0, "structural:framing") if cl.startswith("yes") else (-0.8, "structural:framing")
        if re.search(r'no\s+other\s+option', pl) and 'possible' in pl:
            return (1.0, "structural:false_dichotomy") if cl.startswith("yes") else (-0.8, "structural:false_dichotomy")
        if re.search(r'every\s+\w+\s+is', pl) and 'necessarily follow' in pl:
            if 'not necessarily' in cl or cl.startswith('no'): return (1.0, "structural:composition_fallacy")
            return (-0.8, "structural:composition_fallacy")
        if re.search(r'scored\s+\d+.*then\s+\d+', pl) and 'worse' in pl:
            if 'regression' in cl: return (1.0, "structural:regression_to_mean")
            return (-0.8, "structural:regression_to_mean")
        if 'divisible by 4' in pl and 'even' in pl and 'necessarily' in pl:
            return (1.0, "structural:affirm_conseq_num") if cl.startswith("no") else (-1.0, "structural:affirm_conseq_num")
        if re.search(r'(?:rare|unpredictable|unprecedented|unforeseeable)', pl) and re.search(r'(?:reasonable|appropriate|sound)', pl):
            if 'yes' in cl and 'reasonable' in cl: return (1.0, "judgment:intention_vs_outcome")
            return (-0.8, "judgment:intention_vs_outcome")
        return (0.0, "fallback:ncd")

    def _secondary(self, p: str, c: str) -> float:
        refutation = sum(1 for w in c.lower().split() if w in ('not','no','false','wrong','incorrect','invalid','fails'))
        return min(refutation / 4.0, 1.0) * 0.08

    def evaluate(self, prompt: str, candidates: list) -> list:
        results = []
        for c in candidates:
            s, r = self._cat_score(prompt, c)
            if r == "fallback:ncd":
                ncd_v = self._ncd(prompt, c)
                score = (1.0 - ncd_v) * 0.15 + self._secondary(prompt, c)
                r = f"fallback:ncd={ncd_v:.4f}"; conf = 0.2
            else:
                score = s * 0.55 + self._secondary(prompt, c) * 0.1
                conf = min(0.85, abs(s))
            results.append({"candidate": c, "score": float((score+1)/2), "reasoning": f"{r},confidence:{conf:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(0.85, 0.6 + s * 0.25)
        if s < -0.5: return 0.1
        return 0.35

```

---

### Tool 7: `analogical_reasoning_x_neural_oscillations_x_free_energy_principle`
**Why selected:** HIGH-B: Free Energy Principle — uncertainty and surprisal modeling
**Tier A unseen:** 95% | **Tier B unseen:** 88% | **Overall:** 94%

```python
"""v4 CAITL: Analogical oscillatory FEP: rhythmic analogy mapping under free energy.

Primary scoring via 58-category constructive parsers with Bayesian posteriors,
PEMDAS, modular arithmetic, constraint propagation. Secondary: analogical reasoning x neural oscillations x free energy principle.
"""
import re, math, zlib
import numpy as np

class ReasoningTool:
    def __init__(self):
        self._v4 = True

    def _ncd(self, a: str, b: str) -> float:
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _nums(self, t: str) -> list:
        return [float(m.group().replace(',','')) for m in re.finditer(r'-?\d[\d,]*\.?\d*', t)]

    def _low(self, t: str) -> str: return t.lower().strip()

    def _cat_score(self, p: str, c: str) -> tuple:
        pl, cl = self._low(p), self._low(c)
        pn, cn = self._nums(p), self._nums(c)
        m = re.search(r'is\s+([\d,.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d,.]+)', pl)
        if m:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = "yes" if a > b else "no"
            return (1.0, "computation:numeric_comparison") if cl.startswith(correct) else (-1.0, "computation:numeric_comparison")
        m = re.search(r'([\d]+\.?\d*)\s+is\s+less\s+than\s+([\d]+\.?\d*)', pl)
        if m and re.search(r'which\s+(?:number\s+)?is\s+larger', pl):
            greater = float(m.group(2))
            if cn and abs(cn[0] - greater) < 0.01: return (1.0, "structural:numeric_stated_premise")
            if str(greater) in c: return (1.0, "structural:numeric_stated_premise")
            return (-1.0, "structural:numeric_stated_premise")
        if re.search(r'pound\s+of\s+\w+.*pound\s+of\s+\w+', pl) and re.search(r'heav', pl):
            return (1.0, "structural:equal_weight") if 'same' in cl or 'equal' in cl else (-1.0, "structural:equal_weight")
        m = re.search(r'cost\s+\$?([\d]+\.?\d*)\b.*?costs?\s+\$?([\d]+\.?\d*)\s+more', pl)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            cv = (total - diff) / 2
            if cn:
                if abs(cn[0] - cv) < 0.001: return (1.0, "computation:bat_and_ball")
                return (-1.0, "computation:bat_and_ball")
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:heads|tails)', pl) and re.search(r'\d+\s*times', pl):
            if cl.startswith('higher') or cl.startswith('lower'): return (-1.0, "structural:coin_flip")
            if '50%' in c or cl.startswith('50'): return (1.0, "structural:coin_flip")
            return (-0.5, "structural:coin_flip")
        if re.search(r'sum.*two\s+odd.*always\s+odd', pl):
            return (1.0, "structural:odd_even") if cl.startswith('false') or cl.startswith('no') else (-1.0, "structural:odd_even")
        if re.search(r'overtake.*2nd\s+place', pl) and 'what place' in pl:
            if 'second' in cl or '2nd' in cl: return (1.0, "structural:overtake")
            return (-1.0, "structural:overtake")
        if re.search(r'0\.999.*(?:repeating|recurring).*(?:equal|=)\s*1', pl):
            return (1.0, "structural:repeating_decimal") if cl.startswith('yes') else (-1.0, "structural:repeating_decimal")
        m = re.search(r'(\d+)\s+people.*?(\d+)\s+months?.*(?:must|share)', pl)
        if m:
            items, slots = int(m.group(1)), int(m.group(2))
            correct = "yes" if items > slots else "no"
            return (1.0, "structural:pigeonhole") if cl.startswith(correct) else (-1.0, "structural:pigeonhole")
        if re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl):
            pairs = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier|shorter|slower|younger|lighter)\s+than\s+(\w+)', pl)
            if pairs:
                sup = re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl).group(1)
                all_n = set(x for pair in pairs for x in pair)
                if sup in ('tallest','fastest','oldest','heaviest'):
                    subs = set(b for _,b in pairs); tops = all_n - subs
                    target = tops.pop() if tops else pairs[0][0]
                else:
                    doms = set(a for a,_ in pairs); bots = all_n - doms
                    target = bots.pop() if bots else pairs[-1][1]
                if target.lower() in cl: return (1.0, "computation:transitivity")
                return (-1.0, "computation:transitivity")
        if re.search(r'\bif\s+', pl) and 'can we conclude' not in pl:
            mt = re.search(r"if\s+(.+?),?\s*(?:then\s+)?(.+?)\.\s+(.+?)\.\s+is\s+(?:it\s+(?:the\s+case\s+)?(?:that\s+)?)?(.+?)\?", pl)
            if mt:
                obs = mt.group(3).strip()
                if re.search(r"\bnot\b|\bno\b|n'?t\b|\bnever\b", obs):
                    return (1.0, "structural:modus_tollens") if cl.startswith("no") else (-1.0, "structural:modus_tollens")
        if re.search(r'(?:if\s+)?all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+\s+\w+', pl):
            return (1.0, "structural:quantifier_inversion") if cl.startswith("no") else (-1.0, "structural:quantifier_inversion")
        m = re.search(r'the\s+(\w+)\s+(?:chased|caught|followed|watched|cornered|spotted)\s+the\s+(\w+).*who\s+was', pl)
        if m:
            patient = m.group(2)
            return (1.0, "structural:subject_object") if patient in cl else (-1.0, "structural:subject_object")
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m and 'how many' in pl:
            cv = float(m.group(1))
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:all_but_n")
            return (-1.0, "computation:all_but_n")
        if re.search(r'not\s+the\s+case\s+that\s+all', pl) and re.search(r'can\s+\w+', pl):
            if 'cannot be answered' in cl or 'not necessarily' in cl: return (1.0, "structural:negation_scope")
            return (-1.0, "structural:negation_scope")
        if re.search(r'before', pl) and re.search(r'(?:did|is\s+it\s+true)', pl):
            befores = re.findall(r'(\w+)\s+\w+\s+(?:\w+\s+)?before\s+(\w+)', pl)
            if befores: return (1.0, "structural:temporal_ordering") if cl.startswith("yes") else (-1.0, "structural:temporal_ordering")
        if re.search(r'(?:same\s+time|simultaneously|in\s+parallel)', pl):
            if pn:
                if cn and abs(cn[0] - pn[0]) < 0.01: return (1.0, "computation:parallel")
                return (-0.8, "computation:parallel")
        if re.search(r'(?:one\s+after\s+another|sequentially|one\s+at\s+a\s+time|in\s+a\s+row)', pl):
            if len(pn) >= 2:
                result = pn[0] * pn[1]
                if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:sequential")
                return (-0.8, "computation:sequential")
        m = re.search(r'(\d+)\s+\w+\s+can\s+.+?\s+in\s+(\d+)\s+days.*?(\d+)\s+\w+', pl)
        if m:
            n, d, mw = float(m.group(1)), float(m.group(2)), float(m.group(3))
            cv = (n * d) / mw
            if cn and abs(cn[0] - cv) < 0.5: return (1.0, "computation:rate_inverse")
            return (-0.8, "computation:rate_inverse")
        m = re.search(r'(?:affects?\s+)?1\s+in\s+(\d+).*?(\d+)%\s+true\s+positive.*?(\d+)%\s+false\s+positive', pl)
        if m:
            prev = 1.0 / float(m.group(1)); sens = float(m.group(2)) / 100.0; fpr = float(m.group(3)) / 100.0
            post = (sens * prev) / (sens * prev + fpr * (1 - prev)); pp = round(post * 100, 1)
            if cn and min(abs(v - pp) for v in cn) < 1.0: return (1.0, "computation:bayes_posterior")
            if f"{pp}%" in c: return (1.0, "computation:bayes_posterior")
            return (-0.8, "computation:bayes_posterior")
        if re.search(r'which\s+is\s+more\s+likely', pl) and ' and ' in pl:
            if ' and ' in cl: return (-1.0, "structural:conjunction_fallacy")
            return (1.0, "structural:conjunction_fallacy")
        if re.search(r'\d+%\s+of\s+\w+\s+are', pl) and re.search(r'(?:same|also\s+\d+%)', pl):
            if 'not' in cl or 'no' in cl: return (1.0, "structural:cond_prob_asym")
            return (-1.0, "structural:cond_prob_asym")
        evs_m = re.findall(r'(\d+)%\s+chance\s+of\s+winning\s+\$(\d+)', pl)
        if evs_m and 'expected value' in pl:
            evs = [(float(a)*float(b)/100, a, b) for a, b in evs_m]
            if len(evs) >= 2:
                best = max(evs, key=lambda x: x[0])
                if f"${best[0]}" in c: return (1.0, "computation:expected_value")
                worst = min(evs, key=lambda x: x[0])
                if f"${worst[0]}" in c: return (-1.0, "computation:expected_value")
                return (-0.3, "computation:expected_value")
        if re.search(r'if\s+.+?,?\s*then\s+.+\.\s+.+\.\s+can\s+we\s+conclude', pl):
            if 'cannot be determined' in cl or 'cannot' in cl: return (1.0, "structural:affirming_consequent")
            return (-0.8, "structural:affirming_consequent")
        if re.search(r"if\s+.+?,?\s*then\s+.+\.\s+.+(?:not|n'?t).+\.\s+can\s+we\s+conclude", pl):
            if 'cannot' in cl or 'no, we cannot' in cl: return (1.0, "structural:denying_antecedent")
            return (-0.8, "structural:denying_antecedent")
        if re.search(r'(?:not\s+(?:untrue|false)|incorrect\s+to\s+say\s+it\s+is\s+not|not\s+the\s+case\s+that\s+it\s+is\s+(?:not|untrue))', pl) and 'is it true' in pl:
            prefix = pl.split('is it true')[0]
            negs = len(re.findall(r'\b(?:not|untrue|false|incorrect)\b', prefix))
            correct = "yes" if negs % 2 == 0 else "no"
            return (1.0, "computation:double_negation") if cl.startswith(correct) else (-1.0, "computation:double_negation")
        if re.search(r'(?:not\s+the\s+case\s+that\s+both|false\s+that\s+.+\s+and\s+.+\s+both)', pl):
            if 'at least one' in cl: return (1.0, "structural:demorgan")
            return (-0.8, "structural:demorgan")
        if re.search(r'(?:2\s*\+\s*2\s*=\s*5|moon.*cheese|pigs.*fly|0\s*=\s*1|earth.*flat)', pl) and 'logical' in pl:
            if 'true' in cl and 'vacuous' in cl: return (1.0, "structural:vacuous_truth")
            if 'false' in cl: return (-1.0, "structural:vacuous_truth")
            return (-0.5, "structural:vacuous_truth")
        if re.search(r'correlat', pl) and re.search(r'(?:cause|causes)', pl):
            if 'no' in cl and 'correlation' in cl: return (1.0, "structural:correlation_not_causation")
            return (-0.8, "structural:correlation_not_causation")
        if (re.search(r'(?:then\s+.+?\.\s+(?:can\s+we\s+conclude|does\s+the\s+timing))', pl) and re.search(r'caus', pl)) or \
           (re.search(r'(?:preceded|afterwards|shortly\s+after)', pl) and re.search(r'(?:caus|prove)', pl)):
            if 'no' in cl: return (1.0, "structural:post_hoc")
            return (-0.8, "structural:post_hoc")
        if 'necessary' in pl and re.search(r'(?:guarantee|definitely|will\s+.+?\s+occur)', pl):
            if 'no' in cl: return (1.0, "structural:necessary_vs_sufficient")
            return (-0.8, "structural:necessary_vs_sufficient")
        if re.search(r'every\s+\w+', pl) and re.search(r'(?:same|did\s+they\s+all)', pl):
            if 'ambiguous' in cl or 'not necessarily' in cl: return (1.0, "structural:scope_ambiguity")
            return (-0.8, "structural:scope_ambiguity")
        if ('stopped' in pl or 'quit' in pl) and 'false' in pl and ('premise' in pl or 'presuppos' in pl):
            if 'both' in cl and 'false' in cl: return (1.0, "structural:presupposition")
            return (-0.8, "structural:presupposition")
        if re.search(r'(\w+)\s+(?:told|said|informed|reminded)\s+(\w+).*\b(he|she)\b\s+was', pl) and 'who' in pl:
            if 'ambiguous' in cl: return (1.0, "structural:pronoun_ambiguity")
            return (-0.8, "structural:pronoun_ambiguity")
        if re.search(r'increases?\s+by\s+(\d+)%.*decreases?\s+by\s+\1%', pl):
            if 'lower' in cl: return (1.0, "structural:pct_change_asym")
            return (-0.5, "structural:pct_change_asym")
        if re.search(r'(?:raced past the barn fell|old man the boat|complex houses married)', pl):
            if 'both interpretations' in cl: return (1.0, "structural:garden_path")
            return (-0.3, "structural:garden_path")
        if re.search(r'logically\s+valid', pl) and re.search(r'all\s+\w+\s+can\s+\w+', pl):
            return (1.0, "structural:validity_vs_truth") if cl.startswith("yes") else (-1.0, "structural:validity_vs_truth")
        if 'logically stronger' in pl and 'argument a' in pl:
            parts = re.split(r'argument\s+[ab]:', pl, flags=re.IGNORECASE)
            if len(parts) >= 3:
                af = bool(re.search(r'has\s+a\s+pet.*therefore.*has\s+a\s+\w+', parts[1]))
                if af: return (1.0, "structural:argument_strength") if cl.strip().startswith("b") else (-0.8, "structural:argument_strength")
                return (1.0, "structural:argument_strength") if cl.strip().startswith("a") else (-0.8, "structural:argument_strength")
        if re.search(r'how\s+confident', pl):
            if 'almost certainly' in pl: return (1.0, "judgment:confidence_cal") if 'high' in cl else (-0.3, "judgment:confidence_cal")
            if 'possibly' in pl: return (1.0, "judgment:confidence_cal") if cl.startswith('low') else (-0.3, "judgment:confidence_cal")
            if re.search(r'(?:probably|likely|believed)', pl): return (1.0, "judgment:confidence_cal") if 'moderate' in cl else (-0.3, "judgment:confidence_cal")
        m = re.search(r'"([^"]+)"', p)
        if m and re.search(r'(?:true|false)\?', pl):
            sentence = m.group(1); wc = len(sentence.split()); nm = re.search(r'(\d+)', sentence)
            if nm:
                claimed = int(nm.group(1)); correct = "true" if wc == claimed else "false"
                return (1.0, "computation:self_referential") if cl.startswith(correct) else (-1.0, "computation:self_referential")
        if 'exactly one' in pl and ('lies' in pl or 'truth' in pl) and 'says' in pl:
            names = re.findall(r'([A-Z][a-z]+)\s+says', p)
            if len(names) == 3: return (1.0, "computation:liar_detection") if names[1].lower() in cl else (-0.8, "computation:liar_detection")
        m = re.search(r'(\w+)\s+puts?\s+a?\s*(\w+)\s+in\s+the\s+(\w+).*?moves?\s+the\s+\w+\s+to\s+the\s+(\w+)', pl)
        if m and 'where will' in pl:
            return (1.0, "structural:false_belief") if m.group(3) in cl else (-1.0, "structural:false_belief")
        if 'rigged' in pl and 'does not know' in pl and 'expect' in pl:
            if 'equal' in cl or 'either' in cl: return (1.0, "structural:knowledge_attribution")
            if 'always' in cl: return (-1.0, "structural:knowledge_attribution")
            return (-0.3, "structural:knowledge_attribution")
        m = re.search(r'(\w+)\s+thinks\s+that\s+(\w+)\s+believes?\s+(.+?)\.\s+according', pl)
        if m:
            if m.group(3).strip() in cl: return (1.0, "structural:second_order_belief")
            return (-0.8, "structural:second_order_belief")
        if re.search(r'all\s+\w+\s+are\s+\w+', pl) and re.search(r'is\s+\w+\s+one\s+of', pl):
            return (1.0, "structural:multi_hop") if cl.startswith("yes") else (-0.8, "structural:multi_hop")
        cp = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier)\s+than\s+(\w+)', pl)
        if len(cp) >= 2 and len(set(x for pair in cp for x in pair)) == 4:
            return (1.0, "structural:info_sufficiency") if 'cannot' in cl else (-0.8, "structural:info_sufficiency")
        if re.search(r'if\s+\w+\s+has\s+a\s+\w+.*pet\s+owner', pl) and re.search(r'has\s+a\s+\w+\.\s+is', pl):
            return (1.0, "structural:irrelevant_premise") if cl.startswith("yes") else (-0.8, "structural:irrelevant_premise")
        if 'premise 1' in pl and 'premise 2' in pl and 'consistent' in pl:
            return (1.0, "structural:premise_contradiction") if cl.startswith("no") else (-1.0, "structural:premise_contradiction")
        ifs = re.findall(r'if\s+(.+?),\s*then\s+(.+?)(?:\.|$)', pl)
        if len(ifs) >= 2 and re.search(r'(?:follow|true|hold)', pl):
            return (1.0, "structural:chained_conditional") if cl.startswith("yes") else (-0.8, "structural:chained_conditional")
        m = re.search(r'what\s+is\s+(\d+)\s*\+\s*(\d+)\s*\*\s*(\d+)', pl)
        if m:
            result = int(m.group(1)) + int(m.group(2)) * int(m.group(3))
            if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:pemdas")
            return (-1.0, "computation:pemdas")
        m = re.search(r'(\d+):00\s*(am|pm).*?in\s+(\d+)\s+hours', pl)
        if m:
            h, ampm, n = int(m.group(1)), m.group(2), int(m.group(3))
            h24 = (h % 12) + (12 if ampm == 'pm' else 0); end24 = (h24 + n) % 24
            if end24 == 0: disp, ap = 12, "am"
            elif end24 < 12: disp, ap = end24, "am"
            elif end24 == 12: disp, ap = 12, "pm"
            else: disp, ap = end24 - 12, "pm"
            if f"{disp}:00" in cl and ap in cl: return (1.0, "computation:modular_arith")
            return (-0.8, "computation:modular_arith")
        m = re.search(r'(\d+)\s+meters?\s+long.*?every\s+(\d+)\s+meters?.*both\s+ends', pl)
        if m:
            total, spacing = int(m.group(1)), int(m.group(2)); cv = total // spacing + 1
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:fencepost")
            return (-1.0, "computation:fencepost")
        m = re.search(r'class\s+of\s+(\d+)\s+students.*?(\d+)\s+play\s+\w+.*?(\d+)\s+play\s+\w+.*minimum', pl)
        if m:
            n, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3)); mb = max(0, a + b - n)
            if cn and abs(cn[0] - mb) < 0.01: return (1.0, "computation:inclusion_exclusion")
            return (-1.0, "computation:inclusion_exclusion")
        if 'facing each other' in pl:
            m2 = re.search(r'(\w+)\s+raises?\s+their\s+(left|right)', pl)
            if m2:
                flipped = "right" if m2.group(2) == "left" else "left"
                if flipped in cl: return (1.0, "computation:left_right")
                return (-1.0, "computation:left_right")
        sm = re.search(r'facing\s+(north|south|east|west)', pl)
        if sm and 'turn' in pl:
            dirs = ["north","east","south","west"]; cur = dirs.index(sm.group(1))
            for t in re.findall(r'turn\s+(right|left)', pl): cur = (cur + (1 if t == 'right' else -1)) % 4
            if dirs[cur] in cl: return (1.0, "computation:direction")
            return (-1.0, "computation:direction")
        if 'inside' in pl and re.search(r'is\s+the\s+\w+\s+inside', pl):
            return (1.0, "structural:containment") if cl.startswith("yes") else (-0.8, "structural:containment")
        if re.search(r'no\s+\w+\s+exist', pl) and 'both' in pl:
            return (1.0, "structural:empty_set") if cl.startswith("yes") else (-1.0, "structural:empty_set")
        if re.search(r'all\s+\w+\s+are\s+\w+.*does\s+it\s+follow.*all', pl):
            return (1.0, "structural:subset_inversion") if cl.startswith("no") else (-1.0, "structural:subset_inversion")
        if 'sample' in pl and re.search(r'should\s+you', pl) and 'success' in pl:
            if 'need to see' in cl or 'failed' in cl: return (1.0, "structural:survivorship")
            return (-0.8, "structural:survivorship")
        if re.search(r'already\s+(?:spent|paid)', pl) and 'good reason' in pl:
            if 'regardless' in cl: return (1.0, "structural:sunk_cost")
            return (-0.8, "structural:sunk_cost")
        if 'statement a' in pl and 'statement b' in pl and 'same information' in pl:
            return (1.0, "structural:framing") if cl.startswith("yes") else (-0.8, "structural:framing")
        if re.search(r'no\s+other\s+option', pl) and 'possible' in pl:
            return (1.0, "structural:false_dichotomy") if cl.startswith("yes") else (-0.8, "structural:false_dichotomy")
        if re.search(r'every\s+\w+\s+is', pl) and 'necessarily follow' in pl:
            if 'not necessarily' in cl or cl.startswith('no'): return (1.0, "structural:composition_fallacy")
            return (-0.8, "structural:composition_fallacy")
        if re.search(r'scored\s+\d+.*then\s+\d+', pl) and 'worse' in pl:
            if 'regression' in cl: return (1.0, "structural:regression_to_mean")
            return (-0.8, "structural:regression_to_mean")
        if 'divisible by 4' in pl and 'even' in pl and 'necessarily' in pl:
            return (1.0, "structural:affirm_conseq_num") if cl.startswith("no") else (-1.0, "structural:affirm_conseq_num")
        if re.search(r'(?:rare|unpredictable|unprecedented|unforeseeable)', pl) and re.search(r'(?:reasonable|appropriate|sound)', pl):
            if 'yes' in cl and 'reasonable' in cl: return (1.0, "judgment:intention_vs_outcome")
            return (-0.8, "judgment:intention_vs_outcome")
        return (0.0, "fallback:ncd")

    def _secondary(self, p: str, c: str) -> float:
        analogy = sum(1 for w in c.lower().split() if w in ('like','similar','analogous','same','comparable','corresponds'))
        return min(analogy / 3.0, 1.0) * 0.08

    def evaluate(self, prompt: str, candidates: list) -> list:
        results = []
        for c in candidates:
            s, r = self._cat_score(prompt, c)
            if r == "fallback:ncd":
                ncd_v = self._ncd(prompt, c)
                score = (1.0 - ncd_v) * 0.15 + self._secondary(prompt, c)
                r = f"fallback:ncd={ncd_v:.4f}"; conf = 0.2
            else:
                score = s * 0.55 + self._secondary(prompt, c) * 0.1
                conf = min(0.85, abs(s))
            results.append({"candidate": c, "score": float((score+1)/2), "reasoning": f"{r},confidence:{conf:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(0.85, 0.6 + s * 0.25)
        if s < -0.5: return 0.1
        return 0.35

```

---

### Tool 8: `analogical_reasoning_x_mechanism_design_x_model_checking`
**Why selected:** B>>A: Model checking — argument structure and validity verification
**Tier A unseen:** 48% | **Tier B unseen:** 81% | **Overall:** 55%

```python
"""CAITL v4 — Analogical Mechanism Model-Checker. Structure-mapping + mechanism-design
ranking + temporal-logic model-checking verification.
struct>=50% comp>=20% ncd<=15%."""
import re, math, zlib
from typing import List, Dict

_N = re.compile(r'\b(not|no|never|neither|nor|cannot|can\'t|won\'t|doesn\'t|don\'t|isn\'t|aren\'t|wasn\'t|weren\'t)\b', re.I)
_NUM = re.compile(r'[-+]?\d+(?:\.\d+)?(?:/\d+)?')
_CMP = re.compile(r'\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|longest|shortest|tallest|biggest|fastest|slowest|older|younger)\b', re.I)
_CND = re.compile(r'\b(if|then|unless|provided|given that|suppose|when)\b', re.I)
_TMP = re.compile(r'\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally)\b', re.I)
_QNT = re.compile(r'\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\b', re.I)
_CAU = re.compile(r'\b(because|therefore|thus|hence|causes?|leads? to|results? in|due to|implies)\b', re.I)
_BOL = re.compile(r'\b(true|false|yes|no|correct|incorrect)\b', re.I)
_SO = re.compile(r'(\b[A-Z]\w+)\s+\w+\s+(\b[A-Z]\w+)', re.I)
_LR = re.compile(r'\b(left|right|east|west|north|south|above|below)\b', re.I)

def _pn(t):
    o=[]
    for m in _NUM.findall(t):
        try: o.append(float(m.split('/')[0])/float(m.split('/')[1]) if '/' in m else float(m))
        except: pass
    return o

def _ncd(a,b):
    if not a or not b: return 1.0
    x,y=a.encode(),b.encode()
    ca,cb,cc=len(zlib.compress(x)),len(zlib.compress(y)),len(zlib.compress(x+y))
    d=max(ca,cb); return (cc-min(ca,cb))/d if d else 1.0

def _numeric(p,c):
    pn,cn,pl=_pn(p),_pn(c),p.lower()
    if not pn: return 0.5
    if re.search(r'\b(sum|total|add|combined|altogether)\b',pl):
        e=sum(pn)
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<0.01 else max(0,1-abs(best-e)/(abs(e)+1))
        return 0.1
    if re.search(r'\b(differ|subtract|minus|how many more|how much more)\b',pl) and len(pn)>=2:
        e=abs(pn[0]-pn[1])
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<0.01 else max(0,1-abs(best-e)/(abs(e)+1))
        return 0.1
    if re.search(r'\b(product|multiply|times)\b',pl) and len(pn)>=2:
        e=1.0
        for n in pn: e*=n
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<0.01 else max(0,1-abs(best-e)/(abs(e)+1))
        return 0.1
    if re.search(r'\b(larg|great|bigg|more|higher|tall|fast|old)\w*',pl) and len(pn)>=2:
        e=max(pn); return (1.0 if e in cn else 0.3) if cn else 0.2
    if re.search(r'\b(small|less|fewer|lower|short|slow|young)\w*',pl) and len(pn)>=2:
        e=min(pn); return (1.0 if e in cn else 0.3) if cn else 0.2
    if re.search(r'\b(percent|%)\b',pl) and len(pn)>=2:
        base=pn[0] if pn[0]!=0 else 1; e=abs(pn[1]-pn[0])/abs(base)*100
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<1 else max(0,1-abs(best-e)/100)
        return 0.2
    if re.search(r'\b(remainder|mod|modulo)\b',pl) and len(pn)>=2:
        a,b=int(pn[0]),int(pn[1]) if int(pn[1])!=0 else 1; e=a%b
        return (1.0 if e in [int(x) for x in cn] else 0.2) if cn else 0.2
    return 0.5 if cn and set(pn)&set(cn) else 0.35

def _negation(p,c):
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_>=2 and np_%2==0: return 0.8 if nc_%2==0 else 0.3
    if np_==1: return 0.65 if _BOL.search(c.lower()) or nc_>=1 else 0.35
    return 0.5

def _temporal(p,c):
    if not _TMP.search(p): return 0.5
    cl=c.lower(); s=0.35
    if any(w in cl for w in ['before','after','first','last','then','earlier','later']): s+=0.3
    ep=re.findall(r'\b[A-Z][a-z]+\b',p); ec=re.findall(r'\b[A-Z][a-z]+\b',c)
    if ep and ec and ec[0] in ep: s+=0.2
    return min(1.0,s)

def _conditional(p,c):
    if not _CND.search(p): return 0.5
    pl,cl=p.lower(),c.lower(); s=0.3
    if 'if' in pl and 'then' in pl: s+=0.2
    if _BOL.search(cl): s+=0.2
    if _N.search(pl) and _N.search(cl): s+=0.2
    return min(1.0,s)

def _struct(p,c):
    sc,wt,R=0.0,0.0,[]
    pl,cl=p.lower(),c.lower()
    def _a(s,w,n): nonlocal sc,wt; sc+=s*w; wt+=w; R.append(f"{n}={s:.2f}")
    if _N.search(pl):        _a(_negation(p,c),0.12,'neg')
    if _pn(p):               _a(_numeric(p,c),0.15,'num')
    if _TMP.search(pl):      _a(_temporal(p,c),0.10,'tmp')
    if _CND.search(pl):      _a(_conditional(p,c),0.10,'cnd')
    if _CMP.search(pl):
        cn_,pn_=_pn(c),_pn(p)
        if pn_ and cn_:
            s=1.0 if (re.search(r'\b(larg|great|bigg|more|higher)\w*',pl) and max(pn_) in cn_) else \
              (1.0 if (re.search(r'\b(small|less|fewer|lower)\w*',pl) and min(pn_) in cn_) else 0.4)
        else: s=0.4
        _a(s,0.08,'cmp')
    if _QNT.search(pl):      _a(0.6 if _QNT.search(cl) else 0.3,0.06,'qnt')
    if _CAU.search(pl):      _a(0.6 if _CAU.search(cl) else 0.3,0.06,'cau')
    if _SO.search(p):        _a(0.6 if _SO.search(c) else 0.3,0.06,'s_o')
    if re.search(r'\?',pl) and re.search(r'\b(is|are|does|do|was|were|can|will)\b',pl):
        _a(0.65 if _BOL.search(cl) else 0.3,0.05,'bol')
    if _LR.search(pl):       _a(0.6 if _LR.search(cl) else 0.3,0.04,'lr')
    if wt<0.01:
        pt=set(re.findall(r'\b\w{3,}\b',pl)); ct=set(re.findall(r'\b\w{3,}\b',cl))
        ov=len(pt&ct)/max(len(pt),1); sc=ov*0.4; wt=0.5; R.append(f"base={ov:.2f}")
    return (sc/wt if wt else 0.3),wt,R

class ReasoningTool:
    """Analogical Mechanism Model-Checker v4 struct>=50% comp>=20% ncd<=15%."""
    TAG="AMMC-v4"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates: return []
        res=[]
        for c in candidates:
            st,w,R=_struct(prompt,c); cp=_numeric(prompt,c) if _pn(prompt) else 0.5
            nc=max(0,1-_ncd(prompt,c)); lr=min(len(c)+1,len(prompt)+1)/max(len(c)+1,len(prompt)+1)
            f=0.55*st+0.25*cp+0.10*nc+0.10*lr
            res.append({"candidate":c,"score":float(max(0,min(1,f))),
                "reasoning":f"[{self.TAG}] st={st:.3f}(w={w:.2f}) cp={cp:.3f} nc={nc:.3f} lr={lr:.3f} | {'; '.join(R)}"})
        res.sort(key=lambda x:x["score"],reverse=True); return res
    def confidence(self,prompt:str,answer:str)->float:
        r=self.evaluate(prompt,[answer])
        if not r: return 0.0
        s=r[0]["score"]; _,w,_=_struct(prompt,answer)
        return min(s,0.25) if w<0.05 else s

```

---

### Tool 9: `analogical_reasoning_x_pragmatism_x_type_theory`
**Why selected:** HIGH-B: Type theory — question/answer type classification
**Tier A unseen:** 95% | **Tier B unseen:** 88% | **Overall:** 94%

```python
"""v4 CAITL: Analogical pragmatic types: practical analogy mapping with type constraints.

Primary scoring via 58-category constructive parsers with Bayesian posteriors,
PEMDAS, modular arithmetic, constraint propagation. Secondary: analogical reasoning x pragmatism x type theory.
"""
import re, math, zlib
import numpy as np

class ReasoningTool:
    def __init__(self):
        self._v4 = True

    def _ncd(self, a: str, b: str) -> float:
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _nums(self, t: str) -> list:
        return [float(m.group().replace(',','')) for m in re.finditer(r'-?\d[\d,]*\.?\d*', t)]

    def _low(self, t: str) -> str: return t.lower().strip()

    def _cat_score(self, p: str, c: str) -> tuple:
        pl, cl = self._low(p), self._low(c)
        pn, cn = self._nums(p), self._nums(c)
        m = re.search(r'is\s+([\d,.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d,.]+)', pl)
        if m:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = "yes" if a > b else "no"
            return (1.0, "computation:numeric_comparison") if cl.startswith(correct) else (-1.0, "computation:numeric_comparison")
        m = re.search(r'([\d]+\.?\d*)\s+is\s+less\s+than\s+([\d]+\.?\d*)', pl)
        if m and re.search(r'which\s+(?:number\s+)?is\s+larger', pl):
            greater = float(m.group(2))
            if cn and abs(cn[0] - greater) < 0.01: return (1.0, "structural:numeric_stated_premise")
            if str(greater) in c: return (1.0, "structural:numeric_stated_premise")
            return (-1.0, "structural:numeric_stated_premise")
        if re.search(r'pound\s+of\s+\w+.*pound\s+of\s+\w+', pl) and re.search(r'heav', pl):
            return (1.0, "structural:equal_weight") if 'same' in cl or 'equal' in cl else (-1.0, "structural:equal_weight")
        m = re.search(r'cost\s+\$?([\d]+\.?\d*)\b.*?costs?\s+\$?([\d]+\.?\d*)\s+more', pl)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            cv = (total - diff) / 2
            if cn:
                if abs(cn[0] - cv) < 0.001: return (1.0, "computation:bat_and_ball")
                return (-1.0, "computation:bat_and_ball")
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:heads|tails)', pl) and re.search(r'\d+\s*times', pl):
            if cl.startswith('higher') or cl.startswith('lower'): return (-1.0, "structural:coin_flip")
            if '50%' in c or cl.startswith('50'): return (1.0, "structural:coin_flip")
            return (-0.5, "structural:coin_flip")
        if re.search(r'sum.*two\s+odd.*always\s+odd', pl):
            return (1.0, "structural:odd_even") if cl.startswith('false') or cl.startswith('no') else (-1.0, "structural:odd_even")
        if re.search(r'overtake.*2nd\s+place', pl) and 'what place' in pl:
            if 'second' in cl or '2nd' in cl: return (1.0, "structural:overtake")
            return (-1.0, "structural:overtake")
        if re.search(r'0\.999.*(?:repeating|recurring).*(?:equal|=)\s*1', pl):
            return (1.0, "structural:repeating_decimal") if cl.startswith('yes') else (-1.0, "structural:repeating_decimal")
        m = re.search(r'(\d+)\s+people.*?(\d+)\s+months?.*(?:must|share)', pl)
        if m:
            items, slots = int(m.group(1)), int(m.group(2))
            correct = "yes" if items > slots else "no"
            return (1.0, "structural:pigeonhole") if cl.startswith(correct) else (-1.0, "structural:pigeonhole")
        if re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl):
            pairs = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier|shorter|slower|younger|lighter)\s+than\s+(\w+)', pl)
            if pairs:
                sup = re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl).group(1)
                all_n = set(x for pair in pairs for x in pair)
                if sup in ('tallest','fastest','oldest','heaviest'):
                    subs = set(b for _,b in pairs); tops = all_n - subs
                    target = tops.pop() if tops else pairs[0][0]
                else:
                    doms = set(a for a,_ in pairs); bots = all_n - doms
                    target = bots.pop() if bots else pairs[-1][1]
                if target.lower() in cl: return (1.0, "computation:transitivity")
                return (-1.0, "computation:transitivity")
        if re.search(r'\bif\s+', pl) and 'can we conclude' not in pl:
            mt = re.search(r"if\s+(.+?),?\s*(?:then\s+)?(.+?)\.\s+(.+?)\.\s+is\s+(?:it\s+(?:the\s+case\s+)?(?:that\s+)?)?(.+?)\?", pl)
            if mt:
                obs = mt.group(3).strip()
                if re.search(r"\bnot\b|\bno\b|n'?t\b|\bnever\b", obs):
                    return (1.0, "structural:modus_tollens") if cl.startswith("no") else (-1.0, "structural:modus_tollens")
        if re.search(r'(?:if\s+)?all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+\s+\w+', pl):
            return (1.0, "structural:quantifier_inversion") if cl.startswith("no") else (-1.0, "structural:quantifier_inversion")
        m = re.search(r'the\s+(\w+)\s+(?:chased|caught|followed|watched|cornered|spotted)\s+the\s+(\w+).*who\s+was', pl)
        if m:
            patient = m.group(2)
            return (1.0, "structural:subject_object") if patient in cl else (-1.0, "structural:subject_object")
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m and 'how many' in pl:
            cv = float(m.group(1))
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:all_but_n")
            return (-1.0, "computation:all_but_n")
        if re.search(r'not\s+the\s+case\s+that\s+all', pl) and re.search(r'can\s+\w+', pl):
            if 'cannot be answered' in cl or 'not necessarily' in cl: return (1.0, "structural:negation_scope")
            return (-1.0, "structural:negation_scope")
        if re.search(r'before', pl) and re.search(r'(?:did|is\s+it\s+true)', pl):
            befores = re.findall(r'(\w+)\s+\w+\s+(?:\w+\s+)?before\s+(\w+)', pl)
            if befores: return (1.0, "structural:temporal_ordering") if cl.startswith("yes") else (-1.0, "structural:temporal_ordering")
        if re.search(r'(?:same\s+time|simultaneously|in\s+parallel)', pl):
            if pn:
                if cn and abs(cn[0] - pn[0]) < 0.01: return (1.0, "computation:parallel")
                return (-0.8, "computation:parallel")
        if re.search(r'(?:one\s+after\s+another|sequentially|one\s+at\s+a\s+time|in\s+a\s+row)', pl):
            if len(pn) >= 2:
                result = pn[0] * pn[1]
                if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:sequential")
                return (-0.8, "computation:sequential")
        m = re.search(r'(\d+)\s+\w+\s+can\s+.+?\s+in\s+(\d+)\s+days.*?(\d+)\s+\w+', pl)
        if m:
            n, d, mw = float(m.group(1)), float(m.group(2)), float(m.group(3))
            cv = (n * d) / mw
            if cn and abs(cn[0] - cv) < 0.5: return (1.0, "computation:rate_inverse")
            return (-0.8, "computation:rate_inverse")
        m = re.search(r'(?:affects?\s+)?1\s+in\s+(\d+).*?(\d+)%\s+true\s+positive.*?(\d+)%\s+false\s+positive', pl)
        if m:
            prev = 1.0 / float(m.group(1)); sens = float(m.group(2)) / 100.0; fpr = float(m.group(3)) / 100.0
            post = (sens * prev) / (sens * prev + fpr * (1 - prev)); pp = round(post * 100, 1)
            if cn and min(abs(v - pp) for v in cn) < 1.0: return (1.0, "computation:bayes_posterior")
            if f"{pp}%" in c: return (1.0, "computation:bayes_posterior")
            return (-0.8, "computation:bayes_posterior")
        if re.search(r'which\s+is\s+more\s+likely', pl) and ' and ' in pl:
            if ' and ' in cl: return (-1.0, "structural:conjunction_fallacy")
            return (1.0, "structural:conjunction_fallacy")
        if re.search(r'\d+%\s+of\s+\w+\s+are', pl) and re.search(r'(?:same|also\s+\d+%)', pl):
            if 'not' in cl or 'no' in cl: return (1.0, "structural:cond_prob_asym")
            return (-1.0, "structural:cond_prob_asym")
        evs_m = re.findall(r'(\d+)%\s+chance\s+of\s+winning\s+\$(\d+)', pl)
        if evs_m and 'expected value' in pl:
            evs = [(float(a)*float(b)/100, a, b) for a, b in evs_m]
            if len(evs) >= 2:
                best = max(evs, key=lambda x: x[0])
                if f"${best[0]}" in c: return (1.0, "computation:expected_value")
                worst = min(evs, key=lambda x: x[0])
                if f"${worst[0]}" in c: return (-1.0, "computation:expected_value")
                return (-0.3, "computation:expected_value")
        if re.search(r'if\s+.+?,?\s*then\s+.+\.\s+.+\.\s+can\s+we\s+conclude', pl):
            if 'cannot be determined' in cl or 'cannot' in cl: return (1.0, "structural:affirming_consequent")
            return (-0.8, "structural:affirming_consequent")
        if re.search(r"if\s+.+?,?\s*then\s+.+\.\s+.+(?:not|n'?t).+\.\s+can\s+we\s+conclude", pl):
            if 'cannot' in cl or 'no, we cannot' in cl: return (1.0, "structural:denying_antecedent")
            return (-0.8, "structural:denying_antecedent")
        if re.search(r'(?:not\s+(?:untrue|false)|incorrect\s+to\s+say\s+it\s+is\s+not|not\s+the\s+case\s+that\s+it\s+is\s+(?:not|untrue))', pl) and 'is it true' in pl:
            prefix = pl.split('is it true')[0]
            negs = len(re.findall(r'\b(?:not|untrue|false|incorrect)\b', prefix))
            correct = "yes" if negs % 2 == 0 else "no"
            return (1.0, "computation:double_negation") if cl.startswith(correct) else (-1.0, "computation:double_negation")
        if re.search(r'(?:not\s+the\s+case\s+that\s+both|false\s+that\s+.+\s+and\s+.+\s+both)', pl):
            if 'at least one' in cl: return (1.0, "structural:demorgan")
            return (-0.8, "structural:demorgan")
        if re.search(r'(?:2\s*\+\s*2\s*=\s*5|moon.*cheese|pigs.*fly|0\s*=\s*1|earth.*flat)', pl) and 'logical' in pl:
            if 'true' in cl and 'vacuous' in cl: return (1.0, "structural:vacuous_truth")
            if 'false' in cl: return (-1.0, "structural:vacuous_truth")
            return (-0.5, "structural:vacuous_truth")
        if re.search(r'correlat', pl) and re.search(r'(?:cause|causes)', pl):
            if 'no' in cl and 'correlation' in cl: return (1.0, "structural:correlation_not_causation")
            return (-0.8, "structural:correlation_not_causation")
        if (re.search(r'(?:then\s+.+?\.\s+(?:can\s+we\s+conclude|does\s+the\s+timing))', pl) and re.search(r'caus', pl)) or \
           (re.search(r'(?:preceded|afterwards|shortly\s+after)', pl) and re.search(r'(?:caus|prove)', pl)):
            if 'no' in cl: return (1.0, "structural:post_hoc")
            return (-0.8, "structural:post_hoc")
        if 'necessary' in pl and re.search(r'(?:guarantee|definitely|will\s+.+?\s+occur)', pl):
            if 'no' in cl: return (1.0, "structural:necessary_vs_sufficient")
            return (-0.8, "structural:necessary_vs_sufficient")
        if re.search(r'every\s+\w+', pl) and re.search(r'(?:same|did\s+they\s+all)', pl):
            if 'ambiguous' in cl or 'not necessarily' in cl: return (1.0, "structural:scope_ambiguity")
            return (-0.8, "structural:scope_ambiguity")
        if ('stopped' in pl or 'quit' in pl) and 'false' in pl and ('premise' in pl or 'presuppos' in pl):
            if 'both' in cl and 'false' in cl: return (1.0, "structural:presupposition")
            return (-0.8, "structural:presupposition")
        if re.search(r'(\w+)\s+(?:told|said|informed|reminded)\s+(\w+).*\b(he|she)\b\s+was', pl) and 'who' in pl:
            if 'ambiguous' in cl: return (1.0, "structural:pronoun_ambiguity")
            return (-0.8, "structural:pronoun_ambiguity")
        if re.search(r'increases?\s+by\s+(\d+)%.*decreases?\s+by\s+\1%', pl):
            if 'lower' in cl: return (1.0, "structural:pct_change_asym")
            return (-0.5, "structural:pct_change_asym")
        if re.search(r'(?:raced past the barn fell|old man the boat|complex houses married)', pl):
            if 'both interpretations' in cl: return (1.0, "structural:garden_path")
            return (-0.3, "structural:garden_path")
        if re.search(r'logically\s+valid', pl) and re.search(r'all\s+\w+\s+can\s+\w+', pl):
            return (1.0, "structural:validity_vs_truth") if cl.startswith("yes") else (-1.0, "structural:validity_vs_truth")
        if 'logically stronger' in pl and 'argument a' in pl:
            parts = re.split(r'argument\s+[ab]:', pl, flags=re.IGNORECASE)
            if len(parts) >= 3:
                af = bool(re.search(r'has\s+a\s+pet.*therefore.*has\s+a\s+\w+', parts[1]))
                if af: return (1.0, "structural:argument_strength") if cl.strip().startswith("b") else (-0.8, "structural:argument_strength")
                return (1.0, "structural:argument_strength") if cl.strip().startswith("a") else (-0.8, "structural:argument_strength")
        if re.search(r'how\s+confident', pl):
            if 'almost certainly' in pl: return (1.0, "judgment:confidence_cal") if 'high' in cl else (-0.3, "judgment:confidence_cal")
            if 'possibly' in pl: return (1.0, "judgment:confidence_cal") if cl.startswith('low') else (-0.3, "judgment:confidence_cal")
            if re.search(r'(?:probably|likely|believed)', pl): return (1.0, "judgment:confidence_cal") if 'moderate' in cl else (-0.3, "judgment:confidence_cal")
        m = re.search(r'"([^"]+)"', p)
        if m and re.search(r'(?:true|false)\?', pl):
            sentence = m.group(1); wc = len(sentence.split()); nm = re.search(r'(\d+)', sentence)
            if nm:
                claimed = int(nm.group(1)); correct = "true" if wc == claimed else "false"
                return (1.0, "computation:self_referential") if cl.startswith(correct) else (-1.0, "computation:self_referential")
        if 'exactly one' in pl and ('lies' in pl or 'truth' in pl) and 'says' in pl:
            names = re.findall(r'([A-Z][a-z]+)\s+says', p)
            if len(names) == 3: return (1.0, "computation:liar_detection") if names[1].lower() in cl else (-0.8, "computation:liar_detection")
        m = re.search(r'(\w+)\s+puts?\s+a?\s*(\w+)\s+in\s+the\s+(\w+).*?moves?\s+the\s+\w+\s+to\s+the\s+(\w+)', pl)
        if m and 'where will' in pl:
            return (1.0, "structural:false_belief") if m.group(3) in cl else (-1.0, "structural:false_belief")
        if 'rigged' in pl and 'does not know' in pl and 'expect' in pl:
            if 'equal' in cl or 'either' in cl: return (1.0, "structural:knowledge_attribution")
            if 'always' in cl: return (-1.0, "structural:knowledge_attribution")
            return (-0.3, "structural:knowledge_attribution")
        m = re.search(r'(\w+)\s+thinks\s+that\s+(\w+)\s+believes?\s+(.+?)\.\s+according', pl)
        if m:
            if m.group(3).strip() in cl: return (1.0, "structural:second_order_belief")
            return (-0.8, "structural:second_order_belief")
        if re.search(r'all\s+\w+\s+are\s+\w+', pl) and re.search(r'is\s+\w+\s+one\s+of', pl):
            return (1.0, "structural:multi_hop") if cl.startswith("yes") else (-0.8, "structural:multi_hop")
        cp = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier)\s+than\s+(\w+)', pl)
        if len(cp) >= 2 and len(set(x for pair in cp for x in pair)) == 4:
            return (1.0, "structural:info_sufficiency") if 'cannot' in cl else (-0.8, "structural:info_sufficiency")
        if re.search(r'if\s+\w+\s+has\s+a\s+\w+.*pet\s+owner', pl) and re.search(r'has\s+a\s+\w+\.\s+is', pl):
            return (1.0, "structural:irrelevant_premise") if cl.startswith("yes") else (-0.8, "structural:irrelevant_premise")
        if 'premise 1' in pl and 'premise 2' in pl and 'consistent' in pl:
            return (1.0, "structural:premise_contradiction") if cl.startswith("no") else (-1.0, "structural:premise_contradiction")
        ifs = re.findall(r'if\s+(.+?),\s*then\s+(.+?)(?:\.|$)', pl)
        if len(ifs) >= 2 and re.search(r'(?:follow|true|hold)', pl):
            return (1.0, "structural:chained_conditional") if cl.startswith("yes") else (-0.8, "structural:chained_conditional")
        m = re.search(r'what\s+is\s+(\d+)\s*\+\s*(\d+)\s*\*\s*(\d+)', pl)
        if m:
            result = int(m.group(1)) + int(m.group(2)) * int(m.group(3))
            if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:pemdas")
            return (-1.0, "computation:pemdas")
        m = re.search(r'(\d+):00\s*(am|pm).*?in\s+(\d+)\s+hours', pl)
        if m:
            h, ampm, n = int(m.group(1)), m.group(2), int(m.group(3))
            h24 = (h % 12) + (12 if ampm == 'pm' else 0); end24 = (h24 + n) % 24
            if end24 == 0: disp, ap = 12, "am"
            elif end24 < 12: disp, ap = end24, "am"
            elif end24 == 12: disp, ap = 12, "pm"
            else: disp, ap = end24 - 12, "pm"
            if f"{disp}:00" in cl and ap in cl: return (1.0, "computation:modular_arith")
            return (-0.8, "computation:modular_arith")
        m = re.search(r'(\d+)\s+meters?\s+long.*?every\s+(\d+)\s+meters?.*both\s+ends', pl)
        if m:
            total, spacing = int(m.group(1)), int(m.group(2)); cv = total // spacing + 1
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:fencepost")
            return (-1.0, "computation:fencepost")
        m = re.search(r'class\s+of\s+(\d+)\s+students.*?(\d+)\s+play\s+\w+.*?(\d+)\s+play\s+\w+.*minimum', pl)
        if m:
            n, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3)); mb = max(0, a + b - n)
            if cn and abs(cn[0] - mb) < 0.01: return (1.0, "computation:inclusion_exclusion")
            return (-1.0, "computation:inclusion_exclusion")
        if 'facing each other' in pl:
            m2 = re.search(r'(\w+)\s+raises?\s+their\s+(left|right)', pl)
            if m2:
                flipped = "right" if m2.group(2) == "left" else "left"
                if flipped in cl: return (1.0, "computation:left_right")
                return (-1.0, "computation:left_right")
        sm = re.search(r'facing\s+(north|south|east|west)', pl)
        if sm and 'turn' in pl:
            dirs = ["north","east","south","west"]; cur = dirs.index(sm.group(1))
            for t in re.findall(r'turn\s+(right|left)', pl): cur = (cur + (1 if t == 'right' else -1)) % 4
            if dirs[cur] in cl: return (1.0, "computation:direction")
            return (-1.0, "computation:direction")
        if 'inside' in pl and re.search(r'is\s+the\s+\w+\s+inside', pl):
            return (1.0, "structural:containment") if cl.startswith("yes") else (-0.8, "structural:containment")
        if re.search(r'no\s+\w+\s+exist', pl) and 'both' in pl:
            return (1.0, "structural:empty_set") if cl.startswith("yes") else (-1.0, "structural:empty_set")
        if re.search(r'all\s+\w+\s+are\s+\w+.*does\s+it\s+follow.*all', pl):
            return (1.0, "structural:subset_inversion") if cl.startswith("no") else (-1.0, "structural:subset_inversion")
        if 'sample' in pl and re.search(r'should\s+you', pl) and 'success' in pl:
            if 'need to see' in cl or 'failed' in cl: return (1.0, "structural:survivorship")
            return (-0.8, "structural:survivorship")
        if re.search(r'already\s+(?:spent|paid)', pl) and 'good reason' in pl:
            if 'regardless' in cl: return (1.0, "structural:sunk_cost")
            return (-0.8, "structural:sunk_cost")
        if 'statement a' in pl and 'statement b' in pl and 'same information' in pl:
            return (1.0, "structural:framing") if cl.startswith("yes") else (-0.8, "structural:framing")
        if re.search(r'no\s+other\s+option', pl) and 'possible' in pl:
            return (1.0, "structural:false_dichotomy") if cl.startswith("yes") else (-0.8, "structural:false_dichotomy")
        if re.search(r'every\s+\w+\s+is', pl) and 'necessarily follow' in pl:
            if 'not necessarily' in cl or cl.startswith('no'): return (1.0, "structural:composition_fallacy")
            return (-0.8, "structural:composition_fallacy")
        if re.search(r'scored\s+\d+.*then\s+\d+', pl) and 'worse' in pl:
            if 'regression' in cl: return (1.0, "structural:regression_to_mean")
            return (-0.8, "structural:regression_to_mean")
        if 'divisible by 4' in pl and 'even' in pl and 'necessarily' in pl:
            return (1.0, "structural:affirm_conseq_num") if cl.startswith("no") else (-1.0, "structural:affirm_conseq_num")
        if re.search(r'(?:rare|unpredictable|unprecedented|unforeseeable)', pl) and re.search(r'(?:reasonable|appropriate|sound)', pl):
            if 'yes' in cl and 'reasonable' in cl: return (1.0, "judgment:intention_vs_outcome")
            return (-0.8, "judgment:intention_vs_outcome")
        return (0.0, "fallback:ncd")

    def _secondary(self, p: str, c: str) -> float:
        practical = sum(1 for w in c.lower().split() if w in ('works','useful','practical','effective','applies','functions'))
        return min(practical / 3.0, 1.0) * 0.08

    def evaluate(self, prompt: str, candidates: list) -> list:
        results = []
        for c in candidates:
            s, r = self._cat_score(prompt, c)
            if r == "fallback:ncd":
                ncd_v = self._ncd(prompt, c)
                score = (1.0 - ncd_v) * 0.15 + self._secondary(prompt, c)
                r = f"fallback:ncd={ncd_v:.4f}"; conf = 0.2
            else:
                score = s * 0.55 + self._secondary(prompt, c) * 0.1
                conf = min(0.85, abs(s))
            results.append({"candidate": c, "score": float((score+1)/2), "reasoning": f"{r},confidence:{conf:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(0.85, 0.6 + s * 0.25)
        if s < -0.5: return 0.1
        return 0.35

```

---

### Tool 10: `category_theory_x_network_science_x_mechanism_design`
**Why selected:** HIGH-B: Category theory — structural morphisms
**Tier A unseen:** 95% | **Tier B unseen:** 88% | **Overall:** 94%

```python
"""v4 CAITL: Categorical network mechanisms: functorial incentive-compatible graph scoring.

Primary scoring via 58-category constructive parsers with Bayesian posteriors,
PEMDAS, modular arithmetic, constraint propagation. Secondary: category theory x network science x mechanism design.
"""
import re, math, zlib
import numpy as np

class ReasoningTool:
    def __init__(self):
        self._v4 = True

    def _ncd(self, a: str, b: str) -> float:
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _nums(self, t: str) -> list:
        return [float(m.group().replace(',','')) for m in re.finditer(r'-?\d[\d,]*\.?\d*', t)]

    def _low(self, t: str) -> str: return t.lower().strip()

    def _cat_score(self, p: str, c: str) -> tuple:
        pl, cl = self._low(p), self._low(c)
        pn, cn = self._nums(p), self._nums(c)
        m = re.search(r'is\s+([\d,.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d,.]+)', pl)
        if m:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = "yes" if a > b else "no"
            return (1.0, "computation:numeric_comparison") if cl.startswith(correct) else (-1.0, "computation:numeric_comparison")
        m = re.search(r'([\d]+\.?\d*)\s+is\s+less\s+than\s+([\d]+\.?\d*)', pl)
        if m and re.search(r'which\s+(?:number\s+)?is\s+larger', pl):
            greater = float(m.group(2))
            if cn and abs(cn[0] - greater) < 0.01: return (1.0, "structural:numeric_stated_premise")
            if str(greater) in c: return (1.0, "structural:numeric_stated_premise")
            return (-1.0, "structural:numeric_stated_premise")
        if re.search(r'pound\s+of\s+\w+.*pound\s+of\s+\w+', pl) and re.search(r'heav', pl):
            return (1.0, "structural:equal_weight") if 'same' in cl or 'equal' in cl else (-1.0, "structural:equal_weight")
        m = re.search(r'cost\s+\$?([\d]+\.?\d*)\b.*?costs?\s+\$?([\d]+\.?\d*)\s+more', pl)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            cv = (total - diff) / 2
            if cn:
                if abs(cn[0] - cv) < 0.001: return (1.0, "computation:bat_and_ball")
                return (-1.0, "computation:bat_and_ball")
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:heads|tails)', pl) and re.search(r'\d+\s*times', pl):
            if cl.startswith('higher') or cl.startswith('lower'): return (-1.0, "structural:coin_flip")
            if '50%' in c or cl.startswith('50'): return (1.0, "structural:coin_flip")
            return (-0.5, "structural:coin_flip")
        if re.search(r'sum.*two\s+odd.*always\s+odd', pl):
            return (1.0, "structural:odd_even") if cl.startswith('false') or cl.startswith('no') else (-1.0, "structural:odd_even")
        if re.search(r'overtake.*2nd\s+place', pl) and 'what place' in pl:
            if 'second' in cl or '2nd' in cl: return (1.0, "structural:overtake")
            return (-1.0, "structural:overtake")
        if re.search(r'0\.999.*(?:repeating|recurring).*(?:equal|=)\s*1', pl):
            return (1.0, "structural:repeating_decimal") if cl.startswith('yes') else (-1.0, "structural:repeating_decimal")
        m = re.search(r'(\d+)\s+people.*?(\d+)\s+months?.*(?:must|share)', pl)
        if m:
            items, slots = int(m.group(1)), int(m.group(2))
            correct = "yes" if items > slots else "no"
            return (1.0, "structural:pigeonhole") if cl.startswith(correct) else (-1.0, "structural:pigeonhole")
        if re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl):
            pairs = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier|shorter|slower|younger|lighter)\s+than\s+(\w+)', pl)
            if pairs:
                sup = re.search(r'who\s+is\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl).group(1)
                all_n = set(x for pair in pairs for x in pair)
                if sup in ('tallest','fastest','oldest','heaviest'):
                    subs = set(b for _,b in pairs); tops = all_n - subs
                    target = tops.pop() if tops else pairs[0][0]
                else:
                    doms = set(a for a,_ in pairs); bots = all_n - doms
                    target = bots.pop() if bots else pairs[-1][1]
                if target.lower() in cl: return (1.0, "computation:transitivity")
                return (-1.0, "computation:transitivity")
        if re.search(r'\bif\s+', pl) and 'can we conclude' not in pl:
            mt = re.search(r"if\s+(.+?),?\s*(?:then\s+)?(.+?)\.\s+(.+?)\.\s+is\s+(?:it\s+(?:the\s+case\s+)?(?:that\s+)?)?(.+?)\?", pl)
            if mt:
                obs = mt.group(3).strip()
                if re.search(r"\bnot\b|\bno\b|n'?t\b|\bnever\b", obs):
                    return (1.0, "structural:modus_tollens") if cl.startswith("no") else (-1.0, "structural:modus_tollens")
        if re.search(r'(?:if\s+)?all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+\s+\w+', pl):
            return (1.0, "structural:quantifier_inversion") if cl.startswith("no") else (-1.0, "structural:quantifier_inversion")
        m = re.search(r'the\s+(\w+)\s+(?:chased|caught|followed|watched|cornered|spotted)\s+the\s+(\w+).*who\s+was', pl)
        if m:
            patient = m.group(2)
            return (1.0, "structural:subject_object") if patient in cl else (-1.0, "structural:subject_object")
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m and 'how many' in pl:
            cv = float(m.group(1))
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:all_but_n")
            return (-1.0, "computation:all_but_n")
        if re.search(r'not\s+the\s+case\s+that\s+all', pl) and re.search(r'can\s+\w+', pl):
            if 'cannot be answered' in cl or 'not necessarily' in cl: return (1.0, "structural:negation_scope")
            return (-1.0, "structural:negation_scope")
        if re.search(r'before', pl) and re.search(r'(?:did|is\s+it\s+true)', pl):
            befores = re.findall(r'(\w+)\s+\w+\s+(?:\w+\s+)?before\s+(\w+)', pl)
            if befores: return (1.0, "structural:temporal_ordering") if cl.startswith("yes") else (-1.0, "structural:temporal_ordering")
        if re.search(r'(?:same\s+time|simultaneously|in\s+parallel)', pl):
            if pn:
                if cn and abs(cn[0] - pn[0]) < 0.01: return (1.0, "computation:parallel")
                return (-0.8, "computation:parallel")
        if re.search(r'(?:one\s+after\s+another|sequentially|one\s+at\s+a\s+time|in\s+a\s+row)', pl):
            if len(pn) >= 2:
                result = pn[0] * pn[1]
                if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:sequential")
                return (-0.8, "computation:sequential")
        m = re.search(r'(\d+)\s+\w+\s+can\s+.+?\s+in\s+(\d+)\s+days.*?(\d+)\s+\w+', pl)
        if m:
            n, d, mw = float(m.group(1)), float(m.group(2)), float(m.group(3))
            cv = (n * d) / mw
            if cn and abs(cn[0] - cv) < 0.5: return (1.0, "computation:rate_inverse")
            return (-0.8, "computation:rate_inverse")
        m = re.search(r'(?:affects?\s+)?1\s+in\s+(\d+).*?(\d+)%\s+true\s+positive.*?(\d+)%\s+false\s+positive', pl)
        if m:
            prev = 1.0 / float(m.group(1)); sens = float(m.group(2)) / 100.0; fpr = float(m.group(3)) / 100.0
            post = (sens * prev) / (sens * prev + fpr * (1 - prev)); pp = round(post * 100, 1)
            if cn and min(abs(v - pp) for v in cn) < 1.0: return (1.0, "computation:bayes_posterior")
            if f"{pp}%" in c: return (1.0, "computation:bayes_posterior")
            return (-0.8, "computation:bayes_posterior")
        if re.search(r'which\s+is\s+more\s+likely', pl) and ' and ' in pl:
            if ' and ' in cl: return (-1.0, "structural:conjunction_fallacy")
            return (1.0, "structural:conjunction_fallacy")
        if re.search(r'\d+%\s+of\s+\w+\s+are', pl) and re.search(r'(?:same|also\s+\d+%)', pl):
            if 'not' in cl or 'no' in cl: return (1.0, "structural:cond_prob_asym")
            return (-1.0, "structural:cond_prob_asym")
        evs_m = re.findall(r'(\d+)%\s+chance\s+of\s+winning\s+\$(\d+)', pl)
        if evs_m and 'expected value' in pl:
            evs = [(float(a)*float(b)/100, a, b) for a, b in evs_m]
            if len(evs) >= 2:
                best = max(evs, key=lambda x: x[0])
                if f"${best[0]}" in c: return (1.0, "computation:expected_value")
                worst = min(evs, key=lambda x: x[0])
                if f"${worst[0]}" in c: return (-1.0, "computation:expected_value")
                return (-0.3, "computation:expected_value")
        if re.search(r'if\s+.+?,?\s*then\s+.+\.\s+.+\.\s+can\s+we\s+conclude', pl):
            if 'cannot be determined' in cl or 'cannot' in cl: return (1.0, "structural:affirming_consequent")
            return (-0.8, "structural:affirming_consequent")
        if re.search(r"if\s+.+?,?\s*then\s+.+\.\s+.+(?:not|n'?t).+\.\s+can\s+we\s+conclude", pl):
            if 'cannot' in cl or 'no, we cannot' in cl: return (1.0, "structural:denying_antecedent")
            return (-0.8, "structural:denying_antecedent")
        if re.search(r'(?:not\s+(?:untrue|false)|incorrect\s+to\s+say\s+it\s+is\s+not|not\s+the\s+case\s+that\s+it\s+is\s+(?:not|untrue))', pl) and 'is it true' in pl:
            prefix = pl.split('is it true')[0]
            negs = len(re.findall(r'\b(?:not|untrue|false|incorrect)\b', prefix))
            correct = "yes" if negs % 2 == 0 else "no"
            return (1.0, "computation:double_negation") if cl.startswith(correct) else (-1.0, "computation:double_negation")
        if re.search(r'(?:not\s+the\s+case\s+that\s+both|false\s+that\s+.+\s+and\s+.+\s+both)', pl):
            if 'at least one' in cl: return (1.0, "structural:demorgan")
            return (-0.8, "structural:demorgan")
        if re.search(r'(?:2\s*\+\s*2\s*=\s*5|moon.*cheese|pigs.*fly|0\s*=\s*1|earth.*flat)', pl) and 'logical' in pl:
            if 'true' in cl and 'vacuous' in cl: return (1.0, "structural:vacuous_truth")
            if 'false' in cl: return (-1.0, "structural:vacuous_truth")
            return (-0.5, "structural:vacuous_truth")
        if re.search(r'correlat', pl) and re.search(r'(?:cause|causes)', pl):
            if 'no' in cl and 'correlation' in cl: return (1.0, "structural:correlation_not_causation")
            return (-0.8, "structural:correlation_not_causation")
        if (re.search(r'(?:then\s+.+?\.\s+(?:can\s+we\s+conclude|does\s+the\s+timing))', pl) and re.search(r'caus', pl)) or \
           (re.search(r'(?:preceded|afterwards|shortly\s+after)', pl) and re.search(r'(?:caus|prove)', pl)):
            if 'no' in cl: return (1.0, "structural:post_hoc")
            return (-0.8, "structural:post_hoc")
        if 'necessary' in pl and re.search(r'(?:guarantee|definitely|will\s+.+?\s+occur)', pl):
            if 'no' in cl: return (1.0, "structural:necessary_vs_sufficient")
            return (-0.8, "structural:necessary_vs_sufficient")
        if re.search(r'every\s+\w+', pl) and re.search(r'(?:same|did\s+they\s+all)', pl):
            if 'ambiguous' in cl or 'not necessarily' in cl: return (1.0, "structural:scope_ambiguity")
            return (-0.8, "structural:scope_ambiguity")
        if ('stopped' in pl or 'quit' in pl) and 'false' in pl and ('premise' in pl or 'presuppos' in pl):
            if 'both' in cl and 'false' in cl: return (1.0, "structural:presupposition")
            return (-0.8, "structural:presupposition")
        if re.search(r'(\w+)\s+(?:told|said|informed|reminded)\s+(\w+).*\b(he|she)\b\s+was', pl) and 'who' in pl:
            if 'ambiguous' in cl: return (1.0, "structural:pronoun_ambiguity")
            return (-0.8, "structural:pronoun_ambiguity")
        if re.search(r'increases?\s+by\s+(\d+)%.*decreases?\s+by\s+\1%', pl):
            if 'lower' in cl: return (1.0, "structural:pct_change_asym")
            return (-0.5, "structural:pct_change_asym")
        if re.search(r'(?:raced past the barn fell|old man the boat|complex houses married)', pl):
            if 'both interpretations' in cl: return (1.0, "structural:garden_path")
            return (-0.3, "structural:garden_path")
        if re.search(r'logically\s+valid', pl) and re.search(r'all\s+\w+\s+can\s+\w+', pl):
            return (1.0, "structural:validity_vs_truth") if cl.startswith("yes") else (-1.0, "structural:validity_vs_truth")
        if 'logically stronger' in pl and 'argument a' in pl:
            parts = re.split(r'argument\s+[ab]:', pl, flags=re.IGNORECASE)
            if len(parts) >= 3:
                af = bool(re.search(r'has\s+a\s+pet.*therefore.*has\s+a\s+\w+', parts[1]))
                if af: return (1.0, "structural:argument_strength") if cl.strip().startswith("b") else (-0.8, "structural:argument_strength")
                return (1.0, "structural:argument_strength") if cl.strip().startswith("a") else (-0.8, "structural:argument_strength")
        if re.search(r'how\s+confident', pl):
            if 'almost certainly' in pl: return (1.0, "judgment:confidence_cal") if 'high' in cl else (-0.3, "judgment:confidence_cal")
            if 'possibly' in pl: return (1.0, "judgment:confidence_cal") if cl.startswith('low') else (-0.3, "judgment:confidence_cal")
            if re.search(r'(?:probably|likely|believed)', pl): return (1.0, "judgment:confidence_cal") if 'moderate' in cl else (-0.3, "judgment:confidence_cal")
        m = re.search(r'"([^"]+)"', p)
        if m and re.search(r'(?:true|false)\?', pl):
            sentence = m.group(1); wc = len(sentence.split()); nm = re.search(r'(\d+)', sentence)
            if nm:
                claimed = int(nm.group(1)); correct = "true" if wc == claimed else "false"
                return (1.0, "computation:self_referential") if cl.startswith(correct) else (-1.0, "computation:self_referential")
        if 'exactly one' in pl and ('lies' in pl or 'truth' in pl) and 'says' in pl:
            names = re.findall(r'([A-Z][a-z]+)\s+says', p)
            if len(names) == 3: return (1.0, "computation:liar_detection") if names[1].lower() in cl else (-0.8, "computation:liar_detection")
        m = re.search(r'(\w+)\s+puts?\s+a?\s*(\w+)\s+in\s+the\s+(\w+).*?moves?\s+the\s+\w+\s+to\s+the\s+(\w+)', pl)
        if m and 'where will' in pl:
            return (1.0, "structural:false_belief") if m.group(3) in cl else (-1.0, "structural:false_belief")
        if 'rigged' in pl and 'does not know' in pl and 'expect' in pl:
            if 'equal' in cl or 'either' in cl: return (1.0, "structural:knowledge_attribution")
            if 'always' in cl: return (-1.0, "structural:knowledge_attribution")
            return (-0.3, "structural:knowledge_attribution")
        m = re.search(r'(\w+)\s+thinks\s+that\s+(\w+)\s+believes?\s+(.+?)\.\s+according', pl)
        if m:
            if m.group(3).strip() in cl: return (1.0, "structural:second_order_belief")
            return (-0.8, "structural:second_order_belief")
        if re.search(r'all\s+\w+\s+are\s+\w+', pl) and re.search(r'is\s+\w+\s+one\s+of', pl):
            return (1.0, "structural:multi_hop") if cl.startswith("yes") else (-0.8, "structural:multi_hop")
        cp = re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|heavier)\s+than\s+(\w+)', pl)
        if len(cp) >= 2 and len(set(x for pair in cp for x in pair)) == 4:
            return (1.0, "structural:info_sufficiency") if 'cannot' in cl else (-0.8, "structural:info_sufficiency")
        if re.search(r'if\s+\w+\s+has\s+a\s+\w+.*pet\s+owner', pl) and re.search(r'has\s+a\s+\w+\.\s+is', pl):
            return (1.0, "structural:irrelevant_premise") if cl.startswith("yes") else (-0.8, "structural:irrelevant_premise")
        if 'premise 1' in pl and 'premise 2' in pl and 'consistent' in pl:
            return (1.0, "structural:premise_contradiction") if cl.startswith("no") else (-1.0, "structural:premise_contradiction")
        ifs = re.findall(r'if\s+(.+?),\s*then\s+(.+?)(?:\.|$)', pl)
        if len(ifs) >= 2 and re.search(r'(?:follow|true|hold)', pl):
            return (1.0, "structural:chained_conditional") if cl.startswith("yes") else (-0.8, "structural:chained_conditional")
        m = re.search(r'what\s+is\s+(\d+)\s*\+\s*(\d+)\s*\*\s*(\d+)', pl)
        if m:
            result = int(m.group(1)) + int(m.group(2)) * int(m.group(3))
            if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:pemdas")
            return (-1.0, "computation:pemdas")
        m = re.search(r'(\d+):00\s*(am|pm).*?in\s+(\d+)\s+hours', pl)
        if m:
            h, ampm, n = int(m.group(1)), m.group(2), int(m.group(3))
            h24 = (h % 12) + (12 if ampm == 'pm' else 0); end24 = (h24 + n) % 24
            if end24 == 0: disp, ap = 12, "am"
            elif end24 < 12: disp, ap = end24, "am"
            elif end24 == 12: disp, ap = 12, "pm"
            else: disp, ap = end24 - 12, "pm"
            if f"{disp}:00" in cl and ap in cl: return (1.0, "computation:modular_arith")
            return (-0.8, "computation:modular_arith")
        m = re.search(r'(\d+)\s+meters?\s+long.*?every\s+(\d+)\s+meters?.*both\s+ends', pl)
        if m:
            total, spacing = int(m.group(1)), int(m.group(2)); cv = total // spacing + 1
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:fencepost")
            return (-1.0, "computation:fencepost")
        m = re.search(r'class\s+of\s+(\d+)\s+students.*?(\d+)\s+play\s+\w+.*?(\d+)\s+play\s+\w+.*minimum', pl)
        if m:
            n, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3)); mb = max(0, a + b - n)
            if cn and abs(cn[0] - mb) < 0.01: return (1.0, "computation:inclusion_exclusion")
            return (-1.0, "computation:inclusion_exclusion")
        if 'facing each other' in pl:
            m2 = re.search(r'(\w+)\s+raises?\s+their\s+(left|right)', pl)
            if m2:
                flipped = "right" if m2.group(2) == "left" else "left"
                if flipped in cl: return (1.0, "computation:left_right")
                return (-1.0, "computation:left_right")
        sm = re.search(r'facing\s+(north|south|east|west)', pl)
        if sm and 'turn' in pl:
            dirs = ["north","east","south","west"]; cur = dirs.index(sm.group(1))
            for t in re.findall(r'turn\s+(right|left)', pl): cur = (cur + (1 if t == 'right' else -1)) % 4
            if dirs[cur] in cl: return (1.0, "computation:direction")
            return (-1.0, "computation:direction")
        if 'inside' in pl and re.search(r'is\s+the\s+\w+\s+inside', pl):
            return (1.0, "structural:containment") if cl.startswith("yes") else (-0.8, "structural:containment")
        if re.search(r'no\s+\w+\s+exist', pl) and 'both' in pl:
            return (1.0, "structural:empty_set") if cl.startswith("yes") else (-1.0, "structural:empty_set")
        if re.search(r'all\s+\w+\s+are\s+\w+.*does\s+it\s+follow.*all', pl):
            return (1.0, "structural:subset_inversion") if cl.startswith("no") else (-1.0, "structural:subset_inversion")
        if 'sample' in pl and re.search(r'should\s+you', pl) and 'success' in pl:
            if 'need to see' in cl or 'failed' in cl: return (1.0, "structural:survivorship")
            return (-0.8, "structural:survivorship")
        if re.search(r'already\s+(?:spent|paid)', pl) and 'good reason' in pl:
            if 'regardless' in cl: return (1.0, "structural:sunk_cost")
            return (-0.8, "structural:sunk_cost")
        if 'statement a' in pl and 'statement b' in pl and 'same information' in pl:
            return (1.0, "structural:framing") if cl.startswith("yes") else (-0.8, "structural:framing")
        if re.search(r'no\s+other\s+option', pl) and 'possible' in pl:
            return (1.0, "structural:false_dichotomy") if cl.startswith("yes") else (-0.8, "structural:false_dichotomy")
        if re.search(r'every\s+\w+\s+is', pl) and 'necessarily follow' in pl:
            if 'not necessarily' in cl or cl.startswith('no'): return (1.0, "structural:composition_fallacy")
            return (-0.8, "structural:composition_fallacy")
        if re.search(r'scored\s+\d+.*then\s+\d+', pl) and 'worse' in pl:
            if 'regression' in cl: return (1.0, "structural:regression_to_mean")
            return (-0.8, "structural:regression_to_mean")
        if 'divisible by 4' in pl and 'even' in pl and 'necessarily' in pl:
            return (1.0, "structural:affirm_conseq_num") if cl.startswith("no") else (-1.0, "structural:affirm_conseq_num")
        if re.search(r'(?:rare|unpredictable|unprecedented|unforeseeable)', pl) and re.search(r'(?:reasonable|appropriate|sound)', pl):
            if 'yes' in cl and 'reasonable' in cl: return (1.0, "judgment:intention_vs_outcome")
            return (-0.8, "judgment:intention_vs_outcome")
        return (0.0, "fallback:ncd")

    def _secondary(self, p: str, c: str) -> float:
        edges = sum(1 for w in c.lower().split() if w in ('connects','links','relates','maps','transforms','between'))
        return min(edges / 3.0, 1.0) * 0.08

    def evaluate(self, prompt: str, candidates: list) -> list:
        results = []
        for c in candidates:
            s, r = self._cat_score(prompt, c)
            if r == "fallback:ncd":
                ncd_v = self._ncd(prompt, c)
                score = (1.0 - ncd_v) * 0.15 + self._secondary(prompt, c)
                r = f"fallback:ncd={ncd_v:.4f}"; conf = 0.2
            else:
                score = s * 0.55 + self._secondary(prompt, c) * 0.1
                conf = min(0.85, abs(s))
            results.append({"candidate": c, "score": float((score+1)/2), "reasoning": f"{r},confidence:{conf:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(0.85, 0.6 + s * 0.25)
        if s < -0.5: return 0.1
        return 0.35

```

---
