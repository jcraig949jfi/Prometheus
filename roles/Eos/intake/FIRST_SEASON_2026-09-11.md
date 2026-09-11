# Eos first active season -- results (2026-09-11)

Currency: 2026-09-11. Every prediction in
roles/Eos/intake/PREREGISTRATION_2026-09-11.md was written and committed
before any of this ran. Raw rows: results_2026-09-11.json,
ledger_2026-09-11.json, REFUSALS_2026-09-11.md. Harness:
agents/eos/src/first_season.py. Controls: agents/eos/tests/test_intake.py
(25 passing).

No daemon was started. The only network activity was the bounded liveness
probe: 2 requests, both HTTP 200, 431 ms and 244 ms, at or under 75 percent
of arXiv's documented rate.

## The headline

    mechanism           what it looks at          what it decided
    old scorer          the item's text only      100/100 to a content-free
                                                  keyword string; 8/100 to
                                                  the item that actually
                                                  bears on a live lane
    new gate            the item AND the state    51 REFUSED, 7 sent to a
                        of this repository        human, 1 RESOURCE

## Test 1 (EOS-07): the old scorer is dead, killed by its own controls

Fixtures chosen by the harness, not by hand. Paper ATTENTION threshold is
the scorer's own: 20.

    control    score  fires?  item
    NEGATIVE       0  no      Prospective Compression in Human Abstraction
                              Learning
    POSITIVE       8  NO      Counterexample Guided Learning in the Large
                              using Reasoning Agents
    CHEAT        100  YES     an abstract consisting ONLY of the scorer's
                              own tier-1 and tier-2 substring lists

The preregistered prediction held in full, and worse than predicted. The
CHEAT fixture did not merely beat the POSITIVE: it SATURATED the scale
(capped at 100) on a string with no content, while the genuinely relevant
item scored 8 and would never have been surfaced at all. The scorer's
recorded reason for the 100 is "steering vector, activation engineering,
mechanistic interpretability" -- three phrases it found in a list of
phrases.

A gate that a content-free string passes at 100/100 and a real item fails
at 8/100 is not a weak instrument. It is an instrument pointed at the wrong
object: it measures whether a document contains certain words, and was read
for four months as measuring whether a document mattered.

EOS-08 (the containment double-count) is now moot in production: the scorer
is retired, not repaired. It stays in the tree as archaeological material.

## Test 2 (judgement-free): the old score cannot see the program at all

One item, one claim, two repository states differing only in whether the
named referent exists.

    repository state        old score   gate verdict
    referent present            0       PENDING_ADMISSION
    referent absent             0       REFUSED

The old score is identical in both worlds because it is a pure function of
the item's text; no fact about Prometheus can move it. The gate's verdict
flips. This is the whole difference between the mechanisms, and no
relevance label enters the test -- a reader who distrusts every judgement
in this document can still read this table.

## Test 3: the typed intake

    population                                  REFUSED  PENDING  RESOURCE
    POP-A  28 distinct items behind the old          28        0         0
           scorer's 42 ATTENTION slots
    POP-B  24 unfiltered live arXiv items            18        6         0
    POP-C  4 constructed bait items                   4        0         0
    RESOURCE claims (2)                               1        0         1

    Preregistered 3a: at most 2 POP-A survivors.  Actual 0.
    Preregistered 3b: all bait refused.           Actual 4 of 4 refused.
    Preregistered 3c: 1 to 7 POP-B survivors.     Actual 6 (7 after the
                                                  resubmission below).
    Preregistered 3d: measured RESOURCE passes,
                      documented one refused.      Both held.

POP-A is the important row. Every item the old instrument put in front of a
human over 11 days -- 42 slots, 28 distinct items -- is refused by the new
gate, and none of the refusals is about topic. They are refused because not
one of them can name a place in this repository that would change. That
includes the pavement skid-resistance paper the old scorer promoted to
ATTENTION REQUIRED on 2026-03-25 with the reason "mechanistic
interpretability, interpretability".

The six items sent to a human, each with the referent that admits it:

    2608.15546  ATLAS: Scaffold-Free Algorithm Synthesis by LLMs via
                Embedding-Guided Quality-Diversity
                -> apollo/ARCHITECTURE.md#Structural mutations die on arrival
    2608.05651  Relay, Don't Route: Adaptive Population Handoff for
                Cost-Efficient LLM-Driven Evolution
                -> apollo/ARCHITECTURE.md#Structural mutations die on arrival
    2608.07544  MOSAIC: Adversarial Co-evolution of Specialist Heuristics
                and Problem Instances
                -> roles/Nyx/BACKLOG_H0H5.md#coevolution
    2607.11916  QDEvo: A Multi-Objective Quality-Diversity Framework for
                Automated Heuristic Design
                -> roles/Nyx/RESPONSIBILITIES.md#MAP-Elites
    2609.09776  Proof-Carrying Cognition: Closing the Verification Gap with
                Reality-Settled Reward
                -> roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates
    2606.11521  Counterexample Guided Learning in the Large using Reasoning
                Agents
                -> agents/icarus/daemon.py#counterexample

