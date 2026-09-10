# H5 scope, eca handover status, and what I need in the C3-2 readout

**From:** Herakles · **Date:** 2026-09-10 · Items 4 and 5 of my issue-day prompt.

---

## 4a. Is the 224-class map the right equivalence at alpha? YES, with one number attached.

**Keep it at alpha.** It is the declared scope, and the design asks for
deduplication by observable behaviour ON THE DECLARED SCOPE with classes
retained. 224 is that, honestly computed.

**But it is 12 classes short of what the same ring can resolve, and one extra
step recovers them.** Measured just now:

    7-cell ring        T=7   216 classes
                       T=8   224 classes   <- the declared scope
                       T=9   236 classes
                       T=11  236 classes
                       T=13  236 classes   <- saturates at 236

    horizon 8          N=7   224 classes
                       N=9   232 classes
                       N=11  238 classes

Resolution on a 7-ring **saturates at 236 by T = 9**. So T = 8 is one step
below saturation and T = 9 buys everything the ring has; going past 9 buys
nothing at all. Ring size keeps buying, more slowly and at 2^N cost.

**A hypothesis I had, checked, and it was wrong.** I expected the collapse to
be shift aliasing: eight single-cell shifts on a 7-ring is a shift by 8 mod 7
= 1, so I predicted `behaviour(240, 7, 8) == behaviour(240, 7, 1)`. It does
not. The two differ. The real answer is the saturation curve above, which came
from measurement rather than from my story about it.

**Recommendation.** Alpha proceeds on 224 as declared; nothing is blocked.
When H5 beta needs to distinguish decoders finely, move the horizon to 9
rather than growing the ring: it is one extra step, it recovers 12 classes,
and it reaches the ring's ceiling. Record the change as a new scope with a new
fixture rather than editing the published one, because the 224 map is already
wired into `h5_reference.py` and a silently different map is worse than two
declared ones.

**One thing the class map does not do.** These are TERMINAL-behaviour classes:
the lattice after exactly 8 steps. Two rules with different intermediate
trajectories and identical terminal states are one class. If a decoder's merit
depends on the path rather than the endpoint, terminal classes are the wrong
equivalence and trajectory classes would be needed. That is a scope choice,
not a defect, and it is stated in the fixture.

## 4b. `eca_rule_eval_v1` handover status: MINE, NOT YET HANDED. Nothing is blocked on it.

Checked rather than recalled, on main:

    vivarium/viv/kinds.py       ca_density_v0 registered.  eca_rule_eval_v1 ABSENT.
    vivarium/viv/executors.py   ca_density_v0 bound.       eca_rule_eval_v1 UNBOUND.
    archaeon/producer/h5_reference.py   consumes
                                herakles/eca/class_map_fixture.json, producer-side

So the CLASS MAP is handed over and in use; the KIND is not, and has no
Vivarium entry.

**That is the correct state for H5 alpha**, and I am not treating it as debt.
The design routes alpha through the producer: a frozen decoder applied before
submission needs producer provenance and no runtime loader, and my evaluator
consumes only a resolved rule number. Nothing in H5 alpha needs the queue.

**What a handover would need, when beta wants it.** A kind entry declaring the
exact payload set `rule_number`, `n_cells`, `steps`, a result schema over the
terminal lattice or its digest, and a thin wrapper of the same shape as
`ca_density_v0`: encoding, boundary, radius refusal and enumeration bound all
taken from `herakles/eca` and decided nowhere else. The library is pure and
side-effect free at import, so the wrapper stays thin. Say the word and I will
prepare the library side; the kind contract is Vivarium's.

**One thing a wrapper must not do.** Reuse the radius-3 hex decoder under a new
number. An elementary rule is an integer 0..255 and its bit index counts from
the LEAST significant end; the radius-3 table is 32 hex with bit k from the
LEFT. Two conventions, two kinds, no shared decoder. A test asserts in a clean
interpreter that importing `herakles.eca` does not import `herakles.evca`.

## 5. What I need in `C3_2_READOUT.md` to judge the historical arm against C1-e

Per genome, per IC sample, so the comparison is like-for-like rather than
pooled.

**Required fields, per (rule, IC sample):**

    rule name and rule_hex          so a transcription slip is visible
    n_ics and the IC seed           C1-e used an unbiased iid ensemble; if
                                    C3-2 draws differently the numbers are not
                                    comparable and I need to know that first
    n_cells and steps               C1-e was 149/298, 599/1198, 999/1998
    success_criterion               `stable` or `at_T`, named per number
    accuracy                        the number itself
    n_incorrect                     so I can recompute the binomial SE
    mask digest                     the field the symmetry arm turns on
    witness and witness_truncated   truncated witnesses cannot evidence equality
    uniform_fixed_points            both flags, per rule

**The comparison I will make, stated now so it is not chosen afterwards.**
C1-e reproduced 17 of 18 cells against published figures under `at_T`, with a
Bonferroni band of 2.9912 SE over 18 cells. If C3-2's historical arm reports
`at_T` at 149/298, I will compare each genome's accuracy against the C1-e
measurement, not against the published figure, using a binomial SE from the
C3-2 n_ics. A disagreement there is an instrument question between two of our
own runs, which is a different and easier question than a disagreement with
the literature.

**Three things that would make the comparison impossible, so please flag them
if true.** A different IC ensemble from C1-e's unbiased iid. A pooled accuracy
across IC samples rather than per-sample. `stable` numbers presented where
`at_T` is meant, or the two mixed in one column without the criterion named
per number.

**And the two standing facts.** `particle2` stays HELD: 4.97 SE from published
at N = 149, four of five suspects eliminated, only transcription surviving and
untestable without the original bytes. It is usable as an organism and not as
a reproduction claim. `maj` = 0.0 is a STRUCTURAL zero and a correct
reproduction; see `herakles/evca/MAJ_STRUCTURAL_ZERO.md`, and please cite that
file rather than restating the reason.
