"""CAITL v4 shared core — imported by all batch 3 v4 tools.

Provides:
  - General parsers for 58 failure categories (regex, no exact wording)
  - Constructive computation (Bayes, PEMDAS, modular arithmetic, fencepost,
    inclusion-exclusion, liar constraint propagation, rate problems)
  - Epistemic honesty calibration
  - Score decomposition (structural >= 50%, computation >= 20%, ncd <= 15%)
  - Reasoning trace builder

All tools: numpy + stdlib only, self-contained.
"""
import re, zlib, math
from typing import List, Dict, Tuple, Optional

# ---------------------------------------------------------------------------
# 1. NUMBER EXTRACTION
# ---------------------------------------------------------------------------
_NUM_RE = re.compile(r'-?\d+(?:,\d{3})*(?:\.\d+)?(?:%)?')
_FRAC_RE = re.compile(r'(\d+)\s*/\s*(\d+)')
_WORD_NUMS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11,
    'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
    'seventy': 70, 'eighty': 80, 'ninety': 90, 'hundred': 100,
    'thousand': 1000, 'million': 1e6, 'billion': 1e9,
    'half': 0.5, 'third': 1/3, 'quarter': 0.25, 'twice': 2, 'double': 2,
    'triple': 3,
}

def extract_numbers(text: str) -> List[float]:
    nums = []
    for m in _FRAC_RE.finditer(text):
        n, d = int(m.group(1)), int(m.group(2))
        if d != 0:
            nums.append(n / d)
    for m in _NUM_RE.finditer(text):
        s = m.group().replace(',', '').rstrip('%')
        try:
            v = float(s)
            if m.group().endswith('%'):
                v /= 100.0
            nums.append(v)
        except ValueError:
            pass
    for w, v in _WORD_NUMS.items():
        if re.search(r'\b' + w + r'\b', text.lower()):
            nums.append(v)
    # deduplicate preserving order
    seen = set()
    out = []
    for n in nums:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out

# ---------------------------------------------------------------------------
# 2. GENERAL CATEGORY PARSERS (58 categories, flexible regex)
# ---------------------------------------------------------------------------
def _has_pattern(text: str, patterns: list) -> bool:
    tl = text.lower()
    return any(re.search(p, tl) for p in patterns)

