# PARADIGM P25 — Pivotal Negative Result (worked example + decision tree + code skeleton)

Aporia P92, 2026-08-21. Source: taxonomy P25 (round-2; Fefferman/Manolescu/
Slofstra exemplars). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: find the unexpected counterexample that kills a widely-believed
proposition; the kill's product is the better question (verb:
KILL-THE-EXPECTED; payoff verb: REORIENT-THE-FIELD-BY-ONE-COUNTEREXAMPLE).

## 1. Worked example — EXECUTED (`paradigm_p25_worked_example.py`)

Euler's sum-of-powers conjecture (1769; believed ~200 years):

- **A.** Both historic kills verified in EXACT integer arithmetic:
  27⁵+84⁵+110⁵+133⁵ = 144⁵ (Lander-Parkin) and
  95800⁴+217519⁴+414560⁴ = 422481⁴ (Elkies-Frye).
- **B.** The k=5 kill REDISCOVERED by our own blind meet-in-the-middle
  search (a ≤ b ≤ c ≤ d ≤ e ≤ 150, no knowledge of the answer): the search
  reports **exactly one** solution in range — the Lander-Parkin quadruple,
  nothing spurious, every report re-verified exactly. The 1966 machine-search
  moment reproduced in seconds. Verdict: **KILL-REDISCOVERED**.
- **C.** Reorientation typed: the kill's product is the Waring-type
  reformulation (how many k-th powers suffice) — the negative result as
  reorienting lemma, which is the paradigm's actual payoff.

## 2. Decision tree

- Q1: Is there a WIDELY-BELIEVED proposition with a searchable counterexample
  space (or a computable obstruction candidate)? — NO: negative results
  need a target; exit.
- Q1 YES — Q2: Is the search space STRUCTURED enough for honest search
  (meet-in-the-middle, algebraic parametrization, obstruction classes) —
  not blind enumeration beyond budget? — NO: record the search-frontier
  size as typed residue (P24's gap-metric pattern); exit.
- Q2 YES — Q3: Would a counterexample REORIENT (does the field's roadmap
  detour through this belief)? — NO: a kill nobody depends on is trivia;
  spend elsewhere. (The channel's kill-doctrine analog: kills are the most
  valuable output ONLY when something was resting on the belief.)
- Q3 YES — EXECUTE: search with every report re-verified exactly and
  spurious-solution accounting (a search that cannot report zero or many is
  broken); on a kill, TYPE THE REFORMULATION — the negative result without
  its better question is half-delivered.
- Prometheus note: the falsification battery IS a structural P25 generator;
  every battery kill that reorients a lane is this paradigm firing.

## 3. Code skeleton

```python
def negative_result_attack(belief, search_space, verify_exact, reformulate):
    """P25 template. Every report re-verified; the reformulation is part of
    the deliverable, not an afterthought."""
    hits = [x for x in search_space if verify_exact(belief.counterexample_test, x)]
    if not hits:
        return {"verdict": "BELIEF-SURVIVES-RANGE", "frontier": search_space.bound}
    for h in hits:
        assert verify_exact(belief.counterexample_test, h)   # independent re-check
    return {"verdict": "KILLED", "witnesses": hits,
            "reformulation": reformulate(belief, hits)}
```

## 4. Catalog assignment

Primary: the channel ITSELF — every catalog attack's falsifier field is a
P25 trigger in waiting; the battery and the kill-ledger are this paradigm as
infrastructure (feedback_assume_wrong: kills are the most valuable output).
Catalog rows: 0129/0154/0316-class (finite searches where a counterexample
would kill a pattern), 0137 (a Giuga number IS the P25 event for that row).
Anti-assignment: rows whose falsifiers are asymptotic-only (0060/0370) —
no finite witness kills them.

## Provenance and honesty

Both identities are settled history; the content is leg B — the kill
REDISCOVERED by a search that did not know the answer and could have
reported zero or many (it reported exactly one, correct) — and the tree's
Q3, which prices kills by what rested on the belief.

---

## Attribution pins (P100, layered per the citation rule)

- **k=5**: Lander, L. J.; Parkin, T. R., "Counterexample to Euler's conjecture
  on sums of like powers", *Bull. Amer. Math. Soc.* 72(6):1079 (1966) — the
  famously terse announcement. Citation string quoted from Wikipedia's
  reference list (tertiary-quoted layer; primary PDF unfetched).
- **k=4**: the 95800 quadruple was found by **Roger E. Frye** (1988),
  "Finding 95800^4 + 217519^4 + 414560^4 = 422481^4 on the Connection
  Machine", *Proc. Supercomputing 88*, Vol. II, pp. 106-116 — tertiary-quoted.
  CORRECTION to this artifact's original "(Elkies/Frye 1988)": the SMALLEST
  quadruple is Frye's machine search; Elkies (Math. Comp., 1988) supplied the
  elliptic-curve method and the FIRST k=4 counterexample — a different,
  larger quadruple. The conflation is fixed; Elkies's exact citation remains
  at secondary level pending its own fetch.
