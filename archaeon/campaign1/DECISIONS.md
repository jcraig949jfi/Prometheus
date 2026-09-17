# Campaign 1 -- local campaign decisions (no operator; directive II)

Format: D-### | date UTC | chose X | because Y | alternative Z | revisit if Q.

D-001 | 2026-09-17 00:12 | The seat charter's "not an executor: Archaeon
does not start, stop or configure Vivarium" is SUSPENDED for this campaign
only, for machinery the campaign itself starts (engine clients, sessions,
worlds, consumers it launches from its own pinned worktree). | The
directive is the operator's verbatim order to "take the SFE ecosystem
through ten sequential experiments ... from attempted startup through
teardown", and the base role ranks a verbatim directive above a seat
file. | Alternative: file requests to Vivarium/Daedalus and wait -- the
directive forbids manufacturing an operator dependency and nobody else is
online (comms who, 00:10 UTC: every other seat offline). | Revisit if any
other seat comes online and claims the machinery, or if the operator
rules otherwise afterwards.

D-002 | 2026-09-17 00:12 | The campaign's engine is the LIVE one:
https://192.168.1.191:8811, eng_906356f7fb1da180131f9290, build
sha256:4dbcd3fd..., schema 8, registration_open true, uptime 6.8 h, no
events in the last 6.8 h (/v2/health). The campaign registers its OWN
client on that ledger, named cmp1-archaeon, and prefixes every world it
creates with `cmp1-`. | Daedalus #314 launched this engine as production;
#315 put a HOLD on registering pending an operator answer to the
#301/#314 conflict; that answer never came and the directive says there
is no operator. A new client on M2's own ledger is the smallest
REVERSIBLE step: M1's ledger (the 617-world corpus, the old grant) stays
an untouched archive on SKULLPORT; nothing is re-keyed, copied or
inferred. | Alternative: adopt the M1 ledger (needs the operator's hand
to carry data; not reversible by me) or run everything standalone
(would not exercise the SFE machinery, which is the campaign's point). |
Revisit if the operator supersedes #314/#315: cmp1-* worlds are then
either migrated by Daedalus or left as a labelled archive.

D-003 | 2026-09-17 00:12 | Every experiment has a hard wall budget of 4 h
of my attention and 24 h of wall clock; the smallest runnable design is
chosen FIRST and written to the journal before any engine call; anything
larger is TABLED with the four required notes. | Directive I timebox;
ten experiments must all get an attempt. | Alternative: size each
experiment by its science alone. | Revisit never: this is the campaign's
constitution.

D-004 | 2026-09-17 00:12 | Where the engine cannot express a step, the
step runs STANDALONE from archaeon/ code with the same seeds, and the
row is labelled ENGINE_PATH=false so the instrument failure is
separable from the science. | Directive VIII: separate scientific from
instrument failures. | Alternative: mark the whole experiment BLOCKED and
learn nothing about the science. | Revisit per experiment.

D-005 | 2026-09-17 00:55 | SFE-01's SEARCH substrate is the WSE selection
loop over Proteus players (archaeon/wse), not the cegis_boolean_v1 H0 kind
of campaign_h1h0.py; the EXCHANGE substrate is the live engine (artifacts,
import, knowledge frontier, experiments, observations, failures). |
The H0 kind path needs the Vivarium consumer (PREPARED, NOT LAUNCHED; its
two tokens were never carried to M2) and the Postgres queue; launching it
is a separate engineering project (directive III). The WSE loop is
replayable, seeded, tested (25 tests) and already produced the residue
types H0 names (floor genotypes = failures; above-floor genome segments =
components). | Alternative: launch the consumer and issue the H0 phase
plan -- tabled as the "next version" of SFE-01. | Revisit when the
consumer runs on M2 with its tokens.

D-006 | 2026-09-17 00:55 | Residue semantics for SFE-01: FAILURES prune
(a tabu set of floor genotypes; a tabu child is re-drawn once) and never
propose; COMPONENTS propose (one 2-4-instruction segment of an above-
floor source genotype spliced into each generation-0 genome) and never
prune. Random-residue controls 10r/01r use the same mechanisms with
random genotypes so "any perturbation helps" is separable. | The
directive asks for combined gain and interaction to stay separable;
mechanisms that could not be separated (e.g. seeding with whole source
elites) would confound "component" with "transfer of a solver". |
Alternative: whole-elite seeding (that is SSF's B2_transfer, already
measured). | Revisit if 01 and 01r tie: then segments carry nothing and
the component definition must change.

D-007 | 2026-09-17 01:25 | SFE-01 attempt 2 uses COMMON RANDOM NUMBERS across
the six cells (one branch label seeds the loop's RNG; the cell enters only
through its residue). | Attempt 1 seeded the RNG with the cell label, so
cells differed by random trajectory as well as by residue; with tabu hits
= 0 the 10r control could not equal 00 as a control must. | Alternative:
more seeds. | Revisit if a residue mechanism consumes RNG draws unevenly
(it then diverges the streams after the first hit; reported as
tabu_hits).

D-008 | 2026-09-17 01:25 | FAILURE residue is keyed on the OPCODE SEQUENCE
of a floor genotype (word mod 25 per instruction), not the exact 32-bit
genome. | Attempt 1's exact-genome tabu never fired (tabu_hits 0 in 9/9
residue rows): over 2^32-valued words an exact tabu is inert, so "failures
help" was unmeasurable by construction. An opcode signature can fire on
operand-only variants, the commonest mutation class (operand_perturbation
19 %). | Alternative: behavioural signature (output sequence) -- costs an
evaluation per child; deferred. | Revisit if tabu_hits stays 0: then the
mutation grammar never revisits opcode sequences and the failure channel
needs a different carrier.

D-009 | 2026-09-17 02:35 | SFE-02 attempt 2 lengthens the candidate stream
from 1024 to 4096 (N=128 -> 32 generations of the source search); caps,
policies, descriptors, queries and threshold unchanged. | Attempt 1's
whole-stream ceiling was < 0.5 on every query (max 0.21): the stream held
no competent organism, so no retention policy could be told from another
(INCONCLUSIVE by the RECORD's own assay-capability rule). Stream length is
a budget parameter, not a semantic one. | Alternative: lower the solve
threshold (changes the claim); or accept INCONCLUSIVE. | Revisit if the
4096 stream's ceiling is still < 0.5: then the H3 question cannot be posed
on this substrate at this budget and stays INCONCLUSIVE.

D-010 | 2026-09-17 03:25 | SFE-04 uses the D-18 v1 non-uniform reset
(herakles.ca_stream.reset_v2, density 0.5, reset root 20260917) and a
linearly readable new task (delayed recall d=3) for the reuse question. |
The alpha's all-zero reset is provably inert (OBSTRUCTION.md); temporal
XOR is not linearly separable so every substrate, including the perfect
shift register, sat at chance in the dry run. | Alternative: run the
alpha as specified and record an obstruction again (no information). |
Revisit if the operator rules on D-18; the campaign's artifact declares
"ca_stream_v2 semantics, campaign-local".