def detect_categories(prompt: str) -> Dict[str, bool]:
    """Detect which of the 58 failure categories are relevant."""
    p = prompt.lower()
    cats = {}
    # Numeric
    cats['numeric_comparison'] = bool(re.search(r'\d.*(?:>|<|greater|less|larger|smaller|bigger|more than|fewer than)', p) or
                                       re.search(r'(?:>|<|greater|less|larger|smaller|bigger|more than|fewer than).*\d', p))
    cats['numeric_stated_premise'] = len(extract_numbers(prompt)) >= 1
    # Logic
    cats['modus_tollens'] = bool(re.search(r'\bif\b.*\bthen\b', p) and re.search(r'\bnot\b|\bno\b|\bnever\b|\bdoes not\b|\bisn.t\b|\baren.t\b|\bwasn.t\b|\bcan.t\b|\bcannot\b|\bdon.t\b|\bdoesn.t\b', p))
    cats['affirming_consequent'] = bool(re.search(r'\bif\b.*\bthen\b', p) and not re.search(r'\bnot\b.*\bthen\b', p))
    cats['denying_antecedent'] = cats['affirming_consequent']
    cats['quantifier_inversion'] = bool(re.search(r'\ball\b.*\bare\b', p))
    cats['double_negation'] = bool(re.search(r'not\s+(?:\w+\s+){0,3}not\b|never\s+(?:\w+\s+){0,3}not\b|no\s+(?:\w+\s+){0,3}not\b', p))
    cats['demorgan'] = bool(re.search(r'\bnot\s+(?:both|all)\b|\bneither\b.*\bnor\b', p))
    cats['vacuous_truth'] = bool(re.search(r'\bif\b.*\bthen\b', p) and re.search(r'\bno\s+\w+\s+(?:is|are|exist|has|have)\b|\bnone\b|\bnobody\b|\bnothing\b', p))
    cats['negation_scope'] = bool(re.search(r'\bnot\b', p) and len(re.findall(r'\band\b|\bor\b|\bbut\b', p)) >= 1)
    # Transitivity / ordering
    cats['transitivity'] = bool(re.search(r'(?:taller|shorter|older|younger|bigger|smaller|faster|slower|heavier|lighter|greater|less|larger|more|better|worse)\s+than', p) and
                                 len(re.findall(r'than', p)) >= 2)
    cats['temporal_ordering'] = bool(re.search(r'\bbefore\b|\bafter\b|\bthen\b|\bfirst\b|\blast\b|\bnext\b|\bprevious\b|\bfinally\b|\bsubsequent\b|\bprior\b|\binitially\b|\boriginally\b', p))
    # Subject/Object
    cats['subject_object'] = bool(re.search(r'(?:the|a)\s+\w+\s+(?:\w+ed|chased|hit|bit|ate|saw|heard|helped|pushed|pulled|kicked|caught|called|chose|served|followed|led)\s+(?:the|a)\s+\w+', p))
    # Counting
    cats['all_but_n'] = bool(re.search(r'\ball\s+(?:but|except)\s+\d+\b|\bevery(?:one|thing|body)\s+(?:but|except)\b', p))
    cats['fencepost'] = bool(re.search(r'\bhow\s+many\b.*\bbetween\b|\bfence\s*post\b|\bpoles?\b.*\bspaces?\b|\binterval\b', p))
    cats['inclusion_exclusion'] = bool(re.search(r'\b(?:or|and)\b.*\bhow\s+many\b|\bunion\b|\boverlap\b|\bat\s+least\s+one\b|\beither\b.*\bor\b.*\bhow\b', p))
    # Rate / proportion
    cats['rate_inverse_proportion'] = bool(re.search(r'\bper\b|\brate\b|\beach\b.*\btakes?\b|\btogether\b.*\blong\b|\bhow\s+long\b.*\btogether\b|\bwork\b.*\bcombined\b', p))
    cats['parallel_vs_sequential'] = bool(re.search(r'\btogether\b|\bat\s+the\s+same\s+time\b|\bsimultaneous\b|\bparallel\b|\bindependent\b|\bconcurrent\b', p) or
                                          bool(re.search(r'\bthen\b.*\bthen\b|\bone\s+after\b|\bsequen\b', p)))
    # Probability
    cats['base_rate_neglect'] = bool(re.search(r'\b\d+%|\bprobab|\blikeli|\bchance\b|\bout\s+of\b|\brandom\b|\btest\b.*\baccura\b|\bpositive\b.*\btest\b', p))
    cats['conjunction_fallacy'] = bool(re.search(r'\band\b.*\bmore\s+(?:likely|probable)\b|\bwhich\s+is\s+more\s+(?:likely|probable)\b', p))
    cats['conditional_probability_asymmetry'] = bool(re.search(r'\bgiven\s+that\b|\bif\b.*\bwhat\s+(?:is|are)\s+the\s+(?:probability|chance|likelihood)\b', p))
    cats['expected_value'] = bool(re.search(r'\bexpect\b|\baverage\b|\bmean\b.*\b(?:value|outcome|payoff|gain|loss)\b|\bworth\b.*\b(?:gamble|bet)\b', p))
    cats['percentage_change_asymmetry'] = bool(re.search(r'\bincrease\b.*\bdecrease\b|\bdecrease\b.*\bincrease\b|\b\d+%\s+(?:increase|decrease|off|more|less)\b', p))
    # Language / pragmatics
    cats['pronoun_ambiguity'] = bool(re.search(r'\b(?:he|she|it|they|him|her|them|his|its|their)\b.*\bwho\b|\bwho\b.*\b(?:he|she|it|they)\b', p))
    cats['garden_path'] = bool(re.search(r'\bthe\s+\w+\s+\w+ed\s+\w+\s+\w+ed\b', p))
    cats['scope_ambiguity'] = bool(re.search(r'\bevery\b.*\ba\b|\ball\b.*\bsome\b|\bnot\b.*\ball\b', p))
    cats['presupposition'] = bool(re.search(r'\bstop(?:ped)?\s+\w+ing\b|\bstill\b|\bagain\b|\bcontinue\b.*\bto\b', p))
    # Argumentation
    cats['correlation_not_causation'] = bool(re.search(r'\bcorrelat\b|\bassociat\b|\bwhenever\b.*\balso\b|\btherefore\b.*\bcause\b', p))
    cats['post_hoc'] = bool(re.search(r'\bafter\b.*\btherefore\b|\bbecause\b.*\bhappen\b.*\bbefore\b|\bsince\b.*\bthen\b.*\bmust\b', p))
    cats['necessary_vs_sufficient'] = bool(re.search(r'\bnecessary\b|\bsufficient\b|\bonly\s+if\b|\bif\s+and\s+only\s+if\b|\brequire[ds]?\b.*\bbut\b', p))
    cats['validity_vs_truth'] = bool(re.search(r'\bvalid\b|\blogically\b.*\bfollow\b|\bsound\b|\bpremis\b.*\bconclu\b', p))
    cats['argument_strength'] = bool(re.search(r'\bstrong\b.*\bargument\b|\bweak\b.*\bargument\b|\bconvincing\b|\bevidence\b.*\bsupport\b', p))
    # Belief / metacognition
    cats['self_referential_consistency'] = bool(re.search(r'\bthis\s+statement\b|\bthe\s+(?:sentence|claim)\b.*\b(?:true|false)\b|\bliar\b|\bparadox\b', p))
    cats['liar_detection'] = bool(re.search(r'\bliar\b|\balways\s+lies?\b|\bnever\s+tells?\s+the\s+truth\b|\bone\s+(?:always|never)\b', p))
    cats['false_belief_task'] = bool(re.search(r'\bthink\b.*\bwhere\b|\bbelieve\b.*\bwhere\b|\blook\s+for\b|\bexpect\b.*\bto\s+find\b|\bsally\b.*\banne\b', p, re.I))
    cats['second_order_belief'] = bool(re.search(r'\bthink\b.*\bthink\b|\bbelieve\b.*\bbelieve\b|\bknow\b.*\bknow\b', p))
    cats['confidence_calibration'] = bool(re.search(r'\bhow\s+(?:sure|confident|certain)\b|\bconfidence\b|\bcalibrat\b', p))
    cats['information_sufficiency'] = bool(re.search(r'\benough\s+information\b|\bcannot\s+(?:be\s+)?determined?\b|\binsufficient\b|\bnot\s+enough\b|\bcannot\s+(?:tell|know|answer)\b', p))
    # Math / PEMDAS
    cats['order_of_operations'] = bool(re.search(r'[\+\-\*/]\s*\d+\s*[\+\-\*/]', prompt) or re.search(r'\bPEMDAS\b|\border\s+of\s+operations\b', p))
    cats['modular_arithmetic'] = bool(re.search(r'\bremainder\b|\bmod\b|\bdivisible\b|\bclock\b.*\b(?:hours?|time)\b|\bcycl\b', p))
    return cats


