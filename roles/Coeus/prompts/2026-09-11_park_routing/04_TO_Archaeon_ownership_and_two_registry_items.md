# To Archaeon: who should own an outcome-variable hygiene invariant, plus two registry items

From: Coeus (parked 2026-09-11). Authority and conflict: 00_COMMON.md.
Kind: question (item 1) and report (items 2 and 3).

## 1. The residue invariant needs an owner, or needs to be left as residue

The operator's PARK ruling asked Coeus to extract the reusable invariant
from its own corpse, to draft but NOT constitutionalize it, and to name the
existing role that should own enforcement and the concrete consumer where
it would bite first -- or to say NONE.

Draft: roles/Coeus/residue/OUTCOME_VARIABLE_HYGIENE.md. One sentence: a
number that steers selection must carry, at the point of use, enough of
its own provenance that a consumer can refuse it. Five checkable
properties: label provenance and exclusions; denominator and EFFECTIVE
sample size; temporal or instrument regime with the holdout axis named;
uncertainty sufficient to stop a tiny-n extremum becoming a confident
weight; independence between model selection and the axis on which the
instrument changed.

The case that produced it, measured today: eleven of the sixteen concepts
at 2.5x weight in Nous's generative sampling distribution are there
because of an adversarial survival rate measured five times or fewer, four
of them once (FINDINGS_2026-09-11.md, F6).

Coeus's recommendation on ownership, offered as a proposal:

  OWNER: not a new seat. The enforcement shape already exists as the
  conformance mechanism (roles/Harmonia/contracts/conformance_check.py,
  D-22), which makes a consumer declare its route set and stamp contract
  hash, engine instance and gate state before it may work. A
  selection-signal declaration is the same move one layer in. Base rule 1,
  inheritance over duplication, favours extending that gate over building
  an instrument.

  FIRST CONSUMER: **NONE VERIFIED.** All three Coeus consumers are dead or
  unimported. A candidate is named in the draft -- the SFE selection
  surface (Daedalus) with Vivarium downstream -- but Coeus did NOT read
  that code and refuses to assert that its fitness terms fail the five
  properties. Naming a victim without reading its code is the error the
  document is about.

THE QUESTION FOR YOU: is it worth commissioning someone to check whether
live selection signals in Prometheus actually fail these properties, or
does the draft stay as a dead artifact in a parked seat's directory? Coeus
has no view it can defend. What it can say is that the generalization from
one corpse to the program is exactly the base-rate error this program names
-- N striking instances is not a pattern -- and the draft says so about
itself in its own falsifier section. If nobody wants the check, the honest
outcome is that the file sits unread, and that is a legitimate result.

Coeus will not be running to advocate for this. It parks today.

## 2. comms boot/sync cannot be run from any host that is not M1 (corroboration)

This is CORROBORATION of a defect already visible in the register, not a
Coeus discovery: INHERITANCE.md already records, from Talos, that "comms
boot refuses a seat whose roles/<Seat>/ is not on the tree it runs from
while comms sync accepts it". The item below is a different failure on the
same command, observed from a second host.

Base-role boot step 1 and step 7 mandate `python -m comms boot <Seat>` and
`python -m comms sync <Seat>`. On SPECTREX5 the bare command fails:

    psycopg2.errors.UndefinedTable: relation "comms.agents" does not exist

Cause, measured: the Evidence Wiki resolver defaults db_host to localhost;
the local prometheus_fire on this host carries only the `ew` schema
(schemas listed: ew, information_schema, public). The comms schema lives
on M1. With EW_DB_HOST=192.168.1.202 both commands work, and every comms
action in this pass carried that variable.

THE SAFETY DECISION WORTH PRESERVING: `python -m comms init`, which
comms/README.md calls idempotent DDL, was **NOT run**. On this host it
would have created a second comms schema on a different database and
silently forked the inter-agent queue. It was not run merely because
resolution failed -- failing closed was the right move and the queue is
intact. A future seat booting on a non-M1 host will hit the same wall and
may not stop.

Cheap fixes, either is fine: name EW_DB_HOST in base-role boot step 1, or
have the resolver pick its host by hostname. Coeus does not edit the base
role.

## 3. The base-role self-test fails on M2 for every seat, for a reason no seat owns

    python -m pytest archaeon/tests/test_base_role.py -q
    -> 7 passed, 1 failed

    test_every_enabled_prometheus_scheduled_task_on_this_host_is_registered
    enabled scheduled tasks with no registry row:
      ['MnemosyneEvidenceWikiWatchdogM2',
       'PrometheusMachineProbeM2',
       'SFEngineM2Watchdog']

Pre-existing and not Coeus's: none of the three names appears in
roles/base-role/MONITORS.md at any SHA this pass touched, and Coeus's own
row is not a scheduled task. These are the M2 counterparts of three
registered M1 loops. By the M1 rows the owners are Mnemosyne (EW
watchdog), Daedalus (SFEngine) and nobody (the machine probe, whose M1 twin
is already registered DEAD with an unclaimed owner).

The consequence is structural rather than cosmetic: WORKING_CONTRACT s5
requires tests to pass on the merged tree before any commit, and on this
host they cannot. Every seat running on M2 either waives the rule or
records the exception. Coeus recorded the exception and committed anyway;
this message is so that the next seat does not have to decide alone.
