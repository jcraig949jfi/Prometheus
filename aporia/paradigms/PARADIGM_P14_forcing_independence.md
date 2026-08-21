# PARADIGM P14 — Forcing and Independence (worked example + decision tree + code skeleton)

Aporia P87, 2026-08-21. Source: taxonomy P14; no DR grounding in BACKCORPUS
(checked). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: show a statement UNPROVABLE from given axioms by constructing
alternative universes (verb: FORCE-A-COUNTERMODEL; payoff verb:
EXPLAIN-WHY-A-PROBLEM-RESISTS-EVERYTHING).

## 1. Worked example — the OBJECT computed, the META-LEVEL a typed gap
(`paradigm_p14_worked_example.py`)

Goodstein sequences: termination for every seed is TRUE (ZFC, via ordinals
below ε₀) yet UNPROVABLE in Peano Arithmetic (Kirby–Paris 1982 — cited
unverified-pending-fetch; that meta-claim is NOT what the script tests).
What executes:
- G(2) = [2,2,1,0] and G(3) = [3,3,3,2,1,0], hand-gated to termination —
  hereditary base-change implemented with the recursion into EXPONENTS (flat
  base-change is the classic wrong implementation, named in-script).
- G(4)'s exact opening: 4 → 26 (step-1 gate) → 41 → 60 → … → 211, strictly
  growing. Honesty note: the folklore says G(4) "explodes instantly" — it
  does not; the observed opening is modest and the astronomical behavior
  (termination after ~3·2^402653211 steps) is a stated literature bound, not
  an observation. Verdict: **OBJECT-COMPUTED**.

## STRUCTURAL-GAP (typed, per the tier's honesty rule)

Forcing itself has NO executable local substrate: no proof-assistant with
ZF-models is in the toolchain, and no computation can exhibit unprovability
(only proofs about proofs can). What a computable independence phenomenon
would need here: (a) a formalized PA inside a kernel (Isabelle/ZF-class),
(b) a verified proof of Goodstein in ZFC alongside a verified
non-derivability argument — both are proof-engineering projects, not loop
passes. The paradigm's local value is DIAGNOSTIC: it names the possibility
that a stuck problem is independent, not hard — the taxonomy's own note
(verdict-0 tensor cells) is this diagnosis institutionalized. Pattern check:
this is the third artifact without a full executable core, but NOT the
geometry pattern (P06/P13 lacked targets; P14 lacks a substrate for its
meta-level while its object-level runs) — typed differently on purpose.

## 2. Decision tree

- Q1: Has the problem resisted multiple structurally different paradigms
  (P01-P13 class) beyond effort-proportionate expectations? — NO: do not
  reach for independence; it is the LAST diagnosis, not the first.
- Q1 YES — Q2: Does the problem QUANTIFY over all integers/sets in a way
  that resembles known independent statements (Goodstein/Paris-Harrington
  growth, CH-class cardinality)? — NO: resistance is probably just
  difficulty; return to the other trees.
- Q2 YES — Q3: Is there a proof-theoretic ROUTE (ordinal analysis, known
  independence transfer, a formalizable fragment)? — NO: record the
  independence SUSPICION as a typed residue on the problem (it changes
  expected-value calculations for further attack spend) and stop.
- Q3 YES — EXECUTE (meta-level, outside loop passes): formalize and consult
  proof-theory expertise; loop-level contribution ends at computing the
  objects and typing the suspicion.

## 3. Code skeleton

```python
def independence_diagnosis(problem, attack_history, growth_witnesses):
    """P14 template. Loop-level: compute the OBJECTS, type the suspicion.
    The meta-level is proof engineering, not a pass."""
    resisted = [a for a in attack_history if a.exhausted and not a.resolved]
    if len(resisted) < 3:
        return ("KEEP-ATTACKING", None)
    fast_growth = any(w.outgrows_all_pa_provable_bounds for w in growth_witnesses)
    return ("INDEPENDENCE-SUSPECTED" if fast_growth else "HARD-NOT-INDEPENDENT",
            {"residue": "typed suspicion; changes EV of further spend"})
```

## 4. Catalog assignment

Primary: none executable — the paradigm is a DIAGNOSTIC lens. Diagnostic
assignment: any catalog row that survives 3+ paradigm-diverse attack
campaigns earns a P14 review (none qualify yet — the catalog's attacks are
young). Anti-assignment: everything, as an attack method (Q1's guard); the
tree exists to STOP premature independence claims as much as to enable them.

## Provenance and honesty

The Goodstein computation is elementary; the value is the clean separation of
computable object from meta-mathematical claim (the pass tests the former,
cites the latter), the anti-folklore observation about G(4)'s modest opening,
and the diagnostic tree whose first node REFUSES the paradigm in almost all
cases. An independence paradigm that is easy to invoke would be a
crackpot-magnet; this one is deliberately hard to enter.