These are not findings and not recommendations. They are six items a person
now has to look at, each with the exact file and token that would have to
change for the item to have been worth reading. Two of them point at the
same Apollo sentence, which is itself worth noting: the program's most
attackable standing claim attracted two independent probes in one 24-item
sample.

NOTE ON 2606.11521: it is both the POSITIVE control of Test 1 and a
PENDING item here. The old scorer gave it 8 and would have discarded it;
the gate sent it to a human. That is the same item, both mechanisms, one
sample.

## Test 4: the attack on the new gate -- IT FAILED, as predicted

Bait item "Compressed Coordinate Systems for Cross-Domain Structure
Discovery" -- written to echo the operator's own north-star phrasing --
paired with a REAL referent chosen because it exists, not because it is
related: roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates.

    state: PENDING_ADMISSION. Every check passed. The gate was fooled.

This was predicted in writing before it was run. The gate verifies that a
referent EXISTS; it does not verify that the referent is the RIGHT one. A
proposer willing to name a real file and a real token can push anything
through to the admission queue.

What that does and does not mean:

- It does NOT mean the gate is equivalent to the old scorer. The old
  scorer could be beaten by a string; the gate has to be beaten by a
  person or process willing to write a false claim naming a real object.
  The attack surface went from "any text" to "a checkable lie".
- It DOES mean the gate cannot be trusted as the last step. The terminal
  states ANCHOR and ACQUIRE are human admissions and must stay human. The
  gate's only power is refusal.
- The hole is locked into the test suite
  (test_cheat_a_real_but_unrelated_referent_still_passes). If a future
  change closes it, that test FAILS and forces the seat to update the
  test, the ledger and the docstring together, rather than quietly
  inheriting a reputation the mechanism has not earned.

## Two defects the run found in the gate itself

Both were found by running it, and both are fixed with tests.

1. INSTRUMENT ERROR WAS BEING BANKED AS EVIDENCE. The ACQUIRE dedup search
   (`git grep` over 39,284 files) exceeded its 60 s budget and the gate
   recorded the item as REFUSED. A search that did not answer is not a
   fact about the item. The gate now has a separate INDETERMINATE state
   that is neither a refusal nor an admission, the budget is 240 s, and
   test_indeterminate_is_not_a_refusal holds the line.

2. THE INSTRUMENT WAS CONTAMINATING ITS OWN INPUT, TWICE. The dedup search
   asks "does the program already have this?" over the tracked tree -- and
   the tracked tree contains Eos's own intake records, which quote every
   item they record. The first run found "Microcosmos" in 2 files, both of
   them this seat's probe and sample. Excluding roles/Eos/intake/ and
   roles/Eos/archive/ left 1 hit, and the hit was agents/eos/src/intake.py
   itself: the comment documenting the contamination defect contaminated
   the instrument by naming a real item.

   The rule that survives both rounds is simpler than either patch: the
   search asks what THE PROGRAM has, and Eos is not the program. Everything
   this seat writes -- records, archive and its own source -- is excluded.

## The proposer's own error, and the resubmission

The one ACQUIRE candidate was REFUSED, and not because of the item. The
proposer (this seat) named destination `vivarium/worlds/microcosmos`, a
path it had written into the preregistration without verifying. There is no
`vivarium/worlds/` directory.

The claim was NOT edited in the preregistered run. A separate, labelled
resubmission with a verified destination (`vivarium/specs/microcosmos.json`,
parent exists) reaches PENDING_ADMISSION; both attempts are on the record
in RESUBMISSION_acquire_2026-09-11.json. Nothing in the gate changed
between them.

The gate caught its own author being sloppy. That is the most encouraging
single result in this pass, and it is worth more than the bait test:
constructed bait was designed to fail, while this error was not designed at
all.

## What this pass does NOT establish

- Not that the gate is good. One pass, one seat, one self-labelled sample,
  the author reporting on the author's own mechanism. A positive result
  that favours this seat's lane is exactly the kind that propagates and is
  least attacked; it needs independent attack before it is anything.
- Not that the six PENDING items are worth reading. Nobody has read them.
- Not that the refusal of POP-A was correct in every case. It was correct
  by the gate's rule; whether the rule is right is the operator's question,
  and the refusal corpus is committed so the rule can be argued with.
- Not that collection should restart. The operator's condition was evidence
  that the typed mechanism decides more sharply than the score. That
  evidence is above. The decision is not this seat's.
