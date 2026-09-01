"""Cycle 5: component knockout of v3 on the 80-item holdout. Each ablation replaces ONE component."""
from hephaestus.src import wall_vacuous_truth as W
import importlib.util, json, sys, re, copy
spec = importlib.util.spec_from_file_location("v3", sys.argv[1]); v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)
ex = W.build_examples(); _, hold = W.split(ex)
def run(op): m = W.metrics([W.run_op(op, e) for e in hold]); return {"acc": m["accuracy_decidable"], "bnd_fc": m["boundary_false_commit_rate"], "abstain": m["abstain_rate_decidable"]}
base = run(v3.op_vacuous_truth); out = {"baseline": base, "ablations": {}}
def ablate(name, patch):
    saved = {k: getattr(v3, k) for k in patch}
    for k, v in patch.items(): setattr(v3, k, v)
    try: r = run(v3.op_vacuous_truth)
    finally:
        for k, v in saved.items(): setattr(v3, k, v)
    r["delta_acc"] = round(r["acc"] - base["acc"], 4); out["ablations"][name] = r; print(f"{name:<44} acc {r['acc']:.3f}  d={r['delta_acc']:+.3f}  bnd_fc {r['bnd_fc']:.2f}  abstain {r['abstain']:.2f}")
print(f"{'BASELINE v3':<44} acc {base['acc']:.3f}           bnd_fc {base['bnd_fc']:.2f}")
# K1 kernel -> constant True (keeps parser; kills the reasoning)
ablate("K1 kernel:=constant True", {"quantified_truth": lambda q, nd, ns: True})
# K2 kernel without the empty-domain rule
def k2(q, nd, ns):
    if nd and ns is not None:
        return ns == nd if q in ("universal", "conditional") else ns == 0 if q == "neg_universal" else ns >= 1
    return None
ablate("K2 kernel: drop empty-domain rule", {"quantified_truth": k2})
# K3 kernel: empty domain -> True for ALL quantifiers (existential blind)
ablate("K3 kernel: existential-blind on empty", {"quantified_truth": lambda q, nd, ns: True if nd == 0 else v3.quantified_truth(q, nd, ns)})
# K4 kernel: universal ignores counterexamples (nd>0 and ns known -> True)
ablate("K4 kernel: counterexample-blind", {"quantified_truth": lambda q, nd, ns: (q != "existential") if nd == 0 else (True if (nd and ns is not None) else None)})
# P1 domain match: equality -> containment (premise phrase CONTAINS the claim domain)
orig_facts = v3._domain_facts
def p1(text, dom_key, pred_key, container):
    t = text.lower()
    if container: t = re.sub(r"\s+in\s+" + re.escape(container.lower()) + r"\b", "", t)
    for pat in v3._EMPTY_PATTERNS:
        for m in re.finditer(pat, t):
            phrase = m.group(1) if m.lastindex == 1 else m.group(1) + " that is " + m.group(2)
            if dom_key <= v3._key(phrase): return 0, None
    for m in v3._CARD.finditer(t):
        if dom_key <= v3._key(m.group(2)):
            nd = int(m.group(1)); s = v3._SAT.search(t[m.end():])
            return (nd, int(s.group(1))) if s and v3._key(s.group(2)) == pred_key else (nd, None)
    return None, None
ablate("P1 domain match: equality -> containment", {"_domain_facts": p1})
# P2 no container strip
def p2(text, dom_key, pred_key, container): return orig_facts(text, dom_key, pred_key, "")
ablate("P2 no container strip", {"_domain_facts": p2})
# P3 no cardinality reader (emptiness only)
def p3(text, dom_key, pred_key, container):
    nd, ns = orig_facts(text, dom_key, pred_key, container); return (0, None) if nd == 0 else (None, None)
ablate("P3 no cardinality reader", {"_domain_facts": p3})
# P4 predicate check off in the cardinality reader (any 'k of them are X' counts)
def p4(text, dom_key, pred_key, container):
    t = text.lower()
    if container: t = re.sub(r"\s+in\s+" + re.escape(container.lower()) + r"\b", "", t)
    for pat in v3._EMPTY_PATTERNS:
        for m in re.finditer(pat, t):
            phrase = m.group(1) if m.lastindex == 1 else m.group(1) + " that is " + m.group(2)
            if v3._key(phrase) == dom_key: return 0, None
    for m in v3._CARD.finditer(t):
        if v3._key(m.group(2)) == dom_key:
            nd = int(m.group(1)); s = v3._SAT.search(t[m.end():]); return (nd, int(s.group(1))) if s else (nd, None)
    return None, None
ablate("P4 cardinality reader ignores predicate", {"_domain_facts": p4})
# P5 no stemming
ablate("P5 no stemming", {"_stem": lambda w: w})
json.dump(out, open(sys.argv[2], "w"), indent=1)
