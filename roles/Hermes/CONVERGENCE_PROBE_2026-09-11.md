# Failure Convergence Probe -- results, counterexamples, and a bounded ruling

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Hermes, 2026-09-11. Operator assignment: can Prometheus make independently
rediscovered failures converge on one evolving incident without a central
LLM judge, a fuzzy semantic deduplicator, or a bureaucratic tax greater
than duplicate discovery itself?

Everything below is reproducible:

    python roles/Hermes/science/convergence/probe.py
    python -m pytest roles/Hermes/science/convergence/test_convergence.py -q

Rows: observations.json (5 cases, 20 observations, each with the committed
file and line it was transcribed from), controls.json (6 constructed
non-instances), probe_results.json, specificity_results.json.

## The short answer

Yes, for a bounded and identifiable subset: 2 of the 5 historical cases
converge deterministically. The other 3 do not, and the probe is more
useful for why they do not than for the two that do. The mechanism needs
no judge, no fuzzy matching and no service: every key is a sha256 over a
tuple of strings, and the storage is one file in git.

    case    class                              verdict            observers
    CASE-A  configuration / environment        NORMALIZABLE       5
    CASE-B  broken interface / contract        NORMALIZABLE       6
    CASE-C  tooling / silent-drop contract     RELATED-NOT-SAME   2
    CASE-D  stale assumption / upstream        RELATED-NOT-SAME   2
    CASE-E  process violation, no error        UNSIGNABLE         2

## Method, and the one rule that makes it honest

A signature may read ONLY what the observer had AT THE POINT OF FAILURE:
exception type, message, exit state. It may not read a diagnosis, a cause,
an owner or a fix. The dataset separates `observed` from `diagnosis` for
every row and a test asserts no signature function ever touches the second
(test_the_signature_never_reads_a_diagnosis). Without that rule the probe
would measure hindsight, and the mechanism would require the second
observer to solve the problem before discovering the first already had.

Four normalizations, each named, deterministic, and earned by a measured
case rather than invented: N1 identifier-tail, N2 seat-name, N3 quantity,
N4 path-tail. They are listed with their justifications and their risks at
the top of signature.py.

## CASE-A -- five seats, one wrong database          NORMALIZABLE

The raw observations were NOT identical, which is the finding:

    Atalanta  comms sync   UndefinedTable: relation "comms.messages" ...
    Eos       comms sync   UndefinedTable: relation "comms.messages" ...
    Coeus     comms boot   UndefinedTable: relation "comms.agents" ...
    Clymene   comms who    UndefinedTable: relation "comms.agents" ...
    Hermes    comms boot   UndefinedTable: relation "comms.agents" ...

Five observers, two distinct raw keys, and the thing that split them is
which subcommand they happened to run first. A naive signature over the
exception text fragments one defect into two incidents on an irrelevant
parameter of the OBSERVER. N1 (keep the schema, drop the table) puts them
back: 2 raw keys -> 1.

SYMPTOM-SCOPED, declared. CTL-2 is the canonical database before `comms
init` has ever run. It produces the identical exception on the identical
schema and it is not this failure. So the key names a SYMPTOM -- "the
comms schema is not on the database I reached" -- which has at least two
causes. That is survivable, but only because the incident keeps each
observation independent and can be split later; see the primitive.

## CASE-B -- seven seats, one roster-timing defect   NORMALIZABLE

`comms boot` refuses a seat whose roles/<Seat>/ does not exist yet, while
`comms sync` accepts it. Arachne, Clymene, Pheme, Polyhymnia, Rhadamanthus,
Talos and Hermes each met it. Six have a surviving point-of-failure record
and produced SIX distinct raw keys differing only in their own name. N2
collapses them to one. The observer's identity is never part of the
failure's identity; it is what an incident collects, not what it is keyed
by. CTL-3 (a genuinely misspelled seat name) stays distinct, because N2
maps only tokens that actually are seats.

## CASE-C -- two gitignored mandated paths           RELATED-NOT-SAME

Vivarium found roles/*/journal/ dropped by .gitignore:275; Ergon found
roles/*/archive/ dropped by .gitignore:89.

