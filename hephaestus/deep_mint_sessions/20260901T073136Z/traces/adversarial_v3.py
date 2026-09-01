"""Cycle 4: adversarial phrasings NOT in the dev set (authored after v3 passed; none copied from Charon's E9)."""
from hephaestus.src import wall_vacuous_truth as W
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("v3", sys.argv[1]); v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)
C = ["yes, it is true", "no, it is false", "cannot be determined", "only if the set is empty"]
ADV = [
 # emptiness idioms not in dev
 ("A1", "There aren't any green bottles on the wall. Consider the claim: every green bottle on the wall is cracked. Is the claim true?", "yes", "aren't any / 'on the wall' container"),
 ("A2", "Zero silver coins are in the chest. Consider the claim: each silver coin in the chest is counterfeit. Is the claim true?", "yes", "'Zero X are in C'"),
 ("A3", "The chest has no silver coins. Consider the claim: some silver coin in the chest is counterfeit. Is the claim true?", "no", "'has no'"),
 ("A4", "The pond is empty of frogs. Consider the claim: every frog in the pond is green. Is the claim true?", "yes", "'empty of'"),
 ("A5", "No frog lives in the pond. Consider the claim: all frogs in the pond are green. Is the claim true?", "yes", "'No X lives in C' verb form"),
 # claim framings not in dev
 ("B1", "There are no red marbles in the jar. Is it true that every red marble in the jar is chipped?", "yes", "no 'Consider the claim:' framing"),
 ("B2", "There are no red marbles in the jar. Claim: every red marble in the jar is chipped. True or false?", "yes", "'Claim:' framing"),
 ("B3", "There are no red marbles in the jar. Consider the claim: every one of the red marbles in the jar is chipped. Is the claim true?", "yes", "'every one of the'"),
 ("B4", "There are no red marbles in the jar. Consider the claim: all of the red marbles in the jar are chipped. Is the claim true?", "yes", "'all of the'"),
 ("B5", "There are no red marbles in the jar. Consider the claim: any red marble in the jar that is chipped is also heavy. Is the claim true?", "yes", "restrictive relative + 'also'"),
 ("B6", "There are no red marbles in the jar. Consider the claim: there exists a red marble in the jar that is chipped. Is the claim true?", "no", "'there exists'"),
 # non-empty domains, novel cardinality phrasing
 ("C1", "The jar holds 6 red marbles; 2 are chipped. Consider the claim: every red marble in the jar is chipped. Is the claim true?", "no", "semicolon; no 'of them'"),
 ("C2", "There are exactly 6 red marbles in the jar, and none of them are chipped. Consider the claim: no red marble in the jar is chipped. Is the claim true?", "yes", "'none of them'"),
 ("C3", "There are exactly 6 red marbles in the jar, and all of them are chipped. Consider the claim: every red marble in the jar is chipped. Is the claim true?", "yes", "'all of them' without count"),
 ("C4", "There are exactly 6 red marbles in the jar, and two of them are chipped. Consider the claim: every red marble in the jar is chipped. Is the claim true?", "no", "number word 'two'"),
 ("C5", "There are exactly 6 red marbles in the jar. Consider the claim: some red marble in the jar is chipped. Is the claim true?", "und", "non-empty, no predicate info -> abstain"),
 # traps
 ("D1", "There are no chipped marbles in the jar, but there are exactly 6 red marbles in the jar and 2 of them are heavy. Consider the claim: every red marble in the jar is chipped. Is the claim true?", "no", "predicate-word 'no' + domain non-empty, counterexample about the CLAIM predicate is implied not stated"),
 ("D2", "There are no red marbles in the jar. There are exactly 3 blue marbles in the jar and 1 of them is chipped. Consider the claim: every blue marble in the jar is chipped. Is the claim true?", "no", "empty domain of a DIFFERENT colour"),
 ("D3", "There are no red marbles in the jar. Consider the claim: every blue marble in the jar is chipped. Is the claim true?", "und", "empty domain of a different colour, nothing about blue -> abstain"),
 ("D4", "Consider the claim: every red marble in the jar is chipped. Nothing is known about the jar. Is the claim true?", "und", "explicit no-information"),
]
recs = []
for i, prompt, gold, why in ADV:
    ex = {"id": i, "kind": "ADV", "prompt": prompt, "candidates": C, "correct": C[0] if gold == "yes" else C[1] if gold == "no" else "cannot be determined", "gold": gold}
    r = W.run_op(v3.op_vacuous_truth, ex); r["why"] = why; recs.append(r)
    print(("OK  " if r["ok"] else "FAIL"), i, "gold", gold, "cmp", r["comparison"], "|", why)
ok = sum(r["ok"] for r in recs); print(f"\nADVERSARIAL: {ok}/{len(recs)} correct")
json.dump({"n": len(recs), "ok": ok, "records": recs}, open(sys.argv[2], "w"), indent=1)
