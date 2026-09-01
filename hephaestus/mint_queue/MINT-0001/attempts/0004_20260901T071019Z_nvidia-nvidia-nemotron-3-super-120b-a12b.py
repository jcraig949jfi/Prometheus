import re

def op_vacuous_truth(state):
    text = state.problem_text.lower()

    # ---- extract claim -------------------------------------------------
    m = re.search(r'consider the claim:\s*(.+?)(?:\s+is the claim|\?|$)', text)
    claim = m.group(1).strip() if m else text

    # ---- classify claim ------------------------------------------------
    univ_words = {'each','every','all','any'}
    ex_words   = {'there is','there exists','some','a '}
    if any(w in claim for w in univ_words) or claim.startswith('no '):
        ctype = 'universal'   # includes negative-universal & conditional
    elif any(w in claim for w in ex_words):
        ctype = 'existential'
    else:
        ctype = 'universal'   # default fallback

    # ---- parse subject & predicate --------------------------------------
    def parse_claim(cl):
        cl = cl.strip()
        # universal / negative-universal / conditional
        if cl.startswith('each ') or cl.startswith('every ') or cl.startswith('all ') or cl.startswith('any '):
            prefix = cl[:cl.index(' ')+1]
            rest = cl[len(prefix):]
        elif cl.startswith('no '):
            rest = cl[3:]
        else:
            # existential forms
            if cl.startswith('there is a ') or cl.startswith('there exists a '):
                # strip prefix and look for " that is/"
                if ' that is ' in cl:
                    before, after = cl.split(' that is ', 1)
                    subject = before[len('there is a '):] if before.startswith('there is a ') else before[len('there exists a '):]
                    predicate = after
                    return subject.strip(), predicate.strip(), ctype
            if cl.startswith('some '):
                rest = cl[5:]
            elif cl.startswith('a ') and ' that is ' in cl:
                before, after = cl.split(' that is ', 1)
                subject = before[2:]  # remove leading 'a '
                predicate = after
                return subject.strip(), predicate.strip(), ctype
            else:
                # fallback: split on first " is " or " are "
                sep = ' is ' if ' is ' in cl else ' are '
                if sep in cl:
                    subj, pred = cl.split(sep, 1)
                    return subj.strip(), pred.strip(), ctype
                return '', '', ctype
        # now split rest on first " is " or " are "
        sep = ' is ' if ' is ' in rest else ' are '
        if sep in rest:
            subj, pred = rest.split(sep, 1)
            return subj.strip(), pred.strip(), ctype
        return '', '', ctype

    subject, predicate, _ = parse_claim(claim)

    # ---- detect empty domain -------------------------------------------
    empty_pats = [
        rf'\bno\s+{re.escape(subject)}\b',
        rf'\bzero\s+{re.escape(subject)}\b',
        rf'\bnumber of\s+{re.escape(subject)}\s+is\s+zero\b',
        rf'\bthere are\s+zero\s+{re.escape(subject)}\b',
        rf'\bthere are\s+no\s+{re.escape(subject)}\b',
        rf'\bthere are\s+none\s+{re.escape(subject)}\b'
    ]
    domain_empty = any(re.search(p, text) for p in empty_pats)

    # ---- decide truth value --------------------------------------------
    if domain_empty:
        if ctype == 'universal':
            state.comparison = True
        else:  # existential
            state.comparison = False
        return state

    # non‑empty domain: look for explicit statements
    if ctype == 'universal':
        true_pat  = rf'\b(all|each|every)\s+{re.escape(subject)}\s+(are|is)\s+{re.escape(predicate)}'
        false_pat = rf'\b(no|none)\s+{re.escape(subject)}\s+(are|is)\s+{re.escape(predicate)}'
        if re.search(true_pat, text, re.IGNORECASE):
            state.comparison = True
        elif re.search(false_pat, text, re.IGNORECASE):
            state.comparison = False
        else:
            state.comparison = None
    else:  # existential
        true_pat  = rf'\b(some|there is a|there exists a)\s+{re.escape(subject)}\s+(are|is)\s+{re.escape(predicate)}'
        false_pat = rf'\b(no|none|zero)\s+{re.escape(subject)}\s+(are|is)\s+{re.escape(predicate)}'
        if re.search(true_pat, text, re.IGNORECASE):
            state.comparison = True
        elif re.search(false_pat, text, re.IGNORECASE):
            state.comparison = False
        else:
            state.comparison = None
    return state