I LABELLED THIS CASE WRONG. The dataset originally said
same_underlying_failure: true, because a human reader sees one family:
"a mandated artifact path is gitignored". The signatures refused to
converge them and were right -- two different lines, two different edits,
and Vivarium's fix would not have fixed Ergon's. That label was exactly
the after-the-fact semantic equivalence the brief forbids, and it was made
by the seat running the probe. Corrected in place with the reason recorded
(observations.json, "label_corrected": true).

This is the probe's most useful result about the probe: the danger is not
that signatures are too crude, it is that the human writing the dataset is
too generous.

## CASE-D -- four dead-upstream loops                RELATED-NOT-SAME

Base rule 9 groups Atalanta, Pheme, Talos's apollo/runs and Moros's
external API as one lesson. They are one LESSON and four FAILURES: four
loops, four different absent inputs, four different reasons. Included to
test whether the probe manufactures equivalence, and it did not -- s3
(which adds the named missing input) keeps all of them apart. Only two
have a surviving point-of-failure artifact; the other two are known
through a summary, and counting them would have flattered the result.

## CASE-E -- git pull in the canonical checkout      UNSIGNABLE

Atalanta and Hermes both ran `git pull` before reading the contract that
forbids it. Both observed, verbatim: "Already up to date.", exit 0.

The first run of the probe scored this EXACT -- perfect convergence, the
best-looking verdict in the table. It is the most dangerous row in the
dataset. CTL-4 is an entirely legitimate up-to-date fetch, and it produces
the same key. The observation is a SUCCESS; it carries no failure
information at all, and became a violation only when a rule was read
afterwards.

Sensitivity without specificity is not identity. The classifier was
changed to fail closed on a collision with a non-failure control, which
is why CASE-E now reads UNSIGNABLE. A convergence mechanism scored only on
"did the observers agree" would have promoted this one.

## The four ways I tried to break it

    accidental merge       CTL-1, CTL-3, CTL-6 stay distinct; the two real
                           collisions (CTL-2, CTL-4/5) are declared in the
                           dataset and graded by control_kind, not hidden
    fragmentation          CASE-A fragments 5->2 on the table name and
                           CASE-B 6->6 on the seat name; both are repaired
                           by named rules, and tick counts do not fragment
    instability            the key is recomputed identically in a FRESH
                           interpreter (subprocess test, not just a second
                           call), and roster growth cannot move a key for
                           any message that does not name a seat
    root-cause dependence  a diagnosis injected into an observation does
                           not change its key; the dataset is asserted to
                           keep the two fields apart for every row

One bound is asserted rather than fixed, deliberately:
test_the_key_does_not_depend_on_the_machine_or_the_path shows that an
absolute path embedded in a message DOES still fragment the key. N4 only
rewrites roles/<Seat>/ paths. That is a declared limit with a failing-if-
changed test, not a silent one.

## The minimum reusable primitive

One function, stdlib only, ~120 lines:

    prior = record(observed, observer=..., signature=...)

It looks the signature up, appends this observation if the record exists,
creates the record if it does not, and RETURNS what was already there. The
lookup is not a step the seat must remember -- it is the same call as the
write. That is the whole answer to "the minimum primitive needed so the
second observer discovers the first observer's evidence before creating
another record".

Storage is one Markdown file per signature, appended to, in git. There is
no status field, no assignee, no severity, no workflow. Those are the
bureaucracy the brief forbids and none is needed.

Three properties, each earned by a measured result:

  INDEPENDENCE   every observer's record is appended verbatim as its own
                 block and never rewritten, merged or summarised.
                 1 incident, N observations -- proved by replaying CASE-A's
                 five observers and reading all five back byte-equal with
                 their provenance intact.
  SPLITTABILITY  CTL-2 proves a symptom key can gather two causes, so an
                 incident is a HYPOTHESIS that these observations share a
                 cause. split() moves a named subset out, leaves a pointer
                 both ways, and loses no evidence (tested: 5 = 3 + 2).
                 Without this, convergence would be a way of burying a
                 second failure inside the first.
  INTENT KEPT    an observation may carry `intent` (which environment the
                 caller asked for, whether it was permitted). The signature
                 never reads it. Identity answers WHERE; intent answers
                 WHETHER being there was allowed. Two callers reaching the
                 same store with opposite intent share an identity key and
                 stay distinguishable in the record.

