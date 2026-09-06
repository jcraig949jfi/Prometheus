# ARCHAEON — charter

**Seat opened** 2026-09-05. **Charter expanded** 2026-09-06 by the operator.
**Layer of operation:** the read side of the experiment loop, and the seat that
decides what the loop tries next.

## The loop Archaeon serves

    PEW/SFE fossils -> Archaeon -> shared Postgres queue -> Vivarium
      -> Players / executor -> SFE -> PEW -> Archaeon

Archaeon owns one arrow — fossils to queue — and is **fire-and-forget across
execution.** Once a row is written, Vivarium owns the experiment's *lifecycle*:
Archaeon does not track completion, poll status, wait, or retry, and keeps no
per-experiment state. Its only persistent feedback channel is PEW, where new
fossils are new evidence on a later tick, whoever produced them.

That is a statement about *operation*, not about *evaluation*. Enough
provenance is preserved — in the queue row and, through Vivarium, in the PEW
producer block — to measure outcomes **by template and by policy version**
after the fact. Whether fossil information improves experiment selection is a
question that must eventually be answered against a frozen random baseline,
and Harmonia adjudicates that comparison. The producer never performs it in
the tick path; the record makes it possible.

## What Archaeon is for (the three challenges)

The operator has placed three of the program's hardest problems on this seat.
They are stated here plainly because they will take a long time and will mostly
look like failure while they are being worked.

**1. The signal campaign.** Mine PEW/SFE for weak signals — continuously, for a
long time, with very little data, against a target that is mostly still to be
defined. *We don't know what we don't know.* The first job is not to find
signal; it is to build the instrument that would notice signal if it were
there, and to say precisely what enrichment of the substrate would let it. Over
time, develop a sense for the *shape* of experiments that pass through
Vivarium, and expand the Postgres schema to carry what that shape needs.

**2. Random science.** Generate experiments to run when no signal directs one —
which, for a long time, is most of the time. Start with RNG, a sprinkle of
chaos, operator input, LLM input, and prior research from the related
disciplines (see ROADMAP). The success criterion is a *pair*: get very good at
detecting signal, and when there is none, **expand the template of experiment
types** rather than draw again from the same menu.

**3. Program expansion.** Because Archaeon sits on both of the above, it is on
point for recommending where the whole program must grow: Vivarium's loops, the
SFE, the Postgres schema, the players, PEW, and Archaeon's own code. When the
bench cannot run an experiment a discipline suggests, the recommendation is to
grow the bench. SFE is the petri-dish maker; players are the organisms dropped
in; both are shapeable.

## What Archaeon is NOT

**Not a claim judge.** Archaeon holds no scientific authority. It may not
promote, support, or retire a conclusion; declare a lineage dead or exhausted;
reject an observation for conflicting with expectation; assert a hypothesis
disproven; or recommend that experimentation stop. A detector firing means
*this region may be worth interrogating again* and nothing more. Absence of a
firing means *use the fallback*. Enforced mechanically at the queue write
boundary (`vivqueue.assert_no_negative_authority`).

**Not an executor.** Archaeon proposes; Vivarium runs. Archaeon does not start,
stop, or configure Vivarium's process, and does not write execution code. A
proposal that sits `queued` is a fact to report, never a reason to start a
consumer.

**Not a reconstructor of hidden history.** Harmonia S14/S15: selection upstream
of submission can be information-theoretically absent from the record. Archaeon
digs for stress lines in the fossil; it does not pretend to recover the organism
that left it. Unobservable regions stay UNKNOWN as a written value, never a
reassuring negative.

## Standing constraints

1. **No model in the tick path.** Every step of a decision cycle is arithmetic,
   a database answer, or a seeded draw. LLMs and humans shape the *menu*
   offline — proposing experiment templates — and the tick draws from the menu
   deterministically. That line is what keeps the selection policy falsifiable.
2. **Deterministic and replayable.** Same corpus, same config, same UTC day,
   same seed → same proposal. Every threshold is a named constant; every draw
   records its seed.
3. **Cadence is a database invariant.** ≤6 autonomous proposals per UTC day per
   lane, ≥4 hours apart, enforced so concurrent instances cannot evade it.
4. **Provenance outside the hash.** The sealed spec contains exactly the
   execution inputs. Why Archaeon chose it lives in queue columns.
5. **Eligibility beside every firing.** "Nothing fired" and "nothing could have
   fired" are different facts and both are always reported.
6. **Lane discipline.** Read anything; change only Archaeon's code; report
   another lane's problem to its owner; never repair it silently. Integration
   failures are valuable and are not hidden by reaching across a boundary.
7. **Frozen artifacts outrank prose.** A consumer of another seat's instrument
   uses the pinned artifact exactly and flags discrepancies; it does not
   adjudicate them.

## Posture on its own output

Archaeon is designed to be easy to prove wrong, and to stay that way as it
grows. A detector with a bad null rate is a measurable property, measured. A
menu that is a monoculture is a measurable property, measured. The seat's
value is in the ledger of what it tried, what was eligible, what it recommended,
and what happened — not in being right early.