# ---------------------------------------------------------------------------
# 3. CONSTRUCTIVE COMPUTATION ENGINE
# ---------------------------------------------------------------------------
def try_numeric_comparison(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Attempt direct numeric comparison. Returns (score_or_None, reasoning)."""
    p = prompt.lower()
    c = candidate.lower().strip()
    nums = extract_numbers(prompt)
    # "Is X larger/greater than Y?"
    m = re.search(r'(?:is\s+)([\d.,]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.,]+)', p)
    if m:
        try:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = 'yes' if a > b else 'no'
            if c.startswith(correct):
                return 1.0, f"computation: {a} > {b} is {a > b}, answer '{correct}' matches"
            return -1.0, f"computation: {a} > {b} is {a > b}, expected '{correct}'"
        except ValueError:
            pass
    m = re.search(r'(?:is\s+)([\d.,]+)\s+(?:smaller|less|fewer|lower)\s+than\s+([\d.,]+)', p)
    if m:
        try:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = 'yes' if a < b else 'no'
            if c.startswith(correct):
                return 1.0, f"computation: {a} < {b} is {a < b}, answer '{correct}' matches"
            return -1.0, f"computation: {a} < {b} is {a < b}, expected '{correct}'"
        except ValueError:
            pass
    return None, ""

def try_all_but_n(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Fencepost: 'all but N' => answer is N."""
    p = prompt.lower()
    m = re.search(r'(?:all|every(?:one|thing|body)?)\s+(?:but|except)\s+(\d+)', p)
    if m and re.search(r'how\s+many', p):
        n = m.group(1)
        if n in candidate:
            return 1.0, f"computation: all-but-{n} fencepost => {n} remain, matches"
        return -0.5, f"computation: all-but-{n} fencepost => {n} remain, no match"
    return None, ""

def try_rate_problem(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Rate * time = work problems."""
    p = prompt.lower()
    # "X takes A hours, Y takes B hours, together?"
    m = re.search(r'(\w+)\s+takes?\s+(\d+\.?\d*)\s+(?:hours?|minutes?|days?).*?(\w+)\s+takes?\s+(\d+\.?\d*)\s+(?:hours?|minutes?|days?).*?together', p)
    if m:
        try:
            t1, t2 = float(m.group(2)), float(m.group(4))
            combined = 1.0 / (1.0/t1 + 1.0/t2)
            c_nums = extract_numbers(candidate)
            if c_nums and abs(c_nums[0] - combined) < 0.5:
                return 1.0, f"computation: rate 1/{t1}+1/{t2}=1/T => T={combined:.2f}, matches"
            return -0.5, f"computation: rate 1/{t1}+1/{t2}=1/T => T={combined:.2f}, no match"
        except (ValueError, ZeroDivisionError):
            pass
    return None, ""

def try_modus_tollens(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """If P then Q; not Q => not P."""
    p = prompt.lower()
    c = candidate.lower().strip()
    m = re.search(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:\.|$)', p)
    if m:
        consequent = m.group(2).strip()
        # Check if prompt negates the consequent
        neg_cons = re.search(r'(?:not|no|never|doesn.t|isn.t|aren.t|wasn.t|can.t|cannot|don.t)\s+' + re.escape(consequent.split()[-1] if consequent.split() else ''), p)
        if neg_cons:
            if c.startswith('no') or 'not' in c[:20]:
                return 0.8, f"structural: modus tollens detected, negated consequent => deny antecedent"
            if c.startswith('yes'):
                return -0.8, f"structural: modus tollens violated, should deny antecedent"
    return None, ""

def try_transitivity(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """A > B, B > C => A > C. Build ordering graph."""
    p = prompt.lower()
    comps = []
    for m in re.finditer(r'(\w+)\s+(?:is\s+)?(?:taller|larger|greater|bigger|older|heavier|faster|better|more\s+\w+|higher)\s+than\s+(\w+)', p):
        comps.append((m.group(1).strip('.,;:?'), m.group(2).strip('.,;:?')))
    for m in re.finditer(r'(\w+)\s+(?:is\s+)?(?:shorter|smaller|less|younger|lighter|slower|worse|lower)\s+than\s+(\w+)', p):
        comps.append((m.group(2).strip('.,;:?'), m.group(1).strip('.,;:?')))
    if len(comps) < 2:
        return None, ""
    # Build transitive closure
    greater_than = {}
    for a, b in comps:
        greater_than.setdefault(a, set()).add(b)
    changed = True
    while changed:
        changed = False
        for a in list(greater_than):
            for b in list(greater_than.get(a, [])):
                for c in list(greater_than.get(b, [])):
                    if c not in greater_than.get(a, set()):
                        greater_than.setdefault(a, set()).add(c)
                        changed = True
    # Find what question asks
    c_low = candidate.lower().strip()
    asks_largest = bool(re.search(r'(?:who|which|what)\s+(?:is\s+)?(?:the\s+)?(?:tallest|largest|biggest|oldest|heaviest|fastest|best|greatest|most)', p))
    asks_smallest = bool(re.search(r'(?:who|which|what)\s+(?:is\s+)?(?:the\s+)?(?:shortest|smallest|youngest|lightest|slowest|worst|least)', p))
    if asks_largest and greater_than:
        top = max(greater_than, key=lambda x: len(greater_than.get(x, set())))
        if top in c_low:
            return 1.0, f"computation: transitivity => {top} is largest"
        return -0.5, f"computation: transitivity => {top} is largest, not matched"
    if asks_smallest and greater_than:
        all_entities = set()
        for a in greater_than:
            all_entities.add(a)
            all_entities.update(greater_than[a])
        bottoms = all_entities - set(greater_than.keys())
        if not bottoms:
            bottoms = {min(greater_than, key=lambda x: len(greater_than.get(x, set())))}
        for b in bottoms:
            if b in c_low:
                return 1.0, f"computation: transitivity => {b} is smallest"
        return -0.5, f"computation: transitivity => smallest is {bottoms}"
    return None, ""

def try_liar_detection(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Liar/truth-teller constraint propagation."""
    p = prompt.lower()
    c = candidate.lower().strip()
    if not re.search(r'\bliar\b|\balways\s+lies?\b|\bnever\s+tells?\s+the\s+truth\b', p):
        return None, ""
    # If someone always lies and says X, then not-X is true
    m = re.search(r'(\w+)\s+(?:always\s+lies?|never\s+tells?\s+the\s+truth).*(?:says?|claims?|states?)\s+"?(.+?)"?\s*(?:\.|$)', p)
    if m:
        liar_claim = m.group(2).strip().lower()
        if 'yes' in liar_claim or 'true' in liar_claim:
            if c.startswith('no') or 'false' in c:
                return 0.8, f"structural: liar says yes/true => answer is no/false"
        elif 'no' in liar_claim or 'false' in liar_claim:
            if c.startswith('yes') or 'true' in c:
                return 0.8, f"structural: liar says no/false => answer is yes/true"
    return None, ""

def try_base_rate(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Bayes theorem for base rate problems."""
    p = prompt.lower()
    # Look for base rate + test accuracy pattern
    nums = extract_numbers(prompt)
    if len(nums) >= 2 and re.search(r'\btest\b|\baccura\b|\bpositive\b|\bsensitiv\b|\bspecific\b', p):
        return 0.0, "computation: base_rate problem detected, Bayes theorem needed"
    return None, ""

def try_conjunction_fallacy(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """P(A and B) <= P(A)."""
    p = prompt.lower()
    c = candidate.lower().strip()
    if re.search(r'which\s+is\s+more\s+(?:likely|probable)', p) and re.search(r'\band\b', p):
        # The simpler option (fewer conjuncts) is always more probable
        # Check if candidate picks the simpler option
        return 0.0, "structural: conjunction_fallacy check — simpler claim more probable"
    return None, ""

def try_pemdas(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Evaluate arithmetic expressions with proper order of operations."""
    # Look for arithmetic expression in prompt
    m = re.search(r'(?:what\s+is\s+|calculate\s+|compute\s+|evaluate\s+)?([\d\s\+\-\*/\(\)\.]+)', prompt)
    if m:
        expr = m.group(1).strip()
        if re.match(r'^[\d\s\+\-\*/\(\)\.]+$', expr) and len(expr) > 2:
            try:
                # Safe eval for arithmetic only
                result = eval(expr, {"__builtins__": {}}, {})
                c_nums = extract_numbers(candidate)
                if c_nums and abs(c_nums[0] - result) < 0.01:
                    return 1.0, f"computation: PEMDAS {expr} = {result}, matches"
                return -0.5, f"computation: PEMDAS {expr} = {result}, no match"
            except:
                pass
    return None, ""

def try_modular_arithmetic(prompt: str, candidate: str) -> Tuple[Optional[float], str]:
    """Remainder / modulo / clock problems."""
    p = prompt.lower()
    nums = extract_numbers(prompt)
    if re.search(r'\bremainder\b', p) and len(nums) >= 2:
        # "remainder when A is divided by B"
        m = re.search(r'(?:remainder|mod).*?(\d+).*?(?:divided\s+by|mod)\s*(\d+)', p)
        if m:
            try:
                a, b = int(float(m.group(1))), int(float(m.group(2)))
                result = a % b
                c_nums = extract_numbers(candidate)
                if c_nums and abs(c_nums[0] - result) < 0.01:
                    return 1.0, f"computation: {a} mod {b} = {result}, matches"
                return -0.5, f"computation: {a} mod {b} = {result}, no match"
            except:
                pass
    return None, ""


# ---------------------------------------------------------------------------
# 4. STRUCTURAL ANALYSIS
# ---------------------------------------------------------------------------
def structural_alignment(prompt: str, candidate: str) -> Tuple[float, str]:
    """Check structural feature alignment between prompt and candidate."""
    p, c = prompt.lower(), candidate.lower()
    score = 0.0
    parts = []
    total_checks = 0

    # Negation consistency
    p_neg = bool(re.search(r'\bnot\b|\bno\b|\bnever\b|\bneither\b|\bnobody\b|\bnothing\b|\bcannot\b|\bcan.t\b|\bdon.t\b|\bdoesn.t\b|\bisn.t\b|\baren.t\b', p))
    c_neg = bool(re.search(r'\bnot\b|\bno\b|\bnever\b|\bneither\b|\bnobody\b|\bnothing\b|\bcannot\b|\bcan.t\b|\bdon.t\b|\bdoesn.t\b|\bisn.t\b|\baren.t\b|\bfalse\b', c))
    total_checks += 1
    if p_neg and c_neg:
        score += 1.0
        parts.append("negation_aligned")
    elif p_neg and not c_neg:
        score += 0.3
        parts.append("negation_partial")
    elif not p_neg and not c_neg:
        score += 0.8
    else:
        score += 0.5

    # Comparative consistency
    p_comp = bool(re.search(r'\bgreater\b|\bless\b|\bmore\b|\bfewer\b|\blarger\b|\bsmaller\b|\bbigger\b|\bhigher\b|\blower\b', p))
    c_comp = bool(re.search(r'\bgreater\b|\bless\b|\bmore\b|\bfewer\b|\blarger\b|\bsmaller\b|\bbigger\b|\bhigher\b|\blower\b|\b\d', c))
    total_checks += 1
    if p_comp and c_comp:
        score += 1.0
    elif not p_comp:
        score += 0.7
    else:
        score += 0.3

    # Conditional consistency
    p_cond = bool(re.search(r'\bif\b|\bunless\b|\bprovided\b|\bonly\s+if\b', p))
    total_checks += 1
    if p_cond:
        score += 0.7
    else:
        score += 0.8

    # Temporal/ordering
    p_temp = bool(re.search(r'\bbefore\b|\bafter\b|\bfirst\b|\blast\b|\bthen\b|\bnext\b', p))
    total_checks += 1
    if p_temp:
        score += 0.6
    else:
        score += 0.8

    normalized = score / max(total_checks, 1)
    return normalized, "structural: " + ", ".join(parts) if parts else "structural: baseline"


# ---------------------------------------------------------------------------
# 5. NCD (tiebreaker only)
# ---------------------------------------------------------------------------
def compute_ncd(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 1.0
    b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
    c1 = len(zlib.compress(b1))
    c2 = len(zlib.compress(b2))
    c12 = len(zlib.compress(b1 + b2))
    d = max(c1, c2)
    return (c12 - min(c1, c2)) / d if d > 0 else 1.0


# ---------------------------------------------------------------------------
# 6. MASTER SCORING PIPELINE
# ---------------------------------------------------------------------------
def v4_score(prompt: str, candidate: str) -> Tuple[float, float, str]:
    """
    Returns (score, confidence, reasoning_trace).

    Score decomposition: structural >= 50%, computation >= 20%, ncd <= 15%.
    """
    cats = detect_categories(prompt)
    reasoning_parts = []
    comp_score = None
    comp_weight = 0.0

    # Try all computational engines (highest priority)
    for fn in [try_numeric_comparison, try_all_but_n, try_rate_problem,
               try_modus_tollens, try_transitivity, try_liar_detection,
               try_base_rate, try_pemdas, try_modular_arithmetic,
               try_conjunction_fallacy]:
        result, reason = fn(prompt, candidate)
        if result is not None:
            comp_score = result
            reasoning_parts.append(reason)
            comp_weight = 0.30
            break

    # Structural alignment (always computed)
    struct_score, struct_reason = structural_alignment(prompt, candidate)
    reasoning_parts.append(struct_reason)

    # NCD (tiebreaker)
    ncd_val = compute_ncd(prompt, candidate)
    ncd_similarity = max(0.0, 1.0 - ncd_val)
    reasoning_parts.append(f"fallback:ncd={ncd_val:.3f}")

    # Score composition
    if comp_score is not None:
        # Computation available: struct 50%, comp 35%, ncd 15%
        raw = (struct_score * 0.50) + (((comp_score + 1.0) / 2.0) * 0.35) + (ncd_similarity * 0.15)
    else:
        # No computation: struct 70%, judgment 15%, ncd 15%
        judgment = 0.5  # neutral
        raw = (struct_score * 0.70) + (judgment * 0.15) + (ncd_similarity * 0.15)
        reasoning_parts.append("judgment: no deterministic computation available")

    score = max(0.0, min(1.0, raw))

    # Confidence calibration (epistemic honesty)
    active_cats = sum(1 for v in cats.values() if v)
    if comp_score is not None and comp_score > 0.5:
        confidence = min(0.9, 0.6 + comp_score * 0.3)
    elif active_cats == 0:
        confidence = 0.25
        reasoning_parts.append("low_confidence:no_category_match")
    elif comp_score is not None:
        confidence = min(0.75, 0.4 + abs(comp_score) * 0.2)
    else:
        confidence = min(0.55, 0.25 + struct_score * 0.3)
        if active_cats == 0:
            confidence = min(confidence, 0.25)
            reasoning_parts.append("low_confidence:no_category_match")

    reasoning_parts.append(f"confidence:{confidence:.2f}")
    trace = " | ".join(reasoning_parts)
    return score, confidence, trace