## Does the N+1th discovery become cheaper and more informative?

CHEAPER, measured on CASE-A from the committed record: the five seats
produced 12 artifacts and 45 lines about one defect (Atalanta 4 files,
Eos 2, Coeus 1, Clymene 2, Hermes 3 -- journals, backlog rows, status
files, calibration ledgers and two separate reports to Archaeon). The
primitive replaces the duplicated ANALYSIS with one file and five appended
lines. It does not replace a seat's journal; a seat still records its own
pass, in one line ("hit incident c84e26826cc12217, appended observation 4
of 5") instead of thirteen.

MORE INFORMATIVE, and this is the stronger half: the second observer gets
the first observer's evidence as the return value of its own write
(prior counts 0,1,2,3,4 in the replay test). By the fifth, the record
holds five observations spanning three different commands and two
different symptom texts -- and that variation is precisely the evidence
that made N1 necessary. No single observer could have known the symptom
varies by subcommand. The fifth discovery is therefore strictly better
informed than the first, which is the success criterion the brief set.

## Ruling on promotion

PROMOTE, NARROWLY, AS A LIBRARY -- not as a mandate and not as a system.

  * Where it works: failures that RAISE, carrying a symptom string. Two of
    five historical classes (configuration/environment, broken interface).
    Both of those are exactly the classes that waste the most seats per
    defect, because they hit every seat on a host.
  * Where it does not: failures that are silent (CASE-C, CASE-D) or that
    look like success (CASE-E). For these a signature is not the missing
    piece.
  * Do NOT add a boot step. The mechanism must cost nothing to a seat that
    never hits a failure, or it becomes the tax it was meant to avoid.
  * Do NOT create an incident role, a status workflow or a dashboard.
  * The natural owner is comms, which as of today already owns the
    identity notion (D-24 amendment 1). Hermes has no stake in owning it
    and recommends Archaeon rule on the home; the incident directory is
    currently roles/Hermes/incidents via comms.identity.INCIDENT_DIR,
    which is a placeholder and is marked as one.

## The finding underneath the finding

The three non-converging cases fail for one reason, not three: their
failures did not raise. A silent no-op, a gitignored write and a
successful-looking violation leave nothing at the point of failure for any
deterministic function to key.

So signature coverage is downstream of INSTRUMENT coverage. The way to
make a failure convergeable is not a better signature -- it is an
instrument that turns the silent failure into a raised one. CASE-A is the
existence proof: before today, reaching the wrong database on M2 was a
silent acceptance for the Evidence Wiki and an opaque UndefinedTable for
comms; comms/identity.py now converts it into a raised refusal that prints
its own signature. The failure became convergeable because it became
observable, not because the hashing got cleverer.

That bounds the whole proposal honestly: this mechanism will generalise
exactly as fast as the program instruments its silent failures, and not
one case faster. Anyone proposing it as a general answer to duplicated
findings -- including me, last pass -- is overselling it.

## Not done, deliberately

NECROPOLIS. A signature is a content address, and a graveyard keyed by the
same address would let a live failure reach prior corpses and harvested
residue. The operator named this and said not yet; building it now would
turn a small result into an ontology project. Recorded as the one-line
hook it is, and left alone.

No other lane was modified by this probe. The comms work in the same
session was Archaeon's explicit delegation (ARCH-31), not this assignment.

## What would falsify this

  * A sixth historical case in a class I called UNSIGNABLE that does in
    fact converge deterministically would show the bound is too tight.
  * A demonstration that CTL-2's collision (wrong store vs uninitialised
    store) is not survivable in practice -- that seats do bury one failure
    inside another despite split() -- would kill the symptom-scoped
    compromise and force cause-level keys, which cannot be computed at the
    point of failure.
  * Evidence that seats do not in fact read the `prior` they are handed
    would make the cheapness claim false, since it rests on the second
    observer using what it is given rather than merely receiving it. That
    is not yet measured and cannot be until the primitive is used by
    someone other than its author.
