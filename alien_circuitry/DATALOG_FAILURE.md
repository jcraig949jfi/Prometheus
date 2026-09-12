# AC-01 instrument record: the monotone Datalog universe

Classification: **INSTRUMENTALLY INSUFFICIENT**. Rejected as AC-01's primary instrument on 2026-09-12.
Not repaired. Preserved as evidence. Measurements and scripts are in `evidence/instrument_failure/`
(migrated verbatim from the session scratchpad; sha256 in `evidence/instrument_failure/PROVENANCE.md`).

## The universe as proposed in the first receipt

Constants {a, b, c}; predicates P(x), Q(x), R(x, y); 15 positive ground atoms; state = set of established atoms;
fixed rule templates: modus ponens P(x) & R(x,y) -> Q(y); transitivity R(x,y) & R(y,z) -> R(x,z);
symmetry Q(x) & R(x,y) -> R(y,x); rewrite P(x) <-> Q(x); contradiction P(x) & not P(x) -> bottom.
Negated atoms are never derived, so they only matter through the contradiction rule.

## Measurements (full enumeration of all 2^15 positive states, 0.3 s)

```
universal states                               32768
nominal actions (rule x binding)                  51
distinct successor maps                           15   (= number of derivable atoms)
max shortest proof anywhere                        4
candidate problems (2-5 initial facts)         24780
  D=1 13197 | D=2 7551 | D=3 3900 | D=4 132
eligible EASY(3-4) / MEDIUM(5-6) / HARD(>=7)   4032 / 0 / 0
transitions that change target reachability        0
distinct D-row "behavioural classes"           32768   (one per state: D=0 iff atom in state)
mean BFS expansions / forward-chaining facts / D   8.2 / 4.2 / 1.6
search-avoided ceiling vs BFS / vs chaining      80% / 61%
with 2 random negated atoms: problems unsolvable   9.4%; problems made harder: 0
```

## Why it fails, structurally

1. **No dead ends can exist.** closure(s + c) = closure(s) for every derivable atom c, so no legal derivation
   changes target reachability. The reachability channel is constant across actions; three of the five M2
   sub-channels in the receipt would report 100% preservation for any method.
2. **No MEDIUM or HARD stratum exists.** The closure is small, so no proof needs more than four steps.
3. **Effective operator rank is known before the experiment.** The state is the fact set; 51 nominal actions
   are 15 edges. PC2, H2 and H4 are tautologies in this universe.
4. **The behavioural quotient is the identity.** The D-row encodes the state.
5. **BFS is a straw baseline.** Forward chaining to fixpoint is the honest uninformed method for a monotone
   system; BFS explores derivation orderings, which is an artifact.
6. **The receipt's enumeration strategy (BFS from the empty state) yields one node.**

## The structural theorem that came out of the failure

A target-conditioned trap (t reachable from s, not from a(s)) requires an action that is both **irreversible**
and **non-monotone**.

- Monotone Datalog: irreversible but monotone. Traps impossible (proof above). Measured 0.
- Symmetric equational rewriting (cancel + introduce + relators both ways): non-monotone but reversible, the
  graph is undirected, so no move can lose reachability. Measured 0 at L=7 for both presentations
  (`evidence/instrument_failure/rewrite_results_L7.json`).
- Directed bounded rewriting (cancel + relators both ways, no introduce): irreversible and non-monotone.
  Traps measured at 0.5-1.8% of live (state, action, target) triples with >99% of trap successors still
  having legal actions (`rewrite_directed_results_L8.json`, `_L9.json`, and the Phase A/B results).

That theorem is the design constraint for every future AC-01 universe.
